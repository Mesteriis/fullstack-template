# ADR-1002: Use SBOM, provenance and signatures as first-class verification inputs

- Status: Accepted
- Date: 2026-03-25
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-1001](./1001-trust-and-verification-policy.md)
- [ADR-1003](./1003-quarantine-and-security-gates.md)
- [ADR-1004](./1004-storage-strategy-for-artifacts-metadata-and-decisions.md)

## Context

Для зрелой модели доверия недостаточно проверять только уязвимости или только источник загрузки. Нужны независимые сигналы состава, происхождения и подлинности артефакта.

## Decision

SBOM, provenance и signatures рассматриваются как first-class inputs для trust evaluation.

Отсутствие сигнала:

- либо блокирует promotion;
- либо понижает trust level;
- либо требует manual override;
- определяется policy tier и контекстом экосистемы.

## Consequences

### Positive

- trust decision становится глубже и качественнее;
- появляется база для compliance и explainability;
- можно вводить policy tiers по уровню зрелости verification.

### Negative

- ingestion pipeline усложняется;
- возрастают требования к metadata storage;
- зрелость verification signals зависит от экосистемы.

### Neutral

- разные экосистемы могут предъявлять разные baseline requirements.

## Alternatives considered

- использовать только vulnerability scanning;
- считать SBOM и provenance необязательной дополнительной фичей;
- проверять подписи только выборочно без общей модели.

## Follow-up work

- [ ] определить verification baseline по экосистемам
- [ ] утвердить canonical metadata model
- [ ] определить policy tiers
