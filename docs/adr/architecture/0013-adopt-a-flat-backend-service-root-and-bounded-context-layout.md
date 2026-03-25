# ADR-0013: Adopt a flat backend service root and bounded-context layout

- Status: Accepted
- Date: 2026-03-25
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0008](./0008-layered-testing-strategy.md)
- [ADR-0009](./0009-deployment-topology-and-runtime-model.md)
- [ADR-0012](./0012-define-repository-layout-and-file-placement-rules.md)
- [ADR-0014](./0014-enforce-backend-dependency-direction-and-import-boundaries.md)

## Context

Repo layout сам по себе не отвечает на вопрос, как должен быть устроен backend service изнутри. Без отдельного решения код быстро деградирует в смесь корневых каталогов вроде `api/`, `domain/`, `infrastructure/` без явной top-level модели, а импорты начинают опираться на случайный namespace layer, который не несёт архитектурной ценности.

Это создаёт несколько проблем:

- `src/backend` получает лишний промежуточный namespace layer, который не даёт новых архитектурных границ;
- слои верхнего уровня смешиваются с bounded contexts;
- новые модули копируют layout случайным образом;
- backend структура теряет связь между transport layer, application layer, platform kernel и runtime workers.

Нужно зафиксировать плоский backend service root, который будет масштабироваться по мере появления новых bounded contexts без дополнительной вложенности.

## Decision

Каждый backend service использует плоский service root прямо внутри `src/backend/`.

Repository layout:

```text
src/backend/
  api/
  apps/
  core/
  runtime/
  main.py
  tests/
  pyproject.toml
```

Правила package layout:

- `src/backend` является одновременно service root для backend-кода и repository-local root для manifests, tests и tooling;
- runtime imports backend service начинаются сразу с `api.*`, `apps.*`, `core.*` и `runtime.*`;
- top-level backend service root делится на `api`, `apps`, `core` и `runtime`;
- `apps/` содержит bounded contexts;
- `core/` содержит минимальный shared platform kernel;
- `runtime/` содержит workers, stream consumers, schedulers и orchestration primitives;
- `tests/` повторяет архитектурную топологию backend service root, а не legacy root-layer layout.

Каждый bounded context в `apps/<context>/` использует единый шаблон:

```text
apps/<context>/
  api/
  application/
  contracts/
  domain/
  infrastructure/
```

Назначение top-level packages:

- `api` отвечает за HTTP и transport wiring;
- `apps` отвечает за domain-owned bounded contexts;
- `core` отвечает за shared settings, bootstrap, db primitives и другие стабильные платформенные модули;
- `runtime` отвечает за async workers, background orchestration и messaging runtime.

Назначение context layers:

- `api` для transport adapters, dependency wiring и response mapping;
- `application` для use cases и orchestration;
- `contracts` для typed boundary models;
- `domain` для business rules, entities и policies;
- `infrastructure` для persistence и технических adapters.

## Consequences

### Positive

- backend получает более короткий и прозрачный import graph без искусственного namespace layer;
- bounded contexts становятся первым уровнем архитектуры, а не побочным эффектом структуры файлов;
- проще вводить static checks для import boundaries и package ownership;
- bootstrap, runtime и transport responsibilities перестают смешиваться на корне backend service.

### Negative

- начальная структура выглядит тяжелее, чем flat scaffold;
- для небольших временных модулей нужно сразу выбирать правильный bounded context и слой.

### Neutral

- конкретные имена top-level packages фиксированы этим ADR и не требуют дополнительного service package wrapper.

## Alternatives considered

- хранить `api`, `domain`, `infrastructure` и `settings` прямо в корне `src/backend` без разделения на bounded contexts;
- использовать `src.backend.*` как runtime import namespace;
- оборачивать backend в дополнительный service package внутри `src/backend`;
- раскладывать backend по техническим слоям без bounded contexts.

## Follow-up work

- [x] создать initial backend service root и system context scaffold
- [x] перевести минимальный FastAPI entrypoint на плоский service root
- [ ] добавить static checks для import boundaries между top-level packages и context layers
