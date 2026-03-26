import { trace } from "@opentelemetry/api";

import { resetObservabilityNoiseGate } from "@/shared/observability/noise-control";
import { setObservabilityRuntime } from "@/shared/observability/runtime";
import { trackWidgetFailure } from "@/shared/observability/ui-events";

describe("ui telemetry", () => {
  afterEach(() => {
    resetObservabilityNoiseGate();
    setObservabilityRuntime({
      addBreadcrumb: () => undefined,
      captureException: () => undefined,
      config: createDisabledObservabilityConfig(),
      tracer: trace.getTracer("test.noop"),
    });
  });

  it("deduplicates repeated widget failures within the noise-control window", () => {
    const addBreadcrumb = vi.fn();
    const captureException = vi.fn();

    setObservabilityRuntime({
      addBreadcrumb,
      captureException,
      config: {
        ...createDisabledObservabilityConfig(),
        enabled: true,
        uiTelemetryEnabled: true,
      },
      tracer: trace.getTracer("test.ui"),
    });

    const error = new Error("Widget failed to hydrate");

    trackWidgetFailure("system-health", error, {
      widget_slot: "summary",
    });
    trackWidgetFailure("system-health", error, {
      widget_slot: "summary",
    });

    expect(addBreadcrumb).toHaveBeenCalledTimes(1);
    expect(captureException).toHaveBeenCalledTimes(1);
  });
});

function createDisabledObservabilityConfig() {
  return {
    enabled: false,
    environment: "test",
    release: "test-release",
    serviceName: "registries-frontend-test",
    sentryEnabled: false,
    glitchtipDsn: "",
    tracingEnabled: false,
    otlpEndpoint: "",
    webVitalsEnabled: false,
    traceSampleRate: 0.1,
    uiTelemetryEnabled: false,
    routerTelemetryEnabled: false,
    requestCorrelationEnabled: false,
  };
}
