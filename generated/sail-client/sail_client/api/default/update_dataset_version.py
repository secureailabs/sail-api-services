from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_exception_obj import HTTPExceptionObj
from ...models.update_dataset_version_in import UpdateDatasetVersionIn
from ...models.validation_error import ValidationError
from ...types import Response


def _get_kwargs(
    dataset_version_id: str,
    *,
    client: AuthenticatedClient,
    json_body: UpdateDatasetVersionIn,
) -> Dict[str, Any]:
    url = "{}/dataset-versions/{dataset_version_id}".format(client.base_url, dataset_version_id=dataset_version_id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_json_body = json_body.to_dict()

    return {
        "method": "put",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
        "json": json_json_body,
    }


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Optional[Union[Any, HTTPExceptionObj, ValidationError]]:
    if response.status_code == HTTPStatus.NO_CONTENT:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = ValidationError.from_dict(response.json())

        return response_422
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = HTTPExceptionObj.from_dict(response.json())

        return response_404
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = HTTPExceptionObj.from_dict(response.json())

        return response_403
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Client, response: httpx.Response
) -> Response[Union[Any, HTTPExceptionObj, ValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    dataset_version_id: str,
    *,
    client: AuthenticatedClient,
    json_body: UpdateDatasetVersionIn,
) -> Response[Union[Any, HTTPExceptionObj, ValidationError]]:
    """Update Dataset Version

     Update dataset information

    Args:
        dataset_version_id (str): UUID of the dataset version
        json_body (UpdateDatasetVersionIn):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPExceptionObj, ValidationError]]
    """

    kwargs = _get_kwargs(
        dataset_version_id=dataset_version_id,
        client=client,
        json_body=json_body,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    dataset_version_id: str,
    *,
    client: AuthenticatedClient,
    json_body: UpdateDatasetVersionIn,
) -> Optional[Union[Any, HTTPExceptionObj, ValidationError]]:
    """Update Dataset Version

     Update dataset information

    Args:
        dataset_version_id (str): UUID of the dataset version
        json_body (UpdateDatasetVersionIn):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPExceptionObj, ValidationError]
    """

    return sync_detailed(
        dataset_version_id=dataset_version_id,
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    dataset_version_id: str,
    *,
    client: AuthenticatedClient,
    json_body: UpdateDatasetVersionIn,
) -> Response[Union[Any, HTTPExceptionObj, ValidationError]]:
    """Update Dataset Version

     Update dataset information

    Args:
        dataset_version_id (str): UUID of the dataset version
        json_body (UpdateDatasetVersionIn):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPExceptionObj, ValidationError]]
    """

    kwargs = _get_kwargs(
        dataset_version_id=dataset_version_id,
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    dataset_version_id: str,
    *,
    client: AuthenticatedClient,
    json_body: UpdateDatasetVersionIn,
) -> Optional[Union[Any, HTTPExceptionObj, ValidationError]]:
    """Update Dataset Version

     Update dataset information

    Args:
        dataset_version_id (str): UUID of the dataset version
        json_body (UpdateDatasetVersionIn):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPExceptionObj, ValidationError]
    """

    return (
        await asyncio_detailed(
            dataset_version_id=dataset_version_id,
            client=client,
            json_body=json_body,
        )
    ).parsed
