# ADR-0024: Introduce a UI adapter layer ready for external kits

- Status: Accepted
- Date: 2026-03-26
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0012](./0012-define-repository-layout-and-file-placement-rules.md)
- [ADR-0023](./0023-layer-the-frontend-into-app-pages-features-entities-and-shared.md)

## Context

The frontend needed reusable primitives, but importing raw HTML or ad-hoc local
components directly into pages and features would couple the template to its
temporary implementation.

The template also needs to prepare for future adoption of `ww-ui-kit` without a
large rewrite.

## Decision

The frontend introduces a local UI adapter layer under `shared/ui/` with two
zones:

- `primitives/` for low-level layout, typography and action surfaces;
- `composed/` for thin reusable patterns built on those primitives.

The public surface is exported only through `shared/ui/index.ts`.

Rules:

- app/pages/features import UI only from `shared/ui`;
- component APIs stay stable and semantic, using props like `variant`, `tone`,
  `size`, `align`, `padding`, `radius` and `as`;
- slots are preferred over product-specific convenience props;
- business logic is forbidden inside shared UI components.

## Consequences

### Positive

- migration to `ww-ui-kit` can happen behind the same local `App*` interfaces;
- page and feature code no longer depends on scattered markup decisions;
- UI primitives become governed infrastructure rather than demo code.

### Negative

- the repository carries a temporary local UI implementation;
- maintainers must resist adding product-specific behavior into `shared/ui`.

### Neutral

- the local adapter layer is not a full design system; it is a compatibility
  and discipline boundary.

## Alternatives considered

- let pages and features render raw HTML directly;
- import a future external UI kit directly into route code;
- wait for `ww-ui-kit` before creating any stable local UI boundary.

## Follow-up work

- [x] create `shared/ui/primitives`
- [x] create `shared/ui/composed`
- [x] document the UI boundary and migration rules
- [ ] replace local implementations behind the same interfaces when the external kit is adopted
