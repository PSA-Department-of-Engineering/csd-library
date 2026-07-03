# Playbook Studio

Local visual browser and editor for the AI playbook (the sibling `../../ai-coding-prompts` checkout). The playbook is rendered as a radial reference graph - playbook root at the center, REFs on the inner ring clustered and colored by their `domain:` frontmatter, skills on the outer ring near the REFs they instantiate. Clicking a REF opens its parsed sections for reading and editing.

Editing applies CSD Trust Calibration to the playbook itself: a section edit is written to disk, the playbook's own deterministic gates run (intent-test suite + link checker), and the edit is **rolled back automatically** if any gate fails. The machine-generated "Skills that instantiate this REF" sections are rendered read-only (HTTP 409 on write) - they belong to `scripts/sync_backlinks.py`.

## Layout

- `studio-backend/` - Python FastAPI service, hexagonal (see its README). The domain is the playbook: `RefDoc`, `SkillDoc`, `IntentClaim`, `ReferenceEdge`, `ValidationReport`.
- `studio-frontend/` - React + TypeScript MVVM SPA typed from the backend's `openapi.json`.

## Run

Backend (default port 8000, override with `PORT`; the frontend dev proxy expects 8907):

```bash
cd studio-backend
python -m venv .venv && .venv/Scripts/python -m pip install -e ".[dev]"
.venv/Scripts/python -m pip install -e ../../pytest-intent   # the validator runs the playbook's suite
set PORT=8907 && .venv/Scripts/python -m studio.adapters.inbound.http.run
```

Frontend (dev server proxies `/api` to `127.0.0.1:8907`):

```bash
cd studio-frontend
npm install && npm run dev
```

The playbook location defaults to the sibling `../../../ai-coding-prompts`; override with `STUDIO_PLAYBOOK_ROOT`.

## Contract sync

After any backend DTO or route change: `.venv/Scripts/python scripts/export_openapi.py` in `studio-backend`, then `npm run api:generate` in `studio-frontend` (or `npm run api:sync` against a running backend).
