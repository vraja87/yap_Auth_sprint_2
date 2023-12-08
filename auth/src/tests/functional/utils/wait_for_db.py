import asyncio
import os
import sys

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.join(current_path, '../../../..')  # from service root
sys.path.append(parent_path)

from src.tests.functional.settings import test_settings
from src.utils.wait_for_it import wait_for_postgres

"""
Running db-wait-util for "tests" service.
"""

if __name__ == '__main__':
    asyncio.run(wait_for_postgres(test_settings.asyncpg_dsn))
