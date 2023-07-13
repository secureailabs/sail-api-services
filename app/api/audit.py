# -------------------------------------------------------------------------------
# Engineering
# audit.py
# -------------------------------------------------------------------------------
"""APIs to query audit logs"""
# -------------------------------------------------------------------------------
# Copyright (C) 2022 Secure Ai Labs, Inc. All Rights Reserved.
# Private and Confidential. Internal Use Only.
#     This software contains proprietary information which shall not
#     be reproduced or transferred to other documents and shall not
#     be disclosed to others for any purpose without
#     prior written permission of Secure Ai Labs, Inc.
# -------------------------------------------------------------------------------

from typing import Optional, Union

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import StrictStr

from app.api.accounts import get_user
from app.api.authentication import get_current_user
from app.api.data_federations import get_data_federation
from app.api.data_models import DataModel
from app.api.datasets import Datasets
from app.api.secure_computation_nodes import SecureComputationNode
from app.models.accounts import UserRole
from app.models.audit import QueryResult
from app.models.authentication import TokenData
from app.models.common import PyObjectId
from app.utils.logging import Resource
from app.utils.secrets import get_secret

router = APIRouter()

audit_server_ip = get_secret("audit_service_ip")

audit_server_endpoint = f"http://{audit_server_ip}:3100/loki/api/v1/query_range"
loki_query_pattern = "| json "


@router.get(
    path="/audit-logs",
    description="query by logQL",
    response_description="audit log by stream",
    response_model=QueryResult,
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
    operation_id="audit_incidents_query",
)
async def audit_incidents_query(
    label: StrictStr,
    user_id: Optional[PyObjectId] = Query(default=None, description="query events related to a specific user"),
    resource: Resource = Query(default=None, description="query events related to a specific resource"),
    dataset_id: Optional[PyObjectId] = Query(default=None, description="query events related to a specific dataset"),
    scn_id: Optional[PyObjectId] = Query(default=None, description="query events related to a specific scn"),
    data_model_id: Optional[PyObjectId] = Query(
        default=None, description="query events related to a specific data model"
    ),
    data_federation_id: Optional[PyObjectId] = Query(
        default=None, description="query events related to a specific data federation"
    ),
    start: Optional[Union[int, float]] = Query(default=None, description="starting timestamp of the query range"),
    end: Optional[Union[int, float]] = Query(default=None, description="ending timestamp of the query range"),
    limit: Optional[int] = Query(default=None, description="query events number limit"),
    step: Optional[StrictStr] = Query(default=None, description="query events time interval"),
    direction: Optional[StrictStr] = Query(default=None, description="query events order"),
    current_user: TokenData = Depends(get_current_user),
):
    """
    perform a query on audit log

    :param label: label of the query event type, either "user_activity" for platform logs or "computation" for scn logs.
    :type label: StrictStr
    :param user_id: query events related to a specific userID, optional
    :type user_id: Optional[StrictStr], optional
    :param data_id: query events related to a specific dataID, optional
    :type data_id: Optional[StrictStr], optional
    :param start: query starting timestamp, unix epoch format, default is an hour ago.
    :type start: Optional[Union[int, float]], optional
    :param end: query ending timestamp, unix epoch format, default is now.
    :type end: Optional[Union[int, float]], optional
    :param limit: number of events limit returned per query, default is 100.
    :type limit: Optional[int], optional
    :param step: time interval for query events
    :type step: Optional[StrictStr], optional
    :param direction: query events order, either "backward" or "forward"
    :type direction: Optional[StrictStr], optional
    :param current_user: current user who perform the query
    :type current_user: TokenData, optional
    :return: query results
    :rtype: dict(json)
    """

    # Create a query string for Loki
    query_str = f'{{job="{label}"}}'

    # Add parameters
    query_str = f"{query_str} {loki_query_pattern}"

    if user_id:
        query_str = f'{query_str} | user_id="{user_id}"'

    check_if_role_allows(current_user, resource)

    await check_resource_ownership(
        current_user=current_user,
        resource=resource,
        dataset_id=dataset_id,
        scn_id=scn_id,
        data_model_id=data_model_id,
        user_id=user_id,
        data_federation_id=data_federation_id,
    )

    query_str = create_queries_for_resource(
        resource=resource,
        query_str=query_str,
        dataset_id=dataset_id,
        scn_id=scn_id,
        data_model_id=data_model_id,
        user_id=user_id,
        data_federation_id=data_federation_id,
    )

    # Add optional parameters
    if limit:
        query_str = f"{query_str} | limit {limit}"
    if start:
        query_str = f"{query_str} | start {start}"
    if end:
        query_str = f"{query_str} | end {end}"
    if step:
        query_str = f"{query_str} | step {step}"
    if direction:
        query_str = f"{query_str} | direction {direction}"

    # Create a query for Loki
    query = {"query": query_str}

    # Execute the query asynchronously
    async with aiohttp.ClientSession() as session:
        print("audit_server_endpoint", audit_server_endpoint)
        print("audit_server_endpoint", query)
        async with session.get(audit_server_endpoint, params=query) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=response.reason)
            # return QueryResult(status="success", data=(await response.text()))
            return QueryResult(status="success", data=(await response.json()))


def check_if_role_allows(current_user: TokenData, resource: Resource):
    if UserRole.SAIL_ADMIN in current_user.roles:
        return
    elif Resource.DATASET == resource and UserRole.DATA_SUBMITTER in current_user.roles:
        return
    elif Resource.SECURE_COMPUTATION_NODE == resource and UserRole.RESEARCHER in current_user.roles:
        return
    elif Resource.DATA_MODEL == resource and UserRole.DATA_MODEL_EDITOR in current_user.roles:
        return
    elif Resource.USER_ACTIVITY == resource and (
        UserRole.USER in current_user.roles or UserRole.ORGANIZATION_ADMIN in current_user.roles
    ):
        return
    elif Resource.DATA_FEDERATION == resource and UserRole.PAG_ADMIN in current_user.roles:
        return
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User role does not allow to query this resource"
        )


def create_queries_for_resource(
    resource: Resource,
    query_str: str,
    dataset_id: Optional[PyObjectId],
    scn_id: Optional[PyObjectId],
    data_model_id: Optional[PyObjectId],
    user_id: Optional[PyObjectId],
    data_federation_id: Optional[PyObjectId],
):
    if resource == Resource.DATASET and dataset_id:
        query_str = create_query_for_dataset(query_str, dataset_id)
    elif resource == Resource.SECURE_COMPUTATION_NODE and scn_id:
        query_str = f'{query_str} | scn_id="{str(scn_id)}"'
    elif resource == Resource.DATA_MODEL and data_model_id:
        query_str = f'{query_str} | data_model_id="{str(data_model_id)}"'
    elif resource == Resource.USER_ACTIVITY and user_id:
        query_str = f"{query_str}"
    elif resource == Resource.DATA_FEDERATION and data_federation_id:
        query_str = create_query_for_data_federation(query_str, data_federation_id)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid resource or resource ID")
    return query_str


async def check_resource_ownership(
    current_user: TokenData,
    resource: Resource,
    dataset_id: Optional[PyObjectId],
    scn_id: Optional[PyObjectId],
    data_model_id: Optional[PyObjectId],
    user_id: Optional[PyObjectId],
    data_federation_id: Optional[PyObjectId],
):
    # SAIL_ADMIN can query all resources
    if UserRole.SAIL_ADMIN in current_user.roles:
        return

    # Only allow dataset owner to query dataset events
    if resource == Resource.DATASET and dataset_id:
        dataset = await Datasets.read(dataset_id=dataset_id, organization_id=current_user.organization_id)
        if not dataset:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Dataset does not belong to the user")

    # Only allow SCN owner to query SCN events
    elif resource == Resource.SECURE_COMPUTATION_NODE and scn_id:
        await SecureComputationNode.read(
            secure_computation_node_id=scn_id,
            researcher_organization_id=current_user.organization_id,
            researcher_user_id=current_user.id,
        )

    # Only allow data model owner to query data model events
    elif resource == Resource.DATA_MODEL and data_model_id:
        await DataModel.read(data_model_id=data_model_id, organization_id=current_user.organization_id)

    # Only user or organization admin can query user activity
    elif resource == Resource.USER_ACTIVITY and user_id:
        if UserRole.ORGANIZATION_ADMIN in current_user.roles:
            # check if the user belongs to the same organization
            user = await get_user(
                organization_id=current_user.organization_id, user_id=user_id, current_user=current_user
            )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="User does not belong to the organization"
                )
        elif UserRole.USER in current_user.roles:
            if current_user.id != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User can only query own activity")

    # Only PAG admin can query data federation events
    elif resource == Resource.DATA_FEDERATION and data_federation_id:
        data_federation = await get_data_federation(data_federation_id=data_federation_id, current_user=current_user)
        if not data_federation:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Data federation not found")

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid resource")


def create_query_for_dataset(query_str: str, dataset_id: PyObjectId):
    query_str = f'{query_str} | url=~"/datasets/{str(dataset_id)}.*"'
    query_str = f'{query_str} | method=~"POST|PUT|DELETE"'
    return query_str


def create_query_for_data_federation(query_str: str, data_federation_id: PyObjectId):
    query_str = f'{query_str} | url=~"/data-federations/{str(data_federation_id)}.*"'
    query_str = f'{query_str} | method=~"POST|PUT|DELETE"'
    return query_str


def create_query_for_secure_computation_node(query_str: str, scn_id: PyObjectId):
    query_str = f'{query_str} | url=~"/secure-computation-nodes/{str(scn_id)}.*"'
    query_str = f'{query_str} | method=~"POST|PUT|DELETE"'
    return query_str
