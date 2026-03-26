.DEFAULT_GOAL := help
ALEMBIC := uv run alembic -c ../../alembic.ini

.PHONY: help init-env sync lint types test test-migrations migrate downgrade current history makemigration compose-up compose-down

help: ## Print available backend-local commands
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "%-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

init-env: ## Ensure the shared repository .env exists and contains required defaults
	python3 ../../scripts/init_env.py

sync: ## Sync backend dependencies
	uv sync --group dev

lint: ## Run the backend lint pipeline
	python3 ../../scripts/run_backend_lint.py

types: ## Run backend type checks
	python3 ../../scripts/run_backend_types.py

test: ## Run backend tests, including pytest-alembic checks against Testcontainers PostgreSQL
	python3 ../../scripts/run_backend_tests.py

test-migrations: ## Run migration-only tests against an ephemeral Testcontainers PostgreSQL database
	uv run pytest -q tests/migrations --test-alembic

migrate: ## Apply all Alembic migrations to the configured database
	$(ALEMBIC) upgrade head

downgrade: ## Downgrade the configured database to rev=<revision>
	@test -n "$(rev)" || (echo "Usage: make downgrade rev=<revision>" && exit 1)
	$(ALEMBIC) downgrade $(rev)

current: ## Show the current Alembic revision
	$(ALEMBIC) current

history: ## Show Alembic migration history
	$(ALEMBIC) history

makemigration: ## Create a new Alembic revision with m="message"
	@test -n "$(m)" || (echo "Usage: make makemigration m=\"message\"" && exit 1)
	$(ALEMBIC) revision --autogenerate -m "$(m)"

compose-up: init-env ## Start the backend-local Docker stack
	docker compose --env-file ../../.env -f docker-compose.yml up --build

compose-down: ## Stop the backend-local Docker stack
	docker compose --env-file ../../.env -f docker-compose.yml down -v --remove-orphans
