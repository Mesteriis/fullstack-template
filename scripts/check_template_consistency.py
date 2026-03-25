from __future__ import annotations

import re
import sys
from pathlib import Path

from template_meta import load_template_meta


ROOT = Path(__file__).resolve().parent.parent
MAKEFILE_PATH = ROOT / "Makefile"
PRE_COMMIT_PATH = ROOT / ".pre-commit-config.yaml"
WORKFLOW_PATHS = [
    ROOT / ".github" / "workflows" / "ci.yml",
    ROOT / ".gitea" / "workflows" / "ci.yml",
]
DOCKERFILE_PATH = ROOT / "docker" / "Dockerfile"
REQUIRED_TARGETS = {
    "help",
    "bootstrap",
    "doctor",
    "fix",
    "ci",
    "check",
    "lint",
    "test",
    "build",
    "docker-build",
}
REQUIRED_SCRIPTS = {
    "scripts/check_adrs.py",
    "scripts/check_backend_architecture.py",
    "scripts/check_ci_symmetry.py",
    "scripts/check_environment.py",
    "scripts/check_repo_structure.py",
    "scripts/check_specs.py",
    "scripts/check_template_consistency.py",
    "scripts/run_backend_bandit.py",
    "scripts/run_backend_deptry.py",
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
    "scripts/run_frontend_build.py",
    "scripts/run_frontend_install.py",
    "scripts/run_frontend_lint.py",
    "scripts/run_frontend_lint_fix.py",
    "scripts/run_frontend_tests.py",
    "scripts/run_frontend_types.py",
    "scripts/run_hadolint.sh",
    "scripts/run_shellcheck.sh",
    "scripts/run_trivy_fs.sh",
}
PLACEHOLDER_NAMES = {".gitkeep", "README.md"}


def parse_makefile_targets() -> dict[str, list[str]]:
    targets: dict[str, list[str]] = {}
    current_target: str | None = None

    for raw_line in MAKEFILE_PATH.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith("\t") and current_target is not None:
            targets[current_target].append(raw_line.strip())
            continue

        target_match = re.match(r"^([A-Za-z0-9_.-]+):(?:\s|$)", raw_line)
        if target_match and not raw_line.startswith("."):
            current_target = target_match.group(1)
            targets.setdefault(current_target, [])
            continue

        current_target = None

    return targets


def parse_docker_targets() -> set[str]:
    return {
        match.group(1)
        for match in re.finditer(r"^FROM\s+.+\s+AS\s+([A-Za-z0-9_-]+)$", DOCKERFILE_PATH.read_text(encoding="utf-8"), re.MULTILINE)
    }


def extract_script_references(text: str) -> set[str]:
    script_paths = set(re.findall(r"(?:python3|python)\s+(scripts/[A-Za-z0-9_./-]+)", text))
    script_paths.update(re.findall(r"\./(scripts/[A-Za-z0-9_./-]+)", text))
    return script_paths


def extract_make_references(text: str) -> set[str]:
    targets: set[str] = set()
    for match in re.finditer(r"(?:^|\s)(?:make|\$\(MAKE\))\s+([A-Za-z0-9_.-]+)", text):
        target = match.group(1)
        if not target.startswith("-"):
            targets.add(target)
    return targets


def extract_docker_target_references(text: str) -> set[str]:
    return set(re.findall(r"--target\s+([A-Za-z0-9_-]+)", text))


def main() -> int:
    template_meta = load_template_meta()
    errors: list[str] = []

    make_targets = parse_makefile_targets()
    docker_targets = parse_docker_targets()

    missing_targets = sorted(REQUIRED_TARGETS - make_targets.keys())
    if missing_targets:
        errors.append(
            "Makefile is missing required golden-master targets: " + ", ".join(missing_targets)
        )

    for rel_path in sorted(REQUIRED_SCRIPTS):
        if not (ROOT / rel_path).is_file():
            errors.append(f"required template script is missing: {rel_path}")

    makefile_text = MAKEFILE_PATH.read_text(encoding="utf-8")
    for script_path in sorted(extract_script_references(makefile_text)):
        if not (ROOT / script_path).is_file():
            errors.append(f"Makefile references missing script: {script_path}")

    for target in sorted(extract_make_references(makefile_text)):
        if target not in make_targets:
            errors.append(f"Makefile references undefined nested target: {target}")

    for docker_target in sorted(extract_docker_target_references(makefile_text)):
        if docker_target not in docker_targets:
            errors.append(f"Makefile references undefined docker target: {docker_target}")

    pre_commit_text = PRE_COMMIT_PATH.read_text(encoding="utf-8")
    for script_path in sorted(extract_script_references(pre_commit_text)):
        if not (ROOT / script_path).is_file():
            errors.append(f"pre-commit hook references missing script: {script_path}")

    for workflow_path in WORKFLOW_PATHS:
        workflow_text = workflow_path.read_text(encoding="utf-8")

        for script_path in sorted(extract_script_references(workflow_text)):
            if not (ROOT / script_path).is_file():
                errors.append(f"{workflow_path.relative_to(ROOT)} references missing script: {script_path}")

        for target in sorted(extract_make_references(workflow_text)):
            if target not in make_targets:
                errors.append(f"{workflow_path.relative_to(ROOT)} references undefined Make target: {target}")

        for docker_target in sorted(extract_docker_target_references(workflow_text)):
            if docker_target not in docker_targets:
                errors.append(f"{workflow_path.relative_to(ROOT)} references undefined docker target: {docker_target}")

    owner_token = f"@{template_meta.owner}"
    codeowners_text = (ROOT / "CODEOWNERS").read_text(encoding="utf-8")
    if owner_token not in codeowners_text:
        errors.append(
            f"CODEOWNERS must contain '{owner_token}' to stay aligned with template.meta.toml owner"
        )

    for family in ("openapi", "asyncapi", "jsonschema"):
        family_root = ROOT / "specs" / family
        concrete_specs = [
            path
            for path in family_root.iterdir()
            if path.is_file() and path.name not in PLACEHOLDER_NAMES
        ]
        if not concrete_specs:
            errors.append(
                f"specs/{family} contains placeholders only; max-template requires at least one canonical contract example"
            )

    if errors:
        for error in errors:
            print(error)
        return 1

    print(
        "Template consistency validation passed for "
        f"{template_meta.template_type} owned by {template_meta.owner}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
