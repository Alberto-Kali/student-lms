<script setup lang="ts">
import UiPanel from '../ui/UiPanel.vue'
import type { ExternalUserLink, NotificationItem, UserProfile } from '../../types/lms'

defineProps<{
  user: UserProfile
  externalLinks: ExternalUserLink[]
  notifications: NotificationItem[]
}>()
</script>

<template>
  <div class="grid resources-grid">
    <UiPanel title="Профиль" subtitle="Данные из backend">
      <div class="profile-kv">
        <span><strong>Пользователь:</strong> {{ user.full_name }}</span>
        <span><strong>Роль:</strong> {{ user.role }}</span>
        <span><strong>Email:</strong> {{ user.email }}</span>
        <span><strong>Группа:</strong> {{ user.group_name || '—' }}</span>
        <span><strong>Отдел:</strong> {{ user.department || '—' }}</span>
      </div>
    </UiPanel>

    <UiPanel title="Связки с внешними LMS" subtitle="Сверка локальных и внешних идентификаторов">
      <div class="feed-list">
        <div v-for="link in externalLinks" :key="link.id" class="feed-item">
          <strong>{{ link.external_system }}</strong>
          <span>{{ link.external_username }} · {{ link.external_user_id }}</span>
        </div>
        <span v-if="externalLinks.length === 0" class="demo-meta">Для текущего пользователя связок пока нет.</span>
      </div>
    </UiPanel>
  </div>
</template>
