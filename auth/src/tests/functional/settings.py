import os

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.config import RedisConf

env_file = '.env_auth' if os.path.exists('.env_auth') else None


class DbConf(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file,
                                      env_prefix='POSTGRES_')

    db: str
    user: str
    password: str
    host: str = 'auth_db'
    port: str = '5432'


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, env_prefix='TESTS_')

    redis_conf: RedisConf = RedisConf()
    redis_host: str = f'{redis_conf.host}://{redis_conf.host}:{redis_conf.port}'
    service_url: str = 'http://auth:8000'

    # diff prefixes for diff libs
    db_conf: DbConf = DbConf()

    dsn_params: str = f'{db_conf.user}:{db_conf.password}@{db_conf.host}:{db_conf.port}/{db_conf.db}'
    asyncpg_dsn: str = f'postgres://{dsn_params}'
    alchemy_dsn: str = f'postgresql+asyncpg://{dsn_params}'

    superuser_login: str = 'admin'
    superuser_passwd: str = 'admin'
    superuser_role: str = 'admin'

    def __init__(self, **data):
        super().__init__(**data)


test_settings = TestSettings()
