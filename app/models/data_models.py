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


class DataModelState(Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    DELETED = "DELETED"


class DataModel_Base(SailBaseModel):
    name: str = Field()
    description: str = Field()


class DataModel_Db(DataModel_Base):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    creation_time: datetime = Field(default_factory=datetime.utcnow)
    organization_id: PyObjectId = Field(...)
    data_model_dataframes: List[PyObjectId] = Field(...)
    state: DataModelState = Field(...)


class GetDataModel_Out(DataModel_Base):
    id: PyObjectId = Field(alias="_id")
    creation_time: datetime = Field(default_factory=datetime.utcnow)
    organization_id: PyObjectId = Field(...)
    data_model_dataframes: List[BasicObjectInfo] = Field(...)
    state: DataModelState = Field(...)


class GetMultipleDataModel_Out(SailBaseModel):
    data_models: List[GetDataModel_Out] = Field(...)


class RegisterDataModel_In(DataModel_Base):
    pass


class RegisterDataModel_Out(SailBaseModel):
    id: PyObjectId = Field(alias="_id")


class UpdateDataModel_In(SailBaseModel):
    data_model_dataframe_to_add: Optional[List[PyObjectId]] = Field(
        description="The data_model_dataframes to add to the data model"
    )
    data_model_dataframe_to_remove: Optional[List[PyObjectId]] = Field(
        description="The data_model_dataframes to remove from the data model"
    )
    state: Optional[DataModelState] = Field(description="The state of the data model")
