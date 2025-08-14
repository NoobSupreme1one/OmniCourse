# Repository Guidelines
-You will be working alongside Claude for this project, you each have your own set of tasks,.
-There is also a complete overview @course_creator_agent_pack_claude_md_todo.md
-Only complete tasks from the todo_codex.md

DONT STOP WORKING, IF YOU RUN OUT OF CONTEXT WINDOW USE /COMPACT AND THEN KEEP GOING

## Project Structure & Module Organization
- backend/: Django + DRF code lives under `backend/src/` with apps like `core/`, `ai/`, `courses/`, `assessment/`, `export/`, `jobs/`, `api/`.
- docs/: Contracts and specs (source of truth), e.g., `docs/openapi/`, `docs/schemas/`, `export/specs/`.
- tests/: Pytest suite and fixtures; golden outputs in `tests/golden/{olx,qti,scorm}/`.
- ai/prompts/: Bedrock prompt templates (`*.jinja`).

## Build, Test, and Development Commands
- make dev: Start local stack (API, worker, DB, S3) via compose.
- make test: Run `pytest` with coverage; respects `-k` and `-q`.
- make lint: Run `ruff`, `black --check`, `isort --check-only`, `mypy`.
- make format: Auto-format with `black` and `isort`.
- make migrate|shell|logs: Common Django/Celery dev actions.
- pre-commit install; pre-commit run -a: Set up and run hooks locally.

## Coding Style & Naming Conventions
- Python 3.11+, 4-space indent; `black` (default), `isort` (profile=black), `ruff` for lint, `mypy` strict-ish for public APIs.
- Naming: `snake_case` modules/functions, `PascalCase` classes, `UPPER_SNAKE` constants. Prefer explicit imports.
- API: REST/JSON, idempotent POSTs with `Idempotency-Key`; keep request/response shapes aligned with `docs/openapi/openapi.json`.

## Testing Guidelines
- Framework: `pytest` with `pytest-django`; place unit tests near apps (e.g., `backend/src/export/tests/`) and integration tests under `tests/`.
- Coverage: ≥80% for parsers/validators/exporters; include golden-file tests comparing path listings and hashes under `tests/golden/*`.
- Naming: `test_*.py`, functions `test_*`; use factories/fixtures and minimal mocks.
- Run: `pytest -q` or `pytest backend/src/export -k qti` for focused runs.

## Commit & Pull Request Guidelines
- Branching: `feature/claude/*` (design/contracts) and `feature/codex/*` (impl/refactors). PRs target `develop` and stay ≤400 LOC when feasible.
- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`); imperative mood; scoped changes.
- PRs: Clear description, linked issues, test plan, and sample inputs/outputs (attach golden manifest diffs for exporters). Passing CI required.

## Security & Configuration
- Use `.env` for local secrets; never commit credentials. Prefer IAM roles in prod.
- Don’t log PII or full prompts; redact tokens/keys. Changes to schemas or data model require an ADR in `docs/`.
