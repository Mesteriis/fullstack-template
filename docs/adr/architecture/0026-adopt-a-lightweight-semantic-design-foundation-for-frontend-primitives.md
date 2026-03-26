# ADR-0026: Adopt a lightweight semantic design foundation for frontend primitives

- Status: Accepted
- Date: 2026-03-26
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0008](./0008-layered-testing-strategy.md)
- [ADR-0024](./0024-introduce-a-ui-adapter-layer-ready-for-external-kits.md)
- [ADR-0025](./0025-enforce-frontend-import-boundaries-and-architecture-validation.md)

## Context

The frontend needed stable UI primitives, but styling them with ad-hoc page
rules would make later replacement expensive. The template needs just enough
design foundation to support primitives and migration readiness without turning
the repository into a product design system.

## Decision

Frontend primitives use a lightweight semantic design foundation in
`shared/ui/styles/`:

- tokens define spacing, radius, base color families and type choices;
- semantic roles define surfaces, text, borders and action/state tones;
- primitive and composed styles consume those semantics instead of page-local
  values.

Rules:

- design tokens stay intentionally small and portable;
- styling responsibility belongs to `shared/ui/styles/*`, not to pages or
  features;
- semantic props and tokens are preferred over one-off class names and visual
  hacks.

## Consequences

### Positive

- primitives share one consistent visual and spacing baseline;
- future adapter replacement can map semantics instead of diffing page CSS;
- the frontend gets disciplined styling without a full design-system explosion.

### Negative

- some visual decisions are centralized earlier than in a minimal starter app;
- maintainers must evolve tokens carefully because they become part of the
  primitive contract.

### Neutral

- this is a migration-ready foundation, not final brand styling.

## Alternatives considered

- keep all frontend styling in one root stylesheet;
- let each page or feature own its own visual rules;
- build a very large token matrix before the app needs it.

## Follow-up work

- [x] move frontend styles under `shared/ui/styles/`
- [x] author primitives against semantic roles instead of page-local values
- [ ] keep the semantic token set small unless new primitives genuinely require expansion
