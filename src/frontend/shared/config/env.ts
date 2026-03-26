import { isNonEmptyString, trimTrailingSlash } from "@/shared/lib";

export interface AppObservabilityConfig {
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
}

export interface AppConfig {
  appName: string;
  apiBaseUrl: string;
  observability: AppObservabilityConfig;
}

const frontendSharedEnv = __FRONTEND_SHARED_ENV__;

function readApiBaseUrl(): string {
  const configuredBaseUrl = trimTrailingSlash(frontendSharedEnv.apiBaseUrl);
  const runtimeOrigin = globalThis.location?.origin;

  if (isNonEmptyString(configuredBaseUrl)) {
    return configuredBaseUrl;
  }

  if (isNonEmptyString(runtimeOrigin)) {
    return trimTrailingSlash(runtimeOrigin);
  }

  return "http://localhost:5173";
}

export const appConfig: AppConfig = Object.freeze({
  appName: frontendSharedEnv.appName,
  apiBaseUrl: readApiBaseUrl(),
  observability: Object.freeze({
    ...frontendSharedEnv.observability,
    otlpEndpoint: trimTrailingSlash(frontendSharedEnv.observability.otlpEndpoint),
  }),
});
