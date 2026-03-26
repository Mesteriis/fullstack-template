import { flushPromises, mount } from "@vue/test-utils";
import { defineComponent } from "vue";

import { useSystemHealth } from "@/features/system-health/model/useSystemHealth";
import { trackWidgetFailure } from "@/shared/observability";

vi.mock("@/shared/observability", async () => {
  const actual = await vi.importActual<typeof import("@/shared/observability")>("@/shared/observability");

  return {
    ...actual,
    trackAsyncBoundaryFailure: vi.fn(),
    trackWidgetFailure: vi.fn(),
  };
});

describe("useSystemHealth", () => {
  it("tracks feature-level API failures and exposes a stable error state", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        json: async () => ({
          message: "Health degraded.",
        }),
      } satisfies Partial<Response>),
    );

    const wrapper = mount(defineComponent({
      setup() {
        return useSystemHealth();
      },
      template: "<div />",
    }));

    await flushPromises();
    await flushPromises();

    expect(wrapper.vm.isLoading).toBe(false);
    expect(wrapper.vm.health).toBeNull();
    expect(wrapper.vm.error).toMatchObject({
      kind: "http",
      status: 503,
      message: "Health degraded.",
    });
    expect(trackWidgetFailure).toHaveBeenCalledTimes(1);
  });
});
