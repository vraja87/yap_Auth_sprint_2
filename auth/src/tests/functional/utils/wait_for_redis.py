import os
import sys

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.join(current_path, '../../../..')
sys.path.append(parent_path)

from src.tests.functional.settings import test_settings
from src.utils.wait_for_it import wait_for_redis

if __name__ == '__main__':
    wait_for_redis(test_settings.redis_host)
