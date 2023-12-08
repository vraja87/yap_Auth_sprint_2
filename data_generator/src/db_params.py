import os

from dotenv import load_dotenv

from logger import logger

load_dotenv()
logger.info("Loaded values from .env file")

DSL = {
    'dbname': os.environ.get('POSTGRES_DB'),
    'user': os.environ.get('POSTGRES_USER'),
    'password': os.environ.get('POSTGRES_PASSWORD'),
    'host': os.environ.get('POSTGRES_HOST'),
    'port': os.environ.get('POSTGRES_PORT'),
}


SCHEMA = os.environ.get("SCHEMA", 'content')
