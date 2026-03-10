export type UserRole = 'admin' | 'student' | 'teacher'

export type AccountStatus = 'approved' | 'pending' | 'blocked'

export type PageId =
  | 'home'
  | 'courses'
  | 'tests'
  | 'schedule'
  | 'reviews'
  | 'notifications'
  | 'links'
  | 'profile'

export type NavItem = {
  id: PageId
  label: string
}

export type UserProfile = {
  id: string
  username: string
  full_name: string
  role: UserRole
  status: AccountStatus
  email: string
  group_name: string
  department: string
}

export type DemoAccount = {
  username: string
  password: string
  full_name: string
  role: UserRole
  status: AccountStatus
}

export type AuthSession = {
  access_token: string
  token_type: string
  expires_at: string
  user: UserProfile
}

export type CourseSummary = {
  id: string
  title: string
  description: string
  teacher_name: string
  audience: string
  status: string
  progress: number
}

export type CourseModule = {
  id: string
  title: string
  content: string
  position: number
  estimated_minutes: number
  completed: boolean
  completed_at: string | null
}

export type TestSummary = {
  id: string
  course_id: string
  title: string
  description: string
  duration_minutes: number
  max_attempts: number
  passing_score: number
  latest_status: 'new' | 'in_progress' | 'submitted' | 'failed' | 'passed'
  latest_score: number | null
}

export type CourseDetail = {
  course: CourseSummary
  modules: CourseModule[]
  tests: TestSummary[]
}

export type TestQuestion = {
  id: string
  prompt: string
  options: string[]
  question_type: 'single' | 'multiple'
  position: number
  points: number
}

export type TestAttemptStart = {
  attempt_id: string
  started_at: string
  test: TestSummary
  questions: TestQuestion[]
}

export type TestAnswerSubmission = {
  question_id: string
  selected_option_ids: number[]
}

export type TestAttemptResult = {
  attempt_id: string
  status: 'passed' | 'failed'
  score: number
  passing_score: number
  earned_points: number
  total_points: number
  submitted_at: string
}

export type ScheduleSlot = {
  id: string
  course_id: string
  subject: string
  room: string
  group_name: string
  day_of_week: number
  starts_at: string
  ends_at: string
  teacher_name: string
}

export type NotificationItem = {
  id: string
  kind: string
  title: string
  body: string
  entity_type: string
  entity_id: string
  created_at: string
  is_read: boolean
}

export type ExternalUserLink = {
  id: string
  external_system: string
  external_user_id: string
  external_username: string
  linked_at: string
}

export type ReviewQueueItem = {
  attempt_id: string
  student_name: string
  course_title: string
  test_title: string
  score: number
  submitted_at: string
  teacher_name: string
}

export type DashboardPayload = {
  user: UserProfile
  courses: CourseSummary[]
  schedule: ScheduleSlot[]
  notifications: NotificationItem[]
  external_links: ExternalUserLink[]
  review_queue: ReviewQueueItem[]
  demo_accounts: DemoAccount[]
}
