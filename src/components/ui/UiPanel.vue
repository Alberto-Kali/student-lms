<script setup lang="ts">
defineProps<{
  title?: string
  subtitle?: string
  highlight?: boolean
}>()
</script>

<template>
  <article :class="['ui-panel', { 'ui-panel--highlight': highlight }]">
    <header v-if="title || subtitle" class="ui-panel__head">
      <h3 v-if="title">{{ title }}</h3>
      <span v-if="subtitle">{{ subtitle }}</span>
    </header>
    <slot />
  </article>
</template>
