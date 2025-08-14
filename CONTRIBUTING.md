# Contributing to OmniCourse

## Development Workflow

1. Fork the repository
2. Create a feature branch: `feature/claude/*` or `feature/codex/*`
3. Make your changes following the guidelines below
4. Ensure tests pass and code is formatted
5. Create a pull request against `develop`

## Code Standards

### Python Backend
- Python 3.11+
- Format with `black`, `isort`, `ruff`
- Type hints with `mypy` (strict-ish)
- Test with `pytest`
- Follow conventional commits

### Pull Request Guidelines
- Keep PRs under 400 LOC when feasible
- One feature per PR
- Include tests for new functionality
- Update documentation as needed
- Ensure CI passes

### Commit Messages
Follow conventional commits format:
```
feat: add quiz generation endpoint
fix: resolve CORS issue in dev environment
docs: update API documentation
test: add integration tests for exporters
```

## Architecture Decisions

- Document significant changes in `docs/ADR-NNNN-*.md`
- Changes to data models or export schemas require ADR
- Prefer boring, battle-tested libraries
- Keep human review small and frequent

## Testing
- 80%+ coverage on exporters and parsers
- Golden files for packaged outputs
- Integration tests for API endpoints
- Unit tests for business logic

## Security
- No secrets in code or logs
- Environment variables for configuration
- JWT authentication for MVP
- Owner-based authorization