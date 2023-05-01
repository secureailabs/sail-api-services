from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_data_federation_provision import GetDataFederationProvision
from ...models.validation_error import ValidationError
from ...types import Response


def _get_kwargs(
    provision_id: str,
    *,
    client: AuthenticatedClient,
) -> Dict[str, Any]:
    url = "{}/data-federations-provsions/{provision_id}".format(client.base_url, provision_id=provision_id)

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
) -> Optional[Union[GetDataFederationProvision, ValidationError]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetDataFederationProvision.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = ValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Client, response: httpx.Response
) -> Response[Union[GetDataFederationProvision, ValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    provision_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[GetDataFederationProvision, ValidationError]]:
    """Get Data Federation Provision Info

     Get data federation provision SCNs

    Args:
        provision_id (str): Data Federation Provision Id

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetDataFederationProvision, ValidationError]]
    """

    kwargs = _get_kwargs(
        provision_id=provision_id,
        client=client,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    provision_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[GetDataFederationProvision, ValidationError]]:
    """Get Data Federation Provision Info

     Get data federation provision SCNs

    Args:
        provision_id (str): Data Federation Provision Id

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetDataFederationProvision, ValidationError]
    """

    return sync_detailed(
        provision_id=provision_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    provision_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[GetDataFederationProvision, ValidationError]]:
    """Get Data Federation Provision Info

     Get data federation provision SCNs

    Args:
        provision_id (str): Data Federation Provision Id

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetDataFederationProvision, ValidationError]]
    """

    kwargs = _get_kwargs(
        provision_id=provision_id,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    provision_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[GetDataFederationProvision, ValidationError]]:
    """Get Data Federation Provision Info

     Get data federation provision SCNs

    Args:
        provision_id (str): Data Federation Provision Id

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetDataFederationProvision, ValidationError]
    """

    return (
        await asyncio_detailed(
            provision_id=provision_id,
            client=client,
        )
    ).parsed
