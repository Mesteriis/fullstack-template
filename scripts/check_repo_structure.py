from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REPOSITORY_SKELETON_DIRS = {
    "migrations": "max-template requires migrations/ as the canonical relational schema history root",
    "migrations/versions": "max-template requires migrations/versions for versioned Alembic revisions",
    "docker": "max-template requires docker/ for container runtime definitions",
    "docs/adr": "max-template requires docs/adr to keep decisions version-controlled",
    "docs/adr/architecture": "max-template requires architecture ADRs as a dedicated decision category",
    "docs/adr/product": "max-template requires product ADRs as a dedicated decision category",
    "docs/adr/engineering": "max-template requires engineering ADRs for template- and process-level decisions",
    "docs/frontend": "max-template requires docs/frontend for frontend architecture and UI-layer documentation",
    "docs/template": "max-template requires docs/template for self-describing template governance",
    "scripts": "max-template requires scripts/ for machine-enforced repository checks",
    "specs": "max-template requires specs/ because contracts are first-class artifacts",
    "specs/asyncapi": "max-template requires specs/asyncapi to define event contracts explicitly",
    "specs/jsonschema": "max-template requires specs/jsonschema for canonical schema artifacts",
    "specs/openapi": "max-template requires specs/openapi to define HTTP contracts explicitly",
    "src": "max-template requires src/ as the polyglot application root",
    "src/backend": "max-template requires src/backend as the canonical backend service root",
    "src/backend/api": "max-template requires src/backend/api for transport wiring",
    "src/backend/apps": "max-template requires src/backend/apps for bounded contexts",
    "src/backend/apps/system": "max-template requires a system bounded context scaffold",
    "src/backend/apps/system/api": "max-template requires api layer scaffold inside bounded contexts",
    "src/backend/apps/system/application": "max-template requires application layer scaffold inside bounded contexts",
    "src/backend/apps/system/contracts": "max-template requires contracts layer scaffold inside bounded contexts",
    "src/backend/apps/system/domain": "max-template requires domain layer scaffold inside bounded contexts",
    "src/backend/apps/system/infrastructure": "max-template requires infrastructure layer scaffold inside bounded contexts",
    "src/backend/core": "max-template requires src/backend/core for the shared platform kernel",
    "src/backend/core/bootstrap": "max-template requires src/backend/core/bootstrap for composition root wiring",
    "src/backend/core/db": "max-template requires src/backend/core/db for shared persistence primitives",
    "src/backend/core/observability": "max-template requires src/backend/core/observability for centralized tracing, metrics, logging and error tracking",
    "src/backend/core/settings": "max-template requires src/backend/core/settings for runtime configuration",
    "src/backend/runtime": "max-template requires src/backend/runtime for worker and orchestration runtime",
    "src/backend/runtime/orchestration": "max-template requires runtime/orchestration for broker and worker wiring",
    "src/backend/runtime/streams": "max-template requires runtime/streams for stream-processing primitives",
    "src/backend/tests": "max-template requires src/backend/tests for backend-local verification",
    "src/backend/tests/apps": "max-template requires backend tests to mirror bounded contexts",
    "src/backend/tests/apps/system": "max-template requires app-level tests for the system scaffold",
    "src/backend/tests/architecture": "max-template requires architecture tests as a first-class backend test layer",
    "src/backend/tests/core": "max-template requires core test scaffolding near backend ownership",
    "src/backend/tests/factories": "max-template requires shared backend test factories",
    "src/backend/tests/fixtures": "max-template requires shared backend test fixtures",
    "src/backend/tests/migrations": "max-template requires backend migration tests as a first-class verification layer",
    "src/backend/tests/runtime": "max-template requires runtime test scaffolding",
    "src/frontend": "max-template requires src/frontend as the canonical frontend app root",
    "src/frontend/app": "max-template requires app/ as part of the frontend scaffold",
    "src/frontend/entities": "max-template requires entities/ as part of the frontend scaffold",
    "src/frontend/features": "max-template requires features/ as part of the frontend scaffold",
    "src/frontend/pages": "max-template requires pages/ as part of the frontend scaffold",
    "src/frontend/shared": "max-template requires shared/ as part of the frontend scaffold",
    "src/frontend/shared/api": "max-template requires shared/api for typed client integration",
    "src/frontend/shared/api/generated": "max-template requires generated frontend API artifacts to live under shared/api/generated",
    "src/frontend/shared/assets": "max-template requires shared/assets for frontend asset ownership",
    "src/frontend/shared/config": "max-template requires shared/config for frontend runtime configuration",
    "src/frontend/shared/lib": "max-template requires shared/lib for low-level frontend helpers",
    "src/frontend/shared/ui": "max-template requires shared/ui for reusable interface primitives",
    "src/frontend/tests": "max-template requires src/frontend/tests for frontend-local verification",
    "src/frontend/tests/component": "max-template requires component test coverage scaffolding",
    "src/frontend/tests/unit": "max-template requires unit test coverage scaffolding",
    "tests": "max-template requires tests/ for cross-application verification",
    "tests/contract": "max-template requires tests/contract for contract-driven integration checks",
    "tests/e2e": "max-template requires tests/e2e for cross-app smoke scenarios",
}
REQUIRED_TOOLING_FILES = {
    ".aiassistant/rules/main.md": "max-template requires a global AI agent rule entrypoint",
    ".aiassistant/rules/10-adr-authoring.md": "max-template requires ADR authoring rules for automated agents",
    ".aiassistant/rules/20-repo-governance-and-ci.md": "max-template requires repository governance rules for automated agents",
    ".aiassistant/rules/30-backend-platform.md": "max-template requires backend platform rules for automated agents",
    ".aiassistant/rules/31-backend-apps-and-product-model.md": "max-template requires backend product-model rules for automated agents",
    ".aiassistant/rules/40-frontend.md": "max-template requires frontend rules for automated agents",
    ".aiassistant/rules/50-specs-and-contracts.md": "max-template requires contract-first rules for automated agents",
    ".pre-commit-config.yaml": "max-template requires pre-commit configuration as the local enforcement baseline",
    ".env.example": "max-template requires an example environment file for deterministic bootstrap",
    ".gitea/workflows/ci.yml": "max-template requires Gitea CI because dual-CI support is mandatory",
    ".github/dependabot.yml": "max-template requires dependency update automation",
    ".github/ISSUE_TEMPLATE/bug_report.yml": "max-template requires issue templates as part of governance baseline",
    ".github/ISSUE_TEMPLATE/config.yml": "max-template requires issue template configuration as part of governance baseline",
    ".github/ISSUE_TEMPLATE/feature_request.yml": "max-template requires issue templates as part of governance baseline",
    ".github/PULL_REQUEST_TEMPLATE.md": "max-template requires a PR template to enforce review expectations",
    ".github/workflows/ci.yml": "max-template requires GitHub CI because dual-CI support is mandatory",
    "CODEOWNERS": "max-template requires CODEOWNERS for repository accountability",
    "CONTRIBUTING.md": "max-template requires CONTRIBUTING.md to document the canonical workflow",
    "Makefile": "max-template requires a Makefile as the single DX entrypoint",
    "SECURITY.md": "max-template requires SECURITY.md for vulnerability handling expectations",
    "docker-compose.yml": "max-template requires a root docker-compose.yml to orchestrate the full local ensemble",
    "alembic.ini": "max-template requires alembic.ini in the repository root for migration orchestration",
    "docker/Dockerfile": "max-template requires a canonical multi-stage Dockerfile",
    "docker/entrypoints/backend.sh": "max-template requires backend container entrypoint orchestration",
    "docker/entrypoints/frontend.sh": "max-template requires frontend container entrypoint orchestration",
    "docker/nginx/default.conf": "max-template requires frontend runtime nginx configuration",
    "docker/runs/backend.sh": "max-template requires backend runtime launcher script",
    "docker/runs/frontend.sh": "max-template requires frontend runtime launcher script",
    "docs/adr/INDEX.md": "max-template requires an ADR reading map for humans and automated agents",
    "docs/adr/README.md": "max-template requires ADR root documentation",
    "docs/adr/architecture/README.md": "max-template requires architecture ADR index documentation",
    "docs/adr/architecture/0027-enforce-machine-validated-http-contract-parity-across-spec-backend-and-frontend.md": "max-template requires an ADR for machine-enforced spec/backend/frontend HTTP contract parity",
    "docs/adr/engineering/README.md": "max-template requires engineering ADR index documentation",
    "docs/adr/engineering/2000-centralize-template-metadata-and-self-consistency-checks.md": "max-template requires an engineering ADR for template metadata and self-validation",
    "docs/adr/product/README.md": "max-template requires product ADR index documentation",
    "docs/frontend/ui-layer.md": "max-template requires frontend UI-layer documentation to govern primitive usage and migration",
    "docs/template/PHILOSOPHY.md": "max-template requires PHILOSOPHY.md so the repository explains why strictness is architectural, not incidental",
    "migrations/env.py": "max-template requires Alembic environment wiring",
    "migrations/script.py.mako": "max-template requires Alembic revision template wiring",
    "scripts/check_adrs.py": "max-template requires ADR validation",
    "scripts/check_backend_architecture.py": "max-template requires backend architecture validation",
    "scripts/check_backend_observability.py": "max-template requires backend observability validation to forbid print and ad-hoc logging",
    "scripts/check_ci_symmetry.py": "max-template requires CI symmetry validation",
    "scripts/check_environment.py": "max-template requires environment validation for make doctor",
    "scripts/check_frontend_architecture.py": "max-template requires frontend architecture validation and UI-boundary enforcement",
    "scripts/check_http_contract_parity.py": "max-template requires machine-enforced HTTP contract parity checks for template-owned API surfaces",
    "scripts/generate_frontend_openapi_client.py": "max-template requires OpenAPI-driven frontend API generation for template-owned HTTP surfaces",
    "scripts/init_env.py": "max-template requires shared env bootstrap automation for deterministic local startup",
    "scripts/check_repo_structure.py": "max-template requires repository skeleton validation",
    "scripts/check_specs.py": "max-template requires contract placement validation",
    "scripts/check_template_consistency.py": "max-template requires self-consistency validation across Makefile, hooks and CI",
    "scripts/run_backend_bandit.py": "max-template requires backend security lint automation",
    "scripts/run_backend_deptry.py": "max-template requires dependency hygiene automation",
    "scripts/run_backend_eradicate.py": "max-template requires backend dead-code/comment hygiene automation",
    "scripts/run_backend_import_boundaries.py": "max-template requires import-boundary enforcement",
    "scripts/run_backend_lint.py": "max-template requires backend lint automation",
    "scripts/run_backend_lint_fix.py": "max-template requires backend autofix automation",
    "scripts/run_backend_pip_audit.sh": "max-template requires backend dependency audit automation",
    "scripts/run_backend_pyupgrade.py": "max-template requires Python modernisation automation",
    "scripts/run_backend_sync.py": "max-template requires deterministic backend dependency sync",
    "scripts/run_backend_tests.py": "max-template requires backend test automation",
    "scripts/run_backend_tryceratops.py": "max-template requires exception-style lint automation",
    "scripts/run_backend_types.py": "max-template requires backend type-check automation",
    "scripts/run_backend_xenon.py": "max-template requires complexity-budget enforcement",
    "scripts/run_docker_builds.sh": "max-template requires deterministic Docker target builds",
    "scripts/run_frontend_build.py": "max-template requires frontend build automation",
    "scripts/run_frontend_install.py": "max-template requires deterministic frontend dependency installation",
    "scripts/run_frontend_lint.py": "max-template requires frontend lint automation",
    "scripts/run_frontend_lint_fix.py": "max-template requires frontend autofix automation",
    "scripts/run_frontend_tests.py": "max-template requires frontend test automation",
    "scripts/run_frontend_types.py": "max-template requires frontend type-check automation",
    "scripts/run_hadolint.sh": "max-template requires Dockerfile lint automation",
    "scripts/run_shellcheck.sh": "max-template requires shell lint automation",
    "scripts/run_trivy_fs.sh": "max-template requires filesystem security scanning automation",
    "scripts/template_meta.py": "max-template requires a shared metadata loader to avoid script-level hardcodes",
    "specs/README.md": "max-template requires root contract documentation",
    "specs/openapi/README.md": "max-template requires OpenAPI contract documentation",
    "specs/openapi/platform.openapi.yaml": "max-template requires a canonical OpenAPI example, not just placeholders",
    "specs/asyncapi/README.md": "max-template requires AsyncAPI contract documentation",
    "specs/asyncapi/platform-events.asyncapi.yaml": "max-template requires a canonical AsyncAPI example, not just placeholders",
    "specs/jsonschema/README.md": "max-template requires JSON Schema documentation",
    "specs/jsonschema/artifact.schema.json": "max-template requires a canonical JSON Schema example, not just placeholders",
    "src/backend/main.py": "max-template requires a backend runtime entrypoint",
    "src/backend/Makefile": "max-template requires a backend-local Makefile for backend-owned developer workflows",
    "src/backend/README.md": "max-template requires backend-local onboarding near backend ownership",
    "src/backend/pyproject.toml": "max-template requires a backend-local Python manifest",
    "src/backend/docker-compose.yml": "max-template requires a backend-local docker-compose.yml for the backend service ensemble",
    "src/backend/tests/migrations/test_alembic.py": "max-template requires migration coverage based on pytest-alembic and Testcontainers PostgreSQL",
    "src/frontend/eslint.config.mjs": "max-template requires frontend lint configuration",
    "src/frontend/docker-compose.yml": "max-template requires a frontend-local docker-compose.yml for the frontend runtime shell",
    "src/frontend/Makefile": "max-template requires a frontend-local Makefile for frontend-owned developer workflows",
    "src/frontend/package.json": "max-template requires a frontend-local package manifest",
    "src/frontend/pnpm-lock.yaml": "max-template requires a committed pnpm lockfile",
    "src/frontend/shared/api/generated/platform-api.ts": "max-template requires committed generated frontend API artifacts for template-owned HTTP surfaces",
    "src/frontend/tests/unit/app-shell.spec.ts": "max-template requires an app shell unit test for the frontend scaffold",
    "template.meta.toml": "max-template requires template metadata as the single source of truth for script-level ownership constants",
}
FORBIDDEN_LEGACY_DIRS = {
    "src/backend/fullstack_template": "legacy nested backend namespace is forbidden; backend must stay flat at src/backend/*",
    "src/backend/application": "legacy flat backend/application layout is forbidden; bounded contexts own application code",
    "src/backend/domain": "legacy flat backend/domain layout is forbidden; bounded contexts own domain code",
    "src/backend/infrastructure": "legacy flat backend/infrastructure layout is forbidden; bounded contexts own infrastructure code",
    "src/backend/settings": "legacy flat backend/settings layout is forbidden; shared settings belong in src/backend/core/settings",
    "src/backend/tests/unit": "legacy backend/tests/unit layout is forbidden; tests must mirror bounded contexts and architectural areas",
}
FORBIDDEN_LEGACY_FILES = {
    "src/backend/__init__.py": "legacy backend package wrapper is forbidden; src/backend is a flat service root, not a namespace package",
}
FORBIDDEN_ROOT_MANIFESTS = {
    "pyproject.toml": "root-level Python manifests are forbidden because app-local manifests must stay next to the owning app",
    "uv.lock": "root-level Python lockfiles are forbidden because app-local manifests must stay next to the owning app",
    "package.json": "root-level frontend manifests are forbidden because app-local manifests must stay next to the owning app",
    "package-lock.json": "root-level npm lockfiles are forbidden because app-local manifests must stay next to the owning app",
}
RESERVED_PATHS = {
    "infra": "reserved for future IaC and deployment-level configuration only",
    "packages": "reserved for future shared or generated repo-wide code only",
}


def validate_required_paths(paths: dict[str, str], *, expect_dir: bool, errors: list[str]) -> None:
    path_kind = "directory" if expect_dir else "file"
    for rel_path, reason in paths.items():
        path = ROOT / rel_path
        exists = path.is_dir() if expect_dir else path.is_file()
        if not exists:
            errors.append(f"{reason}; required {path_kind} is missing: {rel_path}")


def validate_forbidden_paths(paths: dict[str, str], *, expect_dir: bool, errors: list[str]) -> None:
    path_kind = "directory" if expect_dir else "file"
    for rel_path, reason in paths.items():
        path = ROOT / rel_path
        exists = path.is_dir() if expect_dir else path.is_file()
        if exists:
            errors.append(f"{reason}; remove forbidden legacy {path_kind}: {rel_path}")


def validate_repository_skeleton(errors: list[str]) -> None:
    validate_required_paths(REPOSITORY_SKELETON_DIRS, expect_dir=True, errors=errors)


def validate_required_tooling(errors: list[str]) -> None:
    validate_required_paths(REQUIRED_TOOLING_FILES, expect_dir=False, errors=errors)


def validate_forbidden_legacy(errors: list[str]) -> None:
    validate_forbidden_paths(FORBIDDEN_ROOT_MANIFESTS, expect_dir=False, errors=errors)
    validate_forbidden_paths(FORBIDDEN_LEGACY_DIRS, expect_dir=True, errors=errors)
    validate_forbidden_paths(FORBIDDEN_LEGACY_FILES, expect_dir=False, errors=errors)


def validate_reserved_paths(errors: list[str]) -> None:
    for rel_path, reason in RESERVED_PATHS.items():
        path = ROOT / rel_path
        if path.exists() and not path.is_dir():
            errors.append(f"{reason}; reserved path must remain a directory when present: {rel_path}")


def main() -> int:
    errors: list[str] = []

    validate_repository_skeleton(errors)
    validate_required_tooling(errors)
    validate_forbidden_legacy(errors)
    validate_reserved_paths(errors)

    if errors:
        for error in errors:
            print(error)
        return 1

    print("Repository structure validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
