# -------------------------------------------------------------------------------
# Engineering
# cache.py
# -------------------------------------------------------------------------------
"""Get the BasicObject with id and name for an id"""
# -------------------------------------------------------------------------------
# Copyright (C) 2022 Secure Ai Labs, Inc. All Rights Reserved.
# Private and Confidential. Internal Use Only.
#     This software contains proprietary information which shall not
#     be reproduced or transferred to other documents and shall not
#     be disclosed to others for any purpose without
#     prior written permission of Secure Ai Labs, Inc.
# -------------------------------------------------------------------------------

from typing import Dict, Union

from app.data import operations as data_service
from app.models.common import BasicObjectInfo, PyObjectId

GLOBAL_CACHE: Dict[PyObjectId, BasicObjectInfo] = {}

DB_COLLECTION_ORGANIZATIONS = "organizations"
DB_COLLECTION_USERS = "users"
DB_COLLECTION_DATA_FEDERATIONS = "data-federations"
DB_COLLECTION_INVITES = "data-federation-invites"
DB_COLLECTION_DATA_MODEL_DATAFRAME = "data-models-dataframe"
DB_COLLECTION_DATA_MODEL_SERIES = "data-models-series"
DB_COLLECTION_DATA_MODEL = "data-models"
DB_COLLECTION_DATASET_VERSIONS = "dataset-versions"
DB_COLLECTION_DATASETS = "datasets"
DB_COLLECTION_SECURE_COMPUTATION_NODE = "secure-computation-node"


def get_basic_object(id: PyObjectId) -> Union[BasicObjectInfo, None]:
    if id in GLOBAL_CACHE:
        return GLOBAL_CACHE[id]
    else:
        return None


async def get_basic_user(id: PyObjectId) -> BasicObjectInfo:
    basic_object = get_basic_object(id)
    if basic_object is None:
        # Get the user from the database
        object = await data_service.find_one(DB_COLLECTION_ORGANIZATIONS, {"_id": str(id)})
        if not object:
            raise Exception("Organization not found")
        basic_object = BasicObjectInfo(id=id, name=object["name"])
        # Add the user to the cache
        GLOBAL_CACHE[id] = basic_object
    return basic_object


def get_basic_data_model(id: PyObjectId) -> BasicObjectInfo:
    pass


def get_basic_data_model_dataframe(id: PyObjectId) -> BasicObjectInfo:
    pass


def get_basic_data_model_series(id: PyObjectId) -> BasicObjectInfo:
    pass


def get_basic_dataset(id: PyObjectId) -> BasicObjectInfo:
    pass


def get_basic_dataset_version(id: PyObjectId) -> BasicObjectInfo:
    pass


def get_basic_data_federation(id: PyObjectId) -> BasicObjectInfo:
    pass


def get_basic_secure_computation_node(id: PyObjectId) -> BasicObjectInfo:
    pass


def get_basic_orgnization(id: PyObjectId) -> BasicObjectInfo:
    pass


def get_basic_data_federation(id: PyObjectId) -> BasicObjectInfo:
    pass
