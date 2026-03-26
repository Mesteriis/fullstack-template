<script setup lang="ts">
import { computed } from "vue";

import { useSystemHealth } from "@/features/system-health/model/useSystemHealth";
import {
  AppButton,
  AppCard,
  AppInline,
  AppStack,
  AppText,
  AppTitle,
  EmptyState,
  StatusBadge,
} from "@/shared/ui";

const {
  error,
  health,
  isLoading,
  load,
} = useSystemHealth();

const healthTone = computed(() => (health.value?.status === "ok" ? "success" : "danger"));
</script>

<template>
  <AppCard
    title="System health"
    description="Feature-level composition over shared/api and typed entity contracts."
  >
    <EmptyState
      v-if="isLoading"
      title="Loading health snapshot"
      description="The feature waits for a typed readiness response before rendering state details."
      align="start"
    />

    <EmptyState
      v-else-if="error"
      title="System health unavailable"
      :description="error.message"
      align="start"
    >
      <template #actions>
        <AppButton
          variant="soft"
          tone="accent"
          @click="load"
        >
          Retry request
        </AppButton>
      </template>
    </EmptyState>

    <AppStack
      v-else-if="health"
      gap="md"
    >
      <AppInline
        align="center"
        justify="between"
        gap="md"
      >
        <AppStack gap="xs">
          <AppTitle
            as="h3"
            size="sm"
          >
            {{ health.service }}
          </AppTitle>
          <AppText
            as="p"
            size="sm"
            tone="muted"
          >
            Readiness data is normalized through the shared HTTP client.
          </AppText>
        </AppStack>

        <StatusBadge
          :tone="healthTone"
          variant="solid"
        >
          {{ health.status }}
        </StatusBadge>
      </AppInline>

      <AppStack gap="sm">
        <AppCard
          v-for="check in health.checks"
          :key="check.name"
          :title="check.name"
          padding="sm"
          tone="muted"
        >
          <AppStack gap="xs">
            <StatusBadge
              :tone="check.status === 'ok' ? 'success' : 'danger'"
              variant="soft"
              size="sm"
            >
              {{ check.status }}
            </StatusBadge>
            <AppText
              as="p"
              size="sm"
              tone="muted"
            >
              {{ check.detail || "No additional dependency detail was provided." }}
            </AppText>
          </AppStack>
        </AppCard>
      </AppStack>
    </AppStack>

    <EmptyState
      v-else
      title="No health payload"
      description="The feature did not receive a readable readiness payload."
      align="start"
    />
  </AppCard>
</template>
