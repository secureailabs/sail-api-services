from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.add_comment_in import AddCommentIn
from ...models.get_comment_chain_out import GetCommentChainOut
from ...models.validation_error import ValidationError
from ...types import Response


def _get_kwargs(
    comment_chain_id: str,
    *,
    client: AuthenticatedClient,
    json_body: AddCommentIn,
) -> Dict[str, Any]:
    url = "{}/comment-chains/{comment_chain_id}".format(client.base_url, comment_chain_id=comment_chain_id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_json_body = json_body.to_dict()

    return {
        "method": "patch",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
        "json": json_json_body,
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
    comment_chain_id: str,
    *,
    client: AuthenticatedClient,
    json_body: AddCommentIn,
) -> Response[Union[GetCommentChainOut, ValidationError]]:
    """Add Comment To Comment Chain

     Add a comment to a comment chain

    Args:
        comment_chain_id (str): Comment chain vesion Id to update
        json_body (AddCommentIn):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetCommentChainOut, ValidationError]]
    """

    kwargs = _get_kwargs(
        comment_chain_id=comment_chain_id,
        client=client,
        json_body=json_body,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    comment_chain_id: str,
    *,
    client: AuthenticatedClient,
    json_body: AddCommentIn,
) -> Optional[Union[GetCommentChainOut, ValidationError]]:
    """Add Comment To Comment Chain

     Add a comment to a comment chain

    Args:
        comment_chain_id (str): Comment chain vesion Id to update
        json_body (AddCommentIn):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetCommentChainOut, ValidationError]
    """

    return sync_detailed(
        comment_chain_id=comment_chain_id,
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    comment_chain_id: str,
    *,
    client: AuthenticatedClient,
    json_body: AddCommentIn,
) -> Response[Union[GetCommentChainOut, ValidationError]]:
    """Add Comment To Comment Chain

     Add a comment to a comment chain

    Args:
        comment_chain_id (str): Comment chain vesion Id to update
        json_body (AddCommentIn):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetCommentChainOut, ValidationError]]
    """

    kwargs = _get_kwargs(
        comment_chain_id=comment_chain_id,
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    comment_chain_id: str,
    *,
    client: AuthenticatedClient,
    json_body: AddCommentIn,
) -> Optional[Union[GetCommentChainOut, ValidationError]]:
    """Add Comment To Comment Chain

     Add a comment to a comment chain

    Args:
        comment_chain_id (str): Comment chain vesion Id to update
        json_body (AddCommentIn):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetCommentChainOut, ValidationError]
    """

    return (
        await asyncio_detailed(
            comment_chain_id=comment_chain_id,
            client=client,
            json_body=json_body,
        )
    ).parsed
