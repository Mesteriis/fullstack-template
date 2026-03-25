from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SPEC_RULES = {
    "openapi": {".gitkeep", "README.md"},
    "asyncapi": {".gitkeep", "README.md"},
    "jsonschema": {".gitkeep", "README.md"},
}
SPEC_SUFFIXES = {
    "openapi": (".openapi.yaml", ".openapi.yml", ".openapi.json"),
    "asyncapi": (".asyncapi.yaml", ".asyncapi.yml", ".asyncapi.json"),
    "jsonschema": (".schema.json",),
}
PLACEHOLDER_NAMES = {".gitkeep", "README.md"}


def main() -> int:
    errors: list[str] = []
    spec_root = ROOT / "specs"

    if not (spec_root / "README.md").is_file():
        errors.append("missing required file: specs/README.md")

    for family, allowed_names in SPEC_RULES.items():
        family_root = spec_root / family
        readme_path = family_root / "README.md"
        if not readme_path.is_file():
            errors.append(f"missing required file: specs/{family}/README.md")

        for path in sorted(family_root.iterdir()):
            if path.name in allowed_names:
                continue
            if path.is_dir():
                errors.append(f"unexpected directory in specs/{family}: {path.name}")
                continue
            if not path.name.endswith(SPEC_SUFFIXES[family]):
                errors.append(
                    f"invalid spec filename in specs/{family}: {path.name}; "
                    f"expected suffixes {SPEC_SUFFIXES[family]}"
                )

        concrete_specs = [
            path
            for path in family_root.iterdir()
            if path.is_file() and path.name not in PLACEHOLDER_NAMES
        ]
        if not concrete_specs:
            errors.append(
                f"max-template requires specs/{family} to contain at least one canonical contract example; "
                "README and .gitkeep placeholders are not sufficient"
            )

    if errors:
        for error in errors:
            print(error)
        return 1

    print("Spec validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
