"""Post-integration tests for the Igede language data collection Flask app.

Run with:  python -m pytest web/MVP/tests/test_submissions.py
"""

import json
import sqlite3
from pathlib import Path

import pytest

from web.MVP import database as dbmod
from web.MVP import app as realapp  # noqa: F401 — module-level import marker
from web.MVP.validators import (
    ALLOWED_CATEGORIES,
    ALLOWED_DIRECTIONS,
    ALLOWED_SOURCE_TYPES,
)


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Spin up the app against a fresh temporary database per test."""
    tmp = tmp_path / "igede.db"
    monkeypatch.setattr(dbmod, "DATABASE", tmp)
    repo_root = Path(__file__).resolve().parents[3]
    monkeypatch.setattr(dbmod, "SCHEMA", str(repo_root / "web" / "MVP" / "schema.sql"))
    dbmod.init_db()  # creates submissions table from corrected schema.sql
    return realapp.app.test_client()


VALID_PAYLOAD = {
    "direction": "en-ig",
    "source_text": "Hello, how are you?",
    "translation": "I am fine, thank you.",
    "category": "greeting",
    "source_type": "native_speaker",
    "submitted_at": "2026-10-29T12:30:00Z",
}


def test_submission_rejects_missing_fields(client):
    payload = {
        "direction": "en-ig",
        "source_text": "",
        "translation": "",
        "category": "greeting",
        "source_type": "native_speaker",
    }
    res = client.post("/api/submissions", json=payload)
    body = res.get_json()
    assert res.status_code == 400
    assert body["ok"] is False
    errors = body["errors"]
    # Check for both errors in any order; source and translation both missing
    assert any("English text is required." in e for e in errors)
    assert any("Igede text is required." in e for e in errors)
    assert len(errors) >= 2


def test_submission_rejects_invalid_options(client):
    payload = dict(VALID_PAYLOAD, category="bogus", source_type="nope")
    res = client.post("/api/submissions", json=payload)
    body = res.get_json()
    assert res.status_code == 400
    assert "Invalid category." in body["errors"]
    assert "Invalid source type." in body["errors"]


def test_submission_rejects_length_overruns(client):
    long_text = "x" * 1001
    payload = dict(VALID_PAYLOAD, source_text=long_text, translation=long_text)
    res = client.post("/api/submissions", json=payload)
    body = res.get_json()
    assert res.status_code == 400
    assert any("too long" in e for e in body["errors"])


def test_submission_inserts_row_on_valid_payload(client):
    res = client.post("/api/submissions", json=VALID_PAYLOAD)
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["message"]

    conn = dbmod.get_db()
    row = conn.execute(
        "SELECT source_text, translation, direction, category FROM submissions ORDER BY id DESC LIMIT 1"
    ).fetchone()
    # SQLite Row objects compare by index by default; construct as tuples via list unpacking
    expected = (
        VALID_PAYLOAD["source_text"],
        VALID_PAYLOAD["translation"],
        VALID_PAYLOAD["direction"],
        VALID_PAYLOAD["category"],
    )
    assert tuple(row) == expected
    conn.close()


def test_duplicate_submission_is_rejected(client):
    first = client.post("/api/submissions", json=VALID_PAYLOAD)
    assert first.status_code == 200
    assert first.get_json()["ok"] is True

    # Identical English text + translation must be rejected as an exact duplicate.
    second = client.post("/api/submissions", json=VALID_PAYLOAD)
    assert second.status_code == 409
    body = second.get_json()
    assert body["ok"] is False
    assert "identical" in body["message"].lower()


def test_whitespace_normalized_duplicate_is_rejected(client):
    """Variations in spacing around the source text are still caught as dup."""
    payload_a = {
        "direction": "en-ig",
        "source_text": "Hello  world.",
        "translation": "Fine." * 3,
        "category": "greeting",
        "source_type": "native_speaker",
    }
    payload_b = {
        "direction": "en-ig",
        "source_text": "Hello world.",
        "translation": "Fine." * 3,
        "category": "greeting",
        "source_type": "native_speaker",
    }
    a = client.post("/api/submissions", json=payload_a)
    assert a.status_code == 200
    b = client.post("/api/submissions", json=payload_b)
    assert b.status_code == 409


def test_allowed_sets_match_frontend_options():
    # Sanity check: validator frozensets match what the template renders
    assert isinstance(ALLOWED_DIRECTIONS, frozenset)
    assert len(ALLOWED_DIRECTIONS) >= 2
    assert ALLOWED_CATEGORIES.issuperset({"greeting", "family", "food", "proverb", "culture", "everyday"})
    assert ALLOWED_SOURCE_TYPES.issuperset({"native_speaker", "elder", "book", "personal_knowledge"})


def test_schema_contains_required_columns():
    conn = dbmod.get_db()
    cols = {c[1] for c in conn.execute("PRAGMA table_info(submissions)").fetchall()}
    for required in ("source_text", "translation", "direction", "category", "source_type", "status", "submitted_at"):
        assert required in cols, f"missing column: {required}"
    conn.close()


# ---------------------------------------------------------------------------
# Auth gate (Decision 008): protected review routes require login.
# Anonymous users are redirected to /login; logged-in reviewers can access
# regardless of whether an env-var gate is set (the decorator handles this).
# ---------------------------------------------------------------------------

def _login(client, username, password):
    return client.post(
        "/login", data={"username": username, "password": password}
    )


def test_dataset_anonymous_redirects_to_login(client, monkeypatch):
    """Anonymous user accessing a protected route gets redirected to login."""
    monkeypatch.delenv("IGEDE_REVIEW_USER", raising=False)
    res = client.get("/dataset")
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_dataset_rejects_without_reviewer_header(client, monkeypatch):
    """Logged-in reviewer without the matching header gets a privilege denial."""
    monkeypatch.setenv("IGEDE_REVIEW_USER", "alice")
    _login(client, "alice", "Alice12345!")
    res = client.get("/dataset")
    body = res.get_json()
    assert res.status_code == 403
    assert body["ok"] is False
    assert body["message"] == "Insufficient privileges."


def test_dataset_accepts_with_matching_login(client, monkeypatch):
    """Logged-in reviewer with matching session can access /dataset."""
    monkeypatch.setenv("IGEDE_REVIEW_USER", "alice")
    _login(client, "alice", "Alice12345!")
    res = client.get("/dataset")
    assert res.status_code == 200


def test_review_protected_like_dataset(client, monkeypatch):
    monkeypatch.setenv("IGEDE_REVIEW_USER", "bob")
    _login(client, "bob", "Bob98765432!")
    ok = client.get("/review")
    denied = client.post("/review/99999/verify", headers={})
    assert ok.status_code == 200
    assert denied.status_code in (403, 404)


def test_submission_endpoint_unaffected_by_gate(client, monkeypatch):
    """The public submission flow must never be blocked by the auth gate."""
    monkeypatch.setenv("IGEDE_REVIEW_USER", "alice")
    payload = dict(VALID_PAYLOAD)
    res = client.post("/api/submissions", json=payload, headers={"X-Reviewer": "carol"})
    assert res.status_code == 200
    assert res.get_json()["ok"] is True


# ---------------------------------------------------------------------------
# Dataset listing (GET /dataset) — empty vs populated states.
# Query contract matches current implementation; pagination is deferred to Unit 5.
# ---------------------------------------------------------------------------

def test_dataset_empty_when_no_verified_rows(client):
    res = client.get("/dataset")
    assert res.status_code == 200
    body = res.get_json()
    assert body["count"] == 0
    assert body["items"] == []


def test_dataset_lists_only_verified_rows(client):
    seed = client.post("/api/submissions", json={**VALID_PAYLOAD, "source_text": "A unique seed.", "translation": "Seed x."})
    assert seed.status_code == 200
    assert seed.get_json()["ok"] is True
    pending = client.get("/review")  # all submissions are pending by default
    pending_id = pending.get_json()["items"][0]["id"]
    client.post(f"/review/{pending_id}/verify", headers={"X-Reviewer": "repo"})

    res = client.get("/dataset")
    body = res.get_json()
    assert res.status_code == 200
    assert body["count"] == 1
    assert body["items"][0]["id"] == pending_id
    assert body["items"][0]["status"] == "verified"


def test_dataset_does_not_list_pending_rows(client, monkeypatch):
    monkeypatch.setenv("IGEDE_REVIEW_USER", "repo")
    import sqlite3 as _sqlite3
    from web.MVP import database as dbmod
    dbmod.get_db()  # ensure tables exist
    seed = client.post("/api/submissions", json={**VALID_PAYLOAD, "source_text": "Another unique seed.", "translation": "Seed y."})
    assert seed.status_code == 200
    inserted_id = dbmod.get_db().execute("SELECT id FROM submissions ORDER BY id DESC LIMIT 1").fetchone()[0]
    conn = dbmod.get_db()
    conn.close()

    client.post(f"/review/{inserted_id}/verify", headers={"X-Reviewer": "repo"})

    res = client.get("/dataset")
    body = res.get_json()
    ids = [item["id"] for item in body["items"]]
    assert inserted_id not in ids


# ---------------------------------------------------------------------------
# Review queue (GET /review) — empty vs populated states.
# ---------------------------------------------------------------------------

def test_review_empty_when_no_pending_rows(client):
    res = client.get("/review")
    assert res.status_code == 200
    body = res.get_json()
    assert body["count"] == 0
    assert body["items"] == []


def test_review_lists_only_pending_rows(client):
    seed = client.post("/api/submissions", json={**VALID_PAYLOAD, "source_text": "Pending-only seed.", "translation": "Seed p."})
    import sqlite3 as _sqlite3
    conn = dbmod.get_db()
    row = conn.execute("SELECT id FROM submissions ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    pending_id = row[0]

    res = client.get("/review")
    body = res.get_json()
    assert res.status_code == 200
    assert body["count"] == 1
    assert body["items"][0]["id"] == pending_id
    assert body["items"][0]["status"] == "pending"


# ---------------------------------------------------------------------------
# Verify transition (POST /review/<id>/verify).
# ---------------------------------------------------------------------------

def test_verify_moves_row_to_verified(client, monkeypatch):
    monkeypatch.setenv("IGEDE_REVIEW_USER", "bob")
    _login(client, "bob", "Bob98765432!")
    from web.MVP import database as dbmod
    # Insert one row so we know it will land in submissions.
    seed = client.post("/api/submissions", json={**VALID_PAYLOAD, "source_text": "Verify this.", "translation": "Verify t."})
    assert seed.status_code == 200
    inserted_id = dbmod.get_db().execute("SELECT id FROM submissions WHERE source_text='Verify this.' ORDER BY id DESC LIMIT 1").fetchone()[0]
    dbmod.get_db().close()

    res = client.post(f"/review/{inserted_id}/verify", headers={"X-Reviewer": "reviewer"})
    assert res.status_code == 200
    assert res.get_json()["ok"] is True

    conn = dbmod.get_db()
    after = conn.execute("SELECT status FROM submissions WHERE id=?", (inserted_id,)).fetchone()[0]
    conn.close()
    assert after == "verified"


