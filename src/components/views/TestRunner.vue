<script setup lang="ts">
import { reactive } from 'vue'
import UiButton from '../ui/UiButton.vue'
import UiPanel from '../ui/UiPanel.vue'
import type { TestAnswerSubmission, TestAttemptStart } from '../../types/lms'

const props = defineProps<{
  attempt: TestAttemptStart
  submitting: boolean
}>()

const emit = defineEmits<{
  submit: [answers: TestAnswerSubmission[]]
  close: []
}>()

const answers = reactive<Record<string, number[]>>({})

function toggleAnswer(questionId: string, optionIndex: number, multiple: boolean) {
  const current = answers[questionId] ?? []
  if (!multiple) {
    answers[questionId] = [optionIndex]
    return
  }
  answers[questionId] = current.includes(optionIndex)
    ? current.filter((value) => value !== optionIndex)
    : [...current, optionIndex].sort((left, right) => left - right)
}

function submit() {
  emit(
    'submit',
    props.attempt.questions.map((question) => ({
      question_id: question.id,
      selected_option_ids: answers[question.id] ?? [],
    })),
  )
}
</script>

<template>
  <div class="runner-overlay">
    <UiPanel :title="attempt.test.title" :subtitle="attempt.test.description" highlight class="runner-panel">
      <div class="stack">
        <div v-for="question in attempt.questions" :key="question.id" class="module-card">
          <div class="section-head">
            <strong>{{ question.position }}. {{ question.prompt }}</strong>
            <span>{{ question.points }} баллов</span>
          </div>
          <div class="feed-list">
            <label v-for="(option, index) in question.options" :key="option" class="answer-option">
              <input
                :type="question.question_type === 'multiple' ? 'checkbox' : 'radio'"
                :name="question.id"
                :checked="(answers[question.id] ?? []).includes(index)"
                @change="toggleAnswer(question.id, index, question.question_type === 'multiple')"
              />
              <span>{{ option }}</span>
            </label>
          </div>
        </div>

        <div class="actions-row">
          <UiButton variant="ghost" @click="emit('close')">Отмена</UiButton>
          <UiButton :disabled="submitting" @click="submit">
            {{ submitting ? 'Отправляем…' : 'Сдать тест' }}
          </UiButton>
        </div>
      </div>
    </UiPanel>
  </div>
</template>
