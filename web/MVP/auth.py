"""Authentication: login, logout, password verification, and role checks.

Defaults comply with Decision 010: no plaintext passwords live in this module.
Developer accounts are provisioned out-of-band via ``flask init-users`` (or a
CI script). Anonymous viewers are seeded automatically.
"""
import functools
from datetime import datetime

from flask import redirect, render_template, request, url_for, jsonify
from flask_login import current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

from web.MVP.database import get_db

SEED_ANONYMOUS = [
    ("anonymous", None, "viewer"),
]


def hash_password(plain):
    """Werkzeug pbkdf2:sha256 hash (Decision 010 — never store plaintext)."""
    return generate_password_hash(plain)


def verify_password(stored, plain):
    return check_password_hash(stored, plain)


def seed_users():
    """Insert an anonymous viewer (empty password_hash column) and commit."""
    db = get_db()
    now = datetime.utcnow().isoformat() + "Z"
    for username, plain, role in SEED_ANONYMOUS:
        db.execute(
            "INSERT OR IGNORE INTO users (username, password_hash, role, created_at) VALUES (?, '', ?, ?)",
            (username, role, now),
        )
    db.commit()
    db.close()


def _check_role(allowed):
    """Decorator restricting access to the listed roles."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("login"))
            if current_user.role not in allowed:
                return jsonify({"ok": False, "message": "Insufficient privileges."}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator


admin_required = _check_role(("admin",))
reviewer_required = _check_role(("reviewer", "admin"))
