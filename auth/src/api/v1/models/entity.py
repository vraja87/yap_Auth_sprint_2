import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

from src.core.logger import logger


@logger.catch(reraise=True)
def validate_login(login: str) -> str:
    """Contain rules to validate login. min 2 max 25. Without spaces."""
    assert isinstance(login, str), f'login {login} is not a string'
    assert len(login) >= 2, f'login {login} too short'
    assert len(login) < 25, f'login {login} too large'
    assert ' ' not in login, f'Spaces not allowed for login {login}'
    assert re.match(r'^\w+$', login), f'Special characters not allowed in login {login}'
    return login


@logger.catch(reraise=True)
def validate_passwd(passwd: str) -> str:
    """Contain rules to validate password. Upper, lower letters, numbers, spec symbols."""
    assert isinstance(passwd, str), 'password is not a string'
    min_len = 4
    assert len(passwd) >= min_len, f'password must be min {min_len}'
    assert ' ' not in passwd, 'Spaces not allowed for password'
    assert re.search("[a-z]", passwd), 'password must contain lowercase letters'
    assert re.search("[A-Z]", passwd), 'password must contain uppercase letters'
    assert re.search("[0-9]", passwd), 'password must contain numbers'
    spec_symbols = '#%_@$!:?&?=*()'
    assert re.search(f"[{spec_symbols}]", passwd), f'password must contain spec symbols {spec_symbols}'
    return passwd


class UserCreate(BaseModel):
    login: Annotated[str, AfterValidator(validate_login)] = Field(example="user123")
    password: Annotated[str, AfterValidator(validate_passwd)] = Field(example="SecurePassword123!")
    first_name: str | None = Field(default=None, example="Albert")
    last_name: str | None = Field(default=None, example="Einstein")


class RoleCreate(BaseModel):
    name: str = Field(..., example="Admin")
    description: str | None = Field(default=None, example="Administrator role")


class UserUpdateRequest(UserCreate):
    login: Annotated[
        str | None,
        AfterValidator(validate_login)
    ] = Field(default=None, example="newuser123")

    password: Annotated[
        str | None,
        AfterValidator(validate_passwd)
    ] = Field(default=None, example="newSecurePassword123")


class UserInDB(BaseModel):
    id: UUID
    login: str
    first_name: str | None
    last_name: str | None

    class Config:
        from_attributes = True


class TwoTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGcixiOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class LoginHistoryResponse(BaseModel):
    user_agent: str
    ip_address: str
    login_date: datetime


class RoleNamesResponse(BaseModel):
    name: str


class RoleResponse(BaseModel):
    id: str
    name: str
    description: str | None


class AssignRoleRequest(BaseModel):
    user_id: UUID
    role_id: UUID
