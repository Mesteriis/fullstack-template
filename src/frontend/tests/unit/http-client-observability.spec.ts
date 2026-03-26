import { trace } from "@opentelemetry/api";

import { createHttpClient } from "@/shared/api";
import { resetObservabilityNoiseGate } from "@/shared/observability/noise-control";
import { setObservabilityRuntime } from "@/shared/observability/runtime";

describe("http client observability", () => {
  afterEach(() => {
    resetObservabilityNoiseGate();
    setObservabilityRuntime({
      addBreadcrumb: () => undefined,
      captureException: () => undefined,
      config: createDisabledObservabilityConfig(),
      tracer: trace.getTracer("test.noop"),
    });
  });

  it("injects request correlation into the existing shared client", async () => {
    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ status: "ok" }),
    } satisfies Partial<Response>);

    const client = createHttpClient({
      baseUrl: "https://api.example.test",
      fetchImplementation: fetchSpy as typeof fetch,
    });

    setObservabilityRuntime({
      config: {
        ...createDisabledObservabilityConfig(),
        enabled: true,
        requestCorrelationEnabled: true,
      },
      tracer: trace.getTracer("test.client"),
    });

    await client.requestJson("/health");

    const [, init] = fetchSpy.mock.calls[0] as [URL, RequestInit];
    const headers = new Headers(init.headers);

    expect(headers.get("Accept")).toBe("application/json");
    expect(headers.get("x-request-id")).toMatch(/^.+$/u);
  });

  it("preserves an explicit request id instead of overwriting it", async () => {
    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ status: "ok" }),
    } satisfies Partial<Response>);

    const client = createHttpClient({
      baseUrl: "https://api.example.test",
      fetchImplementation: fetchSpy as typeof fetch,
    });

    setObservabilityRuntime({
      config: {
        ...createDisabledObservabilityConfig(),
        enabled: true,
        requestCorrelationEnabled: true,
      },
      tracer: trace.getTracer("test.client"),
    });

    await client.requestJson("/health", {
      headers: {
        "x-request-id": "manual-request-id",
      },
    });

    const [, init] = fetchSpy.mock.calls[0] as [URL, RequestInit];
    const headers = new Headers(init.headers);

    expect(headers.get("x-request-id")).toBe("manual-request-id");
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
