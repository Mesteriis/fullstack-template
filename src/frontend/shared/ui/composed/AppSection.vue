<script setup lang="ts">
import AppInline from "@/shared/ui/primitives/AppInline.vue";
import AppStack from "@/shared/ui/primitives/AppStack.vue";
import AppText from "@/shared/ui/primitives/AppText.vue";
import AppTitle from "@/shared/ui/primitives/AppTitle.vue";

withDefaults(
  defineProps<{
    as?: "div" | "section" | "article" | "main";
    title?: string;
    description?: string;
    gap?: "sm" | "md" | "lg";
    align?: "start" | "center";
  }>(),
  {
    as: "section",
    title: "",
    description: "",
    gap: "md",
    align: "start",
  },
);
</script>

<template>
  <component
    :is="as"
    class="app-section"
    :class="[
      `gap-${gap}`,
      `align-${align}`,
    ]"
  >
    <AppInline
      v-if="$slots.header || $slots.actions || title || description"
      as="header"
      align="start"
      justify="between"
      gap="md"
      class="app-section__header"
    >
      <slot name="header">
        <AppStack gap="xs">
          <AppTitle
            v-if="title"
            as="h2"
            size="md"
            :align="align"
          >
            {{ title }}
          </AppTitle>
          <AppText
            v-if="description"
            as="p"
            tone="muted"
            :align="align"
          >
            {{ description }}
          </AppText>
        </AppStack>
      </slot>

      <div
        v-if="$slots.actions"
        class="app-section__actions"
      >
        <slot name="actions" />
      </div>
    </AppInline>

    <div class="app-section__body">
      <slot />
    </div>
  </component>
</template>
