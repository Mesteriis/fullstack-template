from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ENV_EXAMPLE_PATH = ROOT / ".env.example"
ENV_PATH = ROOT / ".env"


def parse_env_lines(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", maxsplit=1)
        values[key] = value
    return values


def merge_missing_defaults(target_text: str, example_text: str) -> str:
    target_values = parse_env_lines(target_text)
    example_values = parse_env_lines(example_text)
    missing_keys = [key for key in example_values if key not in target_values]
    if not missing_keys:
        return target_text

    merged = target_text.rstrip()
    if merged:
        merged += "\n\n"
    merged += "# Added from .env.example by scripts/init_env.py\n"
    merged += "\n".join(f"{key}={example_values[key]}" for key in missing_keys)
    merged += "\n"
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize or refresh the repository .env file from .env.example.")
    parser.add_argument("--force", action="store_true", help="Replace .env even if it already exists.")
    args = parser.parse_args()

    example_text = ENV_EXAMPLE_PATH.read_text(encoding="utf-8")

    if args.force or not ENV_PATH.exists():
        action = "Replaced" if args.force and ENV_PATH.exists() else "Created"
        ENV_PATH.write_text(example_text, encoding="utf-8")
        print(f"{action} {ENV_PATH.relative_to(ROOT)} from {ENV_EXAMPLE_PATH.relative_to(ROOT)}.")
        return 0

    current_text = ENV_PATH.read_text(encoding="utf-8")
    merged_text = merge_missing_defaults(current_text, example_text)
    if merged_text != current_text:
        ENV_PATH.write_text(merged_text, encoding="utf-8")
        print(f"Updated {ENV_PATH.relative_to(ROOT)} with missing defaults from {ENV_EXAMPLE_PATH.relative_to(ROOT)}.")
    else:
        print(f"{ENV_PATH.relative_to(ROOT)} already contains the required defaults.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
