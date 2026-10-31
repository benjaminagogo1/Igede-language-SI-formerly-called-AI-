import csv
import datetime
import hashlib
import io
import json
import os
import uuid
import zipfile
from functools import wraps
import re
import psycopg2


import click
from flask import (
    Flask,
    Response,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)


from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from web.MVP.database import get_db, init_db
from web.MVP.validators import (
    ALLOWED_DIRECTIONS,
    ALLOWED_CATEGORIES,
    ALLOWED_SOURCE_TYPES,
    CATEGORY_DISPLAY,
    SOURCE_TYPE_DISPLAY,
    DIRECTION_DISPLAY,
)

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "change-me-before-deploying"),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16 MB per request
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

UPLOAD_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
MEDIA_TYPES = ("text", "audio", "image")
ALLOWED_EXT = {
    "audio": {"mp3", "wav", "ogg", "m4a", "webm", "aac", "mp4"},
    "image": {"jpg", "jpeg", "png", "webp", "gif"},
}
STAFF = ("admin", "reviewer", "developer")
PER_PAGE = 12
EXPORT_COLS = [
    "id", "media_type", "source_text", "translation", "direction", "category",
    "source_type", "contributor", "status", "file_path", "verified_by",
    "verification_date", "created_at", "license", "consent_version",
    "consent_at", "contributor_token", "speaker_dialect",
    "speaker_age_range", "speaker_gender",
]

# Consent wording that the checkbox on the home page shows. If you ever change
# that wording, bump CONSENT_VERSION (e.g. "cc0-v2") so each row records which
# text the contributor agreed to.
#   cc0-v1: "I agree my contribution can be used for language research and
#            AI training, and I release it to the public domain under CC0 1.0."
CONSENT_VERSION = "cc0-v1"
LICENSE_ID = "CC0-1.0"

AGE_RANGES = ("Under 18", "18-25", "26-35", "36-50", "51+")
GENDERS = ("Female", "Male", "Other")

COOKIE_NAME = "igede_cid"                   # anonymous contributor token
COOKIE_MAX_AGE = 60 * 60 * 24 * 365 * 2     # 2 years
TOKEN_RE = re.compile(r"^[0-9a-f]{32}$")


def _norm(s):
    """Normalize text for duplicate detection (whitespace + case)."""
    return " ".join(s.split()).casefold()
# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
login_manager = LoginManager(app)
login_manager.login_view = "login"  # type: ignore[assignment]


class User(UserMixin):
    def __init__(self, row):
        self.id = row["id"]
        self.username = row["username"]
        self.role = row["role"]


@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    try:
        row = db.execute(
            "SELECT id, username, role FROM users WHERE id=?", (int(user_id),)
        ).fetchone()
    except Exception:
        return None
    finally:
        db.close()
    return User(row) if row else None


def roles_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return fn(*args, **kwargs)
        return login_required(wrapper)
    return deco


@app.context_processor
def inject_labels():
    return dict(
        dir_labels=DIRECTION_DISPLAY,
        cat_labels=CATEGORY_DISPLAY,
        src_labels=SOURCE_TYPE_DISPLAY,
    )




def users_exist():
    db = get_db()
    try:
        return db.execute("SELECT 1 FROM users LIMIT 1").fetchone() is not None
    except Exception:
        return False
    finally:
        db.close()


@app.route("/setup", methods=["GET", "POST"])
def setup():
    """First-run page: creates the first admin. Locks once any user exists."""
    init_db()  # makes sure the tables exist
    if users_exist():
        return redirect(url_for("login"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        if not username or len(username) > 50:
            error = "Enter a username (max 50 characters)."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."
        elif password != confirm:
            error = "Passwords do not match."
        else:
            db = get_db()
            try:
                db.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            finally:
                db.close()
            return redirect(url_for("login"))
    return render_template("setup.html", error=error), (400 if error else 200)







@app.template_filter("timeago")
def timeago(dt):
    if not dt:
        return ""
    secs = int((datetime.datetime.now(datetime.timezone.utc) - dt).total_seconds())
    if secs < 60:
        return "just now"
    if secs < 3600:
        return f"{secs // 60}m ago"
    if secs < 86400:
        return f"{secs // 3600}h ago"
    return f"{secs // 86400}d ago"


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------
def latest_samples():
    """Newest approved item of each type, for the home page previews."""
    samples = {k: None for k in MEDIA_TYPES}
    db = get_db()
    try:
        for kind in MEDIA_TYPES:
            samples[kind] = db.execute(
                "SELECT * FROM submissions "
                "WHERE status = 'approved' AND media_type = ? "
                "ORDER BY created_at DESC, id DESC LIMIT 1",
                (kind,),
            ).fetchone()
    except Exception:
        pass
    finally:
        db.close()
    return samples


@app.route("/")
def home():
    return render_template(
        "index.html",
        active="home",
        samples=latest_samples(),
        source_label="English Sentence",
        target_label="Igede Translation",
        en_placeholder="Type the English sentence here...",
        ig_placeholder="Type the Igede translation here...",
        direction_display=list(DIRECTION_DISPLAY.items()),
        category_items=list(CATEGORY_DISPLAY.items()),
        source_type_items=list(SOURCE_TYPE_DISPLAY.items()),
    )

@app.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html", active="how")



@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"), "our2.png", mimetype="image/png"
    )


@app.route("/explore")
def explore():
    kind = request.args.get("type", "text")
    if kind not in MEDIA_TYPES:
        kind = "text"
    f = {k: request.args.get(k, "").strip() for k in ("q", "category", "direction", "source_type")}
    page = max(request.args.get("page", 1, type=int) or 1, 1)

    where = ["status = 'approved'", "media_type = ?"]
    params = [kind]
    if f["q"]:
        where.append("(source_text ILIKE ? OR translation ILIKE ?)")
        params += [f"%{f['q']}%", f"%{f['q']}%"]
    for col in ("category", "direction", "source_type"):
        if f[col]:
            where.append(f"{col} = ?")
            params.append(f[col])
    clause = " AND ".join(where)

    db = get_db()
    try:
        total = db.execute(f"SELECT COUNT(*) AS n FROM submissions WHERE {clause}", params).fetchone()["n"]
        rows = db.execute(
            f"SELECT * FROM submissions WHERE {clause} ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?",
            params + [PER_PAGE, (page - 1) * PER_PAGE],
        ).fetchall()
    finally:
        db.close()

    qs = {"type": kind, **{k: v for k, v in f.items() if v}}
    return render_template(
        "explore.html",
        active="explore",
        kind=kind,
        f=f,
        qs=qs,
        rows=rows,
        total=total,
        page=page,
        pages=max(1, -(-total // PER_PAGE)),
    )


@app.route("/media/<int:sid>")
def media(sid):
    """Serve an uploaded file. Public only once approved; staff can see all."""
    db = get_db()
    try:
        row = db.execute("SELECT file_path, status FROM submissions WHERE id=?", (sid,)).fetchone()
    finally:
        db.close()
    if not row or not row["file_path"]:
        abort(404)
    if row["status"] != "approved" and not current_user.is_authenticated:
        abort(404)
    return send_from_directory(UPLOAD_ROOT, row["file_path"])


# ---------------------------------------------------------------------------
# Submission API (text / audio / image)
# ---------------------------------------------------------------------------
@app.route("/api/submissions", methods=["POST"])
def api_submissions():
    """Accepts multipart form data (or JSON for text).

    Fields: media_type, direction, source_text, translation (optional),
    category, source_type, consent (required), file (audio/image only),
    speaker_dialect / speaker_age_range / speaker_gender (audio, optional).
    """
    data = request.get_json(silent=True) or request.form

    kind = str(data.get("media_type", "text")).strip() or "text"
    source_text = str(data.get("source_text", "")).strip()
    translation = str(data.get("translation", "")).strip()
    direction = str(data.get("direction", "")).strip()
    category = str(data.get("category", "")).strip()
    source_type = str(data.get("source_type", "")).strip()
    contributor = str(data.get("contributor", "")).strip()
    notes = str(data.get("notes", "")).strip()
    consent = str(data.get("consent", "")).strip().lower() in ("1", "true", "on", "yes")
    dialect = str(data.get("speaker_dialect", "")).strip()
    age_range = str(data.get("speaker_age_range", "")).strip()
    gender = str(data.get("speaker_gender", "")).strip()

    # Anonymous contributor token (random ID in a cookie, no account needed)
    token = request.cookies.get(COOKIE_NAME, "")
    if not TOKEN_RE.match(token):
        token = uuid.uuid4().hex

    def reply(body, status=200):
        resp = jsonify(body)
        resp.status_code = status
        if consent:  # only set the cookie once they have consented
            resp.set_cookie(
                COOKIE_NAME, token, max_age=COOKIE_MAX_AGE,
                httponly=True, samesite="Lax", secure=request.is_secure,
            )
        return resp

    errors = []
    if kind not in MEDIA_TYPES:
        errors.append("Invalid contribution type.")
    if not consent:
        errors.append("Please tick the consent box to submit.")
    if not source_text:
        errors.append("The label is required." if kind == "image" else "The sentence is required.")
    if direction not in ALLOWED_DIRECTIONS:
        errors.append("Invalid direction.")
    if category not in ALLOWED_CATEGORIES:
        errors.append("Invalid category.")
    if source_type not in ALLOWED_SOURCE_TYPES:
        errors.append("Invalid source type.")
    if len(source_text) > 1000:
        errors.append("The sentence is too long.")
    if len(translation) > 1000:
        errors.append("The translation is too long.")
    if len(contributor) > 100:
        errors.append("Contributor name is too long.")
    if len(notes) > 2000:
        errors.append("Notes are too long.")

    if kind == "audio":
        if len(dialect) > 100:
            errors.append("Dialect / village is too long.")
        if age_range and age_range not in AGE_RANGES:
            errors.append("Invalid age range.")
        if gender and gender not in GENDERS:
            errors.append("Invalid gender option.")
    else:
        dialect = age_range = gender = ""

    upload = None
    payload = b""
    ext = ""
    original = None
    mime = None
    if kind in ("audio", "image"):
        upload = request.files.get("file")
        if not upload or not upload.filename:
            errors.append("Please attach or record a file.")
        else:
            filename = upload.filename  # plain str from here on
            original = secure_filename(filename)
            mime = upload.mimetype
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            if ext not in ALLOWED_EXT[kind]:
                errors.append("Unsupported file type: " + ", ".join(sorted(ALLOWED_EXT[kind])) + " only.")
            else:
                payload = upload.read()
                if not payload:
                    errors.append("The uploaded file is empty.")

    if errors:
        return reply({"ok": False, "errors": errors}, 400)

    # Duplicate detection.
    # Text: direction + sentence + translation, so the same sentence can have
    # several different translations, and only exact repeats are blocked.
    # Audio/image: hash of the file bytes, so many voices per prompt are fine.
    if kind == "text":
        key = f"text:{direction}\n{_norm(source_text)}\n{_norm(translation)}"
        source_hash = hashlib.sha1(key.encode("utf-8")).hexdigest()
        dup_msg = ("This exact sentence and translation already exist. "
                   "Try a different translation, or submit another sentence.")
    else:
        source_hash = hashlib.sha1((kind + ":").encode() + payload).hexdigest()
        dup_msg = "This exact file was already submitted."

    db = get_db()
    saved_path = None
    try:
        if db.execute("SELECT id FROM submissions WHERE source_hash = ?", (source_hash,)).fetchone():
            return reply({"ok": False, "message": dup_msg, "errors": [dup_msg]}, 409)

        file_path = None
        if kind in ("audio", "image"):
            folder = os.path.join(UPLOAD_ROOT, kind)
            os.makedirs(folder, exist_ok=True)
            name = f"{uuid.uuid4().hex}.{ext}"
            saved_path = os.path.join(folder, name)
            with open(saved_path, "wb") as fh:
                fh.write(payload)
            file_path = f"{kind}/{name}"

        db.execute(
            """
            INSERT INTO submissions
                (media_type, source_text, translation, direction, category,
                 source_type, contributor, notes, file_path, original_filename,
                 mime_type, source_hash, license, consent_version, consent_at,
                 contributor_token, speaker_dialect, speaker_age_range,
                 speaker_gender)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, now(), ?, ?, ?, ?)
            """,
            (kind, source_text, translation, direction, category, source_type,
             contributor, notes, file_path, original, mime, source_hash,
             LICENSE_ID, CONSENT_VERSION, token,
             dialect or None, age_range or None, gender or None),
        )
        db.commit()
    except psycopg2.IntegrityError:
        # Two identical submissions arrived at the same moment
        db.rollback()
        if saved_path and os.path.exists(saved_path):
            os.remove(saved_path)
        return reply({"ok": False, "message": dup_msg, "errors": [dup_msg]}, 409)
    except Exception as exc:
        db.rollback()
        if saved_path and os.path.exists(saved_path):
            os.remove(saved_path)
        return reply({"ok": False, "errors": ["Server error: " + str(exc)]}, 500)
    finally:
        db.close()

    return reply({"ok": True, "message": "Your contribution has been submitted for review."})
# ---------------------------------------------------------------------------
# Login / logout
# ---------------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if not users_exist():
        return redirect(url_for("setup"))
    if current_user.is_authenticated:
        return redirect(url_for("admin_overview"))
    # ... the rest stays exactly as it was
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        try:
            row = db.execute(
                "SELECT id, username, password_hash, role FROM users WHERE username=?",
                (username,),
            ).fetchone()
        finally:
            db.close()
        if row and check_password_hash(row["password_hash"], password):
            login_user(User(row))
            nxt = request.args.get("next", "")
            if not nxt.startswith("/") or nxt.startswith("//"):
                nxt = url_for("admin_overview")
            return redirect(nxt)
        error = "Invalid username or password."
    return render_template("login.html", error=error), (401 if error else 200)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))



@app.route("/admin/file/<int:sid>")
@roles_required(*STAFF)
def admin_file(sid):
    """Download the original uploaded audio/image file for one submission."""
    db = get_db()
    try:
        row = db.execute(
            "SELECT file_path, original_filename FROM submissions WHERE id=?", (sid,)
        ).fetchone()
    finally:
        db.close()
    if not row or not row["file_path"]:
        abort(404)
    return send_from_directory(
        UPLOAD_ROOT,
        row["file_path"],
        as_attachment=True,
        download_name=row["original_filename"] or os.path.basename(row["file_path"]),
    )






# ---------------------------------------------------------------------------
# Admin dashboard
# ---------------------------------------------------------------------------
@app.route("/admin")
@roles_required(*STAFF)
def admin_overview():
    db = get_db()
    try:
        stats = db.execute(
            """
            SELECT COUNT(*) AS total,
                   COUNT(*) FILTER (WHERE status = 'pending')  AS pending,
                   COUNT(*) FILTER (WHERE status = 'approved') AS approved,
                   COUNT(*) FILTER (WHERE status = 'rejected') AS rejected
            FROM submissions
            """
        ).fetchone()
        rows = db.execute(
            "SELECT * FROM submissions ORDER BY created_at DESC, id DESC LIMIT 8"
        ).fetchall()
    finally:
        db.close()
    return render_template("admin.html", view="overview", title="Dashboard Overview", stats=stats, rows=rows)


@app.route("/admin/data/<kind>")
@roles_required(*STAFF)
def admin_data(kind):
    if kind not in ("all",) + MEDIA_TYPES:
        abort(404)
    status = request.args.get("status", "")
    where, params = [], []
    if kind != "all":
        where.append("media_type = ?")
        params.append(kind)
    if status in ("pending", "approved", "rejected"):
        where.append("status = ?")
        params.append(status)
    sql = "SELECT * FROM submissions"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY created_at DESC, id DESC LIMIT 200"
    db = get_db()
    try:
        rows = db.execute(sql, params).fetchall()
    finally:
        db.close()
    titles = {"text": "Text Data", "audio": "Audio Data", "image": "Image Data", "all": "All Submissions"}
    return render_template("admin.html", view=kind, title=titles[kind], rows=rows, status=status)


@app.route("/admin/review")
@roles_required(*STAFF)
def admin_review():
    flt = {
        "type": request.args.get("type", ""),
        "category": request.args.get("category", ""),
        "token": request.args.get("token", ""),
    }
    where, params = ["status = 'pending'"], []

    if flt["type"] in MEDIA_TYPES:
        where.append("media_type = ?")
        params.append(flt["type"])
    else:
        flt["type"] = ""

    if flt["category"] in ALLOWED_CATEGORIES:
        where.append("category = ?")
        params.append(flt["category"])
    else:
        flt["category"] = ""

    if TOKEN_RE.match(flt["token"]):
        where.append("contributor_token = ?")
        params.append(flt["token"])
    else:
        flt["token"] = ""

    db = get_db()
    try:
        rows = db.execute(
            "SELECT * FROM submissions WHERE " + " AND ".join(where)
            + " ORDER BY created_at ASC LIMIT 200",
            params,
        ).fetchall()
    finally:
        db.close()
    return render_template("admin.html", view="review", title="Review Queue", rows=rows, flt=flt)


@app.route("/admin/review/bulk", methods=["POST"])
@roles_required("admin", "reviewer")
def admin_review_bulk():
    decision = request.form.get("decision", "")
    if decision not in ("approve", "reject"):
        abort(400)
    ids = [int(v) for v in request.form.getlist("ids") if v.isdigit()][:500]
    back = request.referrer or url_for("admin_review")
    if not ids:
        flash("Select at least one item first.", "error")
        return redirect(back)

    status = "approved" if decision == "approve" else "rejected"
    db = get_db()
    try:
        cur = db.execute(
            "UPDATE submissions SET status = ?, verified_by = ?, verification_date = now() "
            "WHERE id = ANY(?) AND status = 'pending' RETURNING id",
            (status, current_user.username, ids),
        )
        done = [r["id"] for r in cur.fetchall()]
        for sid in done:
            db.execute(
                "INSERT INTO review_records (submission_id, reviewer_id, decision, comments) "
                "VALUES (?, ?, ?, '')",
                (sid, int(current_user.id), status),
            )
        db.commit()
        flash(f"{len(done)} item(s) {status}.", "ok")
    except Exception as exc:
        db.rollback()
        flash("Error: " + str(exc), "error")
    finally:
        db.close()
    return redirect(back)

@app.route("/admin/review/<int:sid>/<decision>", methods=["POST"])
@roles_required("admin", "reviewer")
def admin_review_action(sid, decision):
    if decision not in ("approve", "reject"):
        abort(404)
    status = "approved" if decision == "approve" else "rejected"
    db = get_db()
    try:
        if not db.execute(
            "SELECT id FROM submissions WHERE id = ? AND status = 'pending'", (sid,)
        ).fetchone():
            flash("Submission not found or no longer pending.", "error")
        else:
            db.execute(
                "UPDATE submissions SET status = ?, verified_by = ?, verification_date = now() WHERE id = ?",
                (status, current_user.username, sid),
            )
            db.execute(
                "INSERT INTO review_records (submission_id, reviewer_id, decision, comments) VALUES (?, ?, ?, ?)",
                (sid, int(current_user.id), status, request.form.get("comments", "")),
            )
            db.commit()
            flash(f"Submission #{sid} {status}.", "ok")
    except Exception as exc:
        db.rollback()
        flash("Error: " + str(exc), "error")
    finally:
        db.close()
    return redirect(request.referrer or url_for("admin_review"))


@app.route("/admin/downloads")
@roles_required(*STAFF)
def admin_downloads():
    return render_template("admin.html", view="downloads", title="Downloads")


@app.route("/admin/export/<kind>/<fmt>")
@roles_required(*STAFF)
def admin_export(kind, fmt):
    if kind not in ("all",) + MEDIA_TYPES or fmt not in ("csv", "json", "zip"):
        abort(404)
    if fmt == "zip" and kind not in ("audio", "image"):
        abort(404)

    status = "all" if request.args.get("status") == "all" else "approved"
    where, params = [], []
    if kind != "all":
        where.append("media_type = ?")
        params.append(kind)
    if status == "approved":
        where.append("status = 'approved'")
        where.append("consent_at IS NOT NULL")  # only export data with recorded consent
    sql = "SELECT * FROM submissions"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY id"

    db = get_db()
    try:
        rows = db.execute(sql, params).fetchall()
    finally:
        db.close()

    base = f"igede_{kind}_{status}_{datetime.date.today().isoformat()}"

    def headers(ext):
        return {"Content-Disposition": f"attachment; filename={base}.{ext}"}

    if fmt == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(EXPORT_COLS)
        for r in rows:
            writer.writerow([r[c] for c in EXPORT_COLS])
        return Response("\ufeff" + buf.getvalue(), mimetype="text/csv", headers=headers("csv"))

    if fmt == "json":
        body = json.dumps([{c: r[c] for c in EXPORT_COLS} for r in rows],
                          default=str, ensure_ascii=False, indent=2)
        return Response(body, mimetype="application/json", headers=headers("json"))

    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as z:
        for r in rows:
            if r["file_path"]:
                full = os.path.join(UPLOAD_ROOT, r["file_path"])
                if os.path.isfile(full):
                    z.write(full, f"{r['id']}_{r['original_filename'] or os.path.basename(full)}")
    return Response(mem.getvalue(), mimetype="application/zip", headers=headers("zip"))


@app.route("/admin/database")
@roles_required(*STAFF)
def admin_database():
    db = get_db()
    try:
        info = {
            "size": db.execute(
                "SELECT pg_size_pretty(pg_database_size(current_database())) AS s"
            ).fetchone()["s"],
            "users": db.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"],
            "submissions": db.execute("SELECT COUNT(*) AS n FROM submissions").fetchone()["n"],
            "reviews": db.execute("SELECT COUNT(*) AS n FROM review_records").fetchone()["n"],
            "by_type": db.execute(
                "SELECT media_type, COUNT(*) AS n FROM submissions GROUP BY media_type ORDER BY media_type"
            ).fetchall(),
        }
    finally:
        db.close()
    return render_template("admin.html", view="database", title="Database", info=info)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
@app.cli.command("init-db")
def init_db_cli():
    """Create all tables."""
    init_db()
    click.echo("Database tables are ready.")


@app.cli.command("create-user")
@click.argument("username")
@click.option("--role", type=click.Choice(["admin", "reviewer", "developer"]), default="developer")
@click.password_option()
def create_user_cli(username, role, password):
    """Create a user, or reset the password/role if the username exists."""
    db = get_db()
    try:
        db.execute(
            """
            INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)
            ON CONFLICT (username) DO UPDATE
            SET password_hash = EXCLUDED.password_hash, role = EXCLUDED.role
            """,
            (username, generate_password_hash(password), role),
        )
        db.commit()
    finally:
        db.close()
    click.echo(f"User '{username}' saved with role '{role}'.")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)