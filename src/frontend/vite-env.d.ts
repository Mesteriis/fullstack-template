/// <reference types="vite/client" />

import "vue-router";

declare global {
  interface ImportMetaEnv {
    readonly VITE_API_BASE_URL?: string;
    readonly VITE_APP_NAME?: string;
    readonly VITE_DEV_PROXY_TARGET?: string;
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
  }

  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }

  interface FrontendSharedObservabilityEnv {
    readonly enabled: boolean;
    readonly environment: string;
    readonly release: string;
    readonly serviceName: string;
    readonly sentryEnabled: boolean;
    readonly glitchtipDsn: string;
    readonly tracingEnabled: boolean;
    readonly otlpEndpoint: string;
    readonly webVitalsEnabled: boolean;
    readonly traceSampleRate: number;
    readonly uiTelemetryEnabled: boolean;
    readonly routerTelemetryEnabled: boolean;
    readonly requestCorrelationEnabled: boolean;
  }

  interface FrontendSharedEnv {
    readonly appName: string;
    readonly apiBaseUrl: string;
    readonly observability: FrontendSharedObservabilityEnv;
  }

  const __FRONTEND_SHARED_ENV__: Readonly<FrontendSharedEnv>;
}

declare module "vue-router" {
  interface RouteMeta {
    title: string;
    description?: string;
    lazy?: boolean;
  }
}
