---
apply: by file patterns
patterns: specs/**/*, tests/contract/**/*, src/backend/apps/*/contracts/**/*, src/frontend/shared/api/**/*, scripts/check_specs.py
---

# Specs And Contracts

Path scope:

- `specs/**`
- `tests/contract/**`
- `src/backend/apps/*/contracts/**`
- `src/frontend/shared/api/**`
- `scripts/check_specs.py`

Применяй это правило при изменении контрактов и contract tests.

Обязательные ADR:

- [ADR-0002](../../docs/adr/architecture/0002-api-first-and-contract-versioning.md)
- [ADR-0008](../../docs/adr/architecture/0008-layered-testing-strategy.md)
- [ADR-0012](../../docs/adr/architecture/0012-define-repository-layout-and-file-placement-rules.md)
- [ADR-0015](../../docs/adr/architecture/0015-enforce-template-quality-gates-and-governance-baseline.md)

Правила:

- `specs/` является source of truth для OpenAPI, AsyncAPI и JSON Schema;
- breaking changes требуют явной версии контракта и обновления downstream artifacts;
- naming и placement rules для спецификаций нельзя обходить;
- contract tests должны идти после изменения спецификации, а не вместо неё.
