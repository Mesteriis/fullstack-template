# ADR-1003: Introduce explicit quarantine and security gates

- Status: Accepted
- Date: 2026-03-25
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0004](../architecture/0004-observability-and-audit-trail.md)
- [ADR-1000](./1000-artifact-immutability-and-promotion-model.md)
- [ADR-1001](./1001-trust-and-verification-policy.md)
- [ADR-1002](./1002-sbom-provenance-and-signatures.md)

## Context

Часть артефактов нельзя просто "не промоутить". Их нужно удерживать от потребления, передавать на ручной разбор, помечать как подозрительные и сохранять forensic trail.

## Decision

Вводится quarantine как отдельное состояние и отдельная operational model.

Артефакт переводится в quarantine, если:

- обнаружен high-risk verdict;
- нарушена trust policy;
- источник признан компрометированным;
- есть признаки tampering;
- security operator выполнил ручную изоляцию.

Security gates и quarantine model применяются явно, а не через неформальные operator conventions.

## Consequences

### Positive

- появляется понятная operational модель для suspicious artifacts;
- легче отделить "не проверено" от "опасно";
- улучшается incident response.

### Negative

- потребуется UI/API для расследования и override;
- нужны правила выхода из quarantine.

### Neutral

- quarantine может быть как автоматической, так и ручной.

## Alternatives considered

- только soft-fail без quarantine;
- просто deny без отдельного состояния;
- удаление подозрительных артефактов из системы.

## Follow-up work

- [ ] определить quarantine reasons taxonomy
- [ ] описать release and unquarantine flow
- [ ] определить incident annotation model
