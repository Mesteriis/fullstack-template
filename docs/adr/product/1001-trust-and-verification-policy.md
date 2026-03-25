# ADR-1001: Separate artifact storage from trust decision

- Status: Accepted
- Date: 2026-03-25
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0006](../architecture/0006-authn-authz-and-machine-identities.md)
- [ADR-0007](../architecture/0007-configuration-and-policy-as-code.md)
- [ADR-1000](./1000-artifact-immutability-and-promotion-model.md)
- [ADR-1002](./1002-sbom-provenance-and-signatures.md)
- [ADR-1003](./1003-quarantine-and-security-gates.md)
- [ADR-1004](./1004-storage-strategy-for-artifacts-metadata-and-decisions.md)

## Context

Факт физического хранения артефакта не означает, что ему можно доверять. Для управляемой supply-chain модели нужен отдельный trust decision, основанный на verification signals и policy.

## Decision

Разделяются две независимые плоскости:

1. факт хранения артефакта;
2. trust decision по артефакту.

Артефакт может существовать в системе и одновременно иметь один из trust outcomes:

- `not_yet_trusted`;
- `trusted`;
- `denied`;
- `quarantined`;
- `expired`.

Trust decision формируется policy engine на основании verification signals и policy context.

## Consequences

### Positive

- появляется гибкая и объяснимая trust model;
- policy можно развивать без смены модели хранения;
- проще объяснять причины допуска или отказа.

### Negative

- возрастает когнитивная и техническая сложность;
- нужна консистентная модель статусов и verdict reasons.

### Neutral

- один и тот же артефакт может получать разный trust outcome в разных policy contexts.

## Alternatives considered

- считать `stored = trusted`;
- делать trust decision только в момент потребления;
- опираться только на vulnerability scanning.

## Follow-up work

- [ ] определить trust signals
- [ ] определить verdict model
- [ ] определить explainability format
