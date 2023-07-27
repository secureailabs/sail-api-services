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

from app.models.common import PyObjectId, SailBaseModel


class DataModelVersionState(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    DELETED = "DELETED"


class SeriesDataModelType(str, Enum):
    SeriesDataModelCategorical = "SeriesDataModelCategorical"
    SeriesDataModelDate = "SeriesDataModelDate"
    SeriesDataModelDateTime = "SeriesDataModelDateTime"
    SeriesDataModelInterval = "SeriesDataModelInterval"
    SeriesDataModelUnique = "SeriesDataModelUnique"


class DataModelVersionBasicInfo(SailBaseModel):
    id: PyObjectId = Field()
    name: str = Field()
    description: str = Field()
    commit_message: str = Field()
    merge_time: datetime = Field()


class DataModelSeriesSchema(SailBaseModel):
    type: SeriesDataModelType = Field()
    list_value: Optional[List[str]]
    unit: Optional[str]
    min: Optional[float]
    max: Optional[float]
    resolution: Optional[float]


class DataModelSeries(SailBaseModel):
    id: PyObjectId = Field()
    name: str = Field()
    description: str = Field()
    series_schema: DataModelSeriesSchema = Field()


class DataModelDataframe(SailBaseModel):
    id: PyObjectId = Field()
    name: str = Field()
    description: str = Field()
    series: List[DataModelSeries] = Field()


class DataModelVersion_Base(SailBaseModel):
    name: str = Field()
    description: str = Field()
    data_model_id: PyObjectId = Field()
    previous_version_id: Optional[PyObjectId] = Field(default=None)


class DataModelVersion_Db(DataModelVersion_Base):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    creation_time: datetime = Field(default_factory=datetime.utcnow)
    last_save_time: datetime = Field(default_factory=datetime.utcnow)
    commit_time: Optional[datetime] = Field(default_factory=None)
    commit_message: Optional[str] = Field(default=None)
    organization_id: PyObjectId = Field()
    user_id: PyObjectId = Field()
    dataframes: List[DataModelDataframe] = Field()
    state: DataModelVersionState = Field()
    revision_history: List[DataModelVersionBasicInfo] = Field(default_factory=list)


class GetDataModelVersion_Out(DataModelVersion_Base):
    id: PyObjectId = Field(alias="_id")
    creation_time: datetime = Field(default_factory=datetime.utcnow)
    last_save_time: datetime = Field(default_factory=datetime.utcnow)
    commit_time: Optional[datetime] = Field(default_factory=None)
    commit_message: Optional[str] = Field(default=None)
    organization_id: PyObjectId = Field()
    user_id: PyObjectId = Field()
    dataframes: List[DataModelDataframe] = Field()
    state: DataModelVersionState = Field()
    revision_history: List[DataModelVersionBasicInfo] = Field(default_factory=list)


class GetMultipleDataModelVersion_Out(SailBaseModel):
    data_model_versions: List[GetDataModelVersion_Out] = Field()


class RegisterDataModelVersion_In(DataModelVersion_Base):
    pass


class RegisterDataModelVersion_Out(SailBaseModel):
    id: PyObjectId = Field(alias="_id")


class UpdateDataModelVersion_In(SailBaseModel):
    state: Optional[DataModelVersionState] = Field(default=None, description="The state of the data model")
    name: Optional[StrictStr] = Field(default=None, description="The name of the data model")
    description: Optional[StrictStr] = Field(default=None, description="The description of the data model")


class CommitDataModelVersion_In(SailBaseModel):
    commit_message: str = Field()


class SaveDataModelVersion_In(SailBaseModel):
    dataframes: List[DataModelDataframe] = Field()
