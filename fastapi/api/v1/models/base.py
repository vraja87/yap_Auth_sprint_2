from uuid import UUID, uuid4

from pydantic import BaseModel, Extra, Field


class UUIDMixin(BaseModel):
    """
    A mixin class to add a UUID field to models.

    :param uuid: A universally unique identifier for this object. Default is a generated UUID.
    """
    uuid: UUID = Field(default_factory=uuid4)

    class Config:
        extra = Extra.ignore
