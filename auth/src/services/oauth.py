import uuid
from abc import ABC, abstractmethod
from functools import lru_cache
from http import HTTPStatus

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.api.v1.models.entity import OauthData
from src.core.config import GoogleOAuthConfig, YandexOAuthConfig
from src.core.logger import logger
from src.db.postgres import AsyncSession, get_session
from src.models.entity import OAuth2User, User
from src.services.token import TokenService, get_token_service
from src.services.users import UserService, get_user_service
from src.services.utils import generate_unique_login


class OAuthProvider(ABC):
    """
    Abstract base class for OAuth providers. Defines a common interface for all OAuth providers.

    :param client: OAuth client used for interacting with the corresponding OAuth provider.
    :param provider: Name of the OAuth provider.
    """
    def __init__(self, client, provider):
        self.client = client
        self.provider = provider

    @abstractmethod
    async def process_token(self, token) -> OauthData:
        """
        Abstract method to process the received OAuth token.

        :param token: Token obtained from the OAuth provider.
        :return: User data OauthData.
        """
        pass

    async def redirect(self, request) -> RedirectResponse:
        """
        Redirects the user to the OAuth provider's authorization page.

        :param request: HTTP request from the user.
        :return: RedirectResponse to redirect the user.
        """
        redirect_uri = request.url_for('auth_callback', provider=self.provider)
        return await self.client.authorize_redirect(request, redirect_uri)

    async def authorize_access_token(self, request):
        """
        Authorizes and retrieves the available OAuth access token.

        :param request: HTTP request containing authorization data.
        :return: Authorized access token.
        """
        return await self.client.authorize_access_token(request)


class YandexOAuthProvider(OAuthProvider):
    """
    OAuth provider for Yandex. Handles the specifics of OAuth authentication for Yandex.

    :param client: OAuth client configured for Yandex.
    """
    def __init__(self, client):
        super().__init__(client, 'yandex')

    async def process_token(self, token) -> OauthData:
        """
        Processes the OAuth token obtained from Yandex. Extracts and returns the user's data.

        :param token: OAuth token received from Yandex after successful authentication.
        :return: User's data (such as user ID and email) wrapped in an OauthData object.
        """
        res = (await self.client.get('info', token=token)).json()
        user_id = res['id']
        user_email = res['default_email']
        return OauthData(user_id=user_id, email=user_email)


class GoogleOAuthProvider(OAuthProvider):
    """
    OAuth provider for Google. Manages the specific aspects of OAuth authentication for Google.

    :param client: OAuth client configured for Google.
    """
    def __init__(self, client):
        super().__init__(client, 'google')

    async def process_token(self, token) -> OauthData:
        """
         Processes the OAuth token obtained from Google. Extracts and returns the user's data.

         :param token: OAuth token received from Google after successful authentication.
         :return: User's data (such as user ID and email) wrapped in an OauthData object.
         """
        user_info = token['userinfo']
        user_id = user_info['sub']
        user_email = user_info['email']
        return OauthData(user_id=user_id, email=user_email)


class OAuthProviderFactory:
    @staticmethod
    def create_provider(name, client):
        """
        Factory for creating instances of OAuth providers.

        :param name: Name of the OAuth provider.
        :param client: OAuth client to use with the provider.
        :return: An instance of OAuthProvider for the given provider.
        :raises ValueError: If the provider name is not supported.
        """
        if name == 'yandex':
            return YandexOAuthProvider(client)
        elif name == 'google':
            return GoogleOAuthProvider(client)
        else:
            raise ValueError("Unsupported provider")


class OAuthService:
    """
    Service for handling OAuth authentication, including user and token management.

    :param db_session: Async database session for queries.
    :param user_service: Service for managing users.
    :param token_service: Service for handling tokens.
    """
    def __init__(self, db_session: AsyncSession, user_service: UserService, token_service: TokenService):
        self.db = db_session
        self.user_service = user_service
        self.token_service = token_service
        self.oauth = OAuth()
        self.yandex_config = YandexOAuthConfig()
        self.google_config = GoogleOAuthConfig()
        self.providers = {}
        self._register_providers()

    def _register_providers(self):
        self.oauth.register(
            name='yandex',
            client_id=self.yandex_config.client_id,
            client_secret=self.yandex_config.client_secret,
            authorize_url=self.yandex_config.authorize_url,
            access_token_url=self.yandex_config.access_token_url,
            redirect_uri=self.yandex_config.redirect_uri,
            api_base_url=self.yandex_config.api_base_url,
            client_kwargs={'scope': self.yandex_config.scope},
        )

        self.oauth.register(
            name='google',
            client_id=self.google_config.client_id,
            client_secret=self.google_config.client_secret,
            redirect_uri=self.google_config.redirect_uri,
            client_kwargs={'scope': self.google_config.scope},
            server_metadata_url=self.google_config.server_metadata_url
        )

    async def get_provider(self, name) -> OAuthProvider | None:
        """
        Retrieves an OAuth provider by name.

        :param name: Name of the OAuth provider.
        :return: An instance of the OAuth provider.
        """
        if name not in self.providers:
            client = self.oauth.create_client(name)
            provider = OAuthProviderFactory.create_provider(name, client)
            self.providers[name] = provider
        return self.providers[name]

    async def redirect(self, request: Request, provider: str) -> RedirectResponse:
        """
        Handles redirecting the user to the OAuth provider.

        :param request: HTTP request from the user.
        :param provider: Name of the OAuth provider.
        :return: RedirectResponse to redirect the user.
        """
        try:
            client = await self.get_provider(provider)
            if not client:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Wrong oauth provider.")
        except Exception as e:
            logger.error(f"Error getting OAuth provider: {e}")
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Error getting OAuth provider")

        try:
            return await client.redirect(request)
        except Exception as e:
            logger.error(f"Error during redirect to OAuth provider: {e}")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="OAuth redirect failed")

    async def authenticate(self, request, provider: str) -> [str, str, User]:
        """
        Authenticates the user through the OAuth provider and creates user records in the database.

        :param request: HTTP request from the user.
        :param provider: Name of the OAuth provider.
        :return: Access and refresh tokens for the user.
        """
        client = await self.get_provider(provider)
        try:
            token = await client.authorize_access_token(request)
        except OAuthError as error:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"{error}")
        user_data = await client.process_token(token)

        oauth_user = await self.db.scalar(
            select(OAuth2User).where(OAuth2User.oauth_id == user_data.user_id,
                                     OAuth2User.provider == provider)
        )

        if oauth_user:
            user = await self.db.get(User, oauth_user.user_id)
        else:
            try:
                login = generate_unique_login()
                user = User(login=login,
                            password=str(uuid.uuid4()),
                            email=user_data.email,
                            is_oauth2=True,
                            credentials_updated=False)
                self.db.add(user)
                await self.db.flush()
                oauth_user = OAuth2User(oauth_id=user_data.user_id, provider=provider, user_id=user.id)
                self.db.add(oauth_user)
                await self.db.commit()
            except SQLAlchemyError as e:
                logger.error(f"Database error during user creation: {e}")
                await self.db.rollback()
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="User creation failed")

        return await self.user_service.complete_authentication(user, request)


@lru_cache
def get_oauth_service(db_session: AsyncSession = Depends(get_session),
                      token_service: TokenService = Depends(get_token_service),
                      user_service: UserService = Depends(get_user_service)) -> OAuthService:
    """
    Dependency function to obtain an instance of OAuthService.

    :param db_session: An asynchronous database session for database operations.
    :param token_service: A service for managing JWT tokens.
    :param user_service: A service for managing user-related operations.
    :return: An instance of OAuthService.
    """
    return OAuthService(db_session=db_session, token_service=token_service, user_service=user_service)
