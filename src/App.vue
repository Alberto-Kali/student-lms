<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import LoginPage from './components/auth/LoginPage.vue'
import HomeOverview from './components/views/HomeOverview.vue'
import CoursesWorkspace from './components/views/CoursesWorkspace.vue'
import ProfileView from './components/views/ProfileView.vue'
import ReviewQueueView from './components/views/ReviewQueueView.vue'
import ScheduleBoard from './components/views/ScheduleBoard.vue'
import TestRunner from './components/views/TestRunner.vue'
import UiAlert from './components/ui/UiAlert.vue'
import UiButton from './components/ui/UiButton.vue'
import UiTabs from './components/ui/UiTabs.vue'
import { completeModule, fetchCourseDetail, fetchDashboard, submitTestAttempt } from './api/lms'
import { startTestAttempt } from './api/lms'
import { useSession } from './composables/useSession'
import type { CourseDetail, DashboardPayload, NavItem, PageId, TestAnswerSubmission, TestAttemptStart, UserRole } from './types/lms'

const { user, demoAccounts, authenticated, authLoading, loadDemoAccounts, restore, login, logout } = useSession()

const dashboard = ref<DashboardPayload | null>(null)
const selectedPage = ref<PageId>('home')
const selectedCourseId = ref('')
const courseDetail = ref<CourseDetail | null>(null)
const courseLoading = ref(false)
const busyMessage = ref('')
const banner = ref<{ tone: 'success' | 'danger' | 'info'; text: string } | null>(null)
const activeAttempt = ref<TestAttemptStart | null>(null)
const testSubmitting = ref(false)

const navByRole: Record<UserRole, NavItem[]> = {
  student: [
    { id: 'home', label: 'Главная' },
    { id: 'courses', label: 'Курсы' },
    { id: 'tests', label: 'Тесты' },
    { id: 'schedule', label: 'Расписание' },
    { id: 'notifications', label: 'Inbox' },
    { id: 'profile', label: 'Профиль' },
  ],
  teacher: [
    { id: 'home', label: 'Главная' },
    { id: 'courses', label: 'Курсы' },
    { id: 'schedule', label: 'Расписание' },
    { id: 'reviews', label: 'Проверка' },
    { id: 'links', label: 'Внешние LMS' },
    { id: 'profile', label: 'Профиль' },
  ],
  admin: [
    { id: 'home', label: 'Главная' },
    { id: 'courses', label: 'Курсы' },
    { id: 'reviews', label: 'Проверка' },
    { id: 'notifications', label: 'Inbox' },
    { id: 'links', label: 'Внешние LMS' },
    { id: 'profile', label: 'Профиль' },
  ],
}

const activeNav = computed(() => (user.value ? navByRole[user.value.role] : []))

async function refreshDashboard() {
  const nextDashboard = await fetchDashboard()
  dashboard.value = nextDashboard
  const firstCourse = nextDashboard.courses[0]
  if (!selectedCourseId.value && firstCourse) {
    selectedCourseId.value = firstCourse.id
  }
}

async function loadCourse(courseId: string) {
  courseLoading.value = true
  try {
    selectedCourseId.value = courseId
    courseDetail.value = await fetchCourseDetail(courseId)
  } finally {
    courseLoading.value = false
  }
}

async function handleLogin(credentials: { username: string; password: string }) {
  banner.value = null
  try {
    await login(credentials.username, credentials.password)
    await refreshDashboard()
    if (selectedCourseId.value) {
      await loadCourse(selectedCourseId.value)
    }
  } catch (error) {
    banner.value = { tone: 'danger', text: error instanceof Error ? error.message : 'Ошибка авторизации' }
  }
}

async function handleLogout() {
  await logout()
  dashboard.value = null
  courseDetail.value = null
  activeAttempt.value = null
  selectedCourseId.value = ''
  selectedPage.value = 'home'
  banner.value = null
}

async function handleCompleteModule(courseId: string, moduleId: string) {
  busyMessage.value = 'Фиксируем прохождение модуля…'
  try {
    courseDetail.value = await completeModule(courseId, moduleId)
    await refreshDashboard()
    banner.value = { tone: 'success', text: 'Модуль завершён, прогресс курса обновлён.' }
  } catch (error) {
    banner.value = { tone: 'danger', text: error instanceof Error ? error.message : 'Не удалось обновить прогресс' }
  } finally {
    busyMessage.value = ''
  }
}

async function handleStartTest(testId: string) {
  busyMessage.value = 'Открываем тест…'
  try {
    activeAttempt.value = await startTestAttempt(testId)
  } catch (error) {
    banner.value = { tone: 'danger', text: error instanceof Error ? error.message : 'Не удалось запустить тест' }
  } finally {
    busyMessage.value = ''
  }
}

async function handleSubmitAttempt(answers: TestAnswerSubmission[]) {
  if (!activeAttempt.value) return
  testSubmitting.value = true
  try {
    const result = await submitTestAttempt(activeAttempt.value.test.id, activeAttempt.value.attempt_id, answers)
    banner.value = {
      tone: result.status === 'passed' ? 'success' : 'info',
      text: `Тест отправлен. Результат ${result.score}% (${result.earned_points}/${result.total_points} баллов).`,
    }
    activeAttempt.value = null
    await refreshDashboard()
    if (selectedCourseId.value) {
      await loadCourse(selectedCourseId.value)
    }
  } catch (error) {
    banner.value = { tone: 'danger', text: error instanceof Error ? error.message : 'Не удалось отправить тест' }
  } finally {
    testSubmitting.value = false
  }
}

watch(selectedCourseId, async (courseId) => {
  if (authenticated.value && courseId) {
    await loadCourse(courseId)
  }
})

onMounted(async () => {
  await loadDemoAccounts()
  try {
    await restore()
    if (authenticated.value) {
      await refreshDashboard()
      if (selectedCourseId.value) {
        await loadCourse(selectedCourseId.value)
      }
    }
  } catch (error) {
    banner.value = { tone: 'danger', text: error instanceof Error ? error.message : 'Не удалось восстановить сессию' }
    await handleLogout()
  }
})
</script>

<template>
  <LoginPage
    v-if="!authenticated"
    :error="banner?.tone === 'danger' ? banner.text : ''"
    :demo-accounts="demoAccounts"
    :loading="authLoading"
    @login="handleLogin"
  />

  <main v-else-if="dashboard && user" class="app-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">College39 LMS Beta</p>
        <h1>Цифровой кабинет обучения и проверки результатов</h1>
      </div>

      <div class="user-chip">
        <strong>{{ user.full_name }}</strong>
        <span class="user-role">{{ user.role }} · {{ user.email }}</span>
        <UiButton variant="ghost" @click="handleLogout">Выйти</UiButton>
      </div>
    </header>

    <UiTabs :items="activeNav" :active="selectedPage" @change="selectedPage = $event" />

    <div class="alerts-stack">
      <UiAlert v-if="busyMessage" tone="info" title="Запрос в работе">{{ busyMessage }}</UiAlert>
      <UiAlert v-if="banner" :tone="banner.tone" title="Статус">{{ banner.text }}</UiAlert>
    </div>

    <section class="page">
      <HomeOverview
        v-if="selectedPage === 'home'"
        :courses="dashboard.courses"
        :notifications="dashboard.notifications"
        :review-queue="dashboard.review_queue"
        :schedule="dashboard.schedule"
      />

      <CoursesWorkspace
        v-else-if="selectedPage === 'courses' || selectedPage === 'tests'"
        :courses="dashboard.courses"
        :course-detail="courseDetail"
        :selected-course-id="selectedCourseId"
        :loading="courseLoading"
        :role="user.role"
        :focus="selectedPage === 'tests' ? 'tests' : 'courses'"
        @select-course="selectedCourseId = $event"
        @complete-module="handleCompleteModule"
        @start-test="handleStartTest"
      />

      <ScheduleBoard v-else-if="selectedPage === 'schedule'" :schedule="dashboard.schedule" />

      <ReviewQueueView
        v-else-if="selectedPage === 'reviews' || selectedPage === 'notifications'"
        :review-queue="dashboard.review_queue"
        :notifications="dashboard.notifications"
      />

      <ProfileView
        v-else
        :user="dashboard.user"
        :external-links="dashboard.external_links"
        :notifications="dashboard.notifications"
      />
    </section>

    <TestRunner
      v-if="activeAttempt"
      :attempt="activeAttempt"
      :submitting="testSubmitting"
      @submit="handleSubmitAttempt"
      @close="activeAttempt = null"
    />
  </main>
</template>
