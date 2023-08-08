from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_comment_chain_out import GetCommentChainOut
from ...models.validation_error import ValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    data_model_id: Union[Unset, None, str] = UNSET,
    comment_chain_id: Union[Unset, None, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/comment-chains".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["data_model_id"] = data_model_id

    params["comment_chain_id"] = comment_chain_id

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


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Optional[Union[GetCommentChainOut, ValidationError]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetCommentChainOut.from_dict(response.json())

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
) -> Response[Union[GetCommentChainOut, ValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    data_model_id: Union[Unset, None, str] = UNSET,
    comment_chain_id: Union[Unset, None, str] = UNSET,
) -> Response[Union[GetCommentChainOut, ValidationError]]:
    """Get All Comment Chains

     Get all the comment chains with mentioned query

    Args:
        data_model_id (Union[Unset, None, str]): Data model Id for which to get comment chains
        comment_chain_id (Union[Unset, None, str]): Comment chain vesion Id to get

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetCommentChainOut, ValidationError]]
    """

    kwargs = _get_kwargs(
        client=client,
        data_model_id=data_model_id,
        comment_chain_id=comment_chain_id,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    data_model_id: Union[Unset, None, str] = UNSET,
    comment_chain_id: Union[Unset, None, str] = UNSET,
) -> Optional[Union[GetCommentChainOut, ValidationError]]:
    """Get All Comment Chains

     Get all the comment chains with mentioned query

    Args:
        data_model_id (Union[Unset, None, str]): Data model Id for which to get comment chains
        comment_chain_id (Union[Unset, None, str]): Comment chain vesion Id to get

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetCommentChainOut, ValidationError]
    """

    return sync_detailed(
        client=client,
        data_model_id=data_model_id,
        comment_chain_id=comment_chain_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    data_model_id: Union[Unset, None, str] = UNSET,
    comment_chain_id: Union[Unset, None, str] = UNSET,
) -> Response[Union[GetCommentChainOut, ValidationError]]:
    """Get All Comment Chains

     Get all the comment chains with mentioned query

    Args:
        data_model_id (Union[Unset, None, str]): Data model Id for which to get comment chains
        comment_chain_id (Union[Unset, None, str]): Comment chain vesion Id to get

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetCommentChainOut, ValidationError]]
    """

    kwargs = _get_kwargs(
        client=client,
        data_model_id=data_model_id,
        comment_chain_id=comment_chain_id,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    data_model_id: Union[Unset, None, str] = UNSET,
    comment_chain_id: Union[Unset, None, str] = UNSET,
) -> Optional[Union[GetCommentChainOut, ValidationError]]:
    """Get All Comment Chains

     Get all the comment chains with mentioned query

    Args:
        data_model_id (Union[Unset, None, str]): Data model Id for which to get comment chains
        comment_chain_id (Union[Unset, None, str]): Comment chain vesion Id to get

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetCommentChainOut, ValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            data_model_id=data_model_id,
            comment_chain_id=comment_chain_id,
        )
    ).parsed
