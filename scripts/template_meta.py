from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_META_PATH = ROOT / "template.meta.toml"
REQUIRED_FIELDS = {
    "owner": str,
    "adr_decider": str,
    "template_type": str,
}


@dataclass(frozen=True)
class TemplateMeta:
    owner: str
    adr_decider: str
    template_type: str


def load_template_meta() -> TemplateMeta:
    if not TEMPLATE_META_PATH.is_file():
        raise RuntimeError(f"Missing required template metadata file: {TEMPLATE_META_PATH.relative_to(ROOT)}")

    with TEMPLATE_META_PATH.open("rb") as meta_file:
        raw_meta = tomllib.load(meta_file)

    missing_fields = [field for field in REQUIRED_FIELDS if field not in raw_meta]
    if missing_fields:
        missing = ", ".join(missing_fields)
        raise RuntimeError(f"template.meta.toml is missing required fields: {missing}")

    for field, expected_type in REQUIRED_FIELDS.items():
        value = raw_meta[field]
        if not isinstance(value, expected_type) or not value.strip():
            raise RuntimeError(
                f"template.meta.toml field '{field}' must be a non-empty {expected_type.__name__}"
            )

    return TemplateMeta(
        owner=raw_meta["owner"].strip(),
        adr_decider=raw_meta["adr_decider"].strip(),
        template_type=raw_meta["template_type"].strip(),
    )
