import { afterEach, vi } from "vitest";

vi.stubGlobal("scrollTo", vi.fn());

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  vi.stubGlobal("scrollTo", vi.fn());
});
