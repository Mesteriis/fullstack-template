---
apply: path
---

# Backend Apps And Product Model

Применяй это правило при изменении bounded contexts, application/domain/contracts/infrastructure слоёв и app-level тестов backend.

Сначала прочитай:

- [ADR-0002](../../docs/adr/architecture/0002-api-first-and-contract-versioning.md)
- [ADR-0008](../../docs/adr/architecture/0008-layered-testing-strategy.md)
- [ADR-0013](../../docs/adr/architecture/0013-adopt-a-flat-backend-service-root-and-bounded-context-layout.md)
- [ADR-0014](../../docs/adr/architecture/0014-enforce-backend-dependency-direction-and-import-boundaries.md)

Если изменение затрагивает trust, verification, quarantine, promotion, metadata, audit или storage semantics, дополнительно прочитай:

- [ADR-1000](../../docs/adr/product/1000-artifact-immutability-and-promotion-model.md)
- [ADR-1001](../../docs/adr/product/1001-trust-and-verification-policy.md)
- [ADR-1002](../../docs/adr/product/1002-sbom-provenance-and-signatures.md)
- [ADR-1003](../../docs/adr/product/1003-quarantine-and-security-gates.md)
- [ADR-1004](../../docs/adr/product/1004-storage-strategy-for-artifacts-metadata-and-decisions.md)

Правила:

- внутри bounded context соблюдай слои `api/application/contracts/domain/infrastructure`;
- cross-context imports идут только через `contracts`, public facades или события;
- продуктовые правила не должны silently расходиться с product ADR;
- если меняется business semantics, сначала обнови контракт или ADR, затем реализацию и тесты.
