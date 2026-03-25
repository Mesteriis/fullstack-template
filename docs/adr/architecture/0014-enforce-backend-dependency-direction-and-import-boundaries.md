# ADR-0014: Enforce backend dependency direction and import boundaries

- Status: Accepted
- Date: 2026-03-25
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0008](./0008-layered-testing-strategy.md)
- [ADR-0013](./0013-adopt-a-flat-backend-service-root-and-bounded-context-layout.md)
- [ADR-0015](./0015-enforce-template-quality-gates-and-governance-baseline.md)

## Context

Даже при хорошем package layout архитектура быстро размывается, если не зафиксировано направление зависимостей. В этом случае:

- `api` начинает содержать orchestration и прямой доступ к persistence;
- `domain` тянет framework- или ORM-специфичные зависимости;
- один bounded context импортирует внутренности другого;
- `core` превращается в бесконтрольный shared bucket;
- runtime workers начинают обходить application layer и дублировать бизнес-логику.

Нужно явно определить, кто может импортировать кого и какие исключения допустимы.

## Decision

Для backend service действует unidirectional dependency model.

На уровне top-level packages:

- `src/backend` является service root, а не import namespace;
- `api` может зависеть от `apps` и `core`;
- `runtime` может зависеть от `apps` и `core`;
- `apps` может зависеть от `core`;
- `core` не должен зависеть от `api`, `runtime` или конкретных bounded contexts, кроме bootstrap-level wiring, которое собирает приложение.

На уровне bounded context допустимо следующее направление:

```text
api -> application -> domain
infrastructure -> domain
application -> contracts
api -> contracts
infrastructure -> contracts
```

Ограничения по слоям:

- `domain` не импортирует `api`, `application`, `infrastructure`, ORM models, transport objects и external SDKs;
- `application` не импортирует transport-specific types и не знает о framework lifecycle;
- `api` не содержит бизнес-правила и не работает напрямую с persistence models;
- `contracts` остаются лёгкими typed boundary objects и не зависят от transport или persistence implementation;
- `infrastructure` реализует adapters и persistence, но не владеет domain rules.

Cross-context imports:

- bounded context не импортирует внутренности другого bounded context;
- межконтекстное взаимодействие идёт через `contracts`, явные public facades или события;
- прямые импорты `api`, `application.services` и `infrastructure` другого context-а считаются запрещёнными по умолчанию.

Enforcement model:

- bootstrap modules могут иметь ограниченные исключения для composition root;
- import boundaries должны постепенно усиливаться через linter и CI hooks;
- новые исключения допускаются только как явный архитектурный компромисс, а не как молчаливое правило.

## Consequences

### Positive

- архитектурные границы становятся проверяемыми, а не декларативными;
- bounded contexts сохраняют ownership над своей логикой;
- уменьшается вероятность framework leakage в domain layer;
- runtime workers и API начинают использовать одни и те же application contracts.

### Negative

- появляются дополнительные ограничения на быстрые short-term implementation shortcuts;
- часть кода приходится перемещать в contracts или public facades вместо прямых импортов.

### Neutral

- конкретный инструмент enforcement может меняться, если сохраняется сама модель направленных зависимостей.

## Alternatives considered

- не фиксировать import boundaries и полагаться на code review;
- разрешить bounded contexts свободно импортировать внутренности друг друга;
- использовать только naming conventions без явной dependency model.

## Follow-up work

- [x] добавить базовую import-linter configuration в backend tooling
- [ ] расширить CI checks до автоматической проверки top-level и cross-context boundaries
- [ ] добавить правила для domain-safe modules внутри `core`
