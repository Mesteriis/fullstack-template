<script setup lang="ts">
withDefaults(
  defineProps<{
    as?: "div" | "section" | "article" | "aside" | "header" | "main";
    tone?: "default" | "muted" | "accent";
    padding?: "none" | "sm" | "md" | "lg";
    border?: "none" | "soft" | "strong";
    radius?: "sm" | "md" | "lg";
    elevated?: boolean;
  }>(),
  {
    as: "div",
    tone: "default",
    padding: "md",
    border: "soft",
    radius: "md",
    elevated: false,
  },
);
</script>

<template>
  <component
    :is="as"
    class="app-surface"
    :class="[
      `tone-${tone}`,
      `padding-${padding}`,
      `border-${border}`,
      `radius-${radius}`,
      { 'is-elevated': elevated },
    ]"
  >
    <slot />
  </component>
</template>
