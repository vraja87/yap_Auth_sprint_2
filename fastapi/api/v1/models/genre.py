from api.v1.models.base import UUIDMixin


class GenreResponse(UUIDMixin):
    """
    Response model for genre information.

    :param name: The name of the genre.
    """
    name: str
