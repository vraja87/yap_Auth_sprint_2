from http import HTTPStatus

import api.v1.api_examples as api_examples
from api.v1.models.film import FilmResponse
from api.v1.models.person import PersonResponse
from core.logger import logger
from services.film import FilmService, get_film_service
from services.person import PersonService, get_person_service

from fastapi import APIRouter, Depends, HTTPException, Query

router = APIRouter()


@logger.catch
@router.get('/{person_id}',
            response_model=PersonResponse,
            summary='Retrieve Detailed Information for a Specific Person by ID.',
            description='Obtain detailed information about a person identified by their unique ID,'
                        ' including their roles in various films.',
            responses=api_examples.person_id,
            )
async def person_details(
        person_id: str,
        person_service: PersonService = Depends(get_person_service),
        film_service: FilmService = Depends(get_film_service)) -> PersonResponse:
    """
    Fetch detailed information about a person by their ID.

    :param person_id: Unique identifier of the person.
    :param person_service: Dependency that provides access to the person service.
    :param film_service: Dependency that provides access to the film service.
    :return: A PersonResponse object containing detailed information about the person.
    """
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='person not found')

    if not person.films:
        films_result = []
    else:
        films_result = await film_service.get_roles_in_films(person)
    return PersonResponse(
        uuid=person.uuid,
        full_name=person.full_name,
        films=films_result,
    )


@logger.catch
@router.get('/{person_id}/film',
            response_model=list[FilmResponse],
            summary='List All Films Featuring a Specific Person by ID.',
            description='Get a list of films in which a person identified by their unique ID has participated,'
                        ' including their roles in those films.',
            responses=api_examples.person_film,

            )
async def persons_films(person_id: str,
                        person_service: PersonService = Depends(get_person_service),
                        film_service: FilmService = Depends(get_film_service)) -> list[FilmResponse]:
    """
    Fetch a list of films in which a person has participated, based on their ID.

    :param person_id: Unique identifier of the person.
    :param person_service: Dependency that provides access to the person service.
    :param film_service: Dependency that provides access to the film service.
    :return: A list of FilmResponse objects, each containing information about a film.
    """

    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='person not found')
    if not person.films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='films with person were not found')
    films = await film_service.get_person_films_info(person)
    return [FilmResponse(uuid=film['uuid'], title=film['title'], imdb_rating=film['imdb_rating']) for film in films]


@logger.catch
@router.get('/search/',
            response_model=list[PersonResponse],
            summary='Search for Persons by Full Name with Optional Fuzziness and Pagination.',
            description='Perform a search for persons based on their full names. '
                        'Supports fuzzy matching and pagination. '
                        'Fuzziness levels range from 0 to 3. Pagination parameters can be adjusted.',
            responses=api_examples.person_search,
            )
async def persons_search(
        query: str | None = None,
        fuzziness: int = Query(1, ge=0, le=3, alias='fuzzy'),
        page_number: int = Query(0, ge=0, alias='page_number'),
        page_size: int = Query(100, ge=1, alias='page_size'),
        person_service: PersonService = Depends(get_person_service),
        film_service: FilmService = Depends(get_film_service)) -> list[PersonResponse]:
    """
    Search for persons by their full names with optional fuzzy matching and pagination.

    :param query: Search query string for full names.
    :param fuzziness: Level of fuzzy matching. Ranges from 0 to 3.
    :param page_number: Page number for pagination.
    :param page_size: Number of results per page.
    :param person_service: Dependency that provides access to the person service.
    :param film_service: Dependency that provides access to the film service.
    :return: A list of PersonResponse objects, each containing information about a person.
    """
    params = {
                 'from_': page_number * page_size,
                 'size': page_size,
             }
    search_query = await person_service.construct_search_query(query=query, fuzziness=fuzziness)
    if search_query:
        params['query'] = search_query

    persons_list = await person_service.get_all(params)
    if not persons_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='persons not found')
    result_persons = []
    for person in persons_list:
        films_result = await film_service.get_roles_in_films(person)
        result_persons.append(
            PersonResponse(
                uuid=person.uuid,
                full_name=person.full_name,
                films=films_result,
            )
        )
    return result_persons
