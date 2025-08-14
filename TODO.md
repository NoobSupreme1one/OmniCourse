# MVP TODO — Launch-Only Scope

This trims the workplan to the minimum required to launch the MVP: CRUD for course content, contract docs, one export format (SCORM 1.2) end‑to‑end with golden tests, basic auth and idempotency, and health endpoints. Non‑critical enhancements are deferred.

---

## TODO-CLAUDE (Contracts & Fixtures Only)

- [ ] OpenAPI contract: `docs/openapi/openapi.json` up to date with CRUD for courses/modules/lessons/quizzes and artifacts.
- [x] Quiz schema: `docs/schemas/quiz.schema.json` + minimal examples in `tests/fixtures/quiz/*.json`.
- [x] SCORM mapping spec only: `export/specs/scorm.md` (imsmanifest skeleton, SCO layout, minimal runtime notes).
- [x] Golden fixtures (SCORM only): `tests/golden/scorm/MANIFEST.txt` + tiny reference files.
- [ ] Minimal Bedrock prompts: `ai/prompts/{outline,lesson,quiz}.jinja` with variables and guardrails.
- [ ] Seed command: `management/commands/seed_demo_course.py` to create a tiny demo course tree.

Definition of Done (Claude): Contracts and SCORM golden fixtures exist; sample data seeds successfully.

---

## TODO-CODEX (MVP Implementation)

Inputs expected from Claude: OpenAPI, Quiz schema + examples, `export/specs/scorm.md`, SCORM golden fixtures, prompts (for reference).

### Core runtime
- [x] Settings hardening: ensure `settings/{base,dev,prod}.py` load order and env validation; sensible defaults.
- [x] Health endpoints: dependency checks (DB, broker, storage) return booleans and versions.
- [x] JWT auth: token obtain/refresh wired and usable.
- [x] Idempotency: persist/replay for `Idempotency-Key` with request/response hash.

### API basics
- [x] CRUD: implement/verify `Course`, `Module`, `Lesson`, `Quiz`, `Question`, `AIJob`, `ExportArtifact` with serializers/viewsets, pagination, simple filtering.
- [ ] Ownership permissions: owner‑based authorization across CRUD; 401/403 covered.
- [x] Problem+JSON: global error handler returning RFC 7807 shapes for consistency.

### SCORM export (single format for MVP)
- [x] Common utils: deterministic ZIP creator with normalized paths and stable ordering.
- [x] SCORM 1.2 writer: HTML lesson pages, `imsmanifest.xml`, minimal runtime `api.js` to set `cmi.core.lesson_status`.
- [x] Checksums: SHA256 for all exported files; persist on `ExportArtifact`.
- [x] Golden test: compare SCORM zip path listing + hashes with `tests/golden/scorm/*`.

### Dev ergonomics
- [x] Makefile targets verified: `make dev`, `make test`, `make lint`, `make format`, `make migrate`, `make shell` work locally.
- [ ] Pre‑commit: format/lint/type hooks installed and passing on touched code.

Definition of Done (Codex): App boots; CRUD works with auth + idempotency; health endpoints pass; SCORM export produces an archive that matches golden manifests; tests are green.

---

## Out of Scope for MVP (Deferred)

- Additional exporters (OLX, QTI) and their golden tests.
- Dashboard endpoints beyond basic artifacts listing; costs/rate limiting/cancellation.
- Advanced validators (TF‑IDF, coverage export, auto‑validate hooks).
- Sentry, metrics, detailed runbooks, extensive security hardening and backups docs.
- OpenAPI client generation, distribution packaging, and non‑essential examples.
