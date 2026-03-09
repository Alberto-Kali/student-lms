<script setup lang="ts">
import { ref } from 'vue'
import UiButton from '../ui/UiButton.vue'
import UiField from '../ui/UiField.vue'
import UiPanel from '../ui/UiPanel.vue'
import UiStatusPill from '../ui/UiStatusPill.vue'
import type { Account } from '../../types/lms'

const props = defineProps<{
  error: string
  demoAccounts: Account[]
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

const roleLabel: Record<Account['role'], string> = {
  admin: 'Администратор',
  student: 'Студент',
  teacher: 'Преподаватель',
}

const statusLabel: Record<Account['status'], string> = {
  approved: 'Одобрен',
  pending: 'Ожидает одобрения',
  blocked: 'Заблокирован',
}

const statusTone: Record<Account['status'], 'approved' | 'pending' | 'blocked'> = {
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
        <UiButton type="submit">Войти</UiButton>
      </form>
    </UiPanel>

    <UiPanel title="Демо-аккаунты" subtitle="Для проверки разных ролей и статусов.">
      <div class="demo-list">
        <div v-for="account in props.demoAccounts" :key="account.id" class="demo-item">
          <div>
            <p class="demo-name">{{ account.name }}</p>
            <p class="demo-meta">{{ roleLabel[account.role] }} · {{ account.username }} / {{ account.password }}</p>
          </div>
          <UiStatusPill :tone="statusTone[account.status]">{{ statusLabel[account.status] }}</UiStatusPill>
        </div>
      </div>
    </UiPanel>
  </div>
</template>
