.DEFAULT_GOAL := help

.PHONY: help init-env install api-generate api-check dev lint architecture-check types test build preview compose-up compose-down

help: ## Print available frontend-local commands
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "%-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

init-env: ## Ensure the shared repository .env exists and contains required defaults
	python3 ../../scripts/init_env.py

install: ## Install frontend dependencies
	pnpm install --frozen-lockfile

api-generate: ## Generate OpenAPI-derived frontend bindings
	pnpm api:generate

api-check: ## Validate that generated frontend bindings are up to date
	pnpm api:check

dev: init-env ## Start the Vite development server
	pnpm dev

lint: ## Run frontend linting
	pnpm lint

architecture-check: ## Validate frontend architectural boundaries
	pnpm architecture:check

types: ## Run frontend type checks
	pnpm type-check

test: ## Run frontend test suite
	pnpm test:unit

build: ## Build the frontend application
	pnpm build

preview: ## Preview the production frontend build
	pnpm preview

compose-up: init-env ## Start the frontend-local Docker shell
	docker compose --env-file ../../.env -f docker-compose.yml up --build

compose-down: ## Stop the frontend-local Docker shell
	docker compose --env-file ../../.env -f docker-compose.yml down -v --remove-orphans
