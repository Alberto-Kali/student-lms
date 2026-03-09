export type UserRole = 'admin' | 'student' | 'teacher'

export type AccountStatus = 'approved' | 'pending' | 'blocked'

export type PageId =
  | 'home'
  | 'courses'
  | 'tests'
  | 'builder'
  | 'applications'
  | 'accounts'
  | 'schedule'
  | 'events'
  | 'grades'
  | 'resources'
  | 'mail'
  | 'profile'

export type NavItem = {
  id: PageId
  label: string
}

export type Account = {
  id: number
  name: string
  username: string
  password: string
  role: UserRole
  status: AccountStatus
  group?: string
  department?: string
  email?: string
}
