# syntax=docker/dockerfile:1.7

FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS backend-builder

ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /build/backend

COPY src/backend/pyproject.toml src/backend/uv.lock ./
RUN uv sync --frozen --no-dev


FROM python:3.14-slim AS backend

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src/backend
ENV PATH=/opt/venv/bin:${PATH}

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY --from=backend-builder /opt/venv /opt/venv
COPY alembic.ini /app/alembic.ini
COPY migrations /app/migrations
COPY src/backend /app/src/backend
COPY --chmod=755 docker/entrypoints/backend.sh /usr/local/bin/backend-entrypoint.sh
COPY --chmod=755 docker/runs/backend.sh /usr/local/bin/backend-run.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:8000/api/v1/system/health')"

USER app

ENTRYPOINT ["/usr/local/bin/backend-entrypoint.sh"]
CMD ["/usr/local/bin/backend-run.sh"]


FROM node:22-alpine AS frontend-builder

ARG APP__NAME=Fullstack\ Template\ API
ARG APP__VERSION=0.1.0
ARG APP__ENVIRONMENT=local
ARG OBSERVABILITY__ENABLED=true
ARG OBSERVABILITY__ENVIRONMENT=
ARG OBSERVABILITY__SERVICE_NAME=
ARG OBSERVABILITY__SENTRY_ENABLED=false
ARG OBSERVABILITY__GLITCHTIP_DSN=
ARG OBSERVABILITY__TRACES_ENABLED=false
ARG OBSERVABILITY__OTLP_ENDPOINT=
ARG OBSERVABILITY__TRACE_SAMPLE_RATE=0.1
ARG VITE_API_BASE_URL=
ARG VITE_DEV_PROXY_TARGET=http://127.0.0.1:8000
ARG VITE_OBSERVABILITY_WEB_VITALS_ENABLED=false
ARG VITE_OBSERVABILITY_UI_TELEMETRY_ENABLED=false
ARG VITE_OBSERVABILITY_ROUTER_TELEMETRY_ENABLED=true
ARG VITE_OBSERVABILITY_REQUEST_CORRELATION_ENABLED=true
ARG VITE_OBSERVABILITY_SOURCEMAPS_ENABLED=false

ENV APP__NAME=${APP__NAME}
ENV APP__VERSION=${APP__VERSION}
ENV APP__ENVIRONMENT=${APP__ENVIRONMENT}
ENV OBSERVABILITY__ENABLED=${OBSERVABILITY__ENABLED}
ENV OBSERVABILITY__ENVIRONMENT=${OBSERVABILITY__ENVIRONMENT}
ENV OBSERVABILITY__SERVICE_NAME=${OBSERVABILITY__SERVICE_NAME}
ENV OBSERVABILITY__SENTRY_ENABLED=${OBSERVABILITY__SENTRY_ENABLED}
ENV OBSERVABILITY__GLITCHTIP_DSN=${OBSERVABILITY__GLITCHTIP_DSN}
ENV OBSERVABILITY__TRACES_ENABLED=${OBSERVABILITY__TRACES_ENABLED}
ENV OBSERVABILITY__OTLP_ENDPOINT=${OBSERVABILITY__OTLP_ENDPOINT}
ENV OBSERVABILITY__TRACE_SAMPLE_RATE=${OBSERVABILITY__TRACE_SAMPLE_RATE}
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_DEV_PROXY_TARGET=${VITE_DEV_PROXY_TARGET}
ENV VITE_OBSERVABILITY_WEB_VITALS_ENABLED=${VITE_OBSERVABILITY_WEB_VITALS_ENABLED}
ENV VITE_OBSERVABILITY_UI_TELEMETRY_ENABLED=${VITE_OBSERVABILITY_UI_TELEMETRY_ENABLED}
ENV VITE_OBSERVABILITY_ROUTER_TELEMETRY_ENABLED=${VITE_OBSERVABILITY_ROUTER_TELEMETRY_ENABLED}
ENV VITE_OBSERVABILITY_REQUEST_CORRELATION_ENABLED=${VITE_OBSERVABILITY_REQUEST_CORRELATION_ENABLED}
ENV VITE_OBSERVABILITY_SOURCEMAPS_ENABLED=${VITE_OBSERVABILITY_SOURCEMAPS_ENABLED}

WORKDIR /workspace/src/frontend

RUN corepack enable

COPY src/frontend/package.json src/frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY src/frontend ./
RUN pnpm build


FROM nginxinc/nginx-unprivileged:1.27-alpine AS frontend

COPY docker/nginx/default.conf /etc/nginx/templates/default.conf.template
COPY --chmod=755 docker/entrypoints/frontend.sh /usr/local/bin/frontend-entrypoint.sh
COPY --chmod=755 docker/runs/frontend.sh /usr/local/bin/frontend-run.sh
COPY --from=frontend-builder /workspace/src/frontend/dist /usr/share/nginx/html

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD wget -q -O /dev/null http://127.0.0.1:8080/

ENTRYPOINT ["/usr/local/bin/frontend-entrypoint.sh"]
CMD ["/usr/local/bin/frontend-run.sh"]
