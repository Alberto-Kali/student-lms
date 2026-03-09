<script setup lang="ts">
withDefaults(
  defineProps<{
    tone?: 'info' | 'success' | 'warning' | 'danger'
    title?: string
  }>(),
  {
    tone: 'info',
    title: '',
  },
)
</script>

<template>
  <div :class="['ui-alert', `ui-alert--${tone}`]" role="alert">
    <p v-if="title" class="ui-alert__title">{{ title }}</p>
    <p><slot /></p>
  </div>
</template>
