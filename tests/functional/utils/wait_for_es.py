import os
import sys
import time

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.join(current_path, '..')

sys.path.append(parent_path)


from elasticsearch import Elasticsearch
from loguru import logger
from settings import test_settings


def wait_for_es_cluster(es_host: str, max_retries: int = 100, sleep_interval: float = 1.0):
    """
    Wait for the Elasticsearch cluster to be available and have a yellow or green status.

    :param es_host: The Elasticsearch host URL.
    :param max_retries: The maximum number of retries.
    :param sleep_interval: The time to sleep between retries in seconds.
    """
    retry_count = 0
    es_client = Elasticsearch(hosts=[es_host])

    try:
        while retry_count < max_retries:
            response = es_client.ping()

            if not response:
                logger.warning("Ping unsuccessful. Retrying...")
                retry_count += 1
                time.sleep(sleep_interval)
                continue

            health_response = es_client.cluster.health()
            if health_response and health_response['status'] in ['yellow', 'green']:
                logger.info(f"Cluster is ready with status {health_response['status']}.")
                break

            logger.warning(f"Cluster status is {health_response['status']}. Retrying...")
            retry_count += 1
            time.sleep(sleep_interval)

        if retry_count >= max_retries:
            logger.error("Max retries reached. Exiting...")

    finally:
        es_client.close()


if __name__ == '__main__':
    wait_for_es_cluster(test_settings.es_host)
