# ADR-0001: Use a monorepo with explicit bounded contexts

- Status: Accepted
- Date: 2026-03-25
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0002](./0002-api-first-and-contract-versioning.md)
- [ADR-0012](./0012-define-repository-layout-and-file-placement-rules.md)
- [ADR-0013](./0013-adopt-a-flat-backend-service-root-and-bounded-context-layout.md)
- [ADR-0014](./0014-enforce-backend-dependency-direction-and-import-boundaries.md)

## Context

Система объединяет несколько приложений, контракты и эксплуатационные артефакты. Без явных границ репозиторий быстро превращается в плоский набор каталогов с высоким coupling и неясной ответственностью.

## Decision

Используется monorepo, но с явными bounded contexts и нейтральным source root.

Базовая структура:

- `src/` для приложений;
- `specs/` для контрактов;
- `tests/` для cross-app сценариев;
- `docs/` для решений и документации;
- `docker/`, `scripts/` для runtime и automation.

Принципы границ:

- приложение владеет своим локальным кодом, manifest-файлами и тестами;
- если в будущем появится repo-wide shared/generated code, для него зарезервирован корень `packages/`, а не произвольные `shared/` или `libs/`;
- если в будущем появится repo-wide IaC или deployment configuration, для него зарезервирован корень `infra/`, а не произвольные альтернативные имена;
- корень репозитория остаётся polyglot и не выглядит как корень одного языка или одного runtime;
- межконтекстные зависимости проходят через явные контракты, а не через произвольные импорты.

## Consequences

### Positive

- проще навигировать по репозиторию;
- легче контролировать границы ответственности;
- проще масштабировать систему под новые приложения и новые стеки.

### Negative

- нужно поддерживать дисциплину по размещению кода;
- ранняя декомпозиция может показаться более строгой, чем ad-hoc подход.

### Neutral

- monorepo не означает монолитную архитектуру внутри кода.

## Alternatives considered

- плоская структура без bounded contexts;
- несколько отдельных репозиториев;
- структура только по технологическим слоям без доменных границ.

## Follow-up work

- [ ] зафиксировать правила межконтекстных зависимостей
- [ ] описать ownership для основных областей
- [ ] определить минимальный shared kernel
