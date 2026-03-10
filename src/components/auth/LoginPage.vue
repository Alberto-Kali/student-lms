<script setup lang="ts">
import { ref } from 'vue'
import UiButton from '../ui/UiButton.vue'
import UiField from '../ui/UiField.vue'
import UiPanel from '../ui/UiPanel.vue'
import UiStatusPill from '../ui/UiStatusPill.vue'
import type { DemoAccount } from '../../types/lms'

const props = defineProps<{
  error: string
  loading?: boolean
  demoAccounts: DemoAccount[]
}>()

const emit = defineEmits<{
  login: [credentials: { username: string; password: string }]
}>()

const username = ref('')
const password = ref('')

const submit = () => {
  emit('login', {
    username: username.value.trim(),
    password: password.value,
  })
}

const roleLabel: Record<DemoAccount['role'], string> = {
  admin: 'Администратор',
  student: 'Студент',
  teacher: 'Преподаватель',
}

const statusLabel: Record<DemoAccount['status'], string> = {
  approved: 'Одобрен',
  pending: 'Ожидает одобрения',
  blocked: 'Заблокирован',
}

const statusTone: Record<DemoAccount['status'], 'approved' | 'pending' | 'blocked'> = {
  approved: 'approved',
  pending: 'pending',
  blocked: 'blocked',
}
</script>

<template>
  <div class="auth-shell">
    <UiPanel title="Вход в College39 LMS" subtitle="Регистрация отключена. Используйте существующий аккаунт.">
      <form class="auth-form" @submit.prevent="submit">
        <UiField v-model="username" label="Логин" placeholder="Введите логин" />
        <UiField v-model="password" type="password" label="Пароль" placeholder="Введите пароль" />
        <p v-if="props.error" class="auth-error">{{ props.error }}</p>
        <UiButton type="submit" :disabled="props.loading">{{ props.loading ? 'Входим…' : 'Войти' }}</UiButton>
      </form>
    </UiPanel>

    <UiPanel title="Демо-аккаунты" subtitle="Для проверки разных ролей и статусов.">
      <div class="demo-list">
        <div v-for="account in props.demoAccounts" :key="account.username" class="demo-item">
          <div>
            <p class="demo-name">{{ account.full_name }}</p>
            <p class="demo-meta">{{ roleLabel[account.role] }} · {{ account.username }} / {{ account.password }}</p>
          </div>
          <UiStatusPill :tone="statusTone[account.status]">{{ statusLabel[account.status] }}</UiStatusPill>
        </div>
      </div>
    </UiPanel>
  </div>
</template>
