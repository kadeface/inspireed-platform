<template>
  <div class="min-h-screen bg-gray-50">
    <DashboardHeader
      title="学习路径"
      subtitle="系统化的学习计划"
      :user-name="userName"
      @logout="handleLogout"
    />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex items-center justify-between mb-6">
        <button
          @click="router.back()"
          class="flex items-center text-gray-600 hover:text-gray-900"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回
        </button>
      </div>

      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <p class="mt-4 text-gray-600">加载中...</p>
      </div>

      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p class="text-red-600">{{ error }}</p>
      </div>

      <div v-else-if="learningPaths.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
        <div class="text-6xl mb-4">🗺️</div>
        <p class="text-lg text-gray-600">暂无学习路径</p>
        <p class="text-sm text-gray-500 mt-2">请等待老师创建学习路径</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div
          v-for="path in learningPaths"
          :key="path.id"
          class="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
          @click="viewPath(path.id)"
        >
          <div class="h-32 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-t-lg flex items-center justify-center">
            <div class="text-white text-center">
              <div class="text-4xl mb-2">🗺️</div>
              <div class="text-sm opacity-90">{{ getDifficultyText(path.difficulty_level) }}</div>
            </div>
          </div>

          <div class="p-6">
            <h3 class="text-xl font-bold text-gray-900 mb-2">{{ path.title }}</h3>
            <p v-if="path.description" class="text-sm text-gray-600 mb-4 line-clamp-2">
              {{ path.description }}
            </p>

            <div class="flex items-center justify-between text-sm text-gray-500 mb-4">
              <div class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                {{ path.lesson_count }} 个课程
              </div>
              <div v-if="path.estimated_hours" class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                约 {{ path.estimated_hours }} 小时
              </div>
            </div>

            <div class="text-xs text-gray-500">
              创建者：{{ path.creator_name }}
            </div>
          </div>
        </div>
      </div>

      <!-- 学习路径详情模态框 -->
      <div v-if="selectedPath" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click="closePathModal">
        <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto" @click.stop>
          <div class="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
            <h2 class="text-2xl font-bold text-gray-900">{{ selectedPath.title }}</h2>
            <button @click="closePathModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="p-6">
            <p v-if="selectedPath.description" class="text-gray-600 mb-6">{{ selectedPath.description }}</p>

            <div class="flex items-center gap-4 mb-6 text-sm text-gray-600">
              <span class="px-3 py-1 bg-purple-100 text-purple-700 rounded">
                {{ getDifficultyText(selectedPath.difficulty_level) }}
              </span>
              <span>{{ selectedPath.lesson_count }} 个课程</span>
              <span v-if="selectedPath.estimated_hours">约 {{ selectedPath.estimated_hours }} 小时</span>
            </div>

            <div class="space-y-4">
              <h3 class="font-semibold text-gray-900 mb-4">课程列表</h3>
              <div
                v-for="(lesson, index) in selectedPath.lessons"
                :key="lesson.id"
                class="flex items-start gap-4 p-4 border border-gray-200 rounded-lg hover:border-blue-500 transition-colors cursor-pointer"
                @click="viewLesson(lesson.lesson_id)"
              >
                <div class="flex-shrink-0 w-10 h-10 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold">
                  {{ index + 1 }}
                </div>
                <div class="flex-1">
                  <h4 class="font-medium text-gray-900 mb-1">{{ lesson.lesson_title }}</h4>
                  <p v-if="lesson.lesson_description" class="text-sm text-gray-600 line-clamp-2">
                    {{ lesson.lesson_description }}
                  </p>
                  <div class="flex items-center gap-4 mt-2 text-xs text-gray-500">
                    <span v-if="lesson.lesson_difficulty" class="px-2 py-1 bg-gray-100 rounded">
                      {{ getDifficultyText(lesson.lesson_difficulty) }}
                    </span>
                    <span v-if="lesson.lesson_rating">⭐ {{ lesson.lesson_rating.toFixed(1) }}</span>
                    <span v-if="lesson.lesson_duration">⏱ {{ lesson.lesson_duration }} 分钟</span>
                    <span v-if="lesson.is_required" class="text-red-600">必修</span>
                  </div>
                </div>
              </div>
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
import { learningPathService } from '@/services/learningPath'
import type { LearningPathListItem, LearningPathWithLessons } from '@/services/learningPath'
import DashboardHeader from '@/components/Common/DashboardHeader.vue'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const error = ref<string | null>(null)
const learningPaths = ref<LearningPathListItem[]>([])
const selectedPath = ref<LearningPathWithLessons | null>(null)

const userName = computed(() => userStore.user?.full_name || userStore.user?.username || '学生')

const fetchData = async () => {
  loading.value = true
  error.value = null
  try {
    learningPaths.value = await learningPathService.getLearningPaths(true)
  } catch (e: any) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

const viewPath = async (pathId: number) => {
  try {
    selectedPath.value = await learningPathService.getLearningPath(pathId)
  } catch (e: any) {
    alert(e.message || '加载失败')
  }
}

const closePathModal = () => {
  selectedPath.value = null
}

const viewLesson = (lessonId: number) => {
  router.push(`/student/lesson/${lessonId}`)
}

const getDifficultyText = (level: string): string => {
  const map: Record<string, string> = {
    'beginner': '基础',
    'intermediate': '中级',
    'advanced': '高级'
  }
  return map[level] || '基础'
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

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

