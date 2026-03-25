# Product ADR

Этот раздел содержит решения, которые описывают предметную область и продуктовую модель платформы.

Обязательная точка входа перед чтением отдельных ADR: [../INDEX.md](../INDEX.md).

Используем этот раздел для решений про:

- жизненный цикл сущностей домена;
- trust model и verification rules;
- domain-specific storage model;
- quarantine, override, promotion и другие бизнес-значимые состояния;
- внешние экосистемы, адаптеры и каноническую модель идентичности.

Текущий набор accepted ADR:

- [1000-artifact-immutability-and-promotion-model.md](./1000-artifact-immutability-and-promotion-model.md)
- [1001-trust-and-verification-policy.md](./1001-trust-and-verification-policy.md)
- [1002-sbom-provenance-and-signatures.md](./1002-sbom-provenance-and-signatures.md)
- [1003-quarantine-and-security-gates.md](./1003-quarantine-and-security-gates.md)
- [1004-storage-strategy-for-artifacts-metadata-and-decisions.md](./1004-storage-strategy-for-artifacts-metadata-and-decisions.md)
