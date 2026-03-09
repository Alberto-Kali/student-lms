<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import LoginPage from './components/auth/LoginPage.vue'
import UiAlert from './components/ui/UiAlert.vue'
import UiButton from './components/ui/UiButton.vue'
import UiDialog from './components/ui/UiDialog.vue'
import UiDropbox from './components/ui/UiDropbox.vue'
import UiField from './components/ui/UiField.vue'
import UiPanel from './components/ui/UiPanel.vue'
import UiPopup from './components/ui/UiPopup.vue'
import UiStatusPill from './components/ui/UiStatusPill.vue'
import UiTabs from './components/ui/UiTabs.vue'
import type { Account, AccountStatus, NavItem, PageId, UserRole } from './types/lms'

type TestStatus = 'new' | 'in-progress' | 'done'
type AlertTone = 'info' | 'success' | 'warning' | 'danger'
type ApplicationStatus = 'new' | 'approved' | 'rejected'

type CourseItem = {
  id: number
  title: string
  teacher: string
  group: string
  progress: number
  modules: number
  status: 'active' | 'draft' | 'archived'
}

type TestItem = {
  id: number
  title: string
  courseId: number
  subject: string
  group: string
  questions: number
  duration: string
  deadline: string
  status: TestStatus
  createdByRole: UserRole
  score?: number
}

type MailItem = {
  id: number
  to: string
  subject: string
  body: string
  sentAt: string
}

type AlertItem = {
  id: number
  tone: AlertTone
  title: string
  text: string
}

type ResultSubmission = {
  id: number
  entity: 'course' | 'test'
  title: string
  result: string
  sentAt: string
}

type UserApplication = {
  id: number
  name: string
  role: UserRole
  email: string
  note: string
  linkedAccountId?: number
  status: ApplicationStatus
  createdAt: string
}

const mockNow = '08.03.2026 20:00'

const accounts = ref<Account[]>([
  {
    id: 1,
    name: 'Наталья Рощина',
    username: 'admin',
    password: 'admin123',
    role: 'admin',
    status: 'approved',
    department: 'Цифровая платформа',
    email: 'admin@college39.ru',
  },
  {
    id: 2,
    name: 'Альберто Дженуарди',
    username: 'student',
    password: 'student123',
    role: 'student',
    status: 'approved',
    group: 'ИСП24-23',
    email: 'student@college39.ru',
  },
  {
    id: 3,
    name: 'Ольга Савельева',
    username: 'teacher',
    password: 'teacher123',
    role: 'teacher',
    status: 'approved',
    department: 'Кафедра программирования',
    email: 'teacher@college39.ru',
  },
  {
    id: 4,
    name: 'Ирина Логинова',
    username: 'pending.student',
    password: 'student123',
    role: 'student',
    status: 'pending',
    group: 'ИСП24-24',
    email: 'pending@college39.ru',
  },
  {
    id: 5,
    name: 'Кирилл Денисов',
    username: 'blocked.teacher',
    password: 'teacher123',
    role: 'teacher',
    status: 'blocked',
    department: 'Сетевые технологии',
    email: 'blocked@college39.ru',
  },
])

const applications = ref<UserApplication[]>([
  {
    id: 201,
    name: 'Ирина Логинова',
    role: 'student',
    email: 'pending@college39.ru',
    note: 'Заявка на доступ к ИСП24-24 для дистанционного обучения.',
    linkedAccountId: 4,
    status: 'new',
    createdAt: '07.03.2026 15:10',
  },
  {
    id: 202,
    name: 'Антон Кравцов',
    role: 'teacher',
    email: 'a.kravtsov@college39.ru',
    note: 'Запрос роли преподавателя по курсу сетевой безопасности.',
    status: 'new',
    createdAt: '08.03.2026 11:42',
  },
])

const courses = ref<CourseItem[]>([
  { id: 1, title: 'Программирование на TypeScript', teacher: 'Савельева О.И.', group: 'ИСП24-23', progress: 74, modules: 12, status: 'active' },
  { id: 2, title: 'Базы данных и SQL', teacher: 'Карпенко Н.А.', group: 'ИСП24-23', progress: 58, modules: 10, status: 'active' },
  { id: 3, title: 'Компьютерные сети', teacher: 'Громов К.А.', group: 'ИСП24-22', progress: 40, modules: 11, status: 'active' },
])

const tests = ref<TestItem[]>([
  {
    id: 1,
    title: 'Основы алгоритмизации: ветвления и циклы',
    courseId: 1,
    subject: 'Программирование',
    group: 'ИСП24-23',
    questions: 18,
    duration: '35 мин',
    deadline: '10.03.2026 21:00',
    status: 'new',
    createdByRole: 'teacher',
  },
  {
    id: 2,
    title: 'Сетевые протоколы и модели OSI',
    courseId: 3,
    subject: 'Компьютерные сети',
    group: 'ИСП24-23',
    questions: 25,
    duration: '45 мин',
    deadline: '12.03.2026 23:59',
    status: 'in-progress',
    createdByRole: 'teacher',
  },
  {
    id: 3,
    title: 'Базы данных: SQL JOIN',
    courseId: 2,
    subject: 'Базы данных',
    group: 'ИСП24-23',
    questions: 20,
    duration: '40 мин',
    deadline: 'Пройдено',
    status: 'done',
    createdByRole: 'teacher',
    score: 94,
  },
])

const grades = [
  { subject: 'Программирование', teacher: 'Савельева О.И.', current: 5, attendance: '96%', nextControl: 'Лабораторная №5' },
  { subject: 'Базы данных', teacher: 'Карпенко Н.А.', current: 4, attendance: '92%', nextControl: 'SQL-контрольная' },
  { subject: 'Компьютерные сети', teacher: 'Громов К.А.', current: 4, attendance: '88%', nextControl: 'Тест по протоколам' },
]

const schedule = [
  {
    day: 'Понедельник',
    date: '09.03.2026',
    lessons: [
      { time: '08:30-10:00', subject: 'Программирование на TypeScript', room: 'A-304', teacher: 'Савельева О.И.' },
      { time: '10:15-11:45', subject: 'Базы данных', room: 'A-211', teacher: 'Карпенко Н.А.' },
      { time: '12:00-13:30', subject: 'Компьютерные сети', room: 'A-118', teacher: 'Громов К.А.' },
    ],
  },
  {
    day: 'Вторник',
    date: '10.03.2026',
    lessons: [
      { time: '08:30-10:00', subject: 'Операционные системы', room: 'A-302', teacher: 'Кузнецов Д.С.' },
      { time: '10:15-11:45', subject: 'Английский для IT', room: 'C-215', teacher: 'Романова М.В.' },
      { time: '12:00-13:30', subject: 'Проектная лаборатория', room: 'Coworking 2', teacher: 'Петрова А.Р.' },
    ],
  },
]

const events = [
  {
    date: '11.03.2026',
    title: 'Хакатон College39: EdTech Sprint',
    place: 'IT-центр колледжа',
    format: 'Очно',
    description: 'Командный марафон по разработке сервисов для учебного процесса.',
  },
  {
    date: '13.03.2026',
    title: 'День открытых лабораторий БПЛА',
    place: 'Корпус №2, ангар',
    format: 'Очно',
    description: 'Демонстрация полетов, разбор сборки дронов и карьерный трек по БПЛА.',
  },
]

const resources = [
  { title: 'Электронная библиотека College39', type: 'Портал', access: '24/7' },
  { title: 'Тренажер SQL и аналитики', type: 'Практикум', access: 'По аккаунту LMS' },
  { title: 'База видеолекций', type: 'Медиатека', access: 'Расписание + архив' },
]

const navByRole: Record<UserRole, NavItem[]> = {
  student: [
    { id: 'home', label: 'Главная' },
    { id: 'courses', label: 'Курсы' },
    { id: 'tests', label: 'Тесты' },
    { id: 'schedule', label: 'Расписание' },
    { id: 'grades', label: 'Успеваемость' },
    { id: 'events', label: 'Мероприятия' },
    { id: 'resources', label: 'Ресурсы' },
    { id: 'mail', label: 'Отправить письмо' },
    { id: 'profile', label: 'Мой аккаунт' },
  ],
  teacher: [
    { id: 'home', label: 'Главная' },
    { id: 'courses', label: 'Курсы' },
    { id: 'tests', label: 'Тесты' },
    { id: 'builder', label: 'Создание' },
    { id: 'schedule', label: 'Расписание' },
    { id: 'events', label: 'Мероприятия' },
    { id: 'resources', label: 'Ресурсы' },
    { id: 'mail', label: 'Отправить письмо' },
    { id: 'profile', label: 'Мой аккаунт' },
  ],
  admin: [
    { id: 'home', label: 'Панель' },
    { id: 'courses', label: 'Курсы' },
    { id: 'tests', label: 'Тесты' },
    { id: 'builder', label: 'Создание' },
    { id: 'applications', label: 'Заявки' },
    { id: 'accounts', label: 'Аккаунты' },
    { id: 'events', label: 'События' },
    { id: 'resources', label: 'Ресурсы' },
    { id: 'mail', label: 'Отправить письмо' },
    { id: 'profile', label: 'Мой аккаунт' },
  ],
}

const activePage = ref<PageId>('home')
const loginError = ref('')
const currentUser = ref<Account | null>(null)
const alerts = ref<AlertItem[]>([])
const submissions = ref<ResultSubmission[]>([])

const testFilter = ref<'all' | TestStatus>('all')
const selectedTest = ref<TestItem | null>(null)
const showTestPopup = ref(false)

const accountActionDialog = ref<{ show: boolean; accountId: number; status: AccountStatus }>({ show: false, accountId: 0, status: 'approved' })
const applicationDecisionDialog = ref<{ show: boolean; applicationId: number; status: ApplicationStatus }>({
  show: false,
  applicationId: 0,
  status: 'approved',
})
const publishDialog = ref(false)

const builderCourseTitle = ref('')
const builderTeacher = ref('')
const builderGroup = ref('ИСП24-23')
const builderModules = ref('8')

const builderTestTitle = ref('')
const builderTestCourse = ref('1')
const builderQuestions = ref('15')
const builderDuration = ref('30 мин')
const builderDeadline = ref('20.03.2026 20:00')

const mailTo = ref('methodist@college39.ru')
const mailSubject = ref('')
const mailBody = ref('')
const sentMail = ref<MailItem[]>([])

const profileEmail = ref('')
const profilePhone = ref('+7 (900) 000-00-00')
const profileCity = ref('Калининград')

const activeCourseId = ref<number | null>(null)
const courseCompletedModules = ref('1')
const courseComment = ref('')

const activeTestId = ref<number | null>(null)
const testCorrectAnswers = ref('0')
const testComment = ref('')

const roleLabel: Record<UserRole, string> = {
  admin: 'Администратор',
  student: 'Студент',
  teacher: 'Преподаватель',
}

const accountStatusLabel: Record<AccountStatus, string> = {
  approved: 'Одобрен',
  pending: 'Ожидает одобрения',
  blocked: 'Заблокирован',
}

const accountStatusTone: Record<AccountStatus, 'approved' | 'pending' | 'blocked'> = {
  approved: 'approved',
  pending: 'pending',
  blocked: 'blocked',
}

const applicationStatusLabel: Record<ApplicationStatus, string> = {
  new: 'Новая',
  approved: 'Одобрена',
  rejected: 'Отклонена',
}

const applicationStatusTone: Record<ApplicationStatus, 'pending' | 'approved' | 'blocked'> = {
  new: 'pending',
  approved: 'approved',
  rejected: 'blocked',
}

const testStatusLabel: Record<TestStatus, string> = {
  new: 'Новый',
  'in-progress': 'В процессе',
  done: 'Завершен',
}

const testStatusTone: Record<TestStatus, 'new' | 'progress' | 'done'> = {
  new: 'new',
  'in-progress': 'progress',
  done: 'done',
}

const courseStatusLabel: Record<CourseItem['status'], string> = {
  active: 'Активный',
  draft: 'Черновик',
  archived: 'Архив',
}

const navItems = computed(() => (currentUser.value ? navByRole[currentUser.value.role] : []))

const accountStats = computed(() => {
  const stats = { approved: 0, pending: 0, blocked: 0 }

  for (const account of accounts.value) {
    stats[account.status] += 1
  }

  return stats
})

const coursesByRole = computed(() => {
  if (!currentUser.value) {
    return []
  }

  if (currentUser.value.role === 'student') {
    return courses.value.filter((course) => course.group === currentUser.value?.group)
  }

  return courses.value
})

const visibleTests = computed(() => {
  if (!currentUser.value) {
    return []
  }

  const byRole = currentUser.value.role === 'student' ? tests.value.filter((item) => item.group === currentUser.value?.group) : tests.value

  if (testFilter.value === 'all') {
    return byRole
  }

  return byRole.filter((item) => item.status === testFilter.value)
})

const activeCourse = computed(() => courses.value.find((course) => course.id === activeCourseId.value) || null)
const activeTest = computed(() => tests.value.find((test) => test.id === activeTestId.value) || null)

const courseRunnerOptions = computed(() => {
  if (!activeCourse.value) {
    return [{ value: '0', label: '0 модулей' }]
  }

  return Array.from({ length: activeCourse.value.modules }, (_, index) => {
    const value = String(index + 1)
    return { value, label: `${value} модулей` }
  })
})

const courseOptions = computed(() =>
  courses.value.map((course) => ({
    value: String(course.id),
    label: course.title,
  })),
)

const addAlert = (tone: AlertTone, title: string, text: string) => {
  const id = Date.now() + Math.floor(Math.random() * 1000)
  alerts.value.unshift({ id, tone, title, text })
}

const removeAlert = (id: number) => {
  alerts.value = alerts.value.filter((item) => item.id !== id)
}

const handleLogin = (credentials: { username: string; password: string }) => {
  loginError.value = ''

  const account = accounts.value.find((item) => item.username === credentials.username)

  if (!account || account.password !== credentials.password) {
    loginError.value = 'Неверный логин или пароль.'
    return
  }

  if (account.status === 'pending') {
    loginError.value = 'Ваш аккаунт еще не одобрен администратором.'
    return
  }

  if (account.status === 'blocked') {
    loginError.value = 'Аккаунт заблокирован. Обратитесь к администратору.'
    return
  }

  currentUser.value = account
  profileEmail.value = account.email || ''
  activePage.value = 'home'
  addAlert('success', 'Авторизация', `Вход выполнен: ${account.name}`)
}

const logout = () => {
  currentUser.value = null
  loginError.value = ''
  activePage.value = 'home'
  alerts.value = []
}

const setPage = (page: PageId) => {
  activePage.value = page
}

const askAccountStatus = (accountId: number, status: AccountStatus) => {
  accountActionDialog.value = { show: true, accountId, status }
}

const confirmAccountStatus = () => {
  const { accountId, status } = accountActionDialog.value
  const account = accounts.value.find((item) => item.id === accountId)

  accountActionDialog.value.show = false

  if (!account || !currentUser.value || account.id === currentUser.value.id) {
    return
  }

  account.status = status
  addAlert('success', 'Статус обновлен', `${account.name}: ${accountStatusLabel[status]}`)
}

const askApplicationDecision = (applicationId: number, status: ApplicationStatus) => {
  applicationDecisionDialog.value = {
    show: true,
    applicationId,
    status,
  }
}

const confirmApplicationDecision = () => {
  const { applicationId, status } = applicationDecisionDialog.value
  const application = applications.value.find((item) => item.id === applicationId)
  applicationDecisionDialog.value.show = false

  if (!application || application.status !== 'new') {
    return
  }

  application.status = status

  if (application.linkedAccountId) {
    const account = accounts.value.find((item) => item.id === application.linkedAccountId)

    if (account) {
      account.status = status === 'approved' ? 'approved' : 'blocked'
    }
  }

  addAlert(
    status === 'approved' ? 'success' : 'warning',
    'Заявка обработана',
    `${application.name}: ${applicationStatusLabel[status]}`,
  )
}

const openTestPopup = (test: TestItem) => {
  selectedTest.value = test
  showTestPopup.value = true
}

const createCourse = () => {
  if (!builderCourseTitle.value.trim() || !builderTeacher.value.trim() || !builderGroup.value.trim()) {
    addAlert('warning', 'Курс не создан', 'Заполните название, преподавателя и группу.')
    return
  }

  const modules = Number(builderModules.value)

  courses.value.unshift({
    id: Date.now(),
    title: builderCourseTitle.value.trim(),
    teacher: builderTeacher.value.trim(),
    group: builderGroup.value.trim(),
    progress: 0,
    modules: Number.isFinite(modules) && modules > 0 ? modules : 8,
    status: 'draft',
  })

  builderCourseTitle.value = ''
  builderTeacher.value = ''
  builderGroup.value = 'ИСП24-23'
  builderModules.value = '8'

  addAlert('success', 'Курс создан', 'Новый курс добавлен в статусе черновика.')
}

const askPublishTest = () => {
  publishDialog.value = true
}

const publishTest = () => {
  publishDialog.value = false

  if (!builderTestTitle.value.trim()) {
    addAlert('warning', 'Тест не создан', 'Укажите название теста.')
    return
  }

  const courseId = Number(builderTestCourse.value)
  const questions = Number(builderQuestions.value)

  const course = courses.value.find((item) => item.id === courseId)
  const group = course?.group || 'ИСП24-23'
  const subject = course?.title || 'Общий курс'

  tests.value.unshift({
    id: Date.now(),
    title: builderTestTitle.value.trim(),
    courseId,
    subject,
    group,
    questions: Number.isFinite(questions) && questions > 0 ? questions : 10,
    duration: builderDuration.value.trim() || '30 мин',
    deadline: builderDeadline.value.trim() || '20.03.2026 20:00',
    status: 'new',
    createdByRole: currentUser.value?.role || 'teacher',
  })

  builderTestTitle.value = ''
  builderQuestions.value = '15'
  builderDuration.value = '30 мин'
  builderDeadline.value = '20.03.2026 20:00'

  addAlert('success', 'Тест опубликован', 'Новый тест добавлен в систему.')
}

const startCourse = (courseId: number) => {
  activeCourseId.value = courseId
  courseCompletedModules.value = '1'
  courseComment.value = ''
}

const submitCourseResult = () => {
  if (!activeCourse.value) {
    return
  }

  const completedModules = Number(courseCompletedModules.value)
  const normalized = Number.isFinite(completedModules) && completedModules > 0 ? completedModules : 1
  const progress = Math.min(100, Math.round((normalized / activeCourse.value.modules) * 100))

  activeCourse.value.progress = progress

  submissions.value.unshift({
    id: Date.now(),
    entity: 'course',
    title: activeCourse.value.title,
    result: `Пройдено модулей: ${normalized}/${activeCourse.value.modules}, прогресс: ${progress}%`,
    sentAt: `${mockNow} · mock`,
  })

  addAlert('success', 'Результат курса отправлен', 'Отправка выполнена во внешний сервис (mock, без сохранения).')
}

const startTest = (testId: number) => {
  activeTestId.value = testId
  testCorrectAnswers.value = '0'
  testComment.value = ''

  const test = tests.value.find((item) => item.id === testId)
  if (test && test.status === 'new') {
    test.status = 'in-progress'
  }
}

const submitTestResult = () => {
  if (!activeTest.value) {
    return
  }

  const correct = Number(testCorrectAnswers.value)
  const safeCorrect = Number.isFinite(correct) && correct >= 0 ? correct : 0
  const bounded = Math.min(activeTest.value.questions, safeCorrect)
  const score = Math.round((bounded / activeTest.value.questions) * 100)

  activeTest.value.status = 'done'
  activeTest.value.score = score
  activeTest.value.deadline = `Отправлено ${mockNow}`

  submissions.value.unshift({
    id: Date.now(),
    entity: 'test',
    title: activeTest.value.title,
    result: `Верных ответов: ${bounded}/${activeTest.value.questions}, оценка: ${score}/100`,
    sentAt: `${mockNow} · mock`,
  })

  addAlert('success', 'Результат теста отправлен', 'Отправка выполнена во внешний сервис (mock, без сохранения).')
}

const sendMail = () => {
  if (!mailTo.value.trim() || !mailSubject.value.trim() || !mailBody.value.trim()) {
    addAlert('warning', 'Письмо не отправлено', 'Заполните получателя, тему и текст письма.')
    return
  }

  sentMail.value.unshift({
    id: Date.now(),
    to: mailTo.value.trim(),
    subject: mailSubject.value.trim(),
    body: mailBody.value.trim(),
    sentAt: mockNow,
  })

  mailSubject.value = ''
  mailBody.value = ''

  addAlert('success', 'Письмо отправлено', `Получатель: ${mailTo.value.trim()}`)
}

const saveProfile = () => {
  if (!currentUser.value) {
    return
  }

  const account = accounts.value.find((item) => item.id === currentUser.value?.id)
  if (account) {
    account.email = profileEmail.value.trim()
  }

  addAlert('info', 'Профиль обновлен', 'Данные аккаунта сохранены локально.')
}

watch(navItems, (items) => {
  if (!items.length) {
    return
  }

  if (!items.some((item) => item.id === activePage.value)) {
    const firstItem = items[0]
    if (firstItem) {
      activePage.value = firstItem.id
    }
  }
})
</script>

<template>
  <LoginPage v-if="!currentUser" :error="loginError" :demo-accounts="accounts" @login="handleLogin" />

  <div v-else class="app-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">College39 LMS</p>
        <h1>Рабочее пространство: {{ roleLabel[currentUser.role] }}</h1>
      </div>
      <div class="user-chip">
        <p class="user-role">{{ roleLabel[currentUser.role] }}</p>
        <strong>{{ currentUser.name }}</strong>
        <span>{{ currentUser.group || currentUser.department }}</span>
        <UiButton variant="ghost" @click="logout">Выйти</UiButton>
      </div>
    </header>

    <section v-if="alerts.length" class="alerts-stack">
      <div v-for="alert in alerts" :key="alert.id" class="alert-row">
        <UiAlert :tone="alert.tone" :title="alert.title">{{ alert.text }}</UiAlert>
        <UiButton class="icon-btn" variant="ghost" @click="removeAlert(alert.id)">✕</UiButton>
      </div>
    </section>

    <UiTabs :items="navItems" :active="activePage" @change="setPage" />

    <main class="page stack">
      <section v-if="activePage === 'home'" class="stack">
        <article class="hero">
          <div>
            <p class="eyebrow">Главная</p>
            <h2>Единая LMS-платформа колледжа</h2>
            <p>Управляйте курсами, тестами, коммуникацией и доступом к аккаунтам из одного интерфейса.</p>
          </div>
          <div class="hero-stats">
            <div class="stat-box">{{ accountStats.approved }} активных аккаунтов</div>
            <div class="stat-box">{{ courses.length }} курсов в системе</div>
            <div class="stat-box">{{ tests.length }} тестов доступно</div>
          </div>
        </article>
      </section>

      <section v-else-if="activePage === 'courses'" class="stack">
        <UiPanel title="Курсы" subtitle="Каталог курсов и прохождение с отправкой результата">
          <div class="grid resources-grid">
            <div v-for="course in coursesByRole" :key="course.id" class="resource-card">
              <p class="resource-type">{{ courseStatusLabel[course.status] }}</p>
              <h4>{{ course.title }}</h4>
              <p>Преподаватель: {{ course.teacher }}</p>
              <p>Группа: {{ course.group }}</p>
              <p>Модулей: {{ course.modules }}</p>
              <p>Прогресс: {{ course.progress }}%</p>
              <UiButton v-if="currentUser.role === 'student'" variant="ghost" @click="startCourse(course.id)">
                {{ course.progress > 0 ? 'Продолжить' : 'Начать' }}
              </UiButton>
              <UiButton v-else variant="ghost">Открыть курс</UiButton>
            </div>
          </div>

          <div v-if="currentUser.role === 'student' && activeCourse" class="runner-grid">
            <div class="info-card">
              <h4>Прохождение курса: {{ activeCourse.title }}</h4>
              <div class="form-grid">
                <UiDropbox v-model="courseCompletedModules" label="Сколько модулей пройдено" :options="courseRunnerOptions" />
                <UiField v-model="courseComment" label="Комментарий" placeholder="Что получилось / что сложно" />
                <UiButton @click="submitCourseResult">Отправить результат</UiButton>
              </div>
            </div>
          </div>
        </UiPanel>
      </section>

      <section v-else-if="activePage === 'tests'" class="stack">
        <UiPanel title="Тесты" subtitle="Прохождение тестов с отправкой результата">
          <div class="tests-tools">
            <UiDropbox
              v-model="testFilter"
              label="Фильтр по статусу"
              :options="[
                { value: 'all', label: 'Все' },
                { value: 'new', label: 'Новые' },
                { value: 'in-progress', label: 'В процессе' },
                { value: 'done', label: 'Завершенные' },
              ]"
            />
          </div>
          <div class="grid test-grid">
            <div v-for="test in visibleTests" :key="test.id" class="test-card">
              <div class="test-top">
                <h4>{{ test.title }}</h4>
                <UiStatusPill :tone="testStatusTone[test.status]">{{ testStatusLabel[test.status] }}</UiStatusPill>
              </div>
              <p>{{ test.subject }} · {{ test.group }}</p>
              <p>Вопросов: {{ test.questions }} · {{ test.duration }}</p>
              <p>Срок: {{ test.deadline }}</p>
              <p v-if="test.score !== undefined" class="score">Результат: {{ test.score }} / 100</p>
              <div class="actions-row">
                <UiButton @click="openTestPopup(test)">Детали</UiButton>
                <UiButton v-if="currentUser.role === 'student'" variant="ghost" @click="startTest(test.id)">Пройти</UiButton>
                <UiButton v-else variant="ghost">Редактировать</UiButton>
              </div>
            </div>
          </div>

          <div v-if="currentUser.role === 'student' && activeTest" class="runner-grid">
            <div class="info-card">
              <h4>Прохождение теста: {{ activeTest.title }}</h4>
              <div class="form-grid">
                <UiField
                  v-model="testCorrectAnswers"
                  label="Сколько верных ответов"
                  :placeholder="`0-${activeTest.questions}`"
                />
                <UiField v-model="testComment" label="Комментарий" placeholder="Замечания по тесту" />
                <UiButton @click="submitTestResult">Отправить результат</UiButton>
              </div>
            </div>
          </div>
        </UiPanel>
      </section>

      <section v-else-if="activePage === 'builder'" class="stack">
        <UiPanel title="Создание курсов и тестов" subtitle="Доступно администратору и преподавателю">
          <div class="builder-grid">
            <div class="info-card">
              <h4>Создать курс</h4>
              <div class="form-grid">
                <UiField v-model="builderCourseTitle" label="Название курса" placeholder="Например: Веб-разработка 1" />
                <UiField v-model="builderTeacher" label="Преподаватель" placeholder="ФИО" />
                <UiField v-model="builderGroup" label="Группа" placeholder="ИСП24-23" />
                <UiField v-model="builderModules" label="Количество модулей" placeholder="8" />
                <UiButton @click="createCourse">Создать курс</UiButton>
              </div>
            </div>
            <div class="info-card">
              <h4>Создать тест</h4>
              <div class="form-grid">
                <UiField v-model="builderTestTitle" label="Название теста" placeholder="Тема теста" />
                <UiDropbox v-model="builderTestCourse" label="Курс" :options="courseOptions" />
                <UiField v-model="builderQuestions" label="Количество вопросов" placeholder="15" />
                <UiField v-model="builderDuration" label="Длительность" placeholder="30 мин" />
                <UiField v-model="builderDeadline" label="Дедлайн" placeholder="20.03.2026 20:00" />
                <UiButton @click="askPublishTest">Опубликовать тест</UiButton>
              </div>
            </div>
          </div>
        </UiPanel>
      </section>

      <section v-else-if="activePage === 'applications'" class="stack">
        <UiPanel title="Заявки пользователей" subtitle="Одобрение или отклонение доступа">
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Пользователь</th>
                  <th>Роль</th>
                  <th>Email</th>
                  <th>Описание</th>
                  <th>Статус</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="application in applications" :key="application.id">
                  <td>{{ application.name }}</td>
                  <td>{{ roleLabel[application.role] }}</td>
                  <td>{{ application.email }}</td>
                  <td>{{ application.note }}</td>
                  <td>
                    <UiStatusPill :tone="applicationStatusTone[application.status]">
                      {{ applicationStatusLabel[application.status] }}
                    </UiStatusPill>
                  </td>
                  <td>
                    <div class="actions-row">
                      <UiButton
                        variant="success"
                        :disabled="application.status !== 'new'"
                        @click="askApplicationDecision(application.id, 'approved')"
                      >
                        Одобрить
                      </UiButton>
                      <UiButton
                        variant="danger"
                        :disabled="application.status !== 'new'"
                        @click="askApplicationDecision(application.id, 'rejected')"
                      >
                        Отклонить
                      </UiButton>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </UiPanel>
      </section>

      <section v-else-if="activePage === 'accounts'" class="stack">
        <UiPanel title="Аккаунты" subtitle="Одобрение и блокировка пользователей администратором">
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Пользователь</th>
                  <th>Роль</th>
                  <th>Логин</th>
                  <th>Статус</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="account in accounts" :key="account.id">
                  <td>{{ account.name }}</td>
                  <td>{{ roleLabel[account.role] }}</td>
                  <td>{{ account.username }}</td>
                  <td>
                    <UiStatusPill :tone="accountStatusTone[account.status]">{{ accountStatusLabel[account.status] }}</UiStatusPill>
                  </td>
                  <td>
                    <div class="actions-row">
                      <UiButton
                        variant="success"
                        :disabled="account.status === 'approved' || account.id === currentUser.id"
                        @click="askAccountStatus(account.id, 'approved')"
                      >
                        Одобрить
                      </UiButton>
                      <UiButton
                        variant="danger"
                        :disabled="account.status === 'blocked' || account.id === currentUser.id"
                        @click="askAccountStatus(account.id, 'blocked')"
                      >
                        Блокировать
                      </UiButton>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </UiPanel>
      </section>

      <section v-else-if="activePage === 'schedule'" class="stack">
        <UiPanel title="Расписание" subtitle="Учебная неделя">
          <div class="schedule-grid">
            <div v-for="day in schedule" :key="day.day" class="schedule-day">
              <h4>{{ day.day }}</h4>
              <p class="schedule-date">{{ day.date }}</p>
              <div class="lesson-list">
                <div v-for="lesson in day.lessons" :key="lesson.time + lesson.subject" class="lesson">
                  <p class="lesson-time">{{ lesson.time }}</p>
                  <p class="lesson-subject">{{ lesson.subject }}</p>
                  <p>{{ lesson.room }} · {{ lesson.teacher }}</p>
                </div>
              </div>
            </div>
          </div>
        </UiPanel>
      </section>

      <section v-else-if="activePage === 'grades'" class="stack">
        <UiPanel title="Успеваемость" subtitle="Оценки и контрольные точки">
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Дисциплина</th>
                  <th>Преподаватель</th>
                  <th>Оценка</th>
                  <th>Посещаемость</th>
                  <th>Следующий контроль</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in grades" :key="item.subject">
                  <td>{{ item.subject }}</td>
                  <td>{{ item.teacher }}</td>
                  <td>{{ item.current }}</td>
                  <td>{{ item.attendance }}</td>
                  <td>{{ item.nextControl }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </UiPanel>
      </section>

      <section v-else-if="activePage === 'events'" class="stack">
        <UiPanel title="Мероприятия" subtitle="Календарь колледжа">
          <div class="grid event-grid">
            <div v-for="event in events" :key="event.title" class="event-card">
              <p class="event-date">{{ event.date }}</p>
              <h4>{{ event.title }}</h4>
              <p>{{ event.description }}</p>
              <p class="event-meta">{{ event.place }} · {{ event.format }}</p>
              <UiButton variant="ghost">Подробнее</UiButton>
            </div>
          </div>
        </UiPanel>
      </section>

      <section v-else-if="activePage === 'resources'" class="stack">
        <UiPanel title="Ресурсы" subtitle="Учебные сервисы и базы знаний">
          <div class="grid resources-grid">
            <div v-for="resource in resources" :key="resource.title" class="resource-card">
              <p class="resource-type">{{ resource.type }}</p>
              <h4>{{ resource.title }}</h4>
              <p>Доступ: {{ resource.access }}</p>
              <UiButton variant="ghost">Открыть</UiButton>
            </div>
          </div>
        </UiPanel>
      </section>

      <section v-else-if="activePage === 'mail'" class="stack">
        <UiPanel title="Отправить письмо" subtitle="Внутренняя почта LMS">
          <div class="builder-grid">
            <div class="info-card">
              <h4>Новое письмо</h4>
              <div class="form-grid">
                <UiField v-model="mailTo" label="Кому" placeholder="recipient@college39.ru" />
                <UiField v-model="mailSubject" label="Тема" placeholder="Тема письма" />
                <label class="ui-field">
                  <span>Сообщение</span>
                  <textarea v-model="mailBody" rows="6" placeholder="Текст письма" />
                </label>
                <UiButton @click="sendMail">Отправить</UiButton>
              </div>
            </div>
            <div class="info-card">
              <h4>Последние отправленные</h4>
              <div class="feed-list">
                <div v-for="mail in sentMail" :key="mail.id" class="feed-item">
                  <p><strong>{{ mail.subject }}</strong></p>
                  <p>Кому: {{ mail.to }}</p>
                  <p>{{ mail.body }}</p>
                  <p class="schedule-date">{{ mail.sentAt }}</p>
                </div>
                <p v-if="!sentMail.length" class="schedule-date">Пока нет отправленных писем.</p>
              </div>
            </div>
          </div>
        </UiPanel>
      </section>

      <section v-else class="stack">
        <UiPanel title="Мой аккаунт" subtitle="Профиль и отправленные результаты">
          <div class="builder-grid">
            <div class="info-card">
              <h4>Профиль</h4>
              <div class="profile-kv">
                <p><strong>ФИО:</strong> {{ currentUser.name }}</p>
                <p><strong>Роль:</strong> {{ roleLabel[currentUser.role] }}</p>
                <p><strong>Логин:</strong> {{ currentUser.username }}</p>
                <p><strong>Статус:</strong> {{ accountStatusLabel[currentUser.status] }}</p>
              </div>
            </div>
            <div class="info-card">
              <h4>Контакты</h4>
              <div class="form-grid">
                <UiField v-model="profileEmail" label="Email" placeholder="email@college39.ru" />
                <UiField v-model="profilePhone" label="Телефон" placeholder="+7" />
                <UiField v-model="profileCity" label="Город" placeholder="Калининград" />
                <UiButton @click="saveProfile">Сохранить</UiButton>
              </div>
            </div>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Тип</th>
                  <th>Название</th>
                  <th>Результат</th>
                  <th>Статус отправки</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in submissions" :key="item.id">
                  <td>{{ item.entity === 'course' ? 'Курс' : 'Тест' }}</td>
                  <td>{{ item.title }}</td>
                  <td>{{ item.result }}</td>
                  <td>{{ item.sentAt }}</td>
                </tr>
                <tr v-if="!submissions.length">
                  <td colspan="4">Пока нет отправленных результатов.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </UiPanel>
      </section>
    </main>

    <UiPopup v-if="selectedTest" :show="showTestPopup" title="Детали теста" @close="showTestPopup = false">
      <p><strong>{{ selectedTest.title }}</strong></p>
      <p>Курс: {{ selectedTest.subject }}</p>
      <p>Группа: {{ selectedTest.group }}</p>
      <p>Вопросов: {{ selectedTest.questions }}</p>
      <p>Длительность: {{ selectedTest.duration }}</p>
      <p>Срок: {{ selectedTest.deadline }}</p>
      <p>Создано ролью: {{ roleLabel[selectedTest.createdByRole] }}</p>
    </UiPopup>

    <UiDialog
      :show="accountActionDialog.show"
      title="Подтвердите изменение статуса"
      text="Изменение статуса повлияет на возможность входа пользователя в LMS."
      confirm-label="Применить"
      cancel-label="Отмена"
      @cancel="accountActionDialog.show = false"
      @confirm="confirmAccountStatus"
    />

    <UiDialog
      :show="applicationDecisionDialog.show"
      title="Подтвердите решение по заявке"
      text="После обработки заявка перейдет в финальный статус."
      confirm-label="Подтвердить"
      cancel-label="Отмена"
      @cancel="applicationDecisionDialog.show = false"
      @confirm="confirmApplicationDecision"
    />

    <UiDialog
      :show="publishDialog"
      title="Публикация теста"
      text="После публикации тест появится на странице тестов и станет доступен по роли."
      confirm-label="Опубликовать"
      cancel-label="Отмена"
      @cancel="publishDialog = false"
      @confirm="publishTest"
    />
  </div>
</template>
