from functools import lru_cache
from pathlib import Path

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = Path('..') / '.env_auth'
env_file = env_path


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


class DbConf(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file,
                                      env_prefix='POSTGRES_')

    db: str
    user: str
    password: str
    host: str = 'auth_db'
    port: str = '5432'


class JaegerConf(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, env_prefix='JAEGER_')

    host: str = 'auth_jaeger'
    port: int = 6831


class FastApiConf(BaseSettings):
    """
    Configuration settings for the FastAPI application.
    """
    model_config = SettingsConfigDict(env_file=env_file, env_prefix='PROJECT_')

    name: str = 'auth'
    secret_key: str = 'secret'
    admin_login: str = 'admin'
    admin_passwd: str = 'admin'

    is_dev_mode: bool = True

    access_token_ttl: int = 60 * 30
    refresh_token_ttl: int = 60 * 60 * 24 * 2
    clear_expired_token_frequency: int = 60 * 60 * 12

    jaeger: JaegerConf = JaegerConf()

    def __hash__(self):
        return hash((self.name,
                     self.secret_key,
                     self.access_token_ttl,
                     self.refresh_token_ttl,
                     self.clear_expired_token_frequency))


@lru_cache()
def get_config() -> FastApiConf:
    return FastApiConf()


class RateLimitConfig(BaseSettings):
    """
    Configuration settings for the RateLimit service.
    """
    model_config = SettingsConfigDict(env_file=env_file, env_prefix='RATE_LIMIT_')

    is_on: bool = True
    times: int = 40
    times_anonymous: int = 10
    seconds: int = 60

    def __hash__(self):
        return hash((self.is_on,
                     self.times,
                     self.times_anonymous,
                     self.seconds))


@lru_cache()
def get_rate_limit_config() -> RateLimitConfig:
    return RateLimitConfig()
