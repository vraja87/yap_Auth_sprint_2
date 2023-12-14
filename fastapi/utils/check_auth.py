from http import HTTPStatus

import aiohttp
import jwt
from core import config
from core.logger import logger

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()
cache_conf = config.CacheConf.read_config()
fast_api_conf = config.FastApiConf()


async def make_get_request(url: str, query_data: dict | None = None, headers: dict | None = None):
    async with aiohttp.ClientSession().get(url, params=query_data, headers=headers) as response:
        response.body = await response.json()
        return response


async def extract_token(credentials):
    """Extracts the access token from the credentials."""
    if not credentials or not hasattr(credentials, 'scheme') or not credentials.scheme == 'Bearer':
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Invalid authorization code'
        )
    access_token = credentials.credentials
    return access_token


async def get_auth_user_roles(credentials: HTTPAuthorizationCredentials):
    """Retrieves a list of user roles associated with the provided access token."""
    access_token = await extract_token(credentials)
    headers = {"Authorization": f"Bearer {access_token}",
               "Content-Type": "application/json"}
    roles_response = await make_get_request(
        url='http://auth-api:8000/api/v1/user/access-roles',
        headers=headers
    )
    logger.info(roles_response)
    user_roles = [role['name'] for role in roles_response.body]
    if roles_response.status == HTTPStatus.BAD_REQUEST:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="bad auth request")
    if roles_response.status != HTTPStatus.OK:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="User role don't recognized")
    return user_roles


async def is_admin(credentials: HTTPAuthorizationCredentials = Security(security)):
    return fast_api_conf.role_admin in await get_auth_user_roles(credentials)


async def is_authorized(credentials: HTTPAuthorizationCredentials = Security(security)):
    return fast_api_conf.role_user in await get_auth_user_roles(credentials)


async def is_anonymous(credentials: HTTPAuthorizationCredentials = Security(security)):
    return fast_api_conf.role_anonym in await get_auth_user_roles(credentials)


async def decode_jwt_self(credentials: HTTPAuthorizationCredentials):
    """
    To reduce the load on the auth service, we simply check for the presence of a successfully decoded token.
    """
    access_token = await extract_token(credentials)
    try:
        decoded_jwt = jwt.decode(access_token, fast_api_conf.secret_key, algorithms=["HS256"])
        return decoded_jwt
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def check_has_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    # return bool(await get_auth_user_roles(credentials))
    return bool(await decode_jwt_self(credentials))
