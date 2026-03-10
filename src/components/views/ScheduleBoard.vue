<script setup lang="ts">
import { computed } from 'vue'
import UiPanel from '../ui/UiPanel.vue'
import type { ScheduleSlot } from '../../types/lms'

const props = defineProps<{
  schedule: ScheduleSlot[]
}>()

const grouped = computed(() => {
  const labels = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
  return labels.map((label, index) => ({
    label,
    items: props.schedule.filter((slot) => slot.day_of_week === index + 1),
  }))
})
</script>

<template>
  <UiPanel title="Расписание" subtitle="Слоты из backend для текущего пользователя">
    <div class="schedule-grid">
      <div v-for="day in grouped" :key="day.label" class="schedule-day">
        <strong>{{ day.label }}</strong>
        <div class="lesson-list">
          <div v-for="slot in day.items" :key="slot.id" class="lesson">
            <span class="lesson-time">{{ slot.starts_at }}-{{ slot.ends_at }}</span>
            <span class="lesson-subject">{{ slot.subject }}</span>
            <span>{{ slot.room }} · {{ slot.teacher_name }}</span>
          </div>
          <span v-if="day.items.length === 0" class="demo-meta">Нет занятий</span>
        </div>
      </div>
    </div>
  </UiPanel>
</template>
