# Contributing

## Workflow

1. Update specs first when changing public contracts.
2. Keep ADRs in sync with architecture-level decisions.
3. Run `make doctor` before opening a PR.
4. Run `make ci` before opening a PR that changes runtime, CI, tooling or contracts.
5. Include migrations in the same PR as relational schema changes.

## Placement Rules

- App code lives under `src/`
- Cross-app tests live only in `tests/`
- Migrations live in `migrations/`
- Contract sources live in `specs/`

## Pull Requests

- explain the intent
- describe contract, schema or runtime impact
- list manual verification if automation is not enough
