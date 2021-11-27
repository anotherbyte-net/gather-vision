import sqlite3
from pathlib import Path
from sqlite3 import Connection

from django.utils.text import slugify


class SqliteClient:
    def __init__(self, path: Path):
        self._path = path

    def get_sqlite_db(self) -> Connection:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_table_names(self, conn: Connection):
        sql = (
            "SELECT name "
            "FROM sqlite_master "
            "WHERE type = 'table' AND name <> 'sqlite_sequence'"
        )
        with conn:
            c = conn.execute(sql).fetchall()
            for col_names in c:
                for col_name in col_names:
                    yield col_name

    def get_table_data(self, conn: Connection, table: str):
        name = slugify(table).replace("-", "_")
        sql = f"SELECT * from {name}"
        with conn:
            cur = conn.cursor()
            cur.execute(sql)
            for row in cur:
                yield row
