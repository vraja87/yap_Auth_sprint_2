
from http import HTTPStatus

from fastapi import (APIRouter, Depends, Form, HTTPException, Response,
                     Security, Query)
from fastapi.responses import JSONResponse
from fastapi.security import (HTTPAuthorizationCredentials, HTTPBearer,
                              OAuth2PasswordRequestForm)
from starlette.requests import Request

import src.api.v1.api_examples as api_examples
from src.api.v1.models.entity import (LoginHistoryResponse, RoleNamesResponse,
                                      RoleResponse, TwoTokens, UserCreate,
                                      UserInDB, UserUpdateRequest)
from src.core.logger import logger
from src.db import cache
from src.models.entity import User
from src.services.roles import RoleService, get_role_service
from src.services.users import UserService, get_user_service

router = APIRouter()
security = HTTPBearer()


async def get_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Validates the access token from the Authorization header.

    :param credentials: Bearer token from the HTTP Authorization header.
    :return: Valid access token.
    """
    if credentials:
        if await cache.cache.get(credentials.credentials):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
            )
        return credentials.credentials
    else:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )


@logger.catch
@router.post('/signup',
             response_model=UserInDB,
             status_code=HTTPStatus.CREATED,
             summary="User Registration",
             description="Create a new user account.",
             responses=api_examples.user_creation)
async def create_user(user: UserCreate, user_service: UserService = Depends(get_user_service)) -> UserInDB:
    """
    Registers a new user.

    :param user: User data for registration.
    :param user_service: User service for database operations.
    :return: Registered user data.
    """
    return await user_service.create_user(
        User(login=user.login,
             password=user.password,
             first_name=user.first_name,
             last_name=user.last_name)
    )


@logger.catch
@router.post('/login',
             response_model=TwoTokens,
             status_code=HTTPStatus.OK,
             summary="User Login",
             description="Authenticate a user and provide access and refresh tokens.",
             responses=api_examples.login)
async def login(request: Request,
                form_data: OAuth2PasswordRequestForm = Depends(),
                user_service: UserService = Depends(get_user_service)
                ) -> TwoTokens:
    """
    Authenticates user and returns JWT tokens.

    :param request: HTTP request.
    :param form_data: Login credentials.
    :param user_service: User service.
    :return: Access and refresh JWT tokens.
    """
    access_token, refresh_token = await user_service.authenticate(form_data.username, form_data.password, request)
    return TwoTokens(access_token=access_token, refresh_token=refresh_token)


@router.post('/logout',
             status_code=HTTPStatus.OK,
             summary="User Logout",
             description="Logs out a user from the current session.",
             responses=api_examples.logout)
async def logout(access_token: str = Depends(get_token),
                 user_service: UserService = Depends(get_user_service)) -> Response:
    """
    Logs out user from the current session.

    :param access_token: JWT access token.
    :param user_service: User service.
    :return: Success message.
    """
    await user_service.logout(access_token)
    return JSONResponse(content={"message": "Successfully logged out"}, status_code=HTTPStatus.OK)


@router.post('/logout_all',
             status_code=HTTPStatus.OK,
             summary="User Logout from All Sessions",
             description="Logs out a user from all sessions.",
             responses=api_examples.logout_all)
async def logout_all(access_token: str = Depends(get_token),
                     user_service: UserService = Depends(get_user_service)) -> Response:
    """
    Logs out user from all sessions.

    :param access_token: JWT access token.
    :param user_service: User service.
    :return: Success message.
    """
    await user_service.logout_all(access_token)
    return JSONResponse(content={"message": "Successfully logged out from all sessions"}, status_code=HTTPStatus.OK)


@router.post('/refresh',
             status_code=HTTPStatus.OK,
             summary="Refresh Tokens",
             description="Refreshes the access and refresh tokens for a user.",
             responses=api_examples.refresh)
async def refresh(request: Request,
                  refresh_token: str = Form(),
                  user_service: UserService = Depends(get_user_service)) -> TwoTokens:
    """
    Refreshes user's authentication tokens.

    :param request: HTTP request.
    :param refresh_token: Current refresh token.
    :param user_service: User service.
    :return: New access and refresh tokens.
    """
    access_token, refresh_token = await user_service.refresh(refresh_token, request)
    return TwoTokens(access_token=access_token, refresh_token=refresh_token)


@router.get("/login-history",
            response_model=list[LoginHistoryResponse],
            summary="Get User Login History",
            description="Retrieves the login history for the current user, including user agent, "
                        "IP address, and the date and time of each login.",
            responses=api_examples.login_history)
async def get_login_history(access_token: str = Depends(get_token),
                            page_number: int = Query(0, ge=0, alias='page_number'),
                            page_size: int = Query(100, ge=1, alias='page_size'),
                            user_service: UserService = Depends(get_user_service)) -> list[LoginHistoryResponse]:
    records = await user_service.get_history(access_token=access_token,
                                             page_number=page_number,
                                             page_size=page_size)
    return [LoginHistoryResponse(user_agent=x.user_agent,
                                 ip_address=x.ip_address,
                                 login_date=x.created_at) for x in records]


@router.patch("/update",
              status_code=HTTPStatus.OK,
              summary="Update User Information",
              description="Updates the information of the current user, such as login, first name, last name, "
                          "and password. The access token is required to authenticate and identify the user.",
              responses=api_examples.update)
async def update_user(user_update: UserUpdateRequest,
                      access_token: str = Depends(get_token),
                      user_service: UserService = Depends(get_user_service)):
    await user_service.update_user(access_token, User(login=user_update.login,
                                                      password=user_update.password,
                                                      first_name=user_update.first_name,
                                                      last_name=user_update.last_name))
    return JSONResponse(content={"message": "User information successfully updated"}, status_code=HTTPStatus.OK)


@router.get("/access-roles",
            status_code=HTTPStatus.OK,
            response_model=list[RoleNamesResponse],
            summary="Retrieve User Roles",
            description="Retrieves a list of roles associated with the current user, "
                        "based on the provided access token.",
            responses=api_examples.access_role)
async def get_access_data(access_token: str = Depends(get_token),
                          role_service: RoleService = Depends(get_role_service)
                          ) -> list[RoleNamesResponse]:
    user_roles = await role_service.get_roles_by_access_token(access_token)
    return [RoleNamesResponse(name=role.name) for role in user_roles]