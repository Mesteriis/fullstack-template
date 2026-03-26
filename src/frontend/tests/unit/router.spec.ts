import { flushPromises, mount } from "@vue/test-utils";
import { createMemoryHistory } from "vue-router";

import App from "@/app/App.vue";
import { createAppRouter } from "@/app/router";

describe("router", () => {
  it("resolves the not-found route through the shell", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(),
    );

    const router = createAppRouter(createMemoryHistory());

    await router.push("/missing/route");
    await router.isReady();

    const wrapper = mount(App, {
      global: {
        plugins: [router],
      },
    });

    await flushPromises();

    expect(router.currentRoute.value.name).toBe("not-found");
    expect(wrapper.text()).toContain("Route not found");
    expect(wrapper.text()).toContain("Page not found");
  });
});
