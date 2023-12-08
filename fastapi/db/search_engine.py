from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import Any

import backoff
from core.logger import LoggerAdapter, logger
from elasticsearch import (AsyncElasticsearch, BadRequestError,
                           ConnectionError, NotFoundError)

from fastapi import HTTPException


class SearchNotFoundError(Exception):
    """Raised when a search query returns no results."""
    pass


class SearchClientInitializer:
    """
    Initializes and closes search engine clients based on the specified backend type.
    """

    @staticmethod
    @backoff.on_exception(backoff.expo, ConnectionError, factor=0.5, max_value=5.0,
                          max_tries=10, logger=LoggerAdapter(logger))
    async def initialize_client(backend_type: str, **kwargs) -> AsyncElasticsearch | None:
        """
        Asynchronously initializes a search engine client based on the given backend type.

        :param backend_type: The type of the search engine backend ('elasticsearch', etc.).
        :param kwargs: Additional parameters required for initializing the search engine client.
        :return: An initialized search engine client.
        """
        if backend_type == 'elasticsearch':
            host = kwargs.get('host')
            port = kwargs.get('port')
            return AsyncElasticsearch(hosts=[f'http://{host}:{port}'])
        else:
            raise ValueError(f"Unknown search engine backend type: {backend_type}")

    @staticmethod
    async def close_client(backend_type: str, client: Any):
        """
        Asynchronously closes a search engine client based on the given backend type.

        :param backend_type: The type of the search engine backend ('elasticsearch', etc.).
        :param client: The search engine client instance to close.
        """
        if client is None:
            return

        if backend_type == 'elasticsearch':
            await client.close()
        else:
            raise ValueError(f"Unknown search engine backend type: {backend_type}")


class AbstractSearchEngine(ABC):
    """
    Abstract class for interacting with search engines like Elasticsearch.

    Defines the required operations.
    """
    def __init__(self, client: Any):
        self.client = client

    @abstractmethod
    async def get(self, index: str, id: type) -> dict | None:
        """
        Retrieve a document by its index and ID.

        :param index: The index to search in.
        :param id: The ID of the document to retrieve.
        :return: The retrieved document.
        """
        pass

    @abstractmethod
    async def mget(self, index: str, ids: list, source_includes: list[str]) -> list[dict] | None:
        """
        Retrieve multiple documents by their index and IDs.

        :param index: The index to search in.
        :param ids: The IDs of the documents to retrieve.
        :param source_includes: Fields to include in the response.
        :return: A list of retrieved documents.
        """
        pass

    @abstractmethod
    async def search(self, index: str, query: dict, sort: dict[dict], from_: int = 0, size: int = 100) -> dict | None:
        """
        Perform a search query on the given index.

        :param index: The index to search in.
        :param query: The search query.
        :param sort: The sorting criteria.
        :param from_: The starting index for pagination.
        :param size: The number of results to return.
        :return: A dictionary containing the search results.
        """
        pass


class ElasticSearchEngine(AbstractSearchEngine):

    @backoff.on_exception(backoff.expo, ConnectionError, factor=0.5, max_value=5.0,
                          max_tries=5, logger=LoggerAdapter(logger))
    async def get(self, index: str, id: type) -> dict | None:
        try:
            return await self.client.get(index=index, id=id)
        except NotFoundError as e:
            raise SearchNotFoundError(f"Document not found in Elasticsearch: {str(e)}") from e

    @backoff.on_exception(backoff.expo, ConnectionError, factor=0.5, max_value=5.0,
                          max_tries=5, logger=LoggerAdapter(logger))
    async def mget(self, index: str, ids: list, source_includes: list[str]) -> list[dict] | None:
        try:
            return await self.client.mget(index=index, ids=ids, source_includes=source_includes)
        except NotFoundError as e:
            raise SearchNotFoundError(f"Document not found in Elasticsearch: {str(e)}") from e

    @backoff.on_exception(backoff.expo, ConnectionError, factor=0.5, max_value=5.0,
                          max_tries=5, logger=LoggerAdapter(logger))
    async def search(self, index: str, query: dict, sort: dict[dict], from_: int = 0, size: int = 100) -> dict | None:
        try:
            return await self.client.search(index=index, query=query, sort=sort, from_=from_, size=size)
        except NotFoundError as e:
            raise SearchNotFoundError(f"Document not found in Elasticsearch: {str(e)}") from e
        except BadRequestError:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid request parameters")


class SearchBackendFactory:
    """
    Factory class for creating search backends.
    Manages the registration and instantiation of various search backends.
    """
    _backends: dict[str, type[AbstractSearchEngine]] = {}

    @classmethod
    def register_backend(cls, backend_type: str, backend_class: type[AbstractSearchEngine]) -> None:
        """
        Registers a new search backend type and its corresponding class.

        :param backend_type: The type of the search backend.
        :param backend_class: The class corresponding to the search backend.
        """
        cls._backends[backend_type] = backend_class

    @classmethod
    async def create_backend(cls, backend_type: str, **kwargs: type) -> AbstractSearchEngine:
        """
        Asynchronously creates and returns an instance of the specified search backend.

        :param backend_type: The type of the search backend.
        :param kwargs: The keyword arguments to pass to the backend initializer.
        :return: An instance of the specified search backend.
        """
        backend_class = cls._backends.get(backend_type)
        if backend_class is None:
            raise ValueError(f"Unknown search backend type: {backend_type}")

        client = await SearchClientInitializer.initialize_client(backend_type, **kwargs)
        return backend_class(client)


SearchBackendFactory.register_backend('elasticsearch', ElasticSearchEngine)


search_engine: AbstractSearchEngine | None = None


async def get_search_engine() -> AbstractSearchEngine:
    """
    Returns the Elasticsearch database instance.
    """
    return search_engine
