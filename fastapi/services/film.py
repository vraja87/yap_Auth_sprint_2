from functools import lru_cache

from core import config
from db.search_engine import AbstractSearchEngine, get_search_engine
from models import Film, Person
from services.base import BaseService
from services.cache import async_cache

from fastapi import Depends

cache_conf = config.CacheConf.read_config()


class FilmService(BaseService):
    """
    Service class to handle operations related to films.

    :param search_engine: The search engine.
    """
    index = 'movies'
    model = Film
    search_fields = ['title^3', 'description']
    roles = ('actor', 'writer', 'director')

    @async_cache(expire=cache_conf.expire_in_second)
    async def get_roles_in_films(self, person: Person) -> list[dict[str, list[str]]]:
        """
        Fetches the roles a person has played in films.

        :param person: The Person model instance.
        :return: A list of dictionaries containing the roles a person has played in films.
        """
        films_ids = person.films
        response = await self.search_engine.mget(index=self.index,
                                                 ids=films_ids,
                                                 source_includes=[f'{x}s.uuid' for x in self.roles])
        person_uuid = str(person.uuid)
        result = []
        for item in response['docs']:
            if not item['found']:
                continue
            movie_roles = {
                'roles': [],
                'uuid': item['_id'],
            }
            item = item['_source']
            for role in self.roles:
                if any(x['uuid'] == person_uuid for x in item.get(f'{role}s', [])):
                    movie_roles['roles'].append(role)
            result.append(movie_roles)
        return result

    @async_cache(expire=cache_conf.expire_in_second)
    async def get_person_films_info(self, person: Person) -> list[dict]:
        """
        Fetches the film information for a specific person.

        :param person: The Person model instance.
        :return: A list of dictionaries containing film information for the person.
        """
        films_ids = person.films
        response = await self.search_engine.mget(index=self.index,
                                                 ids=films_ids,
                                                 source_includes=('uuid', 'title', 'imdb_rating'))
        return [x['_source'] for x in response['docs'] if x['found']]

    @staticmethod
    @async_cache(expire=cache_conf.expire_low_in_second)
    async def construct_sort_query(sort_by: list[str]) -> dict:
        """
        Constructs the sort query for Elasticsearch.

        :param sort_by: List of fields to sort by.
        :return: A dictionary containing the sorting query.
        """
        sort_settings = {}
        if 'none' in sort_by:
            return sort_settings
        sort_settings['sort'] = []

        for x in sort_by:
            if x.startswith('-'):
                field = x[1:]
                order = 'desc'
            else:
                if x.startswith('+'):
                    field = x[1:]
                else:
                    field = x
                order = 'asc'

            if field == 'imdb_rating':
                sort_settings['sort'].append({
                    field: order,
                })
            elif field == 'title':
                sort_settings['sort'].append({
                    f'{field}.raw': order,
                })
            else:
                raise ValueError(f"{field} doesn't support as sorting filed.")
        return sort_settings

    @staticmethod
    @async_cache(expire=cache_conf.expire_low_in_second)
    async def construct_filter_query(genres: list[str], genre_condition: str) -> dict:
        """
        Constructs the filter query based on genres for Elasticsearch.

        :param genres: List of genres to filter by.
        :param genre_condition: Condition to apply ('any' or 'all').
        :return: A dictionary containing the filter query.
        """
        if not genres:
            return {}

        filter_settings = {
            'bool': {
                'must': [],
            }
        }

        if genre_condition == 'any':
            filter_settings['bool']['must'].append({
                "nested": {
                    "path": "genre_full",
                    "query": {
                        "terms": {
                            "genre_full.uuid": genres,
                        }
                    }
                }
            })
        else:
            for genre in genres:
                filter_settings['bool']['must'].append({
                    "nested": {
                        "path": "genre_full",
                        "query": {
                            "terms": {
                                "genre_full.uuid": [genre]
                            }
                        }
                    }
                })
        return filter_settings

    @staticmethod
    @async_cache(expire=cache_conf.expire_low_in_second)
    async def construct_range_query(rating_min: float | None, rating_max: float | None) -> dict:
        """
        Constructs the range query based on IMDb ratings for Elasticsearch.

        :param rating_min: Minimum rating to filter by.
        :param rating_max: Maximum rating to filter by.
        :return: A dictionary containing the range query.
        """
        if rating_min is None and rating_max is None:
            return {}
        filter_settings = {
            'bool': {
                'must': [],
            }
        }
        if rating_min is not None and rating_max is not None:
            filter_settings['bool']['must'].append({
                'range': {
                    'imdb_rating': {'gte': rating_min, 'lte': rating_max}
                }
            })
        elif rating_min is not None:
            filter_settings['bool']['must'].append({
                'range': {
                    'imdb_rating': {'gte': rating_min}
                }
            })
        else:
            filter_settings['bool']['must'].append({
                'range': {
                    'imdb_rating': {'lte': rating_max}
                }
            })
        return filter_settings


@lru_cache()
def get_film_service(search_engine: AbstractSearchEngine = Depends(get_search_engine)) -> FilmService:
    """
    Dependency function to get an instance of FilmService.

    :param search_engine: The search engine.
    :return: An instance of FilmService.
    """
    return FilmService(search_engine)
