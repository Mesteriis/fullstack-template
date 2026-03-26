<script setup lang="ts">
import { useRouter } from "vue-router";

import {
  AppButton,
  AppStack,
  EmptyState,
} from "@/shared/ui";

const router = useRouter();

function returnHome(): void {
  void router.push({ name: "home" });
}
</script>

<template>
  <AppStack gap="md">
    <EmptyState
      title="Page not found"
      description="The requested route does not exist in the frontend foundation router."
      align="start"
    >
      <template #actions>
        <AppButton
          variant="soft"
          tone="neutral"
          @click="returnHome"
        >
          Return home
        </AppButton>
      </template>
    </EmptyState>
  </AppStack>
</template>
