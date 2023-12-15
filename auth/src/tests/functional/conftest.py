import asyncio
import json
import time
import uuid

import aiohttp
import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.ddl import CreateTable

from src.models.entity import Base

from .settings import test_settings
from .testdata.common_test_db_data import (get_user_roles, login_histories,
                                           roles, users_obj)


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
async def make_get_request(http_session: aiohttp.ClientSession):
    """
    Asynchronously make a GET request using the aiohttp client session.

    :param http_session: aiohttp client session.
    :return: A function that takes a URL path and query data, performs a GET request,
             and returns the response object augmented with the response time and body.
    """
    async def inner(path: str, query_data: dict | None = None, headers: dict | None = None):
        if headers is None:
            headers = {}
        headers.setdefault('X-Request-Id', str(uuid.uuid4()))
        url = f'{test_settings.service_url}{path}'
        start = time.time()
        async with http_session.get(url, params=query_data, headers=headers) as response:
            response.body = await response.json()
            response.response_time = time.time() - start
            return response
    return inner


@pytest_asyncio.fixture
async def make_post_request(http_session: aiohttp.ClientSession):
    """
    Asynchronously make a POST request using the aiohttp client session.

    :param http_session: aiohttp client session.
    :return: A function that takes a URL path and query data, performs a GET request,
             and returns the response object augmented with the response time and body.
    """
    async def inner(path: str, query_data: dict | None = None, headers={"Content-Type": "application/json"},
                    is_json_data=True):
        if headers is None:
            headers = {}
        headers.setdefault('X-Request-Id', str(uuid.uuid4()))
        url = f'{test_settings.service_url}{path}'
        start = time.time()
        if is_json_data:
            data = json.dumps(query_data) if query_data else None
        else:
            data = query_data
        async with http_session.post(url, data=data, headers=headers) as response:
            response.body = await response.json()
            response.response_time = time.time() - start
            return response
    return inner


@pytest_asyncio.fixture
async def make_post_request__form_data(http_session: aiohttp.ClientSession):
    async def inner(path: str, query_data: dict | None = None, headers=None):
        if headers is None:
            headers = {}
        headers.setdefault('X-Request-Id', str(uuid.uuid4()))
        url = f'{test_settings.service_url}{path}'
        start = time.time()
        # Transfer data as `data` to match the `application/x-www-form-urlencoded` format
        async with http_session.post(url, data=query_data, headers=headers) as response:
            response.body = await response.json()
            response.response_time = time.time() - start
            return response
    return inner


@pytest_asyncio.fixture
async def make_post_request_for_login(http_session: aiohttp.ClientSession):
    async def inner(path: str, query_data: dict | None = None, json_encode=True):
        headers = {'X-Request-Id': str(uuid.uuid4())}
        url = f'{test_settings.service_url}{path}'
        start = time.time()
        async with http_session.post(url, data=query_data, headers=headers) as response:
            if json_encode:
                response.body = await response.json()
            else:
                response.body = await response.text()
            response.response_time = time.time() - start
            return response
    return inner


@pytest_asyncio.fixture
async def make_patch_request(http_session: aiohttp.ClientSession):
    async def inner(path: str, query_data: dict | None = None, headers: dict | None = None):
        if headers is None:
            headers = {}
        headers.setdefault('X-Request-Id', str(uuid.uuid4()))
        url = f'{test_settings.service_url}{path}'
        start = time.time()
        async with http_session.patch(url, json=query_data, headers=headers) as response:
            response.body = await response.json()
            response.response_time = time.time() - start
            return response
    return inner


@pytest_asyncio.fixture
async def make_delete_request(http_session: aiohttp.ClientSession):
    async def inner(path: str, query_data: dict | None = None, headers=None):
        if headers is None:
            headers = {}
        headers['X-Request-Id'] = str(uuid.uuid4())
        url = f'{test_settings.service_url}{path}'
        start = time.time()
        async with http_session.delete(url, json=query_data, headers=headers) as response:
            response.body = await response.json()
            response.response_time = time.time() - start
            return response
    return inner


@pytest.fixture(scope="session")
async def create_tables(engine):
    """create tables without main auth service where is the same logic
    Turned off for now.
    """
    async with engine.begin() as conn:  # async variant
        for table in Base.metadata.tables.values():
            create_stmt = CreateTable(table)
            await conn.execute(create_stmt)
    yield
    with engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(text(f"TRUNCATE TABLE {table.name} CASCADE;"))
        conn.execute(text("COMMIT;"))


@pytest.fixture(scope="session")
async def alchemy_session(engine):
    """Создает новую сессию для теста."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    session = async_session()
    yield session
    await session.close()
    # Turned off too. test db will be deleted with container
    # session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # session = session_local()
    # yield session
    # session.close()


@pytest.fixture(scope="session")
def engine():
    engine = create_async_engine(test_settings.alchemy_dsn, echo=True, future=True)
    return engine


@pytest.fixture(scope="session", autouse=True)
async def initialize_test_data(alchemy_session: AsyncSession):
    alchemy_session.add_all(users_obj)
    alchemy_session.add_all(roles)
    await alchemy_session.commit()
    user_roles = get_user_roles(users_obj, roles)  # we need uuid's, after writing them to db.
    alchemy_session.add_all(user_roles)
    await alchemy_session.commit()
    alchemy_session.add_all(login_histories)
    await alchemy_session.commit()
    yield
    # Turned off too. test db will be deleted with container
    # await alchemy_session.execute(
    #     'TRUNCATE TABLE '
    #     'content.users, content.roles, content.user_roles, content.refresh_tokens, content.login_histories '
    #     'RESTART IDENTITY CASCADE'
    # )
    # await alchemy_session.commit()
