import type { App } from "vue";
import type { Router } from "vue-router";

import type { AppConfig } from "@/shared/config/env";
import { setupRouterObservability } from "@/shared/observability/router";
import { setObservabilityRuntime } from "@/shared/observability/runtime";
import { setupSentry } from "@/shared/observability/sentry";
import { setupTracing } from "@/shared/observability/tracing";
import { setupWebVitals } from "@/shared/observability/web-vitals";

export function setupFrontendObservability(
  app: App,
  router: Router,
  config: AppConfig,
): void {
  setObservabilityRuntime({
    config: config.observability,
  });

  if (!config.observability.enabled) {
    return;
  }

  setupTracing(config.observability);
  setupSentry(app, config.observability);
  setupRouterObservability(router);
  setupWebVitals();
}
