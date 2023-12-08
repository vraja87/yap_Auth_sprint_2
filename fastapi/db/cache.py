from abc import ABC, abstractmethod
from typing import Any

import backoff
from core.logger import LoggerAdapter, logger
from redis.asyncio import ConnectionError, Redis


class CacheClientInitializer:
    """
    Initializes and closes cache clients based on the specified backend type.
    """
    @staticmethod
    @backoff.on_exception(backoff.expo, ConnectionError, factor=0.5, max_value=5.0,
                          max_tries=10, logger=LoggerAdapter(logger))
    async def initialize_client(backend_type: str, **kwargs) -> Redis | None:
        """
        Asynchronously initializes a cache client based on the given backend type.

        :param backend_type: The type of the cache backend ('redis', etc.).
        :param kwargs: Additional parameters required for initializing the cache client.
        :return: An initialized cache client.
        """
        if backend_type == 'redis':
            host = kwargs.get('host')
            port = kwargs.get('port')
            return Redis.from_url(f"redis://{host}:{port}")
        else:
            raise ValueError(f"Unknown cache backend type: {backend_type}")

    @staticmethod
    async def close_client(backend_type: str, client: Any):
        """
        Asynchronously closes a cache client based on the given backend type.

        :param backend_type: The type of the cache backend ('redis', etc.).
        :param client: The cache client instance to close.
        """
        if client is None:
            return
        if backend_type == 'redis':
            await client.close()
        else:
            raise ValueError(f"Unknown cache backend type: {backend_type}")


class CacheBackend(ABC):
    """
    Base class for cache backends.
    Defines the interface for cache operations like `get` and `set`.
    """
    def __init__(self):
        self.client = None

    @abstractmethod
    async def get(self, key: str) -> str | None:
        """
        Asynchronously retrieves the value for the given key from the cache.

        :param key: The key for which to retrieve the value.
        :return: The value associated with the key, or None if the key does not exist.
        """
        pass

    @abstractmethod
    async def set(self, key: str, value, expire: int):
        """
        Asynchronously sets the value for the given key in the cache with an expiration time.

        :param key: The key for which to set the value.
        :param value: The value to set.
        :param expire: The expiration time in seconds.
        """
        pass


class RedisCache(CacheBackend):
    """
    Redis implementation of the CacheBackend.

    :param redis: The Redis client.
    """
    def __init__(self, redis: Redis):
        super().__init__()
        self.client = redis

    @backoff.on_exception(backoff.expo, ConnectionError, factor=0.5, max_value=5.0,
                          max_tries=3, logger=LoggerAdapter(logger))
    async def get(self, key: str) -> str | None:
        """
        Asynchronously retrieves the value for the given key from the Redis cache.

        :param key: The key for which to retrieve the value.
        :return: The value associated with the key, or None if the key does not exist.
        """
        value = await self.client.get(key)
        return value

    @backoff.on_exception(backoff.expo, ConnectionError, factor=0.5, max_value=5.0,
                          max_tries=3, logger=LoggerAdapter(logger))
    async def set(self, key: str, value: str, expire: int) -> None:
        """
        Asynchronously sets the value for the given key in the Redis cache with an expiration time.

        :param key: The key for which to set the value.
        :param value: The value to set.
        :param expire: The expiration time in seconds.
        """
        await self.client.set(name=key, value=value, ex=expire)


class CacheBackendFactory:
    """
    Factory class for creating cache backends.
    Manages the registration and instantiation of various cache backends.
    """
    _backends: dict[str, type[CacheBackend]] = {}

    @classmethod
    def register_backend(cls, backend_type: str, backend_class: type[CacheBackend]) -> None:
        """
        Registers a new cache backend type and its corresponding class.

        :param backend_type: The type of the cache backend.
        :param backend_class: The class corresponding to the cache backend.
        """
        cls._backends[backend_type] = backend_class

    @classmethod
    async def create_backend(cls, backend_type: str, **kwargs: Any) -> CacheBackend:
        """
        Creates and returns an instance of the specified cache backend.

        :param backend_type: The type of the cache backend.
        :param kwargs: The keyword arguments to pass to the backend initializer.
        :return: An instance of the specified cache backend.
        """
        backend_class = cls._backends.get(backend_type)
        if backend_class is None:
            raise ValueError(f"Unknown cache backend type: {backend_type}")

        client = await CacheClientInitializer.initialize_client(backend_type, **kwargs)
        return backend_class(client)


CacheBackendFactory.register_backend('redis', RedisCache)


cache: CacheBackend | None = None


async def get_cache() -> CacheBackend:
    """
    Returns the Redis database instance.
    """
    return cache
