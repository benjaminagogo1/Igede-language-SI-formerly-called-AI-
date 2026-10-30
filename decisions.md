# Decisions Log — Phase 2 & Phase 3

> Status: Active
> Date: 2026-10-29
> Format: date, Decision, Reason, People involved, Status

---

## Decision 003 — Use REST for submission API

**Date:** 2026-10-29
**Decision:** The `test/` static site will POST submissions as JSON to a dedicated REST endpoint (`POST /api/submissions`). The existing Flask form route (`POST /submit`) remains available for traditional multi-page apps or quick prototypes.
**Reason:** The static site already builds and sends a JSON payload. Reusing `/submit` would require changing the client to multipart forms; introducing a clean API endpoint decouples the presentation layer from the data layer and aligns with the documented "Backend / API" component in `docs/architecture.md`.
**People involved:** Web Developer (Onminyi Andrew), Community & Growth (Onsegben Solomon)
**Status:** Approved

---

## Decision 004 — SQLite schema stays as MVP baseline

**Date:** 2026-10-29
**Decision:** The SQLite schema in `web/MVP/schema.sql` remains the production baseline for the MVP. The richer PostgreSQL design in `database/schema.sql` is preserved as the future target but is not integrated now.
**Reason:** SQLite requires no separate server process, is simpler to deploy, and the existing `app.py`, `database.py`, and `igede.db` already work with it. PostgreSQL is a longer-term upgrade path that should not delay current integration work.
**People involved:** Data Quality & Database (Ihwe Matthias), Web Developer (Onminyi Andrew)
**Status:** Approved

---

## Decision 005 — Single source of truth for validation constants

**Date:** 2026-10-29
**Decision:** Allowed values for direction, category, and source type live in a shared Python module (`web/MVP/validators.py`) imported by both `app.py` and the Jinja templates. Templates iterate over these sets dynamically rather than hardcoding `<option>` values in HTML.
**Reason:** Currently allowed sets are duplicated across `app.py` (Python) and `submit.html` (HTML). New categories added later require editing two places; this drift risk is unacceptable for a project with quality standards. A shared Python module makes templates inherit from it automatically.
**People involved:** Data Quality & Database (Ihwe Matthias), Communication Lead (Ibe Wealth)
**Status:** Approved

---

## Decision 006 — Exact-duplicate detection at insert, near-duplicate deferred

**Date:** 2026-10-29
**Decision:** Add an indexed hash of the normalized English text checked before INSERT to reject exact duplicates immediately. Full near-duplicate detection (e.g., Levenshtein similarity) remains a review-phase task for subsequent sprints.
**Reason:** Near-duplicate detection requires either expensive full-text similarity computations or an external similarity library. For the MVP target of 1,000 verified entries, exact-duplicate blocking at insert covers the majority of abuse. Deferring near-dup to review avoids premature complexity.
**People involved:** Data Lead (Unsegben Solomon), Data Quality & Database (Ihwe Matthias)
**Status:** Approved

---

## Decision 007 — Server-side pagination over client filtering

**Date:** 2026-10-29
**Decision:** Dataset and review queries use server-side `LIMIT`/`OFFSET` pagination. Client-side infinite scrolling or filtering is deferred until the dataset grows large enough to justify it.
**Reason:** Server pagination produces stable URLs, simple caching, and predictable response sizes. Client-side filtering only becomes valuable once the frontend can receive and filter thousands of rows without degrading performance; deferring keeps the MVP lean.
**People involved:** Web Developer (Onminyi Andrew), AI / Chatbot Developer (Otetem Benjamin)
**Status:** Approved

---

## Decision 008 — Env-var gate for review access

**Date:** 2026-10-29
**Decision:** Protected routes (`/review*`, `/dataset`) require an environment variable check (`IGEDE_REVIEW_USER` set and matching the request header) before rendering. Submit (`/submit`) remains open to all users.
**Reason:** No existing user accounts, sessions, or auth libraries are configured. An environment-variable gate provides immediate protection with zero runtime cost and adequate for MVP testing. Full session login is documented as Future Work for when the app deploys publicly.
**People involved:** Web Developer (Onminyi Andrew), Communication Lead (Ibe Wealth)
**Status:** Approved

---

## Decision 009 — Fix the `varified_by` typo

**Date:** 2026-10-29
**Decision:** Rename the column `varified_by` to `verified_by` in `web/MVP/schema.sql`. No application code currently references the typo'd name, so this is a correctness fix rather than a compatibility break.
**Reason:** Inconsistent spelling creates confusion when reading raw SQL and risks recurrence if someone copy-pastes without checking. Correcting now prevents a silent bug from slipping into later migrations.
**People involved:** Data Quality & Database (Ihwe Matthias)
**Status:** Approved

---

## Decision 010 — Multi-user role-based authentication for admin dashboard

**Date:** 2026-10-29
**Decision:** Replace the single env-var header gate with per-developer user accounts using Flask-Login and Werkzeug password hashing. Roles: `admin`, `reviewer`, `developer`. Each of the eight developers gets their own account. Passwords are hashed and stored in a new `users` table; never plaintext.
**Reason:** With eight developers on the team, a shared password or env-var header check does not provide accountability. Individual accounts let us record *who* approved or rejected each submission and enforce role-based access to admin routes.
**People involved:** Web Developer (Onminyi Andrew), Security Lead (TBD)
**Status:** Approved

---

## Decision 011 — Admin dashboard: server-rendered Jinja + progressive JavaScript

**Date:** 2026-10-29
**Decision:** Build the admin dashboard as server-rendered Flask/Jinja templates with progressive `fetch()` enhancements for approve/reject actions (no full page reload). No separate SPA build step or frontend framework.
**Reason:** Keeps a single codebase and stack consistent with the existing MVP. Easier for the team to maintain, debug, and extend without a Node/build pipeline.
**People involved:** Web Developer (Onminyi Andrew), Frontend Lead (TBD)
**Status:** Approved

---

## Decision 012 — Review history stored in separate `review_records` table

**Date:** 2026-10-29
**Decision:** Add a `review_records` table with foreign keys to `submissions.id` and `users.id`, recording `decision` (approved/rejected/needs_correction), `comments`, and `created_at`. The `submissions.verified_by` column is retained for backwards compatibility but new review actions write to `review_records`.
**Reason:** The SQLite schema currently stores only one `verified_by`/`verification_date` pair per submission, which is overwritten on each decision. A separate history table preserves every review decision, who made it, and when — required for an eight-developer team with audit needs.
**People involved:** Data Quality & Database (Ihwe Matthias), Web Developer (Onminyi Andrew)
**Status:** Approved

---

## Decision 013 — Data export formats: CSV and JSON first

**Date:** 2026-10-29
**Decision:** Admin exports will provide CSV and JSON downloads of verified submissions. Excel-compatible export is deferred unless explicitly requested.
**Reason:** CSV and JSON cover the documented export requirements (text submissions and structured data for programmatic use) with minimal implementation overhead. Excel can be added later via a library if the team needs it.
**People involved:** Data Lead (Unsegben Solomon), Web Developer (Onminyi Andrew)
**Status:** Approved

---

## Future Decisions (not yet made)

The following decisions should be recorded here once the team reaches them:

- Decision for PostgreSQL migration path from SQLite (migration guide / step-by-step).
- Decision on whether Excel export should be added.
- Decision for tests framework version and CI integration (tests exist but no CI configured).
- Decision on keeping or removing `test/Igede Language SI · Data Collection.md` (duplicate of README).

---

## Document Status

Decisions 003–009 cover Phase 2 integration (completed). Decisions 010–013 cover Phase 3 admin dashboard scope (entries 7–8 completed; entries 9–11 planned). Per collaboration principles in `docs/teams.md`, pending team approval before merging into `main`.
