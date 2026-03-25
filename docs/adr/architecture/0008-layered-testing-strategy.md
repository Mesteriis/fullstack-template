# ADR-0008: Define a layered testing strategy for critical flows

- Status: Accepted
- Date: 2026-03-25
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0002](./0002-api-first-and-contract-versioning.md)
- [ADR-0003](./0003-event-driven-internal-integration.md)
- [ADR-0013](./0013-adopt-a-flat-backend-service-root-and-bounded-context-layout.md)
- [ADR-0014](./0014-enforce-backend-dependency-direction-and-import-boundaries.md)
- [ADR-0015](./0015-enforce-template-quality-gates-and-governance-baseline.md)

## Context

Система имеет высокую цену ошибок в интеграциях, orchestration и policy behavior. Одних unit-тестов недостаточно, а ставка только на e2e делает обратную связь медленной и дорогой.

## Decision

Принимается layered testing strategy:

- unit tests для доменной логики и pure functions;
- integration tests для storage, message bus и external adapters;
- contract tests для API и событий;
- workflow tests для state transitions и orchestration;
- smoke/e2e tests для критичных сквозных сценариев;
- security regression tests для чувствительных flows.

Тесты размещаются максимально близко к owning code, а cross-app сценарии живут в корневом `tests/`.

## Consequences

### Positive

- выше уверенность в platform-critical flows;
- быстрее ловятся регрессии на нужном уровне;
- тестовая стратегия остаётся сбалансированной по цене и качеству сигнала.

### Negative

- инфраструктура тестов становится дороже;
- workflow и e2e тесты могут быть медленными и хрупкими.

### Neutral

- высокий coverage сам по себе не гарантирует корректность архитектуры и policy behavior.

## Alternatives considered

- делать ставку только на unit tests;
- тестировать критичные flows в основном вручную;
- полагаться только на e2e без нижних слоёв.

## Follow-up work

- [ ] зафиксировать test pyramid
- [ ] определить список golden scenarios
- [ ] описать общие test fixtures
