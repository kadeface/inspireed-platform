<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 统一头部 -->
    <DashboardHeader
      title="学生工作台"
      subtitle="开始您的学习之旅"
      :user-name="userName"
      :show-profile-button="true"
      @profile="router.push('/student/profile')"
      @logout="handleLogout"
    />

    <!-- 主要内容区域 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- PhET 模拟实验横幅 -->
      <div class="mb-8 bg-gradient-to-r from-orange-500 via-pink-500 to-purple-500 rounded-2xl shadow-2xl overflow-hidden">
        <div class="p-8 md:p-10 text-white">
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="flex items-center mb-3">
                <span class="text-4xl mr-3">🔬</span>
                <h2 class="text-3xl font-bold">探索 PhET 互动模拟实验</h2>
              </div>
              <p class="text-lg text-white opacity-90 mb-6 max-w-2xl">
                来自科罗拉多大学的优质教育资源，涵盖物理、化学、生物、数学等多学科的互动学习体验
              </p>
              <button
                @click="router.push('/student/browse')"
                class="px-8 py-3 bg-white text-orange-600 rounded-xl font-bold hover:bg-gray-100 transition-all shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                立即探索 →
              </button>
            </div>
            <div class="hidden lg:block">
              <div class="text-8xl opacity-20">⚛️🧪📐</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 快捷入口 -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <button
          @click="router.push('/student/favorites')"
          class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow text-center"
        >
          <div class="text-3xl mb-2">❤️</div>
          <div class="text-sm font-medium text-gray-900">我的收藏</div>
        </button>
        <button
          @click="router.push('/student/learning-paths')"
          class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow text-center"
        >
          <div class="text-3xl mb-2">🗺️</div>
          <div class="text-sm font-medium text-gray-900">学习路径</div>
        </button>
        <button
          @click="router.push('/student/profile')"
          class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow text-center"
        >
          <div class="text-3xl mb-2">📊</div>
          <div class="text-sm font-medium text-gray-900">学习统计</div>
        </button>
        <button
          @click="showRecommended = !showRecommended"
          class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow text-center"
        >
          <div class="text-3xl mb-2">⭐</div>
          <div class="text-sm font-medium text-gray-900">推荐课程</div>
        </button>
      </div>

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

      <!-- 推荐课程区域 -->
      <div v-if="showRecommended" class="bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg shadow-lg p-6 mb-8">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold text-white flex items-center">
            <span class="mr-2">⭐</span>
            为你推荐
          </h2>
          <button @click="showRecommended = false" class="text-white hover:text-gray-200">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div v-if="loadingRecommended" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
        </div>
        
        <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div
            v-for="lesson in recommendedLessons"
            :key="lesson.id"
            class="bg-white rounded-lg p-4 hover:shadow-xl transition-shadow cursor-pointer"
            @click="viewLesson(lesson.id)"
          >
            <h3 class="font-semibold text-gray-900 mb-2 line-clamp-1">{{ lesson.title }}</h3>
            <div class="flex items-center text-sm text-gray-600 mb-2">
              <span class="mr-2">⭐</span>
              <span>{{ lesson.average_rating?.toFixed(1) || '暂无评分' }}</span>
              <span class="mx-2">|</span>
              <span>{{ lesson.view_count || 0 }} 次学习</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded">
                {{ getDifficultyText(lesson.difficulty_level) }}
              </span>
              <button class="text-blue-600 text-sm font-medium hover:text-blue-800">
                开始学习 →
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 高级筛选和搜索 -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <div class="flex flex-col gap-4">
          <!-- 第一行：搜索和基础筛选 -->
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
          
          <!-- 第二行：高级筛选 -->
          <div class="flex flex-col md:flex-row gap-4">
            <select
              v-model="filterDifficulty"
              class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">全部难度</option>
              <option value="beginner">基础</option>
              <option value="intermediate">中级</option>
              <option value="advanced">高级</option>
            </select>
            <select
              v-model="filterRating"
              class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">全部评分</option>
              <option value="4">4星以上</option>
              <option value="3">3星以上</option>
              <option value="2">2星以上</option>
            </select>
            <select
              v-model="sortBy"
              class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="default">默认排序</option>
              <option value="rating">评分最高</option>
              <option value="popular">最受欢迎</option>
              <option value="newest">最新发布</option>
            </select>
            <button
              @click="resetFilters"
              class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-gray-700"
            >
              重置筛选
            </button>
          </div>
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
        <p class="mt-2 text-sm text-gray-500">请等待老师发布课程或调整筛选条件</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="lesson in filteredLessons"
          :key="lesson.id"
          class="bg-white rounded-lg shadow hover:shadow-lg transition-shadow relative group"
        >
          <!-- 收藏按钮 -->
          <button
            @click.stop="toggleFavorite(lesson.id)"
            class="absolute top-4 right-4 z-10 p-2 bg-white rounded-full shadow-md hover:bg-red-50 transition-colors"
            :class="{ 'text-red-500': isFavorited(lesson.id), 'text-gray-400': !isFavorited(lesson.id) }"
          >
            <svg class="w-5 h-5" :fill="isFavorited(lesson.id) ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </button>

          <!-- 课程封面 -->
          <div 
            class="h-40 bg-gradient-to-br from-blue-500 to-purple-600 rounded-t-lg flex items-center justify-center cursor-pointer"
            @click="viewLesson(lesson.id)"
          >
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

            <!-- 难度和评分 -->
            <div class="flex items-center gap-2 mb-3">
              <span v-if="lesson.difficulty_level" class="text-xs px-2 py-1 rounded" :class="getDifficultyClass(lesson.difficulty_level)">
                {{ getDifficultyText(lesson.difficulty_level) }}
              </span>
              <div class="flex items-center text-yellow-500">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                <span class="ml-1 text-sm text-gray-700">
                  {{ lesson.average_rating?.toFixed(1) || '0.0' }}
                </span>
                <span class="ml-1 text-xs text-gray-500">
                  ({{ lesson.review_count || 0 }})
                </span>
              </div>
            </div>

            <!-- 课程元信息 -->
            <div class="space-y-2 mb-4">
              <!-- 教师信息 -->
              <div v-if="lesson.creator_name" class="flex items-center text-xs text-gray-600">
                <svg class="w-4 h-4 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <span class="font-medium text-gray-700">{{ lesson.creator_name }} 老师</span>
              </div>
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
              @click="viewLesson(lesson.id)"
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
import { favoriteService } from '@/services/favorite'
import type { Lesson } from '@/types/lesson'
import type { Subject } from '@/types/curriculum'
import DashboardHeader from '@/components/Common/DashboardHeader.vue'

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
const filterDifficulty = ref('')
const filterRating = ref('')
const sortBy = ref('default')
const showRecommended = ref(true)
const loadingRecommended = ref(false)
const recommendedLessons = ref<Lesson[]>([])
const favoritedLessonIds = ref<Set<number>>(new Set())

// 学习进度数据（从localStorage获取）
const progressData = ref<Record<number, number>>({})

// 计算属性
const currentUser = computed(() => userStore.user)
const userName = computed(() => userStore.user?.full_name || userStore.user?.username || '学生')

const filteredLessons = computed(() => {
  let result = [...availableLessons.value]

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

  // 按难度过滤
  if (filterDifficulty.value) {
    result = result.filter(lesson => lesson.difficulty_level === filterDifficulty.value)
  }

  // 按评分过滤
  if (filterRating.value) {
    const minRating = Number(filterRating.value)
    result = result.filter(lesson => (lesson.average_rating || 0) >= minRating)
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

  // 排序
  if (sortBy.value === 'rating') {
    result.sort((a, b) => (b.average_rating || 0) - (a.average_rating || 0))
  } else if (sortBy.value === 'popular') {
    result.sort((a, b) => (b.view_count || 0) - (a.view_count || 0))
  } else if (sortBy.value === 'newest') {
    result.sort((a, b) => new Date(b.published_at || b.created_at).getTime() - new Date(a.published_at || a.created_at).getTime())
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
    
    // 加载收藏列表
    await loadFavorites()
    
    // 加载推荐课程
    await loadRecommendedLessons()
  } catch (e: any) {
    error.value = e.message || '加载数据失败'
    console.error('Failed to fetch data:', e)
  } finally {
    loading.value = false
  }
}

const loadRecommendedLessons = async () => {
  loadingRecommended.value = true
  try {
    const response = await lessonService.fetchRecommendedLessons(6)
    recommendedLessons.value = response.items
  } catch (e) {
    console.error('Failed to load recommended lessons:', e)
  } finally {
    loadingRecommended.value = false
  }
}

const loadFavorites = async () => {
  try {
    const favorites = await favoriteService.getMyFavorites()
    favoritedLessonIds.value = new Set(favorites.map(f => f.lesson_id))
  } catch (e) {
    console.error('Failed to load favorites:', e)
  }
}

const isFavorited = (lessonId: number): boolean => {
  return favoritedLessonIds.value.has(lessonId)
}

const toggleFavorite = async (lessonId: number) => {
  try {
    const isFav = await favoriteService.toggleFavorite(lessonId)
    if (isFav) {
      favoritedLessonIds.value.add(lessonId)
    } else {
      favoritedLessonIds.value.delete(lessonId)
    }
  } catch (e: any) {
    alert(e.message || '操作失败')
  }
}

const getDifficultyText = (level: string | undefined): string => {
  const map: Record<string, string> = {
    'beginner': '基础',
    'intermediate': '中级',
    'advanced': '高级'
  }
  return map[level || ''] || '基础'
}

const getDifficultyClass = (level: string | undefined): string => {
  const map: Record<string, string> = {
    'beginner': 'bg-green-100 text-green-700',
    'intermediate': 'bg-yellow-100 text-yellow-700',
    'advanced': 'bg-red-100 text-red-700'
  }
  return map[level || ''] || 'bg-gray-100 text-gray-700'
}

const resetFilters = () => {
  searchQuery.value = ''
  filterStatus.value = ''
  filterSubject.value = ''
  filterDifficulty.value = ''
  filterRating.value = ''
  sortBy.value = 'default'
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
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
