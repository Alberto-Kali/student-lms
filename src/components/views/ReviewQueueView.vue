<script setup lang="ts">
import UiPanel from '../ui/UiPanel.vue'
import type { NotificationItem, ReviewQueueItem } from '../../types/lms'

defineProps<{
  reviewQueue: ReviewQueueItem[]
  notifications: NotificationItem[]
}>()
</script>

<template>
  <div class="grid resources-grid">
    <UiPanel title="Очередь проверки" subtitle="Результаты, отправленные преподавателю и админу">
      <div class="feed-list">
        <div v-for="item in reviewQueue" :key="item.attempt_id" class="feed-item">
          <strong>{{ item.student_name }} · {{ item.score }}%</strong>
          <span>{{ item.course_title }} / {{ item.test_title }}</span>
        </div>
        <span v-if="reviewQueue.length === 0" class="demo-meta">Пока нет новых работ.</span>
      </div>
    </UiPanel>

    <UiPanel title="Уведомления о сдаче" subtitle="То, что уходит в inbox">
      <div class="feed-list">
        <div v-for="notification in notifications" :key="notification.id" class="feed-item">
          <strong>{{ notification.title }}</strong>
          <span>{{ notification.body }}</span>
        </div>
      </div>
    </UiPanel>
  </div>
</template>
