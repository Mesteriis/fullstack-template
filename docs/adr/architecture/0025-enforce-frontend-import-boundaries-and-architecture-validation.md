# ADR-0025: Enforce frontend import boundaries and architecture validation

- Status: Accepted
- Date: 2026-03-26
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0015](./0015-enforce-template-quality-gates-and-governance-baseline.md)
- [ADR-0016](./0016-support-github-and-gitea-ci-for-template-repositories.md)
- [ADR-0023](./0023-layer-the-frontend-into-app-pages-features-entities-and-shared.md)
- [ADR-0024](./0024-introduce-a-ui-adapter-layer-ready-for-external-kits.md)

## Context

Layered folders alone do not protect the frontend architecture. Without
validation, developers can silently:

- import upward across layers;
- bypass aliases with relative cross-layer imports;
- reintroduce raw HTML and local styling into pages and features;
- let the frontend drift away from the same governance level as the backend.

## Decision

The repository adds explicit frontend architecture validation as a required
quality gate.

Validation responsibilities:

- forbid cross-layer relative imports;
- enforce allowed dependency directions between `app`, `pages`, `features`,
  `entities` and `shared`;
- fail when legacy root frontend files return;
- fail when pages or features use raw HTML, local `<style>` blocks, inline
  styles or direct DOM globals;
- run through `make check`, `make doctor`, `make frontend-lint` and `make ci`.

ESLint complements, but does not replace, the repository-level architecture
checker.

## Consequences

### Positive

- frontend boundaries become machine-enforced instead of advisory;
- local and CI workflows keep the same frontend discipline;
- the template can evolve without reintroducing starter-grade drift.

### Negative

- contributors must satisfy more checks for frontend changes;
- some enforcement is intentionally opinionated and stricter than default Vue tooling.

### Neutral

- the checker may use pragmatic parsing techniques; exact parser choice is less
  important than preserving the governance rule.

## Alternatives considered

- rely only on README guidance and code review;
- use ESLint alone for all boundary validation;
- postpone frontend architecture checks until the app grows larger.

## Follow-up work

- [x] add `scripts/check_frontend_architecture.py`
- [x] wire the checker into Makefile and hooks
- [ ] evolve the checker when new stable frontend layers appear
