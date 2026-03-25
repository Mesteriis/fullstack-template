# ADR-0016: Support GitHub and Gitea CI for template repositories

- Status: Accepted
- Date: 2026-03-25
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0009](./0009-deployment-topology-and-runtime-model.md)
- [ADR-0012](./0012-define-repository-layout-and-file-placement-rules.md)
- [ADR-0015](./0015-enforce-template-quality-gates-and-governance-baseline.md)

## Context

Шаблонный репозиторий должен быть пригоден как для hosted GitHub, так и для self-hosted Gitea installations. Если baseline качества существует только для одного CI окружения, шаблон перестаёт быть переносимым и начинает требовать ручной адаптации сразу после создания проекта.

Дополнительно выбран режим `Dokploy Method 2`, где платформа отслеживает git-репозиторий сама, а CI pipeline отвечает в первую очередь за quality gates, image build validation и security checks, а не за imperative deploy.

## Decision

Шаблон поставляется с двумя совместимыми CI definitions:

- `.github/workflows/ci.yml` для GitHub Actions;
- `.gitea/workflows/ci.yml` для self-hosted Gitea Actions.

Общие правила:

- quality gates в обоих CI должны быть эквивалентны по смыслу;
- pipeline ограничивается максимум двумя параллельными test jobs, после которых может идти общий security/image job;
- backend и frontend проверяются отдельно;
- security/image job выполняет container linting, shell linting, filesystem scanning и smoke build Docker targets;
- Docker images всегда тегируются тремя тегами: `latest`, branch name и commit SHA;
- при `Dokploy Method 2` deploy шаг из CI не обязателен и не является частью базового pipeline.

Gitea-specific baseline:

- workflow использует runner labels `python`, `node` и `main`;
- `main` runner выполняет Docker/security шаги, а `python` и `node` отвечают за language-specific checks.

GitHub-specific baseline:

- workflow использует hosted runners и явную установку Python, `uv`, Node/pnpm и security tooling;
- логика quality gates остаётся эквивалентной Gitea pipeline.

## Consequences

### Positive

- шаблон остаётся переносимым между GitHub и self-hosted Gitea;
- quality gates одинаково работают до выбора конкретной forge platform;
- безопасность Dockerfile и shell entrypoints проверяется в базовом pipeline.

### Negative

- нужно поддерживать две workflow definitions;
- drift между CI конфигурациями становится отдельным риском и требует ревью.

### Neutral

- конкретная deploy automation может быть добавлена позже отдельным ADR без изменения базового CI contract.

## Alternatives considered

- поддерживать только GitHub Actions;
- поддерживать только Gitea Actions;
- оставить адаптацию CI на каждый новый проект после генерации из шаблона.

## Follow-up work

- [x] добавить GitHub workflow
- [x] добавить Gitea workflow
- [x] зафиксировать `Dokploy Method 2` как baseline без CI-driven deploy
- [ ] при необходимости добавить отдельные deploy workflows для environment-specific targets
