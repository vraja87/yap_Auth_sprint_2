import psycopg2
from psycopg2.extras import DictCursor

from logger import logger


class BaseDatabaseConnection:
    """
    Base class for managing database connections.

    :param db_config: Dictionary containing database configuration for the connection.
    """
    def __init__(self, db_config: dict):
        self.db_config = db_config
        self.conn = None

    def __enter__(self):
        """
        Enter method for context management.

        :return: Database connection instance.
        """
        return self.conn


class PostgresConnection(BaseDatabaseConnection):
    """
    Class for managing PostgreSQL database connections.

    Inherits from :class:`BaseDatabaseConnection`.

    :param db_config: Dictionary containing PostgreSQL database configuration.
    """
    def __init__(self, db_config: dict):
        super().__init__(db_config)
        logger.info("Establishing connection to psql DB.")
        self.conn = psycopg2.connect(**self.db_config, cursor_factory=DictCursor)
        logger.info("Connection to psql established")

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb):
        """
        Exit method for context management. Closes the database connection.

        :param exc_type: Type of the exception.
        :param exc_val: Exception value.
        :param exc_tb: Traceback information.
        """
        if self.conn:
            self.conn.close()
            logger.info("Connection to psql closed")
