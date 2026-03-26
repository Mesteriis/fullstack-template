<script setup lang="ts">
import { onMounted } from "vue";

import { SystemHealthPanel } from "@/features/system-health";
import { trackPageMountComplete } from "@/shared/observability";
import {
  AppCard,
  AppSection,
  AppStack,
  AppText,
} from "@/shared/ui";

onMounted(() => {
  trackPageMountComplete("home", {
    route: "home",
  });
});
</script>

<template>
  <AppStack gap="lg">
    <AppSection
      title="Layered shell is active"
      description="Pages stay thin, features own reusable flows, and shared/ui remains the only primitive surface."
    >
      <AppStack gap="md">
        <AppCard
          title="UI adapter boundary"
          description="Local App* primitives are intentionally shaped for low-cost migration to ww-ui-kit."
        >
          <AppText
            as="p"
            tone="muted"
          >
            The page composes only features and shared UI primitives. No route-level raw markup or local style leakage is needed.
          </AppText>
        </AppCard>

        <SystemHealthPanel />
      </AppStack>
    </AppSection>
  </AppStack>
</template>
