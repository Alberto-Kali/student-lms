<script setup lang="ts">
import UiPanel from '../ui/UiPanel.vue'
import type { CourseSummary, NotificationItem, ReviewQueueItem, ScheduleSlot } from '../../types/lms'

const props = defineProps<{
  courses: CourseSummary[]
  notifications: NotificationItem[]
  reviewQueue: ReviewQueueItem[]
  schedule: ScheduleSlot[]
}>()

const dayLabels = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
</script>

<template>
  <div class="stack">
    <section class="hero">
      <div>
        <p class="eyebrow">Beta Prototype</p>
        <h2>Единая LMS с авторизацией, учебным потоком и очередью проверки результатов.</h2>
        <p>Фронт и backend работают от одной модели данных: курсы, модули, тесты, расписание, внешние LMS-связки и уведомления.</p>
      </div>
      <div class="hero-stats">
        <div class="stat-box">Курсов в доступе: {{ props.courses.length }}</div>
        <div class="stat-box">Уведомлений: {{ props.notifications.length }}</div>
        <div class="stat-box">Точек проверки: {{ props.reviewQueue.length }}</div>
      </div>
    </section>

    <div class="grid resources-grid">
      <UiPanel title="Ближайшее расписание" subtitle="Следующие слоты">
        <div class="feed-list">
          <div v-for="slot in props.schedule.slice(0, 4)" :key="slot.id" class="feed-item">
            <strong>{{ dayLabels[slot.day_of_week - 1] }} · {{ slot.starts_at }}-{{ slot.ends_at }}</strong>
            <span>{{ slot.subject }} · {{ slot.room }}</span>
          </div>
        </div>
      </UiPanel>

      <UiPanel title="Уведомления" subtitle="Последние события">
        <div class="feed-list">
          <div v-for="notification in props.notifications.slice(0, 4)" :key="notification.id" class="feed-item">
            <strong>{{ notification.title }}</strong>
            <span>{{ notification.body }}</span>
          </div>
        </div>
      </UiPanel>
    </div>
  </div>
</template>
