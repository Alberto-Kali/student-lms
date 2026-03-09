<script setup lang="ts">
type Option = {
  value: string
  label: string
}

const props = defineProps<{
  modelValue: string
  label: string
  options: Option[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <label class="ui-field">
    <span>{{ props.label }}</span>
    <select :value="props.modelValue" @change="emit('update:modelValue', ($event.target as HTMLSelectElement).value)">
      <option v-for="option in props.options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
  </label>
</template>
