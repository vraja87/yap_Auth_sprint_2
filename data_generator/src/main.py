import os
from dataclasses import astuple, fields

from dotenv import load_dotenv
from psycopg2 import Error as PsycopgError
from psycopg2.extensions import connection as _connection

from db_connection import PostgresConnection
from db_params import DSL
from fake_gerators import FakeDataGenerator, generate_data
from logger import logger
from models import TABLES
from queries import INSERT_ALL

load_dotenv()


class PSQLWriter:
    """
    Class responsible for writing data to a PostgreSQL table.

    :param connection: A PostgreSQL database connection.
    """
    def __init__(self, connection: _connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def write_data(self, data_generator, table, table_class):
        """
        Writes data to a PostgreSQL table using a data generator.

        :param data_generator: Generator that yields batches of data.
        :param table: Name of the table to insert data into.
        :param table_class: Dataclass representing the table structure.
        """
        columns = [field.name for field in fields(table_class)]
        n = len(columns)
        head_str = '({})'.format(','.join(["%s"] * n))
        columns_str = '({})'.format(','.join(columns))
        for data in data_generator:
            data = [astuple(x) for x in data]
            values = ','.join(self.cursor.mogrify(head_str, x).decode('utf-8') for x in data)
            query = INSERT_ALL.format(table, columns_str, values)
            try:
                self.cursor.execute(query)
            except PsycopgError as e:
                logger.error(e)
                logger.error(query)
                break
            self.connection.commit()


def load_fake_data(pg_conn: _connection, batch_size: int):
    """
    Loads fake data into PostgreSQL tables.

    :param pg_conn: A PostgreSQL database connection.
    :param batch_size: Size of each data batch to be inserted.
    """
    logger.info("Generating fake data.")
    fake_data = generate_data()
    logger.info("Creating psql writer.")
    psql_writer = PSQLWriter(pg_conn)
    data_generator = FakeDataGenerator(fake_data, batch_size)
    for table, data_class in TABLES.items():
        logger.info(f"Loading table {table}")
        psql_writer.write_data(data_generator.get_generator(table), table, data_class)


if __name__ == '__main__':
    batch_size = int(os.environ.get('BATCH_SIZE', 100))
    with PostgresConnection(DSL) as pg_conn:
        load_fake_data(pg_conn, batch_size)
