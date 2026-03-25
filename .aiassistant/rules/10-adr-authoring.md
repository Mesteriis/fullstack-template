---
apply: by file patterns
patterns: docs/adr/**/*, .aiassistant/rules/**/*
---

# ADR And Rules Authoring

Применяй это правило при изменении `docs/adr/` и `.aiassistant/rules/`.

Обязательные требования:

- сначала прочитай [docs/adr/INDEX.md](../../docs/adr/INDEX.md);
- не меняй ADR изолированно от индексов и rule-файлов, если меняется область действия решения;
- поддерживай разделение на architecture ADR, product ADR и engineering ADR;
- сохраняй статус, дату, deciders и историю через `Supersedes` или `Superseded by`;
- добавляй или обновляй `Related ADRs`, если решение зависит от других ADR;
- не превращай coding style в ADR без архитектурного основания.

Минимальный набор ADR для чтения:

- [ADR-0000](../../docs/adr/architecture/0000-record-architecture-decisions.md)
- [ADR-0001](../../docs/adr/architecture/0001-monorepo-and-bounded-contexts.md)
- [ADR-0012](../../docs/adr/architecture/0012-define-repository-layout-and-file-placement-rules.md)
- [ADR-0015](../../docs/adr/architecture/0015-enforce-template-quality-gates-and-governance-baseline.md)
- [ADR-0016](../../docs/adr/architecture/0016-support-github-and-gitea-ci-for-template-repositories.md)
- [ADR-2000](../../docs/adr/engineering/2000-centralize-template-metadata-and-self-consistency-checks.md)
