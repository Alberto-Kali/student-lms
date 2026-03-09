<script setup lang="ts">
import UiButton from './UiButton.vue'

defineProps<{
  show: boolean
  title: string
  text: string
  confirmLabel?: string
  cancelLabel?: string
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()
</script>

<template>
  <div v-if="show" class="ui-dialog" @click.self="emit('cancel')">
    <div class="ui-dialog__card">
      <h4>{{ title }}</h4>
      <p>{{ text }}</p>
      <div class="ui-dialog__actions">
        <UiButton variant="ghost" @click="emit('cancel')">{{ cancelLabel || 'Отмена' }}</UiButton>
        <UiButton variant="danger" @click="emit('confirm')">{{ confirmLabel || 'Подтвердить' }}</UiButton>
      </div>
    </div>
  </div>
</template>
