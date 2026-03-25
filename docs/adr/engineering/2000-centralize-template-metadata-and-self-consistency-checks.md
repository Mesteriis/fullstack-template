# ADR-2000: Centralize template metadata and self-consistency checks

- Status: Accepted
- Date: 2026-03-25
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0000](../architecture/0000-record-architecture-decisions.md)
- [ADR-0015](../architecture/0015-enforce-template-quality-gates-and-governance-baseline.md)
- [ADR-0016](../architecture/0016-support-github-and-gitea-ci-for-template-repositories.md)

## Context

Максимально opinionated template быстро деградирует, если внутри него появляются независимые hardcoded assumptions про owner, decider, golden path commands и pipeline semantics. В этом случае:

- скрипты начинают расходиться по ownership и decider constants;
- Makefile, pre-commit и CI больше не описывают один и тот же engineering baseline;
- dual-CI становится формально включённой, но фактически несимметричной;
- `specs/` может остаться набором placeholder-директорий без канонических примеров контрактов.

Для golden-master template нужны не только checks на код и структуру, но и checks на согласованность самого шаблона.

## Decision

Шаблон использует два обязательных механизма:

- `template.meta.toml` как единый источник script-level metadata для owner, ADR decider и типа шаблона;
- self-consistency checks, которые валидируют согласованность Makefile, hooks, CI, docker targets и contract scaffold.

Правила:

- ownership и ADR decider не должны быть захардкожены в validation scripts;
- `Makefile`, pre-commit, GitHub CI и Gitea CI должны оставаться семантически согласованными;
- dual-CI проверяется отдельным symmetry check, а не вручную;
- placeholder-only contract directories не считаются допустимым состоянием максимального шаблона;
- engineering baseline самого шаблона фиксируется как ADR-worthy решение, а не как случайный набор скриптов.

## Consequences

### Positive

- ownership assumptions централизуются и не размазываются по скриптам;
- шаблон становится self-validating не только по коду, но и по собственной инженерной форме;
- легче сопровождать dual-CI и golden-master workflow без скрытого drift;
- derived templates получают более устойчивый исходный baseline.

### Negative

- растёт количество meta-validation checks;
- изменение template governance требует обновлять несколько связанных артефактов.

### Neutral

- `template.meta.toml` не является runtime configuration или feature-flag system; это repository metadata для инженерных инструментов шаблона.

## Alternatives considered

- держать owner и ADR decider как hardcoded constants внутри скриптов;
- считать Makefile, hooks и CI независимыми слоями без symmetry validation;
- разрешить placeholder-only `specs/` scaffold без канонических contract examples.

## Follow-up work

- [x] ввести `template.meta.toml`
- [x] добавить template consistency check
- [x] добавить CI symmetry check
- [ ] при появлении новых engineering-level governance decisions продолжать фиксировать их в `docs/adr/engineering/`
