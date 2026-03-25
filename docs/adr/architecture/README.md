# Architecture ADR

Этот раздел содержит архитектурные решения, которые задают форму системы, но не зависят от названия продукта.

Обязательная точка входа перед чтением отдельных ADR: [../INDEX.md](../INDEX.md).

Используем этот раздел для решений про:

- структуру репозитория и bounded contexts;
- контракты и интеграции;
- runtime topology;
- тестовую стратегию;
- безопасность, identity, policy и observability как платформенные практики.

Текущий набор accepted ADR:

- [0000-record-architecture-decisions.md](./0000-record-architecture-decisions.md)
- [0001-monorepo-and-bounded-contexts.md](./0001-monorepo-and-bounded-contexts.md)
- [0002-api-first-and-contract-versioning.md](./0002-api-first-and-contract-versioning.md)
- [0003-event-driven-internal-integration.md](./0003-event-driven-internal-integration.md)
- [0004-observability-and-audit-trail.md](./0004-observability-and-audit-trail.md)
- [0005-background-jobs-and-workflow-orchestration.md](./0005-background-jobs-and-workflow-orchestration.md)
- [0006-authn-authz-and-machine-identities.md](./0006-authn-authz-and-machine-identities.md)
- [0007-configuration-and-policy-as-code.md](./0007-configuration-and-policy-as-code.md)
- [0008-layered-testing-strategy.md](./0008-layered-testing-strategy.md)
- [0009-deployment-topology-and-runtime-model.md](./0009-deployment-topology-and-runtime-model.md)
- [0010-use-taskiq-redis-streams-and-postgresql.md](./0010-use-taskiq-redis-streams-and-postgresql.md)
- [0011-manage-postgresql-schema-with-alembic.md](./0011-manage-postgresql-schema-with-alembic.md)
- [0012-define-repository-layout-and-file-placement-rules.md](./0012-define-repository-layout-and-file-placement-rules.md)
- [0013-adopt-a-flat-backend-service-root-and-bounded-context-layout.md](./0013-adopt-a-flat-backend-service-root-and-bounded-context-layout.md)
- [0014-enforce-backend-dependency-direction-and-import-boundaries.md](./0014-enforce-backend-dependency-direction-and-import-boundaries.md)
- [0015-enforce-template-quality-gates-and-governance-baseline.md](./0015-enforce-template-quality-gates-and-governance-baseline.md)
- [0016-support-github-and-gitea-ci-for-template-repositories.md](./0016-support-github-and-gitea-ci-for-template-repositories.md)
