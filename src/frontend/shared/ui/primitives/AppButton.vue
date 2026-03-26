<script setup lang="ts">
import AppText from "@/shared/ui/primitives/AppText.vue";

const props = withDefaults(
  defineProps<{
    variant?: "solid" | "soft" | "ghost";
    tone?: "neutral" | "accent" | "danger";
    size?: "sm" | "md" | "lg";
    type?: "button" | "submit" | "reset";
    align?: "start" | "center" | "end";
    disabled?: boolean;
    loading?: boolean;
    loadingLabel?: string;
    block?: boolean;
  }>(),
  {
    variant: "solid",
    tone: "accent",
    size: "md",
    type: "button",
    align: "center",
    disabled: false,
    loading: false,
    loadingLabel: "Loading",
    block: false,
  },
);

const emit = defineEmits<{
  click: [event: MouseEvent];
}>();

function onClick(event: MouseEvent): void {
  if (props.disabled || props.loading) {
    event.preventDefault();
    return;
  }

  emit("click", event);
}
</script>

<template>
  <button
    class="app-button"
    :class="[
      `variant-${variant}`,
      `tone-${tone}`,
      `size-${size}`,
      `align-${align}`,
      { 'is-block': block, 'is-loading': loading },
    ]"
    :type="type"
    :disabled="disabled || loading"
    :aria-busy="loading ? 'true' : undefined"
    :aria-disabled="disabled || loading ? 'true' : undefined"
    @click="onClick"
  >
    <span
      v-if="$slots.leading"
      class="app-button__slot"
      aria-hidden="true"
    >
      <slot name="leading" />
    </span>

    <AppText
      as="span"
      inline
      class="app-button__label"
    >
      <slot />
    </AppText>

    <AppText
      v-if="loading"
      as="span"
      inline
      class="app-button__status"
      aria-live="polite"
    >
      {{ loadingLabel }}
    </AppText>

    <span
      v-if="$slots.trailing"
      class="app-button__slot"
      aria-hidden="true"
    >
      <slot name="trailing" />
    </span>
  </button>
</template>
