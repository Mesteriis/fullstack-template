<script setup lang="ts">
withDefaults(
  defineProps<{
    as?: "span" | "p" | "small" | "strong" | "em" | "code";
    size?: "sm" | "md" | "lg";
    tone?: "default" | "muted" | "accent" | "success" | "warning" | "danger";
    align?: "start" | "center" | "end";
    inline?: boolean;
    truncate?: boolean;
  }>(),
  {
    as: "p",
    size: "md",
    tone: "default",
    align: "start",
    inline: false,
    truncate: false,
  },
);
</script>

<template>
  <component
    :is="as"
    class="app-text"
    :class="[
      `size-${size}`,
      `tone-${tone}`,
      `align-${align}`,
      { 'is-inline': inline, 'is-truncated': truncate },
    ]"
  >
    <slot />
  </component>
</template>
