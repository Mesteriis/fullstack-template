# ADR-0011: Manage PostgreSQL schema evolution with Alembic migrations

- Status: Accepted
- Date: 2026-03-25
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0009](./0009-deployment-topology-and-runtime-model.md)
- [ADR-0010](./0010-use-taskiq-redis-streams-and-postgresql.md)
- [ADR-0012](./0012-define-repository-layout-and-file-placement-rules.md)
- [ADR-1004](../product/1004-storage-strategy-for-artifacts-metadata-and-decisions.md)

## Context

`PostgreSQL` уже выбран как primary relational storage для metadata, state, policy decisions и audit. Без единого механизма schema evolution команда быстро приходит к drift между окружениями, ручным SQL-правкам и неявным зависимостям между кодом и схемой базы.

Этот ADR конкретизирует, как развивается relational schema для хранилища, выбранного в ADR-0010, и как этот процесс встраивается в runtime and deployment model из ADR-0009.

## Decision

Schema evolution для `PostgreSQL` управляется только через `Alembic`.

Правила:

- миграции хранятся в репозитории и version-controlled;
- каждое изменение relational schema идёт в том же pull request, что и изменение application code, зависящего от этой схемы;
- автогенерация `Alembic` допустима только как стартовая точка; итоговый migration script обязан быть прочитан и отревьюен вручную;
- destructive changes не должны смешиваться с expand-этапом, если для rollout нужна совместимость между версиями приложения;
- ручные ad-hoc SQL-изменения в окружениях не считаются допустимым механизмом управления схемой.

Runtime and deployment rules:

- миграции не выполняются как побочный эффект FastAPI app bootstrap, import-time initialization или request handling;
- миграции запускаются либо отдельным административным, CI/CD или deployment step, либо явным pre-start шагом в backend container entrypoint до старта API процесса;
- успешное применение миграций является явной частью rollout для изменений, затрагивающих relational model;
- rollback стратегии для схемы должны продумываться при создании миграций, а не постфактум.

Repository layout rule:

- конфигурация `Alembic` и каталог `migrations/` размещаются в корне репозитория как shared infrastructure artifact для primary relational database.

## Consequences

### Positive

- схема `PostgreSQL` развивается предсказуемо и воспроизводимо;
- уменьшается риск drift между локальной, staging и production средой;
- deployment pipeline получает явный этап изменения схемы;
- связь между моделью данных и кодом становится reviewable.

### Negative

- команда обязана поддерживать дисциплину по миграциям;
- плохо спроектированные migrations могут усложнить rollout и rollback;
- появляется дополнительный операционный шаг в delivery pipeline.

### Neutral

- `Alembic` не определяет саму доменную модель хранения; он фиксирует способ её эволюции.

## Alternatives considered

- ручные SQL-скрипты без общего migration framework;
- автоматическое изменение схемы на старте приложения;
- использование ORM auto-create/update вместо versioned migrations;
- откладывать формализацию schema migration process до появления сложных изменений.

## Follow-up work

- [x] создать `alembic.ini` и каталог `migrations/` в корне репозитория
- [ ] описать naming conventions для revision и branch labels
- [ ] определить expand-contract guideline для breaking schema changes
