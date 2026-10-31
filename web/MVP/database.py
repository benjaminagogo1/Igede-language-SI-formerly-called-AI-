import os
from pathlib import Path

import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/igede"
)
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


class Database:
    """Thin wrapper so code can keep using db.execute(sql, params).fetchone().

    Placeholders can be written as ? and are converted to %s for psycopg2.
    Rows come back as dicts.
    """

    def __init__(self, conn):
        self.conn = conn

    def execute(self, sql, params=()):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql.replace("?", "%s"), params or None)
        return cur

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


def get_db():
    return Database(psycopg2.connect(DATABASE_URL))


def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn, conn.cursor() as cur:
            cur.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
    finally:
        conn.close()