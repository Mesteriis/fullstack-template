from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
GITHUB_CI = ROOT / ".github" / "workflows" / "ci.yml"
GITEA_CI = ROOT / ".gitea" / "workflows" / "ci.yml"
SEMANTIC_STAGES = {
    "check": [
        r"\bmake check\b",
        r"check_adrs\.py",
        r"check_repo_structure\.py",
        r"check_backend_architecture\.py",
        r"check_specs\.py",
        r"check_template_consistency\.py",
        r"check_ci_symmetry\.py",
    ],
    "backend-lint": [
        r"\bmake backend-lint\b",
        r"ruff check",
        r"lint-imports",
        r"deptry",
        r"tryceratops",
        r"xenon",
    ],
    "backend-types": [
        r"\bmake backend-types\b",
        r"\bmypy\b",
    ],
    "backend-test": [
        r"\bmake backend-test\b",
        r"pytest -x -q",
    ],
    "backend-security": [
        r"\bmake backend-security\b",
        r"\bbandit\b",
        r"pip-audit",
    ],
    "frontend-lint": [
        r"\bmake frontend-lint\b",
        r"pnpm lint",
    ],
    "frontend-types": [
        r"\bmake frontend-types\b",
        r"pnpm type-check",
    ],
    "frontend-test": [
        r"\bmake frontend-test\b",
        r"pnpm test:unit",
    ],
    "frontend-build": [
        r"\bmake frontend-build\b",
        r"pnpm build",
    ],
    "repo-lint": [
        r"\bmake repo-lint\b",
        r"shellcheck",
        r"hadolint",
    ],
    "repo-security": [
        r"\bmake repo-security\b",
        r"trivy",
    ],
    "docker-build": [
        r"\bmake docker-build\b",
        r"docker build -f docker/Dockerfile --target backend",
        r"docker build -f docker/Dockerfile --target frontend",
    ],
}
REQUIRED_MAJOR_STAGES = {
    "check",
    "backend-lint",
    "backend-test",
    "frontend-lint",
    "frontend-test",
    "frontend-build",
    "docker-build",
}


def detect_stages(path: Path) -> set[str]:
    content = path.read_text(encoding="utf-8")
    stages: set[str] = set()
    for stage_name, patterns in SEMANTIC_STAGES.items():
        if any(re.search(pattern, content) for pattern in patterns):
            stages.add(stage_name)
    return stages


def main() -> int:
    errors: list[str] = []
    github_stages = detect_stages(GITHUB_CI)
    gitea_stages = detect_stages(GITEA_CI)

    for workflow_name, stages in (
        (GITHUB_CI.relative_to(ROOT), github_stages),
        (GITEA_CI.relative_to(ROOT), gitea_stages),
    ):
        missing = sorted(REQUIRED_MAJOR_STAGES - stages)
        if missing:
            errors.append(
                f"{workflow_name} is missing required semantic stages: {', '.join(missing)}"
            )

    github_only = sorted(github_stages - gitea_stages)
    if github_only:
        errors.append(
            f"{GITHUB_CI.relative_to(ROOT)} defines semantic stages absent from Gitea CI: {', '.join(github_only)}"
        )

    gitea_only = sorted(gitea_stages - github_stages)
    if gitea_only:
        errors.append(
            f"{GITEA_CI.relative_to(ROOT)} defines semantic stages absent from GitHub CI: {', '.join(gitea_only)}"
        )

    if errors:
        for error in errors:
            print(error)
        return 1

    print("CI symmetry validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
