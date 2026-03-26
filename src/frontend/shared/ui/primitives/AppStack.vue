<script setup lang="ts">
withDefaults(
  defineProps<{
    as?: "div" | "section" | "article" | "header" | "footer" | "main" | "aside";
    gap?: "none" | "xs" | "sm" | "md" | "lg" | "xl";
    align?: "start" | "center" | "stretch";
  }>(),
  {
    as: "div",
    gap: "md",
    align: "stretch",
  },
);
</script>

<template>
  <component
    :is="as"
    class="app-stack"
    :class="[
      `gap-${gap}`,
      `align-${align}`,
    ]"
  >
    <slot />
  </component>
</template>
