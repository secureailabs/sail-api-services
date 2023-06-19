from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_users_out import GetUsersOut
from ...models.http_exception_obj import HTTPExceptionObj
from ...models.validation_error import ValidationError
from ...types import Response


def _get_kwargs(
    organization_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient,
) -> Dict[str, Any]:
    url = "{}/organizations/{organization_id}/users/{user_id}".format(
        client.base_url, organization_id=organization_id, user_id=user_id
    )

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
    }


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Optional[Union[GetUsersOut, HTTPExceptionObj, ValidationError]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetUsersOut.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = ValidationError.from_dict(response.json())

        return response_422
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = HTTPExceptionObj.from_dict(response.json())

        return response_403
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = HTTPExceptionObj.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Client, response: httpx.Response
) -> Response[Union[GetUsersOut, HTTPExceptionObj, ValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[GetUsersOut, HTTPExceptionObj, ValidationError]]:
    """Get User

     Get information about a user

    Args:
        organization_id (str): UUID of the organization
        user_id (str): UUID of the user

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetUsersOut, HTTPExceptionObj, ValidationError]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        user_id=user_id,
        client=client,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[GetUsersOut, HTTPExceptionObj, ValidationError]]:
    """Get User

     Get information about a user

    Args:
        organization_id (str): UUID of the organization
        user_id (str): UUID of the user

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetUsersOut, HTTPExceptionObj, ValidationError]
    """

    return sync_detailed(
        organization_id=organization_id,
        user_id=user_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[GetUsersOut, HTTPExceptionObj, ValidationError]]:
    """Get User

     Get information about a user

    Args:
        organization_id (str): UUID of the organization
        user_id (str): UUID of the user

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetUsersOut, HTTPExceptionObj, ValidationError]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        user_id=user_id,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[GetUsersOut, HTTPExceptionObj, ValidationError]]:
    """Get User

     Get information about a user

    Args:
        organization_id (str): UUID of the organization
        user_id (str): UUID of the user

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetUsersOut, HTTPExceptionObj, ValidationError]
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            user_id=user_id,
            client=client,
        )
    ).parsed
