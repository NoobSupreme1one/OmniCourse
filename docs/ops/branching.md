# Branch Protection and Development Workflow

## Branch Structure

- `main` - Production-ready code, protected
- `develop` - Integration branch for features, protected  
- `feature/claude/*` - Claude Code feature branches
- `feature/codex/*` - Codex feature branches

## Branch Protection Rules

### Main Branch
- Require pull request reviews (2 reviewers)
- Require status checks to pass
- Require branches to be up to date
- Require conversation resolution before merging
- Restrict pushes to admins only

### Develop Branch  
- Require pull request reviews (1 reviewer)
- Require status checks to pass
- Require branches to be up to date
- Allow force pushes by admins

## Status Checks Required

- CI/CD pipeline (lint, test, build)
- Code coverage threshold (80%+)
- Security scan
- Dependency vulnerability check

## Merge Strategy

- Use "Squash and merge" for feature branches
- Use "Create a merge commit" for releases
- Delete feature branches after merge

## Release Process

1. Create release branch from `develop`
2. Bump version and update CHANGELOG.md
3. Merge to `main` via pull request
4. Tag release with semantic version
5. Merge back to `develop`