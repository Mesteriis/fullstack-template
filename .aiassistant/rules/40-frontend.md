---
apply: by file patterns
patterns: src/frontend/**
---

# Frontend

Применяй это правило при изменении frontend app, frontend tests и frontend container runtime.

Обязательные ADR:

- [ADR-0001](../../docs/adr/architecture/0001-monorepo-and-bounded-contexts.md)
- [ADR-0002](../../docs/adr/architecture/0002-api-first-and-contract-versioning.md)
- [ADR-0008](../../docs/adr/architecture/0008-layered-testing-strategy.md)
- [ADR-0012](../../docs/adr/architecture/0012-define-repository-layout-and-file-placement-rules.md)
- [ADR-0015](../../docs/adr/architecture/0015-enforce-template-quality-gates-and-governance-baseline.md)
- [ADR-0016](../../docs/adr/architecture/0016-support-github-and-gitea-ci-for-template-repositories.md)

Правила:

- frontend остаётся app-local внутри `src/frontend`, без вынесения app-specific code в корень репозитория;
- API surface и typed clients не должны дрейфовать относительно `specs/`;
- lint, type-check, unit tests и production build считаются обязательной частью изменения;
- container runtime для frontend не должен расходиться с CI baseline и smoke-build assumptions.
