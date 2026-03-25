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
CORE_STAGES = {
    "check",
    "backend-lint",
    "backend-test",
    "docker-build",
}
EXTENDED_STAGES = {
    "frontend-lint",
    "frontend-test",
    "frontend-build",
}
SUPPORTING_STAGES = {
    "backend-types",
    "backend-security",
    "frontend-types",
    "repo-lint",
    "repo-security",
}


def active_text(path: Path) -> str:
    return "\n".join(
        line for line in path.read_text(encoding="utf-8").splitlines() if not line.lstrip().startswith("#")
    )


def detect_stages(path: Path) -> set[str]:
    content = active_text(path)
    stages: set[str] = set()
    for stage_name, patterns in SEMANTIC_STAGES.items():
        if any(re.search(pattern, content) for pattern in patterns):
            stages.add(stage_name)
    return stages


def validate_core_stages(workflow_path: Path, stages: set[str], errors: list[str]) -> None:
    missing_core = sorted(CORE_STAGES - stages)
    if missing_core:
        errors.append(
            f"{workflow_path.relative_to(ROOT)} is missing required core stages: {', '.join(missing_core)}. "
            "Core stages are mandatory for every CI implementation of the master template."
        )


def validate_extended_stages(github_stages: set[str], gitea_stages: set[str], errors: list[str]) -> None:
    github_extended = github_stages & EXTENDED_STAGES
    gitea_extended = gitea_stages & EXTENDED_STAGES

    if not github_extended and not gitea_extended:
        return

    missing_github = sorted(EXTENDED_STAGES - github_extended)
    missing_gitea = sorted(EXTENDED_STAGES - gitea_extended)
    if missing_github:
        errors.append(
            f"{GITHUB_CI.relative_to(ROOT)} has an incomplete fullstack stage set and is missing: {', '.join(missing_github)}. "
            "Once frontend stages exist, the full extended set must remain intact."
        )
    if missing_gitea:
        errors.append(
            f"{GITEA_CI.relative_to(ROOT)} has an incomplete fullstack stage set and is missing: {', '.join(missing_gitea)}. "
            "Once frontend stages exist, the full extended set must remain intact."
        )

    if github_extended != gitea_extended:
        errors.append(
            f"Frontend/fullstack stage symmetry drift detected: GitHub has {sorted(github_extended)} while Gitea has {sorted(gitea_extended)}. "
            "Extended stages must match across CI implementations when present."
        )


def validate_supporting_stages(github_stages: set[str], gitea_stages: set[str], errors: list[str]) -> None:
    github_supporting = github_stages & SUPPORTING_STAGES
    gitea_supporting = gitea_stages & SUPPORTING_STAGES

    if github_supporting != gitea_supporting:
        errors.append(
            f"Supporting CI stage drift detected: GitHub has {sorted(github_supporting)} while Gitea has {sorted(gitea_supporting)}. "
            "Non-core quality and security stages must not silently diverge."
        )


def main() -> int:
    errors: list[str] = []
    github_stages = detect_stages(GITHUB_CI)
    gitea_stages = detect_stages(GITEA_CI)

    validate_core_stages(GITHUB_CI, github_stages, errors)
    validate_core_stages(GITEA_CI, gitea_stages, errors)
    validate_extended_stages(github_stages, gitea_stages, errors)
    validate_supporting_stages(github_stages, gitea_stages, errors)

    if errors:
        for error in errors:
            print(error)
        return 1

    print("CI symmetry validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
