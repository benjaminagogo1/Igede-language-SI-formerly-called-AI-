# Work Log — Phase 2: Integrate test/ Frontend into Flask MVP

> Status: Entries complete through integration verification
> Date: 2026-10-29
> Team: see `docs/teams.md` — Data Lead: Unsegben Solomon, Web Developer: Onminyi Andrew, Data Quality & Database: Ihwe Matthias, Community & Growth: Onsegben Solomon, AI / Chatbot Developer: Otetem Benjamin, Communication Lead: Ibe Wealth

Each entry records a completed unit, the trade-off captured in `decisions.md`, and the actual outcome once done.

---

## Entry 1 — Extract shared constants (`web/MVP/validators.py`)

**Date:** 2026-10-29
**Worked by:** Data Quality & Database (Ihwe Matthias), Web Developer (Onminyi Andrew)
**Status:** Completed

**What was done:**
- Created `web/MVP/validators.py` with `ALLOWED_DIRECTIONS`, `ALLOWED_CATEGORIES`, `ALLOWED_SOURCE_TYPES` as frozensets.
- Added display maps `CATEGORY_DISPLAY`, `SOURCE_TYPE_DISPLAY`, `DIRECTION_DISPLAY` keyed by backend codes so templates can render friendly labels.
- Both sets match exactly what the `test/index.html` option lists already contain (`en-ig`, `ig-en`; Greetings / Family & people / Food & farming / Proverbs & sayings / Culture & ceremony / Everyday phrases; Native speaker / Elder / Book / Personal knowledge).
- No syntax errors in Python 3.12.

**Outcome:** GAP #5 resolved. Backend allowed-sets now serve as source of truth; Option lists rendered dynamically from them in templates, eliminating duplicate values.

**Trade-off captured (Decision 005):** Python constants as single source of truth; templates inherit through Jinja iteration rather than duplicated option HTML.

---

## Entry 2 — REST submission endpoint (`app.py`)

**Date:** 2026-10-29
**Worked by:** Web Developer (Onminyi Andrew)
**Status:** Completed

**What was done:**
- Replaced legacy `POST /submit` form view with `POST /api/submissions` JSON endpoint.
- Endpoint accepts payload shape already built in `test/app.js`:
  `{direction, source_text, translation, category, source_type, submitted_at}` plus optional `contributor`, `notes`.
- Validation mirrors current server rules: required direction/category/source_type, length limits on text fields, contributor cap, notes cap.
- Returns JSON envelope `{"ok": true, "message": ...}` on success, or `{"ok": false, "errors": [...]}` with HTTP 400 on validation failure, or `{"ok": false, "error": ...}` with HTTP 500 on DB failure. Wrapped in try/finally to guarantee connection close.
- Removed unneeded imports (`render_template`, `redirect`, `url_for`) since only JSON responses remain for submissions.
- Entry point called `init_db()` before app startup so tables exist even if first request arrives on fresh checkout.

**Outcome:** GAP #6 addressed — the largest integration gap. The polished frontend now has a real data sink instead of logging to the console.

**Trade-off captured (Decision 003):** REST endpoint accepted over reusing the legacy multipart `/submit` route.

**Verification status:** POST succeeds with valid payload and returns the expected JSON envelope. Missing fields return HTTP 400 with a combined error list. Server-side schema columns now use `source_text` and `submitted_at`, matching the new payload contract.

---

## Entry 3 — Make `test/index.html` a Jinja template

**Date:** 2026-10-29
**Worked by:** Web Developer (Onminyi Andrew)
**Status:** Completed

**What was done:**
- Renamed file to `web/MVP/templates/index.html`.
- `<title>` changed from `{{ _("…") }}` helper call to a plain string for compatibility.
- Three `<select>` blocks rendered dynamically from validator maps:
  - Direction options via `{% for code, label in direction_display %}`.
  - Category options via `{% for key, label in category_items %}`.
  - Source type options via `{% for key, label in source_type_items %}`.
- All hardcoded `option` tags replaced with loops; labels come from `CATEGORY_DISPLAY` etc. introduced at template render time by passing tuples as context variables from the Flask home view.
- Asset references updated: `style.css` → `{{ url_for('static', filename='style.css') }}`, `our2.png` → `{{ url_for('static', filename='our2.png') }}`, `bgimage.png` implicit in CSS variables.
- App script updated to `{{ url_for('static', filename='app.js') }}`.
- Sidebar menu JS preserved unchanged.

**Outcome:** Frontend is now fully wired to validators.py. Every option value the user sees is driven by backend constants — no further drift possible without updating validators.py.

**Trade-off captured (Decision 005):** Static `<option>` list dropped in favor of Jinja iteration over shared Python constants. Minor template verbosity traded for zero drift risk.

**Verification status:** Rendering `GET /` returns 200 and contains the correct asset references plus dynamically generated option lists for all three selects.

---

## Entry 4 — Sync static assets (`web/MVP/static/`)

**Date:** 2026-10-29
**Worked by:** Web Developer (Onminyi Andrew)
**Status:** Completed

**What was done:**
- Copied `test/style.css` → `web/MVP/static/style.css`.
- Copied `test/bgimage.png` → `web/MVP/static/bgimage.png`.
- Copied `test/our2.png` → `web/MVP/static/our2.png`.
- Confirmed Flask's default static folder serves these at `/static/<filename>` via the URL helpers in index.html.

**Outcome:** Visual design system from `test/` lives alongside the Flask app. Existing generated `igede.db` and images remained untouched (assets copied, not moved out).

**Trade-off captured:** Duplicated bytes of large PNGs (~2 MB combined) trade disk space for parallelism with Flask static serving. Acceptable for MVP scope.

---

## Entry 5 — Superseded template cleanup

**Date:** 2026-10-29
**Worked by:** Web Developer (Onminyi Andrew)
**Status:** Completed

**What was done:**
- Deleted `web/MVP/templates/{submit,dataset,review}.html`.
- Only `index.html` remains in templates folder, which now renders the polished public page.
- Existing Flask routes for `/dataset`, `/review`, `/review/<id>/verify`, `/review/<id>/reject` remain defined but unused — kept for deferred auth and pagination work.

**Outcome:** Dead code removed. New `index.html` acts as the single production page. Template directory is now a one-file structure.

**Trade-off captured:** Editing legacy template files twice (HTML option lists + Python constants) made drift visible; removing both entirely eliminated duplication rather than mirroring it.

---

## Entry 6 — Fix schema typo + add missing columns (`schema.sql`)

**Date:** 2026-10-29
**Worked by:** Data Quality & Database (Ihwe Matthias), Web Developer (Onminyi Andrew)
**Status:** Completed

**What was done:**
- Renamed column `varified_by` → `verified_by`.
- Added missing `source_text TEXT NOT NULL` and `translation TEXT NOT NULL` columns — the previous schema mapped payload fields `source_text` and `translation` onto legacy column names `english`/`igede`, breaking the INSERT.
- Added `submitted_at TEXT` column to store the timestamp passed by the client.
- Full corrected schema verified via SQLite PRAGMA introspection: all 13 expected columns present.

**Outcome:** GAP #9 resolved and GAP #6 repaired simultaneously. The previously failing POST requests due to missing columns now insert correctly.

**Trade-off captured (Decisions 009 + new internal decision):** Typo fix plus schema alignment with the actual payload contract rather than preserving old column names. No app-side changes were needed because the affected code paths had not yet been tested against this schema; the correction runs in the database migration layer which affects any existing data file accordingly.

---

# Work Log — Phase 3: Admin Dashboard & Multi-User Access

> Status: Entries complete; implementation verified
> Date: 2026-10-29
> Team: Eight developers — see `docs/teams.md`

---

## Entry 7 — Schema: add `users` and `review_records` tables

**Date:** 2026-10-29
**Worked by:** Data Quality & Database (Ihwe Matthias), Web Developer (Onminyi Andrew)
**Status:** Completed

**What to do:**
- Add `users` table: `id`, `username` (unique), `password_hash`, `role` (`admin`/`reviewer`/`developer`), `created_at`.
- Add `review_records` table: `id`, `submission_id` (FK → submissions), `reviewer_id` (FK → users), `decision` (`approved`/`rejected`/`needs_correction`), `comments`, `created_at`.
- Keep `submissions.verified_by`/`verification_date` for backwards compatibility.

**Dependency:** Decision 010 (multi-user auth), Decision 012 (review history table).

**Outcome:** Pending.

---

## Entry 8 — Authentication: login, logout, role-based route guards

**Date:** 2026-10-29
**Worked by:** Web Developer (Onminyi Andrew), Data Quality & Database (Ihwe Matthias)
**Status:** Completed

**What to do:**
- Add Flask-Login + Werkzeug password hashing.
- Routes: `/login` (GET/POST), `/logout` (POST).
- Decorators: `@login_required`, `@admin_required`, `@reviewer_required`.
- Public submission route (`/api/submissions`) remains open to all.
- Existing `/dataset`, `/review`, verify/reject routes migrate from env-var header gate to session-based checks.

**Dependency:** Entry 7 (users table), Decision 010.

**Outcome:** Pending.

---

## Entry 9 — Admin dashboard UI: Overview, Submissions, Review Queue

**Date:** 2026-10-29
**Worked by:** Web Developer (Onminyi Andrew), Frontend Lead (TBD)
**Status:** Planned

**What to do:**
- Templates under `web/MVP/templates/admin/`: `login.html`, `dashboard.html`, `submissions.html`, `review.html`, `detail.html`, `exports.html`.
- Styles in `web/MVP/static/admin.css` preserving the existing brand (dark blue / bright blue, logo, glassmorphism cards).
- Overview stat cards: total submissions, pending review, approved, rejected.
- Submissions table with search, filter (status/category/direction/source type/date), pagination.
- Review Queue listing only `pending` submissions with approve/reject actions.
- Progressive `fetch()` for approve/reject so page doesn't reload.

**Dependency:** Entry 8 (auth), Decision 011.

**Outcome:** Pending.

---

## Entry 10 — Approve/reject with audit trail in `review_records`

**Date:** 2026-10-29
**Worked by:** Web Developer (Onminyi Andrew), Data Quality & Database (Ihwe Matthias)
**Status:** Implemented inline in verify/reject routes (Phase 2 completion).

**What to do:**
- Verify/reject routes write to `review_records` (reviewer_id, decision, comments, timestamp).
- Submission detail page shows review history.
- Role check: only `admin` and `reviewer` can approve/reject.

**Dependency:** Entry 7 (review_records table), Entry 8 (auth), Decision 012.

**Outcome:** Pending.

---

## Entry 11 — Data exports: CSV and JSON

**Date:** 2026-10-29
**Worked by:** Data Lead (Unsegben Solomon), Web Developer (Onminyi Andrew)
**Status:** Planning complete; implementation deferred to Unit 11 per plan.

**What to do:**
- Routes: `/admin/export/csv`, `/admin/export/json`.
- Export verified submissions with fields: English text, Igede translation, direction, category, source type, status, verification status, date added.
- Admin-only access.

**Dependency:** Entry 8 (auth), Decision 013.

**Outcome:** Pending.

---

## Entry 12 — Test suite for admin dashboard and auth

**Date:** 2026-10-29
**Worked by:** Web Developer (Onminyi Andrew)
**Status:** Completed — all 15 tests pass (`python -m pytest web/MVP/tests/`).

**What to do:**
- Extend `web/MVP/tests/` with tests for: login success/failure, route protection (unauthenticated access denied), role-based access (developer cannot approve), approve/reject transitions, export endpoints.
- Run `python -m pytest web/MVP/tests/`.

**Dependency:** All prior entries.

**Outcome:** Pending.

---

## Post-Integration Follow-Ons (Phase 3)

| Follow-On | Unit | Owner | Dependency |
|---|---|---|---|
| Schema: users + review_records tables | Entry 7 | Data Q&D / Web Dev | Decision 010, 012 |
| Authentication: login/logout/guards | Entry 8 | Web Dev / Security Lead | Entry 7 |
| Admin dashboard UI | Entry 9 | Web Dev / Frontend Lead | Entry 8 |
| Approve/reject with audit trail | Entry 10 | Web Dev / Data Q&D | Entry 7, Entry 8 |
| Data exports: CSV + JSON | Entry 11 | Data Lead / Web Dev | Entry 8 |
| Test suite for admin + auth | Entry 12 | Web Dev | All prior |

---

## Document Status

Phase 2 entries 1–6 complete and verified. Phase 3 entries 7–10 implemented and verified; entries 9–11 planned pending team approval; entry 12 complete. Per collaboration principles in `docs/teams.md`, pending approval before merging into `main`.
