const SENSITIVE_KEY_PATTERN = /authorization|cookie|token|secret|password|session|jwt|bearer|body|payload|email|phone|address/i;
const SENSITIVE_PATH_SEGMENT_PATTERN = /^(?:\d{3,}|[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}|[A-Za-z0-9_-]{24,})$/iu;
const MAX_STRING_LENGTH = 180;

type TelemetryScalar = boolean | number | string;

export function sanitizeUrl(input: string | URL): string {
  const baseUrl = "http://frontend.local";

  try {
    const url = input instanceof URL ? input : new URL(input, baseUrl);
    const sanitizedPathname = url.pathname
      .split("/")
      .map((segment) => (isSensitivePathSegment(segment) ? ":id" : segment))
      .join("/");
    const sanitizedPath = `${url.origin}${sanitizedPathname}`;

    return url.origin === baseUrl
      ? sanitizedPathname
      : sanitizedPath;
  } catch {
    return String(input).split(/[?#]/u, 1)[0] || "/";
  }
}

export function sanitizeTelemetryAttributes(
  attributes: Record<string, unknown>,
): Record<string, TelemetryScalar> {
  return Object.fromEntries(
    Object.entries(attributes).flatMap(([key, value]) => {
      const sanitizedValue = sanitizeAttributeValue(key, value);

      return typeof sanitizedValue === "undefined"
        ? []
        : [[key, sanitizedValue]];
    }),
  );
}

export function sanitizeRouteKeyCollection(values: Record<string, unknown>): string {
  return Object.keys(values)
    .filter((key) => !SENSITIVE_KEY_PATTERN.test(key))
    .sort()
    .join(",");
}

export function sanitizeErrorMessage(error: unknown): string {
  if (error instanceof Error && typeof error.message === "string" && error.message.trim()) {
    return clampString(error.message);
  }

  if (typeof error === "string" && error.trim()) {
    return clampString(error);
  }

  return "Unknown frontend error";
}

export function createErrorSignature(error: unknown): string {
  if (error instanceof Error) {
    return `${error.name}:${sanitizeErrorMessage(error)}`;
  }

  return sanitizeErrorMessage(error);
}

function sanitizeAttributeValue(
  key: string,
  value: unknown,
): TelemetryScalar | undefined {
  if (SENSITIVE_KEY_PATTERN.test(key)) {
    return "[redacted]";
  }

  if (typeof value === "boolean") {
    return value;
  }

  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string" && value.trim()) {
    return clampString(value);
  }

  if (Array.isArray(value)) {
    const joinedValue = value
      .map((item) => sanitizeAttributeValue(key, item))
      .filter((item): item is TelemetryScalar => typeof item !== "undefined")
      .join(",");

    return joinedValue ? clampString(joinedValue) : undefined;
  }

  return undefined;
}

function clampString(value: string): string {
  return value.trim().slice(0, MAX_STRING_LENGTH);
}

function isSensitivePathSegment(segment: string): boolean {
  return Boolean(segment) && SENSITIVE_PATH_SEGMENT_PATTERN.test(segment);
}
