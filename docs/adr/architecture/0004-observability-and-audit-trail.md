# ADR-0004: Make observability and audit trail first-class concerns

- Status: Accepted
- Date: 2026-03-25
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0003](./0003-event-driven-internal-integration.md)
- [ADR-0006](./0006-authn-authz-and-machine-identities.md)
- [ADR-1004](../product/1004-storage-strategy-for-artifacts-metadata-and-decisions.md)

## Context

Без хорошей observability платформа быстро превращается в чёрный ящик. Для эксплуатации, безопасности и объяснимости решений нужны не только технические логи, но и полноценный audit trail для чувствительных действий.

## Decision

Observability и audit закладываются как базовые свойства системы.

Обязательные элементы:

- structured logs;
- trace и correlation IDs;
- метрики по API, job execution и integration points;
- audit records для чувствительных действий;
- события домена и pipeline state changes.

Audit и observability рассматриваются как связанные, но разные плоскости.

## Consequences

### Positive

- проще расследовать инциденты и регрессии;
- легче объяснять принятые системой решения;
- растёт сопровождаемость platform-critical flows.

### Negative

- увеличиваются требования к storage и retention;
- нужна политика redaction и контроля чувствительных данных.

### Neutral

- локальная разработка может использовать упрощённый стек наблюдаемости, но не иную модель событий.

## Alternatives considered

- только технические логи;
- audit как отложенная задача;
- минимальные логи без correlation.

## Follow-up work

- [ ] определить taxonomy audit events
- [ ] зафиксировать log schema
- [ ] описать redaction policy
