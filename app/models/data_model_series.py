# -------------------------------------------------------------------------------
# Engineering
# data_federations.py
# -------------------------------------------------------------------------------
"""Series Data Models used by data models dataframes"""
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
from typing import Dict, List, Optional

from pydantic import Field

from app.models.common import BasicObjectInfo, PyObjectId, SailBaseModel


class DataModelSeriesState(Enum):
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"


class DataModelSeries_Base(SailBaseModel):
    data_model_dataframe_id: PyObjectId = Field()


class DataModelSeries_Db(DataModelSeries_Base):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    creation_time: datetime = Field(default_factory=datetime.utcnow)
    organization_id: PyObjectId = Field()
    schema: Dict = Field()
    state: DataModelSeriesState = Field()


class GetDataModelSeries(DataModelSeries_Base):
    id: PyObjectId = Field(alias="_id")
    creation_time: datetime = Field(default_factory=datetime.utcnow)
    organization_id: PyObjectId = Field()
    schema: Dict = Field()
    state: DataModelSeriesState = Field()


class GetMultipleDataModelSeries_Out(SailBaseModel):
    data_model_series: List[GetDataModelSeries] = Field()


class RegisterDataModelSeries_In(DataModelSeries_Base):
    pass


class RegisterDataModelSeries_Out(DataModelSeries_Base):
    id: PyObjectId = Field(alias="_id")
    creation_time: datetime = Field()
    organization_id: PyObjectId = Field()
    state: DataModelSeriesState = Field()
    schema: Dict = Field()


class UpdateDataModelSeries_In(SailBaseModel):
    schema: Optional[Dict] = Field(default=None)
    state: Optional[DataModelSeriesState] = Field(default=None)
