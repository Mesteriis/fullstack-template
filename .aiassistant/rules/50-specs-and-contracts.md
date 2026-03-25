---
apply: path
---

# Specs And Contracts

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
