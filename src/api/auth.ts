import { apiRequest, clearAccessToken, getAccessToken, setAccessToken } from './client'
import type { AuthSession, DemoAccount, UserProfile } from '../types/lms'

export async function fetchDemoAccounts() {
  return apiRequest<DemoAccount[]>('/auth/demo-accounts', {}, false)
}

export async function login(username: string, password: string) {
  const session = await apiRequest<AuthSession>(
    '/auth/login',
    {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    },
    false,
  )
  setAccessToken(session.access_token)
  return session
}

export async function fetchCurrentUser() {
  return apiRequest<UserProfile>('/auth/me')
}

export async function logout() {
  if (getAccessToken()) {
    await apiRequest('/auth/logout', { method: 'POST' })
  }
  clearAccessToken()
}
