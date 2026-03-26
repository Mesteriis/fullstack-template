from __future__ import annotations

import ast
import re
import shlex
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
SCRIPTS_ROOT = ROOT / "scripts"
REQUIRED_TARGETS = {
    "help",
    "bootstrap",
    "init-env",
    "doctor",
    "fix",
    "check",
    "check-core",
    "lint",
    "lint-core",
    "test",
    "test-core",
    "build",
    "build-core",
    "security",
    "security-core",
    "ci",
    "docker-build",
    "compose-up",
    "compose-down",
}
REQUIRED_SCRIPTS = {
    "scripts/check_adrs.py",
    "scripts/check_backend_architecture.py",
    "scripts/check_backend_observability.py",
    "scripts/check_ci_symmetry.py",
    "scripts/check_environment.py",
    "scripts/check_frontend_architecture.py",
    "scripts/check_http_contract_parity.py",
    "scripts/generate_frontend_openapi_client.py",
    "scripts/init_env.py",
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
SCRIPT_PATH_PATTERN = re.compile(r"(?:^|[\s\"'=])(?:\./)?(scripts/[A-Za-z0-9_./-]+\.(?:py|sh))(?=$|[\s\"'])")
DOCKER_TARGET_PATTERN = re.compile(r"--target\s+([A-Za-z0-9_-]+)")
TARGET_DEFINITION_PATTERN = re.compile(r"^([A-Za-z0-9_.\-/ ]+):(?!=)")


def iter_active_lines(text: str) -> list[str]:
    return [line.rstrip("\n") for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalize_script_path(raw_path: str) -> str | None:
    candidate = raw_path.strip().strip("\"'")
    if candidate.startswith("./"):
        candidate = candidate[2:]

    relative_path = Path(candidate)
    if relative_path.is_absolute():
        return None

    normalized_path = (ROOT / relative_path).resolve()
    try:
        normalized_relative = normalized_path.relative_to(ROOT).as_posix()
    except ValueError:
        return None

    if not normalized_relative.startswith("scripts/"):
        return None
    return normalized_relative


def collapse_makefile_lines(text: str) -> list[str]:
    logical_lines: list[str] = []
    buffer = ""

    for raw_line in text.splitlines():
        if raw_line.lstrip().startswith("#"):
            continue

        if raw_line.startswith("\t"):
            if buffer:
                logical_lines.append(buffer)
                buffer = ""
            logical_lines.append(raw_line.rstrip())
            continue

        line = raw_line.rstrip()
        if not line:
            if buffer:
                logical_lines.append(buffer)
                buffer = ""
            continue

        if buffer:
            buffer = f"{buffer} {line.lstrip()}"
        else:
            buffer = line

        if buffer.endswith("\\"):
            buffer = buffer[:-1].rstrip()
            continue

        logical_lines.append(buffer)
        buffer = ""

    if buffer:
        logical_lines.append(buffer)
    return logical_lines


def parse_makefile_targets() -> dict[str, list[str]]:
    targets: dict[str, list[str]] = {}
    current_targets: list[str] = []

    for line in collapse_makefile_lines(read_text(MAKEFILE_PATH)):
        if line.startswith("\t"):
            if current_targets:
                command = line.strip()
                for target in current_targets:
                    targets[target].append(command)
            continue

        current_targets = []
        if line.startswith("."):
            continue

        target_match = TARGET_DEFINITION_PATTERN.match(line)
        if not target_match:
            continue

        target_names = [target for target in target_match.group(1).split() if target]
        if not target_names:
            continue

        current_targets = target_names
        for target in current_targets:
            targets.setdefault(target, [])

    return targets


def parse_docker_targets() -> set[str]:
    return {
        match.group(1)
        for match in re.finditer(r"^FROM\s+.+\s+AS\s+([A-Za-z0-9_-]+)$", read_text(DOCKERFILE_PATH), re.MULTILINE)
    }


def extract_script_references(text: str) -> set[str]:
    script_paths: set[str] = set()
    for line in iter_active_lines(text):
        for match in SCRIPT_PATH_PATTERN.finditer(line):
            normalized_path = normalize_script_path(match.group(1))
            if normalized_path is not None:
                script_paths.add(normalized_path)
    return script_paths


def extract_make_references(text: str) -> set[str]:
    targets: set[str] = set()
    for line in iter_active_lines(text):
        try:
            tokens = shlex.split(line, comments=True, posix=True)
        except ValueError:
            tokens = line.split()

        for index, token in enumerate(tokens):
            normalized_token = token.lstrip("@-+")
            if normalized_token not in {"make", "$(MAKE)"}:
                continue
            for candidate in tokens[index + 1 :]:
                if candidate.startswith("-"):
                    continue
                targets.add(candidate)
                break
    return targets


def extract_docker_target_references(text: str) -> set[str]:
    docker_targets: set[str] = set()
    for line in iter_active_lines(text):
        docker_targets.update(DOCKER_TARGET_PATTERN.findall(line))
    return docker_targets


def collect_script_import_references() -> set[str]:
    module_to_path = {
        script_path.stem: script_path.relative_to(ROOT).as_posix()
        for script_path in sorted(SCRIPTS_ROOT.glob("*.py"))
    }
    referenced_scripts: set[str] = set()

    for script_path in sorted(SCRIPTS_ROOT.glob("*.py")):
        tree = ast.parse(script_path.read_text(encoding="utf-8"), filename=str(script_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in module_to_path:
                        referenced_scripts.add(module_to_path[alias.name])
            if isinstance(node, ast.ImportFrom) and node.module in module_to_path:
                referenced_scripts.add(module_to_path[node.module])

    return referenced_scripts


def collect_all_script_paths() -> set[str]:
    return {
        script_path.relative_to(ROOT).as_posix()
        for script_path in SCRIPTS_ROOT.iterdir()
        if script_path.is_file() and script_path.suffix in {".py", ".sh"}
    }


def validate_required_targets(make_targets: dict[str, list[str]], errors: list[str]) -> None:
    missing_targets = sorted(REQUIRED_TARGETS - make_targets.keys())
    if missing_targets:
        errors.append(
            "Makefile is missing required golden-master targets: "
            + ", ".join(missing_targets)
            + ". These targets are the canonical orchestration surface for local DX and CI."
        )


def validate_required_scripts(errors: list[str]) -> None:
    for rel_path in sorted(REQUIRED_SCRIPTS):
        if not (ROOT / rel_path).is_file():
            errors.append(
                f"Required template script is missing: {rel_path}. "
                "Golden-master validation depends on every declared control script being present."
            )


def validate_script_references(source_path: Path, text: str, errors: list[str]) -> set[str]:
    referenced_scripts = extract_script_references(text)
    for script_path in sorted(referenced_scripts):
        if not (ROOT / script_path).is_file():
            errors.append(
                f"{source_path.relative_to(ROOT)} references missing script '{script_path}'. "
                "Automation surfaces must point to real files or the template drifts silently."
            )
    return referenced_scripts


def validate_make_references(source_path: Path, text: str, make_targets: dict[str, list[str]], errors: list[str]) -> set[str]:
    referenced_targets = extract_make_references(text)
    for target in sorted(referenced_targets):
        if target not in make_targets:
            errors.append(
                f"{source_path.relative_to(ROOT)} calls undefined Make target '{target}'. "
                "Nested orchestration must resolve to real targets to keep pipelines deterministic."
            )
    return referenced_targets


def validate_docker_target_references(source_path: Path, text: str, docker_targets: set[str], errors: list[str]) -> None:
    for docker_target in sorted(extract_docker_target_references(text)):
        if docker_target not in docker_targets:
            errors.append(
                f"{source_path.relative_to(ROOT)} references undefined Docker target '{docker_target}'. "
                "Image build automation must track real multi-stage targets."
            )


def validate_codeowners(template_owner: str, errors: list[str]) -> None:
    owner_token = f"@{template_owner}"
    codeowners_text = read_text(ROOT / "CODEOWNERS")
    if owner_token not in codeowners_text:
        errors.append(
            f"CODEOWNERS must contain '{owner_token}'. Repository accountability must stay aligned with template.meta.toml."
        )


def validate_spec_families(errors: list[str]) -> None:
    for family in ("openapi", "asyncapi", "jsonschema"):
        family_root = ROOT / "specs" / family
        concrete_specs = [
            path
            for path in family_root.iterdir()
            if path.is_file() and path.name not in PLACEHOLDER_NAMES
        ]
        if not concrete_specs:
            errors.append(
                f"specs/{family} contains placeholders only. "
                "The maximum template requires at least one concrete contract example per spec family."
            )


def validate_orphan_scripts(referenced_scripts: set[str], errors: list[str]) -> None:
    orphan_scripts = sorted(collect_all_script_paths() - referenced_scripts)
    if orphan_scripts:
        errors.append(
            "Orphan scripts detected: "
            + ", ".join(orphan_scripts)
            + ". Every script in scripts/ must be wired into Makefile, hooks, CI or another script to avoid dead policy paths."
        )


def main() -> int:
    template_meta = load_template_meta()
    errors: list[str] = []

    make_targets = parse_makefile_targets()
    docker_targets = parse_docker_targets()
    referenced_scripts: set[str] = set()

    validate_required_targets(make_targets, errors)
    validate_required_scripts(errors)

    makefile_text = read_text(MAKEFILE_PATH)
    referenced_scripts.update(validate_script_references(MAKEFILE_PATH, makefile_text, errors))
    validate_make_references(MAKEFILE_PATH, makefile_text, make_targets, errors)
    validate_docker_target_references(MAKEFILE_PATH, makefile_text, docker_targets, errors)

    pre_commit_text = read_text(PRE_COMMIT_PATH)
    referenced_scripts.update(validate_script_references(PRE_COMMIT_PATH, pre_commit_text, errors))

    for workflow_path in WORKFLOW_PATHS:
        workflow_text = read_text(workflow_path)
        referenced_scripts.update(validate_script_references(workflow_path, workflow_text, errors))
        validate_make_references(workflow_path, workflow_text, make_targets, errors)
        validate_docker_target_references(workflow_path, workflow_text, docker_targets, errors)

    referenced_scripts.update(collect_script_import_references())

    validate_codeowners(template_meta.owner, errors)
    validate_spec_families(errors)
    validate_orphan_scripts(referenced_scripts, errors)

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
