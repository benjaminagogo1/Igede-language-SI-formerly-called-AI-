# Observation Report: Gaps, Loopholes, and Issues

> Date: 2026-10-29
> Prepared from a full inspection of all 26 files in the repository.

This document compiles every gap, inconsistency, and known limitation identified during the inspection of this project. Severity ratings use HIGH, MEDIUM, and LOW. The most actionable findings are at the top for prioritisation.

---

## Summary Table

| # | Severity | Category | Issue |
|---|---|---|---|
| 1 | **HIGH** | Schema mismatch | Two competing DB designs, no reconciliation |
| 2 | LOW | Typos | `varified_by` typo in schema |
| 3 | MEDIUM | Missing init | `init_db()` not called on startup |
| 4 | None | Template vars | All variables are consistent across routes |
| 5 | **MEDIUM** | Missing tests | Zero test files despite README promise |
| 6 | LOW | UX | No root-level convenience command |
| 7 | **HIGH** | Security | No auth on protected review/verify routes |
| 8 | **HIGH** | Data quality | No duplicate detection |
| 9 | MEDIUM | Architecture | No reviewer role tracking / audit trail |
| 10 | LOW | Maintainability | Hardcoded category/source_type lists duplicated across HTML+Python |
| 11 | MEDIUM | Error handling | Unhandled DB exceptions during insert |
| 12 | **HIGH** | Performance | No pagination on large datasets |
| 13 | LOW | Tech debt | No JS despite static dir existing |
| 14 | LOW | Docs | No canonical project name |
| 15 | MEDIUM | Architecture | No API layer despite documented plan |
| 16 | LOW | Security | No CSRF protection noted |

---

## 1. High — Schema Mismatch (CRITICAL)

Two competing database designs coexist with no resolution. Neither schema was updated to address the other.

### PostgreSQL design (`database/schema.sql`)
- **Tables:** `actors`, `sentence_pairs`, `review_records`
- **Direction:** Not present — only english + igede text stored
- **Status values:** `pending`, `needs_revision`, `verified`, `approved`, `rejected`
- **Verification history:** Separate `review_records` table linked via foreign keys, recording reviewer ID, decision, comments, timestamp
- **Target DB:** PostgreSQL
- **Relationships:** Enforced via PRIMARY KEY / FOREIGN KEY constraints

### SQLite design (`web/MVP/schema.sql`)
- **Tables:** Single table `submissions`
- **Direction:** Present as column
- **Status values:** Only `pending` default — no alternative statuses allowed
- **Verification history:** Verification stored on one row using `varified_by` and `verification_date` columns; no per-reviewer audit trail
- **Foreign keys:** None enforced
- **Target DB:** SQLite (file `igede.db`)

### Impact
The web app uses the simpler SQLite schema, while all documentation describes a richer PostgreSQL design. The web app does not implement the review-history tracking described in the docs. Review decisions cannot be attributed to individual reviewers or tracked as history records.

### Recommended action
Either consolidate into one schema, or add a `review_records` equivalent to the SQLite schema with a separate status tracking mechanism that supports the full decision workflow.

---

## 2. Low — Typo: `varified_by` Column Name

In `web/MVP/schema.sql`:
```sql
varified_by TEXT,
verification_date TEXT,
```
The spelling "varified" is inconsistent with the rest of the schema and with `docs/database-schema.md` which correctly uses `verified_by`. No code references it by the typo'd name, so it does not currently break anything, but it creates confusion for anyone reading raw SQL and risks being miscopied again.

### Recommended action
Rename `varified_by` → `verified_by`.

---

## 3. Medium — Missing `init_db()` Call on App Startup

`app.py` defines routes but never calls `init_db()` from `database.py`. The `init_db()` function runs the schema script to create tables if they don't exist. On a fresh checkout where `igede.db` has never been created, the first HTTP request would fail because the `submissions` table does not exist. The table may already exist from prior runs, making this intermittent failure.

### Recommended action
Call `from web.MVP.database import init_db; init_db()` at module load time, before the first route executes. Or document the prerequisite command explicitly in READMEs.

---

## 4. None — Template Variables Consistent

All template variables referenced by routes match what the templates actually render:
- `dataset.html` receives and displays the `submissions` list correctly
- `review.html` receives and displays the `submissions` list correctly
- `submit.html` receives and displays both `error` and `success`

No gap found.

---

## 5. Medium — No Tests Written

`tests/README.md` promises coverage for: "Website functionality, Form validation, Database operations, API endpoints, Chatbot responses, Translation quality." There are zero test files, no `conftest.py`, no pytest configuration, and no CI integration. The testing infrastructure was planned but never built.

### Recommended action
Write at minimum smoke tests covering: form submission flow, validation rejection paths, dataset listing when empty vs populated, verify and reject transitions, and database connection errors.

---

## 6. Low — No Root-Level Convenience Command

Setup instructions say to run:
```bash
cd web/MVP && python database.py
```
and then start the app from within that directory. There is no single command at the repository root (e.g., `flask --app web.MVP run`) that bundles the full setup, seed, and launch sequence. Users must remember three steps manually.

### Recommended action
Add a root-level `run.sh` or document a `make dev` target.

---

## 7. High — No Authentication on Protected Routes

`web/MVP/README.md` explicitly states:
> "The review interface does not yet have production-ready authentication and authorization."

`docs/database-schema.md` states:
> "Only authorized reviewers and administrators should be allowed to make verification and approval decisions."

Yet `app.py` has zero auth checks. Any anonymous user can view pending submissions, verify or reject them, and access the verified dataset. This is a documented gap that remains unaddressed and represents a real security risk if the app were deployed publicly.

### Recommended action
Even an MVP auth guard — e.g., requiring a simple session token or environment variable check before allowing access to `/review*` and `/dataset` — would close this gap immediately.

---

## 8. High — No Duplicate Detection

`docs/dataset-guidelines.md` states that review should look for duplicate entries, but the submission form and backend have no deduplication logic whatsoever. Submissions submitted multiple times will all enter the database as separate rows, inflating the dataset without any way for reviewers to flag duplicates.

### Recommended action
At minimum, compute a hash or slug of the English text (and optionally the Igede text) before inserting, and check existence against the existing rows. A simple index on `lower(english)` or `igede` would catch exact duplicates. Near-duplicate detection is future work.

---

## 9. Medium — No Reviewer Role Tracking

The PostgreSQL schema tracks `reviewer_id` (foreign key to `actors`), but the SQLite schema stores only `varified_by`/`verification_date` on the submission row. There is no way to see who reviewed what, how many reviews each person did, build audit trails, or enforce that only designated reviewers touch the submission workflow. The web app has no user accounts, no login system, and no per-user identifiers.

### Recommended action
Extend the SQLite schema to include at least a `reviewed_by` column on submissions (or better, duplicate the review-history pattern), and add a simple login gate to `/review` so anyone accessing the page at least needs to reach it through some identifying path.

---

## 10. Low — Hardcoded Lists Duplicated Across HTML and Python

In `submit.html`, the `<select>` options are hardcoded:
```html
<option value="english_to_igede">English - Igede</option>
<option value="word">Word</option>
<option value="native_speaker">Native Speaker</option>
```

In `app.py`, the same values are hardcoded again:
```python
allowed_directions = {"english_to_igede", "igede_to_english"}
allowed_categories = {"word", "phrase", "sentence", "proverb", "expression"}
allowed_source_types = {"native_speaker", "dictionary", "book", "community", "other"}
```

If new categories need adding, both must be edited in two places simultaneously. There is no shared constants module or enum to prevent drift between the two sources of truth.

### Recommended action
Extract these sets into a shared module (e.g., `constants.py` or `validators.py`) that both templates and Python code import from. Use Jinja2 `{% set %}` blocks or render options dynamically from a Python constant to eliminate the duplication entirely.

---

## 11. Medium — Unhandled Database Exceptions During Insert

In the POST handler (`app.py` lines 99–127), there is no try/except around the INSERT. If the database is locked, corrupted, or the connection drops mid-transaction, the exception propagates as an unhandled traceback to the user with no friendly message. This contrasts with the verify endpoint which does handle failures gracefully with rollback.

### Recommended action
Wrap the INSERT in try/except and re-raise as a Flask abort() or return a formatted error message to the user.

---

## 12. High — No Pagination on Dataset and Review Pages

Both `dataset.html` and `review.html` render **every** submission in a single Jinja loop with no limit, offset, or pagination. At scale (the stated target is 1,000+ verified entries and potentially hundreds of pending submissions), this will produce an enormous HTML response — thousands of `<tr>` rows — causing severe performance degradation, timeouts, and poor UX.

Neither template includes client-side filtering, sorting, or any pagination controls. The Flask endpoints (`/dataset`, `/review`) accept no pagination parameters either.

### Recommended action
- Add `LIMIT`/`OFFSET` clauses to the SQL queries and pass pagination metadata to templates
- Add page navigation (Previous / Next / Page number) to `dataset.html` and `review.html`
- Consider a search box to filter submissions client-side if server pagination proves complex

---

## 13. Low — No JavaScript Files Despite Static Directory Existing

`web/MVP/static/css/style.css` exists, but there are **no JavaScript files** anywhere in the project. All interactivity is pure server-rendered HTML forms. The absence is never explained or justified in any documentation. While this does not break anything in the current MVP scope, it leaves the static directory incomplete and makes future feature additions (modals, loading spinners, real-time validation feedback) awkward to plan around.

### Recommended action
Decide whether JS is intentionally deferred for later phases (documenting this as a deliberate tech-debt item) or whether it should be part of the baseline and simply missing from the initial commit.

---

## 14. Low — No Canonical Project Name

The repo name includes "(formerly-called-AI)" and reads "Igede Language SI" but across the entire codebase and documentation the project name appears in multiple inconsistent forms:

| Location | Name used |
|---|---|
| README | "Igede Language Project" / "Igede Language AI project" |
| README section header | "A community-driven SI project" |
| docs/project-overview.md | "Igede language AI project" |
| docs/database-schema.md | "Igede language data" |
| docs/architecture.md | "Igede Language AI project" |
| All other docs | "Igede language" (lowercase, generic) |

There is no Decision entry documenting a canonical name. Future contributors must guess from context.

### Recommended action
Add a `DECISION-00X` entry to `docs/decisions.md` naming the canonical project name and standardise all references.

---

## 15. Medium — No API Layer Despite Documented Architecture Plan

`docs/architecture.md` explicitly describes a "Backend / API" component in the main pipeline and references future API integration in the roadmap. Yet the current implementation is purely monolithic Flask — no separate API routes, no JSON responses, no REST endpoints, no API documentation, and no separation between data access logic and presentation logic.

The architecture documents a layer that was described years ago but was never built. New contributors planning features will assume an API exists, causing confusion.

### Recommended action
Decide now whether the API layer is Phase 5 content or whether some basic endpoint structure should exist in the MVP. Document the choice clearly in decisions.

---

## 16. Low — No CSRF Protection Noted

No mention of CSRF tokens in any template, any form, or any security documentation. With Flask's debug mode enabled by default (`app.run(debug=True)`), CSRF protection is less critical than in production, but the project plans eventual deployment. The lack of any CSRF awareness means the team could miss it during deployment hardening.

### Recommended action
At minimum, note CSRF as a future requirement in `docs/decisions.md` or set up Flask-WTF in a later phase. For now, acknowledge as tech debt.

---

## Per-File Reference for Findings

For traceability, each finding maps to the file(s) that raised it:

| # | Files involved |
|---|---|
| 1 | `database/schema.sql`, `web/MVP/schema.sql`, `docs/database-schema.md`, `docs/architecture.md` |
| 2 | `web/MVP/schema.sql` |
| 3 | `web/MVP/app.py`, `web/MVP/database.py` |
| 4 | `web/MVP/templates/{dataset,review}.html`, `web/MVP/app.py` |
| 5 | `tests/README.md` |
| 6 | `README.md`, `web/MVP/README.md` |
| 7 | `web/MVP/app.py`, `web/MVP/README.md`, `docs/database-schema.md` |
| 8 | `web/MVP/app.py`, `docs/dataset-guidelines.md` |
| 9 | `web/MVP/schema.sql`, `web/MVP/app.py`, `docs/database-schema.md` |
| 10 | `web/MVP/templates/submit.html`, `web/MVP/app.py` |
| 11 | `web/MVP/app.py` (POST handler section) |
| 12 | `web/MVP/app.py`, `web/MVP/templates/{dataset,review}.html` |
| 13 | `web/MVP/static/css/style.css`, all templates |
| 14 | `README.md`, all `docs/*` files |
| 15 | `docs/architecture.md`, `ai/README.md`, all roadmap docs |
| 16 | No file — observation only; plans exist in `docs/database-schema.md`, `web/MVP/README.md`, `docs/decisions.md` |
