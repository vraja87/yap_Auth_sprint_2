import uuid
from http import HTTPStatus

import src.services.utils as utils_service
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from create_admin import create_admin
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from fastapi.responses import Response
from sqlalchemy.exc import SQLAlchemyError
from src.api.v1 import roles, user
from src.core import config
from src.core.logger import logger
from src.db import cache
from src.db.cache import CacheBackendFactory, CacheClientInitializer
from src.db.postgres import create_database, db_conf
from src.services.utils import TokenCleaner
from src.utils.jaeger import configure_tracer
from starlette.datastructures import Headers
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware

from fastapi import FastAPI, HTTPException
from fastapi.responses import ORJSONResponse


fast_api_conf = config.get_config()


configure_tracer(fast_api_conf.jaeger.host, fast_api_conf.jaeger.port)
app = FastAPI(
    title=fast_api_conf.name,
    docs_url='/api/openapi-auth',
    openapi_url='/api/openapi-auth.json',
    default_response_class=ORJSONResponse,
)

app.add_middleware(SessionMiddleware, secret_key=fast_api_conf.secret_key_session)

scheduler = AsyncIOScheduler()


@app.on_event('startup')
async def startup():
    """
    Initialize resources when the FastAPI application starts.

    Connect to Redis and config database.
    """

    if fast_api_conf.is_dev_mode:
        await create_database()
        await create_admin()

    cache_conf = config.CacheConf.read_config()
    logger.info('Startup api service.')
    cache.cache = await CacheBackendFactory.create_backend(
        cache_conf.backend_type,
        **cache_conf.get_init_params()
    )
    utils_service.token_cleaner = TokenCleaner()
    await utils_service.token_cleaner.init_session()
    scheduler.add_job(utils_service.token_cleaner.clear_expired_token,
                      'interval',
                      seconds=fast_api_conf.clear_expired_token_frequency)
    scheduler.start()


@app.on_event('shutdown')
async def shutdown():
    """
    Release resources when the FastAPI application stops.

    Closes connections to Redis and Elasticsearch databases.
    """
    cache_conf = config.CacheConf.read_config()
    logger.info('Shutdown api service.')
    await CacheClientInitializer.close_client(
        cache_conf.backend_type,
        cache.cache.client
    )
    await utils_service.token_cleaner.close_session()
    scheduler.shutdown()


from src.services.rate_limit import rate_limit_dependency

from fastapi import Depends


@app.get("/health")
async def health_check(rate_limit=Depends(rate_limit_dependency)):
    """healthcheck for service"""
    return {"status": "ok"}


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Global exception handler for SQLAlchemyError.

    Intercepts all SQLAlchemyError exceptions that occur within the application and converts it into an HTTPException
    with status code of 500 (Internal Server Error).
    The detail of the exception (the error message) is included in the response body
    to provide more context about the error. (maybe bad idea)
    """
    return HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail=str(exc)
    )


@app.middleware('http')
async def before_request(request: Request, call_next):
    """Middleware to enforce the presence of 'X-Request-Id' header in all incoming requests.

    :param request: The incoming HTTP request instance.
    :param call_next: The function to call the next middleware or route handler.
    :return: An ORJSONResponse with status code 400 if 'X-Request-Id' is missing, otherwise proceeds to the next handler.
    """
    # TODO Have troubles with requests from movies-api swagger documentation.
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        return ORJSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content={'detail': 'X-Request-Id is required'}
        )
    return await call_next(request)

FastAPIInstrumentor.instrument_app(app)


app.include_router(user.router, prefix='/api/v1/user', tags=['user'])
app.include_router(roles.router, prefix='/api/v1/roles', tags=['roles'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app', host='0.0.0.0', port=8000, reload=True,
    )
