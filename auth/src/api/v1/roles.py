from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

import src.api.v1.api_examples as api_examples
from src.api.v1.models.entity import (RoleCreate, RoleNamesResponse,
                                      RoleResponse, AssignRoleRequest)
from src.api.v1.user import get_token
from src.core.logger import logger
from src.models.entity import Role
from src.services.roles import RoleService, get_role_service

router = APIRouter()


@logger.catch
@router.post("/create",
             response_model=RoleResponse,
             status_code=HTTPStatus.CREATED,
             summary="Create a new role",
             description="Creates a new role with the specified name and description.",
             responses=api_examples.create_role)
async def create_role(
        role_data: RoleCreate,
        role_service: RoleService = Depends(get_role_service),
        access_token: str = Depends(get_token)) -> RoleResponse:
    """
    Creates a new role.

    :param role_data: Data model containing the name and description of the role.
    :param role_service: Dependency injection of the RoleService.
    :param access_token: JWT access token for authorization.
    :return: Newly created Role object.
    """
    role = await role_service.create_role(Role(name=role_data.name, description=role_data.description), access_token)
    return RoleResponse(id=str(role.id), name=role.name, description=role.description)


@router.delete("/delete/{role_id}",
               status_code=HTTPStatus.NO_CONTENT,
               summary="Delete a role",
               description="Deletes a role based on its UUID.",
               responses=api_examples.delete_role)
async def delete_role(role_id: UUID,
                      role_service: RoleService = Depends(get_role_service),
                      access_token: str = Depends(get_token)):
    """
    Deletes a role by its ID.

    :param role_id: UUID of the role to be deleted.
    :param role_service: Dependency injection of the RoleService.
    :param access_token: JWT access token for authorization.
    """
    await role_service.delete_role(role_id, access_token)


@router.get("/",
            response_model=list[RoleResponse],
            status_code=HTTPStatus.OK,
            summary="List all roles",
            description = "Retrieves a list of all roles.",
            responses=api_examples.list_roles)
async def get_all_roles(role_service: RoleService = Depends(get_role_service)) -> list[RoleResponse]:
    """
    Get all roles.

    :param role_service: Dependency injection of the RoleService.
    :return: List of all roles in the system.
    """
    roles = await role_service.get_roles_all()
    return [RoleResponse(id=str(role.id), name=role.name, description=role.description) for role in roles]


@router.get("/{role_id}",
            response_model=RoleResponse,
            status_code=HTTPStatus.OK,
            summary="Get a role by ID",
            description="Retrieves a role by its UUID.",
            responses=api_examples.get_role)
async def get_role(role_id: UUID, role_service: RoleService = Depends(get_role_service)) -> RoleResponse:
    """
    Get a role by its ID.

    :param role_id: UUID of the role to retrieve.
    :param role_service: Dependency injection of the RoleService.
    :return: Role object if found, raises 404 if not found.
    """
    role = await role_service.get_role_by_id(role_id)
    if role is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Role not found")
    return RoleResponse(id=str(role.id), name=role.name, description=role.description)


@router.get("/{role_name}/name",
            response_model=RoleResponse,
            status_code=HTTPStatus.OK,
            summary="Get a role by name",
            description="Retrieves a role by its name.",
            responses=api_examples.get_role_name)
async def get_role_name(role_name: str, role_service: RoleService = Depends(get_role_service)) -> RoleResponse:
    """
    Get a role by its name.

    :param role_name: Name of the role to retrieve.
    :param role_service: Dependency injection of the RoleService.
    :return: Role object if found, raises 404 if not found.
    """
    role = await role_service.get_role_by_name(role_name)
    if role is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Role not found")
    return RoleResponse(id=str(role.id), name=role.name, description=role.description)


#
@router.get("/user/{user_id}",
            response_model=list[RoleNamesResponse],
            status_code=HTTPStatus.OK,
            summary="Get roles for a user",
            description="Retrieves roles assigned to a specified user.",
            responses=api_examples.get_user_roles)
async def get_user_roles(user_id: UUID,
                         access_token: str = Depends(get_token),
                         role_service: RoleService = Depends(get_role_service),
                         ) -> list[RoleNamesResponse]:
    """
    Get roles for a user.

    :param user_id: UUID of the user whose roles to retrieve.
    :param access_token: JWT access token for authorization.
    :param role_service: Dependency injection of the RoleService.
    :return: List of roles assigned to the user.
    """
    user_roles = await role_service.get_roles_by_user_id(user_id, access_token)
    return [RoleNamesResponse(name=role.name) for role in user_roles]


@router.post("/assign",
             response_model=list[RoleNamesResponse],
             status_code=HTTPStatus.OK,
             summary="Assign a role to a user",
             description="Assigns a specified role to a user.",
             responses=api_examples.assign_role)
async def assign_role_to_user(assign_role: AssignRoleRequest,
                              access_token: str = Depends(get_token),
                              role_service: RoleService = Depends(get_role_service),
                              ) -> list[RoleNamesResponse]:
    """
    Assign a role to a user.

    :param assign_role: UUID of the user to whom the role will be assigned, UUID of the role to be assigned.
    :param access_token: JWT access token for authorization.
    :param role_service: Dependency injection of the RoleService.
    :return: List of roles assigned to the user after the operation.
    """
    await role_service.assign_role_to_user(assign_role.user_id, assign_role.role_id, access_token)
    user_roles = await role_service.get_roles_by_user_id(assign_role.user_id, access_token)
    return [RoleNamesResponse(name=role.name) for role in user_roles]


@router.delete("/detach",
               response_model=list[RoleNamesResponse],
               status_code=HTTPStatus.OK,
               summary="Detach a role from a user",
               description="Detaches a specified role from a user.",
               responses=api_examples.detach_role)
async def detach_role_from_user(detach_role: AssignRoleRequest,
                                access_token: str = Depends(get_token),
                                role_service: RoleService = Depends(get_role_service),
                                ):
    """
    Detach a role from a user.
    :param detach_role: UUID of the user from whom the role will be detached, UUID of the role to be detached.
    :param access_token: JWT access token for authorization.
    :param role_service: Dependency injection of the RoleService.
    :return: List of roles assigned to the user after the operation.
    """
    await role_service.detach_role_from_user(detach_role.user_id, detach_role.role_id, access_token)
    user_roles = await role_service.get_roles_by_user_id(detach_role.user_id, access_token)
    return [RoleNamesResponse(name=role.name) for role in user_roles]
