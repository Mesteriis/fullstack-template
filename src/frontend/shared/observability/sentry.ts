import * as Sentry from "@sentry/vue";
import type { App } from "vue";

import type { AppObservabilityConfig } from "@/shared/config/env";
import { isNonEmptyString } from "@/shared/lib";
import {
  type ObservabilityBreadcrumb,
  type ObservabilityCaptureContext,
  setObservabilityRuntime,
} from "@/shared/observability/runtime";
import {
  sanitizeErrorMessage,
  sanitizeTelemetryAttributes,
  sanitizeUrl,
} from "@/shared/observability/sanitize";

const NOISY_BREADCRUMB_CATEGORIES = new Set([
  "console",
  "fetch",
  "ui.click",
  "xhr",
]);

let sentryInitialized = false;

export function setupSentry(app: App, config: AppObservabilityConfig): void {
  if (
    sentryInitialized
    || !config.enabled
    || !config.sentryEnabled
    || !isNonEmptyString(config.glitchtipDsn)
  ) {
    return;
  }

  Sentry.init({
    app,
    dsn: config.glitchtipDsn,
    environment: config.environment,
    release: config.release,
    enabled: true,
    sendDefaultPii: false,
    maxBreadcrumbs: 20,
    ignoreErrors: [
      "ResizeObserver loop completed with undelivered notifications.",
      "ResizeObserver loop limit exceeded",
      "Network request failed",
    ],
    initialScope(scope) {
      scope.setTag("service.name", config.serviceName);
      scope.setTag("deployment.environment", config.environment);
      return scope;
    },
    beforeBreadcrumb(breadcrumb) {
      if (breadcrumb.category && NOISY_BREADCRUMB_CATEGORIES.has(breadcrumb.category)) {
        return null;
      }

      if (breadcrumb.data && typeof breadcrumb.data === "object") {
        breadcrumb.data = sanitizeTelemetryAttributes(breadcrumb.data as Record<string, unknown>);
      }

      if (typeof breadcrumb.message === "string") {
        breadcrumb.message = sanitizeErrorMessage(breadcrumb.message);
      }

      return breadcrumb;
    },
    beforeSend(event) {
      if (event.request) {
        delete event.request.cookies;
        delete event.request.data;
        delete event.request.headers;

        if (typeof event.request.url === "string") {
          event.request.url = sanitizeUrl(event.request.url);
        }
      }

      delete event.user;

      if (event.contexts) {
        delete event.contexts.response;
      }

      if (event.extra) {
        event.extra = sanitizeTelemetryAttributes(event.extra);
      }

      return event;
    },
  });

  setObservabilityRuntime({
    addBreadcrumb: (breadcrumb: ObservabilityBreadcrumb) => {
      Sentry.addBreadcrumb({
        category: breadcrumb.category,
        data: breadcrumb.data,
        level: breadcrumb.level,
        message: breadcrumb.message,
      });
    },
    captureException: (error: unknown, context?: ObservabilityCaptureContext) => {
      Sentry.withScope((scope) => {
        if (context?.level) {
          scope.setLevel(context.level);
        }

        for (const [key, value] of Object.entries(context?.tags ?? {})) {
          scope.setTag(key, value);
        }

        if (context?.extra) {
          scope.setContext("frontend_observability", sanitizeTelemetryAttributes(context.extra));
        }

        Sentry.captureException(error);
      });
    },
  });

  sentryInitialized = true;
}
