from http import HTTPStatus

import functional.testdata.es_backup as es_mapping
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from functional.settings import test_settings
from loguru import logger


@pytest_asyncio.fixture(scope="session", autouse=True)
async def es_fill_indexes():
    """
    Asynchronously create and fill Elasticsearch indices for testing.

    This fixture runs automatically before the test session and
    - Creates an Elasticsearch client
    - Checks if the index exists; if so, deletes it
    - Creates a new index with settings and mappings
    - Fills the index with data
    - Refreshes all indices

    Yields:
        client: The Elasticsearch client.
    """

    logger.info("Create elasticsearch client.")

    async with AsyncElasticsearch(hosts=[test_settings.es_host]) as client:
        for index_name in test_settings.es_indexes:
            if await client.indices.exists(index=index_name):
                await client.indices.delete(index=index_name)
            logger.info(f"Create {index_name} index.")
            await client.indices.create(index=index_name,
                                        settings=es_mapping.index[index_name]['settings'],
                                        mappings=es_mapping.index[index_name]['mappings'])

        for index_name in test_settings.es_indexes:
            logger.info(f"Fill {index_name} index.")
            actions = [
                {
                    "_index": index_name,
                    "_id": doc.get("uuid", None),
                    "_source": doc
                }
                for doc in es_mapping.data[index_name]
            ]
            await async_bulk(client, actions)

        await client.indices.refresh(index="_all")
        for index_name in test_settings.es_indexes:
            await client.cluster.health(index=index_name, wait_for_status='yellow')

        yield client
        for index in test_settings.es_indexes:
            logger.info(f"Clear {index_name} index.")
            await client.options(
                ignore_status=[HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND]
            ).indices.delete(index=index)
