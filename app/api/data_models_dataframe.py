# -------------------------------------------------------------------------------
# Engineering
# data_model_dataframe.py
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

from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Response, status
from fastapi.encoders import jsonable_encoder

from app.api.authentication import RoleChecker, get_current_user
from app.data import operations as data_service
from app.models.accounts import UserRole
from app.models.authentication import TokenData
from app.models.common import PyObjectId
from app.models.data_model_dataframes import (
    DataModelDataframe_Db,
    DataModelDataframeState,
    GetDataModelDataframe_Out,
    GetMultipleDataModelDataframe_Out,
    RegisterDataModelDataframe_In,
    RegisterDataModelDataframe_Out,
    UpdateDataModelDataframe_In,
)

router = APIRouter()


class DataModelDataframe:
    """
    Data model dataframe CRUD operations
    """

    DB_COLLECTION_DATA_MODEL_DATAFRAME = "data-models-dataframe"

    @staticmethod
    async def create(
        data_model_dataframe: DataModelDataframe_Db,
    ):
        """
        Create a new data model dataframe

        :param data_model_dataframe: data model dataframe
        :type data_model_dataframe: DataModelDataframe_Db
        :return: data model dataframe
        :rtype: DataModelDataframe_Db
        """
        return await data_service.insert_one(
            collection=DataModelDataframe.DB_COLLECTION_DATA_MODEL_DATAFRAME,
            data=jsonable_encoder(data_model_dataframe),
        )

    @staticmethod
    async def read(
        organization_id: Optional[PyObjectId] = None,
        data_model_dataframe_id: Optional[PyObjectId] = None,
        data_model_id: Optional[PyObjectId] = None,
        throw_on_not_found: bool = True,
    ) -> List[DataModelDataframe_Db]:
        """
        Read a data model dataframe

        :param data_model_dataframe_id: data model dataframe id
        :type data_model_dataframe_id: PyObjectId
        :return: data model dataframe
        :rtype: DataModelDataframe_Db
        """

        data_model_dataframe_list = []

        query = {}
        if data_model_dataframe_id:
            query["_id"] = data_model_dataframe_id
        if organization_id:
            query["organization_id"] = organization_id
        if data_model_id:
            query["data_model_id"] = data_model_id
        if not query:
            raise Exception("Invalid query")

        query["state"] = {"$ne": DataModelDataframeState.DELETED.value}

        response = await data_service.find_by_query(
            collection=DataModelDataframe.DB_COLLECTION_DATA_MODEL_DATAFRAME,
            query=jsonable_encoder(query),
        )

        if response:
            for data_model_dataframe in response:
                data_model_dataframe_list.append(DataModelDataframe_Db(**data_model_dataframe))
        elif throw_on_not_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data model dataframe not found",
            )

        return data_model_dataframe_list

    @staticmethod
    async def update(
        data_model_dataframe_id: PyObjectId,
        organization_id: PyObjectId,
        name: Optional[str] = None,
        description: Optional[str] = None,
        state: Optional[DataModelDataframeState] = None,
    ):
        """
        Update a data model dataframe

        :param data_model_dataframe_id: _description_
        :type data_model_dataframe_id: PyObjectId
        :param state: _description_, defaults to None
        :type state: Optional[DataModelDataframeState], optional
        :return: _description_
        :rtype: _type_
        """

        update_request = {}
        if state:
            update_request["$set"] = {"state": state.value}
        if name:
            update_request["$set"] = {"name": name}
        if description:
            update_request["$set"] = {"description": description}

        if not update_request:
            raise Exception("Invalid update request")

        update_result = await data_service.update_many(
            collection=DataModelDataframe.DB_COLLECTION_DATA_MODEL_DATAFRAME,
            query={
                "_id": str(data_model_dataframe_id),
                "organization_id": str(organization_id),
                "state": {"$ne": DataModelDataframeState.DELETED.value},
            },
            data=jsonable_encoder(update_request),
        )

        if update_result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data model dataframe update failed",
            )

        return update_result


@router.post(
    path="/data-models-dataframes",
    description="Provision data federation SCNs",
    response_description="Data model dataframe Id and list of SCNs",
    response_model=RegisterDataModelDataframe_Out,
    response_model_by_alias=False,
    response_model_exclude_unset=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_MODEL_EDITOR]))],
    operation_id="register_data_model_dataframe",
)
async def register_data_model_dataframe(
    data_model_dataframe_req: RegisterDataModelDataframe_In = Body(
        description="Information required for creating data model dataframe"
    ),
    current_user: TokenData = Depends(get_current_user),
) -> RegisterDataModelDataframe_Out:
    """
    Register a new data model dataframe

    :param data_model_dataframe_req: information required for provsioning, defaults to Body(...)
    :type data_model_dataframe_req: RegisterDataModelDataframe_In, optional
    :param current_user: current user information
    :type current_user: TokenData, optional
    :return: Data model dataframe Id
    :rtype: RegisterDataModelDataframe_Out
    """
    # Create a new provision object
    data_model_dataframe_db = DataModelDataframe_Db(
        name=data_model_dataframe_req.name,
        description=data_model_dataframe_req.description,
        organization_id=current_user.organization_id,
        data_model_id=data_model_dataframe_req.data_model_id,
        state=DataModelDataframeState.ACTIVE,
    )

    # Add to the database
    await DataModelDataframe.create(data_model_dataframe_db)

    return RegisterDataModelDataframe_Out(**data_model_dataframe_db.dict())


@router.get(
    path="/data-models-dataframes/{data_model_dataframe_id}",
    description="Get data model dataframe",
    response_description="Data model dataframe information and list of SCNs",
    response_model=GetDataModelDataframe_Out,
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
    operation_id="get_data_model_dataframe_info",
)
async def get_data_model_dataframe_info(
    data_model_dataframe_id: PyObjectId = Path(description="Data model dataframe Id"),
    current_user: TokenData = Depends(get_current_user),
) -> GetDataModelDataframe_Out:
    """
    Get data model dataframe information

    :param data_model_dataframe_id: Data model dataframe Id
    :type data_model_dataframe_id: PyObjectId
    :param current_user: current user information, defaults to Depends(get_current_user)
    :type current_user: TokenData, optional
    :raises HTTPException: 404 if data model dataframe not found
    :return: Data model dataframe information and list of SCNs
    :rtype: GetDataModelDataframe_Out
    """
    # Get the data model dataframe
    data_model_dataframe_db = await DataModelDataframe.read(
        data_model_dataframe_id=data_model_dataframe_id,
        throw_on_not_found=True,
    )

    return GetDataModelDataframe_Out(**(data_model_dataframe_db[0].dict()))


@router.get(
    path="/data-models-dataframes",
    description="Get all data model dataframe SCNs",
    response_description="All Data model dataframe information for the current organization or data model",
    response_model=GetMultipleDataModelDataframe_Out,
    status_code=status.HTTP_200_OK,
    operation_id="get_all_data_model_dataframe_info",
)
async def get_all_data_model_dataframe_info(
    data_model_id: Optional[PyObjectId] = Query(default=None, description="UUID of Data Model"),
    current_user: TokenData = Depends(get_current_user),
) -> GetMultipleDataModelDataframe_Out:
    """
    Get all data model dataframe information

    :param data_model_dataframe_id: Data model dataframe Id
    :type data_model_dataframe_id: PyObjectId
    :param current_user: current user information, defaults to Depends(get_current_user)
    :type current_user: TokenData, optional
    :raises HTTPException: 404 if data model dataframe not found
    :return: Data model dataframe information and list of SCNs
    :rtype: GetDataModelDataframe_Out
    """
    if data_model_id:
        data_model_dataframe_info = await DataModelDataframe.read(data_model_id=data_model_id)
    else:
        # Get all the data model dataframes for the current organization
        data_model_dataframe_info = await DataModelDataframe.read(organization_id=current_user.organization_id)

    response_list: List[GetDataModelDataframe_Out] = []
    for model in data_model_dataframe_info:
        response_list.append(GetDataModelDataframe_Out(**model.dict()))

    return GetMultipleDataModelDataframe_Out(data_model_dataframes=response_list)


@router.patch(
    path="/data-models-dataframes/{data_model_dataframe_id}",
    description="Update data model dataframe",
    response_description="Data model dataframe information",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_MODEL_EDITOR]))],
    operation_id="update_data_model_dataframe",
)
async def update_data_model_dataframe(
    data_model_dataframe_id: PyObjectId = Path(description="Data model dataframe Id"),
    data_model_dataframe_req: UpdateDataModelDataframe_In = Body(..., description="Data model dataframe information"),
    current_user: TokenData = Depends(get_current_user),
) -> Response:
    """
    Add or remove series from a data model dataframe

    :param data_model_dataframe_id: Data model dataframe Id
    :type data_model_dataframe_id: PyObjectId
    :param data_model_dataframe_req: Data model dataframe information
    :type data_model_dataframe_req: UpdateDataModelDataframe_In
    :param current_user: current user information, defaults to Depends(get_current_user)
    :type current_user: TokenData, optional
    :raises http_exception: 404 if data model dataframe not found
    :return: None
    :rtype: Response
    """
    # Update the data model dataframe
    await DataModelDataframe.update(
        data_model_dataframe_id=data_model_dataframe_id,
        organization_id=current_user.organization_id,
        name=data_model_dataframe_req.name,
        description=data_model_dataframe_req.description,
        state=data_model_dataframe_req.state,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    path="/data-models-dataframes/{data_model_dataframe_id}",
    description="Soft delete data model dataframe",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_MODEL_EDITOR]))],
    operation_id="delete_data_model_dataframe",
)
async def delete_data_model_dataframe(
    data_model_dataframe_id: PyObjectId = Path(description="Data model dataframe Id to delete"),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Soft delete data model dataframe

    :param data_model_dataframe_id: Data model dataframe Id
    :type data_model_dataframe_id: PyObjectId
    :param current_user: current user information, defaults to Depends(get_current_user)
    :type current_user: TokenData, optional
    :raises http_exception: 404 if data model dataframe not found
    :return: None
    :rtype: Response
    """
    await DataModelDataframe.update(
        data_model_dataframe_id=data_model_dataframe_id,
        organization_id=current_user.organization_id,
        state=DataModelDataframeState.DELETED,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
