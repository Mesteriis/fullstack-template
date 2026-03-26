import { fileURLToPath, URL } from "node:url";

import vue from "@vitejs/plugin-vue";
import { defineConfig, loadEnv } from "vite";

interface FrontendSharedRuntimeEnv {
  appName: string;
  apiBaseUrl: string;
  observability: {
    enabled: boolean;
    environment: string;
    release: string;
    serviceName: string;
    sentryEnabled: boolean;
    glitchtipDsn: string;
    tracingEnabled: boolean;
    otlpEndpoint: string;
    webVitalsEnabled: boolean;
    traceSampleRate: number;
    uiTelemetryEnabled: boolean;
    routerTelemetryEnabled: boolean;
    requestCorrelationEnabled: boolean;
  };
}

function readBooleanEnv(rawValue: string | undefined, fallback: boolean): boolean {
  if (!rawValue) {
    return fallback;
  }

  const normalizedValue = rawValue.trim().toLowerCase();

  if (["1", "true", "yes", "on"].includes(normalizedValue)) {
    return true;
  }

  if (["0", "false", "no", "off"].includes(normalizedValue)) {
    return false;
  }

  return fallback;
}

function readNumberEnv(rawValue: string | undefined, fallback: number, min: number, max: number): number {
  if (!rawValue) {
    return fallback;
  }

  const parsedValue = Number(rawValue);
  if (!Number.isFinite(parsedValue)) {
    return fallback;
  }

  return Math.min(max, Math.max(min, parsedValue));
}

function readStringEnv(rawValue: string | undefined, fallback: string): string {
  const normalizedValue = rawValue?.trim();
  return normalizedValue ? normalizedValue : fallback;
}

function normalizeDevServerHost(host: string): string {
  const normalizedHost = host.trim();

  if (!normalizedHost || ["0.0.0.0", "::"].includes(normalizedHost)) {
    return "127.0.0.1";
  }

  return normalizedHost;
}

function buildDevProxyTarget(env: Record<string, string>): string {
  const explicitTarget = env.VITE_DEV_PROXY_TARGET?.trim();
  if (explicitTarget) {
    return explicitTarget;
  }

  const apiHost = normalizeDevServerHost(env.API__HOST ?? "127.0.0.1");
  const apiPort = readStringEnv(env.API__PORT, "8000");
  return `http://${apiHost}:${apiPort}`;
}

function buildFrontendSharedRuntimeEnv(
  env: Record<string, string>,
  mode: string,
): FrontendSharedRuntimeEnv {
  const sharedObservabilityEnabled = readBooleanEnv(env.OBSERVABILITY__ENABLED, false);

  return {
    appName: readStringEnv(env.VITE_APP_NAME, readStringEnv(env.APP__NAME, "Fullstack Template")),
    apiBaseUrl: readStringEnv(env.VITE_API_BASE_URL, ""),
    observability: {
      enabled: readBooleanEnv(env.VITE_OBSERVABILITY_ENABLED, sharedObservabilityEnabled),
      environment: readStringEnv(
        env.VITE_OBSERVABILITY_ENVIRONMENT,
        readStringEnv(env.OBSERVABILITY__ENVIRONMENT, readStringEnv(env.APP__ENVIRONMENT, mode)),
      ),
      release: readStringEnv(
        env.VITE_OBSERVABILITY_RELEASE,
        readStringEnv(env.APP__VERSION, "frontend-local"),
      ),
      serviceName: readStringEnv(
        env.VITE_OBSERVABILITY_SERVICE_NAME,
        readStringEnv(env.OBSERVABILITY__SERVICE_NAME, readStringEnv(env.APP__NAME, "Fullstack Template")),
      ),
      sentryEnabled: readBooleanEnv(
        env.VITE_OBSERVABILITY_SENTRY_ENABLED,
        readBooleanEnv(env.OBSERVABILITY__SENTRY_ENABLED, false),
      ),
      glitchtipDsn: readStringEnv(
        env.VITE_OBSERVABILITY_GLITCHTIP_DSN,
        readStringEnv(env.OBSERVABILITY__GLITCHTIP_DSN, ""),
      ),
      tracingEnabled: readBooleanEnv(
        env.VITE_OBSERVABILITY_TRACING_ENABLED,
        readBooleanEnv(env.OBSERVABILITY__TRACES_ENABLED, false),
      ),
      otlpEndpoint: readStringEnv(
        env.VITE_OBSERVABILITY_OTLP_ENDPOINT,
        readStringEnv(env.OBSERVABILITY__OTLP_ENDPOINT, ""),
      ),
      webVitalsEnabled: readBooleanEnv(
        env.VITE_OBSERVABILITY_WEB_VITALS_ENABLED,
        sharedObservabilityEnabled,
      ),
      traceSampleRate: readNumberEnv(
        env.VITE_OBSERVABILITY_TRACE_SAMPLE_RATE ?? env.OBSERVABILITY__TRACE_SAMPLE_RATE,
        0.1,
        0,
        1,
      ),
      uiTelemetryEnabled: readBooleanEnv(
        env.VITE_OBSERVABILITY_UI_TELEMETRY_ENABLED,
        sharedObservabilityEnabled,
      ),
      routerTelemetryEnabled: readBooleanEnv(
        env.VITE_OBSERVABILITY_ROUTER_TELEMETRY_ENABLED,
        sharedObservabilityEnabled,
      ),
      requestCorrelationEnabled: readBooleanEnv(
        env.VITE_OBSERVABILITY_REQUEST_CORRELATION_ENABLED,
        sharedObservabilityEnabled,
      ),
    },
  };
}

export default defineConfig(({ mode }) => {
  const repoRoot = fileURLToPath(new URL("../..", import.meta.url));
  const env = {
    ...process.env,
    ...loadEnv(mode, repoRoot, ""),
  } as Record<string, string>;
  const sourceMapsEnabled = readBooleanEnv(env.VITE_OBSERVABILITY_SOURCEMAPS_ENABLED, false);
  const devProxyTarget = buildDevProxyTarget(env);
  const frontendSharedRuntimeEnv = buildFrontendSharedRuntimeEnv(env, mode);

  return {
    envDir: repoRoot,
    define: {
      __FRONTEND_SHARED_ENV__: JSON.stringify(frontendSharedRuntimeEnv),
    },
    plugins: [vue()],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./", import.meta.url)),
        "@/app": fileURLToPath(new URL("./app", import.meta.url)),
        "@/pages": fileURLToPath(new URL("./pages", import.meta.url)),
        "@/features": fileURLToPath(new URL("./features", import.meta.url)),
        "@/entities": fileURLToPath(new URL("./entities", import.meta.url)),
        "@/shared": fileURLToPath(new URL("./shared", import.meta.url)),
      },
    },
    build: {
      sourcemap: sourceMapsEnabled ? "hidden" : false,
    },
    server: {
      host: "0.0.0.0",
      port: 5173,
      proxy: {
        "/api": {
          target: devProxyTarget,
          changeOrigin: true,
        },
      },
    },
    test: {
      environment: "jsdom",
      globals: true,
      setupFiles: ["./tests/setup/vitest.setup.ts"],
    },
  };
});
