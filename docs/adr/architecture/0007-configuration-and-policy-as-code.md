# ADR-0007: Keep configuration and operational policy under version control

- Status: Accepted
- Date: 2026-03-25
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0006](./0006-authn-authz-and-machine-identities.md)
- [ADR-0015](./0015-enforce-template-quality-gates-and-governance-baseline.md)
- [ADR-1001](../product/1001-trust-and-verification-policy.md)
- [ADR-1003](../product/1003-quarantine-and-security-gates.md)

## Context

Операционные правила, trust policy, routing rules, thresholds и feature toggles не должны жить только в UI, в базе данных или в памяти отдельных операторов. Такие решения требуют review, diff и rollback.

## Decision

Конфигурация и policy, влияющие на поведение платформы, хранятся как code/config под version control.

Это относится к:

- operational policy;
- trust and verification rules;
- environment-specific configuration;
- allow/deny lists;
- thresholds и gates;
- override rules.

Изменение таких правил проходит review и валидацию до применения.

## Consequences

### Positive

- появляется reviewable history изменения правил;
- проще делать rollback и анализировать diff;
- выше воспроизводимость между окружениями.

### Negative

- меньше мгновенной операторской гибкости;
- нужны безопасные механизмы загрузки и валидации policy.

### Neutral

- UI над policy-as-code допустим, если он генерирует versioned source of truth.

## Alternatives considered

- policy только в базе данных;
- policy только в UI;
- ручные overrides без versioned source of truth.

## Follow-up work

- [ ] выбрать format для policy
- [ ] описать validation pipeline
- [ ] определить override process
