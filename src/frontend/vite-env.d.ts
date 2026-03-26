/// <reference types="vite/client" />

import "vue-router";

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_APP_NAME?: string;
  readonly VITE_OBSERVABILITY_ENABLED?: string;
  readonly VITE_OBSERVABILITY_ENVIRONMENT?: string;
  readonly VITE_OBSERVABILITY_GLITCHTIP_DSN?: string;
  readonly VITE_OBSERVABILITY_OTLP_ENDPOINT?: string;
  readonly VITE_OBSERVABILITY_RELEASE?: string;
  readonly VITE_OBSERVABILITY_REQUEST_CORRELATION_ENABLED?: string;
  readonly VITE_OBSERVABILITY_ROUTER_TELEMETRY_ENABLED?: string;
  readonly VITE_OBSERVABILITY_SERVICE_NAME?: string;
  readonly VITE_OBSERVABILITY_SENTRY_ENABLED?: string;
  readonly VITE_OBSERVABILITY_SOURCEMAPS_ENABLED?: string;
  readonly VITE_OBSERVABILITY_TRACE_SAMPLE_RATE?: string;
  readonly VITE_OBSERVABILITY_TRACING_ENABLED?: string;
  readonly VITE_OBSERVABILITY_UI_TELEMETRY_ENABLED?: string;
  readonly VITE_OBSERVABILITY_WEB_VITALS_ENABLED?: string;
  readonly VITE_SYSTEM_HEALTH_PATH?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare module "vue-router" {
  interface RouteMeta {
    title: string;
    description?: string;
    lazy?: boolean;
  }
}
