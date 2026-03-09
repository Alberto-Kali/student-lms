<script setup lang="ts">
import type { NavItem, PageId } from '../../types/lms'

const props = defineProps<{
  items: NavItem[]
  active: PageId
}>()

const emit = defineEmits<{
  change: [page: PageId]
}>()
</script>

<template>
  <nav class="ui-tabs">
    <button
      v-for="item in props.items"
      :key="item.id"
      :class="['ui-tab-btn', { active: item.id === props.active }]"
      @click="emit('change', item.id)"
    >
      {{ item.label }}
    </button>
  </nav>
</template>
