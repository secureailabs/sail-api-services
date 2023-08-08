# -------------------------------------------------------------------------------
# Engineering
# data_models.py
# -------------------------------------------------------------------------------
"""Data Models used by data federations"""
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
from app.models.data_model_versions import DataModelVersionBasicInfo


class DataModelState(str, Enum):
    DRAFT = "DRAFT"
    CHECKED_OUT = "CHECKED_OUT"
    PUBLISHED = "PUBLISHED"
    DELETED = "DELETED"


class DataModel_Base(SailBaseModel):
    name: str = Field()
    description: str = Field()
    tags: List[str] = Field(default_factory=list)


class DataModel_Db(DataModel_Base):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    creation_time: datetime = Field(default_factory=datetime.utcnow)
    maintainer_organization_id: PyObjectId = Field()
    current_version_id: PyObjectId = Field(default=None)
    revision_history: List[DataModelVersionBasicInfo] = Field(default_factory=list)
    state: DataModelState = Field()
    current_editor_id: Optional[PyObjectId] = Field(default=None)
    current_editor_organization_id: Optional[PyObjectId] = Field(default=None)


class GetDataModel_Out(DataModel_Base):
    id: PyObjectId = Field(alias="_id")
    creation_time: datetime = Field(default_factory=datetime.utcnow)
    maintainer_organization: BasicObjectInfo = Field()
    current_version_id: Optional[PyObjectId] = Field()
    revision_history: List[DataModelVersionBasicInfo] = Field(default_factory=list)
    state: DataModelState = Field()
    current_editor: Optional[BasicObjectInfo] = Field(default=None)
    current_editor_organization: Optional[BasicObjectInfo] = Field(default=None)


class GetMultipleDataModel_Out(SailBaseModel):
    data_models: List[GetDataModel_Out] = Field()


class RegisterDataModel_In(DataModel_Base):
    pass


class RegisterDataModel_Out(SailBaseModel):
    id: PyObjectId = Field(alias="_id")


class UpdateDataModel_In(SailBaseModel):
    state: Optional[DataModelState] = Field(default=None, description="The state of the data model")
    name: Optional[StrictStr] = Field(default=None, description="The name of the data model")
    description: Optional[StrictStr] = Field(default=None, description="The description of the data model")
