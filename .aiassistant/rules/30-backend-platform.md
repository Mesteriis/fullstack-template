---
apply: by file patterns
patterns: src/backend/api/**/*, src/backend/core/**/*, src/backend/runtime/**/*, src/backend/main.py, src/backend/pyproject.toml, src/backend/tests/architecture/**/*, src/backend/tests/core/**/*, src/backend/tests/runtime/**/*, src/backend/tests/factories/**/*, src/backend/tests/fixtures/**/*, src/backend/tests/conftest.py, migrations/**/*, alembic.ini, docker/Dockerfile, docker/entrypoints/backend.sh, docker/runs/backend.sh, scripts/check_backend_architecture.py, scripts/run_backend_bandit.py, scripts/run_backend_deptry.py, scripts/run_backend_eradicate.py, scripts/run_backend_import_boundaries.py, scripts/run_backend_lint.py, scripts/run_backend_lint_fix.py, scripts/run_backend_pip_audit.sh, scripts/run_backend_pyupgrade.py, scripts/run_backend_sync.py, scripts/run_backend_tests.py, scripts/run_backend_tryceratops.py, scripts/run_backend_types.py, scripts/run_backend_xenon.py
---

# Backend Platform

Path scope:

- `src/backend/api/**`
- `src/backend/core/**`
- `src/backend/runtime/**`
- `src/backend/main.py`
- `src/backend/pyproject.toml`
- `src/backend/tests/architecture/**`
- `src/backend/tests/core/**`
- `src/backend/tests/runtime/**`
- `src/backend/tests/factories/**`
- `src/backend/tests/fixtures/**`
- `src/backend/tests/conftest.py`
- `migrations/**`
- `alembic.ini`
- `docker/Dockerfile`
- `docker/entrypoints/backend.sh`
- `docker/runs/backend.sh`
- `scripts/check_backend_architecture.py`
- `scripts/run_backend_bandit.py`
- `scripts/run_backend_deptry.py`
- `scripts/run_backend_eradicate.py`
- `scripts/run_backend_import_boundaries.py`
- `scripts/run_backend_lint.py`
- `scripts/run_backend_lint_fix.py`
- `scripts/run_backend_pip_audit.sh`
- `scripts/run_backend_pyupgrade.py`
- `scripts/run_backend_sync.py`
- `scripts/run_backend_tests.py`
- `scripts/run_backend_tryceratops.py`
- `scripts/run_backend_types.py`
- `scripts/run_backend_xenon.py`

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
