<script setup lang="ts">
import { onBeforeUnmount, watch } from 'vue'

const props = defineProps<{
  show: boolean
  title: string
}>()

const emit = defineEmits<{
  close: []
}>()

let closeTimer: ReturnType<typeof setTimeout> | null = null

watch(
  () => props.show,
  (isShown) => {
    if (closeTimer) {
      clearTimeout(closeTimer)
      closeTimer = null
    }

    if (isShown) {
      closeTimer = setTimeout(() => {
        emit('close')
      }, 5000)
    }
  },
)

onBeforeUnmount(() => {
  if (closeTimer) {
    clearTimeout(closeTimer)
  }
})
</script>

<template>
  <div v-if="show" class="ui-popup" @click.self="emit('close')">
    <div class="ui-popup__card">
      <header>
        <h4>{{ title }}</h4>
        <button class="ui-popup__close" @click="emit('close')">×</button>
      </header>
      <div class="ui-popup__content">
        <slot />
      </div>
    </div>
  </div>
</template>
