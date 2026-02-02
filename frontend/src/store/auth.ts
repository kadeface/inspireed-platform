/**
 * Auth Store - 最小实现用于测试
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)

  function setToken(newToken: string) {
    token.value = newToken
  }

  function clearToken() {
    token.value = null
  }

  return {
    token,
    setToken,
    clearToken,
  }
})
