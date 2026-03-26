import { propagation, trace } from "@opentelemetry/api";
import { ZoneContextManager } from "@opentelemetry/context-zone";
import { W3CTraceContextPropagator } from "@opentelemetry/core";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { registerInstrumentations } from "@opentelemetry/instrumentation";
import { DocumentLoadInstrumentation } from "@opentelemetry/instrumentation-document-load";
import { resourceFromAttributes } from "@opentelemetry/resources";
import {
  BatchSpanProcessor,
  ParentBasedSampler,
  TraceIdRatioBasedSampler,
} from "@opentelemetry/sdk-trace-base";
import { WebTracerProvider } from "@opentelemetry/sdk-trace-web";

import type { AppObservabilityConfig } from "@/shared/config/env";
import { isNonEmptyString } from "@/shared/lib";
import { setObservabilityRuntime } from "@/shared/observability/runtime";

let tracingInitialized = false;

export function setupTracing(config: AppObservabilityConfig): void {
  if (
    tracingInitialized
    || !config.enabled
    || !config.tracingEnabled
    || !isNonEmptyString(config.otlpEndpoint)
  ) {
    return;
  }

  const provider = new WebTracerProvider({
    resource: resourceFromAttributes({
      "service.name": config.serviceName,
      "service.version": config.release,
      "deployment.environment": config.environment,
    }),
    sampler: new ParentBasedSampler({
      root: new TraceIdRatioBasedSampler(config.traceSampleRate),
    }),
    spanProcessors: [
      new BatchSpanProcessor(
        new OTLPTraceExporter({
          url: config.otlpEndpoint,
        }),
      ),
    ],
  });

  provider.register({
    contextManager: new ZoneContextManager(),
  });

  propagation.setGlobalPropagator(new W3CTraceContextPropagator());
  registerInstrumentations({
    instrumentations: [new DocumentLoadInstrumentation()],
    tracerProvider: provider,
  });

  setObservabilityRuntime({
    tracer: trace.getTracer(config.serviceName),
  });

  tracingInitialized = true;
}
