import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

env_file = '.env' if os.path.exists('.env') else None


class DbConf(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file,
                                      env_prefix='POSTGRES_')

    name: str = Field('movies_database', env='POSTGRES_DB')
    user: str
    password: str
    host: str = 'admin_db'
    port: str = '5432'


class ElasticConf(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, env_prefix='ELASTIC_')

    hosts: str = 'elasticsearch'


class CacheConf(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, env_prefix='CACHE_')

    main: str = './cache/main.txt'
    producer: str = './cache/postgres_producer.txt'
    enricher: str = './cache/postgres_enricher.txt'
    enricher_persons: str = './cache/postgres_enricher_persons.txt'
    merger: str = './cache/postgres_merger.txt'


class LogConf(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, env_prefix='LOG_')

    etl: str = './log/etl.log'


class MainConf(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, env_prefix='ETL_')

    limit_size: int = 100000
    sleep_period: float = 120
