<script setup lang="ts">
withDefaults(
  defineProps<{
    as?: "h1" | "h2" | "h3" | "h4" | "h5" | "h6";
    size?: "sm" | "md" | "lg" | "xl";
    tone?: "default" | "muted" | "accent";
    align?: "start" | "center" | "end";
  }>(),
  {
    as: "h2",
    size: "md",
    tone: "default",
    align: "start",
  },
);
</script>

<template>
  <component
    :is="as"
    class="app-title"
    :class="[
      `size-${size}`,
      `tone-${tone}`,
      `align-${align}`,
    ]"
  >
    <slot />
  </component>
</template>
