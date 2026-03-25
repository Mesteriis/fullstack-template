# ADR-0015: Enforce template quality gates and governance baseline

- Status: Accepted
- Date: 2026-03-25
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0002](./0002-api-first-and-contract-versioning.md)
- [ADR-0008](./0008-layered-testing-strategy.md)
- [ADR-0012](./0012-define-repository-layout-and-file-placement-rules.md)
- [ADR-0014](./0014-enforce-backend-dependency-direction-and-import-boundaries.md)
- [ADR-0016](./0016-support-github-and-gitea-ci-for-template-repositories.md)

## Context

Шаблонный репозиторий ценен только если он переносит не набор файлов, а работающий engineering baseline. Без этого новые проекты начинают быстро расходиться:

- архитектурные ограничения остаются только в ADR и не проверяются автоматически;
- spec-first сводится к декларации без naming и placement rules;
- локальный developer workflow и CI дают разный результат;
- governance артефакты вроде `CODEOWNERS`, contribution guide и security policy добавляются нерегулярно;
- базовые security checks появляются слишком поздно и уже после появления сервисов.

Нужен единый baseline, который будет поставляться вместе с шаблоном и проходить machine-enforced validation.

## Decision

Шаблонный репозиторий обязан включать единый quality and governance baseline:

- machine-enforced checks для ADR, repo structure, backend architecture и spec placement;
- локальный automation layer через `Makefile` и `pre-commit`;
- governance artifacts: `CODEOWNERS`, `CONTRIBUTING.md`, `SECURITY.md`, issue/PR templates;
- security baseline checks: dependency audit, `bandit`, `trivy`, `hadolint`, `shellcheck`;
- frontend baseline: lint, type-check, unit tests и production build;
- backend baseline: lint, format, type-check, import boundaries, architecture checks и tests.

Spec-first baseline:

- `specs/` остаётся source of truth для контрактов;
- naming rules для OpenAPI, AsyncAPI и JSON Schema валидируются автоматически;
- generated artifacts считаются производными и не подменяют исходные контракты.

DX baseline:

- репозиторий должен содержать короткий набор canonical commands для sync, check, lint, test и build;
- локальные hooks должны быть совместимы с CI pipeline, а не вводить собственный альтернативный процесс.

## Consequences

### Positive

- новый проект получает не только scaffold, но и рабочую инженерную дисциплину;
- architectural drift ловится раньше и дешевле;
- onboarding становится короче и предсказуемее;
- security и governance перестают быть необязательным follow-up.

### Negative

- стартовый шаблон становится тяжелее по числу checks и служебных файлов;
- поддержка baseline требует регулярного обновления tooling и workflow definitions.

### Neutral

- конкретные инструменты внутри baseline могут эволюционировать, если сохраняется сам принцип machine-enforced quality gates.

## Alternatives considered

- ограничиться только README и ADR без автоматических checks;
- отдать governance и security baseline на усмотрение каждого нового проекта;
- включать только language-specific lint/test без repo-wide правил.

## Follow-up work

- [x] добавить repo-wide validators для architecture и specs
- [x] добавить governance baseline files
- [x] добавить DX entrypoints для локального запуска quality gates
- [ ] добавить template bootstrap/init flow для переименования project-specific identifiers
