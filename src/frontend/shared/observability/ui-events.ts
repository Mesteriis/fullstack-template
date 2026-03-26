import { SpanStatusCode, trace } from "@opentelemetry/api";

import { allowObservabilitySignal } from "@/shared/observability/noise-control";
import { getObservabilityRuntime } from "@/shared/observability/runtime";
import {
  createErrorSignature,
  sanitizeErrorMessage,
  sanitizeTelemetryAttributes,
} from "@/shared/observability/sanitize";

export interface UiTelemetryOptions {
  attributes?: Record<string, unknown>;
  dedupeKey?: string;
  dedupeWindowMs?: number;
  error?: unknown;
}

export function trackPageMountComplete(
  pageName: string,
  attributes: Record<string, unknown> = {},
): void {
  emitUiTelemetry("page.mount_complete", {
    attributes: {
      page: pageName,
      ...attributes,
    },
    dedupeKey: `page.mount_complete:${pageName}`,
    dedupeWindowMs: 15_000,
  });
}

export function trackPageLoadFailure(
  pageName: string,
  error: unknown,
  attributes: Record<string, unknown> = {},
): void {
  emitUiTelemetry("page.load_failed", {
    attributes: {
      page: pageName,
      ...attributes,
    },
    dedupeKey: `page.load_failed:${pageName}:${createErrorSignature(error)}`,
    dedupeWindowMs: 60_000,
    error,
  });
}

export function trackWidgetFailure(
  widgetName: string,
  error: unknown,
  attributes: Record<string, unknown> = {},
): void {
  emitUiTelemetry("widget.failed", {
    attributes: {
      widget: widgetName,
      ...attributes,
    },
    dedupeKey: `widget.failed:${widgetName}:${createErrorSignature(error)}`,
    dedupeWindowMs: 60_000,
    error,
  });
}

export function trackUiActionFailure(
  actionName: string,
  error: unknown,
  attributes: Record<string, unknown> = {},
): void {
  emitUiTelemetry("ui.action_failed", {
    attributes: {
      action: actionName,
      ...attributes,
    },
    dedupeKey: `ui.action_failed:${actionName}:${createErrorSignature(error)}`,
    dedupeWindowMs: 30_000,
    error,
  });
}

export function trackAsyncBoundaryFailure(
  boundaryName: string,
  error: unknown,
  attributes: Record<string, unknown> = {},
): void {
  emitUiTelemetry("async_boundary.failed", {
    attributes: {
      boundary: boundaryName,
      ...attributes,
    },
    dedupeKey: `async_boundary.failed:${boundaryName}:${createErrorSignature(error)}`,
    dedupeWindowMs: 60_000,
    error,
  });
}

export function trackWebVitalMetric(
  metricName: string,
  attributes: Record<string, unknown>,
): void {
  emitUiTelemetry(`web_vital.${metricName.toLowerCase()}`, {
    attributes,
    dedupeKey: `web_vital:${metricName}`,
    dedupeWindowMs: 300_000,
  });
}

function emitUiTelemetry(
  eventName: string,
  options: UiTelemetryOptions,
): void {
  const runtime = getObservabilityRuntime();
  if (!runtime.config.enabled) {
    return;
  }

  const isUiSignal = !eventName.startsWith("web_vital");
  if (isUiSignal && !runtime.config.uiTelemetryEnabled) {
    return;
  }

  const dedupeKey = options.dedupeKey ?? eventName;
  if (!allowObservabilitySignal(dedupeKey, options.dedupeWindowMs)) {
    return;
  }

  const attributes = sanitizeTelemetryAttributes(options.attributes ?? {});
  const activeSpan = trace.getActiveSpan();

  if (activeSpan) {
    activeSpan.addEvent(eventName, attributes);
    if (options.error) {
      activeSpan.recordException(toSpanError(options.error));
      activeSpan.setStatus({
        code: SpanStatusCode.ERROR,
        message: sanitizeErrorMessage(options.error),
      });
    }
  } else if (runtime.config.tracingEnabled) {
    const span = runtime.tracer.startSpan(`ui.${eventName}`);

    span.addEvent(eventName, attributes);
    if (options.error) {
      span.recordException(toSpanError(options.error));
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: sanitizeErrorMessage(options.error),
      });
    }
    span.end();
  }

  runtime.addBreadcrumb({
    category: "frontend.observability",
    message: eventName,
    level: options.error ? "error" : "info",
    data: attributes,
  });

  if (options.error) {
    runtime.captureException(options.error, {
      level: "error",
      tags: {
        "frontend.signal": eventName,
      },
      extra: attributes,
    });
  }
}

function toSpanError(error: unknown): Error {
  if (error instanceof Error) {
    return error;
  }

  return new Error(sanitizeErrorMessage(error));
}
