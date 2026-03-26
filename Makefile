.DEFAULT_GOAL := help
BACKEND_PYTHON := uv run --project src/backend python

.PHONY: help \
	init-env compose-up compose-down \
	backend-sync frontend-install install-hooks bootstrap \
	check check-core check-environment doctor frontend-architecture contract-parity frontend-api-generate \
	backend-fix frontend-fix fix \
	backend-lint backend-observability frontend-lint repo-lint lint lint-core \
	backend-types frontend-types \
	backend-test frontend-test contract-test e2e-test test test-core \
	frontend-build build build-core \
	backend-security repo-security security \
	docker-build security-core ci

help: ## Print available commands
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "%-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

init-env: ## Initialize the shared .env from .env.example and backfill missing defaults
	python3 scripts/init_env.py

backend-sync: ## Sync backend dependencies
	python3 scripts/run_backend_sync.py

frontend-install: ## Install frontend dependencies
	python3 scripts/run_frontend_install.py

install-hooks: ## Install local pre-commit and pre-push hooks
	cd src/backend && uv run pre-commit install --config ../../.pre-commit-config.yaml --install-hooks --hook-type pre-commit --hook-type pre-push

bootstrap: init-env ## Sync dependencies and install repository hooks
	@echo "==> Syncing backend dependencies"
	python3 scripts/run_backend_sync.py
	@echo "==> Installing frontend dependencies"
	python3 scripts/run_frontend_install.py
	@echo "==> Installing git hooks"
	cd src/backend && uv run pre-commit install --config ../../.pre-commit-config.yaml --install-hooks --hook-type pre-commit --hook-type pre-push

check-environment: ## Validate required local tooling
	python3 scripts/check_environment.py

check-core: ## Run repository invariants shared by local checks, doctor and CI
	python3 scripts/check_adrs.py
	python3 scripts/check_repo_structure.py
	$(BACKEND_PYTHON) scripts/check_backend_architecture.py
	$(BACKEND_PYTHON) scripts/check_backend_observability.py
	python3 scripts/check_frontend_architecture.py
	python3 scripts/check_specs.py
	$(BACKEND_PYTHON) scripts/check_http_contract_parity.py
	python3 scripts/check_template_consistency.py
	python3 scripts/check_ci_symmetry.py

contract-parity: ## Validate spec/backend/frontend HTTP contract parity
	$(BACKEND_PYTHON) scripts/check_http_contract_parity.py

check: ## Run repository invariants
	@$(MAKE) check-core

doctor: ## Validate environment and core template invariants
	@echo "==> Validating local toolchain"
	@$(MAKE) check-environment
	@echo "==> Validating repository skeleton, ADRs and architecture"
	@$(MAKE) check-core
	@echo "Doctor completed successfully."

compose-up: init-env ## Start the full Docker compose ensemble
	docker compose --env-file .env up --build

compose-down: ## Stop the full Docker compose ensemble
	docker compose --env-file .env down -v --remove-orphans

backend-fix: ## Run backend autofixers
	python3 scripts/run_backend_lint_fix.py
	python3 scripts/run_backend_pyupgrade.py
	python3 scripts/run_backend_eradicate.py

frontend-fix: ## Run frontend autofixers
	uv run --project src/backend python scripts/generate_frontend_openapi_client.py
	python3 scripts/run_frontend_lint_fix.py

frontend-api-generate: ## Generate frontend API client and types from OpenAPI
	uv run --project src/backend python scripts/generate_frontend_openapi_client.py

fix: ## Run all autofixers
	@echo "==> Fixing backend sources"
	python3 scripts/run_backend_lint_fix.py
	python3 scripts/run_backend_pyupgrade.py
	python3 scripts/run_backend_eradicate.py
	@echo "==> Fixing frontend sources"
	uv run --project src/backend python scripts/generate_frontend_openapi_client.py
	python3 scripts/run_frontend_lint_fix.py

backend-lint: ## Run backend lint pipeline
	python3 scripts/run_backend_lint.py
	$(BACKEND_PYTHON) scripts/check_backend_observability.py
	python3 scripts/run_backend_import_boundaries.py
	python3 scripts/run_backend_deptry.py
	python3 scripts/run_backend_tryceratops.py
	python3 scripts/run_backend_xenon.py

backend-observability: ## Validate backend observability invariants
	$(BACKEND_PYTHON) scripts/check_backend_observability.py

frontend-lint: ## Run frontend lint pipeline
	python3 scripts/run_frontend_lint.py

frontend-architecture: ## Validate frontend architecture and UI boundary
	python3 scripts/check_frontend_architecture.py

repo-lint: ## Run shell and Dockerfile lint checks
	./scripts/run_shellcheck.sh
	./scripts/run_hadolint.sh

lint-core: ## Run the shared lint stage for local and CI workflows
	@echo "==> Linting backend"
	@$(MAKE) backend-lint
	@echo "==> Linting frontend"
	@$(MAKE) frontend-lint
	@echo "==> Linting repository assets"
	@$(MAKE) repo-lint

lint: ## Run full lint pipeline
	@$(MAKE) lint-core

backend-types: ## Run backend type checks
	python3 scripts/run_backend_types.py

frontend-types: ## Run frontend type checks
	python3 scripts/run_frontend_types.py

backend-test: ## Run backend tests
	python3 scripts/run_backend_tests.py

frontend-test: ## Run frontend tests
	python3 scripts/run_frontend_tests.py

contract-test: ## Run cross-app contract tests
	python3 scripts/run_contract_tests.py

e2e-test: ## Run cross-app smoke/e2e tests
	python3 scripts/run_e2e_tests.py

test-core: ## Run the shared test stage for local and CI workflows
	@echo "==> Testing backend"
	@$(MAKE) backend-test
	@echo "==> Testing frontend"
	@$(MAKE) frontend-test
	@echo "==> Testing cross-app contracts"
	@$(MAKE) contract-test
	@echo "==> Testing cross-app smoke flows"
	@$(MAKE) e2e-test

test: ## Run full test pipeline
	@$(MAKE) test-core

frontend-build: ## Build frontend artifacts
	python3 scripts/run_frontend_build.py

build-core: ## Run the shared build stage for local and CI workflows
	@echo "==> Running backend type checks"
	@$(MAKE) backend-types
	@echo "==> Running frontend type checks"
	@$(MAKE) frontend-types
	@echo "==> Building frontend"
	@$(MAKE) frontend-build

build: ## Run build-oriented checks
	@$(MAKE) build-core

backend-security: ## Run backend security checks
	python3 scripts/run_backend_bandit.py
	./scripts/run_backend_pip_audit.sh

repo-security: ## Run repository-wide security scans
	./scripts/run_trivy_fs.sh

security-core: ## Run the shared security stage for local and CI workflows
	@echo "==> Running backend security checks"
	@$(MAKE) backend-security
	@echo "==> Running repository security scans"
	@$(MAKE) repo-security

security: ## Run security checks required by the maximum template
	@$(MAKE) security-core

docker-build: ## Build template Docker targets
	./scripts/run_docker_builds.sh

ci: ## Run the full golden-master pipeline
	@echo "==> Running invariant checks"
	@$(MAKE) check-core
	@echo "==> Running lint pipeline"
	@$(MAKE) lint-core
	@echo "==> Running tests"
	@$(MAKE) test-core
	@echo "==> Running build-oriented checks"
	@$(MAKE) build-core
	@echo "==> Running security checks"
	@$(MAKE) security-core
	@echo "==> Building Docker targets"
	@$(MAKE) docker-build
