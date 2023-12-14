import asyncio
import os
import sys
import uuid

import aiohttp
from loguru import logger

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.join(current_path, '../../../..')  # from service root
sys.path.append(parent_path)

from src.tests.functional.settings import test_settings


async def wait_for_service(path: str, max_retries: int = 10, sleep_interval: float = 1.0):
    async with aiohttp.ClientSession() as http_session:
        retry_count = 0
        while retry_count < max_retries:
            try:
                url = f'{test_settings.service_url}{path}'
                headers = {'X-Request-Id': str(uuid.uuid4())}
                async with http_session.get(url, headers=headers) as response:
                    response_dict = await response.json()
                    logger.info(response)
                if response.status == 200 and 'status' in response_dict and response_dict['status'] == 'ok':
                    logger.info("Service is ready.")
                    return
                else:
                    logger.warning("Service is up but returned non-200 status code.")
            except Exception as e:
                logger.warning(f"An error occurred while connecting to Service: {e}. Retrying...")
                await asyncio.sleep(sleep_interval)
                retry_count += 1
        logger.error("Max retries reached. Exiting...")


if __name__ == '__main__':
    asyncio.run(wait_for_service('/health'))
