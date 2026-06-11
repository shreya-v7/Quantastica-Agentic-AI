.DEFAULT_GOAL := help
SHELL := /bin/bash

PYTHON := $(shell command -v python3.13 || command -v python3.12 || command -v python3.11 || command -v python3)
VENV := apps/server/.venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: help
help: ## List available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-14s %s\n", $$1, $$2}'

.PHONY: setup
setup: ## Install everything: types, web deps, python venv, and .env files
	npm install
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r apps/server/requirements-dev.txt
	@test -f apps/server/.env || cp apps/server/.env.example apps/server/.env
	@test -f apps/web/.env || cp apps/web/.env.example apps/web/.env
	@echo "Setup complete. Add ANTHROPIC_API_KEY to apps/server/.env, then run 'make seed' and 'make dev'."

.PHONY: seed
seed: ## Load flagged seed data into the local database
	cd apps/server && ../../$(PY) -m app.seed load

.PHONY: seed-reset
seed-reset: ## Remove flagged seed data from the local database
	cd apps/server && ../../$(PY) -m app.seed reset

.PHONY: dev
dev: ## Run the API (:8000) and the web app (:5173) together
	@bash -c 'trap "kill 0" EXIT; \
		(cd apps/server && ../../$(VENV)/bin/uvicorn app.main:app --reload --port 8000) & \
		(npm run dev:web) & \
		wait'

.PHONY: test
test: ## Run backend and frontend tests
	cd apps/server && ../../$(PY) -m pytest -q
	npm run test -w @quantastica/web

.PHONY: lint
lint: ## Lint backend (ruff) and frontend (eslint)
	cd apps/server && ../../$(VENV)/bin/ruff check app tests
	npm run lint -w @quantastica/web

.PHONY: typecheck
typecheck: ## Typecheck the frontend
	npm run typecheck -w @quantastica/web

.PHONY: contract
contract: ## Verify contracts.json version matches the types package
	npm run check:contract

.PHONY: check-emdash
check-emdash: ## Fail if any file contains an em dash
	$(PYTHON) scripts/check_no_emdash.py

.PHONY: build-web
build-web: ## Build the web app for production
	npm run build:web

.PHONY: check
check: lint typecheck test contract check-emdash ## Run all checks (CI parity)

.PHONY: docker-up
docker-up: ## Run the full stack with docker compose
	docker compose up --build
