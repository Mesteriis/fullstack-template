<script setup lang="ts">
withDefaults(
  defineProps<{
    as?: "div" | "section" | "article" | "header" | "footer" | "nav";
    gap?: "none" | "xs" | "sm" | "md" | "lg";
    align?: "start" | "center" | "end" | "stretch";
    justify?: "start" | "center" | "end" | "between";
    wrap?: boolean;
  }>(),
  {
    as: "div",
    gap: "sm",
    align: "center",
    justify: "start",
    wrap: true,
  },
);
</script>

<template>
  <component
    :is="as"
    class="app-inline"
    :class="[
      `gap-${gap}`,
      `align-${align}`,
      `justify-${justify}`,
      { 'no-wrap': !wrap },
    ]"
  >
    <slot />
  </component>
</template>
