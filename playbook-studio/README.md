# Playbook Studio

Local visual browser and editor for the AI playbook (the sibling `../../ai-coding-prompts` checkout). The playbook is rendered as a radial reference graph - playbook root at the center, REFs on the inner ring clustered and colored by their `domain:` frontmatter, skills on the outer ring near the REFs they instantiate. Clicking a REF opens its parsed sections for reading and editing.

Editing applies CSD Trust Calibration to the playbook itself: a section edit is written to disk, the playbook's own deterministic gates run (intent-test suite + link checker), and the edit is **rolled back automatically** if any gate fails. The machine-generated "Skills that instantiate this REF" sections are rendered read-only (HTTP 409 on write) - they belong to `scripts/sync_backlinks.py`.

## Layout

- `studio-backend/` - Python FastAPI service, hexagonal (see its README). The domain is the playbook: `RefDoc`, `SkillDoc`, `IntentClaim`, `ReferenceEdge`, `ValidationReport`.
- `studio-frontend/` - React + TypeScript MVVM SPA typed from the backend's `openapi.json`.

## Run

Double-click `devops/start.bat` (or `powershell -ExecutionPolicy Bypass -File devops/start.ps1`). The first run provisions everything (backend venv + deps + pytest-intent, frontend `npm ci` + generated API types); every run spawns the two server windows and opens http://localhost:5199. Close the windows to stop.

Manual equivalent: backend `PORT=8907` via `studio-backend/.venv/Scripts/python -m studio.adapters.inbound.http.run`, frontend `npm run dev -- --port 5199` (the dev proxy expects the backend on `127.0.0.1:8907`). The playbook location defaults to the sibling `../../../ai-coding-prompts`; override with `STUDIO_PLAYBOOK_ROOT`.

## Intent claims (CSD)

The studio eats its own dog food: `intent.yaml` at this root declares the claims (gated writes roll back, generated sections immutable, creation delegates to the playbook's own bootstrap skills, graph fidelity, layout invariants). Backend tests carry `@intent` (pytest-intent), frontend tests carry `intent()` (vitest-intent). Audit both in one pass:

```bash
studio-backend/.venv/Scripts/csd-intent .
```

## Contract sync

After any backend DTO or route change: `.venv/Scripts/python scripts/export_openapi.py` in `studio-backend`, then `npm run api:generate` in `studio-frontend` (or `npm run api:sync` against a running backend).
