# -------------------------------------------------------------------------------
# Engineering
# main.py
# -------------------------------------------------------------------------------
"""The main entrypoint of the API Services"""
# -------------------------------------------------------------------------------
# Copyright (C) 2022 Secure Ai Labs, Inc. All Rights Reserved.
# Private and Confidential. Internal Use Only.
#     This software contains proprietary information which shall not
#     be reproduced or transferred to other documents and shall not
#     be disclosed to others for any purpose without
#     prior written permission of Secure Ai Labs, Inc.
# -------------------------------------------------------------------------------

import base64
import json
import logging
import traceback

import aiohttp
import fastapi.openapi.utils as utils
from fastapi import FastAPI, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_responses import custom_openapi
from pydantic import BaseModel, Field, StrictStr

from app.api import (
    accounts,
    audit,
    authentication,
    data_federations,
    data_models,
    data_models_dataframe,
    data_models_series,
    dataset_versions,
    datasets,
    internal_utils,
    secure_computation_nodes,
)
from app.data import operations as data_service
from app.models.common import PyObjectId
from app.utils.logging import LogLevel, Resource, add_log_message
from app.utils.secrets import get_secret

server = FastAPI(
    title="SAIL",
    description="All the private and public APIs for the Secure AI Labs",
    version="0.1.0",
    docs_url=None,
)
server.openapi = custom_openapi(server)


origins = [
    "*",
]

# Add all the API services here exposed to the public
server.include_router(audit.router)
server.include_router(authentication.router)
server.include_router(accounts.router)
server.include_router(data_federations.router)
server.include_router(datasets.router)
server.include_router(dataset_versions.router)
server.include_router(secure_computation_nodes.router)
server.include_router(internal_utils.router)
server.include_router(data_models.router)
server.include_router(data_models_dataframe.router)
server.include_router(data_models_series.router)

server.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Override the default validation error handler as it throws away a lot of information
# about the schema of the request body.
class ValidationError(BaseModel):
    error: StrictStr = Field(default="Invalid Schema")


@server.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    error = ValidationError(error="Invalid Schema")
    return JSONResponse(status_code=422, content=jsonable_encoder(error))


@server.exception_handler(Exception)
async def server_error_exception_handler(request: Request, exc: Exception):
    """
    Handle all unknown exceptions

    :param request: The http request object
    :type request: Request
    :param exc: The exception object
    :type exc: Exception
    """
    message = {
        "_id": str(PyObjectId()),
        "exception": f"{str(exc)}",
        "request": f"{request.method} {request.url}",
        "stack_trace": f"{traceback.format_exc()}",
    }

    # if the slack webhook is set, send the error to slack via aiohttp
    if get_secret("slack_webhook"):
        headers = {"Content-type": "application/json"}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                get_secret("slack_webhook"),
                headers=headers,
                json={
                    "text": json.dumps(
                        {
                            "id": message["_id"],
                            "owner": get_secret("owner"),
                            "exception": message["exception"],
                        },
                        indent=2,
                    )
                },
            ) as response:
                logging.info(f"Slack webhook response: {response.status}")

    # Add it to the sail database audit log
    await data_service.insert_one("errors", jsonable_encoder(message))

    # Add the exception to the audit log as well
    # await log_message(json.dumps(message))

    # Respond with a 500 error
    return Response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content="Internal Server Error id: {}".format(message["_id"]),
    )


utils.validation_error_response_definition = ValidationError.schema()


@server.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    if server.openapi_url is None:
        raise RequestValidationError("openapi_url must be provided to serve Swagger UI")

    server.mount("/static", StaticFiles(directory="./app/static"), name="static")
    return get_swagger_ui_html(
        openapi_url=server.openapi_url,
        title=server.title + " - Swagger UI",
        oauth2_redirect_url=server.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@server.middleware("http")
async def add_audit_log(request: Request, call_next):
    """
    Add audit log to the request

    :param request: The http request object
    :type request: Request
    :param call_next: The next function to call
    :type call_next: function
    """
    response: Response = await call_next(request)

    # Extract the user id from the JWT token in the request header
    user_id = None
    if "Authorization" in request.headers:
        auth_token_list = request.headers["Authorization"].split(".")
        if len(auth_token_list) > 1:
            user_info_base_64 = request.headers["Authorization"].split(".")[1]
            user_info = json.loads(base64.b64decode(user_info_base_64 + "=="))
            user_id = user_info["_id"]

    message = {
        "user_id": user_id,
        "request": f"{request.method} {request.url}",
        "response": f"{response.status_code}",
    }

    add_log_message(LogLevel.INFO, Resource.USER_ACTIVITY, message)

    return response
