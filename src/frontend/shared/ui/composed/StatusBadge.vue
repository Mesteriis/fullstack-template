<script setup lang="ts">
withDefaults(
  defineProps<{
    tone?: "neutral" | "info" | "success" | "warning" | "danger";
    variant?: "soft" | "solid" | "outline";
    size?: "sm" | "md";
  }>(),
  {
    tone: "neutral",
    variant: "soft",
    size: "md",
  },
);
</script>

<template>
  <span
    class="status-badge"
    :class="[
      `tone-${tone}`,
      `variant-${variant}`,
      `size-${size}`,
    ]"
  >
    <slot />
  </span>
</template>
