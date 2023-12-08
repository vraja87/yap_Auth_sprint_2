from http import HTTPStatus

import api.v1.api_examples as api_examples
from api.v1.models.genre import GenreResponse
from core.logger import logger
from services.genre import GenreService, get_genre_service

from fastapi import APIRouter, Depends, HTTPException, Query

router = APIRouter()


@logger.catch
@router.get('/{genre_id}',
            response_model=GenreResponse,
            summary='Fetch Detailed Information of a Genre by ID.',
            description='Retrieve detailed information for a genre, '
                        'including its unique identifier and name, based on its unique ID.',
            responses=api_examples.genre,
            )
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> GenreResponse:
    """
    Fetches the details of a genre by its ID.

    :param genre_id: The ID of the genre to retrieve.
    :param genre_service: Dependency that provides access to the genre service.
    :return: The genre details in the format of GenreResponse model.
    """
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='Genre not found.')
    return GenreResponse(uuid=genre.uuid, name=genre.name)


@logger.catch
@router.get('/',
            response_model=list[GenreResponse],
            summary=' Fetch All Genres with Pagination Support.',
            description='Get a list of all genres available in the database. '
                        'Supports pagination and sorting by genre name.',
            responses=api_examples.genres,
            )
async def genres_all(genre_service: GenreService = Depends(get_genre_service),
                     page_number: int = Query(0, ge=0, alias='page_number'),
                     page_size: int = Query(100, ge=1, alias='page_size'),
                     ) -> list[GenreResponse]:
    """
    Fetches all genres with pagination support.

    :param genre_service: Dependency that provides access to the genre service.
    :param page_number: The current page number, starts at 0.
    :param page_size: The number of genres to return per page.
    :return: A list of genres in the format of GenreResponse model.
    """
    params = {
        'from_': page_number * page_size,
        'size': page_size,
        'sort': [
            {
                'name.keyword': 'asc',
            }
        ]
    }
    genres = await genre_service.get_all(params)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Genres not found.')

    result = [GenreResponse(uuid=genre.uuid, name=genre.name) for genre in genres]
    return result
