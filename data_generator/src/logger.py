import os

from loguru import logger

LOGS_LEVEL = os.getenv("LOGS_LEVEL", default="INFO")
LOGS_DIR = os.getenv("LOGS_DIR", default="logs")

logger.add(sink=f"{LOGS_DIR}/logs.log", level=LOGS_LEVEL, backtrace=False, diagnose=False, rotation='64 MB')
logger.add(sink=f"{LOGS_DIR}/error.log", level="ERROR", backtrace=False, diagnose=False, rotation='64 MB')
