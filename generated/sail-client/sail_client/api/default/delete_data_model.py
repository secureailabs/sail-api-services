from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.validation_error import ValidationError
from ...types import Response


def _get_kwargs(
    data_model_id: str,
    *,
    client: AuthenticatedClient,
) -> Dict[str, Any]:
    url = "{}/data-models/{data_model_id}".format(client.base_url, data_model_id=data_model_id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "method": "delete",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
    }


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[Any, ValidationError]]:
    if response.status_code == HTTPStatus.NO_CONTENT:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = ValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[Any, ValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    data_model_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, ValidationError]]:
    """Delete Data Model

     Soft delete data model

    Args:
        data_model_id (str): Data model Id to delete

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ValidationError]]
    """

    kwargs = _get_kwargs(
        data_model_id=data_model_id,
        client=client,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    data_model_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, ValidationError]]:
    """Delete Data Model

     Soft delete data model

    Args:
        data_model_id (str): Data model Id to delete

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ValidationError]
    """

    return sync_detailed(
        data_model_id=data_model_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    data_model_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, ValidationError]]:
    """Delete Data Model

     Soft delete data model

    Args:
        data_model_id (str): Data model Id to delete

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ValidationError]]
    """

    kwargs = _get_kwargs(
        data_model_id=data_model_id,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    data_model_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, ValidationError]]:
    """Delete Data Model

     Soft delete data model

    Args:
        data_model_id (str): Data model Id to delete

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ValidationError]
    """

    return (
        await asyncio_detailed(
            data_model_id=data_model_id,
            client=client,
        )
    ).parsed
