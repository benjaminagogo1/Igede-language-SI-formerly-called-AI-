from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent

DATABASE = BASE_DIR / "igede.db"
SCHEMA = BASE_DIR  / "schema.sql"


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    return connection

def init_db():
    connection = get_db()

    with open(SCHEMA) as file:
        connection.executescript(file.read())
    
    connection.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
