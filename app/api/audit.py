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

from app.api.authentication import get_current_user
from app.models.accounts import UserRole
from app.models.audit import QueryResult
from app.models.authentication import TokenData
from app.utils.secrets import get_secret

router = APIRouter()

audit_server_ip = get_secret("audit_service_ip")

audit_server_endpoint = f"http://{audit_server_ip}:3100/loki/api/v1/query_range"
# audit_server_endpoint = f"http://172.20.100.4:3100/loki/api/v1/query_range"
loki_query_pattern = "| pattern \"<time> - <level> - [<message_type>] {'user_id': '<user_id>', 'request': '<method> <url>', 'response': 'response_code'}\""


########################################################################################################################
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
    user_id: Optional[StrictStr] = Query(default=None, description="query events related to a specific user id"),
    data_id: Optional[StrictStr] = Query(default=None, description="query events related to a specific data id"),
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
    query_raw = locals()
    query = {}
    query_raw.pop("current_user")
    for key in query_raw:
        if query_raw[key]:
            query[key] = query_raw[key]

    label = query.pop("label")
    response = {}

    query_str = f'{{job="{label}"}}'
    query["query"] = query_str

    # Create a query string for Loki
    if "user_id" in query:
        user_id = query.pop("user_id")
        query_str = f'{query_str}{loki_query_pattern} | user_id = "{user_id}"'
        query["query"] = query_str

    # Execute the query asynchronously
    async with aiohttp.ClientSession() as session:
        async with session.get(audit_server_endpoint, params=query) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=response.reason)
            return QueryResult(status="success", data=(await response.json()))
