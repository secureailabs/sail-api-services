# -------------------------------------------------------------------------------
# Engineering
# data_model.py
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

from typing import Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Response, status
from fastapi.encoders import jsonable_encoder

from app.api.authentication import RoleChecker, get_current_user
from app.api.comment_chains import CommentChain
from app.api.data_model_versions import DataModelVersion
from app.data import operations as data_service
from app.models.accounts import UserRole
from app.models.authentication import TokenData
from app.models.common import PyObjectId
from app.models.data_model_versions import DataModelVersionBasicInfo, DataModelVersionState
from app.models.data_models import (
    DataModel_Db,
    DataModelState,
    GetDataModel_Out,
    GetMultipleDataModel_Out,
    RegisterDataModel_In,
    RegisterDataModel_Out,
    UpdateDataModel_In,
)
from app.utils import cache

router = APIRouter()


class DataModel:
    """
    Data model CRUD operations
    """

    DB_COLLECTION_DATA_MODEL = "data-models"

    @staticmethod
    async def create(
        data_model: DataModel_Db,
    ):
        """
        Create a new data model

        :param data_model: data model
        :type data_model: DataModel_Db
        :return: data model
        :rtype: DataModel_Db
        """
        return await data_service.insert_one(
            collection=DataModel.DB_COLLECTION_DATA_MODEL,
            data=jsonable_encoder(data_model),
        )

    @staticmethod
    async def read(
        data_model_id: Optional[PyObjectId] = None,
        maintainer_organization_id: Optional[PyObjectId] = None,
        name: Optional[str] = None,
        throw_on_not_found: bool = True,
    ) -> List[DataModel_Db]:
        """
        Read a data model

        :param data_model_id: data model id
        :type data_model_id: PyObjectId
        :return: data model
        :rtype: DataModel_Db
        """

        data_model_list = []

        query = {}
        if data_model_id:
            query["_id"] = str(data_model_id)
        if maintainer_organization_id:
            query["maintainer_organization_id"] = str(maintainer_organization_id)
        if name:
            query["name"] = name

        # Don't return deleted data models
        query["state"] = {"$ne": DataModelState.DELETED.value}

        response = await data_service.find_by_query(
            collection=DataModel.DB_COLLECTION_DATA_MODEL,
            query=jsonable_encoder(query),
        )

        if response:
            for data_model in response:
                data_model_list.append(DataModel_Db(**data_model))
        elif throw_on_not_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data model not found",
            )

        return data_model_list

    @staticmethod
    async def update(
        query_data_model_id: PyObjectId,
        query_organization_id: Optional[PyObjectId] = None,
        query_state: Optional[DataModelState] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        state: Optional[DataModelState] = None,
        current_version: Optional[DataModelVersionBasicInfo] = None,
        current_editor_id: Optional[PyObjectId] = None,
        current_editor_organization_id: Optional[PyObjectId] = None,
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
            # if state is being set to draft, there should no current editors
            if state == DataModelState.DRAFT:
                update_request["$set"]["current_editor_id"] = None
                update_request["$set"]["current_editor_organization_id"] = None
        if name:
            update_request["$set"]["name"] = name
        if description:
            update_request["$set"]["description"] = description
        if current_version:
            update_request["$set"]["current_version_id"] = str(current_version.id)
            update_request["$push"] = {"revision_history": current_version}
        if current_editor_id:
            update_request["$set"]["current_editor_id"] = str(current_editor_id)
        if current_editor_organization_id:
            update_request["$set"]["current_editor_organization_id"] = str(current_editor_organization_id)

        update_query = {}
        if query_data_model_id:
            update_query["_id"] = str(query_data_model_id)
        if query_organization_id:
            update_query["maintainer_organization_id"] = str(query_organization_id)

        if query_state:
            update_query["state"] = query_state.value
        else:
            update_query["state"] = {"$ne": DataModelState.DELETED.value}

        update_response = await data_service.update_one(
            collection=DataModel.DB_COLLECTION_DATA_MODEL,
            query=jsonable_encoder(update_query),
            data=jsonable_encoder(update_request),
        )
        if update_response.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data model not found OR No update performed.",
            )


@router.post(
    path="/data-models",
    description="Register a new data model",
    response_description="Data model Id",
    response_model=RegisterDataModel_Out,
    response_model_by_alias=False,
    response_model_exclude_unset=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_MODEL_EDITOR]))],
    operation_id="register_data_model",
)
async def register_data_model(
    data_model_req: RegisterDataModel_In = Body(description="Information required for creating data model"),
    current_user: TokenData = Depends(get_current_user),
) -> RegisterDataModel_Out:
    """
    Register a new data model

    :param data_model_req: information required for provsioning, defaults to Body(...)
    :type data_model_req: RegisterDataModel_In, optional
    :param current_user: current user information
    :type current_user: TokenData, optional
    :return: Data model Id
    :rtype: RegisterDataModel_Out
    """

    # Check if data model with same name exists
    data_model_list = await DataModel.read(
        name=data_model_req.name,
        throw_on_not_found=False,
    )
    if data_model_list:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Data model with name {data_model_req.name} already exists",
        )

    # Create a new data model
    data_model_db = DataModel_Db(
        name=data_model_req.name,
        description=data_model_req.description,
        maintainer_organization_id=current_user.organization_id,
        state=DataModelState.DRAFT,
    )

    # Add to the database
    await DataModel.create(data_model_db)

    # Add a comment chain for the data model
    from app.models.comment_chain import CommentChain_Db

    comment_chain = CommentChain_Db(data_model_id=data_model_db.id)
    await CommentChain.create(comment_chain)

    return RegisterDataModel_Out(_id=data_model_db.id)


@router.get(
    path="/data-models/{data_model_id}",
    description="Get data model",
    response_description="Data model information and list of SCNs",
    response_model=GetDataModel_Out,
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
    operation_id="get_data_model_info",
)
async def get_data_model_info(
    data_model_id: PyObjectId = Path(description="Data model Id"),
    current_user: TokenData = Depends(get_current_user),
) -> GetDataModel_Out:
    """
    Get data model information

    :param data_model_id: Data model Id
    :type data_model_id: PyObjectId
    :param current_user: current user information, defaults to Depends(get_current_user)
    :type current_user: TokenData, optional
    :raises HTTPException: 404 if data model not found
    :return: Data model information and list of SCNs
    :rtype: GetDataModel
    """
    # Get the data model
    datamodel_db_list = await DataModel.read(
        data_model_id=data_model_id,
        throw_on_not_found=True,
    )
    datamodel_db = datamodel_db_list[0]

    return GetDataModel_Out(
        **(datamodel_db.dict()),
        maintainer_organization=await cache.get_basic_orgnization(datamodel_db.maintainer_organization_id),
        current_editor=await cache.get_basic_user(datamodel_db.current_editor_id)
        if datamodel_db.current_editor_id
        else None,
        current_editor_organization=await cache.get_basic_orgnization(datamodel_db.current_editor_organization_id)
        if datamodel_db.current_editor_organization_id
        else None,
    )


@router.get(
    path="/data-models",
    description="Get all data model",
    response_description="All Data model information for the current organization",
    response_model=GetMultipleDataModel_Out,
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
    operation_id="get_all_data_model_info",
)
async def get_all_data_model_info(
    current_user: TokenData = Depends(get_current_user),
) -> GetMultipleDataModel_Out:
    """
    Get all data model information

    :param data_model_id: Data model Id
    :type data_model_id: PyObjectId
    :param current_user: current user information, defaults to Depends(get_current_user)
    :type current_user: TokenData, optional
    :raises HTTPException: 404 if data model not found
    :return: Data model information
    :rtype: GetDataModel
    """
    # Get the data model
    data_model_info = await DataModel.read(
        throw_on_not_found=False,
    )

    response_list: List[GetDataModel_Out] = []
    for model in data_model_info:
        response_list.append(
            GetDataModel_Out(
                **model.dict(),
                maintainer_organization=await cache.get_basic_orgnization(model.maintainer_organization_id),
                current_editor=await cache.get_basic_user(model.current_editor_id) if model.current_editor_id else None,
                current_editor_organization=await cache.get_basic_orgnization(model.current_editor_organization_id)
                if model.current_editor_organization_id
                else None,
            )
        )

    return GetMultipleDataModel_Out(data_models=response_list)


@router.get(
    path="/data-model/{data_model_id}/published-versions",
    description="Get all published data model versions",
    response_description="List of all published Data model versions",
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
    operation_id="get_all_published_data_model_version_names",
)
async def get_all_published_data_model_version_names(
    data_model_id: PyObjectId,
    current_user: TokenData = Depends(get_current_user),
) -> Dict[PyObjectId, str]:
    """
    Get data model information

    :param data_model_id: Data model Id
    :type data_model_id: PyObjectId
    :param current_user: current user information, defaults to Depends(get_current_user)
    :type current_user: TokenData, optional
    :raises HTTPException: 404 if data model not found
    :return: Data model information and list of SCNs
    :rtype: GetDataModel
    """

    # Get the data model
    datamodel_db_list = await DataModelVersion.read(
        data_model_id=data_model_id,
        state=DataModelVersionState.PUBLISHED,
        throw_on_not_found=False,
    )

    return {datamodel_db.id: datamodel_db.name for datamodel_db in datamodel_db_list}


@router.get(
    path="/data-model/{data_model_id}/draft-versions",
    description="Get all draft data model versions",
    response_description="List of all published Data model versions",
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
    operation_id="get_all_draft_data_model_version_names",
)
async def get_all_draft_data_model_version_names(
    data_model_id: PyObjectId,
    current_user: TokenData = Depends(get_current_user),
) -> Dict[PyObjectId, str]:
    """
    Get data model information

    :param data_model_id: Data model Id
    :type data_model_id: PyObjectId
    :param current_user: current user information, defaults to Depends(get_current_user)
    :type current_user: TokenData, optional
    :raises HTTPException: 404 if data model not found
    :return: Data model information and list of SCNs
    :rtype: GetDataModel
    """

    # Get the data model
    datamodel_db_list = await DataModelVersion.read(
        data_model_id=data_model_id,
        user_id=current_user.id,
        state=DataModelVersionState.DRAFT,
        throw_on_not_found=False,
    )

    return {datamodel_db.id: datamodel_db.name for datamodel_db in datamodel_db_list}


@router.patch(
    path="/data-models/{data_model_id}",
    description="Update data model information",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_MODEL_EDITOR]))],
    operation_id="update_data_model",
)
async def update_data_model(
    data_model_id: PyObjectId = Path(description="Data model Id to update"),
    data_model_req: UpdateDataModel_In = Body(description="Information required for updating data model"),
    current_user: TokenData = Depends(get_current_user),
) -> Response:
    """
    Update data model information

    :param data_model_id: Data model Id to update
    :type data_model_id: PyObjectId, optional
    :param data_model_req: Information required for updating data model
    :type data_model_req: UpdateDataModel_In, optional
    :param current_user: current user information
    :type current_user: TokenData, optional
    :return: 204 if successful
    :rtype: Response
    """

    await DataModel.update(
        query_data_model_id=data_model_id,
        query_organization_id=current_user.organization_id,
        name=data_model_req.name,
        description=data_model_req.description,
        state=data_model_req.state,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    path="/data-models/{data_model_id}",
    description="Soft delete data model",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_MODEL_EDITOR]))],
    operation_id="delete_data_model",
)
async def delete_data_model(
    data_model_id: PyObjectId = Path(description="Data model Id to delete"),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Soft delete data model

    :param data_model_id: Data model Id
    :type data_model_id: PyObjectId
    :param current_user: current user information, defaults to Depends(get_current_user)
    :type current_user: TokenData, optional
    :raises http_exception: 404 if data model not found
    :return: None
    :rtype: Response
    """
    await DataModel.update(
        query_data_model_id=data_model_id,
        query_organization_id=current_user.organization_id,
        state=DataModelState.DELETED,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
