# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OmniCourse is a vendor-neutral, AI-assisted course authoring and export platform that generates educational content (lessons, quizzes, lecture assets), validates quality, and exports to multiple LMS formats including Open edX (OLX), QTI, SCORM 1.2, and Udemy/Teachable bundles.

**Mission**: Author → Generate → Validate → Export (no hosted LMS in v1)

## Architecture

**Stack**:
- **Frontend**: Next.js + shadcn/ui (existing, calls backend REST API)
- **Backend**: Django + DRF
- **Async Jobs**: Celery + SQS
- **Database**: PostgreSQL (RDS in prod, local Docker in dev)
- **Object Storage**: S3 (localstack/minio for dev)
- **Auth**: DRF + JWT (MVP), OIDC/Cognito planned for v2
- **AI Runtime**: boto3 → AWS Bedrock (Claude for content generation)
- **Observability**: Sentry + structured JSON logging + health endpoints

**Project Structure**:
```
backend/
  manage.py
  pyproject.toml
  src/
    core/           # settings, db, storage, auth
    ai/             # bedrock clients, prompts, validators
    courses/        # models: Course, Module, Lesson
    assessment/     # models: Quiz, Question, Objective
    export/
      olx/          # Open edX tarball builder
      scorm/
      qti/
      bundles/      # udemy/teachable packagers
    jobs/           # Celery tasks, status models
    api/            # DRF viewsets/serializers/routers
  tests/
frontend/ (existing UI)
infra/    # docker-compose, terraform placeholders
```

## Development Commands

Since this is a greenfield project, the following commands will be available once the scaffolding is complete:

**Setup & Development** (via Makefile when implemented):
- `make dev` - Start development environment with docker-compose
- `make down` - Stop development environment  
- `make logs` - View container logs
- `make test` - Run test suite
- `make lint` - Run linting (black, isort, ruff, mypy)
- `make format` - Format code
- `make migrate` - Run Django migrations
- `make shell` - Django shell

**Django Management**:
- `python manage.py seed_demo_course` - Create sample course data for testing
- `python manage.py runserver` - Start Django dev server
- `python manage.py migrate` - Apply database migrations
- `python manage.py createsuperuser` - Create admin user

**Testing**:
- `pytest` - Run all tests
- `pytest tests/exporters/` - Test specific exporter functionality
- `pytest --cov` - Run with coverage reporting

## Data Model

**Core Entities**:
- **Course**: `{id, title, audience, goals[], platform_targets[], status}`
- **Module**: `{id, course_id, title, order}`
- **Lesson**: `{id, module_id, title, markdown, est_minutes, assets[]}`
- **Quiz**: `{id, owner_ref (lesson_id|module_id), policy{difficulty, items}, export_formats[]}`
- **Question**: `{id, quiz_id, type: MCQ|MSQ|TF|SHORT, prompt, choices[], answer_key, rationale}`
- **AIJob**: `{id, kind: OUTLINE|LESSON|QUIZ|LECTURE|EXPORT, input_ref, status, cost_cents, output_ref, created_at}`
- **ExportArtifact**: `{id, course_id, kind: OLX|SCORM|QTI|UDEMY|TEACHABLE, path_s3, checksum, created_at}`

**Content Storage**: Canonical lesson content stored in Markdown, with derived assets (HTML, PDF, slides) generated on demand.

## Core API Endpoints

**Content Generation**:
- `POST /v1/jobs/generate-outline` → Create course outline
- `POST /v1/jobs/generate-lessons` → Generate lesson content 
- `POST /v1/jobs/generate-quiz` → Create quiz with questions
- `POST /v1/jobs/generate-lecture` → Generate lecture materials (script/slides/handout)

**Export**:
- `POST /v1/jobs/export` → Export course to target formats (OLX/SCORM/QTI/Udemy/Teachable)

**Management**:
- `GET /v1/jobs/{id}` → Check job status and results
- `GET /v1/courses/{id}` → Get expanded course tree
- `PUT /v1/lessons/{id}` → Update lesson content with validation

## AI Integration (AWS Bedrock)

**Models**: Claude for content generation (default temp: 0.3 for educational tone)

**Content Generation Workflows**:
1. **Course Outline**: Instructional design with learning objectives, weekly plans
2. **Lesson Generation**: Structured Markdown with sections (Overview, Objectives, Key Concepts, Examples, Summary, Check Your Understanding)
3. **Quiz Generation**: JSON-formatted questions with distractors, mapped to learning objectives
4. **Lecture Materials**: Slide outlines, speaker notes, handouts

**Quality Controls**: All AI-generated content passes through validation for profanity filtering, reading level (Flesch 60-80), objective coverage, and duplicate detection.

## Export Formats

**Target Platforms**:
- **Open edX (OLX)**: Tarball with course.xml, policies/, verticals/, problem XML
- **QTI 2.1**: Standards-compliant assessment packages with imsmanifest.xml
- **SCORM 1.2**: HTML lessons with tracking, basic cmi.core.lesson_status support
- **Udemy/Teachable**: CSV/JSON outlines + content directory with assets

**Validation**: All exports include checksums, golden file testing, and format-specific validation against XSD schemas where available.

## Development Conventions

**Code Quality**:
- Python 3.11+, strict typing with mypy
- Formatting: black, isort, ruff
- Testing: pytest with 80%+ coverage on exporters/parsers
- Commit style: Conventional commits, PRs < 400 LOC

**API Style**:
- REST/JSON with idempotent POST operations using `Idempotency-Key` header
- DRF viewsets with pagination and filtering
- RFC 7807 Problem+JSON error responses

**Security**:
- JWT authentication for MVP
- Owner-based authorization on all resources
- Secret management via environment variables
- No PII or raw prompts in logs

## Parallel Development Workflow

This project uses a dual-agent approach:
-You will be working alongside Codex for this project, you each have your own set of tasks,.
-There is also a complete overview @course_creator_agent_pack_claude_md_todo.md
-Only complete tasks from the todo_claude.md

DONT STOP WORKING, IF YOU RUN OUT OF CONTEXT WINDOW USE /COMPACT AND THEN KEEP GOING

**Claude Code Focus**: Draft code & tests, design prompts/schemas, map exporters, author Dockerfiles/CI, define validation rules

**Codex Focus**: Refactor & optimize scaffolding, implement parsers/repair utils, build XML/ZIP exporters, enhance validators, harden infrastructure

**Shared Artifacts** (must exist by Sprint 1):
- `docs/openapi/openapi.json` - API contract
- `docs/schemas/quiz.schema.json` - Quiz JSON schema
- `export/specs/{olx,qti,scorm}.md` - Export format mappings
- `tests/golden/` - Reference fixtures for export validation
- `ai/prompts/*.jinja` - Content generation templates

## Quality Standards

**Content Validation**:
- Readability: Flesch score 60-80 target
- Objective coverage: Each learning objective mapped to ≥1 assessment question
- Distractor quality: No duplicates, length variance ±30% rule
- Export validation: Golden file roundtrip tests, manifest validation

**Definition of Done** (per feature):
- Idempotent job creation with stored outputs
- Validator passes with ≤2 warnings
- Export artifacts validate against target format specs
- API matches OpenAPI documentation
- Unit + integration tests with ≥80% coverage on critical paths

## Architecture Decision Records

Significant changes to data models or export formats require ADRs in `docs/ADR-NNNN-*.md` before implementation.

## Branch Strategy

- `feature/claude/*` - Claude Code branches
- `feature/codex/*` - Codex branches  
- Target PRs against `develop`
- Keep PRs ≤400 LOC with green tests