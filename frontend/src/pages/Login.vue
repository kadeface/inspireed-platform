<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          InspireEd 教师教研系统
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          {{ isLogin ? '登录到您的账户' : '创建新账户' }}
        </p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="rounded-md shadow-sm -space-y-px">
          <div v-if="!isLogin">
            <input
              v-model="form.email"
              type="email"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
              placeholder="邮箱地址"
            />
          </div>
          
          <div>
            <input
              v-model="form.username"
              type="text"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
              :class="{ 'rounded-t-md': isLogin }"
              placeholder="用户名"
            />
          </div>
          
          <div>
            <input
              v-model="form.password"
              type="password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
              placeholder="密码"
            />
          </div>
        </div>

        <div v-if="error" class="text-red-600 text-sm text-center">
          {{ error }}
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            {{ loading ? '处理中...' : (isLogin ? '登录' : '注册') }}
          </button>
        </div>

        <div class="text-center">
          <button
            type="button"
            @click="toggleMode"
            class="text-sm text-primary-600 hover:text-primary-500"
          >
            {{ isLogin ? '还没有账户？立即注册' : '已有账户？立即登录' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { authService } from '../services/auth'
import { UserRole } from '../types/user'

const router = useRouter()
const userStore = useUserStore()

const isLogin = ref(true)
const loading = ref(false)
const error = ref('')

const form = ref({
  email: '',
  username: '',
  password: '',
})

function toggleMode() {
  isLogin.value = !isLogin.value
  error.value = ''
}

async function handleSubmit() {
  loading.value = true
  error.value = ''

  try {
    if (isLogin.value) {
      // 步骤1: 登录获取token
      console.log('🔐 开始登录...')
      const tokenResponse = await authService.login({
        username: form.value.username,
        password: form.value.password,
      })
      console.log('✅ Token获取成功:', tokenResponse)
      
      userStore.setToken(tokenResponse.access_token)
      
      // 步骤2: 获取用户信息
      console.log('👤 获取用户信息...')
      const user = await authService.getCurrentUser()
      console.log('✅ 用户信息:', user)
      console.log('👤 用户角色:', user.role)
      
      userStore.setUser(user)
      
      // 步骤3: 根据角色跳转
      let targetPath = ''
      if (user.role === UserRole.ADMIN) {
        targetPath = '/admin'
      } else if (user.role === UserRole.TEACHER) {
        targetPath = '/teacher'
      } else if (user.role === UserRole.STUDENT) {
        targetPath = '/student'
      } else if (user.role === UserRole.RESEARCHER) {
        targetPath = '/researcher'
      } else {
        console.error('❌ 未知角色:', user.role)
        error.value = '用户角色配置错误，请联系管理员'
        return
      }
      
      console.log('🚀 准备跳转到:', targetPath)
      await router.push(targetPath)
      console.log('✅ 跳转完成')
    } else {
      await authService.register({
        email: form.value.email,
        username: form.value.username,
        password: form.value.password,
        role: UserRole.STUDENT,
      })
      
      error.value = '注册成功！请登录'
      isLogin.value = true
    }
  } catch (err: any) {
    console.error('❌ 登录失败:', err)
    error.value = err.response?.data?.detail || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

