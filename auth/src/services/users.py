from datetime import datetime, timedelta
from functools import lru_cache
from http import HTTPStatus

from fastapi import Depends, HTTPException
from sqlalchemy import delete, desc, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.requests import Request

from src.core.config import FastApiConf, get_config
from src.core.logger import logger
from src.db.cache import CacheBackend, get_cache
from src.db.postgres import AsyncSession, get_session
from src.models.entity import LoginHistory, RefreshToken, User
from src.services.token import TokenService, get_token_service
from src.services.utils import calculate_ttl, get_ip_address, get_user_agent


class UserAlreadyExistsException(HTTPException):
    pass


class AuthenticationFailedException(HTTPException):
    pass


class UserService:
    """
    Manages user-related actions in an application, handling authentication, token management, and user login history.
    Utilizes asynchronous methods for database and cache interactions.

    :param db_session: Async database session for queries.
    :param cache_service: Service for caching.
    :param token_service: Service for JWT token generation and validation.
    :param access_token_ttl: Lifespan of access tokens in seconds.
    :param refresh_token_ttl: Lifespan of refresh tokens in seconds.
    """
    def __init__(self, db_session: AsyncSession,
                 cache_service: CacheBackend,
                 token_service: TokenService,
                 access_token_ttl: int,
                 refresh_token_ttl: int
                 ):
        self.db = db_session
        self.cache_service = cache_service
        self.token_service = token_service
        self.access_token_ttl = access_token_ttl
        self.refresh_token_ttl = refresh_token_ttl

    async def get_user_by_username(self, username: str) -> User:
        """
        Retrieves a user by username.

        :param username: The username to search for.
        :return: User object if found.
        """
        return await self.db.scalar(select(User).where(User.login == username))

    async def get_user_by_id(self, user_id: str) -> User:
        """
        Retrieves a user by user id.

        :param user_id: The user uuid to search for.
        :return: User object if found.
        """
        return await self.db.scalar(select(User).where(User.id == user_id))

    async def create_user(self, user: User) -> User:
        """
        Adds a new user to the database.

        :param user: The User object to add.
        :return: The added User object.
        """
        self.db.add(user)
        try:
            await self.db.commit()
        except IntegrityError:
            logger.error(f"User creation failed, user already exists: {user.login}")
            raise UserAlreadyExistsException(status_code=HTTPStatus.CONFLICT, detail="User already exists")

        await self.db.refresh(user)
        logger.info(f'Signup login {user.login}')
        return user

    async def authenticate(self, username: str, password: str, request: Request) -> tuple[str, str, User]:
        """
        Authenticates a user and generates access and refresh tokens.

        :param username: The username of the user.
        :param password: The password of the user.
        :param request: The request object to extract user agent and IP.
        :return: A tuple of access token and refresh token.
        """
        user = await self.get_user_by_username(username)
        if not user or not user.check_password(password):
            logger.warning(f"Authentication failed for user: {username}")
            raise AuthenticationFailedException(status_code=HTTPStatus.UNAUTHORIZED, detail="Wrong login or password")

        logger.info(f"User authenticated successfully: {username}")
        user_id, user_agent, ip_address = str(user.id), get_user_agent(request), get_ip_address(request)

        refresh_token, refresh_record = await self.create_new_refresh_token(user_id, user_agent)
        await self.create_login_history(user_id=user.id, ip_address=ip_address, user_agent=user_agent)

        try:
            await self.db.commit()
            logger.debug(f"Authentication records saved successfully for user: {username}")
        except IntegrityError:
            logger.error(f"Error saving session for user: {username}")
            self.db.rollback()
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Error saving session")

        refresh_record_id = str(refresh_record.id)
        access_token = self.create_access_token(str(user.id), refresh_token_id=refresh_record_id)
        return access_token, refresh_token, user

    async def logout(self, access_token: str):
        """
        Logs out a user from a single session by invalidating the given access token.

        :param access_token: The JWT access token to be invalidated.
        """
        access_token_decoded = self.token_service.decode_jwt(access_token)
        logger.debug(f"Logging out from one session for user: {access_token_decoded['sub']}")
        jti = access_token_decoded["jti"]
        ttl = calculate_ttl(access_token_decoded['exp'])

        await self.invalidate_refresh_token(jti)
        await self.cache_service.set(access_token, 'bad', expire=ttl)

    async def logout_all(self, access_token: str):
        """
        Logs out a user from all sessions by invalidating all refresh tokens associated with the user.

        :param access_token: The JWT access token of the current session, used to identify the user.
        """
        access_token_decoded = self.token_service.decode_jwt(access_token)
        logger.debug(f"Logging out from all sessions for user: {access_token_decoded['sub']}")
        ttl = calculate_ttl(access_token_decoded['exp'])
        user_id = access_token_decoded['sub']

        await self.invalidate_all_user_refresh_tokens(user_id)
        await self.cache_service.set(access_token, 'bad', expire=ttl)

    def create_access_token(self, user_id: str, refresh_token_id: str):
        """
        Generates a new access token for a user.

        :param user_id: The user's unique identifier.
        :param refresh_token_id: The identifier of the associated refresh token.
        :return: A new JWT access token.
        """
        return self.token_service.encode_jwt(user_id, timedelta(seconds=self.access_token_ttl), jti=refresh_token_id)

    def create_refresh_token(self, user_id: str):
        """
        Generates a new refresh token for a user.

        :param user_id: The user's unique identifier.
        :return: A new JWT refresh token.
        """
        return self.token_service.encode_jwt(user_id, timedelta(seconds=self.refresh_token_ttl))

    async def create_new_refresh_token(self, user_id: str, user_agent: str) -> tuple[str, RefreshToken]:
        """
        Creates and persists a new refresh token record.

        :param user_id: The user's unique identifier.
        :param user_agent: The user agent string from the user's request.
        :return: A tuple of the new refresh token and its database record.
        """
        new_refresh_token = self.create_refresh_token(user_id)
        refresh_record = RefreshToken(
            user_id=user_id,
            user_agent=user_agent,
            jwt_token=new_refresh_token,
            expiry_date=datetime.utcnow() + timedelta(seconds=self.refresh_token_ttl),
            is_valid=True,
        )
        self.db.add(refresh_record)
        return new_refresh_token, refresh_record

    async def get_valid_refresh_token(self, refresh_token: str, user_agent: str) -> RefreshToken:
        """
        Retrieves and validates a refresh token.

        :param refresh_token: The refresh token to validate.
        :param user_agent: The user agent to match with the token.
        :return: A valid RefreshToken instance.
        """
        query = select(RefreshToken).where(RefreshToken.jwt_token == refresh_token)
        result = await self.db.execute(query)
        token = result.scalar_one_or_none()

        if not token or not token.is_valid or user_agent != token.user_agent or token.expiry_date < datetime.utcnow():
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return token

    async def refresh(self, refresh_token: str, request: Request) -> tuple[str, str]:
        """
        Refreshes the authentication tokens for a user.

        :param refresh_token: The current refresh token.
        :param request: The request object to extract user agent and IP.
        :return: A tuple of a new access token and a new refresh token.
        """
        user_agent, ip_address = get_user_agent(request), get_ip_address(request)

        try:
            token = await self.get_valid_refresh_token(refresh_token, user_agent)
        except HTTPException as e:
            logger.warning(
                f"Failed to validate refresh token for user agent: {user_agent} and IP: {ip_address}, Error: {e}")
            raise

        user_id = str(token.user_id)
        logger.debug(f"Valid refresh token found for user ID: {user_id}")

        refresh_token, refresh_record = await self.create_new_refresh_token(user_id, user_agent)

        token.is_valid = False
        try:
            await self.db.commit()
            logger.debug(f"Refresh token invalidated and database committed for user ID: {user_id}")
        except SQLAlchemyError as e:
            logger.error(f"Failed to commit to database for user ID: {user_id}, Error: {e}")
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail="Error while updating refresh token db")

        refresh_record_id = str(refresh_record.id)
        access_token = self.create_access_token(str(token.user_id), refresh_token_id=refresh_record_id)
        logger.debug(f"Access token created and refresh token updated successfully for user ID: {user_id}")

        return access_token, refresh_token

    async def create_login_history(self, user_id: int, user_agent: str, ip_address: str):
        """
        Records a user's login history in the database.

        :param user_id: The ID of the user who is logging in.
        :param user_agent: The user agent string from the user's request.
        :param ip_address: The IP address of the user at the time of login.
        """
        history_record = LoginHistory(user_id=user_id, ip_address=ip_address, user_agent=user_agent)
        self.db.add(history_record)

    async def invalidate_refresh_token(self, jti: str):
        """
        Invalidates a specific refresh token by its JTI (JWT ID).

        :param jti: The unique identifier of the refresh token to invalidate.
        """
        logger.debug(f"Invalidating refresh token with uuid: {jti}")
        query = delete(RefreshToken).where(RefreshToken.id == jti)
        try:
            await self.db.execute(query)
            await self.db.commit()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail=f"Error while committing refresh token status: {e}")

    async def invalidate_all_user_refresh_tokens(self, user_id: str):
        """
        Invalidates all refresh tokens issued to a specific user.

        :param user_id: The ID of the user whose refresh tokens need to be invalidated.
        """
        logger.debug(f"Invalidating all refresh tokens for user ID: {user_id}")
        query = delete(RefreshToken).where(RefreshToken.user_id == user_id)
        try:
            await self.db.execute(query)
            await self.db.commit()
            logger.debug(f"All refresh tokens invalidated for user ID: {user_id}")
        except SQLAlchemyError as e:
            logger.error(f"Error invalidating all refresh tokens for user ID {user_id}: {e}")
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail=f"Error while committing refresh token status: {e}")

    async def get_history(self, access_token: str, page_number: int, page_size: int) -> list[LoginHistory]:
        """
        Retrieves a paginated list of login history records for a user.

        :param access_token: JWT access token of the user.
        :param page_number: The page number of the login history to retrieve.
        :param page_size: The number of login history records per page.
        :return: A list of LoginHistory records for the specified page.
        """
        access_token_decoded = self.token_service.decode_jwt(access_token)
        offset = page_number * page_size
        query = (select(LoginHistory)
                 .where(LoginHistory.user_id == access_token_decoded['sub'])
                 .order_by(desc(LoginHistory.created_at))
                 .offset(offset)
                 .limit(page_size))
        try:
            result = await self.db.execute(query)
        except SQLAlchemyError as e:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))
        return result.scalars().all()

    async def update_user(self, access_token: str, user_update: User):
        """
        Updates user information based on the provided User object.

        :param access_token: JWT access token of the user.
        :param user_update: A User object containing the updated user information.
        """
        access_token_decoded = self.token_service.decode_jwt(access_token)
        user_id = access_token_decoded['sub']
        user = await self.get_user_by_id(user_id)

        if not user:
            logger.error(f"Can't find user with uuid: {user_id}")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

        if user_update.login is not None:
            user.login = user_update.login
        if user_update.password is not None:
            user.password = user_update.password
        if user_update.first_name is not None:
            user.first_name = user_update.first_name
        if user_update.last_name is not None:
            user.last_name = user_update.last_name

        try:
            await self.db.commit()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail=f"Error while updating user information: {e}")


@lru_cache()
def get_user_service(db_session: AsyncSession = Depends(get_session),
                     cache_service: CacheBackend = Depends(get_cache),
                     token_service: TokenService = Depends(get_token_service),
                     config: FastApiConf = Depends(get_config)
                     ) -> UserService:
    """
    Dependency function to get an instance of UserService.

    :param db_session: An asynchronous database session, used for database operations.
    :param cache_service: A cache backend instance, used for caching data to improve performance.
    :param token_service: A token service instance, used for managing authentication tokens.
    :param role_service: A role service instance, used for managing user roles.
    :param config: Configuration settings for the FastAPI application
    :return: An instance of UserService.
    """
    return UserService(db_session, cache_service, token_service, config.access_token_ttl, config.refresh_token_ttl)
