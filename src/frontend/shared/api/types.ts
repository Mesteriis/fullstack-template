export interface NormalizedApiError {
  kind: "http" | "network" | "parse";
  message: string;
  status: number | null;
  details: unknown | null;
}

export interface ApiSuccess<TData> {
  ok: true;
  status: number;
  data: TData;
}

export interface ApiFailure {
  ok: false;
  status: number | null;
  error: NormalizedApiError;
}

export type ApiResponse<TData> = ApiSuccess<TData> | ApiFailure;
