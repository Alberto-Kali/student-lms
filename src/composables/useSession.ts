import { computed, ref } from 'vue'
import { fetchCurrentUser, fetchDemoAccounts, login as apiLogin, logout as apiLogout } from '../api/auth'
import { getAccessToken } from '../api/client'
import type { AuthSession, DemoAccount, UserProfile } from '../types/lms'

export function useSession() {
  const user = ref<UserProfile | null>(null)
  const demoAccounts = ref<DemoAccount[]>([])
  const authLoading = ref(false)

  const authenticated = computed(() => Boolean(user.value))

  async function loadDemoAccounts() {
    demoAccounts.value = await fetchDemoAccounts()
  }

  async function restore() {
    if (!getAccessToken()) {
      return
    }
    user.value = await fetchCurrentUser()
  }

  async function login(username: string, password: string) {
    authLoading.value = true
    try {
      const session: AuthSession = await apiLogin(username, password)
      user.value = session.user
      return session
    } finally {
      authLoading.value = false
    }
  }

  async function logout() {
    await apiLogout()
    user.value = null
  }

  return {
    user,
    demoAccounts,
    authLoading,
    authenticated,
    loadDemoAccounts,
    restore,
    login,
    logout,
  }
}
