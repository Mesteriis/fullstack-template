import { onMounted, ref } from "vue";

import { getSystemHealth, type ReadinessProbe } from "@/entities/system";
import type { NormalizedApiError } from "@/shared/api";
import {
  trackAsyncBoundaryFailure,
  trackWidgetFailure,
} from "@/shared/observability";

export function useSystemHealth() {
  const isLoading = ref(true);
  const error = ref<NormalizedApiError | null>(null);
  const health = ref<ReadinessProbe | null>(null);

  async function load(): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await getSystemHealth();
      if (response.ok) {
        health.value = response.data;
        return;
      }

      error.value = response.error;
      health.value = null;
      trackWidgetFailure("system-health", response.error, {
        feature: "system-health",
        flow: "load",
      });
    } catch (caughtError: unknown) {
      error.value = {
        kind: "network",
        message: caughtError instanceof Error
          ? caughtError.message
          : "System health request failed unexpectedly.",
        status: null,
        details: null,
      };
      health.value = null;

      trackAsyncBoundaryFailure("system-health.load", caughtError, {
        composable: "useSystemHealth",
      });
    } finally {
      isLoading.value = false;
    }
  }

  onMounted(() => {
    void load();
  });

  return {
    error,
    health,
    isLoading,
    load,
  };
}
