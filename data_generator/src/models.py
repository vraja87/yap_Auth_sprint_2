import datetime
import uuid
from dataclasses import dataclass, field


@dataclass
class UUIDMixin:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class TimeStampedMixin:
    created: datetime.datetime = field(default_factory=datetime.datetime.now)
    modified: datetime.datetime = field(default_factory=datetime.datetime.now)


@dataclass
class FilmWork(UUIDMixin, TimeStampedMixin):
    title: str = field(default='')
    description: str = field(default=None)
    creation_date: datetime.date = field(default_factory=datetime.date.today)
    certificate: str = field(default='')
    file_path: str = field(default=None)
    rating: float = field(default=0.0)
    type: str = field(default='')


@dataclass
class Person(UUIDMixin, TimeStampedMixin):
    full_name: str = field(default='')
    gender: str = field(default=None)


@dataclass
class Genre(UUIDMixin, TimeStampedMixin):
    name: str = field(default='')
    description: str = field(default='')


@dataclass
class GenreFilmWork(UUIDMixin):
    film_work_id: uuid.UUID = field(default_factory=uuid.uuid4)
    genre_id: uuid.UUID = field(default_factory=uuid.uuid4)
    created: datetime.datetime = field(default_factory=datetime.datetime.now)


@dataclass
class PersonFilmWork(UUIDMixin):
    film_work_id: uuid.UUID = field(default_factory=uuid.uuid4)
    person_id: uuid.UUID = field(default_factory=uuid.uuid4)
    role: str = field(default='')
    created: datetime.datetime = field(default_factory=datetime.datetime.now)


TABLES = {
    'film_work': FilmWork,
    'person': Person,
    'genre': Genre,
    'person_film_work': PersonFilmWork,
    'genre_film_work': GenreFilmWork,
}
