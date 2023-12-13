from http import HTTPStatus

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from sqlalchemy.exc import SQLAlchemyError

from src.api.v1 import roles, user
from src.core import config
from src.core.logger import logger
from src.db import cache
from src.db.cache import CacheBackendFactory, CacheClientInitializer
from src.db.postgres import create_database, db_conf
import src.services.utils as utils_service
from src.services.utils import TokenCleaner
from starlette.requests import Request

from fastapi import FastAPI, HTTPException
from fastapi.responses import ORJSONResponse

from src.utils.jaeger import configure_tracer

fast_api_conf = config.get_config()


configure_tracer(fast_api_conf.jaeger.host, fast_api_conf.jaeger.port)
app = FastAPI(
    title=fast_api_conf.name,
    docs_url='/api/openapi-auth',
    openapi_url='/api/openapi-auth.json',
    default_response_class=ORJSONResponse,
)


scheduler = AsyncIOScheduler()


@app.on_event('startup')
async def startup():
    """
    Initialize resources when the FastAPI application starts.

    Connect to Redis and config database.
    """

    if fast_api_conf.is_dev_mode:  # create db with alchemy instead of alembic in dev_mode
        await create_database()

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


@app.get("/health")
async def health_check():
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
    """strictly filter out any requests that do not have a header field"""
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
