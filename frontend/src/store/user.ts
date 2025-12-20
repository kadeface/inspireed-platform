import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '../types/user'

export const useUserStore = defineStore('user', () => {
  // 尝试从 localStorage 恢复用户信息
  const storedUser = localStorage.getItem('user')
  const user = ref<User | null>(storedUser ? JSON.parse(storedUser) : null)
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

