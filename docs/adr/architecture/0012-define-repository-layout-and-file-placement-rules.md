# ADR-0012: Define repository layout and file placement rules

- Status: Accepted
- Date: 2026-03-25
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0001](./0001-monorepo-and-bounded-contexts.md)
- [ADR-0002](./0002-api-first-and-contract-versioning.md)
- [ADR-0013](./0013-adopt-a-flat-backend-service-root-and-bounded-context-layout.md)
- [ADR-0015](./0015-enforce-template-quality-gates-and-governance-baseline.md)
- [ADR-0016](./0016-support-github-and-gitea-ci-for-template-repositories.md)

## Context

Высокоуровневое решение о monorepo и bounded contexts уже принято, но без точных правил размещения файлов репозиторий быстро начинает деградировать: language-specific manifest files возвращаются в корень, тесты лежат далеко от owning code, а инфраструктурные каталоги появляются ad hoc. Дополнительно важно не смешивать два уровня решений: repo-wide layout и внутреннюю package architecture отдельных приложений.

## Decision

Фиксируется базовая layout model репозитория:

- `src/backend/` для backend service roots, backend manifests и backend tests;
- `src/frontend/` для frontend application code, frontend manifests и frontend tests;
- `specs/` для OpenAPI, AsyncAPI и JSON Schema contracts;
- `migrations/` для versioned migrations primary relational database;
- `tests/contract` и `tests/e2e` только для cross-app scenarios;
- `docker/`, `scripts/` для runtime, deployment и automation.

Правила placement:

- application-local manifests лежат рядом с owning app, а не в корне;
- backend test suites живут в `src/backend/tests/` и повторяют архитектурную топологию backend service root;
- frontend component-level tests живут рядом с frontend app root;
- корневой `tests/` не используется для app-local test suites;
- пустые, но обязательные каталоги могут храниться через `.gitkeep`;
- новая директория в корне репозитория допустима только если она относится к repo-wide concerns, а не к одному приложению.
- `packages/` не является обязательной частью текущего layout, но зарезервирован для будущего shared/generated repo-wide code именно под этим именем;
- `infra/` не является обязательной частью текущего layout, но зарезервирован для будущего IaC и deployment-level configuration именно под этим именем;
- внутренняя структура backend service root не определяется этим ADR и фиксируется отдельным архитектурным решением.

## Consequences

### Positive

- layout репозитория становится предсказуемым;
- проще валидировать структуру автоматически;
- не создаются пустые каталоги без реального владельца и сценария использования;
- уменьшается риск возвращения к Python-first или framework-first корню.

### Negative

- поддержание структуры требует дисциплины;
- временные экспериментальные файлы нужно сразу класть в правильное место, а не в корень.

### Neutral

- layout не определяет архитектуру модулей внутри каждого приложения, а только правила размещения на уровне репозитория.

## Alternatives considered

- ограничиться только общим ADR про monorepo;
- не фиксировать точную layout model и решать placement case-by-case;
- хранить app-local tests и manifests в корне репозитория.

## Follow-up work

- [x] поддерживать layout через автоматическую проверку в `pre-commit`
- [x] отделить repo-wide layout rules от backend service architecture
- [x] убрать из текущего scaffold необязательные `packages/` и `infra/`, оставив их как reserved roots
- [ ] документировать новые repo-wide каталоги отдельным ADR при необходимости
- [ ] синхронизировать contribution guide с layout rules
