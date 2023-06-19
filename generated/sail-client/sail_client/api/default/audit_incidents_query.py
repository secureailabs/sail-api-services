from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.query_result import QueryResult
from ...models.resource import Resource
from ...models.validation_error import ValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    label: str,
    user_id: Union[Unset, None, str] = UNSET,
    resource: Union[Unset, None, Resource] = UNSET,
    dataset_id: Union[Unset, None, str] = UNSET,
    scn_id: Union[Unset, None, str] = UNSET,
    data_mode_id: Union[Unset, None, str] = UNSET,
    start: Union[None, Unset, float, int] = UNSET,
    end: Union[None, Unset, float, int] = UNSET,
    limit: Union[Unset, None, int] = UNSET,
    step: Union[Unset, None, str] = UNSET,
    direction: Union[Unset, None, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/audit-logs".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["label"] = label

    params["user_id"] = user_id

    json_resource: Union[Unset, None, str] = UNSET
    if not isinstance(resource, Unset):
        json_resource = resource.value if resource else None

    params["resource"] = json_resource

    params["dataset_id"] = dataset_id

    params["scn_id"] = scn_id

    params["data_mode_id"] = data_mode_id

    json_start: Union[None, Unset, float, int]
    if isinstance(start, Unset):
        json_start = UNSET
    elif start is None:
        json_start = None

    else:
        json_start = start

    params["start"] = json_start

    json_end: Union[None, Unset, float, int]
    if isinstance(end, Unset):
        json_end = UNSET
    elif end is None:
        json_end = None

    else:
        json_end = end

    params["end"] = json_end

    params["limit"] = limit

    params["step"] = step

    params["direction"] = direction

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
        "params": params,
    }


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[QueryResult, ValidationError]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = QueryResult.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = ValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[QueryResult, ValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    label: str,
    user_id: Union[Unset, None, str] = UNSET,
    resource: Union[Unset, None, Resource] = UNSET,
    dataset_id: Union[Unset, None, str] = UNSET,
    scn_id: Union[Unset, None, str] = UNSET,
    data_mode_id: Union[Unset, None, str] = UNSET,
    start: Union[None, Unset, float, int] = UNSET,
    end: Union[None, Unset, float, int] = UNSET,
    limit: Union[Unset, None, int] = UNSET,
    step: Union[Unset, None, str] = UNSET,
    direction: Union[Unset, None, str] = UNSET,
) -> Response[Union[QueryResult, ValidationError]]:
    """Audit Incidents Query

     query by logQL

    Args:
        label (str):
        user_id (Union[Unset, None, str]): query events related to a specific user
        resource (Union[Unset, None, Resource]): An enumeration.
        dataset_id (Union[Unset, None, str]): query events related to a specific dataset
        scn_id (Union[Unset, None, str]): query events related to a specific scn
        data_mode_id (Union[Unset, None, str]): query events related to a specific data model
        start (Union[None, Unset, float, int]): starting timestamp of the query range
        end (Union[None, Unset, float, int]): ending timestamp of the query range
        limit (Union[Unset, None, int]): query events number limit
        step (Union[Unset, None, str]): query events time interval
        direction (Union[Unset, None, str]): query events order

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[QueryResult, ValidationError]]
    """

    kwargs = _get_kwargs(
        client=client,
        label=label,
        user_id=user_id,
        resource=resource,
        dataset_id=dataset_id,
        scn_id=scn_id,
        data_mode_id=data_mode_id,
        start=start,
        end=end,
        limit=limit,
        step=step,
        direction=direction,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    label: str,
    user_id: Union[Unset, None, str] = UNSET,
    resource: Union[Unset, None, Resource] = UNSET,
    dataset_id: Union[Unset, None, str] = UNSET,
    scn_id: Union[Unset, None, str] = UNSET,
    data_mode_id: Union[Unset, None, str] = UNSET,
    start: Union[None, Unset, float, int] = UNSET,
    end: Union[None, Unset, float, int] = UNSET,
    limit: Union[Unset, None, int] = UNSET,
    step: Union[Unset, None, str] = UNSET,
    direction: Union[Unset, None, str] = UNSET,
) -> Optional[Union[QueryResult, ValidationError]]:
    """Audit Incidents Query

     query by logQL

    Args:
        label (str):
        user_id (Union[Unset, None, str]): query events related to a specific user
        resource (Union[Unset, None, Resource]): An enumeration.
        dataset_id (Union[Unset, None, str]): query events related to a specific dataset
        scn_id (Union[Unset, None, str]): query events related to a specific scn
        data_mode_id (Union[Unset, None, str]): query events related to a specific data model
        start (Union[None, Unset, float, int]): starting timestamp of the query range
        end (Union[None, Unset, float, int]): ending timestamp of the query range
        limit (Union[Unset, None, int]): query events number limit
        step (Union[Unset, None, str]): query events time interval
        direction (Union[Unset, None, str]): query events order

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[QueryResult, ValidationError]
    """

    return sync_detailed(
        client=client,
        label=label,
        user_id=user_id,
        resource=resource,
        dataset_id=dataset_id,
        scn_id=scn_id,
        data_mode_id=data_mode_id,
        start=start,
        end=end,
        limit=limit,
        step=step,
        direction=direction,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    label: str,
    user_id: Union[Unset, None, str] = UNSET,
    resource: Union[Unset, None, Resource] = UNSET,
    dataset_id: Union[Unset, None, str] = UNSET,
    scn_id: Union[Unset, None, str] = UNSET,
    data_mode_id: Union[Unset, None, str] = UNSET,
    start: Union[None, Unset, float, int] = UNSET,
    end: Union[None, Unset, float, int] = UNSET,
    limit: Union[Unset, None, int] = UNSET,
    step: Union[Unset, None, str] = UNSET,
    direction: Union[Unset, None, str] = UNSET,
) -> Response[Union[QueryResult, ValidationError]]:
    """Audit Incidents Query

     query by logQL

    Args:
        label (str):
        user_id (Union[Unset, None, str]): query events related to a specific user
        resource (Union[Unset, None, Resource]): An enumeration.
        dataset_id (Union[Unset, None, str]): query events related to a specific dataset
        scn_id (Union[Unset, None, str]): query events related to a specific scn
        data_mode_id (Union[Unset, None, str]): query events related to a specific data model
        start (Union[None, Unset, float, int]): starting timestamp of the query range
        end (Union[None, Unset, float, int]): ending timestamp of the query range
        limit (Union[Unset, None, int]): query events number limit
        step (Union[Unset, None, str]): query events time interval
        direction (Union[Unset, None, str]): query events order

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[QueryResult, ValidationError]]
    """

    kwargs = _get_kwargs(
        client=client,
        label=label,
        user_id=user_id,
        resource=resource,
        dataset_id=dataset_id,
        scn_id=scn_id,
        data_mode_id=data_mode_id,
        start=start,
        end=end,
        limit=limit,
        step=step,
        direction=direction,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    label: str,
    user_id: Union[Unset, None, str] = UNSET,
    resource: Union[Unset, None, Resource] = UNSET,
    dataset_id: Union[Unset, None, str] = UNSET,
    scn_id: Union[Unset, None, str] = UNSET,
    data_mode_id: Union[Unset, None, str] = UNSET,
    start: Union[None, Unset, float, int] = UNSET,
    end: Union[None, Unset, float, int] = UNSET,
    limit: Union[Unset, None, int] = UNSET,
    step: Union[Unset, None, str] = UNSET,
    direction: Union[Unset, None, str] = UNSET,
) -> Optional[Union[QueryResult, ValidationError]]:
    """Audit Incidents Query

     query by logQL

    Args:
        label (str):
        user_id (Union[Unset, None, str]): query events related to a specific user
        resource (Union[Unset, None, Resource]): An enumeration.
        dataset_id (Union[Unset, None, str]): query events related to a specific dataset
        scn_id (Union[Unset, None, str]): query events related to a specific scn
        data_mode_id (Union[Unset, None, str]): query events related to a specific data model
        start (Union[None, Unset, float, int]): starting timestamp of the query range
        end (Union[None, Unset, float, int]): ending timestamp of the query range
        limit (Union[Unset, None, int]): query events number limit
        step (Union[Unset, None, str]): query events time interval
        direction (Union[Unset, None, str]): query events order

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[QueryResult, ValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            label=label,
            user_id=user_id,
            resource=resource,
            dataset_id=dataset_id,
            scn_id=scn_id,
            data_mode_id=data_mode_id,
            start=start,
            end=end,
            limit=limit,
            step=step,
            direction=direction,
        )
    ).parsed
