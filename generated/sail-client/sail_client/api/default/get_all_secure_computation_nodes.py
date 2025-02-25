from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_multiple_secure_computation_node_out import GetMultipleSecureComputationNodeOut
from ...models.http_exception_obj import HTTPExceptionObj
from ...types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
) -> Dict[str, Any]:
    url = "{}/secure-computation-node".format(client.base_url)

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
) -> Optional[Union[GetMultipleSecureComputationNodeOut, HTTPExceptionObj]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetMultipleSecureComputationNodeOut.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = HTTPExceptionObj.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Client, response: httpx.Response
) -> Response[Union[GetMultipleSecureComputationNodeOut, HTTPExceptionObj]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[Union[GetMultipleSecureComputationNodeOut, HTTPExceptionObj]]:
    """Get All Secure Computation Nodes

     Get list of all the secure_computation_node for the current user

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetMultipleSecureComputationNodeOut, HTTPExceptionObj]]
    """

    kwargs = _get_kwargs(
        client=client,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> Optional[Union[GetMultipleSecureComputationNodeOut, HTTPExceptionObj]]:
    """Get All Secure Computation Nodes

     Get list of all the secure_computation_node for the current user

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetMultipleSecureComputationNodeOut, HTTPExceptionObj]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[Union[GetMultipleSecureComputationNodeOut, HTTPExceptionObj]]:
    """Get All Secure Computation Nodes

     Get list of all the secure_computation_node for the current user

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetMultipleSecureComputationNodeOut, HTTPExceptionObj]]
    """

    kwargs = _get_kwargs(
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> Optional[Union[GetMultipleSecureComputationNodeOut, HTTPExceptionObj]]:
    """Get All Secure Computation Nodes

     Get list of all the secure_computation_node for the current user

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetMultipleSecureComputationNodeOut, HTTPExceptionObj]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
