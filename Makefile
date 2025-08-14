#!/usr/bin/env make

.PHONY: help dev up down logs test lint format migrate shell install clean e2e

# Default target
help:
	@echo "Available commands:"
	@echo "  dev       - Start development environment"
	@echo "  up        - Start all services"
	@echo "  down      - Stop all services"  
	@echo "  logs      - View container logs"
	@echo "  test      - Run test suite"
	@echo "  lint      - Run linting (ruff, mypy)"
	@echo "  format    - Format code (black, isort)"
	@echo "  migrate   - Run Django migrations"
	@echo "  shell     - Django shell"
	@echo "  install   - Install dependencies"
	@echo "  clean     - Clean up containers and volumes"
	@echo "  e2e       - Run end-to-end stub"

# Development environment
dev: up migrate
	@echo "Development environment ready!"
	@echo "API: http://localhost:8000"
	@echo "Admin: http://localhost:8000/admin"
	@echo "Docs: http://localhost:8000/api/docs"

e2e:
	@echo "E2E stub: run app, hit /healthz and basic flows."
	@echo "Implement real browser/API tests in CI pipeline."

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

# Testing
test:
	cd backend && python -m pytest

test-cov:
	cd backend && python -m pytest --cov=src --cov-report=html --cov-report=term-missing

# Code quality
lint:
	cd backend && python -m ruff check src/
	cd backend && python -m mypy src/

format:
	cd backend && python -m black src/
	cd backend && python -m isort src/

# Django management
migrate:
	cd backend && python manage.py migrate

makemigrations:
	cd backend && python manage.py makemigrations

shell:
	cd backend && python manage.py shell

createsuperuser:
	cd backend && python manage.py createsuperuser

collectstatic:
	cd backend && python manage.py collectstatic --noinput

# Dependencies
install:
	cd backend && pip install -e .[dev]

# Cleanup
clean:
	docker-compose down -v
	docker system prune -f

# Database
dbshell:
	cd backend && python manage.py dbshell

# Celery
celery:
	cd backend && celery -A core worker -l INFO

celery-beat:
	cd backend && celery -A core beat -l INFO

# Seed data
seed:
	cd backend && python manage.py seed_demo_course

# OpenAPI schema
schema:
	cd backend && python manage.py spectacular --file docs/openapi/openapi.json

# Pre-commit hooks
install-hooks:
	pre-commit install

run-hooks:
	pre-commit run --all-files
