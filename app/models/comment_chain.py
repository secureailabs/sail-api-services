# -------------------------------------------------------------------------------
# Engineering
# data_model_version.py
# -------------------------------------------------------------------------------
"""Data Model Version used by data federations"""
# -------------------------------------------------------------------------------
# Copyright (C) 2022 Secure Ai Labs, Inc. All Rights Reserved.
# Private and Confidential. Internal Use Only.
#     This software contains proprietary information which shall not
#     be reproduced or transferred to other documents and shall not
#     be disclosed to others for any purpose without
#     prior written permission of Secure Ai Labs, Inc.
# -------------------------------------------------------------------------------

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import Field, StrictStr

from app.models.common import BasicObjectInfo, PyObjectId, SailBaseModel


class CommentChain_Base(SailBaseModel):
    data_model_id: PyObjectId = Field()


class Comment_Db(SailBaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId = Field()
    organization_id: PyObjectId = Field()
    comment: StrictStr = Field()
    time: datetime = Field(default_factory=datetime.utcnow)


class CommentChain_Db(CommentChain_Base):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    creation_time: datetime = Field(default_factory=datetime.utcnow)
    comments: List[Comment_Db] = Field(default_factory=list)


class GetComment_Out(SailBaseModel):
    id: PyObjectId = Field(alias="_id")
    user: BasicObjectInfo = Field()
    organization: BasicObjectInfo = Field()
    comment: StrictStr = Field()
    time: datetime = Field(default_factory=datetime.utcnow)


class GetCommentChain_Out(CommentChain_Base):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    comments: List[GetComment_Out] = Field(default_factory=list)
    data_model_id: PyObjectId = Field()


class AddComment_In(SailBaseModel):
    comment: StrictStr = Field()
