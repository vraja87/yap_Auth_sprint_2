from db_params import SCHEMA

INSERT_ALL = f"INSERT INTO {SCHEMA}" + ".{} {} VALUES {} ON CONFLICT DO NOTHING;"
