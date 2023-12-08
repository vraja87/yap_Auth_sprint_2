from models.base import UUIDMixin


class Person(UUIDMixin):
    """
    Person model representing a person involved in films.

    :param full_name: The full name of the person.
    :param films: A list of film IDs that the person has been involved in.
    """
    full_name: str
    films: list[str] = []
