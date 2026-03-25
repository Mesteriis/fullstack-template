# ADR-0010: Use Taskiq with Redis Streams for background jobs and PostgreSQL for primary relational state

- Status: Accepted
- Date: 2026-03-25
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0005](./0005-background-jobs-and-workflow-orchestration.md)
- [ADR-0009](./0009-deployment-topology-and-runtime-model.md)
- [ADR-0011](./0011-manage-postgresql-schema-with-alembic.md)
- [ADR-1004](../product/1004-storage-strategy-for-artifacts-metadata-and-decisions.md)

## Context

Платформе нужны:

- отложенные задачи и фоновые workers для тяжёлых процессов;
- надёжное transactional storage для metadata, policy decisions, audit и pipeline state.

Высокоуровневые ADR уже фиксируют необходимость background jobs и раздельного хранения данных, но без явного выбора инфраструктурного стека это решение остаётся расплывчатым.

## Decision

Принимаются следующие базовые технологии:

- `Taskiq` используется как runtime и programming model для background jobs;
- `Redis Streams` используется как broker для доставки задач между producers и workers;
- `PostgreSQL` используется как primary relational database для metadata, state, policy decisions, audit и другой долговременной transactional информации.

Границы ответственности:

- broker отвечает за доставку и координацию выполнения задач;
- `PostgreSQL` является source of truth для доменного состояния;
- `Redis Streams` не рассматривается как долговременное хранилище бизнес-состояния.
- schema evolution для `PostgreSQL` управляется через versioned migrations; детали фиксируются отдельным ADR про `Alembic`.

## Consequences

### Positive

- появляется явный и понятный стек для async processing;
- упрощается разработка workers и background workflows;
- transactional state и audit остаются в зрелом SQL-хранилище.

### Negative

- система становится зависимой сразу от двух инфраструктурных компонентов;
- нужно внимательно проектировать идемпотентность и повторное выполнение задач;
- требуется эксплуатационная экспертиза и по Redis Streams, и по PostgreSQL.

### Neutral

- при необходимости конкретные реализации брокера или БД могут быть заменены отдельным ADR без смены базовой архитектурной модели.

## Alternatives considered

- выполнять фоновые задачи только через cron или batch processing;
- использовать только PostgreSQL без отдельного job broker;
- использовать Redis и как broker, и как primary state storage;
- оставить технологический выбор открытым до более поздней стадии.

## Follow-up work

- [ ] определить naming conventions для queues и job types
- [ ] описать retry, timeout и dead-letter policy для `Taskiq`
- [ ] определить модель хранения job outcome и execution history в `PostgreSQL`
