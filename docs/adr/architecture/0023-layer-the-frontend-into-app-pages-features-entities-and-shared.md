# ADR-0023: Layer the frontend into app, pages, features, entities and shared

- Status: Accepted
- Date: 2026-03-26
- Deciders: avm
- Supersedes:
- Superseded by:

## Related ADRs

- [ADR-0008](./0008-layered-testing-strategy.md)
- [ADR-0012](./0012-define-repository-layout-and-file-placement-rules.md)
- [ADR-0015](./0015-enforce-template-quality-gates-and-governance-baseline.md)

## Context

Frontend skeleton directories already existed in the repository, but the actual
application still lived as a flat Vite starter rooted in `App.vue`,
`main.ts` and `styles.css`. That gap made the declared structure misleading:

- `app/`, `pages/`, `features/`, `entities/` and `shared/` were present but not used;
- route-level code had no shell, no router contract and no real layering;
- frontend discipline lagged behind the backend architecture baseline.

The maximum template needs the frontend to be structurally real, not
aspirational.

## Decision

The frontend is layered as follows:

- `app/` owns bootstrap, router and the application shell;
- `pages/` own route-level composition only;
- `features/` own reusable user-facing slices;
- `entities/` own typed domain-facing models and endpoint contracts;
- `shared/` owns config, API infrastructure, low-level helpers and UI
  primitives.

Rules:

- frontend bootstrap moves into `app/`;
- the root Vite starter files `App.vue`, `main.ts` and `styles.css` are removed
  from the frontend root;
- routes render pages through an app shell rather than directly mounting a
  demo component.

## Consequences

### Positive

- the frontend structure now matches the repository contract;
- layering becomes explicit enough for machine validation;
- app/pages/features/entities/shared responsibilities stop drifting.

### Negative

- even small frontend changes now require choosing the correct layer;
- more files exist up front than in a flat starter scaffold.

### Neutral

- this does not create product features by itself; it creates architectural
  ownership boundaries.

## Alternatives considered

- keep the flat Vite starter and rely on future cleanup;
- keep the directories as placeholders without moving real code into them;
- collapse features and entities into pages for convenience.

## Follow-up work

- [x] move frontend bootstrap into `app/`
- [x] add router-based page composition
- [x] make `features/` and `entities/` part of the real frontend graph
- [ ] keep new frontend code aligned with the layered ownership model
