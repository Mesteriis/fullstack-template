<script setup lang="ts">
import { computed } from "vue";
import { RouterView, useRoute } from "vue-router";

import AppShell from "@/app/shell/AppShell.vue";
import { appConfig } from "@/shared/config/env";

const route = useRoute();

const title = computed(() => route.meta.title || appConfig.appName);
const description = computed(() => route.meta.description || "");
</script>

<template>
  <AppShell
    :eyebrow="appConfig.appName"
    :title="title"
    :description="description"
  >
    <RouterView />
  </AppShell>
</template>
