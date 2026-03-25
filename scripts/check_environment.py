from __future__ import annotations

import shutil
import sys

from template_meta import load_template_meta


REQUIRED_COMMANDS = {
    "git": "repository operations and metadata-aware docker tagging",
    "make": "golden-master orchestration entrypoint",
    "uv": "backend dependency and Python tooling runtime",
    "pnpm": "frontend dependency and package runtime",
    "pre-commit": "local repository enforcement hooks",
    "docker": "container validation and image builds",
    "shellcheck": "shell quality baseline",
    "hadolint": "Dockerfile lint baseline",
    "trivy": "filesystem vulnerability and misconfiguration scanning",
}


def main() -> int:
    template_meta = load_template_meta()
    print(f"Doctor for template type: {template_meta.template_type}")
    print(f"Template owner: {template_meta.owner}")
    print("Validating required local tooling:")

    missing: list[str] = []
    for command, reason in REQUIRED_COMMANDS.items():
        resolved = shutil.which(command)
        if resolved is None:
            print(f"  [missing] {command}: required for {reason}")
            missing.append(command)
            continue
        print(f"  [ok] {command}: {resolved}")

    if missing:
        missing_text = ", ".join(missing)
        print(f"Doctor failed: missing required commands: {missing_text}")
        return 1

    print("Environment validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
