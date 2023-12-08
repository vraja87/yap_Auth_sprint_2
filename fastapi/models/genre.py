from models.base import UUIDMixin


class Genre(UUIDMixin):
    """
    Genre model representing a film genre.

    :param name: The name of the genre.
    """
    name: str
