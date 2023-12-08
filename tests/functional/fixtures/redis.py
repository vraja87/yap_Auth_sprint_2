import pytest_asyncio
from functional.settings import test_settings
from redis.asyncio import Redis


@pytest_asyncio.fixture(scope='session')
def redis_cleanup():
    """Cleanup redis cache."""
    async def inner():
        redis_client = Redis.from_url(test_settings.redis_host)
        await redis_client.flushall()
    return inner
