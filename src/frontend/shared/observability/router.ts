import { type Attributes, type Span,SpanStatusCode } from "@opentelemetry/api";
import type {
  RouteLocationNormalized,
  RouteLocationNormalizedLoaded,
  Router,
} from "vue-router";

import { getObservabilityRuntime } from "@/shared/observability/runtime";
import {
  sanitizeErrorMessage,
  sanitizeRouteKeyCollection,
} from "@/shared/observability/sanitize";
import { trackAsyncBoundaryFailure } from "@/shared/observability/ui-events";

const instrumentedRouters = new WeakSet<Router>();

export function setupRouterObservability(router: Router): void {
  const runtime = getObservabilityRuntime();
  if (
    instrumentedRouters.has(router)
    || !runtime.config.enabled
    || !runtime.config.routerTelemetryEnabled
  ) {
    return;
  }

  let activeNavigationSpan: Span | null = null;

  router.beforeEach((to, from) => {
    if (activeNavigationSpan) {
      activeNavigationSpan.end();
    }

    activeNavigationSpan = runtime.config.tracingEnabled
      ? runtime.tracer.startSpan("router.navigation", {
        attributes: buildRouteTelemetryAttributes(to, from),
      })
      : null;

    runtime.addBreadcrumb({
      category: "frontend.router",
      message: "route.navigation_started",
      level: "info",
      data: buildRouteTelemetryAttributes(to, from),
    });
  });

  router.afterEach((to, from, failure) => {
    const attributes = buildRouteTelemetryAttributes(to, from);

    runtime.addBreadcrumb({
      category: "frontend.router",
      message: failure ? "route.navigation_failed" : "route.navigation_completed",
      level: failure ? "warning" : "info",
      data: attributes,
    });

    if (!activeNavigationSpan) {
      return;
    }

    if (failure) {
      activeNavigationSpan.recordException(new Error(sanitizeErrorMessage(failure)));
      activeNavigationSpan.setStatus({
        code: SpanStatusCode.ERROR,
        message: sanitizeErrorMessage(failure),
      });
    } else {
      activeNavigationSpan.setAttributes(attributes);
      activeNavigationSpan.setStatus({
        code: SpanStatusCode.OK,
      });
    }

    activeNavigationSpan.end();
    activeNavigationSpan = null;
  });

  router.onError((error) => {
    if (activeNavigationSpan) {
      activeNavigationSpan.recordException(error instanceof Error ? error : new Error(sanitizeErrorMessage(error)));
      activeNavigationSpan.setStatus({
        code: SpanStatusCode.ERROR,
        message: sanitizeErrorMessage(error),
      });
      activeNavigationSpan.end();
      activeNavigationSpan = null;
    }

    trackAsyncBoundaryFailure("route.navigation", error, {
      flow: "router",
    });
  });

  instrumentedRouters.add(router);
}

export function buildRouteTelemetryAttributes(
  to: RouteLocationNormalizedLoaded | RouteLocationNormalized,
  from?: RouteLocationNormalizedLoaded | RouteLocationNormalized,
): Attributes {
  return {
    "route.to.name": routeName(to.name),
    "route.to.path": routePattern(to),
    "route.to.params.keys": sanitizeRouteKeyCollection(to.params),
    "route.to.query.keys": sanitizeRouteKeyCollection(to.query),
    "route.to.matched": to.matched.map((record) => record.path).join(","),
    "route.to.lazy": to.meta.lazy === true,
    "route.from.name": from ? routeName(from.name) : "direct-entry",
    "route.from.path": from ? routePattern(from) : "direct-entry",
  };
}

function routeName(name: RouteLocationNormalized["name"]): string {
  return typeof name === "string" && name.trim()
    ? name
    : "anonymous-route";
}

function routePattern(route: RouteLocationNormalizedLoaded | RouteLocationNormalized): string {
  return route.matched.at(-1)?.path ?? route.path;
}
