from models.base import UUIDMixin
from models.genre import Genre
from pydantic import Field


class PersonShort(UUIDMixin):
    """
    A Pydantic model for short representation of a person.

    :param full_name: The full name of the person.
    """
    full_name: str = Field(..., alias='name')


class FilmShort(UUIDMixin):
    """
    A Pydantic model for short representation of a film.

    :param title: The title of the film.
    :param imdb_rating: The IMDb rating of the film, can be None.
    """
    title: str
    imdb_rating: float | None


class Film(FilmShort):
    """
    A Pydantic model for detailed representation of a film, inherits from FilmShort.

    :param description: A brief description of the film, default is empty string.
    :param genre: A list of genre names associated with the film.
    :param genre_full: A list of Genre (id, name) objects associated with the film.
    :param directors_names: A list of names of the directors of the film.
    :param actors_names: A list of names of the actors in the film.
    :param writers_names: A list of names of the writers of the film.
    :param actors: A list of PersonShort objects representing the actors.
    :param writers: A list of PersonShort objects representing the writers.
    :param directors: A list of PersonShort objects representing the directors.
    """
    description: str | None = ''
    genre: list[str]
    genre_full: list[Genre]
    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]
    actors: list[PersonShort]
    writers: list[PersonShort]
    directors: list[PersonShort]
