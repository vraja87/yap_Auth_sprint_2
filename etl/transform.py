from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ActorsWriters(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    name: str


class DbFilmPerson(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    fw_id: UUID = Field(default_factory=uuid4)
    created: datetime
    description: Optional[str]
    full_name: Optional[str]
    modified: datetime
    name: Optional[str]
    g_id: UUID = Field(default_factory=uuid4)
    rating: Optional[float]
    role: Optional[str]
    title: str
    type: str


class DbGenre(BaseModel):
    uuid: UUID = Field(default_factory=uuid4, alias='id')
    name: str
    modified: datetime


class DbPerson(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    fw_id: UUID = Field(default_factory=uuid4)
    role: str
    full_name: str
    modified: datetime


class EsGenre(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    name: str


class EsFilm(BaseModel):
    """
    схема ElasticSearch нужные данные:

    id - изменение в фильме. надо подтянуть все связанные данные
    imdb_rating
    genre - МАССИВ - изменение в жанре. затронет все связанные фильмы.
    title - title.raw
    description - МАССИВ
    director
    actors_names
    writers_names
    actors{
        id, name
    }
    writers{
        id, name
    }
    """
    uuid: UUID = Field(default_factory=uuid4)
    imdb_rating: Optional[float]
    title: str
    genre: list[str]
    genre_full: list[EsGenre]
    description: Optional[str]
    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]
    actors: list[ActorsWriters]
    writers: list[ActorsWriters]
    directors: list[ActorsWriters]


class EsPerson(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    full_name: str
    films: list[UUID]


class Transform:
    elastic_format: dict[UUID, EsFilm]
    raw_films_linked: list[dict]
    films_linked: list[DbFilmPerson]

    genres: list[DbGenre]
    el_genres: dict[UUID, EsGenre]

    persons: list[DbPerson]
    el_persons: dict[UUID, EsPerson]

    def __init__(self, films_linked: list[dict],
                 raw_genres: list[dict],
                 raw_persons: list[dict]) -> None:
        self.raw_films_linked = films_linked
        self.films_linked = [DbFilmPerson.model_validate(film_dict)
                             for film_dict in films_linked]

        self.genres = [DbGenre.model_validate(genre_dict) for genre_dict in
                       raw_genres]

        self.persons = [DbPerson.model_validate(person_dict) for person_dict in
                        raw_persons]
        self.el_persons = {}

    def reformat_genres(self) -> None:
        """Transform genres to elasticsearch format"""
        self.el_genres = {}
        for one_db_genre in self.genres:
            genre_dict = one_db_genre.model_dump()  # in dict
            genre_dict.pop('modified')  # drop unused field
            self.el_genres[
                genre_dict['uuid']
            ] = EsGenre.model_validate(genre_dict)

    def reformat_persons(self) -> None:
        """Transform persons to elasticsearch format"""
        self.el_persons: dict[UUID, dict] = {}
        for db_psn in self.persons:
            self.el_persons.setdefault(db_psn.id, {
                'films': set(),
            })
            self.el_persons[db_psn.id]['uuid'] = db_psn.id
            self.el_persons[db_psn.id]['full_name'] = db_psn.full_name
            self.el_persons[db_psn.id]['films'].add(db_psn.fw_id)
        self.el_persons = {id_: EsPerson.model_validate(psn_dict)
                           for id_, psn_dict in self.el_persons.items()}

    def reformat(self) -> None:
        """Приводим данные ближе к формату elasticsearch"""
        step_one: dict[UUID, dict] = {}
        # Первый этап. Укладываем данные ближе к формату эластик.
        for one_db_film in self.films_linked:
            step_one.setdefault(one_db_film.fw_id, {
                'genre': set(),
                'genre_full': set(),
                'directors': set(),
                'actors': set(),
                'writers': set(),
            })
            step_one[one_db_film.fw_id]['imdb_rating'] = one_db_film.rating
            step_one[one_db_film.fw_id]['title'] = one_db_film.title
            step_one[one_db_film.fw_id]['title.raw'] = one_db_film.title
            step_one[one_db_film.fw_id][
                'description'] = one_db_film.description

            step_one[one_db_film.fw_id]['genre'].add(one_db_film.name)
            step_one[one_db_film.fw_id]['genre_full'].add((one_db_film.g_id, one_db_film.name))

            if one_db_film.role == 'director':
                step_one[one_db_film.fw_id]['directors'].add(
                    (one_db_film.id, one_db_film.full_name)
                )
            if one_db_film.role == 'actor':
                step_one[one_db_film.fw_id]['actors'].add(
                    (one_db_film.id, one_db_film.full_name)
                )
            if one_db_film.role == 'writer':
                step_one[one_db_film.fw_id]['writers'].add(
                    (one_db_film.id, one_db_film.full_name)
                )
        # Второй этап. Укладываем данные ближе к формату эластик.
        self.elastic_format = {}
        for fw_id, film_dict in step_one.items():
            film_dict['actors'] = [{'uuid': uuid, 'name': name} for uuid, name
                                   in film_dict['actors']]
            film_dict['writers'] = [{'uuid': uuid, 'name': name} for uuid, name
                                    in film_dict['writers']]
            film_dict['directors'] = [{'uuid': uuid, 'name': name} for uuid, name
                                      in film_dict['directors']]

            film_dict['genre_full'] = [{'uuid': uuid, 'name': name} for uuid, name
                                       in film_dict['genre_full']]

            film_dict['actors_names'] = list(map(lambda x: x['name'],
                                                 film_dict['actors']))
            film_dict['writers_names'] = list(map(lambda x: x['name'],
                                                  film_dict['writers']))
            film_dict['directors_names'] = list(map(lambda x: x['name'],
                                                    film_dict['directors']))
            film_dict['uuid'] = fw_id
            self.elastic_format[fw_id] = EsFilm.model_validate(film_dict)
