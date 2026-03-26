import {
  createRouter,
  createWebHistory,
  type Router,
  type RouteRecordRaw,
  type RouterHistory,
} from "vue-router";

export const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "home",
    component: () => import("@/pages/home/ui/HomePage.vue"),
    meta: {
      title: "Frontend foundation",
      description: "Layered app shell, UI adapter boundary, typed API access and governed frontend checks.",
      lazy: true,
    },
  },
  {
    path: "/:pathMatch(.*)*",
    name: "not-found",
    component: () => import("@/pages/not-found/ui/NotFoundPage.vue"),
    meta: {
      title: "Route not found",
      description: "The router resolves unknown paths through an explicit not-found route.",
      lazy: true,
    },
  },
];

export function createAppRouter(
  history: RouterHistory = createWebHistory(import.meta.env.BASE_URL),
): Router {
  return createRouter({
    history,
    routes,
    scrollBehavior() {
      return { top: 0 };
    },
  });
}
