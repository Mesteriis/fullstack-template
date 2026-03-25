from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REQUIRED_DIRS = [
    "migrations",
    "migrations/versions",
    "docker",
    "docs/adr",
    "docs/adr/architecture",
    "docs/adr/product",
    "scripts",
    "specs",
    "specs/asyncapi",
    "specs/jsonschema",
    "specs/openapi",
    "src",
    "src/backend",
    "src/backend/api",
    "src/backend/apps",
    "src/backend/apps/system",
    "src/backend/apps/system/api",
    "src/backend/apps/system/application",
    "src/backend/apps/system/contracts",
    "src/backend/apps/system/domain",
    "src/backend/apps/system/infrastructure",
    "src/backend/core",
    "src/backend/core/bootstrap",
    "src/backend/core/db",
    "src/backend/core/settings",
    "src/backend/runtime",
    "src/backend/runtime/orchestration",
    "src/backend/runtime/streams",
    "src/backend/tests",
    "src/backend/tests/apps",
    "src/backend/tests/apps/system",
    "src/backend/tests/architecture",
    "src/backend/tests/core",
    "src/backend/tests/factories",
    "src/backend/tests/fixtures",
    "src/backend/tests/runtime",
    "src/frontend",
    "src/frontend/app",
    "src/frontend/entities",
    "src/frontend/features",
    "src/frontend/pages",
    "src/frontend/shared",
    "src/frontend/shared/api",
    "src/frontend/shared/assets",
    "src/frontend/shared/config",
    "src/frontend/shared/lib",
    "src/frontend/shared/ui",
    "src/frontend/tests",
    "src/frontend/tests/component",
    "src/frontend/tests/unit",
    "tests",
    "tests/contract",
    "tests/e2e",
]
REQUIRED_FILES = [
    ".aiassistant/rules/main.md",
    ".aiassistant/rules/10-adr-authoring.md",
    ".aiassistant/rules/20-repo-governance-and-ci.md",
    ".aiassistant/rules/30-backend-platform.md",
    ".aiassistant/rules/31-backend-apps-and-product-model.md",
    ".aiassistant/rules/40-frontend.md",
    ".aiassistant/rules/50-specs-and-contracts.md",
    ".pre-commit-config.yaml",
    ".env.example",
    ".gitea/workflows/ci.yml",
    ".github/dependabot.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/workflows/ci.yml",
    "CODEOWNERS",
    "CONTRIBUTING.md",
    "Makefile",
    "SECURITY.md",
    "alembic.ini",
    "docker/Dockerfile",
    "docker/entrypoints/backend.sh",
    "docker/entrypoints/frontend.sh",
    "docker/nginx/default.conf",
    "docker/runs/backend.sh",
    "docker/runs/frontend.sh",
    "docs/adr/INDEX.md",
    "docs/adr/README.md",
    "docs/adr/architecture/README.md",
    "docs/adr/product/README.md",
    "migrations/env.py",
    "migrations/script.py.mako",
    "scripts/check_backend_architecture.py",
    "scripts/run_backend_bandit.py",
    "scripts/run_backend_deptry.py",
    "scripts/run_backend_eradicate.py",
    "scripts/run_backend_import_boundaries.py",
    "scripts/run_backend_lint.py",
    "scripts/run_backend_lint_fix.py",
    "scripts/run_backend_pip_audit.sh",
    "scripts/run_backend_pyupgrade.py",
    "scripts/run_backend_sync.py",
    "scripts/run_backend_tests.py",
    "scripts/run_backend_tryceratops.py",
    "scripts/run_backend_types.py",
    "scripts/run_backend_xenon.py",
    "scripts/run_docker_builds.sh",
    "scripts/check_specs.py",
    "scripts/run_frontend_install.py",
    "scripts/run_frontend_lint.py",
    "scripts/run_frontend_lint_fix.py",
    "scripts/run_frontend_build.py",
    "scripts/run_frontend_tests.py",
    "scripts/run_frontend_types.py",
    "scripts/run_hadolint.sh",
    "scripts/run_shellcheck.sh",
    "scripts/run_trivy_fs.sh",
    "specs/README.md",
    "specs/openapi/README.md",
    "specs/asyncapi/README.md",
    "specs/jsonschema/README.md",
    "src/backend/main.py",
    "src/backend/pyproject.toml",
    "src/frontend/eslint.config.mjs",
    "src/frontend/package.json",
    "src/frontend/pnpm-lock.yaml",
    "src/frontend/tests/unit/App.spec.ts",
]
FORBIDDEN_ROOT_FILES = [
    "pyproject.toml",
    "uv.lock",
    "package.json",
    "package-lock.json",
]
FORBIDDEN_DIRS = [
    "src/backend/registries",
    "src/backend/application",
    "src/backend/domain",
    "src/backend/infrastructure",
    "src/backend/settings",
    "src/backend/tests/unit",
]
FORBIDDEN_FILES = [
    "src/backend/__init__.py",
]
OPTIONAL_DIRS = [
    "infra",
    "packages",
]


def main() -> int:
    errors: list[str] = []

    for rel_path in REQUIRED_DIRS:
        path = ROOT / rel_path
        if not path.is_dir():
            errors.append(f"missing required directory: {rel_path}")

    for rel_path in REQUIRED_FILES:
        path = ROOT / rel_path
        if not path.is_file():
            errors.append(f"missing required file: {rel_path}")

    for rel_path in FORBIDDEN_ROOT_FILES:
        path = ROOT / rel_path
        if path.exists():
            errors.append(f"root-level manifest is not allowed here: {rel_path}")

    for rel_path in FORBIDDEN_DIRS:
        path = ROOT / rel_path
        if path.exists():
            errors.append(f"forbidden legacy directory still exists: {rel_path}")

    for rel_path in FORBIDDEN_FILES:
        path = ROOT / rel_path
        if path.exists():
            errors.append(f"forbidden legacy file still exists: {rel_path}")

    for rel_path in OPTIONAL_DIRS:
        path = ROOT / rel_path
        if path.exists() and not path.is_dir():
            errors.append(f"optional reserved path must be a directory when present: {rel_path}")

    if errors:
        for error in errors:
            print(error)
        return 1

    print("Repository structure validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
