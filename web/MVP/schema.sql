-- Igede Language Data Collection — SQLite schema (MVP baseline)
--
-- Idempotent: every statement uses CREATE TABLE IF NOT EXISTS, so running
-- init_db() against an existing database adds new tables without dropping or
-- altering existing ones. Foreign keys are enforced via PRAGMA foreign_keys = ON.
--
-- Phase 3 additions (Decision 010, 012):
--   * users        — per-developer accounts with roles (admin/reviewer/developer)
--   * review_records — audit trail of every approve/reject/needs_correction decision
--
-- To apply to an existing database:  python database.py
-- (init_db() runs this file via executescript; existing data is untouched.)

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    source_text TEXT NOT NULL,
    translation TEXT NOT NULL,

    direction TEXT NOT NULL,
    category TEXT NOT NULL,
    source_type TEXT NOT NULL,

    contributor TEXT,

    status TEXT NOT NULL DEFAULT 'pending',

    verified_by TEXT,
    verification_date TEXT,

    notes TEXT,

    source_hash TEXT NOT NULL,

    submitted_at TEXT,

    date_added TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Per-developer accounts. Passwords are stored as Werkzeug/Flask-Login
-- password hashes (pbkdf2:sha256), never plaintext (Decision 010).
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,

    -- Roles: admin (full access), reviewer (approve/reject only),
    -- developer (read-only dashboard access).
    role TEXT NOT NULL CHECK (role IN ('admin', 'reviewer', 'developer')),

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Audit trail of every review decision (Decision 012).
-- One submission may have multiple review records (e.g. approved, then
-- later rejected) so decisions are never silently overwritten.
CREATE TABLE IF NOT EXISTS review_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    submission_id INTEGER NOT NULL,
    reviewer_id INTEGER NOT NULL,

    decision TEXT NOT NULL CHECK (
        decision IN ('approved', 'rejected', 'needs_correction')
    ),

    comments TEXT,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (submission_id) REFERENCES submissions (id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id)    REFERENCES users (id)       ON DELETE CASCADE
);