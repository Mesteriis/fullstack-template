import {
  context,
  propagation,
  type Span,
  SpanKind,
  SpanStatusCode,
  trace,
} from "@opentelemetry/api";

import type { NormalizedApiError } from "@/shared/api/types";
import { allowObservabilitySignal } from "@/shared/observability/noise-control";
import { getObservabilityRuntime } from "@/shared/observability/runtime";
import {
  sanitizeErrorMessage,
  sanitizeUrl,
} from "@/shared/observability/sanitize";

const HEADER_SETTER = {
  set(carrier: Headers, key: string, value: string) {
    carrier.set(key, value);
  },
};

export interface ApiRequestSessionOptions {
  method: string;
  url: URL;
  headers?: HeadersInit;
}

export interface ApiRequestSession {
  requestId: string | null;
  run<T>(request: (headers: Headers) => Promise<T>): Promise<T>;
  finishFailure(error: NormalizedApiError): NormalizedApiError;
  finishSuccess(response: Response): void;
}

export function createApiRequestSession(
  options: ApiRequestSessionOptions,
): ApiRequestSession {
  const runtime = getObservabilityRuntime();
  const headers = new Headers(options.headers);
  const sanitizedUrl = sanitizeUrl(options.url);
  const requestId = attachRequestCorrelation(headers);
  const span = createClientSpan(options.method, sanitizedUrl);
  const spanContext = span
    ? trace.setSpan(context.active(), span)
    : context.active();

  if (span) {
    context.with(spanContext, () => {
      propagation.inject(spanContext, headers, HEADER_SETTER);
    });
  }

  return {
    requestId,
    run<T>(request: (observedHeaders: Headers) => Promise<T>): Promise<T> {
      return context.with(spanContext, () => request(headers));
    },
    finishFailure(error: NormalizedApiError): NormalizedApiError {
      if (span) {
        span.recordException(new Error(sanitizeErrorMessage(error.message)));
        span.setStatus({
          code: SpanStatusCode.ERROR,
          message: error.message,
        });

        if (typeof error.status === "number") {
          span.setAttribute("http.response.status_code", error.status);
        }

        span.end();
      }

      if (shouldCaptureApiFailure(error)) {
        const signature = `${options.method}:${sanitizedUrl}:${error.kind}:${error.status ?? "none"}`;

        if (allowObservabilitySignal(signature, 60_000)) {
          runtime.captureException(new Error(error.message), {
            level: "error",
            tags: {
              "frontend.api.kind": error.kind,
              "http.method": options.method,
              "http.status_code": String(error.status ?? "none"),
            },
            extra: {
              request_id: requestId,
              url: sanitizedUrl,
            },
          });
        }
      }

      return error;
    },
    finishSuccess(response: Response): void {
      if (!span) {
        return;
      }

      span.setAttribute("http.response.status_code", response.status);
      span.setStatus({
        code: response.ok ? SpanStatusCode.OK : SpanStatusCode.ERROR,
      });
      span.end();
    },
  };
}

function attachRequestCorrelation(headers: Headers): string | null {
  const runtime = getObservabilityRuntime();
  if (!runtime.config.enabled || !runtime.config.requestCorrelationEnabled) {
    return headers.get("x-request-id");
  }

  if (headers.has("x-request-id")) {
    return headers.get("x-request-id");
  }

  const requestId = createRequestId();
  headers.set("x-request-id", requestId);
  return requestId;
}

function createClientSpan(method: string, sanitizedUrl: string): Span | null {
  const runtime = getObservabilityRuntime();
  if (!runtime.config.enabled || !runtime.config.tracingEnabled) {
    return null;
  }

  return runtime.tracer.startSpan(`http.client ${method}`, {
    kind: SpanKind.CLIENT,
    attributes: {
      "http.method": method,
      "url.full": sanitizedUrl,
    },
  });
}

function createRequestId(): string {
  if (
    typeof globalThis.crypto !== "undefined"
    && typeof globalThis.crypto.randomUUID === "function"
  ) {
    return globalThis.crypto.randomUUID();
  }

  return `req-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

function shouldCaptureApiFailure(error: NormalizedApiError): boolean {
  return (
    error.kind === "network"
    || error.kind === "parse"
    || (typeof error.status === "number" && error.status >= 500)
  );
}
