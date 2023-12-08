import asyncio
import time

import asyncpg
from loguru import logger
from redis import ConnectionError, Redis


async def wait_for_postgres(dsn: str, max_retries: int = 50, sleep_interval: float = 1.0):
    """
    Wait for the PostgreSQL service to be available.

    :param dsn: The PostgreSQL DSN.
    :param max_retries: The maximum number of retries.
    :param sleep_interval: The time to sleep between retries in seconds.
    """
    retry_count = 0
    print(dsn)
    while retry_count < max_retries:
        try:
            conn = await asyncpg.connect(dsn=dsn)
            await conn.execute("SELECT 1")
            await conn.close()
            logger.info("PostgreSQL is ready.")
            return
        except Exception as e:
            logger.warning(dsn)
            logger.warning(f"An error occurred while connecting to PostgreSQL: {e}. Retrying...")
            retry_count += 1
            await asyncio.sleep(sleep_interval)
    logger.error("Max retries reached. Exiting...")


def wait_for_redis(redis_url: str, max_retries: int = 50, sleep_interval: float = 1.0):
    """
    Wait for the Redis service to be available.

    :param redis_url: The Redis URL.
    :param max_retries: The maximum number of retries.
    :param sleep_interval: The time to sleep between retries in seconds.
    """
    retry_count = 0
    redis_client = Redis.from_url(redis_url)

    try:
        while retry_count < max_retries:
            try:
                response = redis_client.ping()
            except ConnectionError:
                logger.warning("An error occurred while pinging Redis. Retrying...")
                retry_count += 1
                time.sleep(sleep_interval)
                continue

            if response:
                logger.info("Redis is ready.")
                break

            logger.warning("Ping to Redis unsuccessful. Retrying...")
            retry_count += 1
            time.sleep(sleep_interval)

        if retry_count >= max_retries:
            logger.error("Max retries reached. Exiting...")

    finally:
        del redis_client
