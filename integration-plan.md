# Integration Plan — Phase 2: Replace MVP Templates with test/ Frontend

> Status: Draft
> Date: 2026-10-29
> Owner: Web Developer (Onminyi Andrew)

This plan documents how the polished `test/` frontend replaces the legacy Flask templates (`submit.html`, `dataset.html`, `review.html`) while making `test/index.html` live as the single production page served through Flask.

---

## Rationale

The current Flask app had four templates under `web/MVP/templates/`:

- `index.html` — minimal home page (nav links only)
- `submit.html` — inline form (hardcoded option lists, manual redirect)
- `dataset.html` — table of verified rows (no pagination)
- `review.html` — review interface (no auth gate, renders full rows)

`test/index.html` contains a fully polished hero, 4 feature tiles, dynamic form labels, direction swap, per-field character counters, validation, toast notification, theme toggle, and sidebar drawer menu — none of which existed before. Keeping both sets causes maintenance debt every time one set changes. One source of truth wins.

---

## Approach

### Step 1 — Extract shared constants
Create `web/MVP/validators.py` exporting allowed-set frozensets plus display maps, used by both `app.py` and the Jinja template. This prevents drift between backend rules and frontend options.

### Step 2 — Make `test/index.html` a Jinja template
Rename references appropriately. Rewrite the two `<select>` blocks to render options dynamically from `{{ CATEGORY_DISPLAY }}` etc. Add `url_for('static', ...)` calls for CSS and images. Keep the toast markup; surface server response via JS instead of `console.log`.

### Step 3 — Add REST submission endpoint
Replace `POST /submit` form view with `POST /api/submissions` JSON endpoint, matching the payload shape already built in `test/app.js` (`direction`, `source_text`, `translation`, `category`, `source_type`, `submitted_at`).

### Step 4 — Surface submitted messages server-side
Return JSON envelope `{"ok": true, "message": ...}`. In `test/app.js`, on success, fetch `/api/submissions` again and display the response message as the toast text.

### Step 5 — Sync static assets
Copy `test/style.css`, `test/bgimage.png`, `test/our2.png` into `web/MVP/static/`. They now live alongside Flask's static folder. Update asset references in the template to use Flask's `url_for('static', ...)` helper instead of bare filenames.

### Step 6 — Remove superseded Flask templates
Delete `web/MVP/templates/{submit,dataset,review}.html`. Update `.gitignore` if needed to stop tracking these specific files or mark them gone. Leave the route functions alone — they just won't be rendered anymore.

### Step 7 — Keep admin views available for deferred auth work
Routes `/review` and `/dataset` stay defined but protected; they'll activate once auth gate code lands in Unit 6. No changes needed here.

---

## Pending Tasks (Phase-3 items for after integration)

- Auth implementation for `/review*` and `/dataset` (Unit 6)
- Duplicate detection at insert (Unit 4)
- Pagination UI on dataset/review views (Unit 5)
- Test suite (Unit 7)
- Test copy cleanup (Unit 8)

See `work_log.md` for per-unit entries.

---

## Approval

Per collaboration principles in `docs/teams.md`, pending Team approval before merging into `main`.
