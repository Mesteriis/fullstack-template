# ADR-0005: Run heavy processing as background jobs and orchestrated workflows

- Status: Accepted
- Date: 2026-03-25
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0003](./0003-event-driven-internal-integration.md)
- [ADR-0009](./0009-deployment-topology-and-runtime-model.md)
- [ADR-0010](./0010-use-taskiq-redis-streams-and-postgresql.md)
- [ADR-1004](../product/1004-storage-strategy-for-artifacts-metadata-and-decisions.md)

## Context

Часть операций системы потенциально тяжёлая, долгая и внешне зависимая. Выполнять всё inline внутри запроса неэффективно и хрупко: API latency растёт, а recovery становится сложнее.

## Decision

Тяжёлые и потенциально длительные этапы выполняются как background jobs или workflow steps.

Базовый стек для execution path:

- `Taskiq` как runtime для отложенных задач;
- `Redis Streams` как broker и транспорт доставки задач между producers и workers.

Синхронно допускается только минимум:

- принять запрос;
- сохранить входные данные или ссылку на них;
- зарегистрировать старт процесса;
- вернуть tracking reference или текущий статус.

Оркестрация обязана поддерживать retry, idempotency, timeout и dead-letter semantics. Состояние домена и результаты выполнения, имеющие долговременную ценность, не считаются ответственностью брокера и сохраняются в основном хранилище.

## Consequences

### Positive

- API остаётся отзывчивым;
- проще повторять и изолировать упавшие шаги;
- тяжёлые обработчики масштабируются независимо.

### Negative

- требуется явная state machine pipeline;
- появляется eventual consistency и операционная сложность.

### Neutral

- мелкие sync-checks допустимы, если они не ломают latency budget.

## Alternatives considered

- полностью synchronous pipeline;
- batch-only processing;
- один giant worker без явной workflow model.

## Follow-up work

- [ ] зафиксировать очереди, приоритеты и job classes поверх `Taskiq`
- [ ] описать retry, backoff и dead-letter policy
- [ ] зафиксировать idempotency strategy
