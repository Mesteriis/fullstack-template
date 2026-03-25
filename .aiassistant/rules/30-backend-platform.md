---
apply: path
---

# Backend Platform

Применяй это правило при изменении backend platform, runtime, migrations и backend container wiring.

Обязательные ADR:

- [ADR-0005](../../docs/adr/architecture/0005-background-jobs-and-workflow-orchestration.md)
- [ADR-0008](../../docs/adr/architecture/0008-layered-testing-strategy.md)
- [ADR-0009](../../docs/adr/architecture/0009-deployment-topology-and-runtime-model.md)
- [ADR-0010](../../docs/adr/architecture/0010-use-taskiq-redis-streams-and-postgresql.md)
- [ADR-0011](../../docs/adr/architecture/0011-manage-postgresql-schema-with-alembic.md)
- [ADR-0012](../../docs/adr/architecture/0012-define-repository-layout-and-file-placement-rules.md)
- [ADR-0013](../../docs/adr/architecture/0013-adopt-a-flat-backend-service-root-and-bounded-context-layout.md)
- [ADR-0014](../../docs/adr/architecture/0014-enforce-backend-dependency-direction-and-import-boundaries.md)

Правила:

- backend service root остаётся плоским: `src/backend/{api,apps,core,runtime,main.py,tests}`;
- `core` не зависит от `api`, `runtime` и внутренних bounded contexts кроме bootstrap wiring;
- runtime и workers не обходят application/contracts слои без явной причины;
- миграции хранятся в `migrations/` и управляются только через `Alembic`;
- миграции не должны запускаться как side effect import-time bootstrap;
- для фоновых задач сохраняется стек `Taskiq + Redis Streams + PostgreSQL`.
