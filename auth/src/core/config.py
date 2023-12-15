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
    """
    Configuration settings for the database.

    :param db: Database name.
    :param user: Database user name.
    :param password: Database password.
    :param host: Database host, default is 'auth_db'.
    :param port: Database port, default is '5432'.
    """
    db: str
    user: str
    password: str
    host: str = 'auth_db'
    port: str = '5432'


class JaegerConf(BaseSettings):
    """
    Configuration settings for Jaeger tracing.

    :param host: Jaeger host, default is 'auth_jaeger'.
    :param port: Jaeger port, default is 6831.
    """
    model_config = SettingsConfigDict(env_file=env_file, env_prefix='JAEGER_')

    host: str = 'auth_jaeger'
    port: int = 6831


class FastApiConf(BaseSettings):
    """
    Configuration settings for the FastAPI application.

    :param name: Name of the FastAPI application.
    :param secret_key: Secret key used for cryptographic signing.
    :param secret_key_session: Secret key used for session management.
    :param admin_login: Default admin login name.
    :param admin_passwd: Default admin password.
    :param is_dev_mode: Flag to indicate if the application is running in development mode.
    :param access_token_ttl: Time-to-live for access tokens, in seconds.
    :param refresh_token_ttl: Time-to-live for refresh tokens, in seconds.
    :param clear_expired_token_frequency: Frequency to clear expired tokens, in seconds.
    :param jaeger: Configuration settings for Jaeger tracing integration.
    """
    model_config = SettingsConfigDict(env_file=env_file, env_prefix='PROJECT_')

    name: str = 'auth'
    secret_key: str = 'secret'
    secret_key_session: str = 'secret'
    admin_login: str = 'admin'
    admin_passwd: str = 'admin'

    is_dev_mode: bool = True
    enable_tracer: bool = True

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


class YandexOAuthConfig(BaseSettings):
    """
    Configuration settings for Yandex OAuth.

    :param client_id: Yandex OAuth client ID.
    :param client_secret: Yandex OAuth client secret.
    :param redirect_uri: Redirect URI for Yandex OAuth.
    :param scope: OAuth scopes, default is 'login:email'.
    :param authorize_url: URL to initiate authorization, default is Yandex's authorization URL.
    :param access_token_url: URL to obtain the access token, default is Yandex's token URL.
    :param api_base_url: Base URL for Yandex API, default is Yandex login API URL.
    """
    model_config = SettingsConfigDict(env_file=env_file, env_prefix='YANDEX_')

    client_id: str
    client_secret: str
    redirect_uri: str
    scope: str = 'login:email'
    authorize_url: str = 'https://oauth.yandex.ru/authorize'
    access_token_url: str = 'https://oauth.yandex.ru/token'
    api_base_url: str = 'https://login.yandex.ru/'


class GoogleOAuthConfig(BaseSettings):
    """
    Configuration settings for Google OAuth.

    :param client_id: Google OAuth client ID.
    :param client_secret: Google OAuth client secret.
    :param redirect_uri: Redirect URI for Google OAuth.
    :param scope: OAuth scopes, default is 'openid email'.
    :param server_metadata_url: URL for the OpenID Connect discovery document.
    """
    model_config = SettingsConfigDict(env_file=env_file, env_prefix='GOOGLE_')

    client_id: str
    client_secret: str
    redirect_uri: str
    scope: str = 'openid email'
    server_metadata_url: str = 'https://accounts.google.com/.well-known/openid-configuration'


@lru_cache()
def get_config() -> FastApiConf:
    """
    Caches and returns the FastAPI application configuration.

    :return: An instance of FastApiConf with the application configuration.
    """
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
