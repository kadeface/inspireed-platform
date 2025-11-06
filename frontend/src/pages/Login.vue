<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 - PhET 风格 -->
    <header class="bg-white shadow-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
              </svg>
            </div>
            <h1 class="text-2xl md:text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              InspireEd
            </h1>
          </div>
          <button
            v-if="!showLoginForm"
            @click="showLoginForm = true"
            class="px-6 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 font-medium shadow-md hover:shadow-lg transition-all"
          >
            登录
          </button>
          <button
            v-else
            @click="showLoginForm = false"
            class="px-6 py-2 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-all"
          >
            返回
          </button>
        </div>
      </div>
    </header>

    <!-- Hero 区域 - PhET 风格 -->
    <section v-if="!showLoginForm" class="bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 text-white py-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="text-4xl md:text-6xl font-bold mb-6">
          交互式科学与数学学习平台
        </h2>
        <p class="text-xl md:text-2xl mb-4 text-blue-100">
          让学习变得更有趣和高效
        </p>
        <p class="text-lg md:text-xl text-blue-100 mb-12">
          融合 PhET 互动模拟实验，打造高效互动的现代化教学体验
        </p>
        
        <!-- 统计数据 -->
        <div class="flex flex-wrap justify-center gap-12 md:gap-20 mt-16">
          <div class="text-center">
            <div class="text-5xl md:text-6xl font-bold mb-2">100+</div>
            <div class="text-lg md:text-xl text-blue-100">互动课程</div>
          </div>
          <div class="text-center">
            <div class="text-5xl md:text-6xl font-bold mb-2">30+</div>
            <div class="text-lg md:text-xl text-blue-100">PhET 模拟实验</div>
          </div>
          <div class="text-center">
            <div class="text-5xl md:text-6xl font-bold mb-2">10K+</div>
            <div class="text-lg md:text-xl text-blue-100">学习者</div>
          </div>
        </div>
      </div>
    </section>

    <!-- 学科分类 - PhET 风格 -->
    <section v-if="!showLoginForm" class="py-16 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h3 class="text-3xl md:text-4xl font-bold text-gray-900 mb-12 text-center">探索学科</h3>
        
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 md:gap-6">
          <!-- 人工智能 -->
          <div class="group cursor-pointer">
            <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-orange-500 to-orange-600 p-8 text-white shadow-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300">
              <div class="text-center">
                <div class="text-5xl mb-4">🤖</div>
                <h4 class="text-xl font-bold mb-2">人工智能</h4>
                <p class="text-sm text-orange-100">Artificial Intelligence</p>
              </div>
            </div>
          </div>

          <!-- 物理 -->
          <div class="group cursor-pointer">
            <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 p-8 text-white shadow-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300">
              <div class="text-center">
                <div class="text-5xl mb-4">⚛️</div>
                <h4 class="text-xl font-bold mb-2">物理</h4>
                <p class="text-sm text-blue-100">Physics</p>
              </div>
            </div>
          </div>

          <!-- 数学 -->
          <div class="group cursor-pointer">
            <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-green-500 to-green-600 p-8 text-white shadow-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300">
              <div class="text-center">
                <div class="text-5xl mb-4">📐</div>
                <h4 class="text-xl font-bold mb-2">数学</h4>
                <p class="text-sm text-green-100">Math</p>
              </div>
            </div>
          </div>

          <!-- 化学 -->
          <div class="group cursor-pointer">
            <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-purple-500 to-purple-600 p-8 text-white shadow-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300">
              <div class="text-center">
                <div class="text-5xl mb-4">🧪</div>
                <h4 class="text-xl font-bold mb-2">化学</h4>
                <p class="text-sm text-purple-100">Chemistry</p>
              </div>
            </div>
          </div>

          <!-- 生物 -->
          <div class="group cursor-pointer">
            <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-pink-500 to-pink-600 p-8 text-white shadow-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300">
              <div class="text-center">
                <div class="text-5xl mb-4">🧬</div>
                <h4 class="text-xl font-bold mb-2">生物</h4>
                <p class="text-sm text-pink-100">Biology</p>
              </div>
            </div>
          </div>

          <!-- 地球科学 -->
          <div class="group cursor-pointer">
            <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-yellow-500 to-yellow-600 p-8 text-white shadow-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300">
              <div class="text-center">
                <div class="text-5xl mb-4">🌍</div>
                <h4 class="text-xl font-bold mb-2">地球科学</h4>
                <p class="text-sm text-yellow-100">Earth Science</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 特色功能 - PhET 风格 -->
    <section v-if="!showLoginForm" class="py-16 bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h3 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4 text-center">教学资源与社区</h3>
        <p class="text-center text-gray-600 mb-12 text-lg">教师可以访问模拟特定的提示和视频，以及与我们社区共享的活动</p>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- 智能化课程设计 -->
          <div class="bg-white rounded-xl p-8 shadow-md hover:shadow-xl transition-shadow">
            <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mb-6 mx-auto">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
              </svg>
            </div>
            <h4 class="text-xl font-bold text-gray-900 mb-3 text-center">智能化课程设计</h4>
            <p class="text-gray-600 text-center">多种交互式教学组件，支持代码演示、仿真实验、视频教学等多元化内容</p>
          </div>

          <!-- 协作式教研 -->
          <div class="bg-white rounded-xl p-8 shadow-md hover:shadow-xl transition-shadow">
            <div class="w-16 h-16 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl flex items-center justify-center mb-6 mx-auto">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
              </svg>
            </div>
            <h4 class="text-xl font-bold text-gray-900 mb-3 text-center">协作式教研管理</h4>
            <p class="text-gray-600 text-center">教师团队协作备课，课程资源共享，实时同步更新教学内容</p>
          </div>

          <!-- AI 智能助手 -->
          <div class="bg-white rounded-xl p-8 shadow-md hover:shadow-xl transition-shadow">
            <div class="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center mb-6 mx-auto">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
              </svg>
            </div>
            <h4 class="text-xl font-bold text-gray-900 mb-3 text-center">AI 智能问答助手</h4>
            <p class="text-gray-600 text-center">集成智能问答系统，即时解答学生疑问，提升学习效率</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 登录表单区域 -->
    <section v-if="showLoginForm" class="py-16">
      <div class="max-w-md mx-auto px-4">
        <div class="bg-white rounded-2xl shadow-xl p-8">
          <div class="mb-8 text-center">
            <h2 class="text-3xl font-bold text-gray-900 mb-2">
              {{ isLogin ? '欢迎回来' : '创建账户' }}
            </h2>
            <p class="text-gray-600">
              {{ isLogin ? '登录到您的账户继续学习' : '注册新账户开始您的学习之旅' }}
            </p>
          </div>
          
          <form class="space-y-5" @submit.prevent="handleSubmit">
            <!-- 邮箱输入（仅注册时显示） -->
            <div v-if="!isLogin">
              <label class="block text-sm font-medium text-gray-700 mb-2">邮箱地址</label>
              <input
                v-model="form.email"
                type="email"
                required
                class="block w-full px-4 py-3 border border-gray-300 rounded-lg bg-white text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                placeholder="your.email@example.com"
              />
            </div>
            
            <!-- 用户名输入 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">用户名</label>
              <input
                v-model="form.username"
                type="text"
                required
                class="block w-full px-4 py-3 border border-gray-300 rounded-lg bg-white text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                placeholder="请输入用户名"
              />
            </div>
            
            <!-- 密码输入 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">密码</label>
              <input
                v-model="form.password"
                type="password"
                required
                class="block w-full px-4 py-3 border border-gray-300 rounded-lg bg-white text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                placeholder="请输入密码"
              />
            </div>

            <!-- 错误提示 -->
            <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {{ error }}
            </div>

            <!-- 提交按钮 -->
            <button
              type="submit"
              :disabled="loading"
              class="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-lg text-white font-medium bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              <span v-if="loading" class="flex items-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                处理中...
              </span>
              <span v-else>{{ isLogin ? '登录' : '注册' }}</span>
            </button>

            <!-- 切换登录/注册 -->
            <div class="text-center pt-4">
              <button
                type="button"
                @click="toggleMode"
                class="text-sm text-blue-600 hover:text-blue-500 font-medium transition-colors"
              >
                {{ isLogin ? '还没有账户？立即注册' : '已有账户？立即登录' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </section>

    <!-- 底部信息 -->
    <footer class="bg-gray-900 text-white py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          <div>
            <h4 class="text-lg font-bold mb-4">关于 InspireEd</h4>
            <p class="text-gray-400 text-sm">
              打造高效互动的现代化教学体验，让每一位学习者都能享受优质的教育资源。
            </p>
          </div>
          <div>
            <h4 class="text-lg font-bold mb-4">合作伙伴</h4>
            <ul class="space-y-2 text-sm">
              <li><a href="https://phet.colorado.edu" target="_blank" class="text-gray-400 hover:text-white transition-colors">PhET 交互式模拟</a></li>
              <li><span class="text-gray-400">更多教育资源</span></li>
            </ul>
          </div>
          <div>
            <h4 class="text-lg font-bold mb-4">语言</h4>
            <select class="bg-gray-800 text-white px-4 py-2 rounded-lg text-sm border border-gray-700">
              <option>简体中文</option>
              <option>English</option>
            </select>
          </div>
        </div>
        
        <div class="pt-8 border-t border-gray-800 text-center text-sm text-gray-400">
          <p>© 2025 InspireEd. 专注于提供优质的教育科技解决方案</p>
        </div>
      </div>
    </footer>
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

const showLoginForm = ref(false)
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
      // 登录
      const tokenResponse = await authService.login({
        username: form.value.username,
        password: form.value.password,
      })
      
      userStore.setToken(tokenResponse.access_token)
      
      const user = await authService.getCurrentUser()
      userStore.setUser(user)
      
      // 根据角色跳转
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
        error.value = '用户角色配置错误，请联系管理员'
        return
      }
      
      await router.push(targetPath)
    } else {
      // 注册
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
    error.value = err.response?.data?.detail || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>
