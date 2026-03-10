import { apiRequest } from './client'
import type {
  CourseDetail,
  CourseSummary,
  DashboardPayload,
  ExternalUserLink,
  NotificationItem,
  ReviewQueueItem,
  ScheduleSlot,
  TestAnswerSubmission,
  TestAttemptResult,
  TestAttemptStart,
} from '../types/lms'

export async function fetchDashboard() {
  return apiRequest<DashboardPayload>('/lms/dashboard')
}

export async function fetchCourses() {
  return apiRequest<CourseSummary[]>('/lms/courses')
}

export async function fetchCourseDetail(courseId: string) {
  return apiRequest<CourseDetail>(`/lms/courses/${courseId}`)
}

export async function completeModule(courseId: string, moduleId: string) {
  return apiRequest<CourseDetail>(`/lms/courses/${courseId}/modules/${moduleId}/complete`, {
    method: 'POST',
  })
}

export async function startTestAttempt(testId: string) {
  return apiRequest<TestAttemptStart>(`/lms/tests/${testId}/attempts`, {
    method: 'POST',
  })
}

export async function submitTestAttempt(testId: string, attemptId: string, answers: TestAnswerSubmission[]) {
  return apiRequest<TestAttemptResult>(`/lms/tests/${testId}/attempts/${attemptId}/submit`, {
    method: 'POST',
    body: JSON.stringify({ answers }),
  })
}

export async function fetchSchedule() {
  return apiRequest<ScheduleSlot[]>('/lms/schedule')
}

export async function fetchNotifications() {
  return apiRequest<NotificationItem[]>('/lms/notifications')
}

export async function fetchExternalLinks() {
  return apiRequest<ExternalUserLink[]>('/lms/external-links')
}

export async function fetchReviewQueue() {
  return apiRequest<ReviewQueueItem[]>('/lms/review-queue')
}
