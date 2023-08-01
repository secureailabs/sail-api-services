# -------------------------------------------------------------------------------
# Engineering
# secure_computation_nodes.py
# -------------------------------------------------------------------------------
"""APIs to manage secure computation nodes"""
# -------------------------------------------------------------------------------
# Copyright (C) 2022 Secure Ai Labs, Inc. All Rights Reserved.
# Private and Confidential. Internal Use Only.
#     This software contains proprietary information which shall not
#     be reproduced or transferred to other documents and shall not
#     be disclosed to others for any purpose without
#     prior written permission of Secure Ai Labs, Inc.
# -------------------------------------------------------------------------------

import json
from typing import List, Optional

import yaml
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Response, status
from fastapi.encoders import jsonable_encoder
from sail_dns_management_client import Client as DNSClient
from sail_dns_management_client.api.default import add_domain_dns_post
from sail_dns_management_client.models import DomainData

import app.utils.azure as azure
from app.api.authentication import RoleChecker, get_current_user
from app.api.data_federations import get_data_federation, get_existing_dataset_key
from app.api.dataset_versions import DatasetVersion
from app.data import operations as data_service
from app.models.accounts import UserRole
from app.models.authentication import TokenData
from app.models.common import BasicObjectInfo, PyObjectId
from app.models.dataset_versions import DatasetVersionState
from app.models.secure_computation_nodes import (
    DatasetBasicInformation,
    DatasetInformation,
    DatasetInformationWithKey,
    GetMultipleSecureComputationNode_Out,
    GetSecureComputationNode_Out,
    RegisterSecureComputationNode_In,
    RegisterSecureComputationNode_Out,
    SecureComputationNode_Db,
    SecureComputationNodeInitializationVector,
    SecureComputationNodeState,
    UpdateSecureComputationNode_In,
)
from app.utils import cache
from app.utils.background_couroutines import add_async_task
from app.utils.secrets import get_secret

router = APIRouter()


class SecureComputationNode:
    """
    Dataset Version CRUD operations
    """

    DB_COLLECTION_SECURE_COMPUTATION_NODE = "secure-computation-node"

    @staticmethod
    async def create(
        secure_computation_node: SecureComputationNode_Db,
    ):
        """
        Create a new dataset version

        :param secure_computation_node: Secure computation node information
        :type secure_computation_node: SecureComputationNode_Db
        :return: Secure computation node information
        :rtype: SecureComputationNode_Db
        """
        return await data_service.insert_one(
            collection=SecureComputationNode.DB_COLLECTION_SECURE_COMPUTATION_NODE,
            data=jsonable_encoder(secure_computation_node),
        )

    @staticmethod
    async def read(
        query_secure_computation_node_id: Optional[PyObjectId] = None,
        query_organization_id: Optional[PyObjectId] = None,
        query_researcher_organization_id: Optional[PyObjectId] = None,
        query_researcher_user_id: Optional[PyObjectId] = None,
        query_state: Optional[SecureComputationNodeState] = None,
        throw_on_not_found: bool = True,
    ) -> List[SecureComputationNode_Db]:
        secure_computation_node_list = []

        query = {}
        if query_secure_computation_node_id:
            query["_id"] = str(query_secure_computation_node_id)
        if query_organization_id:
            query["organization_id"] = str(query_organization_id)
        if query_researcher_organization_id:
            query["researcher_id"] = str(query_researcher_organization_id)
        if query_researcher_user_id:
            query["researcher_user_id"] = str(query_researcher_user_id)
        if query_state:
            query["state"] = query_state.value

        response = await data_service.find_by_query(
            collection=SecureComputationNode.DB_COLLECTION_SECURE_COMPUTATION_NODE,
            query=jsonable_encoder(query),
        )

        if response:
            for data_model in response:
                secure_computation_node_list.append(SecureComputationNode_Db(**data_model))
        elif throw_on_not_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Secure Computation Node not found",
            )

        return secure_computation_node_list

    @staticmethod
    async def update(
        secure_computation_node_id: PyObjectId,
        researcher_user_id: Optional[PyObjectId] = None,
        researcher_organization_id: Optional[PyObjectId] = None,
        state: Optional[SecureComputationNodeState] = None,
        detail: Optional[str] = None,
        url: Optional[str] = None,
    ):
        update_request = {"$set": {}}
        if state:
            update_request["$set"]["state"] = state.value
        if detail:
            update_request["$set"]["detail"] = detail
        if url:
            update_request["$set"]["url"] = url

        query = {}
        if secure_computation_node_id:
            query["_id"] = str(secure_computation_node_id)
        if researcher_user_id:
            query["researcher_user_id"] = str(researcher_user_id)
        if researcher_organization_id:
            query["researcher_id"] = str(researcher_organization_id)

        update_response = await data_service.update_many(
            collection=SecureComputationNode.DB_COLLECTION_SECURE_COMPUTATION_NODE,
            query=query,
            data=jsonable_encoder(update_request),
        )

        if update_response.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Secure Computation Node not found.",
            )


@router.post(
    path="/secure-computation-node",
    description="Provision data federation SCNs",
    response_description="SCN information",
    response_model=RegisterSecureComputationNode_Out,
    response_model_by_alias=False,
    response_model_exclude_unset=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.RESEARCHER]))],
    operation_id="register_secure_computation_node",
)
async def register_secure_computation_node(
    secure_computation_node_req: RegisterSecureComputationNode_In = Body(description="SCN request body"),
    current_user: TokenData = Depends(get_current_user),
) -> RegisterSecureComputationNode_Out:
    """
    Register a secure computation node

    :param secure_computation_node_req: Secure computation node request body
    :type secure_computation_node_req: RegisterSecureComputationNode_In, optional
    :param current_user: Current user information
    :type current_user: TokenData, optional
    :return: Secure computation node information
    :rtype: RegisterSecureComputationNode_Out
    """

    # Current user organization must be one of the the data federation researcher
    data_federation_db = await get_data_federation(
        data_federation_id=secure_computation_node_req.data_federation_id, current_user=current_user
    )
    if not data_federation_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data Federation not found")

    # Researcher must be one of the data federation researchers
    if [
        organization
        for organization in data_federation_db.research_organizations
        if organization.id == current_user.organization_id
    ] is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization must be one of the the data federation researcher",
        )

    # Get the dataset versions for the data federation
    datasets = data_federation_db.datasets
    dataset_info: List[DatasetInformation] = []
    for dataset in datasets:
        # Get the dataset versions
        dataset_id = dataset.id
        response = await DatasetVersion.read(dataset_id=dataset_id)

        # Add all the dataset versions
        for dataset_version in response:
            # check if the dataset version is uploaded and active
            if dataset_version.state is not DatasetVersionState.ACTIVE:
                organization_info = await cache.get_basic_orgnization(id=dataset_version.organization_id)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Dataset version {dataset_version.name} from {dataset.name} must be uploaded and active. It is owned by {organization_info.name}.",
                )

            dataset_info.append(
                DatasetInformation(
                    id=dataset_id,
                    version_id=dataset_version.id,
                    data_owner_id=dataset_version.organization_id,
                )
            )

    # Add the secure computation node to the database
    secure_computation_node_db = SecureComputationNode_Db(
        data_federation_id=secure_computation_node_req.data_federation_id,
        datasets=dataset_info,
        size=secure_computation_node_req.size,
        researcher_user_id=current_user.id,
        state=SecureComputationNodeState.REQUESTED,
        researcher_id=current_user.organization_id,
    )

    dataset_with_keys: List[DatasetInformationWithKey] = []
    for dataset in dataset_info:
        # Check if dataset version exist
        await DatasetVersion.read(dataset_version_id=dataset.version_id)

        # Get the encryption key of the dataset
        dataset_key = await get_existing_dataset_key(
            data_federation_id=secure_computation_node_db.data_federation_id,
            dataset_id=dataset.id,
            current_user=current_user,
        )

        dataset_with_keys.append(
            DatasetInformationWithKey(
                id=dataset.id,
                version_id=dataset.version_id,
                data_owner_id=dataset.data_owner_id,
                key=dataset_key.dataset_key,
            )
        )

    # Start the provisioning of the secure computation node in a background thread which will update the IP address
    add_async_task(provision_secure_computation_node(secure_computation_node_db, dataset_with_keys))

    await SecureComputationNode.create(secure_computation_node_db)

    return RegisterSecureComputationNode_Out(**secure_computation_node_db.dict())


@router.get(
    path="/secure-computation-node",
    description="Get list of all the secure_computation_node for the current user",
    response_description="List of secure_computation_nodes",
    response_model=GetMultipleSecureComputationNode_Out,
    response_model_by_alias=False,
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.RESEARCHER]))],
    operation_id="get_all_secure_computation_nodes",
)
async def get_all_secure_computation_nodes(
    current_user: TokenData = Depends(get_current_user),
) -> GetMultipleSecureComputationNode_Out:
    from app.api.data_federations import get_data_federation

    secure_computation_nodes = await SecureComputationNode.read(
        # query_researcher_organization_id=current_user.organization_id,
        # query_researcher_user_id=current_user.id,
        query_state=SecureComputationNodeState.READY,
        throw_on_not_found=False,
    )

    response_secure_computation_nodes: List[GetSecureComputationNode_Out] = []

    # Get the basic information of the data federation
    if secure_computation_nodes:
        secure_computation_node = secure_computation_nodes[0]
        data_federation = await get_data_federation(secure_computation_node.data_federation_id, current_user)

        # Add the organization information to the data federation
        data_researcher_basic_info = [
            organization
            for organization in data_federation.research_organizations
            if organization.id == current_user.organization_id
        ][0]

        for secure_computation_node in secure_computation_nodes:
            dataset_info: List[DatasetBasicInformation] = []
            for dataset in secure_computation_node.datasets:
                # Get the basic information of the dataset
                dataset_basic_info = [dataset for dataset in data_federation.datasets if dataset.id == dataset.id][0]

                # Get the basic information of the data version
                dataset_version_basic_info = await DatasetVersion.read(dataset_version_id=dataset.version_id)
                dataset_version_basic_info = dataset_version_basic_info[0]

                # Get the information about the data owner organization
                data_owner_organization = await cache.get_basic_orgnization(
                    id=dataset_version_basic_info.organization_id
                )

                dataset_info.append(
                    DatasetBasicInformation(
                        dataset=BasicObjectInfo(id=dataset_basic_info.id, name=dataset_basic_info.name),
                        version=BasicObjectInfo(id=dataset_version_basic_info.id, name=dataset_version_basic_info.name),
                        data_owner=data_owner_organization,
                    )
                )

            response_secure_computation_node = GetSecureComputationNode_Out(
                _id=secure_computation_node.id,
                data_federation=BasicObjectInfo(id=data_federation.id, name=data_federation.name),
                datasets=dataset_info,
                researcher=data_researcher_basic_info,
                researcher_user=current_user.id,
                timestamp=secure_computation_node.timestamp,
                state=secure_computation_node.state,
                detail=secure_computation_node.detail,
                url=secure_computation_node.url,
            )

            response_secure_computation_nodes.append(response_secure_computation_node)

    return GetMultipleSecureComputationNode_Out(secure_computation_nodes=response_secure_computation_nodes)


@router.get(
    path="/secure-computation-node/{secure_computation_node_id}",
    description="Get the information about a secure computation node",
    response_model=GetSecureComputationNode_Out,
    response_model_by_alias=False,
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.RESEARCHER]))],
    operation_id="get_secure_computation_node",
)
async def get_secure_computation_node(
    secure_computation_node_id: PyObjectId = Path(description="UUID of Secure Computation Node"),
    current_user: TokenData = Depends(get_current_user),
):
    from app.api.data_federations import get_data_federation

    secure_computation_node = await SecureComputationNode.read(
        query_secure_computation_node_id=secure_computation_node_id,
        query_researcher_organization_id=current_user.organization_id,
        query_researcher_user_id=current_user.id,
    )

    # Get the basic information of the data federation
    secure_computation_node = secure_computation_node[0]
    data_federation = await get_data_federation(secure_computation_node.data_federation_id, current_user)

    # Add the organization information to the secure computation node information
    data_researcher_basic_info = [
        organization
        for organization in data_federation.research_organizations
        if organization.id == current_user.organization_id
    ][0]

    dataset_info: List[DatasetBasicInformation] = []
    for dataset in secure_computation_node.datasets:
        # Get the basic information of the dataset
        dataset_basic_info = [dataset for dataset in data_federation.datasets if dataset.id == dataset.id][0]

        # Get the basic information of the data version
        dataset_version_basic_info = await DatasetVersion.read(dataset_version_id=dataset.version_id)
        dataset_version_basic_info = dataset_version_basic_info[0]

        # Get the information about the data owner organization
        data_owner_organization = await cache.get_basic_orgnization(id=dataset_version_basic_info.organization_id)

        dataset_info.append(
            DatasetBasicInformation(
                dataset=BasicObjectInfo(id=dataset_basic_info.id, name=dataset_basic_info.name),
                version=BasicObjectInfo(id=dataset_version_basic_info.id, name=dataset_version_basic_info.name),
                data_owner=data_owner_organization,
            )
        )

    response_secure_computation_node = GetSecureComputationNode_Out(
        _id=secure_computation_node.id,
        data_federation=BasicObjectInfo(id=data_federation.id, name=data_federation.name),
        datasets=dataset_info,
        researcher=data_researcher_basic_info,
        researcher_user=current_user.id,
        timestamp=secure_computation_node.timestamp,
        state=secure_computation_node.state,
        detail=secure_computation_node.detail,
        url=secure_computation_node.url,
    )

    return response_secure_computation_node


@router.put(
    path="/secure-computation-node/{secure_computation_node_id}",
    description="Update secure computation node information",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.RESEARCHER]))],
    operation_id="update_secure_computation_node",
)
async def update_secure_computation_node(
    secure_computation_node_id: PyObjectId = Path(description="UUID of Secure Computation Node"),
    updated_secure_computation_node_info: UpdateSecureComputationNode_In = Body(
        description="Updated Secure Computation Node information"
    ),
    current_user: TokenData = Depends(get_current_user),
):
    secure_computation_node_db = await SecureComputationNode.read(
        query_secure_computation_node_id=secure_computation_node_id
    )
    secure_computation_node_db = secure_computation_node_db[0]

    new_state = secure_computation_node_db.state
    if secure_computation_node_db.state == SecureComputationNodeState.WAITING_FOR_DATA:
        if updated_secure_computation_node_info.state == SecureComputationNodeState.READY:
            new_state = SecureComputationNodeState.READY
        elif updated_secure_computation_node_info.state == SecureComputationNodeState.IN_USE:
            new_state = SecureComputationNodeState.IN_USE
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    await SecureComputationNode.update(secure_computation_node_id=secure_computation_node_id, state=new_state)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    path="/secure-computation-node/{secure_computation_node_id}",
    description="Deprovision SCN",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRole.RESEARCHER]))],
    operation_id="deprovision_secure_computation_node",
)
async def deprovision_secure_computation_node(
    secure_computation_node_id: PyObjectId,
    current_user: TokenData = Depends(get_current_user),
):
    await SecureComputationNode.update(
        secure_computation_node_id=secure_computation_node_id, state=SecureComputationNodeState.DELETING, url=""
    )

    # Start a background task to deprovision the secure computation node which will update the status
    add_async_task(delete_resource_group(secure_computation_node_id, current_user))

    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def provision_secure_computation_node(
    secure_computation_node_db: SecureComputationNode_Db, datasets: List[DatasetInformationWithKey]
):
    """
    Provision a secure computation node

    :param secure_computation_node_db: secure computation node information
    :type secure_computation_node_db: SecureComputationNode_Db
    :param dataset_key: dataset key
    :type dataset_key: str
    """
    try:
        # Create a SCN initialization vector json
        securecomputationnode_json = SecureComputationNodeInitializationVector(
            secure_computation_node_id=secure_computation_node_db.id,
            storage_account_name=get_secret("azure_storage_account_name"),
            dataset_storage_password=get_secret("azure_storage_account_password"),
            datasets=datasets,
            data_federation_id=secure_computation_node_db.data_federation_id,
            researcher_id=secure_computation_node_db.researcher_id,
            researcher_user_id=secure_computation_node_db.researcher_user_id,
            version=get_secret("version"),
            audit_service_ip=get_secret("audit_service_ip"),
        )

        with open(str(secure_computation_node_db.id), "w") as outfile:
            json.dump(jsonable_encoder(securecomputationnode_json), outfile)

        await provision_virtual_machine(
            secure_computation_node_db, "securecomputationnode", jsonable_encoder(securecomputationnode_json)
        )

        # TODO: Wait for the the data to be uploaded on the VM before marking it as ready
        await SecureComputationNode.update(
            secure_computation_node_id=secure_computation_node_db.id, state=SecureComputationNodeState.READY
        )

    except Exception as exception:
        print(exception)
        # Update the database to mark the VM as FAILED
        await SecureComputationNode.update(
            secure_computation_node_id=secure_computation_node_db.id,
            state=SecureComputationNodeState.FAILED,
            detail=str(exception),
        )


def create_cloud_init_file(initialization_json: dict, image_name: str):
    """
    Create a cloud init file

    :param initialization_json: initialization vector json
    :type initialization_json: dict
    :param image_name: name of the docker image
    :type image_name: str
    :return: cloud init file contents
    :rtype: str
    """
    cloud_init_file = "#cloud-config\n"

    cloud_init_yaml = {}

    # Copy the initialization.json file to the VM
    cloud_init_yaml["write_files"] = [
        {
            "path": "/etc/initialization.json",
            "content": json.dumps(initialization_json, indent=4),
        }
    ]

    cloud_init_yaml["runcmd"] = [
        f"sudo mkdir -p /opt/{image_name}_dir",
        "sudo docker login {0} --username {1} --password {2}".format(
            get_secret("docker_registry_url"),
            get_secret("docker_registry_username"),
            get_secret("docker_registry_password"),
        ),
        "sudo docker run -dit {0} -v /etc/initialization.json:/InitializationVector.json -v /opt/certs:/etc/nginx/certs --name {3} {1}/{3}:{2}".format(
            get_secret(f"{image_name}_docker_params"),
            get_secret("docker_registry_url"),
            get_secret(f"{image_name}_image_tag"),
            image_name,
        ),
    ]

    cloud_init_file += yaml.dump(cloud_init_yaml)

    return cloud_init_file


async def provision_virtual_machine(
    virtual_machine_info_db: SecureComputationNode_Db,
    template_name: str,
    initialization_vector_json: dict,
) -> None:
    """
    Provision a virtual machine

    :param virtual_machine_info_db: virtual machine information
    :type virtual_machine_info_db: SecureComputationNode_Db
    :param template_name: template name
    :type template_name: str
    :param initialization_vector_json: initialization vector json
    :type initialization_vector_json: str
    :rtype: SecureComputationNode_Db
    """
    # Update the database to mark the VM as being created
    await SecureComputationNode.update(
        secure_computation_node_id=virtual_machine_info_db.id, state=SecureComputationNodeState.CREATING
    )

    # The name of the resource group is same as the data federation provision id
    owner = get_secret("owner")
    resource_group_name = f"{owner}-{str(virtual_machine_info_db.id)}-scn"

    # Deploy the smart broker
    account_credentials = await azure.authenticate()
    deploy_response: azure.DeploymentResponse = await azure.deploy_module(
        account_credentials,
        resource_group_name,
        str(virtual_machine_info_db.id),
        jsonable_encoder(virtual_machine_info_db.size),
        custom_data=create_cloud_init_file(initialization_vector_json, template_name),
    )
    if deploy_response.status != "Success":
        raise Exception(deploy_response.note)

    # Update the DNS entry for the scn
    dns_ip = get_secret("dns_ip")
    dns_client = DNSClient(
        base_url=f"https://{dns_ip}:8000",
        verify_ssl=False,
        raise_on_unexpected_status=True,
        timeout=30,
        follow_redirects=True,
    )

    dns_entry = f"{str(virtual_machine_info_db.id)}-scn.{get_secret('base_domain')}"
    request = DomainData(ip=deploy_response.ip_address, domain=f"{dns_entry}.")
    add_domain_dns_post.sync(client=dns_client, json_body=request)

    # Update the database to mark the VM as WAITING FOR DATA
    await SecureComputationNode.update(
        secure_computation_node_id=virtual_machine_info_db.id,
        url=dns_entry,
        state=SecureComputationNodeState.WAITING_FOR_DATA,
    )


async def delete_resource_group(secure_computation_node_id: PyObjectId, current_user: TokenData):
    """
    Delete a resource group

    :param data_federation_provision_id: data federation provision id
    :type data_federation_provision_id: PyObjectId
    :param current_user: current user information
    :type current_user: TokenData
    """
    try:
        # Delete the scn resource group
        owner = get_secret("owner")
        deployment_name = f"{owner}-{str(secure_computation_node_id)}-scn"

        account_credentials = await azure.authenticate()
        delete_response = await azure.delete_resouce_group(account_credentials, deployment_name)
        if delete_response.status != "Success":
            raise Exception(delete_response.note)

        # Update the secure computation node
        await SecureComputationNode.update(
            secure_computation_node_id=secure_computation_node_id,
            researcher_organization_id=current_user.organization_id,
            researcher_user_id=current_user.id,
            state=SecureComputationNodeState.DELETED,
        )

    except Exception as exception:
        print(exception)
        # Update the database to mark the VM as FAILED
        await SecureComputationNode.update(
            secure_computation_node_id=secure_computation_node_id,
            researcher_organization_id=current_user.organization_id,
            researcher_user_id=current_user.id,
            state=SecureComputationNodeState.DELETE_FAILED,
            detail=str(exception),
        )
