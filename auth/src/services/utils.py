import uuid
from datetime import datetime

from sqlalchemy import delete, or_
from starlette.requests import Request
from user_agents import parse

from src.db.postgres import async_session
from src.models.entity import RefreshToken


def get_ip_address(request: Request) -> str:
    """
    Parse the client's IP address from the request.

    :param request: The Request object from FastAPI containing the request information.
    :return: A string representing the client's IP address.
    """
    return request.client.host


def get_user_agent(request: Request) -> str:
    """
    Parse the client's User-Agent information from the request header.

    :param request: The Request object from FastAPI containing the request information.
    :return: A string representing the client's operating system and browser information.
    """
    user_agent_string = request.headers.get('User-Agent')
    user_agent = parse(user_agent_string)
    os_info = f'{user_agent.os.family} {user_agent.os.version_string}'
    browser = f'{user_agent.browser.family} {user_agent.browser.version_string}'
    return f'{os_info} {browser}'


def calculate_ttl(exp: int) -> int:
    """
    Calculates the TTL (Time To Live) for a given expiry time.

    :param exp: The expiry time as a Unix timestamp.
    :return: The TTL in seconds.
    """
    return int((datetime.utcfromtimestamp(exp) - datetime.utcnow()).total_seconds()) + 1


class TokenCleaner:
    """
    A class for cleaning expired tokens from the database.
    """
    def __init__(self):
        self.db_session = None

    async def init_session(self):
        """
        Initializes an asynchronous session with the database if not already initialized.
        """
        if self.db_session is None:
            async with async_session() as session:
                self.db_session = session

    async def close_session(self):
        """
        Closes the asynchronous session with the database if it is open.
        """
        if self.db_session:
            await self.db_session.close()

    async def clear_expired_token(self):
        """
        Removes all expired tokens from the database. Tokens are considered expired if their
        expiry date has passed or if they are marked as invalid.
        """
        if self.db_session is None:
            await self.init_session()

        query = delete(RefreshToken).where(
            or_(
                RefreshToken.expiry_date < datetime.utcnow(),
                RefreshToken.is_valid.is_(False)
            )
        )
        await self.db_session.execute(query)
        await self.db_session.commit()


def generate_unique_login():
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    unique_login = f"{uuid.uuid4().hex}_{timestamp}"
    return unique_login


token_cleaner: TokenCleaner() = None
