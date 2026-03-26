import { flushPromises, mount } from "@vue/test-utils";

import HomePage from "@/pages/home/ui/HomePage.vue";

describe("HomePage", () => {
  it("renders the routed page and feature panel through shared UI primitives", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          status: "ok",
          service: "Registries API",
          checks: [
            {
              name: "postgresql",
              status: "ok",
              detail: "reachable",
            },
            {
              name: "redis",
              status: "error",
              detail: "connection timed out",
            },
          ],
        }),
      } satisfies Partial<Response>),
    );

    const wrapper = mount(HomePage);

    await flushPromises();
    await flushPromises();

    expect(wrapper.text()).toContain("Layered shell is active");
    expect(wrapper.text()).toContain("System health");
    expect(wrapper.text()).toContain("Registries API");
    expect(wrapper.text()).toContain("postgresql");
    expect(wrapper.text()).toContain("redis");
  });
});
