import os

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

env_file = '.env' if os.path.exists('.env') else None


class CacheConfBase(BaseSettings):
    """
    Configuration settings for cache backend.

    :param backend_type: Type of cache backend.
    :param expire_in_second: Default cache expiration time in seconds.
    :param expire_low_in_second: Low-priority cache expiration time in seconds.
    """

    model_config = SettingsConfigDict(env_file=env_file, env_prefix='CACHE_')

    backend_type: str = 'redis'
    expire_in_second: int = 180
    expire_low_in_second: int = 30


class RedisConf(CacheConfBase):
    """
    Configuration settings for Redis.

    :param host: The Redis host address.
    :param port: The Redis port.
    """

    host: str = 'redis'
    port: int = 6379

    def get_init_params(self) -> dict:
        return {
            'host': self.host,
            'port': self.port,
        }


class CacheConf:
    """
    Class for reading Cache configuration.
    """
    _configs: dict[str, type[CacheConfBase]] = {}

    @classmethod
    def register_conf(cls, backend_type: str, conf_class: type[CacheConfBase]):
        """
        Registers a new cache backend configuration type and its corresponding class.

        :param backend_type: The type of the cache backend ('redis', etc.).
        :param conf_class: The class corresponding to the cache backend configuration.
        """
        cls._configs[backend_type] = conf_class

    @staticmethod
    def read_config() -> CacheConfBase:
        """
        Reads and returns cache settings according backend type.

        :return: The config settings for the chosen cache backend.
        """
        try:
            base_config = CacheConfBase()
        except ValidationError as e:
            raise ValueError("Invalid base cache configuration") from e

        backend_type = base_config.backend_type
        config_class = CacheConf._configs.get(backend_type)

        if config_class is None:
            raise ValueError(f"Unknown backend type: {backend_type}")

        try:
            return config_class()
        except ValidationError as e:
            raise ValueError(f"Invalid {backend_type} configuration") from e


CacheConf.register_conf('redis', RedisConf)


class SearchConfBase(BaseSettings):
    """
    Configuration settings for search backend.

    :param backend_type: Type of search backend.
    """
    model_config = SettingsConfigDict(env_file=env_file, env_prefix='SEARCH_')

    backend_type: str = 'elasticsearch'


class ElasticConf(SearchConfBase):
    """
    Configuration settings for Elasticsearch.

    :param host: The Elasticsearch host address.
    :param port: The Elasticsearch port.
    """

    host: str = 'elasticsearch'
    port: int = 9200

    def get_init_params(self) -> dict:
        return {
            'host': self.host,
            'port': self.port,
        }


class SearchConf:
    """
    Class for reading Search configuration.
    """
    _configs: dict[str, type[SearchConfBase]] = {}

    @classmethod
    def register_conf(cls, backend_type: str, conf_class: type[SearchConfBase]):
        """
        Registers a new search backend configuration type and its corresponding class.

        :param backend_type: The type of the search backend ('elasticsearch', etc.).
        :param conf_class: The class corresponding to the search backend configuration.
        """
        cls._configs[backend_type] = conf_class

    @staticmethod
    def read_config() -> SearchConfBase:
        """
        Reads and returns search settings according to the backend type.

        :return: The config settings for the chosen search backend.
        """
        try:
            base_config = SearchConfBase()
        except ValidationError as e:
            raise ValueError("Invalid base search configuration") from e

        backend_type = base_config.backend_type
        config_class = SearchConf._configs.get(backend_type)

        if config_class is None:
            raise ValueError(f"Unknown backend type: {backend_type}")

        try:
            return config_class()
        except ValidationError as e:
            raise ValueError(f"Invalid {backend_type} configuration") from e


SearchConf.register_conf('elasticsearch', ElasticConf)


class FastApiConf(BaseSettings):
    """
    Configuration settings for the FastAPI application.

    :param name: The name of the FastAPI application.
    """
    model_config = SettingsConfigDict(env_file=env_file, env_prefix='PROJECT_')

    name: str = 'movies'
