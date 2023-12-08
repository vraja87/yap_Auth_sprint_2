from api.v1 import films, genres, persons
from core import config
from core.logger import logger
from db import cache, search_engine
from db.cache import CacheBackendFactory, CacheClientInitializer
from db.search_engine import SearchBackendFactory, SearchClientInitializer

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

fast_api_conf = config.FastApiConf()

app = FastAPI(
    title=fast_api_conf.name,
    docs_url='/api/openapi-movies',
    openapi_url='/api/openapi-movies.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    """
    Initialize resources when the FastAPI application starts.

    Connects to Redis and Elasticsearch databases.
    """
    cache_conf = config.CacheConf.read_config()
    search_conf = config.SearchConf.read_config()
    logger.info('Startup api service.')
    cache.cache = await CacheBackendFactory.create_backend(
        cache_conf.backend_type,
        **cache_conf.get_init_params()
    )
    search_engine.search_engine = await SearchBackendFactory.create_backend(
        search_conf.backend_type,
        **search_conf.get_init_params()
    )


@app.on_event('shutdown')
async def shutdown():
    """
    Release resources when the FastAPI application stops.

    Closes connections to Redis and Elasticsearch databases.
    """
    cache_conf = config.CacheConf.read_config()
    search_conf = config.SearchConf.read_config()
    logger.info('Shutdown api service.')
    await CacheClientInitializer.close_client(
        cache_conf.backend_type,
        cache.cache.client
    )
    await SearchClientInitializer.close_client(
        search_conf.backend_type,
        search_engine.search_engine.client
    )


app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])
