-- Igede Language AI Dataset
-- Initial relational database schema
-- Proposed database: PostgreSQL
-- Requires team approval before adoption.

-- BEGIN;

-- CREATE TABLE actors (
--     actor_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
--     role VARCHAR(20) NOT NULL
--         CHECK (role IN ('contributor', 'reviewer', 'admin'))
-- );

-- CREATE TABLE sentence_pairs (
--     pair_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
--     english_text TEXT NOT NULL,
--     igede_text TEXT NOT NULL,
--     category VARCHAR(100) NOT NULL,

--     verification_status VARCHAR(20) NOT NULL DEFAULT 'pending'
--         CHECK (
--             verification_status IN (
--                 'pending',
--                 'needs_revision',
--                 'verified',
--                 'approved',
--                 'rejected'
--             )
--         ),

--     submitted_by BIGINT
--         REFERENCES actors(actor_id)
--         ON DELETE SET NULL,

--     created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
--     updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

--     CHECK (LENGTH(TRIM(english_text)) > 0),
--     CHECK (LENGTH(TRIM(igede_text)) > 0),
--     CHECK (LENGTH(TRIM(category)) > 0)
-- );

-- CREATE TABLE review_records (
--     review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

--     pair_id BIGINT NOT NULL
--         REFERENCES sentence_pairs(pair_id)
--         ON DELETE RESTRICT,

--     reviewer_id BIGINT NOT NULL
--         REFERENCES actors(actor_id)
--         ON DELETE RESTRICT,

--     decision VARCHAR(20) NOT NULL
--         CHECK (
--             decision IN (
--                 'needs_revision',
--                 'verified',
--                 'approved',
--                 'rejected'
--             )
--         ),

--     comments TEXT,
--     reviewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
-- );

-- CREATE INDEX idx_sentence_pairs_status
--     ON sentence_pairs(verification_status);

-- CREATE INDEX idx_sentence_pairs_category
--     ON sentence_pairs(category);

-- CREATE INDEX idx_review_records_pair
--     ON review_records(pair_id);

-- CREATE INDEX idx_review_records_reviewer
--     ON review_records(reviewer_id);

-- COMMIT;
