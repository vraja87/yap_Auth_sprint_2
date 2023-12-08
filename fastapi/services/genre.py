from functools import lru_cache

from db.search_engine import AbstractSearchEngine, get_search_engine
from models.genre import Genre
from services.base import BaseService

from fastapi import Depends


class GenreService(BaseService):
    """
    Service class to handle operations related to genres.

    :param search_engine: The search engine.
    """
    index = 'genres'
    model = Genre


@lru_cache()
def get_genre_service(search_engine: AbstractSearchEngine = Depends(get_search_engine)) -> GenreService:
    """
    Dependency function to get an instance of GenreService.

    :param search_engine: The search engine.
    :return: An instance of GenreService.
    """
    return GenreService(search_engine)
