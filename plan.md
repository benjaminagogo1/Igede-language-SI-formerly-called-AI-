# Development Plan — Phase 3: Admin Dashboard & Multi-User Access

> Status: Planning complete; implementation not started
> Date: 2026-10-29
> Owner: Web Developer (Primary: Onminyi Andrew)
> Team: Eight developers — see `docs/teams.md`

This plan covers the work after Phase 2 integration (frontend wired to Flask backend, REST submission endpoint, shared validators, corrected schema, passing test suite). Phase 3 adds authenticated, role-based admin access so the eight developers can review, approve, reject, and export Igede language submissions.

---

## 1. Objective

Turn the current public submission flow into a full data management platform:

- **Multi-user authentication**: each of the eight developers gets their own account (`admin`, `reviewer`, or `developer` role).
- **Admin dashboard**: a modern browser-based UI for reviewing submissions, approving/rejecting them with audit trail, and exporting verified data.
- **Public site preserved**: the existing home page, contribution form (text, audio, image tabs), and cultural design remain unchanged and open to everyone.

---

## 2. What Already Exists (Inventory)

| Area | Current State | Owner Files |
|------|---------------|-------------|
| Backend | Flask app with `GET /`, `POST /api/submissions` (JSON REST), protected JSON endpoints `/dataset`, `/review`, `/review/<id>/verify`, `/review/<id>/reject` (env-var gate, not multi-user) | `web/MVP/app.py`, `database.py`, `schema.sql` |
| Schema | Single `submissions` table (`source_text`, `translation`, `direction`, `category`, `source_type`, `status`, `verified_by`, `verification_date`, `notes`, `source_hash`, `submitted_at`, `date_added`) | `web/MVP/schema.sql` |
| Frontend | Polished public page with Text contribution form (Audio/Image tabs not yet implemented), theme toggle, character counters, REST submit via `fetch` | `web/MVP/templates/index.html`, `web/MVP/static/{app.js,style.css}` |
| Shared constants | `validators.py` owns allowed directions/categories/source types | `web/MVP/validators.py` |
| Tests | `web/MVP/tests/{conftest.py,test_submissions.py}` — 7 tests, all passing | `web/MVP/tests/` |
| Docs | `Igede .md` (project overview + three new ideas), `decisions.md` (003–013), `work_log.md` (Phase 2 complete, Phase 3 planned), `integration-plan.md` | Root + docs |

---

## 3. Work Units

### Unit 7 — Schema: add `users` and `review_records` tables

**Priority:** High

**Rationale:** With eight developers, we need individual accounts and an audit trail of who approved or rejected each submission. The current schema has only `verified_by`/`verification_date` (overwritten on each decision).

**Approach:**
- Add `users` table: `id`, `username` (unique), `password_hash`, `role` (`admin`/`reviewer`/`developer`), `created_at`.
- Add `review_records` table: `id`, `submission_id` (FK → submissions), `reviewer_id` (FK → users), `decision` (`approved`/`rejected`/`needs_correction`), `comments`, `created_at`.
- Keep `submissions.verified_by`/`verification_date` for backwards compatibility.
- Migration script to apply to existing `igede.db`.

**Dependency:** Decision 010 (multi-user auth), Decision 012 (review history table).

**Deliverable:** Updated `web/MVP/schema.sql`, migration applied, `init_db()` creates both new tables.

---

### Unit 8 — Authentication: login, logout, role-based route guards

**Priority:** High (Security)

**Rationale:** Admin routes must not be accessible without login. With eight developers, role-based access prevents developers from accidentally approving submissions they shouldn't.

**Approach:**
- Add Flask-Login + Werkzeug password hashing.
- Routes: `/login` (GET/POST), `/logout` (POST).
- Decorators: `@login_required`, `@admin_required`, `@reviewer_required`.
- Public submission route (`/api/submissions`) remains open to all.
- Migrate `/dataset`, `/review`, verify/reject routes from env-var header gate to session-based checks.

**Dependency:** Unit 7 (users table), Decision 010.

**Deliverable:** Auth routes in `app.py`, login template, protected admin routes.

---

### Unit 9 — Admin dashboard UI: Overview, Submissions, Review Queue

**Priority:** High

**Rationale:** Developers need a browser-based dashboard to manage data, not just JSON API endpoints. Matches the `Admin_UI.png` mockup.

**Approach:**
- Templates under `web/MVP/templates/admin/`: `login.html`, `dashboard.html`, `submissions.html`, `review.html`, `detail.html`, `exports.html`.
- Styles in `web/MVP/static/admin.css` preserving the existing brand (dark blue / bright blue, logo, glassmorphism cards).
- Overview stat cards: total submissions, pending review, approved, rejected.
- Submissions table with search, filter (status/category/direction/source type/date), pagination (server-side `LIMIT`/`OFFSET`, Decision 007).
- Review Queue listing only `pending` submissions with approve/reject actions.
- Progressive `fetch()` for approve/reject so page doesn't reload (Decision 011).

**Dependency:** Unit 8 (auth), Decision 011.

**Deliverable:** Admin templates + CSS, dashboard routes in `app.py`.

---

### Unit 10 — Approve/reject with audit trail in `review_records`

**Priority:** High

**Rationale:** Every review decision must record who made it and when, for accountability across eight developers.

**Approach:**
- Verify/reject routes write to `review_records` (reviewer_id, decision, comments, timestamp).
- Submission detail page shows review history.
- Role check: only `admin` and `reviewer` can approve/reject.

**Dependency:** Unit 7 (review_records table), Unit 8 (auth), Decision 012.

**Deliverable:** Approve/reject routes writing audit records, detail page with history.

---

### Unit 11 — Data exports: CSV and JSON

**Priority:** Medium

**Rationale:** Admins need to download verified data for dataset preparation and AI training (per `Igede .md` New Idea One).

**Approach:**
- Routes: `/admin/export/csv`, `/admin/export/json`.
- Export verified submissions with fields: English text, Igede translation, direction, category, source type, status, verification status, date added.
- Admin-only access.

**Dependency:** Unit 8 (auth), Decision 013.

**Deliverable:** Export routes returning file downloads.

---

### Unit 12 — Test suite for admin dashboard and auth

**Priority:** Medium

**Rationale:** Auth and admin actions need test coverage before merging to `main` with eight developers touching the code.

**Approach:**
- Extend `web/MVP/tests/` with tests for: login success/failure, route protection (unauthenticated access denied), role-based access (developer cannot approve), approve/reject transitions, export endpoints.
- Run `python -m pytest web/MVP/tests/`.

**Dependency:** All prior units.

**Deliverable:** New test files, all tests passing.

---

### Unit 13 — Audio and Image contribution tabs (public frontend)

**Priority:** Medium

**Rationale:** Per `Igede .md` New Ideas Two and Three and the `users_UI.png` mockup — three contribution tabs (Text/Audio/Image) using the same card.

**Approach:**
- Extend `templates/index.html` form card with Audio and Image tabs.
- Audio: record/upload file, associate with written sentence, dialect/location, consent status.
- Image: upload image, English label, Igede label, category, notes, permission status.
- Backend endpoints to receive and store audio/image metadata (files stored separately, paths saved in DB per `Igede .md` architecture).

**Dependency:** Unit 8 (auth for media access), `Igede .md` sections 5–6.

**Deliverable:** Public UI tabs + backend media upload routes.

---

## 4. Dependencies and Sequence

```
Unit 7 (schema) ──► Unit 8 (auth) ──► Unit 9 (dashboard UI)
                     │                │
                     └──► Unit 10 (audit trail) ◄── Unit 9
                          │
                          └──► Unit 11 (exports) ◄── Unit 8
                          
Unit 7 ──► Unit 12 (tests) ◄── all prior units

Unit 13 (audio/image tabs) — independent; can run in parallel with Units 7–11
```

Unit 8 depends on Unit 7. Unit 9 depends on Unit 8. Unit 10 depends on Units 7 and 8. Unit 11 depends on Unit 8. Unit 12 depends on all prior units. Unit 13 is independent and can start in parallel.

---

## 5. Risks

| Risk | Mitigation |
|------|------------|
| Schema divergence between SQLite MVP and PostgreSQL target | Keep `web/MVP/schema.sql` as single source of truth; document PostgreSQL migration as a future decision entry. |
| Eight developers making conflicting auth decisions | Enforce Decision 010: one shared auth implementation, no per-developer auth forks. |
| Review decisions overwritten without audit trail | `review_records` table (Decision 012) preserves every decision; `verified_by` not the sole source of truth. |
| Admin routes accessible without login | Role-based decorators on every admin route; tests in Unit 12 assert protection. |
| Public site broken by admin work | Admin templates live under `templates/admin/`; public `index.html` unchanged. |

---

## 6. Success Criteria

After completing these units, the following must hold:

1. Each of the eight developers can log in with their own account and role.
2. Unauthenticated users cannot access `/admin/*` routes (HTTP 401/redirect to login).
3. Developers cannot approve/reject submissions (role enforcement).
4. Admins and reviewers can approve/reject with an audit record in `review_records`.
5. Admin dashboard shows paginated, filterable submissions with search.
6. Verified data can be exported as CSV and JSON.
7. Public contribution form (text/audio/image tabs) still works without login.
8. `python -m pytest web/MVP/tests/` passes (including new auth/admin tests).
9. `decisions.md` and `work_log.md` are current with all Phase 3 decisions and entries.

---

## 7. Approval

Per collaboration principles in `docs/teams.md`, any technical change affecting these units requires team review before merging into `main`. Pending approval: [Date: TBD].
