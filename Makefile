.DEFAULT_GOAL := help

.PHONY: help \
	backend-sync frontend-install install-hooks bootstrap \
	check check-environment doctor \
	backend-fix frontend-fix fix \
	backend-lint frontend-lint repo-lint lint \
	backend-types frontend-types \
	backend-test frontend-test test \
	frontend-build build \
	backend-security repo-security security \
	docker-build ci

help: ## Print available commands
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "%-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

backend-sync: ## Sync backend dependencies
	python3 scripts/run_backend_sync.py

frontend-install: ## Install frontend dependencies
	python3 scripts/run_frontend_install.py

install-hooks: ## Install pre-commit and pre-push hooks
	cd src/backend && uv run pre-commit install --install-hooks && uv run pre-commit install --hook-type pre-push --install-hooks

bootstrap: ## Sync dependencies and install repository hooks
	@echo "==> Syncing backend dependencies"
	python3 scripts/run_backend_sync.py
	@echo "==> Installing frontend dependencies"
	python3 scripts/run_frontend_install.py
	@echo "==> Installing git hooks"
	cd src/backend && uv run pre-commit install --install-hooks && uv run pre-commit install --hook-type pre-push --install-hooks

check-environment: ## Validate required local tooling
	python3 scripts/check_environment.py

check: ## Run repository invariants
	python3 scripts/check_adrs.py
	python3 scripts/check_repo_structure.py
	python3 scripts/check_backend_architecture.py
	python3 scripts/check_specs.py
	python3 scripts/check_template_consistency.py
	python3 scripts/check_ci_symmetry.py

doctor: ## Validate environment and core template invariants
	@echo "==> Validating local toolchain"
	python3 scripts/check_environment.py
	@echo "==> Validating repository skeleton, ADRs and architecture"
	python3 scripts/check_adrs.py
	python3 scripts/check_repo_structure.py
	python3 scripts/check_backend_architecture.py
	python3 scripts/check_specs.py
	python3 scripts/check_template_consistency.py
	python3 scripts/check_ci_symmetry.py
	@echo "Doctor completed successfully."

backend-fix: ## Run backend autofixers
	python3 scripts/run_backend_lint_fix.py
	python3 scripts/run_backend_pyupgrade.py
	python3 scripts/run_backend_eradicate.py

frontend-fix: ## Run frontend autofixers
	python3 scripts/run_frontend_lint_fix.py

fix: ## Run all autofixers
	@echo "==> Fixing backend sources"
	python3 scripts/run_backend_lint_fix.py
	python3 scripts/run_backend_pyupgrade.py
	python3 scripts/run_backend_eradicate.py
	@echo "==> Fixing frontend sources"
	python3 scripts/run_frontend_lint_fix.py

backend-lint: ## Run backend lint pipeline
	python3 scripts/run_backend_lint.py
	python3 scripts/run_backend_import_boundaries.py
	python3 scripts/run_backend_deptry.py
	python3 scripts/run_backend_tryceratops.py
	python3 scripts/run_backend_xenon.py

frontend-lint: ## Run frontend lint pipeline
	python3 scripts/run_frontend_lint.py

repo-lint: ## Run shell and Dockerfile lint checks
	./scripts/run_shellcheck.sh
	./scripts/run_hadolint.sh

lint: ## Run full lint pipeline
	@echo "==> Linting backend"
	python3 scripts/run_backend_lint.py
	python3 scripts/run_backend_import_boundaries.py
	python3 scripts/run_backend_deptry.py
	python3 scripts/run_backend_tryceratops.py
	python3 scripts/run_backend_xenon.py
	@echo "==> Linting frontend"
	python3 scripts/run_frontend_lint.py
	@echo "==> Linting repository assets"
	./scripts/run_shellcheck.sh
	./scripts/run_hadolint.sh

backend-types: ## Run backend type checks
	python3 scripts/run_backend_types.py

frontend-types: ## Run frontend type checks
	python3 scripts/run_frontend_types.py

backend-test: ## Run backend tests
	python3 scripts/run_backend_tests.py

frontend-test: ## Run frontend tests
	python3 scripts/run_frontend_tests.py

test: ## Run full test pipeline
	@echo "==> Testing backend"
	python3 scripts/run_backend_tests.py
	@echo "==> Testing frontend"
	python3 scripts/run_frontend_tests.py

frontend-build: ## Build frontend artifacts
	python3 scripts/run_frontend_build.py

build: ## Run build-oriented checks
	@echo "==> Running backend type checks"
	python3 scripts/run_backend_types.py
	@echo "==> Running frontend type checks"
	python3 scripts/run_frontend_types.py
	@echo "==> Building frontend"
	python3 scripts/run_frontend_build.py

backend-security: ## Run backend security checks
	python3 scripts/run_backend_bandit.py
	./scripts/run_backend_pip_audit.sh

repo-security: ## Run repository-wide security scans
	./scripts/run_trivy_fs.sh

security: ## Run security checks required by the maximum template
	@echo "==> Running backend security checks"
	python3 scripts/run_backend_bandit.py
	./scripts/run_backend_pip_audit.sh
	@echo "==> Running repository security scans"
	./scripts/run_trivy_fs.sh

docker-build: ## Build template Docker targets
	./scripts/run_docker_builds.sh

ci: ## Run the full golden-master pipeline
	@echo "==> Running invariant checks"
	python3 scripts/check_adrs.py
	python3 scripts/check_repo_structure.py
	python3 scripts/check_backend_architecture.py
	python3 scripts/check_specs.py
	python3 scripts/check_template_consistency.py
	python3 scripts/check_ci_symmetry.py
	@echo "==> Running lint pipeline"
	python3 scripts/run_backend_lint.py
	python3 scripts/run_backend_import_boundaries.py
	python3 scripts/run_backend_deptry.py
	python3 scripts/run_backend_tryceratops.py
	python3 scripts/run_backend_xenon.py
	python3 scripts/run_frontend_lint.py
	./scripts/run_shellcheck.sh
	./scripts/run_hadolint.sh
	@echo "==> Running tests"
	python3 scripts/run_backend_tests.py
	python3 scripts/run_frontend_tests.py
	@echo "==> Running build-oriented checks"
	python3 scripts/run_backend_types.py
	python3 scripts/run_frontend_types.py
	python3 scripts/run_frontend_build.py
	@echo "==> Running security checks"
	python3 scripts/run_backend_bandit.py
	./scripts/run_backend_pip_audit.sh
	./scripts/run_trivy_fs.sh
	@echo "==> Building Docker targets"
	./scripts/run_docker_builds.sh
