import os

from pydantic_settings import BaseSettings, SettingsConfigDict

env_file = '.env' if os.path.exists('.env') else None


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, env_prefix='TESTS_')

    es_host: str = 'http://elasticsearch:9200'
    redis_host: str = 'redis://redis:6379'
    es_index_movies: str = 'movies'
    es_index_persons: str = 'persons'
    es_index_genres: str = 'genres'
    es_indexes: list[str] | None = None
    es_id_field: str = 'uuid'
    service_url: str = 'http://fastapi:8000'

    def __init__(self, **data):
        super().__init__(**data)
        if not self.es_indexes:
            self.es_indexes = [self.es_index_movies,
                               self.es_index_persons,
                               self.es_index_genres,
                               ]


test_settings = TestSettings()
