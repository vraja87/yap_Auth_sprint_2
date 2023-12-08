import os
import sys
import time

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.join(current_path, '..')

sys.path.append(parent_path)

from loguru import logger
from redis import ConnectionError, Redis
from settings import test_settings


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


if __name__ == '__main__':
    wait_for_redis(test_settings.redis_host)
