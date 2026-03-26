export type SystemHealthStatus = "ok" | "error";

export interface DependencyProbe {
  name: string;
  status: SystemHealthStatus;
  detail: string | null;
}

export interface ReadinessProbe {
  status: SystemHealthStatus;
  service: string;
  checks: readonly DependencyProbe[];
}
