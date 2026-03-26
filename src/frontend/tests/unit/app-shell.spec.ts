import { flushPromises, mount } from "@vue/test-utils";
import { createMemoryHistory } from "vue-router";

import App from "@/app/App.vue";
import { createAppRouter } from "@/app/router";

describe("App shell", () => {
  it("mounts the shell and renders the home route inside it", async () => {
    mockHealthResponse();

    const router = createAppRouter(createMemoryHistory());

    await router.push("/");
    await router.isReady();

    const wrapper = mount(App, {
      global: {
        plugins: [router],
      },
    });

    await flushPromises();

    expect(wrapper.text()).toContain("Frontend foundation");
    expect(wrapper.text()).toContain("Layered shell is active");
    expect(wrapper.text()).toContain("Template-grade frontend");
  });
});

function mockHealthResponse() {
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
        ],
      }),
    } satisfies Partial<Response>),
  );
}
