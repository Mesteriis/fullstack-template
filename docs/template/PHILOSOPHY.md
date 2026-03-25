# Template Philosophy

This repository is a maximum template.

Its purpose is not flexibility.
Its purpose is to define the strongest, cleanest and most opinionated baseline from which smaller templates can be derived.

## Core Position

- strictness is intentional;
- validation is part of architecture, not auxiliary tooling;
- repository governance is part of the runtime contract;
- derived templates must remove scope deliberately instead of weakening rules in place.

## How To Derive Templates

Derived templates are expected to:

- remove parts that do not apply to the target use case;
- keep the remaining rules internally consistent;
- preserve machine-enforced validation for every retained architectural decision;
- avoid “optional baseline” drift where the same rule exists in docs but not in automation.

Derived templates must not:

- keep the same scope but silently relax validation;
- replace explicit architectural rules with conventions-only documentation;
- treat CI, hooks, ADR checks or structure checks as optional.

## Why The Repository Is So Strict

The template is designed to survive long-term reuse across projects.
Without strict validation, repository drift appears quickly:

- documented architecture diverges from code layout;
- CI and local workflows stop matching;
- policy becomes tribal knowledge instead of versioned source of truth;
- new projects inherit inconsistencies instead of a real baseline.

The repository therefore treats:

- ADR validation,
- structure validation,
- architecture validation,
- CI symmetry,
- local hooks,
- and governance artifacts

as first-class architectural controls.

## Self-Governance

This template is self-governed.

That means the repository validates its own assumptions:

- orchestration checks its own targets and scripts;
- CI validates that parallel implementations stay symmetric;
- repository structure is enforced, not merely suggested;
- ADRs are part of the executable governance model.

The expected maintenance model is simple:

1. strengthen consistency when weak spots are found;
2. remove duplication when drift risk appears;
3. never dilute rules indirectly while “cleaning up”.
