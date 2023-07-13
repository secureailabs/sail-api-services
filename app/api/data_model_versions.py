# -------------------------------------------------------------------------------
# Engineering
# data_model_version.py
# -------------------------------------------------------------------------------
"""APIs to manage data-models"""
# -------------------------------------------------------------------------------
# Copyright (C) 2022 Secure Ai Labs, Inc. All Rights Reserved.
# Private and Confidential. Internal Use Only.
#     This software contains proprietary information which shall not
#     be reproduced or transferred to other documents and shall not
#     be disclosed to others for any purpose without
#     prior written permission of Secure Ai Labs, Inc.
# -------------------------------------------------------------------------------

from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Response, status
from fastapi.encoders import jsonable_encoder
from pydantic import StrictStr

from app.api.authentication import RoleChecker, get_current_user
from app.data import operations as data_service
from app.models.accounts import UserRole
from app.models.authentication import TokenData
from app.models.common import PyObjectId
from app.models.data_model_versions import (
    CommitDataModelVersion_In,
    DataModelDataframe,
    DataModelVersion_Db,
    DataModelVersionState,
    GetDataModelVersion_Out,
    GetMultipleDataModelVersion_Out,
    RegisterDataModelVersion_In,
    RegisterDataModelVersion_Out,
    SaveDataModelVersion_In,
    UpdateDataModelVersion_In,
)

router = APIRouter()


class DataModelVersion:
    """
    Data model Version CRUD operations
    """

    DB_COLLECTION_DATA_MODEL_VERSION = "data-model-versions"

    @staticmethod
    async def create(
        data_model: DataModelVersion_Db,
    ):
        """
        Create a new data model

        :param data_model: data model
        :type data_model: DataModel_Db
        :return: data model
        :rtype: DataModel_Db
        """
        return await data_service.insert_one(
            collection=DataModelVersion.DB_COLLECTION_DATA_MODEL_VERSION,
            data=jsonable_encoder(data_model),
        )

    @staticmethod
    async def read(
        name: Optional[StrictStr] = None,
        data_model_id: Optional[PyObjectId] = None,
        data_model_version_id: Optional[PyObjectId] = None,
        organization_id: Optional[PyObjectId] = None,
        user_id: Optional[PyObjectId] = None,
        state: Optional[DataModelVersionState] = None,
        throw_on_not_found: bool = True,
    ) -> List[DataModelVersion_Db]:
        """
        Read a data model

        :param data_model_id: data model id
        :type data_model_id: PyObjectId
        :return: data model
        :rtype: DataModel_Db
        """

        data_model_list = []

        query = {}
        if name:
            query["name"] = name
        if data_model_id:
            query["data_model_id"] = data_model_id
        if data_model_version_id:
            query["_id"] = data_model_version_id
        if organization_id:
            query["organization_id"] = organization_id
        if user_id:
            query["user_id"] = user_id
        if state:
            query["state"] = state.value

        # Don't return deleted data models
        query["state"] = {"$ne": DataModelVersionState.DELETED.value}

        response = await data_service.find_by_query(
            collection=DataModelVersion.DB_COLLECTION_DATA_MODEL_VERSION,
            query=jsonable_encoder(query),
        )

        if response:
            for data_model in response:
                data_model_list.append(DataModelVersion_Db(**data_model))
        elif throw_on_not_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data model not found",
            )

        return data_model_list

    @staticmethod
    async def update(
        data_model_version_id: PyObjectId,
        organization_id: PyObjectId,
        user_id: Optional[PyObjectId] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        state: Optional[DataModelVersionState] = None,
        current_version_id: Optional[PyObjectId] = None,
        dataframes: Optional[List[DataModelDataframe]] = None,
        commit_message: Optional[str] = None,
        commit_time: Optional[datetime] = None,
    ):
        """
        Update a data model

        :param data_model_id: _description_
        :type data_model_id: PyObjectId
        :param state: _description_, defaults to None
        :type state: Optional[DataModelState], optional
        :return: _description_
        :rtype: _type_
        """

        update_request = {"$set": {}}
        if state:
            update_request["$set"]["state"] = state.value
        if name:
            update_request["$set"]["name"] = name
        if description:
            update_request["$set"]["description"] = description
        if current_version_id:
            update_request["$set"]["current_version_id"] = str(current_version_id)
        if dataframes:
            update_request["$set"]["dataframes"] = dataframes
        if commit_message:
            update_request["$set"]["commit_message"] = commit_message
        if commit_time:
            update_request["$set"]["commit_time"] = commit_time

        update_query = {
            "_id": str(data_model_version_id),
            "state": {"$ne": DataModelVersionState.DELETED.value},
        }
        if user_id:
            update_query["user_id"] = str(user_id)
        if organization_id:
            update_query["organization_id"] = str(organization_id)

        update_response = await data_service.update_one(
            collection=DataModelVersion.DB_COLLECTION_DATA_MODEL_VERSION,
            query=update_query,
            data=jsonable_encoder(update_request),
        )

        if update_response.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data model not found. No update performed.",
            )


@router.post(
    path="/data-model-version",
    description="Register a new data model version",
    response_description="Data model version Id",
    response_model=RegisterDataModelVersion_Out,
    response_model_by_alias=False,
    response_model_exclude_unset=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_MODEL_EDITOR]))],
    operation_id="register_data_model_version",
)
async def register_data_model_version(
    data_model_req: RegisterDataModelVersion_In = Body(
        description="Information required for creating data model version"
    ),
    current_user: TokenData = Depends(get_current_user),
) -> RegisterDataModelVersion_Out:
    """
    Register a new data model

    :param data_model_req: information required for provsioning, defaults to Body(...)
    :type data_model_req: RegisterDataModel_In, optional
    :param current_user: current user information
    :type current_user: TokenData, optional
    :return: Data model Id
    :rtype: RegisterDataModel_Out
    """
    from app.api.data_models import DataModel

    # Check if a data model exists
    data_model_list = await DataModel.read(data_model_id=data_model_req.data_model_id, throw_on_not_found=False)
    if not data_model_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data model with id {data_model_req.data_model_id} not found",
        )

    # Previous data model version id can be null only for the first version
    if not data_model_req.previous_version_id and data_model_list[0].current_version_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Previous version id is required for creating a new version",
        )

    # If previous version id is provided, check if it exists and then populate the new version with the previous version data
    dataframes = []
    if data_model_req.previous_version_id:
        previous_version_list = await DataModelVersion.read(data_model_version_id=data_model_req.previous_version_id)
        if not previous_version_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data model version with id {data_model_req.previous_version_id} not found",
            )
        else:
            # TODO: remove the comments for the dataframe copy
            dataframes = previous_version_list[0].dataframes

    # Check if a data model version already exists with the provided name for the data model
    data_model_list = await DataModelVersion.read(
        name=data_model_req.name, data_model_id=data_model_req.data_model_id, throw_on_not_found=False
    )
    if data_model_list:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Data model with name {data_model_req.name} already exists",
        )

    # Create a new data model version object
    data_model_db = DataModelVersion_Db(
        name=data_model_req.name,
        description=data_model_req.description,
        data_model_id=data_model_req.data_model_id,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        previous_version_id=data_model_req.previous_version_id,
        dataframes=dataframes,
        state=DataModelVersionState.DRAFT,
    )

    # Add to the database
    await DataModelVersion.create(data_model_db)

    return RegisterDataModelVersion_Out(_id=data_model_db.id)


@router.get(
    path="/data-model-versions/{data_model_version_id}",
    description="Get data model version",
    response_description="Data model information and list of SCNs",
    response_model=GetDataModelVersion_Out,
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
    operation_id="get_data_model_version",
)
async def get_data_model_version(
    data_model_version_id: PyObjectId = Path(description="Data model Id"),
    current_user: TokenData = Depends(get_current_user),
) -> GetDataModelVersion_Out:
    # Get the data model
    datamodel_db_list = await DataModelVersion.read(
        data_model_version_id=data_model_version_id,
        throw_on_not_found=True,
    )
    datamodel_db = datamodel_db_list[0]

    return GetDataModelVersion_Out(**(datamodel_db.dict()))


@router.get(
    path="/data-model-versions",
    description="Get all data model versions for the current user",
    response_description="List of Data model versions for the current user",
    response_model=GetMultipleDataModelVersion_Out,
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
    operation_id="get_all_data_model_versions",
)
async def get_all_data_model_versions(
    current_user: TokenData = Depends(get_current_user),
) -> GetMultipleDataModelVersion_Out:
    # Get the data model
    datamodel_db_list = await DataModelVersion.read(
        user_id=current_user.id,
        throw_on_not_found=False,
    )
    datamodels = [GetDataModelVersion_Out(**(datamodel_db.dict())) for datamodel_db in datamodel_db_list]

    return GetMultipleDataModelVersion_Out(data_model_versions=datamodels)


@router.patch(
    path="/data-model-versions/{data_model_version_id}/save",
    description="Save the changes made to the current data model",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_MODEL_EDITOR]))],
    operation_id="save_data_model",
)
async def save_data_model(
    data_model_version_id: PyObjectId = Path(description="Data model Id to update"),
    data_model_save_req: SaveDataModelVersion_In = Body(description="Information required for saving data model"),
    current_user: TokenData = Depends(get_current_user),
):
    data_model_version_list = await DataModelVersion.read(
        data_model_version_id=data_model_version_id,
        throw_on_not_found=True,
    )
    data_model_version = data_model_version_list[0]

    # Check if the data model is in draft state
    if data_model_version.state != DataModelVersionState.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Data model version is not in draft state and cannot be updated. Checkout a new version and try again.",
        )

    await DataModelVersion.update(
        data_model_version_id=data_model_version_id,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        dataframes=data_model_save_req.dataframes,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    path="/data-model-versions/{data_model_version_id}/commit",
    description="Commit the changes made to the current data model",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_MODEL_EDITOR]))],
    operation_id="save_data_model_version",
)
async def commit_data_model(
    data_model_version_id: PyObjectId = Path(description="Data model Id to update"),
    data_model_commit_req: CommitDataModelVersion_In = Body(description="Information required for saving data model"),
    current_user: TokenData = Depends(get_current_user),
):
    # Only allow commit if the data model is in draft state
    data_model_version_list = await DataModelVersion.read(
        data_model_version_id=data_model_version_id,
        throw_on_not_found=True,
    )
    data_model_version = data_model_version_list[0]

    # Check if the data model is in draft state
    if data_model_version.state != DataModelVersionState.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Data model version is not in draft state and cannot be updated. Checkout a new version and try again.",
        )

    await DataModelVersion.update(
        data_model_version_id=data_model_version_id,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        commit_message=data_model_commit_req.commit_message,
        commit_time=datetime.utcnow(),
        state=DataModelVersionState.PUBLISHED,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    path="/data-model-versions/{data_model_version_id}",
    description="Soft delete data model version",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_MODEL_EDITOR]))],
    operation_id="delete_data_model_version",
)
async def delete_data_model_version(
    data_model_version_id: PyObjectId = Path(description="Data model vesion Id to delete"),
    current_user: TokenData = Depends(get_current_user),
):
    await DataModelVersion.update(
        data_model_version_id=data_model_version_id,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        state=DataModelVersionState.DELETED,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
