import time
from functools import lru_cache
from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis, RedisError
from starlette.requests import Request

from src.core.config import RateLimitConfig, get_rate_limit_config
from src.core.logger import logger
from src.db.cache import CacheBackend, get_cache, get_redis_instance
from src.services.token import TokenService, get_token_service
from src.services.utils import get_ip_address, get_user_agent

security = HTTPBearer()


class RateLimiter:
    """
    Implements rate limiting logic using Redis.

    :param config: Configuration settings for rate limiting.
    :param redis: Redis client instance for data storage and retrieval.
    """
    def __init__(self, config: RateLimitConfig, redis):
        self.config = config
        self.redis = redis

    async def is_rate_limited(self, key: str) -> bool:
        """
        Checks if a request is rate limited based on the provided key.

        :param key: The key to identify the rate limit context (e.g., user ID or IP).
        :return: True if rate limited, False otherwise.
        """
        current = int(time.time())
        print(current)
        window_start = current - self.config.seconds
        async with self.redis.pipeline() as pipe:
            try:
                pipe.zremrangebyscore(key, 0, window_start)
                pipe.zcard(key)
                pipe.zadd(key, {current: current})
                pipe.expire(key, self.config.seconds)
                results = await pipe.execute()
            except RedisError as e:
                logger.error(f"Redis error encountered: {e}")
                pass
        logger.debug(f"Rate Limited {key} {results}")
        if 'auth' in key.split(':'):
            return results[1] > self.config.times
        else:
            return results[1] > self.config.times_anonymous


@lru_cache
def get_rate_limiter(config: RateLimitConfig = Depends(get_rate_limit_config),
                     redis: Redis = Depends(get_redis_instance)) -> RateLimiter:
    """
    Provides a cached instance of RateLimiter.

    :param config: Configuration settings for rate limiting.
    :param redis: Redis client instance for data storage and retrieval.
    :return: An instance of RateLimiter.
    """
    return RateLimiter(config, redis)


async def get_optional_credentials(request: Request,
                                   security: HTTPBearer = Depends()) -> HTTPAuthorizationCredentials | None:
    """
    Extracts authorization credentials from the request, returning None if not present or invalid.

    :param request: The HTTP request to extract credentials from.
    :param security: The security dependency used for extracting credentials.
    :return: Extracted authorization credentials, or None if not found or invalid.
    """
    try:
        return await security(request)
    except Exception:
        return None


async def rate_limit_dependency(request: Request,
                                credentials: HTTPAuthorizationCredentials | None = Depends(get_optional_credentials),
                                cache: CacheBackend = Depends(get_cache),
                                rate_limiter: RateLimiter = Depends(get_rate_limiter),
                                token_service: TokenService = Depends(get_token_service)
                                ) -> None:
    """
     Enforces rate limiting on the endpoint using user identification from JWT or IP address and user agent.

     :param request: The current HTTP request to determine the user's IP and user agent.
     :param credentials: Optional JWT credentials for the user, used for user identification.
     :param cache: Backend cache service to check for existing rate limit data.
     :param rate_limiter: The rate limiting service to enforce request limits.
     :param token_service: Service to decode JWT tokens for user identification.
     """
    successful_decode = False
    if credentials and hasattr(credentials, 'credentials') and not await cache.get(credentials.credentials):
        try:
            user_id = token_service.decode_jwt(credentials.credentials)['sub']
            user_id = f"auth:{user_id}"
            successful_decode = True
        except Exception:
            pass
    if not successful_decode:
        ip_address = get_ip_address(request)
        user_agent = get_user_agent(request)
        user_id = f"anonym:{ip_address}:{user_agent}"
    key = f"rate_limit:{request.url.path}:{user_id}"
    if await rate_limiter.is_rate_limited(key):
        raise HTTPException(status_code=HTTPStatus.TOO_MANY_REQUESTS, detail="Too many requests")
