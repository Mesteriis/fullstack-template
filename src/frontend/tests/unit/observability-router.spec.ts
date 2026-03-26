import type { RouteLocationNormalizedLoaded } from "vue-router";

import { buildRouteTelemetryAttributes } from "@/shared/observability/router";

describe("router observability", () => {
  it("keeps route telemetry metadata safe for params and query strings", () => {
    const attributes = buildRouteTelemetryAttributes(
      {
        name: "system-details",
        path: "/systems/123",
        params: {
          id: "123",
        },
        query: {
          tab: "checks",
          token: "secret-value",
        },
        matched: [
          {
            path: "/systems/:id",
          },
        ],
        meta: {
          lazy: true,
        },
      } as unknown as RouteLocationNormalizedLoaded,
      {
        name: "home",
        path: "/",
        params: {},
        query: {},
        matched: [
          {
            path: "/",
          },
        ],
        meta: {},
      } as unknown as RouteLocationNormalizedLoaded,
    );

    expect(attributes["route.to.path"]).toBe("/systems/:id");
    expect(attributes["route.to.params.keys"]).toBe("id");
    expect(attributes["route.to.query.keys"]).toBe("tab");
    expect(attributes["route.to.matched"]).toBe("/systems/:id");
    expect(Object.values(attributes)).not.toContain("123");
    expect(Object.values(attributes)).not.toContain("secret-value");
  });
});
