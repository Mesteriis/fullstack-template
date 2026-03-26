<script setup lang="ts">
withDefaults(
  defineProps<{
    as?: "div" | "section" | "article" | "main" | "nav" | "aside";
    size?: "narrow" | "content" | "wide" | "full";
    pad?: "none" | "sm" | "md" | "lg";
    center?: boolean;
  }>(),
  {
    as: "div",
    size: "content",
    pad: "md",
    center: true,
  },
);
</script>

<template>
  <component
    :is="as"
    class="app-container"
    :class="[
      `size-${size}`,
      `pad-${pad}`,
      { 'is-centered': center },
    ]"
  >
    <slot />
  </component>
</template>
