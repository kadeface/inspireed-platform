import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '../types/user'

function safeParseUser(raw: string | null): User | null {
  if (!raw) return null
  try {
    return JSON.parse(raw) as User
  } catch {
    localStorage.removeItem('user')
    return null
  }
}

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(safeParseUser(localStorage.getItem('user')))
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const isAuthenticated = ref(!!token.value)

  function setUser(userData: User) {
    user.value = userData
    // 保存用户信息到 localStorage
    localStorage.setItem('user', JSON.stringify(userData))
  }

  function setToken(accessToken: string) {
    token.value = accessToken
    localStorage.setItem('access_token', accessToken)
    isAuthenticated.value = true
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    sessionStorage.removeItem('access_token')
    isAuthenticated.value = false
  }

  return {
    user,
    token,
    isAuthenticated,
    setUser,
    setToken,
    logout,
  }
})

