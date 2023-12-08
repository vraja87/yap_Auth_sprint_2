from typing import Literal

AllowedFilmSorting = Literal[
    'none',
    'title',
    '+title',
    '-title',
    'imdb_rating',
    '+imdb_rating',
    '-imdb_rating',
]
