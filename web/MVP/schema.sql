CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    english TEXT NOT NULL,
    igede TEXT NOT NULL,

    direction TEXT NOT NULL,
    category TEXT NOT NULL,
    source_type TEXT NOT NULL,

    contributor TEXT,

    status TEXT NOT NULL DEFAULT 'pending',

    varified_by TEXT,
    verification_date TEXT,

    notes TEXT,

    date_added TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);