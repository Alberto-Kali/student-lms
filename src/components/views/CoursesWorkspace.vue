<script setup lang="ts">
import { computed } from 'vue'
import UiButton from '../ui/UiButton.vue'
import UiPanel from '../ui/UiPanel.vue'
import UiStatusPill from '../ui/UiStatusPill.vue'
import type { CourseDetail, CourseSummary, TestSummary, UserRole } from '../../types/lms'

const props = defineProps<{
  courses: CourseSummary[]
  courseDetail: CourseDetail | null
  selectedCourseId: string
  loading: boolean
  role: UserRole
  focus: 'courses' | 'tests'
}>()

const emit = defineEmits<{
  selectCourse: [courseId: string]
  completeModule: [courseId: string, moduleId: string]
  startTest: [testId: string]
}>()

const canCompleteModules = computed(() => props.role === 'student')

function statusTone(test: TestSummary) {
  if (test.latest_status === 'passed' || test.latest_status === 'submitted') return 'done'
  if (test.latest_status === 'in_progress') return 'progress'
  return 'new'
}
</script>

<template>
  <div class="workspace-grid">
    <UiPanel title="Курсы" subtitle="Выберите курс для деталей">
      <div class="feed-list">
        <button
          v-for="course in props.courses"
          :key="course.id"
          class="course-pick"
          :class="{ active: course.id === props.selectedCourseId }"
          @click="emit('selectCourse', course.id)"
        >
          <strong>{{ course.title }}</strong>
          <span>{{ course.teacher_name }} · {{ course.progress }}%</span>
        </button>
      </div>
    </UiPanel>

    <UiPanel
      :title="props.courseDetail?.course.title ?? 'Детали курса'"
      :subtitle="props.courseDetail?.course.description ?? 'Загрузка курса...'"
      :highlight="props.focus === 'tests'"
    >
      <div v-if="props.loading" class="empty-state">Загружаем структуру курса…</div>
      <div v-else-if="!props.courseDetail" class="empty-state">Выберите курс слева.</div>
      <div v-else class="stack">
        <div v-if="props.focus === 'courses'" class="stack">
          <div class="section-head">
            <h3>Модули курса</h3>
            <span>Прогресс: {{ props.courseDetail.course.progress }}%</span>
          </div>
          <div class="feed-list">
            <div v-for="module in props.courseDetail.modules" :key="module.id" class="module-card">
              <div>
                <strong>{{ module.position }}. {{ module.title }}</strong>
                <p>{{ module.content }}</p>
                <small>{{ module.estimated_minutes }} мин</small>
              </div>
              <div class="module-actions">
                <UiStatusPill :tone="module.completed ? 'done' : 'new'">
                  {{ module.completed ? 'Пройден' : 'Не завершён' }}
                </UiStatusPill>
                <UiButton
                  v-if="canCompleteModules && !module.completed"
                  variant="success"
                  @click="emit('completeModule', props.courseDetail.course.id, module.id)"
                >
                  Завершить
                </UiButton>
              </div>
            </div>
          </div>
        </div>

        <div class="stack">
          <div class="section-head">
            <h3>Тесты</h3>
            <span>{{ props.courseDetail.tests.length }} активных тестов</span>
          </div>
          <div class="test-grid grid">
            <div v-for="test in props.courseDetail.tests" :key="test.id" class="test-card">
              <div class="test-top">
                <h4>{{ test.title }}</h4>
                <UiStatusPill :tone="statusTone(test)">
                  {{ test.latest_status }}
                </UiStatusPill>
              </div>
              <p>{{ test.description }}</p>
              <p class="demo-meta">
                {{ test.duration_minutes }} мин · проходной {{ test.passing_score }}% · максимум {{ test.max_attempts }} попытки
              </p>
              <p v-if="test.latest_score !== null" class="score">Последний результат: {{ test.latest_score }}%</p>
              <UiButton v-if="props.role === 'student'" @click="emit('startTest', test.id)">Запустить тест</UiButton>
            </div>
          </div>
        </div>
      </div>
    </UiPanel>
  </div>
</template>
