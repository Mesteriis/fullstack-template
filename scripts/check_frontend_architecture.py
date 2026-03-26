from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FRONTEND_ROOT = ROOT / "src" / "frontend"
LAYERS = ("shared", "entities", "features", "pages", "app")
ALLOWED_LAYER_IMPORTS = {
    "shared": {"shared"},
    "entities": {"shared", "entities"},
    "features": {"shared", "entities", "features"},
    "pages": {"shared", "entities", "features", "pages"},
    "app": {"shared", "entities", "features", "pages", "app"},
}
IGNORED_PARTS = {".git", "coverage", "dist", "node_modules"}
SOURCE_SUFFIXES = {".ts", ".vue"}
FORBIDDEN_LEGACY_FILES = (
    "src/frontend/App.vue",
    "src/frontend/main.ts",
    "src/frontend/styles.css",
)
REQUIRED_FILES = (
    "src/frontend/app/App.vue",
    "src/frontend/app/main.ts",
    "src/frontend/app/router/index.ts",
    "src/frontend/shared/api/http-client.ts",
    "src/frontend/shared/config/env.ts",
    "src/frontend/shared/observability/setup.ts",
    "src/frontend/shared/ui/index.ts",
)
IMPORT_PATTERN = re.compile(
    r"""(?x)
    (?:import|export)\s+
    (?:type\s+)?
    (?:[\w*\s{},]+?\s+from\s+)?
    ["']([^"']+)["']
    """
)
DYNAMIC_IMPORT_PATTERN = re.compile(r"""import\(\s*["']([^"']+)["']\s*\)""")
TEMPLATE_PATTERN = re.compile(r"<template[^>]*>(?P<body>[\s\S]*?)</template>")
STYLE_BLOCK_PATTERN = re.compile(r"<style\b", re.IGNORECASE)
RAW_TAG_PATTERN = re.compile(r"<\s*([a-z][a-z0-9-]*)\b")
INLINE_CLASS_PATTERN = re.compile(r"\sclass\s*=")
INLINE_STYLE_PATTERN = re.compile(r"\sstyle\s*=")
FORBIDDEN_DOM_PATTERN = re.compile(r"\b(?:document|window)\s*\.")
ALLOWED_TEMPLATE_TAGS = {"component", "slot", "template"}


def iter_source_files() -> list[Path]:
    files: list[Path] = []
    for path in FRONTEND_ROOT.rglob("*"):
        if path.suffix not in SOURCE_SUFFIXES:
            continue
        if any(part in IGNORED_PARTS for part in path.relative_to(FRONTEND_ROOT).parts):
            continue
        files.append(path)
    return sorted(files)


def classify_layer(path: Path) -> str | None:
    relative_path = path.relative_to(FRONTEND_ROOT)
    if not relative_path.parts:
        return None

    top_level = relative_path.parts[0]
    if top_level in LAYERS:
        return top_level
    return None


def extract_imports(source: str) -> set[str]:
    imports = {match.group(1) for match in IMPORT_PATTERN.finditer(source)}
    imports.update(match.group(1) for match in DYNAMIC_IMPORT_PATTERN.finditer(source))
    return imports


def resolve_relative_import(current_path: Path, import_path: str) -> Path | None:
    base_path = (current_path.parent / import_path).resolve()
    candidates = (
        base_path,
        base_path.with_suffix(".ts"),
        base_path.with_suffix(".vue"),
        base_path / "index.ts",
        base_path / "index.vue",
    )

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    return None


def validate_required_files(errors: list[str]) -> None:
    for rel_path in REQUIRED_FILES:
        if not (ROOT / rel_path).is_file():
            errors.append(f"required frontend architecture file is missing: {rel_path}")


def validate_legacy_files(errors: list[str]) -> None:
    for rel_path in FORBIDDEN_LEGACY_FILES:
        if (ROOT / rel_path).exists():
            errors.append(
                f"legacy frontend root file must be removed after app-layer migration: {rel_path}"
            )


def validate_import_boundaries(path: Path, source: str, errors: list[str]) -> None:
    layer = classify_layer(path)
    if layer is None:
        return

    allowed_layers = ALLOWED_LAYER_IMPORTS[layer]
    for imported in sorted(extract_imports(source)):
        if imported.startswith("@/"):
            target_layer = imported.removeprefix("@/").split("/", 1)[0]
            if target_layer in LAYERS and target_layer not in allowed_layers:
                errors.append(
                    f"{path.relative_to(ROOT)} violates frontend layer rule: {layer} -> {target_layer} via '{imported}'"
                )
            continue

        if not imported.startswith("."):
            continue

        resolved_path = resolve_relative_import(path, imported)
        if resolved_path is None:
            errors.append(
                f"{path.relative_to(ROOT)} uses unresolved relative import '{imported}'. Frontend imports must remain explicit."
            )
            continue

        target_layer = classify_layer(resolved_path)
        if target_layer is None:
            continue

        if target_layer != layer:
            errors.append(
                f"{path.relative_to(ROOT)} uses relative import '{imported}' across frontend layers ({layer} -> {target_layer}). Use aliases instead."
            )

        if target_layer not in allowed_layers:
            errors.append(
                f"{path.relative_to(ROOT)} violates frontend layer rule via relative import '{imported}' ({layer} -> {target_layer})"
            )


def validate_page_and_feature_ui(path: Path, source: str, errors: list[str]) -> None:
    layer = classify_layer(path)
    if layer not in {"pages", "features"}:
        return

    if FORBIDDEN_DOM_PATTERN.search(source):
        errors.append(
            f"{path.relative_to(ROOT)} must not use direct DOM globals. Compose behavior through Vue and shared/ui instead."
        )

    if STYLE_BLOCK_PATTERN.search(source):
        errors.append(
            f"{path.relative_to(ROOT)} must not declare local <style> blocks. Styling belongs to shared/ui."
        )

    template_match = TEMPLATE_PATTERN.search(source)
    if template_match is None:
        return

    template_body = template_match.group("body")
    if INLINE_CLASS_PATTERN.search(template_body):
        errors.append(
            f"{path.relative_to(ROOT)} must not leak local classes in page/feature templates. Use shared/ui props and composition."
        )

    if INLINE_STYLE_PATTERN.search(template_body):
        errors.append(
            f"{path.relative_to(ROOT)} must not use inline styles in page/feature templates. Use shared/ui tokens and semantics."
        )

    raw_tags = {
        tag_name
        for tag_name in RAW_TAG_PATTERN.findall(template_body)
        if tag_name not in ALLOWED_TEMPLATE_TAGS
    }
    if raw_tags:
        tag_list = ", ".join(sorted(raw_tags))
        errors.append(
            f"{path.relative_to(ROOT)} uses raw HTML tags in {layer}: {tag_list}. Pages and features must render through shared/ui primitives."
        )

    if 'from "@/shared/ui"' not in source and 'from "@/shared/ui/' not in source:
        errors.append(
            f"{path.relative_to(ROOT)} must import from '@/shared/ui' to keep page/feature UI composition on the adapter boundary."
        )


def main() -> int:
    errors: list[str] = []

    validate_required_files(errors)
    validate_legacy_files(errors)

    for path in iter_source_files():
        source = path.read_text(encoding="utf-8")
        validate_import_boundaries(path, source, errors)
        validate_page_and_feature_ui(path, source, errors)

    if errors:
        for error in errors:
            print(error)
        return 1

    print("Frontend architecture validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
