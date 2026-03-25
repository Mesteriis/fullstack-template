# ADR-0009: Separate control plane from heavy execution workers

- Status: Accepted
- Date: 2026-03-25
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0005](./0005-background-jobs-and-workflow-orchestration.md)
- [ADR-0010](./0010-use-taskiq-redis-streams-and-postgresql.md)
- [ADR-0011](./0011-manage-postgresql-schema-with-alembic.md)
- [ADR-0016](./0016-support-github-and-gitea-ci-for-template-repositories.md)

## Context

Система обслуживает разные типы нагрузки: API requests, orchestration, фоновые вычисления, периодические reconciliation jobs и integration workloads. Если всё исполняется в одном runtime-процессе, тяжёлые задачи начинают влиять на latency и stability control plane.

## Decision

Runtime разделяется как минимум на:

- control plane/API;
- background workers;
- optional scheduled or reconciliation workers.

Control plane не должен зависеть по latency и ресурсам от тяжёлых background tasks. Для локальной разработки допускается collapsed topology, но production model остаётся разделённой.

Schema migrations для primary relational database не выполняются как часть FastAPI app bootstrap. Они запускаются либо как отдельный административный или deployment step, либо как явный pre-start шаг backend container entrypoint до старта API-процесса.

## Consequences

### Positive

- повышается стабильность API;
- тяжёлые обработчики можно масштабировать независимо;
- уменьшается resource contention между разными типами нагрузки.

### Negative

- возрастает операционная сложность;
- нужны conventions для coordination, deployment и health management.

### Neutral

- физическая реализация может отличаться между окружениями при сохранении логической модели.

## Alternatives considered

- один процесс для всего;
- только cron/batch workers;
- отложить разделение topology до появления проблем.

## Follow-up work

- [ ] описать runtime roles и их обязанности
- [ ] определить health, readiness и scaling semantics
- [ ] зафиксировать deployment conventions для окружений
