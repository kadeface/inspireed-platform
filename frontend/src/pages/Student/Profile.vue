<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <button
              @click="router.push('/student')"
              class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="返回工作台"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <h1 class="text-2xl font-bold text-gray-900">个人中心</h1>
          </div>
        </div>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- 左侧：个人信息 -->
        <div class="lg:col-span-1">
          <div class="bg-white rounded-lg shadow p-6">
            <!-- 头像 -->
            <div class="flex flex-col items-center">
              <div class="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <h2 class="mt-4 text-xl font-semibold text-gray-900">{{ currentUser?.username || '学生' }}</h2>
              <p class="text-sm text-gray-500">{{ currentUser?.email }}</p>
              <div class="mt-2 px-3 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                学生
              </div>
            </div>

            <!-- 个人统计 -->
            <div class="mt-6 space-y-4">
              <div class="flex justify-between items-center py-3 border-b border-gray-200">
                <span class="text-sm text-gray-600">已学课程</span>
                <span class="text-lg font-semibold text-gray-900">{{ stats.totalLessons }}</span>
              </div>
              <div class="flex justify-between items-center py-3 border-b border-gray-200">
                <span class="text-sm text-gray-600">已完成</span>
                <span class="text-lg font-semibold text-green-600">{{ stats.completedLessons }}</span>
              </div>
              <div class="flex justify-between items-center py-3 border-b border-gray-200">
                <span class="text-sm text-gray-600">进行中</span>
                <span class="text-lg font-semibold text-yellow-600">{{ stats.inProgressLessons }}</span>
              </div>
              <div class="flex justify-between items-center py-3">
                <span class="text-sm text-gray-600">学习时长</span>
                <span class="text-lg font-semibold text-gray-900">{{ stats.totalStudyTime }}h</span>
              </div>
            </div>

            <!-- 成就徽章 -->
            <div class="mt-6">
              <h3 class="text-sm font-semibold text-gray-900 mb-3">成就徽章</h3>
              <div class="grid grid-cols-3 gap-3">
                <div
                  v-for="badge in badges"
                  :key="badge.id"
                  :class="['p-3 rounded-lg text-center', badge.earned ? 'bg-yellow-100' : 'bg-gray-100 opacity-50']"
                >
                  <div class="text-2xl mb-1">{{ badge.icon }}</div>
                  <div class="text-xs text-gray-600">{{ badge.name }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：学习记录和统计 -->
        <div class="lg:col-span-2 space-y-6">
          <!-- 学习进度概览 -->
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">学习进度概览</h3>
            <div class="space-y-4">
              <div>
                <div class="flex justify-between text-sm text-gray-600 mb-2">
                  <span>总体完成度</span>
                  <span>{{ overallProgress }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-3">
                  <div
                    class="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full transition-all"
                    :style="{ width: `${overallProgress}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- 最近学习 -->
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">最近学习</h3>
            <div v-if="recentLessons.length > 0" class="space-y-4">
              <div
                v-for="lesson in recentLessons"
                :key="lesson.lessonId"
                class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                @click="router.push(`/student/lesson/${lesson.lessonId}`)"
              >
                <div class="flex-1">
                  <h4 class="font-medium text-gray-900">{{ lesson.title }}</h4>
                  <p class="text-sm text-gray-500 mt-1">上次学习: {{ formatDate(lesson.lastStudied) }}</p>
                </div>
                <div class="flex items-center gap-4">
                  <div class="text-right">
                    <div class="text-sm text-gray-600">进度</div>
                    <div class="text-lg font-semibold text-blue-600">{{ lesson.progress }}%</div>
                  </div>
                  <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <p class="mt-2">暂无学习记录</p>
            </div>
          </div>

          <!-- 学习笔记 -->
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">我的笔记</h3>
            <div v-if="savedNotes.length > 0" class="space-y-3">
              <div
                v-for="note in savedNotes"
                :key="note.lessonId"
                class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                @click="router.push(`/student/lesson/${note.lessonId}`)"
              >
                <h4 class="font-medium text-gray-900 mb-2">{{ note.lessonTitle }}</h4>
                <p class="text-sm text-gray-600 line-clamp-2">{{ note.content }}</p>
                <div class="mt-2 text-xs text-gray-500">
                  {{ note.content.length }} 字符 · {{ formatDate(note.lastUpdated) }}
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <p class="mt-2">暂无笔记</p>
            </div>
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
import type { Lesson } from '@/types/lesson'

const router = useRouter()
const userStore = useUserStore()

// 状态
const lessons = ref<Lesson[]>([])

// 计算属性
const currentUser = computed(() => userStore.user)

interface LearningRecord {
  lessonId: number
  title: string
  progress: number
  lastStudied: string
}

interface NoteRecord {
  lessonId: number
  lessonTitle: string
  content: string
  lastUpdated: string
}

// 统计数据
const stats = computed(() => {
  const progressData = getProgressData()
  const totalLessons = Object.keys(progressData).length
  const completedLessons = Object.values(progressData).filter(p => p === 100).length
  const inProgressLessons = Object.values(progressData).filter(p => p > 0 && p < 100).length
  
  // 简单估算学习时长（每个课程平均45分钟）
  const totalStudyTime = Math.round((totalLessons * 45) / 60)
  
  return {
    totalLessons,
    completedLessons,
    inProgressLessons,
    totalStudyTime
  }
})

// 总体进度
const overallProgress = computed(() => {
  const progressData = getProgressData()
  const values = Object.values(progressData)
  if (values.length === 0) return 0
  const sum = values.reduce((acc, val) => acc + val, 0)
  return Math.round(sum / values.length)
})

// 最近学习记录
const recentLessons = computed((): LearningRecord[] => {
  const progressData = getProgressData()
  const records: LearningRecord[] = []
  
  for (const [lessonIdStr, progress] of Object.entries(progressData)) {
    const lessonId = Number(lessonIdStr)
    const lesson = lessons.value.find(l => l.id === lessonId)
    if (lesson) {
      records.push({
        lessonId,
        title: lesson.title,
        progress,
        lastStudied: new Date().toISOString() // TODO: 实际应从localStorage读取最后学习时间
      })
    }
  }
  
  // 按学习时间排序，最近的在前
  return records.slice(0, 5)
})

// 保存的笔记
const savedNotes = computed((): NoteRecord[] => {
  const notes: NoteRecord[] = []
  
  for (const lesson of lessons.value) {
    const key = `lesson_${lesson.id}_notes`
    const content = localStorage.getItem(key)
    if (content && content.trim()) {
      notes.push({
        lessonId: lesson.id,
        lessonTitle: lesson.title,
        content,
        lastUpdated: new Date().toISOString() // TODO: 实际应保存笔记更新时间
      })
    }
  }
  
  return notes.slice(0, 5)
})

// 成就徽章
const badges = computed(() => {
  return [
    {
      id: 1,
      name: '初学者',
      icon: '🎓',
      earned: stats.value.totalLessons >= 1
    },
    {
      id: 2,
      name: '勤奋学习',
      icon: '📚',
      earned: stats.value.totalLessons >= 5
    },
    {
      id: 3,
      name: '完成大师',
      icon: '🏆',
      earned: stats.value.completedLessons >= 3
    },
    {
      id: 4,
      name: '笔记达人',
      icon: '📝',
      earned: savedNotes.value.length >= 3
    },
    {
      id: 5,
      name: '学习之星',
      icon: '⭐',
      earned: stats.value.completedLessons >= 10
    },
    {
      id: 6,
      name: '坚持不懈',
      icon: '💪',
      earned: stats.value.totalStudyTime >= 10
    }
  ]
})

// 方法
const getProgressData = (): Record<number, number> => {
  const saved = localStorage.getItem('student_lesson_progress')
  if (saved) {
    try {
      return JSON.parse(saved)
    } catch (e) {
      console.error('Failed to load progress data:', e)
    }
  }
  return {}
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)
  
  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins}分钟前`
  if (diffHours < 24) return `${diffHours}小时前`
  if (diffDays < 7) return `${diffDays}天前`
  
  return date.toLocaleDateString('zh-CN')
}

const loadLessons = async () => {
  try {
    const response = await lessonService.fetchLessons({
      status: 'published',
      page: 1,
      page_size: 100
    })
    lessons.value = response.items
  } catch (e: any) {
    console.error('Failed to load lessons:', e)
  }
}

// 生命周期
onMounted(() => {
  loadLessons()
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

