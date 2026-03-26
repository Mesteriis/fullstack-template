# ADR Index

Этот файл является обязательной точкой входа для людей и ИИ-агентов перед изменением архитектуры, кода, CI, migration flow, контрактов и продуктовой модели.

Сначала нужно прочитать:

1. [README.md](./README.md)
2. этот `INDEX.md`
3. обязательные foundation ADR
4. ADR по соответствующей зоне изменений

## Foundation ADR

Эти ADR нужно считать базовыми почти для любой нетривиальной задачи:

- [ADR-0000](./architecture/0000-record-architecture-decisions.md) - как фиксируются решения;
- [ADR-0001](./architecture/0001-monorepo-and-bounded-contexts.md) - monorepo и bounded contexts;
- [ADR-0002](./architecture/0002-api-first-and-contract-versioning.md) - spec-first и contract versioning;
- [ADR-0012](./architecture/0012-define-repository-layout-and-file-placement-rules.md) - layout и placement rules;
- [ADR-0015](./architecture/0015-enforce-template-quality-gates-and-governance-baseline.md) - quality gates, governance и security baseline;
- [ADR-0016](./architecture/0016-support-github-and-gitea-ci-for-template-repositories.md) - CI baseline для GitHub и Gitea.
- [ADR-0017](./architecture/0017-standardize-backend-testing-on-pytest-testcontainers-and-full-request-flows.md) - backend testing baseline на pytest и Testcontainers.
- [ADR-0018](./architecture/0018-enforce-typed-contracts-and-unit-of-work-owned-persistence.md) - typed contracts, repositories и Unit of Work.
- [ADR-0019](./architecture/0019-centralize-persistence-behind-repositories-query-services-and-exhaustive-layer-contracts.md) - repository/query split и exhaustive layer contracts.
- [ADR-0020](./architecture/0020-centralize-platform-error-registry-and-http-error-projection.md) - centralized error registry и typed HTTP error projection.
- [ADR-0021](./architecture/0021-centralize-backend-observability-bootstrap-and-structured-telemetry.md) - centralized observability bootstrap, structured logging, tracing, metrics and GlitchTip.
- [ADR-0022](./architecture/0022-group-backend-settings-into-nested-platform-models.md) - grouped backend settings, nested env keys and clearer config ownership.
- [ADR-2000](./engineering/2000-centralize-template-metadata-and-self-consistency-checks.md) - template metadata и self-consistency enforcement.

## Reading Map By Change Area

### Backend platform

Пути:

- `src/backend/api/`
- `src/backend/core/`
- `src/backend/runtime/`
- `src/backend/main.py`
- `src/backend/pyproject.toml`
- `migrations/`
- `alembic.ini`
- backend-related `docker/`

Читать дополнительно:

- [ADR-0005](./architecture/0005-background-jobs-and-workflow-orchestration.md)
- [ADR-0008](./architecture/0008-layered-testing-strategy.md)
- [ADR-0009](./architecture/0009-deployment-topology-and-runtime-model.md)
- [ADR-0010](./architecture/0010-use-taskiq-redis-streams-and-postgresql.md)
- [ADR-0011](./architecture/0011-manage-postgresql-schema-with-alembic.md)
- [ADR-0013](./architecture/0013-adopt-a-flat-backend-service-root-and-bounded-context-layout.md)
- [ADR-0014](./architecture/0014-enforce-backend-dependency-direction-and-import-boundaries.md)
- [ADR-0017](./architecture/0017-standardize-backend-testing-on-pytest-testcontainers-and-full-request-flows.md)
- [ADR-0018](./architecture/0018-enforce-typed-contracts-and-unit-of-work-owned-persistence.md)
- [ADR-0019](./architecture/0019-centralize-persistence-behind-repositories-query-services-and-exhaustive-layer-contracts.md)
- [ADR-0020](./architecture/0020-centralize-platform-error-registry-and-http-error-projection.md)
- [ADR-0021](./architecture/0021-centralize-backend-observability-bootstrap-and-structured-telemetry.md)
- [ADR-0022](./architecture/0022-group-backend-settings-into-nested-platform-models.md)

### Backend apps and product semantics

Пути:

- `src/backend/apps/`
- `src/backend/tests/apps/`

Читать дополнительно:

- [ADR-0013](./architecture/0013-adopt-a-flat-backend-service-root-and-bounded-context-layout.md)
- [ADR-0014](./architecture/0014-enforce-backend-dependency-direction-and-import-boundaries.md)
- [ADR-0017](./architecture/0017-standardize-backend-testing-on-pytest-testcontainers-and-full-request-flows.md)
- [ADR-0018](./architecture/0018-enforce-typed-contracts-and-unit-of-work-owned-persistence.md)
- [ADR-0019](./architecture/0019-centralize-persistence-behind-repositories-query-services-and-exhaustive-layer-contracts.md)
- [ADR-0020](./architecture/0020-centralize-platform-error-registry-and-http-error-projection.md)

Если изменение затрагивает trust, verification, quarantine, promotion, metadata, audit, state или storage semantics, дополнительно читать:

- [ADR-1000](./product/1000-artifact-immutability-and-promotion-model.md)
- [ADR-1001](./product/1001-trust-and-verification-policy.md)
- [ADR-1002](./product/1002-sbom-provenance-and-signatures.md)
- [ADR-1003](./product/1003-quarantine-and-security-gates.md)
- [ADR-1004](./product/1004-storage-strategy-for-artifacts-metadata-and-decisions.md)

### Frontend

Пути:

- `src/frontend/`
- `docs/frontend/`
- frontend-related `docker/`

Читать дополнительно:

- [ADR-0008](./architecture/0008-layered-testing-strategy.md)
- [ADR-0023](./architecture/0023-layer-the-frontend-into-app-pages-features-entities-and-shared.md)
- [ADR-0024](./architecture/0024-introduce-a-ui-adapter-layer-ready-for-external-kits.md)
- [ADR-0025](./architecture/0025-enforce-frontend-import-boundaries-and-architecture-validation.md)
- [ADR-0026](./architecture/0026-adopt-a-lightweight-semantic-design-foundation-for-frontend-primitives.md)

### Specs and contract tests

Пути:

- `specs/`
- `tests/contract/`

Читать дополнительно:

- [ADR-0008](./architecture/0008-layered-testing-strategy.md)

### Repo automation, governance and CI

Пути:

- `.github/`
- `.gitea/`
- `.pre-commit-config.yaml`
- `Makefile`
- `scripts/`
- governance docs и templates

Читать дополнительно:

- [ADR-0007](./architecture/0007-configuration-and-policy-as-code.md)
- [ADR-0015](./architecture/0015-enforce-template-quality-gates-and-governance-baseline.md)
- [ADR-0016](./architecture/0016-support-github-and-gitea-ci-for-template-repositories.md)
- [ADR-0021](./architecture/0021-centralize-backend-observability-bootstrap-and-structured-telemetry.md)
- [ADR-0022](./architecture/0022-group-backend-settings-into-nested-platform-models.md)
- [ADR-2000](./engineering/2000-centralize-template-metadata-and-self-consistency-checks.md)

### ADR and rule changes

Пути:

- `docs/adr/`
- `.aiassistant/rules/`

Читать дополнительно:

- [ADR-0000](./architecture/0000-record-architecture-decisions.md)
- [ADR-0015](./architecture/0015-enforce-template-quality-gates-and-governance-baseline.md)
- [ADR-2000](./engineering/2000-centralize-template-metadata-and-self-consistency-checks.md)

## Maintenance Rules

- если меняется область действия ADR, обновляй этот индекс;
- если ADR связан с другими решениями, поддерживай раздел `Related ADRs`;
- если меняется архитектурное ограничение, обновляй и ADR, и `.aiassistant/rules/`;
- если появляется новый обязательный root-level артефакт или новый control path, это должно быть отражено в ADR и в этом индексе.
