# -------------------------------------------------------------------------------
# Engineering
# data_federations.py
# -------------------------------------------------------------------------------
"""Models used by data federations"""
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

from pydantic import Field

from app.models.common import BasicObjectInfo, PyObjectId, SailBaseModel


class DataModelDataframeState(Enum):
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"


class DataModelDataframe_Base(SailBaseModel):
    data_federation_id: PyObjectId = Field()


class DataModelDataframe_Db(DataModelDataframe_Base):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    creation_time: datetime = Field(default_factory=datetime.utcnow)
    organization_id: PyObjectId = Field()
    series: List[PyObjectId] = Field()
    state: DataModelDataframeState = Field()


class GetDataModelDataframe(DataModelDataframe_Base):
    id: PyObjectId = Field(alias="_id")
    creation_time: datetime = Field(default_factory=datetime.utcnow)
    organization_id: PyObjectId = Field()
    series: List[BasicObjectInfo] = Field()
    state: DataModelDataframeState = Field()


class GetMultipleDataModelDataframe_Out(SailBaseModel):
    data_model_dataframes: List[GetDataModelDataframe] = Field()


class RegisterDataModelDataframe_In(DataModelDataframe_Base):
    pass


class RegisterDataModelDataframe_Out(DataModelDataframe_Base):
    id: PyObjectId = Field(alias="_id")
    creation_time: datetime = Field()
    organization_id: PyObjectId = Field()
    series: List[BasicObjectInfo] = Field()
    state: DataModelDataframeState = Field()


class UpdateDataModelDataframe_In(SailBaseModel):
    data_model_series_to_add: Optional[List[PyObjectId]] = Field(default=None)
    data_model_series_to_remove: Optional[List[PyObjectId]] = Field(default=None)
    state: Optional[DataModelDataframeState] = Field(default=None)
