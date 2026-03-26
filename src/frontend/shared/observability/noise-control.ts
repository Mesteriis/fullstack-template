const eventRegistry = new Map<string, number>();

export function allowObservabilitySignal(
  signature: string,
  windowMs: number = 60_000,
): boolean {
  const now = Date.now();
  const lastSeenAt = eventRegistry.get(signature);

  if (typeof lastSeenAt === "number" && now - lastSeenAt < windowMs) {
    return false;
  }

  eventRegistry.set(signature, now);
  pruneExpiredSignals(now, windowMs * 4);
  return true;
}

function pruneExpiredSignals(now: number, ttlMs: number): void {
  for (const [signature, lastSeenAt] of eventRegistry.entries()) {
    if (now - lastSeenAt > ttlMs) {
      eventRegistry.delete(signature);
    }
  }
}

export function resetObservabilityNoiseGate(): void {
  eventRegistry.clear();
}
