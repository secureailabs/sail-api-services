# -------------------------------------------------------------------------------
# Engineering
# data_model_series.py
# -------------------------------------------------------------------------------
"""APIs to manage data-models-series"""
# -------------------------------------------------------------------------------
# Copyright (C) 2022 Secure Ai Labs, Inc. All Rights Reserved.
# Private and Confidential. Internal Use Only.
#     This software contains proprietary information which shall not
#     be reproduced or transferred to other documents and shall not
#     be disclosed to others for any purpose without
#     prior written permission of Secure Ai Labs, Inc.
# -------------------------------------------------------------------------------

from ast import Dict
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Response, status
from fastapi.encoders import jsonable_encoder

from app.api.authentication import get_current_user
from app.data import operations as data_service
from app.log import log_message
from app.models.authentication import TokenData
from app.models.common import PyObjectId
from app.models.data_model_series import (
    DataModelSeries_Db,
    DataModelSeriesState,
    GetDataModelSeries_Out,
    GetMultipleDataModelSeries_Out,
    RegisterDataModelSeries_In,
    RegisterDataModelSeries_Out,
    UpdateDataModelSeries_In,
)

router = APIRouter()


class DataModelSeries:
    """
    Data model series CRUD operations
    """

    DB_COLLECTION_DATA_MODEL_SERIES = "data-models-series"

    @staticmethod
    async def create(
        data_model_series: DataModelSeries_Db,
    ):
        """
        Create a new data model series

        :param data_model_series: data model series
        :type data_model_series: DataModelSeries_Db
        :return: data model series
        :rtype: DataModelSeries_Db
        """
        return await data_service.insert_one(
            collection=DataModelSeries.DB_COLLECTION_DATA_MODEL_SERIES,
            data=jsonable_encoder(data_model_series),
        )

    @staticmethod
    async def read(
        organization_id: Optional[PyObjectId] = None,
        data_model_series_id: Optional[PyObjectId] = None,
        data_model_dataframe_id: Optional[PyObjectId] = None,
        throw_on_not_found: bool = True,
    ) -> List[DataModelSeries_Db]:
        """
        Read a data model series

        :param data_model_series_id: data model series id
        :type data_model_series_id: PyObjectId
        :return: data model series
        :rtype: DataModelSeries_Db
        """

        data_model_series_list = []

        query = {}
        if data_model_series_id:
            query["_id"] = data_model_series_id
        if organization_id:
            query["organization_id"] = organization_id
        if data_model_dataframe_id:
            query["data_model_dataframe_id"] = data_model_dataframe_id
        if not query:
            raise Exception("Invalid query")

        response = await data_service.find_by_query(
            collection=DataModelSeries.DB_COLLECTION_DATA_MODEL_SERIES,
            query=jsonable_encoder(query),
        )

        if response:
            for data_model_series in response:
                data_model_series_list.append(DataModelSeries_Db(**data_model_series))
        elif throw_on_not_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data model series not found",
            )

        return data_model_series_list

    @staticmethod
    async def update(
        data_model_series_id: PyObjectId,
        organization_id: PyObjectId,
        data_model_series_schema: Optional[Dict] = None,
        state: Optional[DataModelSeriesState] = None,
    ):
        """
        Update a data model series

        :param data_model_series_id: _description_
        :type data_model_series_id: PyObjectId
        :param state: _description_, defaults to None
        :type state: Optional[DataModelSeriesState], optional
        :return: _description_
        :rtype: _type_
        """

        update_request = {}
        if state:
            update_request["$set"] = {"state": state}
        if data_model_series_schema:
            update_request["$set"] = {"schema": data_model_series_schema}

        if not update_request:
            raise Exception("Invalid update request")

        return await data_service.update_many(
            collection=DataModelSeries.DB_COLLECTION_DATA_MODEL_SERIES,
            query={"_id": str(data_model_series_id), "organization_id": str(organization_id)},
            data=update_request,
        )


@router.post(
    path="/data-models-series",
    description="Register a new data model series",
    response_description="Data model series Id",
    response_model=RegisterDataModelSeries_Out,
    response_model_by_alias=False,
    response_model_exclude_unset=True,
    status_code=status.HTTP_201_CREATED,
    operation_id="register_data_model_series",
)
async def register_data_model_series(
    data_model_series_req: RegisterDataModelSeries_In = Body(
        description="Information required for creating data model series"
    ),
    current_user: TokenData = Depends(get_current_user),
) -> RegisterDataModelSeries_Out:
    """
    Register a new data model series

    :param data_model_series_req: information required for provsioning, defaults to Body(...)
    :type data_model_series_req: RegisterDataModelSeries_In, optional
    :param current_user: current user information
    :type current_user: TokenData, optional
    :return: Data model series Id
    :rtype: RegisterDataModelSeries_Out
    """
    # Create a new provision object
    data_model_series_db = DataModelSeries_Db(
        name=data_model_series_req.name,
        description=data_model_series_req.description,
        organization_id=current_user.organization_id,
        series_schema=data_model_series_req.series_schema,
        state=DataModelSeriesState.ACTIVE,
    )

    # Add to the database
    await DataModelSeries.create(data_model_series_db)

    message = f"[Add Data Model dataframe]: user_id:{current_user.id}, data_model_series_id: {data_model_series_db.id}"
    await log_message(message)

    return RegisterDataModelSeries_Out(**data_model_series_db.dict())


@router.get(
    path="/data-models-series/{data_model_series_id}",
    description="Get data model series",
    response_description="Data model series information and list of SCNs",
    response_model=GetDataModelSeries_Out,
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
    operation_id="get_data_model_series_info",
)
async def get_data_model_series_info(
    data_model_series_id: PyObjectId = Path(description="Data model series Id"),
    current_user: TokenData = Depends(get_current_user),
) -> GetDataModelSeries_Out:
    """
    Get data model series information

    :param data_model_series_id: Data model series Id
    :type data_model_series_id: PyObjectId
    :param current_user: current user information, defaults to Depends(get_current_user)
    :type current_user: TokenData, optional
    :raises HTTPException: 404 if data model series not found
    :return: Data model series information and list of SCNs
    :rtype: GetDataModelSeries_Out
    """
    # Get the data model series
    data_model_series_db = await DataModelSeries.read(
        data_model_series_id=data_model_series_id,
        throw_on_not_found=True,
    )

    message = f"[Get Data model series Info]: user_id:{current_user.id}, data_model_series_id: {data_model_series_id}"
    await log_message(message)

    return GetDataModelSeries_Out(**(data_model_series_db[0].dict()))


@router.get(
    path="/data-models-series",
    description="Get all data model series SCNs",
    response_description="All Data model series information for the current organization or data model",
    response_model=GetMultipleDataModelSeries_Out,
    status_code=status.HTTP_200_OK,
    operation_id="get_all_data_model_series_info",
)
async def get_all_data_model_series_info(
    current_user: TokenData = Depends(get_current_user),
) -> GetMultipleDataModelSeries_Out:
    """
    Get all data model series information

    :param data_model_series_id: Data model series Id
    :type data_model_series_id: PyObjectId
    :param current_user: current user information, defaults to Depends(get_current_user)
    :type current_user: TokenData, optional
    :raises HTTPException: 404 if data model series not found
    :return: Data model series information and list of SCNs
    :rtype: GetDataModelSeries_Out
    """
    # Get the data model series
    data_model_series_info = await DataModelSeries.read(organization_id=current_user.organization_id)

    response_list: List[GetDataModelSeries_Out] = []
    for model in data_model_series_info:
        response_list.append(GetDataModelSeries_Out(**model.dict()))

    message = f"[Get All Data model series Info]: user_id:{current_user.id}"
    await log_message(message)

    return GetMultipleDataModelSeries_Out(data_model_series=response_list)


@router.put(
    path="/data-models-series/{data_model_series_id}",
    description="Update data model series",
    response_description="Data model series information",
    response_model=GetDataModelSeries_Out,
    status_code=status.HTTP_200_OK,
    operation_id="update_data_model_series",
)
async def update_data_model_series(
    data_model_series_id: PyObjectId = Path(description="Data model series Id"),
    data_model_series_req: UpdateDataModelSeries_In = Body(..., description="Data model series information"),
    current_user: TokenData = Depends(get_current_user),
) -> Response:
    """
    Update data model series

    :param data_model_series_id: Data model series Id
    :type data_model_series_id: PyObjectId
    :param data_model_series_req: Data model series information
    :type data_model_series_req: UpdateDataModelSeries
    :param current_user: current user information, defaults to Depends(get_current_user)
    :type current_user: TokenData, optional
    :raises HTTPException: 404 if data model series not found
    :return: Data model series information
    :rtype: GetDataModelSeries_Out
    """
    # Update the data model series
    await DataModelSeries.update(
        data_model_series_id=data_model_series_id,
        organization_id=current_user.organization_id,
        data_model_series_schema=data_model_series_req.schema,  # type: ignore
        state=data_model_series_req.state,
    )

    message = f"[Update Data model series]: user_id:{current_user.id}, data_model_series_id: {data_model_series_id}"
    await log_message(message)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    path="/data-models-series/{data_model_series_id}",
    description="Soft delete data model series",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_data_model_series",
)
async def delete_data_model_series(
    data_model_series_id: PyObjectId = Path(description="Data model series Id to delete"),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Soft delete data model series

    :param data_model_series_id: Data model series Id
    :type data_model_series_id: PyObjectId
    :param current_user: current user information, defaults to Depends(get_current_user)
    :type current_user: TokenData, optional
    :raises http_exception: 404 if data model series not found
    :return: None
    :rtype: Response
    """
    await DataModelSeries.update(
        data_model_series_id=data_model_series_id,
        organization_id=current_user.organization_id,
        state=DataModelSeriesState.DELETED,
    )

    message = f"[Delete Data Model dataframe]: user_id:{current_user.id}, data_model_series_id: {data_model_series_id}"
    await log_message(message)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
