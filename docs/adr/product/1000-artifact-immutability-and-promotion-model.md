# ADR-1000: Treat stored artifacts as immutable and promote by stage

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

Платформа управляет жизненным циклом загруженных артефактов и должна поддерживать воспроизводимость, auditability и контролируемое продвижение между стадиями доверия. Если артефакты можно изменять "на месте", теряется причинно-следственная связь и затрудняется расследование.

## Decision

Все сохранённые артефакты считаются immutable.

Продвижение выполняется только как переход стадии или статуса, а не как перезапись существующего объекта.

Базовая stage model:

- `incoming` - артефакт принят, но ещё не trusted;
- `trusted` - артефакт прошёл необходимые проверки и policy;
- `quarantine` - артефакт изолирован и недоступен для обычного потребления.

## Consequences

### Positive

- выше воспроизводимость и auditability;
- проще строить deterministic promotion pipeline;
- легче проводить forensic analysis.

### Negative

- возможен рост storage usage;
- нужны retention и garbage collection правила.

### Neutral

- promotion может быть как физическим копированием, так и логическим переводом состояния.

## Alternatives considered

- mutable overwrite по version или tag;
- "latest wins" без stage model;
- ручное продвижение без формализованных стадий.

## Follow-up work

- [ ] утвердить lifecycle states и transitions
- [ ] определить retention policy
- [ ] определить rollback semantics
