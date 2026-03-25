from __future__ import annotations

import re
import sys
from pathlib import Path

from template_meta import load_template_meta


ROOT = Path(__file__).resolve().parent.parent
ADR_ROOT = ROOT / "docs" / "adr"
STATUS_VALUES = {
    "Proposed",
    "Accepted",
    "Deprecated",
    "Rejected",
    "Superseded",
}
REQUIRED_FIELDS = [
    "Status",
    "Date",
    "Deciders",
    "Supersedes",
    "Superseded by",
]
REQUIRED_SECTIONS = [
    "## Related ADRs",
    "## Context",
    "## Decision",
    "## Consequences",
    "## Alternatives considered",
    "## Follow-up work",
]
CATEGORY_RULES = {
    "architecture": re.compile(r"^0\d{3}-[a-z0-9-]+\.md$"),
    "product": re.compile(r"^1\d{3}-[a-z0-9-]+\.md$"),
    "engineering": re.compile(r"^2\d{3}-[a-z0-9-]+\.md$"),
}


def find_links(readme_path: Path) -> list[str]:
    content = readme_path.read_text(encoding="utf-8")
    return re.findall(r"\[\s*([0-9]{4}-[a-z0-9-]+\.md)\s*\]\(\./[^)]+\)", content)


def validate_root_readme(errors: list[str]) -> None:
    readme_path = ADR_ROOT / "README.md"
    content = readme_path.read_text(encoding="utf-8")

    for category in CATEGORY_RULES:
        expected_link = f"[{category}/](./{category}/README.md)"
        if expected_link not in content:
            errors.append(
                f"{readme_path.relative_to(ROOT)} must link to {category}/README.md to keep ADR navigation explicit"
            )


def validate_index(category: str, errors: list[str]) -> None:
    category_dir = ADR_ROOT / category
    readme_path = category_dir / "README.md"
    actual = sorted(path.name for path in category_dir.glob("*.md") if path.name != "README.md")
    indexed = find_links(readme_path)
    if indexed != actual:
        errors.append(
            f"{readme_path.relative_to(ROOT)} index mismatch: indexed={indexed}, actual={actual}"
        )


def validate_related_adrs(path: Path, content: str, errors: list[str]) -> None:
    related_section_match = re.search(
        r"## Related ADRs\s+(.*?)(?:\n## |\Z)",
        content,
        flags=re.DOTALL,
    )
    if not related_section_match:
        errors.append(f"{path.relative_to(ROOT)} must contain a Related ADRs section")
        return

    related_links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", related_section_match.group(1))
    if not related_links:
        errors.append(f"{path.relative_to(ROOT)} must link at least one related ADR")
        return

    for link in related_links:
        related_path = (path.parent / link).resolve()
        try:
            related_path.relative_to(ADR_ROOT)
        except ValueError:
            errors.append(f"{path.relative_to(ROOT)} links Related ADR outside docs/adr: {link}")
            continue
        if not related_path.is_file():
            errors.append(f"{path.relative_to(ROOT)} links missing Related ADR target: {link}")


def validate_status(path: Path, content: str, errors: list[str]) -> None:
    status_match = re.search(r"^- Status:[ \t]*(.+)$", content, flags=re.MULTILINE)
    if not status_match:
        errors.append(f"{path.relative_to(ROOT)} missing status value")
        return

    status = status_match.group(1).strip()
    if status not in STATUS_VALUES:
        errors.append(f"{path.relative_to(ROOT)} has invalid status '{status}'")
        return

    superseded_by_match = re.search(r"^- Superseded by:[ \t]*(.*)$", content, flags=re.MULTILINE)
    superseded_by = superseded_by_match.group(1).strip() if superseded_by_match else ""

    if status == "Superseded":
        if not superseded_by:
            errors.append(
                f"{path.relative_to(ROOT)} has status Superseded but an empty '- Superseded by:' field"
            )
        elif not re.fullmatch(r"ADR-\d{4}", superseded_by):
            errors.append(
                f"{path.relative_to(ROOT)} must use '- Superseded by: ADR-XXXX' when status is Superseded"
            )
        return

    if superseded_by:
        errors.append(
            f"{path.relative_to(ROOT)} must leave '- Superseded by:' empty unless status is Superseded"
        )


def validate_file(path: Path, category: str, expected_decider: str, errors: list[str]) -> None:
    content = path.read_text(encoding="utf-8")
    file_name = path.name
    rule = CATEGORY_RULES[category]
    if not rule.match(file_name):
        errors.append(f"{path.relative_to(ROOT)} has invalid filename for category '{category}'")

    number = file_name.split("-", 1)[0]
    title_line = f"# ADR-{number}:"
    if not content.startswith(title_line):
        errors.append(f"{path.relative_to(ROOT)} must start with '{title_line}'")

    for field in REQUIRED_FIELDS:
        if f"- {field}:" not in content:
            errors.append(f"{path.relative_to(ROOT)} missing field '- {field}:'")

    validate_status(path, content, errors)

    date_match = re.search(r"^- Date:[ \t]*(\d{4}-\d{2}-\d{2})$", content, flags=re.MULTILINE)
    if not date_match:
        errors.append(f"{path.relative_to(ROOT)} must use Date in YYYY-MM-DD format")

    deciders_match = re.search(r"^- Deciders:[ \t]*(.+)$", content, flags=re.MULTILINE)
    if not deciders_match:
        errors.append(f"{path.relative_to(ROOT)} missing deciders value")
    else:
        deciders = deciders_match.group(1).strip()
        if deciders != expected_decider:
            errors.append(
                f"{path.relative_to(ROOT)} must use '- Deciders: {expected_decider}', found '{deciders}'"
            )

    for section in REQUIRED_SECTIONS:
        if section not in content:
            errors.append(f"{path.relative_to(ROOT)} missing section '{section}'")

    validate_related_adrs(path, content, errors)


def main() -> int:
    template_meta = load_template_meta()
    errors: list[str] = []

    validate_root_readme(errors)

    for category in sorted(CATEGORY_RULES):
        validate_index(category, errors)
        category_dir = ADR_ROOT / category
        for path in sorted(category_dir.glob("*.md")):
            if path.name == "README.md":
                continue
            validate_file(path, category, template_meta.adr_decider, errors)

    if errors:
        for error in errors:
            print(error)
        return 1

    print("ADR validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
