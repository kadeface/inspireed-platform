import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '../types/user'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const isAuthenticated = ref(!!token.value)

  function setUser(userData: User) {
    user.value = userData
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

