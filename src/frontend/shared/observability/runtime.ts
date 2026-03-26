import { trace, type Tracer } from "@opentelemetry/api";

import type { AppObservabilityConfig } from "@/shared/config/env";

export interface ObservabilityBreadcrumb {
  category: string;
  message: string;
  level: "info" | "warning" | "error";
  data?: Record<string, unknown>;
}

export interface ObservabilityCaptureContext {
  tags?: Record<string, string>;
  extra?: Record<string, unknown>;
  level?: "info" | "warning" | "error";
}

export interface ObservabilityRuntimeState {
  config: AppObservabilityConfig;
  tracer: Tracer;
  captureException: (error: unknown, context?: ObservabilityCaptureContext) => void;
  addBreadcrumb: (breadcrumb: ObservabilityBreadcrumb) => void;
}

const DEFAULT_CONFIG: AppObservabilityConfig = Object.freeze({
  enabled: false,
  environment: "development",
  release: "frontend-local",
  serviceName: "registries-frontend",
  sentryEnabled: false,
  glitchtipDsn: "",
  tracingEnabled: false,
  otlpEndpoint: "",
  webVitalsEnabled: false,
  traceSampleRate: 0.1,
  uiTelemetryEnabled: false,
  routerTelemetryEnabled: false,
  requestCorrelationEnabled: false,
});

let runtimeState: ObservabilityRuntimeState = {
  config: DEFAULT_CONFIG,
  tracer: trace.getTracer("registries-frontend.noop"),
  captureException: () => undefined,
  addBreadcrumb: () => undefined,
};

export function getObservabilityRuntime(): ObservabilityRuntimeState {
  return runtimeState;
}

export function setObservabilityRuntime(
  nextState: Partial<ObservabilityRuntimeState>,
): ObservabilityRuntimeState {
  runtimeState = {
    ...runtimeState,
    ...nextState,
  };

  return runtimeState;
}
