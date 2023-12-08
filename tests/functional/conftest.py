import asyncio
import time

import aiohttp
import pytest
import pytest_asyncio
from functional.settings import test_settings

pytest_plugins = ("functional.fixtures.redis", "functional.fixtures.elastic")


@pytest.fixture(scope="session")
def event_loop():
    """
    Create and yield a new event loop for the test session.

    :yield: aiohttp client session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def http_session():
    """
    Asynchronously create and yield an aiohttp client session for the test session.

    Yields:
        session: The aiohttp client session.
    """
    async with aiohttp.ClientSession() as session:
        yield session


@pytest_asyncio.fixture
async def make_get_request(http_session):
    """
    Asynchronously make a GET request using the aiohttp client session.

    :param http_session: aiohttp client session.
    :return: A function that takes a URL path and query data, performs a GET request,
             and returns the response object augmented with the response time and body.
    """
    async def inner(path: str, query_data: dict | None = None):
        url = f'{test_settings.service_url}{path}'
        start = time.time()
        async with http_session.get(url, params=query_data) as response:
            response.body = await response.json()
            response.response_time = time.time() - start
            return response
    return inner
