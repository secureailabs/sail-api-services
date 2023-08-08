# -------------------------------------------------------------------------------
# Engineering
# comment_chain.py
# -------------------------------------------------------------------------------
"""APIs to manage comment chain"""
# -------------------------------------------------------------------------------
# Copyright (C) 2022 Secure Ai Labs, Inc. All Rights Reserved.
# Private and Confidential. Internal Use Only.
#     This software contains proprietary information which shall not
#     be reproduced or transferred to other documents and shall not
#     be disclosed to others for any purpose without
#     prior written permission of Secure Ai Labs, Inc.
# -------------------------------------------------------------------------------

from datetime import datetime, time
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Response, status
from fastapi.encoders import jsonable_encoder
from pydantic import StrictStr

from app.api.authentication import RoleChecker, get_current_user
from app.data import operations as data_service
from app.models.accounts import UserRole
from app.models.authentication import TokenData
from app.models.comment_chain import AddComment_In, Comment_Db, CommentChain_Db, GetComment_Out, GetCommentChain_Out
from app.models.common import PyObjectId
from app.utils import cache

router = APIRouter()


class CommentChain:
    """
    Comment chain CRUD operations
    """

    DB_COLLECTION_COMMENTS_CHAIN = "comment-chain"

    @staticmethod
    async def create(
        comment_chain: CommentChain_Db,
    ):
        """
        Create a new data model

        :param comment_chain: data model
        :type comment_chain: DataModel_Db
        :return: data model
        :rtype: DataModel_Db
        """
        return await data_service.insert_one(
            collection=CommentChain.DB_COLLECTION_COMMENTS_CHAIN,
            data=jsonable_encoder(comment_chain),
        )

    @staticmethod
    async def read(
        query_comment_chain_id: Optional[PyObjectId] = None,
        query_data_model_id: Optional[PyObjectId] = None,
        throw_on_not_found: bool = True,
    ) -> List[CommentChain_Db]:
        """
        Read a data model

        :param comment_chain_id: data model id
        :type comment_chain_id: PyObjectId
        :return: data model
        :rtype: DataModel_Db
        """

        comment_chain_list = []

        query = {}
        if query_comment_chain_id:
            query["_id"] = query_comment_chain_id
        if query_data_model_id:
            query["data_model_id"] = query_data_model_id

        response = await data_service.find_by_query(
            collection=CommentChain.DB_COLLECTION_COMMENTS_CHAIN,
            query=jsonable_encoder(query),
        )

        if response:
            for comment_chain in response:
                comment_chain_list.append(CommentChain_Db(**comment_chain))
        elif throw_on_not_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comment chain not found",
            )

        return comment_chain_list

    @staticmethod
    async def update(
        query_comment_chain_id: PyObjectId,
        query_user_id: Optional[PyObjectId] = None,
        add_comment: Optional[Comment_Db] = None,
        delete_comment_id: Optional[PyObjectId] = None,
    ):
        update_request = {"$set": {}}
        if add_comment:
            update_request["$push"] = {"comments": add_comment}
        if delete_comment_id and query_user_id:
            update_request["$pull"] = {"comments": {"_id": delete_comment_id, "user_id": query_user_id}}
        if delete_comment_id:
            update_request["$pull"] = {"comments": {"_id": delete_comment_id}}

        update_query = {
            "_id": str(query_comment_chain_id),
        }

        update_response = await data_service.update_one(
            collection=CommentChain.DB_COLLECTION_COMMENTS_CHAIN,
            query=update_query,
            data=jsonable_encoder(update_request),
        )

        if update_response.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comment chain not found. No update performed.",
            )


@router.get(
    path="/comment-chains",
    description="Get all the comment chains with mentioned query",
    response_description="Requested comment chain",
    response_model=GetCommentChain_Out,
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_MODEL_EDITOR]))],
    operation_id="get_all_comment_chain",
)
async def get_all_comment_chains(
    data_model_id: Optional[PyObjectId] = Query(
        default=None, description="Data model Id for which to get comment chains"
    ),
    comment_chain_id: Optional[PyObjectId] = Query(default=None, description="Comment chain vesion Id to get"),
    current_user: TokenData = Depends(get_current_user),
) -> GetCommentChain_Out:
    # Get the comment chain
    comment_chain_db_list = await CommentChain.read(
        query_comment_chain_id=comment_chain_id,
        query_data_model_id=data_model_id,
        throw_on_not_found=False,
    )
    comment_chain_db = comment_chain_db_list[0]

    reponse_comments = []
    for comment in comment_chain_db.comments:
        response_comment = GetComment_Out(
            _id=comment.id,
            user=await cache.get_basic_user(comment.user_id),
            organization=await cache.get_basic_orgnization(comment.organization_id),
            comment=comment.comment,
            time=comment.time,
        )
        reponse_comments.append(response_comment)

    response = GetCommentChain_Out(
        _id=comment_chain_db.id,
        data_model_id=comment_chain_db.data_model_id,
        comments=reponse_comments,
    )

    return response


@router.get(
    path="/comment-chains/{comment_chain_id}",
    description="Get a comment chain version",
    response_description="Requested comment chain",
    response_model=GetCommentChain_Out,
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_MODEL_EDITOR]))],
    operation_id="get_comment_chain",
)
async def get_comment_chains(
    comment_chain_id: PyObjectId = Path(description="Comment chain vesion Id to get"),
    current_user: TokenData = Depends(get_current_user),
) -> GetCommentChain_Out:
    # Get the comment chain
    comment_chain_db_list = await CommentChain.read(
        query_comment_chain_id=comment_chain_id,
        throw_on_not_found=False,
    )
    comment_chain_db = comment_chain_db_list[0]

    reponse_comments = []
    for comment in comment_chain_db.comments:
        response_comment = GetComment_Out(
            _id=comment.id,
            user=await cache.get_basic_user(comment.user_id),
            organization=await cache.get_basic_orgnization(comment.organization_id),
            comment=comment.comment,
            time=comment.time,
        )
        reponse_comments.append(response_comment)

    response = GetCommentChain_Out(
        _id=comment_chain_db.id,
        data_model_id=comment_chain_db.data_model_id,
        comments=reponse_comments,
    )

    return response


@router.patch(
    path="/comment-chains/{comment_chain_id}",
    description="Add a comment to a comment chain",
    response_description="Updated comment chain",
    response_model=GetCommentChain_Out,
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_MODEL_EDITOR]))],
    operation_id="add_comment_to_comment_chain",
)
async def add_comment_to_comment_chain(
    comment_chain_id: PyObjectId = Path(description="Comment chain vesion Id to update"),
    add_comment: AddComment_In = Body(description="Comment to add"),
    current_user: TokenData = Depends(get_current_user),
) -> GetCommentChain_Out:
    # Add the comment
    comment = Comment_Db(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        comment=add_comment.comment,
        time=datetime.utcnow(),
    )
    await CommentChain.update(
        query_comment_chain_id=comment_chain_id,
        add_comment=comment,
    )

    # Get the comment chain
    comment_chain_db_list = await CommentChain.read(
        query_comment_chain_id=comment_chain_id,
        throw_on_not_found=True,
    )
    comment_chain_db = comment_chain_db_list[0]

    reponse_comments = []
    for comment in comment_chain_db.comments:
        response_comment = GetComment_Out(
            _id=comment.id,
            user=await cache.get_basic_user(comment.user_id),
            organization=await cache.get_basic_orgnization(comment.organization_id),
            comment=comment.comment,
            time=comment.time,
        )
        reponse_comments.append(response_comment)

    response = GetCommentChain_Out(
        _id=comment_chain_db.id,
        data_model_id=comment_chain_db.data_model_id,
        comments=reponse_comments,
    )

    return response


@router.delete(
    path="/comment-chains/{comment_chain_id}/comments/{comment_id}",
    description="Delete a comment from a comment chain",
    response_description="Updated comment chain",
    response_model=GetCommentChain_Out,
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.DATA_MODEL_EDITOR]))],
    operation_id="delete_comment_from_comment_chain",
)
async def delete_comment_from_comment_chain(
    comment_chain_id: PyObjectId = Path(description="Comment chain vesion Id to update"),
    comment_id: PyObjectId = Path(description="Comment Id to delete"),
    current_user: TokenData = Depends(get_current_user),
) -> GetCommentChain_Out:
    # Ensure that the comment can be deleted only by the user who created it or the data model maintainer
    comment_chain_db_list = await CommentChain.read(
        query_comment_chain_id=comment_chain_id,
        throw_on_not_found=True,
    )
    comment_chain_db = comment_chain_db_list[0]

    # Get the data model maintainer id
    from app.api.data_models import DataModel

    data_model_db_list = await DataModel.read(
        data_model_id=comment_chain_db.data_model_id,
        throw_on_not_found=True,
    )
    data_model_db = data_model_db_list[0]

    # Get the comment
    comment = [comment for comment in comment_chain_db.comments if comment.id == comment_id][0]
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    if comment.user_id != current_user.id and data_model_db.maintainer_organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only the user who created the comment or the data model maintainer can delete it",
        )

    # Delete the comment
    await CommentChain.update(
        query_comment_chain_id=comment_chain_id,
        query_user_id=current_user.id,
        delete_comment_id=comment_id,
    )

    # Get the comment chain
    comment_chain_db_list = await CommentChain.read(
        query_comment_chain_id=comment_chain_id,
        throw_on_not_found=True,
    )
    comment_chain_db = comment_chain_db_list[0]

    reponse_comments = []
    for comment in comment_chain_db.comments:
        response_comment = GetComment_Out(
            _id=comment.id,
            user=await cache.get_basic_user(comment.user_id),
            organization=await cache.get_basic_orgnization(comment.organization_id),
            comment=comment.comment,
            time=comment.time,
        )
        reponse_comments.append(response_comment)

    response = GetCommentChain_Out(
        _id=comment_chain_db.id,
        data_model_id=comment_chain_db.data_model_id,
        comments=reponse_comments,
    )

    return response
