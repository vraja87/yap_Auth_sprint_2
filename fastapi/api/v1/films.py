from http import HTTPStatus
from typing import Literal

import api.v1.api_examples as api_examples
from api.v1.constants import AllowedFilmSorting
from api.v1.models.film import FilmDetailsResponse, FilmResponse
from api.v1.models.genre import GenreResponse
from api.v1.models.person import PersonShortResponse
from core import config
from core.logger import logger
from services.film import FilmService, get_film_service

from fastapi import APIRouter, Depends, HTTPException, Query

router = APIRouter()
redis_conf = config.RedisConf()


@logger.catch
@router.get('/',
            summary='Retrieve Films Based on Multiple Filters',
            description='Fetch a list of films filtered by genres, IMDb rating, and sorting preferences.'
                        'Supports pagination.',
            response_model=list[FilmResponse] | None,
            responses=api_examples.films,
            )
async def films(genre: list[str] = Query([], min_length=0, max_length=5),
                genre_condition: Literal['all', 'any'] = Query('all'),
                sort_by: list[AllowedFilmSorting] = Query(['-imdb_rating'], alias='sort', min_length=1, max_length=5),
                rating_min: float | None = Query(None, ge=0),
                rating_max: float | None = Query(None),
                page_number: int = Query(0, ge=0, alias='page_number'),
                page_size: int = Query(100, ge=1, alias='page_size'),
                film_service: FilmService = Depends(get_film_service),
                ) -> list[FilmResponse]:
    """
    Retrieve a list of films based on various filter parameters.

    :param genre: List of genres to filter.
    :param genre_condition: Condition to apply for genre filtering ('all' or 'any').
    :param sort_by: List of fields to sort the results.
    :param rating_min: Minimum IMDb rating for filtering.
    :param rating_max: Maximum IMDb rating for filtering.
    :param page_number: Current page number.
    :param page_size: Number of items per page.
    :param film_service: Dependency to access the film service.
    :return: A list of films meeting the filter criteria.
    """

    try:
        result = await film_search(
            query=None,
            fuzziness=0,
            genre=genre,
            genre_condition=genre_condition,
            sort_by=sort_by,
            rating_min=rating_min,
            rating_max=rating_max,
            page_number=page_number,
            page_size=page_size,
            film_service=film_service
        )
        if result is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Films not found.')
        return result

    except HTTPException as e:
        raise e


@logger.catch
@router.get('/search/',
            summary='Search for Films with Query and Filters',
            description='Perform a fuzzy search for films based on a query string. '
                        'Further filter the results by genre, rating, and sort them according to preferences. '
                        'Supports pagination.',
            response_model=list[FilmResponse],
            responses=api_examples.film_search,
            )
async def film_search(query: str | None = Query(None, min_length=1, max_length=128),
                      fuzziness: int = Query(1, ge=0, le=3, alias='fuzzy'),
                      genre: list[str] = Query([], min_length=0, max_length=5),
                      genre_condition: Literal['all', 'any'] = Query('all'),
                      sort_by: list[AllowedFilmSorting] = Query(['-imdb_rating'],
                                                                alias='sort', min_length=1, max_length=5),
                      rating_min: float | None = Query(None, ge=0),
                      rating_max: float | None = Query(None),
                      page_number: int = Query(0, ge=0, alias='page_number'),
                      page_size: int = Query(100, ge=1, alias='page_size'),
                      film_service: FilmService = Depends(get_film_service)) -> list[FilmResponse]:
    """
    Perform a search for films based on a query string and various filter parameters.

    :param query: Search query string.
    :param fuzziness: Fuzziness level for the search.
    :param genre: List of genres to filter.
    :param genre_condition: Condition to apply for genre filtering ('all' or 'any').
    :param sort_by: List of fields to sort the results.
    :param rating_min: Minimum IMDb rating for filtering.
    :param rating_max: Maximum IMDb rating for filtering.
    :param page_number: Current page number.
    :param page_size: Number of items per page.
    :param film_service: Dependency to access the film service.
    :return: A list of films meeting the search and filter criteria.
    """
    if rating_max is not None and rating_min is not None and rating_max <= rating_min:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="rating_max must be greater than rating_min")
    params = {
                 'from_': page_number * page_size,
                 'size': page_size,
             }
    search_query = await film_service.construct_search_query(query=query, fuzziness=fuzziness)
    filter_query = await film_service.construct_filter_query(genres=genre, genre_condition=genre_condition)
    range_query = await film_service.construct_range_query(rating_min=rating_min, rating_max=rating_max)
    sort_query = await film_service.construct_sort_query(sort_by=sort_by)
    params = params | sort_query

    query = film_service.merge_queries(film_service.merge_queries(search_query, filter_query), range_query)

    if query:
        params['query'] = query

    films = await film_service.get_all(params)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Films not found.')

    return [FilmResponse(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in films]


@logger.catch
@router.get('/{film_id}',
            summary='Fetch Detailed Information of a Film by ID.',
            description='Retrieve detailed information about a film, including genres, '
                        'directors, actors, and writers, based on its unique ID.',
            response_model=FilmDetailsResponse,
            responses=api_examples.film_details,
            )
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> FilmDetailsResponse:
    """
    Retrieve detailed information about a specific film by its ID.

    :param film_id: The ID of the film to fetch details for.
    :param film_service: Dependency to access the film service.
    :return: Detailed information about the film.
    """
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Film not found.')
    return FilmDetailsResponse(uuid=film.uuid,
                               title=film.title,
                               imdb_rating=film.imdb_rating,
                               description=film.description,
                               genre=[GenreResponse(uuid=x.uuid, name=x.name) for x in film.genre_full],
                               directors=[PersonShortResponse(**x.model_dump(by_alias=False)) for x in film.directors],
                               actors=[PersonShortResponse(**x.model_dump(by_alias=False)) for x in film.actors],
                               wriers=[PersonShortResponse(**x.model_dump(by_alias=False)) for x in film.writers],
                               )
