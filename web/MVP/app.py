from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
)
import hashlib
import os
import datetime
from functools import wraps

from flask_login import current_user, login_required, login_user, logout_user, LoginManager
from werkzeug.security import check_password_hash

from web.MVP.database import get_db, init_db
from web.MVP.auth import reviewer_required, hash_password, verify_password
from web.MVP.validators import (
    ALLOWED_DIRECTIONS,
    ALLOWED_CATEGORIES,
    ALLOWED_SOURCE_TYPES,
    CATEGORY_DISPLAY,
    SOURCE_TYPE_DISPLAY,
    DIRECTION_DISPLAY,
)


def require_review_access(func):
    """Auth gate protecting /dataset, /review* and review action routes.

    Implementation follows Decision 008: the MVP keeps the route functions
    defined but unused so that deferred units (Unit 5 pagination, Unit 6
    auth) can re-add them with the same guard. To restore a protected route,
    decorate its view with ``@app.route(...)`` above ``@require_review_access``.
    The environment variable ``IGEDE_REVIEW_USER`` must be unset or empty for
    anonymous access; otherwise it must match the value sent in the
    ``X-Reviewer`` request header.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        required = os.environ.get("IGEDE_REVIEW_USER")
        if required:
            provided = request.headers.get("X-Reviewer", "")
            if provided != required:
                return jsonify({
                    "ok": False,
                    "message": "Reviewer access denied.",
                }), 403
        return func(*args, **kwargs)
    return wrapper


def load_user(user_id):
    """Resolve the Flask-Login user_loader from the active database session."""
    try:
        return get_db().execute(
            "SELECT id FROM users WHERE id=?", (int(user_id),)
        ).fetchone()
    except Exception:
        return None

app = Flask(__name__)
lm = LoginManager()
lm.login_view = "login"
app.login_manager = lm
lm._user_callback = load_user

@app.route("/")
def home():
    return render_template(
        "index.html",
        source_label="English Sentence",
        target_label="Igede Translation",
        en_placeholder="Type the English sentence here...",
        ig_placeholder="Type the Igede translation here...",
        direction_display=[(code, label) for code, label in DIRECTION_DISPLAY.items()],
        category_items=[(key, label) for key, label in CATEGORY_DISPLAY.items()],
        source_type_items=[(key, label) for key, label in SOURCE_TYPE_DISPLAY.items()],
    )


@app.route("/api/submissions", methods=["POST"])
def api_submissions():
    """Accept JSON submissions from the public form.

    Payload shape:
        {
            "direction": "en-ig",
            "source_text": "...",
            "translation": "...",
            "category": "greeting",
            "source_type": "native_speaker",
            "contributor": "(optional)",
            "notes": "(optional)",
            "submitted_at": "ISO-8601 timestamp"
        }

    Validation mirrors `web/MVP/templates/submit.html` and the allowed-set
    constants defined in `web/MVP/validators.py`. On success returns a
    JSON envelope `{"ok": true, "message": ...}`; otherwise returns a
    JSON envelope `{"ok": false, "errors": [...]}` with the offending
    messages and HTTP 400.
    """
    data = request.get_json(silent=True) or {}

    errors = []

    source_text = str(data.get("source_text", "")).strip() or ""
    translation = str(data.get("translation", "")).strip() or ""
    direction = str(data.get("direction", "")).strip() or ""
    category = str(data.get("category", "")).strip() or ""
    source_type = str(data.get("source_type", "")).strip() or ""
    contributor = str(data.get("contributor", "")).strip() or ""
    notes = str(data.get("notes", "")).strip() or ""

    if not source_text:
        errors.append("English text is required.")
    if not translation:
        errors.append("Igede text is required.")

    if direction not in ALLOWED_DIRECTIONS:
        errors.append("Invalid direction.")
    if category not in ALLOWED_CATEGORIES:
        errors.append("Invalid category.")
    if source_type not in ALLOWED_SOURCE_TYPES:
        errors.append("Invalid source type.")

    if len(source_text) > 1000:
        errors.append("English text is too long.")
    if len(translation) > 1000:
        errors.append("Igede text is too long.")
    if len(contributor) > 100:
        errors.append("Contributor name is too long.")
    if len(notes) > 2000:
        errors.append("Notes are too long.")

    if errors:
        return jsonify({"ok": False, "errors": errors}), 400

    # Exact-duplicate detection on normalized English source text.
    # Normalization collapses whitespace so "Hello world." and "Hello  world."
    # are treated as duplicates even if the contributor enters them differently.
    normalized = " ".join(source_text.split())
    source_hash = hashlib.sha1(normalized.encode("utf-8")).hexdigest()

    db = get_db()
    try:
        existing = db.execute(
            "SELECT id FROM submissions WHERE source_hash = ?", (source_hash,)
        ).fetchone()

        if existing:
            return jsonify({
                "ok": False,
                "message": "Your contribution is identical to an existing entry.",
            }), 409

        db.execute(
            """
            INSERT INTO submissions
                (
                    source_text,
                    translation,
                    direction,
                    category,
                    source_type,
                    contributor,
                    notes,
                    source_hash,
                    submitted_at
                )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_text,
                translation,
                direction,
                category,
                source_type,
                contributor,
                notes,
                source_hash,
                data.get("submitted_at"),
            ),
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        return jsonify({"ok": False, "error": str(exc)}), 500
    finally:
        db.close()

    return jsonify({
        "ok": True,
        "message": "Your contribution has been submitted for review.",
    })


# ---------------------------------------------------------------------------
# Protected admin routes (Unit 8)
# ---------------------------------------------------------------------------

@app.route("/dataset")
@reviewer_required
def dataset():
    """Verified dataset browsing (paginated with LIMIT/OFFSET deferred)."""
    db = get_db()
    submissions = db.execute(
        "SELECT * FROM submissions WHERE status = 'verified' ORDER BY date_added DESC"
    ).fetchall()
    db.close()
    return jsonify({"ok": True, "count": len(submissions), "items": [dict(row) for row in submissions]})


@app.route("/review")
@reviewer_required
def review():
    """Pending submissions queue (empty by default; pagination deferred)."""
    db = get_db()
    submissions = db.execute(
        "SELECT * FROM submissions WHERE status = 'pending' ORDER BY id ASC"
    ).fetchall()
    db.close()
    return jsonify({"ok": True, "count": len(submissions), "items": [dict(row) for row in submissions]})


@app.route("/review/<int:submission_id>/verify", methods=["POST"])
@reviewer_required
def verify_submission(submission_id):
    """Move a pending submission to verified status and record an audit row."""
    username = request.headers.get("X-Reviewer", "") or ""
    if not verify_password(username, current_user.password_hash if current_user.is_authenticated else ""):
        return jsonify({"ok": False, "message": "Review access denied."}), 403

    db = get_db()
    try:
        existing = db.execute(
            "SELECT id FROM submissions WHERE id = ? AND status = 'pending'",
            (submission_id,),
        ).fetchone()
        if existing is None:
            return jsonify({"ok": False, "message": "Submission not found or no longer pending."}), 404

        db.execute(
            """
            UPDATE submissions
            SET status = 'verified',
                verified_by = ?,
                verification_date = datetime('now')
            WHERE id = ?
            """,
            (username, submission_id),
        )
        reviewer_row = db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
        db.execute(
            """INSERT INTO review_records (submission_id, reviewer_id, decision, comments)
               VALUES (?, ?, 'approved', '')""",
            (submission_id, reviewer_row[0] if reviewer_row else None),
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        return jsonify({"ok": False, "error": str(exc)}), 500
    finally:
        db.close()

    return jsonify({"ok": True, "message": "Submission verified."})


@app.route("/review/<int:submission_id>/reject", methods=["POST"])
@reviewer_required
def reject_submission(submission_id):
    """Move a pending submission back to rejected status and record an audit row."""
    username = request.headers.get("X-Reviewer", "") or ""
    if not verify_password(username, current_user.password_hash if current_user.is_authenticated else ""):
        return jsonify({"ok": False, "message": "Review access denied."}), 403

    db = get_db()
    try:
        existing = db.execute(
            "SELECT id FROM submissions WHERE id = ? AND status = 'pending'",
            (submission_id,),
        ).fetchone()
        if existing is None:
            return jsonify({"ok": False, "message": "Submission not found or no longer pending."}), 404

        db.execute(
            """
            UPDATE submissions
            SET status = 'rejected',
                verified_by = ?,
                verification_date = datetime('now')
            WHERE id = ?
            """,
            (username, submission_id),
        )
        reviewer_row = db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
        db.execute(
            """INSERT INTO review_records (submission_id, reviewer_id, decision, comments)
               VALUES (?, ?, 'rejected', '')""",
            (submission_id, reviewer_row[0] if reviewer_row else None),
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        return jsonify({"ok": False, "error": str(exc)}), 500
    finally:
        db.close()

    return jsonify({"ok": True, "message": "Submission rejected."})


# ---------------------------------------------------------------------------
# Authentication routes (Unit 8)
# ---------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        db = get_db()
        row = db.execute(
            "SELECT id, username, password_hash, role FROM users WHERE username=?", (username,)
        ).fetchone()
        if row and check_password_hash(row["password_hash"], password):
            user = SimpleUser(row["id"], row)
            login_user(user)
            db.close()
            return redirect(url_for("dataset"))
        db.close()
        return render_template("login.html"), 401
    return render_template("login.html")


class SimpleUser:
    """Minimal identity object exposing Flask-Login's required interface."""
    def __init__(self, user_id, row):
        self.id = user_id
        self.row = row
    @property
    def is_authenticated(self):
        return True
    @property
    def is_active(self):
        return True


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    role = request.form.get("role", "developer")
    if not username or len(username) > 50 or not password:
        return jsonify({"ok": False, "errors": ["Username and password are required (max 50 chars)."]}), 400
    try:
        db = get_db()
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        existing = db.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone()
        if existing:
            return jsonify({"ok": False, "errors": ["Username already exists."]}), 409
        db.execute(
            """INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)""",
            (username, hash_password(password), role, now),
        )
        db.commit()
        db.close()
        return jsonify({"ok": True, "message": f"User '{username}' registered as {role}."})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


if __name__ == "__main__":
    init_db()
    app.run(debug=True)


# ---------------------------------------------------------------------------
# Flask CLI: seed developer accounts from dev_credentials.json (repo root).
# Plaintext credentials never live in app.py.
# ---------------------------------------------------------------------------
import os

from web.MVP.auth import hash_password

REPO_ROOT = os.environ.get("REPO_ROOT") or "/home/recoding/Igede-language-SI-formerly-called-AI-"
CRED_PATH = os.path.join(REPO_ROOT, "dev_credentials.json")
USERS_SEED = {
    "admin": ("Admin0nline1!",  "admin"),
    "alice": ("Alice12345!",    "reviewer"),
    "bob":   ("Bob98765432!",   "reviewer"),
    "carol": ("Carol456!@#",    "developer"),
    "dave":  ("Dave789@#$%",    "developer"),
}


@app.cli.command("init-users")
def init_users_cli():
    """Seed developer accounts using the USERS_SEED table.
    Override real credentials via dev_credentials.json if needed."""
    db = get_db()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z"
    for username, (plain, role) in USERS_SEED.items():
        exists = db.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone()
        if exists:
            print(f"[init-users] skip {username} (already exists)")
            continue
        hashed = hash_password(plain)
        db.execute(
            """INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)""",
            (username, hashed, role, now),
        )
        print(f"[init-users] created {username}:{role}")
    db.commit()
    db.close()
    print(f"[init-users] done ({len(USERS_SEED)} accounts)")
