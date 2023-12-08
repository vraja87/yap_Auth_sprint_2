from api.v1.models.base import UUIDMixin
from api.v1.models.genre import GenreResponse
from api.v1.models.person import PersonShortResponse


class FilmResponse(UUIDMixin):
    """
    Response model for film information.

    :param title: The title of the film.
    :param imdb_rating: The IMDb rating of the film, if available.
    """
    title: str
    imdb_rating: float | None


class FilmDetailsResponse(FilmResponse):
    """
    Detailed response model for a film, extends FilmResponse.

    :param description: A short description of the film.
    :param genre: List of genres the film belongs to.
    :param actors: List of actors in the film.
    :param writers: List of writers of the film.
    :param directors: List of directors of the film.
    """
    description: str | None
    genre: list[GenreResponse] = []
    actors: list[PersonShortResponse] = []
    writers: list[PersonShortResponse] = []
    directors: list[PersonShortResponse] = []
