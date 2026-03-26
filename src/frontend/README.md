# Frontend

Strict Vue frontend scaffold for the maximum template repository.

## Architecture

- `app/` owns bootstrap, router, and the application shell
- `pages/` own route-level composition
- `features/` own reusable business-facing slices
- `entities/` own typed domain-facing models and endpoint contracts
- `shared/` owns the lowest-level config, API, helpers, and UI adapter boundary

UI code outside `shared/ui` is expected to compose primitives, not invent new
raw markup or local styling systems.

## Commands

```bash
pnpm install
pnpm dev
pnpm lint
pnpm architecture:check
pnpm type-check
pnpm test:unit
pnpm build
```
