from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.dataset_encryption_key_out import DatasetEncryptionKeyOut
from ...models.http_exception_obj import HTTPExceptionObj
from ...models.validation_error import ValidationError
from ...types import Response


def _get_kwargs(
    data_federation_id: str,
    dataset_id: str,
    *,
    client: AuthenticatedClient,
) -> Dict[str, Any]:
    url = "{}/data-federations/{data_federation_id}/dataset_key/{dataset_id}".format(
        client.base_url, data_federation_id=data_federation_id, dataset_id=dataset_id
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
) -> Optional[Union[DatasetEncryptionKeyOut, HTTPExceptionObj, ValidationError]]:
    if response.status_code == HTTPStatus.CREATED:
        response_201 = DatasetEncryptionKeyOut.from_dict(response.json())

        return response_201
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = ValidationError.from_dict(response.json())

        return response_422
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = HTTPExceptionObj.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Client, response: httpx.Response
) -> Response[Union[DatasetEncryptionKeyOut, HTTPExceptionObj, ValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    data_federation_id: str,
    dataset_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[DatasetEncryptionKeyOut, HTTPExceptionObj, ValidationError]]:
    """Get Existing Dataset Key

     Return a dataset encryption key by either retrieving and unwrapping

    Args:
        data_federation_id (str): UUID of the Data federation to which the dataset belongs
        dataset_id (str): UUID of the dataset for which the key is being requested

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DatasetEncryptionKeyOut, HTTPExceptionObj, ValidationError]]
    """

    kwargs = _get_kwargs(
        data_federation_id=data_federation_id,
        dataset_id=dataset_id,
        client=client,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    data_federation_id: str,
    dataset_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[DatasetEncryptionKeyOut, HTTPExceptionObj, ValidationError]]:
    """Get Existing Dataset Key

     Return a dataset encryption key by either retrieving and unwrapping

    Args:
        data_federation_id (str): UUID of the Data federation to which the dataset belongs
        dataset_id (str): UUID of the dataset for which the key is being requested

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DatasetEncryptionKeyOut, HTTPExceptionObj, ValidationError]
    """

    return sync_detailed(
        data_federation_id=data_federation_id,
        dataset_id=dataset_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    data_federation_id: str,
    dataset_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[DatasetEncryptionKeyOut, HTTPExceptionObj, ValidationError]]:
    """Get Existing Dataset Key

     Return a dataset encryption key by either retrieving and unwrapping

    Args:
        data_federation_id (str): UUID of the Data federation to which the dataset belongs
        dataset_id (str): UUID of the dataset for which the key is being requested

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DatasetEncryptionKeyOut, HTTPExceptionObj, ValidationError]]
    """

    kwargs = _get_kwargs(
        data_federation_id=data_federation_id,
        dataset_id=dataset_id,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    data_federation_id: str,
    dataset_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[DatasetEncryptionKeyOut, HTTPExceptionObj, ValidationError]]:
    """Get Existing Dataset Key

     Return a dataset encryption key by either retrieving and unwrapping

    Args:
        data_federation_id (str): UUID of the Data federation to which the dataset belongs
        dataset_id (str): UUID of the dataset for which the key is being requested

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DatasetEncryptionKeyOut, HTTPExceptionObj, ValidationError]
    """

    return (
        await asyncio_detailed(
            data_federation_id=data_federation_id,
            dataset_id=dataset_id,
            client=client,
        )
    ).parsed
