from api.v1.models.base import UUIDMixin


class PersonsFilm(UUIDMixin):
    """
    Represents the films in which a person participated, along with their roles in those films.

    :param roles: A list of roles that the person had in the film.
    """
    roles: list[str]


class PersonShortResponse(UUIDMixin):
    """
    Short response model for person information.

    :param full_name: The full name of the person.
    """
    full_name: str


class PersonResponse(PersonShortResponse):
    """
    Detailed response model for person information, includes films and roles.

    :param films: A list of films in which the person participated, represented by the PersonsFilm model.
    """
    films: list[PersonsFilm]
