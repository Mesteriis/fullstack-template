<script setup lang="ts">
import AppStack from "@/shared/ui/primitives/AppStack.vue";
import AppSurface from "@/shared/ui/primitives/AppSurface.vue";
import AppText from "@/shared/ui/primitives/AppText.vue";
import AppTitle from "@/shared/ui/primitives/AppTitle.vue";

withDefaults(
  defineProps<{
    as?: "div" | "section" | "article" | "aside";
    title?: string;
    description?: string;
    tone?: "default" | "muted" | "accent";
    padding?: "sm" | "md" | "lg";
    border?: "none" | "soft" | "strong";
    radius?: "sm" | "md" | "lg";
    elevated?: boolean;
  }>(),
  {
    as: "article",
    title: "",
    description: "",
    tone: "default",
    padding: "md",
    border: "soft",
    radius: "md",
    elevated: false,
  },
);
</script>

<template>
  <AppSurface
    :as="as"
    :tone="tone"
    :padding="padding"
    :border="border"
    :radius="radius"
    :elevated="elevated"
    class="app-card"
  >
    <AppStack
      v-if="$slots.header || title || description"
      as="header"
      gap="xs"
      class="app-card__header"
    >
      <slot name="header">
        <AppTitle
          v-if="title"
          as="h3"
          size="sm"
        >
          {{ title }}
        </AppTitle>
        <AppText
          v-if="description"
          as="p"
          size="sm"
          tone="muted"
        >
          {{ description }}
        </AppText>
      </slot>
    </AppStack>

    <div class="app-card__body">
      <slot />
    </div>

    <div
      v-if="$slots.footer"
      class="app-card__footer"
    >
      <slot name="footer" />
    </div>
  </AppSurface>
</template>
