import { mount } from "@vue/test-utils";

import {
  AppButton,
  AppCard,
  AppDivider,
  AppInline,
  AppStack,
  AppText,
  EmptyState,
  StatusBadge,
} from "@/shared/ui";

describe("shared/ui primitives", () => {
  it("compose layout, surface, status, and empty states through the shared boundary", () => {
    const wrapper = mount({
      components: {
        AppButton,
        AppCard,
        AppDivider,
        AppInline,
        AppStack,
        AppText,
        EmptyState,
        StatusBadge,
      },
      template: `
        <AppStack gap="md">
          <AppCard title="Adapter-ready card" description="Shared UI stays stable.">
            <AppInline justify="between">
              <StatusBadge tone="success" variant="solid">healthy</StatusBadge>
              <AppButton variant="soft" tone="accent">Inspect</AppButton>
            </AppInline>
            <AppDivider label="details" />
            <AppText as="p" tone="muted">Primitive composition works.</AppText>
          </AppCard>
          <EmptyState title="Nothing here" description="Empty state support is part of the shared UI boundary." />
        </AppStack>
      `,
    });

    expect(wrapper.text()).toContain("Adapter-ready card");
    expect(wrapper.text()).toContain("healthy");
    expect(wrapper.text()).toContain("Primitive composition works.");
    expect(wrapper.text()).toContain("Nothing here");
  });
});
