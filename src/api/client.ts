const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'
const TOKEN_KEY = 'student-lms-token'

let accessToken = typeof window !== 'undefined' ? window.localStorage.getItem(TOKEN_KEY) ?? '' : ''

export function getAccessToken() {
  return accessToken
}

export function setAccessToken(token: string) {
  accessToken = token
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(TOKEN_KEY, token)
  }
}

export function clearAccessToken() {
  accessToken = ''
  if (typeof window !== 'undefined') {
    window.localStorage.removeItem(TOKEN_KEY)
  }
}

export async function apiRequest<T>(path: string, init: RequestInit = {}, auth = true): Promise<T> {
  const headers = new Headers(init.headers ?? {})
  if (!headers.has('Content-Type') && init.body) {
    headers.set('Content-Type', 'application/json')
  }
  if (auth && accessToken) {
    headers.set('Authorization', `Bearer ${accessToken}`)
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Request failed with status ${response.status}`)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}
