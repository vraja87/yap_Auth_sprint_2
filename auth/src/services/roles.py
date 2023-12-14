from functools import lru_cache
from http import HTTPStatus
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import FastApiConf, get_config
from src.core.logger import logger
from src.db.postgres import get_session
from src.models.entity import Role, User, UserRoles
from src.services.token import TokenService, get_token_service

from fastapi import Depends, HTTPException


class RoleAlreadyExistsException(HTTPException):
    pass


class RoleNotFoundException(HTTPException):
    pass


class RoleService:
    """
    Service class for managing roles in the application.

    :param db_session: The database session to use for queries.
    :param token_service: The service for handling JWT tokens.
    :param admin_login: The login identifier for the admin user.
    """

    def __init__(self, db_session: AsyncSession,
                 token_service: TokenService,
                 admin_login: str
                 ):
        self.db = db_session
        self.token_service = token_service
        self.admin_login = admin_login
        self.admin_user_id = None
        self.admin_role_id = None

    async def create_role(self, role_data: Role, access_token: str) -> Role:
        """
        Creates a new role in the system.

        :param role_data: The Role object containing name and description.
        :param access_token: JWT access token to authenticate the user.
        :return: The newly created Role object.
        """
        access_token_decoded = self.token_service.decode_jwt(access_token)
        if not await self.is_admin(user_id=access_token_decoded['sub']):
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                                detail="You do not have permission to perform this action")

        role = Role(name=role_data.name, description=role_data.description)
        self.db.add(role)
        try:
            await self.db.commit()
        except IntegrityError:
            logger.error(f"User creation failed, user already exists: {role.name}")
            raise RoleAlreadyExistsException(status_code=HTTPStatus.CONFLICT, detail="Role already exists")
        await self.db.refresh(role)
        logger.info(f'Create new role: {role.name}')
        return role

    async def delete_role(self, role_id: UUID, access_token: str):
        """
        Deletes a role by its ID.

        :param role_id: UUID of the role to be deleted.
        :param access_token: JWT access token to authenticate the user.
        """

        if role_id == self.admin_role_id:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                                detail="Deleting the admin role is forbidden")

        access_token_decoded = self.token_service.decode_jwt(access_token)
        if not await self.is_admin(user_id=access_token_decoded['sub']):
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                                detail="You do not have permission to perform this action")

        role = await self.db.get(Role, role_id)
        if not role:
            return
        await self.db.delete(role)
        await self.db.commit()

    async def assign_role_to_user(self, user_id: UUID, role_id: UUID, access_token: str):
        """
        Assigns a role to a user.

        :param user_id: The UUID of the user to whom the role is being assigned.
        :param role_id: The UUID of the role to assign.
        :param access_token: JWT access token to authenticate the user.
        """
        access_token_decoded = self.token_service.decode_jwt(access_token)
        if not await self.is_admin(user_id=access_token_decoded['sub']):
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                                detail="You do not have permission to perform this action")

        existing = await self.db.execute(
            select(UserRoles).where(UserRoles.user_id == user_id, UserRoles.role_id == role_id)
        )
        if existing.scalars().first() is not None:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Role already assigned to this user")

        try:
            user_role = UserRoles(user_id=user_id, role_id=role_id)
            self.db.add(user_role)
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail="Error while assigning role to user")

    async def detach_role_from_user(self, user_id: UUID, role_id: UUID, access_token: str):
        """
        Detaches a role from a user.

        :param user_id: The UUID of the user from whom the role is being detached.
        :param role_id: The UUID of the role to detach.
        :param access_token: JWT access token to authenticate the user.
        """
        admin_user_id = await self._get_admin_user_id()
        admin_role_id = await self._get_admin_role_id()
        if user_id == admin_user_id and role_id == admin_role_id:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                                detail="Deleting the admin role from admin user is forbidden")

        access_token_decoded = self.token_service.decode_jwt(access_token)
        if not await self.is_admin(user_id=access_token_decoded['sub']):
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                                detail="You do not have permission to perform this action")

        user_role = await self.db.execute(select(UserRoles).where(
            UserRoles.user_id == user_id,
            UserRoles.role_id == role_id)
        )
        user_role = user_role.scalars().first()
        if not user_role:
            return

        await self.db.delete(user_role)
        await self.db.commit()

    async def get_roles_all(self) -> list[Role]:
        """
        Retrieves all roles from the database.

        :return: A list of Role objects.
        """
        result = await self.db.execute(select(Role))
        roles = result.scalars().all()
        return roles if roles else []

    async def get_role_by_id(self, role_id: UUID) -> Role | None:
        """
        Retrieves a role by its UUID.

        :param role_id: The UUID of the role to be retrieved.
        :return: A Role object if found, otherwise None.
        """
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        return result.scalars().first()

    async def get_role_by_name(self, role_name: str) -> Role | None:
        """
        Retrieves a role by its name.

        :param role_name: The name of the role to be retrieved.
        :return: A Role object if found, otherwise None.
        """
        result = await self.db.execute(select(Role).where(Role.name == role_name))
        return result.scalars().first()

    async def get_roles_by_user_id(self, user_id: UUID, access_token: str) -> list[Role]:
        """
        Retrieves roles associated with a specific user ID.

        :param user_id: The UUID of the user for whom to retrieve roles.
        :param access_token: JWT access token to authenticate the user.
        :return: A list of Role objects associated with the user.
        """
        access_token_decoded = self.token_service.decode_jwt(access_token)
        if access_token_decoded['sub'] != str(user_id) and not await self.is_admin(user_id=access_token_decoded['sub']):
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                                detail="You do not have permission to perform this action")
        return await self.get_roles_by_user_id_query(user_id)

    async def get_roles_by_access_token(self, access_token: str) -> list[Role]:
        """
         Retrieves roles associated with the user identified by the given access token.

         :param access_token: JWT access token to identify and authenticate the user.
         :return: A list of Role objects associated with the user.
         """
        access_token_decoded = self.token_service.decode_jwt(access_token)
        return await self.get_roles_by_user_id_query(user_id=access_token_decoded['sub'])

    async def has_role(self, user_id: UUID, role_name: str) -> bool:
        """
        Checks if a user has a specific role.

        :param user_id: The UUID of the user.
        :param role_name: The name of the role to check.
        :return: True if the user has the role, False otherwise.
        """
        all_user_roles = await self.get_roles_by_user_id_query(user_id)
        return any(role.name == role_name for role in all_user_roles)

    async def has_roles(self, user_id: UUID, role_names: list[str]) -> bool:
        """
        Checks if a user has any of the specified roles.

        :param user_id: The UUID of the user.
        :param role_names: A list of role names to check.
        :return: True if the user has any of the roles, False otherwise.
        """
        all_user_roles = await self.get_roles_by_user_id_query(user_id)
        return any(role.name in role_names for role in all_user_roles)

    async def is_admin(self, user_id: UUID) -> bool:
        """
        Checks if a user is an admin.

        :param user_id: The UUID of the user to check.
        :return: True if the user is an admin, False otherwise.
        """
        return await self.has_role(user_id=user_id, role_name='admin')

    async def get_roles_by_user_id_query(self, user_id: UUID) -> list[Role]:
        """
        Helper method to get roles by user ID.

        :param user_id: The UUID of the user for whom to retrieve roles.
        :return: A list of Role objects associated with the user.
        """
        result = await self.db.execute(
            select(Role).join(UserRoles, Role.id == UserRoles.role_id).where(UserRoles.user_id == user_id)
        )
        roles = result.scalars().all()
        return roles if roles else []

    async def _get_admin_user_id(self) -> UUID:
        """
         Retrieves the UUID of the admin user.

         :return: The UUID of the admin user.
         :raises HTTPException: If the administrator account is not found.
         """
        if self.admin_user_id is None:
            admin_user = await self.db.scalar(select(User).where(User.login == self.admin_login))
            if admin_user is None:
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                    detail="Administrator account not found")
            self.admin_user_id = admin_user.id
        return self.admin_user_id

    async def _get_admin_role_id(self) -> UUID:
        """
        Retrieves the UUID of the admin role.

        :return: The UUID of the admin role.
        :raises HTTPException: If the administrator role is not found.
        """
        if self.admin_role_id is None:
            role_id = await self.get_role_by_name('admin')
            if role_id is None:
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                    detail="Administrator role not found")
            self.admin_role_id = role_id.id
        return self.admin_role_id


@lru_cache()
def get_role_service(db_session: AsyncSession = Depends(get_session),
                     token_service: TokenService = Depends(get_token_service),
                     config: FastApiConf = Depends(get_config)
                     ) -> RoleService:
    """
    Dependency-injection getter for RoleService.

    :param db_session: The database session to be used by the RoleService.
    :param token_service: The token service for handling JWT tokens.
    :param config: The application configuration.
    :return: An instance of RoleService.
    """
    return RoleService(db_session, token_service, config.admin_login)
