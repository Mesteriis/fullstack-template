---
apply: by file patterns
patterns: src/frontend/**/*, docs/frontend/**/*, docker/Dockerfile, docker/entrypoints/frontend.sh, docker/runs/frontend.sh, docker/nginx/default.conf, scripts/check_frontend_architecture.py, scripts/run_frontend_build.py, scripts/run_frontend_install.py, scripts/run_frontend_lint.py, scripts/run_frontend_lint_fix.py, scripts/run_frontend_tests.py, scripts/run_frontend_types.py
---

# Frontend

Path scope:

- `src/frontend/**`
- `docs/frontend/**`
- `docker/Dockerfile`
- `docker/entrypoints/frontend.sh`
- `docker/runs/frontend.sh`
- `docker/nginx/default.conf`
- `scripts/check_frontend_architecture.py`
- `scripts/run_frontend_build.py`
- `scripts/run_frontend_install.py`
- `scripts/run_frontend_lint.py`
- `scripts/run_frontend_lint_fix.py`
- `scripts/run_frontend_tests.py`
- `scripts/run_frontend_types.py`

Применяй это правило при изменении frontend app, frontend tests и frontend container runtime.

Обязательные ADR:

- [ADR-0001](../../docs/adr/architecture/0001-monorepo-and-bounded-contexts.md)
- [ADR-0002](../../docs/adr/architecture/0002-api-first-and-contract-versioning.md)
- [ADR-0008](../../docs/adr/architecture/0008-layered-testing-strategy.md)
- [ADR-0012](../../docs/adr/architecture/0012-define-repository-layout-and-file-placement-rules.md)
- [ADR-0015](../../docs/adr/architecture/0015-enforce-template-quality-gates-and-governance-baseline.md)
- [ADR-0016](../../docs/adr/architecture/0016-support-github-and-gitea-ci-for-template-repositories.md)
- [ADR-0023](../../docs/adr/architecture/0023-layer-the-frontend-into-app-pages-features-entities-and-shared.md)
- [ADR-0024](../../docs/adr/architecture/0024-introduce-a-ui-adapter-layer-ready-for-external-kits.md)
- [ADR-0025](../../docs/adr/architecture/0025-enforce-frontend-import-boundaries-and-architecture-validation.md)
- [ADR-0026](../../docs/adr/architecture/0026-adopt-a-lightweight-semantic-design-foundation-for-frontend-primitives.md)

Правила:

- frontend остаётся app-local внутри `src/frontend`, без вынесения app-specific code в корень репозитория;
- приложение bootstraps from `app/`, а route-level composition живёт в `pages/`;
- `pages/` и `features/` не используют raw HTML, local `<style>` или direct DOM access вместо `shared/ui`;
- `shared/ui` является единственной primitive/composed UI boundary для app/pages/features и готовится как adapter surface для будущего `ww-ui-kit`;
- cross-layer relative imports запрещены; нижние слои не тянут верхние;
- API surface и typed clients не должны дрейфовать относительно `specs/`;
- lint, type-check, unit tests и production build считаются обязательной частью изменения;
- container runtime для frontend не должен расходиться с CI baseline и smoke-build assumptions.
