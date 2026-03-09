<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    modelValue: string
    label: string
    type?: 'text' | 'password'
    placeholder?: string
  }>(),
  {
    type: 'text',
    placeholder: '',
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <label class="ui-field">
    <span>{{ props.label }}</span>
    <input
      :type="props.type"
      :value="props.modelValue"
      :placeholder="props.placeholder"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
  </label>
</template>
