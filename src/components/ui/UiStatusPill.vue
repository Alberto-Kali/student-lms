<script setup lang="ts">
withDefaults(
  defineProps<{
    tone?: 'new' | 'progress' | 'done' | 'approved' | 'pending' | 'blocked'
  }>(),
  {
    tone: 'new',
  },
)
</script>

<template>
  <span :class="['ui-status-pill', `ui-status-pill--${tone}`]">
    <slot />
  </span>
</template>
