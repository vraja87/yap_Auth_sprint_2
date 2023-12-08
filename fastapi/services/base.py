from abc import abstractmethod

from core import config
from db.search_engine import AbstractSearchEngine, SearchNotFoundError
from models import Film, Genre, Person
from services.cache import async_cache

cache_conf = config.CacheConf.read_config()


class BaseService:
    """
    Base class that provides common methods for all services.

    :param search_engine: The search engine.
    """
    def __init__(self, search_engine: AbstractSearchEngine):
        self.search_engine = search_engine

    @property
    @abstractmethod
    def index(self) -> str:
        pass

    @property
    @abstractmethod
    def search_fields(self) -> list[str] | None:
        return

    @staticmethod
    @abstractmethod
    def model(*args, **kwargs) -> Film | Person | Genre:
        pass

    async def get_by_id(self, id: str) -> Film | Person | Genre | None:
        """
        Fetches a document by its ID from Elasticsearch.

        :param id: The ID of the document to fetch.
        :return: An instance of Film, Person, or Genre if found; otherwise, None.
        """
        result = await self._get_by_id(id)
        if result is None:
            return
        return self.model(**result)

    @async_cache(expire=cache_conf.expire_in_second)
    async def _get_by_id(self, id: str) -> dict | None:
        """
        Fetches a document by its ID from Elasticsearch and caches the result.

        :param id: The ID of the document to fetch.
        :return: The fetched document as a dictionary or None if not found.
        """
        try:
            doc = await self.search_engine.get(index=self.index, id=id)
            return doc['_source']
        except SearchNotFoundError:
            return

    async def get_all(self, params: dict | None) -> list[Film | Person | Genre] | None:
        """
        Retrieves all documents based on the provided query parameters.

        :param params: Query parameters for fetching documents.
        :return: A list of Film, Person, or Genre instances or None if not found.
        """
        result = await self._get_all(params)
        if result is None:
            return
        return [self.model(**x) for x in result]

    @async_cache(expire=cache_conf.expire_in_second)
    async def _get_all(self, params: dict | None) -> list[dict]:
        """
        Retrieves all documents from Elasticsearch based on the query parameters and caches the result.

        :param params: Query parameters for fetching documents.
        :return: A list of fetched documents as dictionaries.
        """
        pagination = {
            'from_': params['from_'],
            'size': params['size'],
        }
        body = {
            'query': params['query'] if 'query' in params else None,
            'sort': params['sort'] if 'sort' in params else None,
        }
        if body['query'] is None:
            body['query'] = {}
            body['query']['match_all'] = {}

        try:
            result = await self.search_engine.search(index=self.index,
                                                     query=body['query'],
                                                     sort=body['sort'],
                                                     **pagination)
        except SearchNotFoundError:
            result = {}
            pass

        result = result.get('hits', {}).get('hits', [])
        if result:
            result = [x['_source'] for x in result]
        return result

    @async_cache(expire=cache_conf.expire_low_in_second)
    async def construct_search_query(self, query: str | None, fuzziness: int, search_fields: list[str] = None) -> dict:
        """
        Constructs a search query based on the given parameters.

        :param query: The search query string.
        :param fuzziness: Fuzziness level for the search.
        :param search_fields: Fields to search in. Defaults to None.
        :return: The constructed search query as a dictionary.
        """
        if query is None:
            return {}

        if search_fields is None:
            if self.search_fields is None:
                return {}
            search_fields = self.search_fields

        result = {'bool': {'must': []}}
        search_bool = {
            'bool': {
                'should': [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": search_fields,
                            "type": "best_fields",
                            'boost': 3,
                        }
                    }
                ]
            }
        }
        if fuzziness > 0:
            fuzziness_value = 'AUTO' if fuzziness > 2 else str(fuzziness)
            for field in search_fields:
                field_name = field.split("^")[0]
                search_bool['bool']['should'].append({
                    "fuzzy": {
                        field_name: {
                            "value": query,
                            "fuzziness": fuzziness_value,
                            'boost': 1,
                        }
                    }
                })

        result['bool']['must'].append(search_bool)
        return result

    @staticmethod
    def _validate_query_structure(query: dict):
        """
        Validates the structure of an Elasticsearch query.

        :param query: The Elasticsearch query to validate.
        :raises ValueError: If the query does not have the expected structure.
        """
        if 'bool' not in query:
            raise ValueError("Missing 'bool' key in query dict.")
        if 'must' not in query['bool']:
            raise ValueError("Missing 'must' key in query['bool'] dict.")

    def merge_queries(self, main_query: dict, new_query: dict) -> dict:
        """
        Merges two query dictionaries into a single query dictionary.

        :param main_query: The main query dictionary.
        :param new_query: The new query dictionary to merge.
        :return: The merged query dictionary.
        """
        if main_query:
            self._validate_query_structure(main_query)

        if new_query:
            self._validate_query_structure(new_query)
            if 'bool' not in main_query:
                main_query['bool'] = {'must': new_query['bool']['must']}
            else:
                main_query['bool']['must'].extend(new_query['bool']['must'])
        return main_query
