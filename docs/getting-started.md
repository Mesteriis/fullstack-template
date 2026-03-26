# Getting Started

This document is the fast path for new developers. Read this before going deep
into ADRs.

## Prerequisites

Required local tools:

- `git`
- `make`
- `uv`
- `pnpm`
- `pre-commit`
- `docker`

If you want the full local quality pipeline, you also need:

- `shellcheck`
- `hadolint`
- `trivy`

You can verify the expected toolchain with:

```bash
make doctor
```

## Environment Setup

Copy the template env file at the repository root:

```bash
make init-env
```

The backend reads the repository-root `.env` file. Each settings section owns its
own namespace and only consumes its own prefix:

- `APP__*`
- `API__*`
- `DB__*`
- `BROKER__*`
- `SYSTEM__*`
- `OBSERVABILITY__*`

The defaults are already wired for local development:

- PostgreSQL on `localhost:5432`
- Redis on `localhost:6379`
- backend API on `http://localhost:8000`

The frontend reads the same repository-root `.env` file through Vite `envDir`.
By default it derives shared values from the backend namespaces:

- `APP__NAME` for the app title
- `APP__VERSION` / `APP__ENVIRONMENT` for release/environment fallbacks
- `OBSERVABILITY__*` for shared observability defaults
- `API__HOST` / `API__PORT` for the dev proxy target

Only a safe derived subset is exposed to browser code. Backend-only values such
as database settings or observability headers are not exposed. By default the
frontend uses the current browser origin and Vite proxies `/api` to the backend.

If you need to override frontend settings, add or edit `VITE_*` variables in the
same root `.env`, for example:

```env
VITE_DEV_PROXY_TARGET=http://127.0.0.1:8000
VITE_OBSERVABILITY_WEB_VITALS_ENABLED=true
```

The frontend works without an extra env file for local development.

Note: the backend intentionally targets Python 3.14. Syntax that is valid in
Python 3.14 is part of the template baseline and should not be downgraded for
older interpreters.

## Adding A Bounded Context

When you add a new bounded context, keep the repository shape strict:

1. Create the backend slice under `src/backend/apps/<context>/` with `api/`,
   `application/`, `contracts/`, `domain/`, and `infrastructure/`.
2. Add or update the public HTTP contract in `specs/openapi/platform.openapi.yaml`
   before wiring the transport layer.
3. Regenerate frontend API bindings with `cd src/frontend && make api-generate`.
4. Add frontend ownership in `src/frontend/entities/<context>/`,
   `src/frontend/features/<context>/`, and `src/frontend/pages/` only where it
   belongs.
5. Add backend tests near the bounded context, then update cross-app contract or
   e2e tests only when the public surface changes.

Keep `specs/` as the source of truth and let generated/frontend boundary code
follow from it.

## Install Dependencies

Bootstrap both apps and install local git hooks:

```bash
make bootstrap
```

## Start Local Services

Choose one local runtime mode.

Full Docker ensemble:

```bash
make compose-up
```

Manual mode:

Use your own PostgreSQL and Redis, or start quick containers:

```bash
docker run -d --name fullstack-template-postgres \
  -e POSTGRES_USER=fullstack_template \
  -e POSTGRES_PASSWORD=fullstack_template \
  -e POSTGRES_DB=fullstack_template \
  -p 5432:5432 postgres:17

docker run -d --name fullstack-template-redis \
  -p 6379:6379 redis:7-alpine
```

## Run The Backend

These steps are for manual mode. The Docker ensemble already runs migrations
and starts the backend container for you.

Apply migrations first:

```bash
cd src/backend && make migrate
```

Start the API:

```bash
cd src/backend && uv run uvicorn main:app --reload
```

Useful backend URLs:

- root metadata: `http://localhost:8000/`
- docs: `http://localhost:8000/docs`
- health: `http://localhost:8000/api/v1/system/health`

## Run The Frontend

This step is for manual mode. The Docker ensemble already serves the frontend
shell for you.

In another terminal:

```bash
cd src/frontend && make dev
```

Frontend URL:

- app shell: `http://localhost:5173/`

## Docker Compose Options

If you prefer containerized local runtime:

- full ensemble: `make compose-up`
- backend-only stack: `docker compose --env-file .env -f src/backend/docker-compose.yml up --build`
- frontend-only shell: `docker compose --env-file .env -f src/frontend/docker-compose.yml up --build`

The frontend-only compose file proxies `/api` to `BACKEND_UPSTREAM`. By default
it targets `http://host.docker.internal:8000`, so it expects a backend already
running on the host or another reachable Docker network.

If default host ports are already in use, override
`POSTGRES_HOST_PORT`, `REDIS_HOST_PORT`, `BACKEND_HOST_PORT`, or
`FRONTEND_HOST_PORT` when running `docker compose`.

## Quality Checks

Common commands:

- `make init-env`
- `make check`
- `make contract-parity`
- `make lint`
- `make test`
- `make contract-test`
- `make e2e-test`
- `make build`
- `make ci`

App-specific commands:

- backend commands: `cd src/backend && make help`
- frontend commands: `cd src/frontend && make help`
- frontend API generation: `cd src/frontend && make api-generate`
- backend tests: `cd src/backend && make test`
- backend migration tests: `cd src/backend && make test-migrations`
- frontend tests: `cd src/frontend && make test`
- frontend build: `cd src/frontend && make build`

## Typical Developer Workflow

1. Read `README.md` and this document.
2. Check `specs/` before changing public contracts.
3. Read `docs/adr/INDEX.md` before changing architecture, runtime or governance.
4. Make the change in the owning layer only.
5. Run the smallest relevant checks locally.
6. Run `make doctor` and `make ci` before a large PR or infrastructure change.

Backend test note:
- backend tests include `pytest-alembic`;
- migration checks run against a dedicated PostgreSQL database created inside a
  `testcontainers` container, not against your live local database.

## First-Run Problems

`uv` or `pnpm` is missing:
- install the missing tool, then rerun `make doctor`.

Backend cannot connect to PostgreSQL or Redis:
- verify local services are running;
- verify `.env` matches your local ports and credentials.

`alembic upgrade head` fails:
- confirm PostgreSQL is reachable and the database exists;
- confirm `DB__POSTGRES_DSN` in `.env`.

Frontend shows health errors on the homepage:
- check that the backend is running on `localhost:8000`;
- if you changed backend host/port, update `VITE_DEV_PROXY_TARGET` or `VITE_API_BASE_URL` in the root `.env`.

Pre-commit hooks fail on unrelated paths:
- hooks are path-scoped now, so check whether you also changed root/shared files
  such as `Makefile`, `scripts/`, `docs/`, or `specs/`.

You are unsure which document is normative:
- `specs/` is the source of truth for public contracts;
- ADRs are the source of truth for architecture-level decisions;
- code and checks must stay aligned with both.
