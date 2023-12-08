from functools import lru_cache

from db.search_engine import AbstractSearchEngine, get_search_engine
from models.person import Person
from services.base import BaseService

from fastapi import Depends


class PersonService(BaseService):
    """
    Service class to handle operations related to persons.

    :param search_engine: The search engine.
    """
    index = 'persons'
    model = Person
    search_fields = ['full_name']


@lru_cache()
def get_person_service(search_engine: AbstractSearchEngine = Depends(get_search_engine)) -> PersonService:
    """
    Dependency function to get an instance of PersonService.

    :param search_engine: The search engine.
    :return: An instance of PersonService.
    """
    return PersonService(search_engine)
