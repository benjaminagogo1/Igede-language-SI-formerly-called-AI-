-- Igede Language Data Collection — PostgreSQL schema
-- Safe to run repeatedly. New columns are added with ALTER ... IF NOT EXISTS,
-- so existing databases keep their data.

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'reviewer', 'developer')),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS submissions (
    id                SERIAL PRIMARY KEY,
    media_type        VARCHAR(10) NOT NULL DEFAULT 'text'
                      CHECK (media_type IN ('text', 'audio', 'image')),
    source_text       TEXT NOT NULL DEFAULT '',
    translation       TEXT NOT NULL DEFAULT '',
    direction         TEXT NOT NULL,
    category          TEXT NOT NULL,
    source_type       TEXT NOT NULL,
    contributor       TEXT,
    notes             TEXT,
    file_path         TEXT,
    original_filename TEXT,
    mime_type         TEXT,
    status            VARCHAR(20) NOT NULL DEFAULT 'pending'
                      CHECK (status IN ('pending', 'approved', 'rejected')),
    verified_by       TEXT,
    verification_date TIMESTAMPTZ,
    source_hash       CHAR(40) NOT NULL UNIQUE,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Consent / licence, anonymous contributor token, optional speaker details
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS license           TEXT;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS consent_version   TEXT;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS consent_at        TIMESTAMPTZ;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS contributor_token VARCHAR(32);
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS speaker_dialect   TEXT;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS speaker_age_range TEXT;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS speaker_gender    TEXT;

CREATE INDEX IF NOT EXISTS idx_submissions_status_type ON submissions (status, media_type);
CREATE INDEX IF NOT EXISTS idx_submissions_created     ON submissions (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_submissions_category    ON submissions (category);
CREATE INDEX IF NOT EXISTS idx_submissions_token       ON submissions (contributor_token);

CREATE TABLE IF NOT EXISTS review_records (
    id            SERIAL PRIMARY KEY,
    submission_id INTEGER NOT NULL REFERENCES submissions (id) ON DELETE CASCADE,
    reviewer_id   INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    decision      VARCHAR(20) NOT NULL CHECK (decision IN ('approved', 'rejected', 'needs_correction')),
    comments      TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);