"""Development seeder for Phase 3 developer accounts.

Provides six named developer logins with Werkzeug-hashed passwords so that the
full Phase 3 test suite can authenticate as any role without committing
plaintext credentials into the application tree.

Run:  python ../seed_users.py
"""
import os
from datetime import datetime

from web.MVP.auth import hash_password
from web.MVP.database import get_db

USERS = [
    ("admin",      "Admin0nline1!", "admin"),
    ("alice",      "Alice12345!",  "reviewer"),
    ("bob",        "Bob98765432!", "reviewer"),
    ("carol",      "Carol456!@#", "developer"),
    ("dave",       "Dave789@#$%", "developer"),
    ("eve",        "Eve998!@@@", "developer"),
    ("frank",      "Frank777%^&", "developer"),
]


def main():
    db = get_db()
    now = datetime.utcnow().isoformat() + "Z"
    for username, plain, role in USERS:
        db.execute(
            """INSERT OR IGNORE INTO users (username, password_hash, role, created_at)
               VALUES (?, ?, ?, ?)""",
            (username, hash_password(plain), role, now),
        )
    db.commit()
    db.close()
    print(f"Seeded {len(USERS)} developer accounts into igede.db")


if __name__ == "__main__":
    main()
