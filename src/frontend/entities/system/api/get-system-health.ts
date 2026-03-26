import type { ReadinessProbe } from "@/entities/system/model/system-health";
import { type ApiResponse,httpClient } from "@/shared/api";
import { appConfig } from "@/shared/config/env";

export function getSystemHealth(): Promise<ApiResponse<ReadinessProbe>> {
  return httpClient.requestJson<ReadinessProbe>(appConfig.systemHealthPath);
}
