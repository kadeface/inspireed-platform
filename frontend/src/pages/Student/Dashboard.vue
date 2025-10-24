<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">学生工作台</h1>
            <p class="text-sm text-gray-500 mt-1">欢迎回来，{{ currentUser?.username || '学生' }}！</p>
          </div>
          <div class="flex items-center gap-4">
            <button
              @click="router.push('/student/profile')"
              class="px-4 py-2 text-sm text-gray-700 hover:text-gray-900 flex items-center gap-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              个人中心
            </button>
            <button
              @click="handleLogout"
              class="px-4 py-2 text-sm bg-red-500 text-white rounded-lg hover:bg-red-600"
            >
              退出登录
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-blue-500 rounded-md p-3">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">可用课程</p>
              <p class="text-2xl font-semibold text-gray-900">{{ availableLessons.length }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-green-500 rounded-md p-3">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">已完成</p>
              <p class="text-2xl font-semibold text-gray-900">{{ completedCount }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-yellow-500 rounded-md p-3">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">进行中</p>
              <p class="text-2xl font-semibold text-gray-900">{{ inProgressCount }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 筛选和搜索 -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <div class="flex flex-col md:flex-row gap-4">
          <div class="flex-1">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索课程名称..."
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <select
            v-model="filterStatus"
            class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">全部状态</option>
            <option value="not_started">未开始</option>
            <option value="in_progress">进行中</option>
            <option value="completed">已完成</option>
          </select>
          <select
            v-model="filterSubject"
            class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">全部学科</option>
            <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
              {{ subject.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- 课程列表 -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <p class="mt-4 text-gray-600">加载中...</p>
      </div>

      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p class="text-red-600">{{ error }}</p>
        <button
          @click="fetchData"
          class="mt-4 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
        >
          重试
        </button>
      </div>

      <div v-else-if="filteredLessons.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="mt-4 text-lg text-gray-600">暂无课程</p>
        <p class="mt-2 text-sm text-gray-500">请等待老师发布课程</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="lesson in filteredLessons"
          :key="lesson.id"
          class="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
          @click="viewLesson(lesson.id)"
        >
          <!-- 课程封面 -->
          <div class="h-40 bg-gradient-to-br from-blue-500 to-purple-600 rounded-t-lg flex items-center justify-center">
            <svg class="w-16 h-16 text-white opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>

          <!-- 课程信息 -->
          <div class="p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
              {{ lesson.title }}
            </h3>
            <p v-if="lesson.description" class="text-sm text-gray-600 mb-4 line-clamp-2">
              {{ lesson.description }}
            </p>

            <!-- 课程元信息 -->
            <div class="space-y-2 mb-4">
              <div v-if="lesson.course" class="flex items-center text-xs text-gray-500">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                </svg>
                {{ lesson.course.name }}
              </div>
              <div v-if="lesson.chapter" class="flex items-center text-xs text-gray-500">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                {{ lesson.chapter.name }}
              </div>
              <div class="flex items-center text-xs text-gray-500">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ lesson.estimated_duration || 45 }} 分钟
              </div>
            </div>

            <!-- 学习进度 -->
            <div class="mb-4">
              <div class="flex items-center justify-between text-xs text-gray-600 mb-1">
                <span>学习进度</span>
                <span>{{ getLessonProgress(lesson.id) }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-blue-500 h-2 rounded-full transition-all"
                  :style="{ width: `${getLessonProgress(lesson.id)}%` }"
                ></div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <button
              class="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              @click.stop="viewLesson(lesson.id)"
            >
              {{ getLessonProgress(lesson.id) === 0 ? '开始学习' : '继续学习' }}
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { lessonService } from '@/services/lesson'
import { curriculumService } from '@/services/curriculum'
import type { Lesson } from '@/types/lesson'
import type { Subject } from '@/types/curriculum'

const router = useRouter()
const userStore = useUserStore()

// 状态
const loading = ref(false)
const error = ref<string | null>(null)
const availableLessons = ref<Lesson[]>([])
const subjects = ref<Subject[]>([])
const searchQuery = ref('')
const filterStatus = ref('')
const filterSubject = ref('')

// 学习进度数据（从localStorage获取）
const progressData = ref<Record<number, number>>({})

// 计算属性
const currentUser = computed(() => userStore.user)

const filteredLessons = computed(() => {
  let result = availableLessons.value

  // 按搜索词过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(lesson =>
      lesson.title.toLowerCase().includes(query) ||
      lesson.description?.toLowerCase().includes(query)
    )
  }

  // 按学科过滤
  if (filterSubject.value) {
    result = result.filter(lesson => lesson.course?.subject_id === Number(filterSubject.value))
  }

  // 按状态过滤
  if (filterStatus.value) {
    result = result.filter(lesson => {
      const progress = getLessonProgress(lesson.id)
      if (filterStatus.value === 'not_started') return progress === 0
      if (filterStatus.value === 'in_progress') return progress > 0 && progress < 100
      if (filterStatus.value === 'completed') return progress === 100
      return true
    })
  }

  return result
})

const completedCount = computed(() => {
  return availableLessons.value.filter(lesson => getLessonProgress(lesson.id) === 100).length
})

const inProgressCount = computed(() => {
  return availableLessons.value.filter(lesson => {
    const progress = getLessonProgress(lesson.id)
    return progress > 0 && progress < 100
  }).length
})

// 方法
const getLessonProgress = (lessonId: number): number => {
  return progressData.value[lessonId] || 0
}

const loadProgressData = () => {
  const saved = localStorage.getItem('student_lesson_progress')
  if (saved) {
    try {
      progressData.value = JSON.parse(saved)
    } catch (e) {
      console.error('Failed to load progress data:', e)
    }
  }
}

const fetchData = async () => {
  loading.value = true
  error.value = null
  
  try {
    // 获取已发布的课程列表
    const response = await lessonService.fetchLessons({
      status: 'published',
      page: 1,
      page_size: 100
    })
    availableLessons.value = response.items

    // 获取学科列表
    subjects.value = await curriculumService.getSubjects()
    
    // 加载学习进度
    loadProgressData()
  } catch (e: any) {
    error.value = e.message || '加载数据失败'
    console.error('Failed to fetch data:', e)
  } finally {
    loading.value = false
  }
}

const viewLesson = (lessonId: number) => {
  router.push(`/student/lesson/${lessonId}`)
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

// 生命周期
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
