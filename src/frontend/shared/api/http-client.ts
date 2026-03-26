import type {
  ApiResponse,
  NormalizedApiError,
} from "@/shared/api/types";
import { appConfig } from "@/shared/config/env";
import { isNonEmptyString } from "@/shared/lib";
import { createApiRequestSession } from "@/shared/observability/api";

export interface HttpClient {
  requestJson<TData>(path: string, init?: RequestInit): Promise<ApiResponse<TData>>;
}

interface HttpClientOptions {
  baseUrl: string;
  fetchImplementation?: typeof fetch;
}

export function createHttpClient(options: HttpClientOptions): HttpClient {
  return {
    async requestJson<TData>(path: string, init: RequestInit = {}): Promise<ApiResponse<TData>> {
      const fetchImplementation = options.fetchImplementation ?? globalThis.fetch.bind(globalThis);
      const url = buildUrl(options.baseUrl, path);
      const method = resolveMethod(init.method);
      const requestSession = createApiRequestSession({
        method,
        url,
        headers: init.headers,
      });

      try {
        const response = await requestSession.run((headers) => fetchImplementation(url, {
          ...init,
          headers: mergeHeaders(headers),
        }));

        if (!response.ok) {
          const normalizedError = await normalizeHttpError(response);
          requestSession.finishFailure(normalizedError);

          return {
            ok: false,
            status: response.status,
            error: normalizedError,
          };
        }

        try {
          const data = (await response.json()) as TData;
          requestSession.finishSuccess(response);

          return {
            ok: true,
            status: response.status,
            data,
          };
        } catch (error: unknown) {
          return {
            ok: false,
            status: response.status,
            error: requestSession.finishFailure(
              normalizeThrownError(error, "parse", response.status),
            ),
          };
        }
      } catch (error: unknown) {
        return {
          ok: false,
          status: null,
          error: requestSession.finishFailure(normalizeThrownError(error, "network", null)),
        };
      }
    },
  };
}

export const httpClient = createHttpClient({
  baseUrl: appConfig.apiBaseUrl,
});

function buildUrl(baseUrl: string, path: string): URL {
  return new URL(path, `${baseUrl}/`);
}

async function normalizeHttpError(response: Response): Promise<NormalizedApiError> {
  let details: unknown | null = null;
  let message = `Request failed with status ${response.status}.`;

  try {
    details = await response.json();
    if (hasMessage(details)) {
      message = details.message;
    }
  } catch {
    details = null;
  }

  return {
    kind: "http",
    message,
    status: response.status,
    details,
  };
}

function normalizeThrownError(
  error: unknown,
  kind: NormalizedApiError["kind"],
  status: number | null,
): NormalizedApiError {
  return {
    kind,
    message: error instanceof Error && isNonEmptyString(error.message)
      ? error.message
      : "Request failed before a valid JSON payload was received.",
    status,
    details: error,
  };
}

function mergeHeaders(headers: Headers): Headers {
  const mergedHeaders = new Headers(headers);

  if (!mergedHeaders.has("Accept")) {
    mergedHeaders.set("Accept", "application/json");
  }

  return mergedHeaders;
}

function resolveMethod(method: string | undefined): string {
  return isNonEmptyString(method) ? method.trim().toUpperCase() : "GET";
}

function hasMessage(value: unknown): value is { message: string } {
  return (
    typeof value === "object"
    && value !== null
    && "message" in value
    && typeof value.message === "string"
  );
}
