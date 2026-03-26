# Frontend

Strict Vue frontend scaffold for the maximum template repository.

## Architecture

- `app/` owns bootstrap, router, and the application shell
- `pages/` own route-level composition
- `features/` own reusable business-facing slices
- `entities/` own typed domain-facing models and endpoint contracts
- `shared/` owns the lowest-level config, API, helpers, and UI adapter boundary
- `shared/api/generated/` contains derived frontend API artifacts generated from `specs/openapi/platform.openapi.yaml`

UI code outside `shared/ui` is expected to compose primitives, not invent new
raw markup or local styling systems.

Generated API files are derived artifacts. Do not edit them manually. Refresh
them from the spec instead.

Frontend runtime config is read from the repository-root `.env` via Vite `envDir`.
Shared defaults come from `APP__`, `API__`, and a safe subset of `OBSERVABILITY__`.
Only the derived safe subset plus optional `VITE_*` overrides are exposed to browser code.

## Commands

```bash
make help
make install
make api-generate
make api-check
make dev
make lint
make architecture-check
make types
make test
make build
make compose-up
make compose-down
```
