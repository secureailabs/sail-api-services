# -------------------------------------------------------------------------------
# Engineering
# dataset_versions.py
# -------------------------------------------------------------------------------
"""APIs to manage dataset-versions"""
# -------------------------------------------------------------------------------
# Copyright (C) 2022 Secure Ai Labs, Inc. All Rights Reserved.
# Private and Confidential. Internal Use Only.
#     This software contains proprietary information which shall not
#     be reproduced or transferred to other documents and shall not
#     be disclosed to others for any purpose without
#     prior written permission of Secure Ai Labs, Inc.
# -------------------------------------------------------------------------------

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Response, status
from fastapi.encoders import jsonable_encoder

import app.utils.azure as azure
from app.api.authentication import RoleChecker, get_current_user
from app.api.datasets import Datasets
from app.data import operations as data_service
from app.models.accounts import UserRole
from app.models.authentication import TokenData
from app.models.common import PyObjectId
from app.models.dataset_versions import (
    DatasetVersion_Db,
    DatasetVersionState,
    GetDatasetVersion_Out,
    GetDatasetVersionConnectionString_Out,
    GetMultipleDatasetVersion_Out,
    RegisterDatasetVersion_In,
    RegisterDatasetVersion_Out,
    UpdateDatasetVersion_In,
)
from app.models.datasets import DatasetState
from app.utils import cache
from app.utils.background_couroutines import add_async_task
from app.utils.secrets import get_secret

router = APIRouter()


class DatasetVersion:
    """
    Dataset Version CRUD operations
    """

    DB_COLLECTION_DATASET_VERSIONS = "dataset-versions"

    @staticmethod
    async def create(
        dataset_version: DatasetVersion_Db,
    ):
        """
        Create a new dataset version

        :param dataset_version: dataset version
        :type dataset_version: DatasetVersion_Db
        :return: dataset version id
        :rtype: PyObjectId
        """
        return await data_service.insert_one(
            collection=DatasetVersion.DB_COLLECTION_DATASET_VERSIONS,
            data=jsonable_encoder(dataset_version),
        )

    @staticmethod
    async def read(
        dataset_version_id: Optional[PyObjectId] = None,
        organization_id: Optional[PyObjectId] = None,
        name: Optional[str] = None,
        dataset_id: Optional[PyObjectId] = None,
        throw_on_not_found: bool = True,
    ) -> List[DatasetVersion_Db]:
        """
        Read a dataset version

        :param dataset_version_id: dataset version id
        :type dataset_version_id: PyObjectId
        :param throw_on_not_found: throw exception if dataset version not found, defaults to True
        :type throw_on_not_found: bool, optional
        :return: dataset version list
        :rtype: DatasetVersion_Db
        """

        dataset_version_list = []

        query = {}
        if dataset_version_id:
            query["_id"] = dataset_version_id
        if organization_id:
            query["organization_id"] = organization_id
        if name:
            query["name"] = name
        if dataset_id:
            query["dataset_id"] = dataset_id

        response = await data_service.find_by_query(
            collection=DatasetVersion.DB_COLLECTION_DATASET_VERSIONS,
            query=jsonable_encoder(query),
        )

        if response:
            for data_model in response:
                dataset_version_list.append(DatasetVersion_Db(**data_model))
        elif throw_on_not_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data model not found",
            )

        return dataset_version_list

    @staticmethod
    async def update(
        dataset_version_id: PyObjectId,
        organization_id: Optional[PyObjectId] = None,
        description: Optional[str] = None,
        state: Optional[DatasetVersionState] = None,
        note: Optional[str] = None,
    ):
        """
        Update a dataset version
        """

        update_request = {}
        if state:
            update_request["$set"] = {"state": state.value}
        if description:
            update_request["$set"] = {"description": description}
        if note:
            update_request["$set"] = {"note": note}

        query = {}
        if organization_id:
            query["organization_id"] = organization_id
        if dataset_version_id:
            query["_id"] = dataset_version_id

        update_response = await data_service.update_many(
            collection=DatasetVersion.DB_COLLECTION_DATASET_VERSIONS,
            query=query,
            data=update_request,
        )

        if update_response.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset version not found in the organization",
            )


@router.post(
    path="/dataset-versions",
    description="Register new dataset-version",
    response_description="Dataset Version Id",
    response_model=RegisterDatasetVersion_Out,
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_SUBMITTER]))],
    operation_id="register_dataset_version",
)
async def register_dataset_version(
    response: Response,
    dataset_version_req: RegisterDatasetVersion_In = Body(description="Dataset Version information to register"),
    current_user: TokenData = Depends(get_current_user),
) -> RegisterDatasetVersion_Out:
    # Check if dataset version was already registered with the same name
    dataset_version_db = await DatasetVersion.read(
        name=dataset_version_req.name,
        dataset_id=dataset_version_req.dataset_id,
        organization_id=current_user.organization_id,
        throw_on_not_found=False,
    )
    # If the dataset version was already registered, return the dataset version id
    if dataset_version_db:
        response.status_code = status.HTTP_200_OK
        return RegisterDatasetVersion_Out(_id=dataset_version_db[0].id)

    # Dataset organization and dataset-versions organization should be same
    dataset_db = await Datasets.read(
        dataset_id=dataset_version_req.dataset_id, organization_id=current_user.organization_id
    )
    dataset_db = dataset_db[0]

    # The dataset should be in active state
    if dataset_db.state != DatasetState.ACTIVE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Dataset is not active. Try again later")

    # Add the dataset to the database
    dataset_version_db = DatasetVersion_Db(
        **dataset_version_req.dict(),
        organization_id=current_user.organization_id,
        state=DatasetVersionState.CREATING_DIRECTORY,
    )
    await DatasetVersion.create(dataset_version_db)

    # Create a directory in the azure file share for the dataset version
    add_async_task(create_directory_in_file_share(dataset_version_db.dataset_id, dataset_version_db.id))

    return RegisterDatasetVersion_Out(**dataset_version_db.dict())


@router.get(
    path="/dataset-versions",
    description="Get list of all the dataset-versions for the dataset",
    response_description="List of dataset-versions for the dataset",
    response_model=GetMultipleDatasetVersion_Out,
    response_model_by_alias=False,
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
    operation_id="get_all_dataset_versions",
)
async def get_all_dataset_versions(
    dataset_id: PyObjectId = Query(description="UUID of the dataset"),
    current_user: TokenData = Depends(get_current_user),
) -> GetMultipleDatasetVersion_Out:
    """
    Get list of all the dataset-versions for the dataset

    :param dataset_id: UUID of the dataset
    :type dataset_id: PyObjectId, optional
    :param current_user: Current user information
    :type current_user: TokenData, optional
    :return: List of dataset-versions for the dataset
    :rtype: GetMultipleDatasetVersion_Out
    """

    dataset_versions = await DatasetVersion.read(dataset_id=dataset_id, throw_on_not_found=False)

    response_list_of_dataset_version: List[GetDatasetVersion_Out] = []
    # Add the organization information to the dataset
    for dataset_version in dataset_versions:
        organization_info = await cache.get_basic_orgnization(id=dataset_version.organization_id)

        response_dataset_version = GetDatasetVersion_Out(**dataset_version.dict(), organization=organization_info)
        response_list_of_dataset_version.append(response_dataset_version)

    return GetMultipleDatasetVersion_Out(dataset_versions=response_list_of_dataset_version)


@router.get(
    path="/dataset-versions/{dataset_version_id}",
    description="Get the information about a dataset version",
    response_model=GetDatasetVersion_Out,
    response_model_by_alias=False,
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
    operation_id="get_dataset_version",
)
async def get_dataset_version(
    dataset_version_id: PyObjectId = Path(description="UUID of the dataset version"),
    current_user: TokenData = Depends(get_current_user),
) -> GetDatasetVersion_Out:
    """
    Get the information about a dataset version

    :param dataset_version_id: UUID of the dataset version
    :type dataset_version_id: PyObjectId, optional
    :param current_user: Current user information
    :type current_user: TokenData, optional
    :raises HTTPException: Dataset version not found
    :return: Information about a dataset version
    :rtype: GetDatasetVersion_Out
    """
    dataset_version = await DatasetVersion.read(dataset_version_id=dataset_version_id)

    # Add the organization information to the dataset version
    organization_info = await cache.get_basic_orgnization(id=dataset_version[0].organization_id)

    return GetDatasetVersion_Out(**dataset_version[0].dict(), organization=organization_info)


@router.get(
    path="/dataset-versions/{dataset_version_id}/connection-string",
    description="Get the write only connection string for the dataset version upload",
    response_model=GetDatasetVersionConnectionString_Out,
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_SUBMITTER]))],
    operation_id="get_dataset_version_connection_string",
)
async def get_dataset_version_connection_string(
    dataset_version_id: PyObjectId = Path(description="UUID of the dataset version"),
    current_user: TokenData = Depends(get_current_user),
) -> GetDatasetVersionConnectionString_Out:
    """
    Get the write only connection string for the dataset version upload

    :param dataset_version_id: UUID of the dataset version
    :type dataset_version_id: PyObjectId, optional
    :param current_user: Current user information
    :type current_user: TokenData, optional
    :return: Write only connection string for the dataset version upload
    :rtype: GetDatasetVersionConnectionString_Out
    """
    dataset_version_list = await DatasetVersion.read(
        dataset_version_id=dataset_version_id, organization_id=current_user.organization_id
    )
    dataset_version = dataset_version_list[0]

    # Send the connection string only if the dataset version is not uploaded to prevent overwriting
    if dataset_version.state != DatasetVersionState.ENCRYPTING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Dataset version is not in ENCRYPTING state. Cannot get the connection string.",
        )

    # Authenticate azure
    account_credentials = await azure.authenticate()
    dataset_version_file_name = f"dataset_{dataset_version.id}.zip"

    # Get the connection string for the dataset version which is valid for 30 minutes
    # This could be a long running operation
    connection_string = await azure.authentication_shared_access_signature(
        account_credentials=account_credentials,
        account_name=get_secret("azure_storage_account_name"),
        resource_group_name=get_secret("azure_storage_resource_group"),
        file_path=f"{dataset_version.id}/{dataset_version_file_name}",
        share_name=str(dataset_version.dataset_id),
        permission="cw",  # Create and write permission only
        expiry=datetime.utcnow() + timedelta(minutes=30),
    )

    url = f"https://{get_secret('azure_storage_account_name')}.file.core.windows.net/{dataset_version.dataset_id}/{dataset_version.id}"
    full_url = f"{url}/{dataset_version_file_name}?{connection_string.response}"

    return GetDatasetVersionConnectionString_Out(_id=dataset_version_id, connection_string=full_url)


@router.put(
    path="/dataset-versions/{dataset_version_id}",
    description="Update dataset information",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_SUBMITTER]))],
    operation_id="update_dataset_version",
)
async def update_dataset_version(
    dataset_version_id: PyObjectId = Path(description="UUID of the dataset version"),
    updated_dataset_version_info: UpdateDatasetVersion_In = Body(
        description="Object containing the information to be updated"
    ),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Update the dataset version information

    :param dataset_version_id: The dataset version id
    :type dataset_version_id: PyObjectId
    :param updated_dataset_version_info: Object containing the information to be updated
    :type updated_dataset_version_info: UpdateDatasetVersion_In, optional
    :param current_user: inforamtion of the current user, defaults to Depends(get_current_user)
    :type current_user: TokenData, optional
    :raises HTTPException: Dataset not found
    :return: Response with no content
    :rtype: Response
    """

    # Dataset version must be part of same organization
    await DatasetVersion.update(
        dataset_version_id=dataset_version_id,
        organization_id=current_user.organization_id,
        description=updated_dataset_version_info.description,
        state=updated_dataset_version_info.state,
        note=updated_dataset_version_info.note,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    path="/dataset-versions/{dataset_version_id}",
    description="Disable a dataset version",
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_SUBMITTER]))],
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="soft_delete_dataset_version",
)
async def soft_delete_dataset_version(
    dataset_version_id: PyObjectId = Path(description="UUID of the dataset version"),
    current_user: TokenData = Depends(get_current_user),
):
    # Dataset version must be part of same organization
    await DatasetVersion.update(
        dataset_version_id=dataset_version_id,
        organization_id=current_user.organization_id,
        state=DatasetVersionState.INACTIVE,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def create_directory_in_file_share(dataset_id: PyObjectId, dataset_version_id: PyObjectId):
    """
    Create a directory in the Azure file share

    :param dataset_id: Dataset id
    :type dataset_id: PyObjectId
    :param dataset_version_id: Dataset version id
    :type dataset_version_id: PyObjectId
    """
    try:
        account_credentials = await azure.authenticate()

        # Get the connection string for the storage account
        connection_string_response = await azure.get_storage_account_connection_string(
            account_credentials=account_credentials,
            resource_group_name=get_secret("azure_storage_resource_group"),
            account_name=get_secret("azure_storage_account_name"),
        )
        if connection_string_response.status != "Success":
            raise Exception(connection_string_response.note)

        # Create the directory in the file share
        create_response = await azure.file_share_create_directory(
            connection_string=connection_string_response.response,
            file_share_name=str(dataset_id),
            directory_name=str(dataset_version_id),
        )
        if create_response.status != "Success":
            raise Exception(create_response.note)

        await DatasetVersion.update(
            dataset_version_id=dataset_version_id,
            state=DatasetVersionState.NOT_UPLOADED,
        )

    except Exception as exception:
        await DatasetVersion.update(
            dataset_version_id=dataset_version_id,
            state=DatasetVersionState.ERROR,
            note=str(exception),
        )
