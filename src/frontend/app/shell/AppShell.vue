<script setup lang="ts">
import {
  AppContainer,
  AppInline,
  AppStack,
  AppSurface,
  AppText,
  AppTitle,
  StatusBadge,
} from "@/shared/ui";

withDefaults(
  defineProps<{
    eyebrow?: string;
    title: string;
    description?: string;
  }>(),
  {
    eyebrow: "",
    description: "",
  },
);
</script>

<template>
  <AppContainer
    as="div"
    size="wide"
    pad="lg"
  >
    <AppStack gap="lg">
      <AppSurface
        as="header"
        tone="muted"
        padding="lg"
        radius="lg"
        elevated
      >
        <AppStack gap="md">
          <AppInline
            align="start"
            justify="between"
            gap="md"
          >
            <AppStack gap="xs">
              <AppText
                v-if="eyebrow"
                as="span"
                size="sm"
                tone="accent"
                inline
              >
                {{ eyebrow }}
              </AppText>
              <AppTitle
                as="h1"
                size="lg"
              >
                {{ title }}
              </AppTitle>
            </AppStack>

            <StatusBadge
              tone="info"
              variant="soft"
            >
              Template-grade frontend
            </StatusBadge>
          </AppInline>

          <AppText
            v-if="description"
            as="p"
            tone="muted"
          >
            {{ description }}
          </AppText>
        </AppStack>
      </AppSurface>

      <AppSurface
        as="main"
        padding="lg"
        radius="lg"
        elevated
      >
        <slot />
      </AppSurface>
    </AppStack>
  </AppContainer>
</template>
