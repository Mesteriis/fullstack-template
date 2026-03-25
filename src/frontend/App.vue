<script setup lang="ts">
const highlights = [
  "Vue 3 with script setup",
  "TypeScript in strict mode",
  "Vite dev/build pipeline",
];
</script>

<template>
  <main class="shell">
    <section class="hero">
      <p class="eyebrow">src/frontend</p>
      <h1>Base Vue 3 application</h1>
      <p class="lead">
        Minimal starting point for the frontend layer with Vue 3, TypeScript and Vite.
      </p>

      <ul class="highlights">
        <li v-for="item in highlights" :key="item">
          {{ item }}
        </li>
      </ul>
    </section>
  </main>
</template>
