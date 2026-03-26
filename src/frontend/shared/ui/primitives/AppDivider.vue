<script setup lang="ts">
withDefaults(
  defineProps<{
    label?: string;
    orientation?: "horizontal" | "vertical";
  }>(),
  {
    label: "",
    orientation: "horizontal",
  },
);
</script>

<template>
  <div
    class="app-divider"
    :class="`orientation-${orientation}`"
    :role="orientation === 'horizontal' ? 'separator' : undefined"
    :aria-orientation="orientation"
  >
    <span
      v-if="label"
      class="app-divider__label"
    >
      {{ label }}
    </span>
  </div>
</template>
