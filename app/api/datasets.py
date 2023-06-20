# -------------------------------------------------------------------------------
# Engineering
# datasets.py
# -------------------------------------------------------------------------------
"""APIs to manage datasets"""
# -------------------------------------------------------------------------------
# Copyright (C) 2022 Secure Ai Labs, Inc. All Rights Reserved.
# Private and Confidential. Internal Use Only.
#     This software contains proprietary information which shall not
#     be reproduced or transferred to other documents and shall not
#     be disclosed to others for any purpose without
#     prior written permission of Secure Ai Labs, Inc.
# -------------------------------------------------------------------------------

import os
from base64 import b64encode
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Response, status
from fastapi.encoders import jsonable_encoder

import app.utils.azure as azure
from app.api.authentication import RoleChecker, get_current_user
from app.data import operations as data_service
from app.models.accounts import UserRole
from app.models.authentication import TokenData
from app.models.common import KeyVaultObject, PyObjectId
from app.models.datasets import (
    Dataset_Db,
    DatasetEncryptionKey_Out,
    DatasetState,
    GetDataset_Out,
    GetMultipleDataset_Out,
    RegisterDataset_In,
    RegisterDataset_Out,
    UpdateDataset_In,
)
from app.utils import cache
from app.utils.background_couroutines import add_async_task
from app.utils.secrets import get_secret

router = APIRouter()


class Datasets:
    """
    Dataset Version CRUD operations
    """

    DB_COLLECTION_DATASETS = "datasets"

    @staticmethod
    async def create(
        dataset: Dataset_Db,
    ):
        """
        Create a new dataset version

        :param dataset_version: dataset version
        :type dataset_version: DatasetVersion_Db
        :return: dataset version id
        :rtype: PyObjectId
        """
        return await data_service.insert_one(
            collection=Datasets.DB_COLLECTION_DATASETS,
            data=jsonable_encoder(dataset),
        )

    @staticmethod
    async def read(
        dataset_id: Optional[PyObjectId] = None,
        organization_id: Optional[PyObjectId] = None,
        name: Optional[str] = None,
        throw_on_not_found: bool = True,
    ) -> List[Dataset_Db]:
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
        if dataset_id:
            query["_id"] = dataset_id
        if organization_id:
            query["organization_id"] = organization_id
        if name:
            query["name"] = name

        response = await data_service.find_by_query(
            collection=Datasets.DB_COLLECTION_DATASETS,
            query=jsonable_encoder(query),
        )

        if response:
            for data_model in response:
                dataset_version_list.append(Dataset_Db(**data_model))
        elif throw_on_not_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset not found",
            )

        return dataset_version_list

    @staticmethod
    async def update(
        dataset_id: PyObjectId,
        organization_id: Optional[PyObjectId] = None,
        description: Optional[str] = None,
        tag: Optional[str] = None,
        state: Optional[DatasetState] = None,
        note: Optional[str] = None,
        encryption_key: Optional[KeyVaultObject] = None,
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
        if tag:
            update_request["$set"] = {"tag": tag}
        if encryption_key:
            update_request["$set"] = {"encryption_key": encryption_key}

        query = {}
        if dataset_id:
            query["_id"] = dataset_id
        if organization_id:
            query["organization_id"] = organization_id

        update_response = await data_service.update_many(
            collection=Datasets.DB_COLLECTION_DATASETS,
            query=query,
            data=update_request,
        )

        if update_response.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset not found in the organization",
            )


@router.post(
    path="/datasets",
    description="Register new dataset",
    response_description="Dataset Id",
    response_model=RegisterDataset_Out,
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_SUBMITTER]))],
    operation_id="register_dataset",
)
async def register_dataset(
    response: Response,
    dataset_req: RegisterDataset_In = Body(description="information required to register a dataset"),
    current_user: TokenData = Depends(get_current_user),
) -> RegisterDataset_Out:
    """
    Register new dataset

    :param response: Response object
    :type response: Response
    :param dataset_req: information required to register a dataset, defaults to Body(...)
    :type dataset_req: RegisterDataset_In, optional
    :param current_user: information of current authenticated user, defaults to Depends(get_current_user)
    :type current_user: TokenData, optional
    :return: Dataset Id
    :rtype: RegisterDataset_Out
    """
    # Check if there is an existing dataset with the same name
    existing_dataset = await Datasets.read(name=dataset_req.name, organization_id=current_user.organization_id)
    # If there is an existing dataset with the same name, return the existing dataset ID
    if existing_dataset:
        dataset_db = existing_dataset[0]
        response.status_code = status.HTTP_200_OK
        return RegisterDataset_Out(_id=dataset_db.id)

    # Add the dataset to the database
    dataset_db = Dataset_Db(
        **dataset_req.dict(), organization_id=current_user.organization_id, state=DatasetState.CREATING_STORAGE
    )
    await Datasets.create(dataset_db)

    # Create a file share for the dataset
    add_async_task(create_azure_file_share(dataset_db.id))

    return RegisterDataset_Out(_id=dataset_db.id)


@router.get(
    path="/datasets",
    description="Get list of all the datasets for the current organization",
    response_description="List of datasets",
    response_model=GetMultipleDataset_Out,
    response_model_by_alias=False,
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_SUBMITTER]))],
    operation_id="get_all_datasets",
)
async def get_all_datasets(current_user: TokenData = Depends(get_current_user)):
    """
    Get list of all the datasets for the current organization

    :param current_user: information of current authenticated user
    :type current_user: TokenData, optional
    :return: List of datasets
    :rtype: GetMultipleDataset_Out
    """
    datasets = await Datasets.read(organization_id=current_user.organization_id)

    # Add the organization information to the dataset
    organization = await cache.get_basic_orgnization(id=current_user.organization_id)

    response_list_of_datasets: List[GetDataset_Out] = []
    datasets_ids = []
    # Add the organization information to the dataset
    for dataset in datasets:
        datasets_ids.append(dataset.id)
        response_dataset = GetDataset_Out(**dataset.dict(), organization=organization)
        response_list_of_datasets.append(response_dataset)

    return GetMultipleDataset_Out(datasets=response_list_of_datasets)


@router.get(
    path="/datasets/{dataset_id}",
    description="Get the information about a dataset",
    response_model=GetDataset_Out,
    response_model_by_alias=False,
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_SUBMITTER]))],
    operation_id="get_dataset",
)
async def get_dataset(
    dataset_id: PyObjectId = Path(description="UUID of the dataset being fetched"),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Get the information about a dataset

    :param dataset_id: UUID of the dataset being fetched
    :type dataset_id: PyObjectId, optional
    :param current_user: information of current authenticated user
    :type current_user: TokenData, optional
    :return: Dataset information
    :rtype: GetDataset_Out
    """
    dataset = await Datasets.read(dataset_id=dataset_id, organization_id=current_user.organization_id)

    organization_info = await cache.get_basic_orgnization(id=dataset[0].organization_id)

    return GetDataset_Out(**dataset[0].dict(), organization=organization_info)


@router.put(
    path="/datasets/{dataset_id}",
    description="Update dataset information",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_SUBMITTER]))],
    operation_id="update_dataset",
)
async def update_dataset(
    dataset_id: PyObjectId = Path(description="UUID of the dataset being updated"),
    updated_dataset_info: UpdateDataset_In = Body(description="Updated dataset information"),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Update dataset information

    :param dataset_id: UUID of the dataset being updated
    :type dataset_id: PyObjectId, optional
    :param updated_dataset_info: Updated dataset information
    :type updated_dataset_info: UpdateDataset_In, optional
    :param current_user: information of current authenticated user
    :type current_user: TokenData, optional
    :return: Updated dataset information
    :rtype: UpdateDataset_Out
    """

    # Dataset must be part of same organization
    await Datasets.update(
        dataset_id=dataset_id,
        organization_id=current_user.organization_id,
        description=updated_dataset_info.description,
        tag=updated_dataset_info.tag,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    path="/datasets/{dataset_id}",
    description="Disable the dataset",
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_SUBMITTER]))],
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="soft_delete_dataset",
)
async def soft_delete_dataset(
    dataset_id: PyObjectId = Path(description="UUID of the dataset being soft deleted"),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Disable the dataset

    :param dataset_id: UUID of the dataset being soft deleted
    :type dataset_id: PyObjectId, optional
    :param current_user: information of current authenticated user
    :type current_user: TokenData, optional
    :return: Dataset information
    :rtype: GetDataset_Out
    """
    # Dataset must be part of same organization
    await Datasets.update(
        dataset_id=dataset_id,
        organization_id=current_user.organization_id,
        state=DatasetState.INACTIVE,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def get_datset_encryption_key(
    dataset_id: PyObjectId,
    wrapping_key: KeyVaultObject,
    create_if_doesnt_exit: bool,
    current_user: TokenData,
) -> DatasetEncryptionKey_Out:
    """
    Get the dataset encryption key to the database, if it does not exist, create it

    :param dataset_id: The dataset id
    :type dataset_id: PyObjectId
    :param rsa_key_name: The name of the wrapping RSA key
    :type rsa_key_name: str
    :param rsa_key_version: The version of the wrapping RSA key
    :type rsa_key_version: str
    :param current_user: The current user
    :type current_user: TokenData
    :return: base64 encoded dataset encryption key
    :rtype: DatasetEncryptionKey_Out
    """
    # Dataset organization and currnet user organization should be same
    dataset_db = await Datasets.read(dataset_id=dataset_id)
    dataset_db = dataset_db[0]

    # We generate a key if none has been assigned to this dataset, otherwise we unwrap the key
    # that was used to encrypt the DS
    if dataset_db.encryption_key is None:
        if not create_if_doesnt_exit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset encryption key not found")

        # Generate a new key. TODO: could be done in keyvault
        aes_key = os.urandom(32)

        wrapped_key_secret = await azure.wrap_aes_key(
            aes_key=aes_key,
            wrapping_key=wrapping_key,
        )

        # Add the key information to the database
        dataset_db.encryption_key = wrapped_key_secret
        await Datasets.update(dataset_id=dataset_id, encryption_key=wrapped_key_secret)
    else:
        wrapped_key_secret = dataset_db.encryption_key
        aes_key = await azure.unwrap_aes_with_rsa_key(wrapped_aes_key=wrapped_key_secret, wrapping_key=wrapping_key)

    return DatasetEncryptionKey_Out(dataset_key=b64encode(aes_key).decode("ascii"))


async def create_azure_file_share(dataset_id: PyObjectId):
    """
    Create a file share in Azure

    :param dataset_id: Dataset ID
    :type dataset_id: PyObjectId
    :raises Exception: failed to create file share
    """
    try:
        account_credentials = await azure.authenticate()

        create_response = await azure.create_file_share(
            account_credentials,
            get_secret("azure_storage_resource_group"),
            get_secret("azure_storage_account_name"),
            str(dataset_id),
        )
        if create_response.status != "Success":
            raise Exception(create_response.note)

        # Mark the dataset as active
        await Datasets.update(dataset_id=dataset_id, state=DatasetState.ACTIVE)

    except Exception as exception:
        await Datasets.update(dataset_id=dataset_id, state=DatasetState.ERROR, note=str(exception))
