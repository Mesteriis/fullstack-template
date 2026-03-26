import {
  type Metric,
  onCLS,
  onINP,
  onLCP,
  onTTFB,
} from "web-vitals";

import { getObservabilityRuntime } from "@/shared/observability/runtime";
import { trackWebVitalMetric } from "@/shared/observability/ui-events";

let webVitalsInitialized = false;

export function setupWebVitals(): void {
  const runtime = getObservabilityRuntime();
  if (
    webVitalsInitialized
    || !runtime.config.enabled
    || !runtime.config.webVitalsEnabled
  ) {
    return;
  }

  const reportMetric = (metric: Metric) => {
    trackWebVitalMetric(metric.name, {
      "web_vital.name": metric.name,
      "web_vital.value": metric.value,
      "web_vital.rating": metric.rating,
      "web_vital.navigation_type": metric.navigationType,
    });
  };

  onCLS(reportMetric);
  onINP(reportMetric);
  onLCP(reportMetric);
  onTTFB(reportMetric);

  webVitalsInitialized = true;
}
