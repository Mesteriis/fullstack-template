<script setup lang="ts">
import AppInline from "@/shared/ui/primitives/AppInline.vue";
import AppStack from "@/shared/ui/primitives/AppStack.vue";
import AppText from "@/shared/ui/primitives/AppText.vue";
import AppTitle from "@/shared/ui/primitives/AppTitle.vue";

withDefaults(
  defineProps<{
    title: string;
    description?: string;
    align?: "start" | "center";
  }>(),
  {
    description: "",
    align: "center",
  },
);
</script>

<template>
  <AppStack
    gap="md"
    class="empty-state"
    :class="`align-${align}`"
  >
    <div
      v-if="$slots.media"
      class="empty-state__media"
    >
      <slot name="media" />
    </div>

    <AppStack gap="xs">
      <AppTitle
        as="h2"
        size="sm"
        :align="align"
      >
        {{ title }}
      </AppTitle>
      <AppText
        v-if="description"
        as="p"
        tone="muted"
        :align="align"
      >
        {{ description }}
      </AppText>
    </AppStack>

    <AppInline
      v-if="$slots.actions"
      :justify="align === 'center' ? 'center' : 'start'"
      gap="sm"
      class="empty-state__actions"
    >
      <slot name="actions" />
    </AppInline>
  </AppStack>
</template>
