<template>
  <div class="min-h-screen bg-gray-50">
    <DashboardHeader
      title="我的收藏"
      subtitle="您收藏的课程"
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

      <div v-else-if="favorites.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
        <div class="text-6xl mb-4">❤️</div>
        <p class="text-lg text-gray-600">还没有收藏的课程</p>
        <p class="text-sm text-gray-500 mt-2">浏览课程并点击收藏按钮添加到这里</p>
        <button
          @click="router.push('/student')"
          class="mt-6 px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          去浏览课程
        </button>
      </div>

      <div v-else>
        <div class="mb-4 text-sm text-gray-600">
          共 {{ favorites.length }} 个收藏
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="fav in favorites"
            :key="fav.id"
            class="bg-white rounded-lg shadow hover:shadow-lg transition-shadow relative group"
          >
            <!-- 取消收藏按钮 -->
            <button
              @click.stop="removeFavorite(fav.lesson_id)"
              class="absolute top-4 right-4 z-10 p-2 bg-white rounded-full shadow-md hover:bg-red-50 transition-colors text-red-500"
            >
              <svg class="w-5 h-5" fill="currentColor" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </button>

            <!-- 课程封面 -->
            <div
              class="h-40 bg-gradient-to-br from-pink-500 to-rose-600 rounded-t-lg flex items-center justify-center cursor-pointer"
              @click="viewLesson(fav.lesson_id)"
            >
              <svg class="w-16 h-16 text-white opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>

            <!-- 课程信息 -->
            <div class="p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                {{ fav.lesson_title }}
              </h3>
              <p v-if="fav.lesson_description" class="text-sm text-gray-600 mb-4 line-clamp-2">
                {{ fav.lesson_description }}
              </p>

              <div class="flex items-center gap-2 mb-4">
                <span v-if="fav.lesson_difficulty" class="text-xs px-2 py-1 rounded" :class="getDifficultyClass(fav.lesson_difficulty)">
                  {{ getDifficultyText(fav.lesson_difficulty) }}
                </span>
                <div class="flex items-center text-yellow-500">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                  <span class="ml-1 text-sm text-gray-700">{{ fav.lesson_rating.toFixed(1) }}</span>
                </div>
              </div>

              <div class="text-xs text-gray-500 mb-4">
                收藏于 {{ new Date(fav.created_at).toLocaleDateString('zh-CN') }}
              </div>

              <button
                class="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                @click="viewLesson(fav.lesson_id)"
              >
                开始学习
              </button>
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
import { favoriteService } from '@/services/favorite'
import type { FavoriteWithLesson } from '@/services/favorite'
import DashboardHeader from '@/components/Common/DashboardHeader.vue'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const error = ref<string | null>(null)
const favorites = ref<FavoriteWithLesson[]>([])

const userName = computed(() => userStore.user?.full_name || userStore.user?.username || '学生')

const fetchData = async () => {
  loading.value = true
  error.value = null
  try {
    favorites.value = await favoriteService.getMyFavorites()
  } catch (e: any) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

const removeFavorite = async (lessonId: number) => {
  if (!confirm('确定要取消收藏吗？')) return

  try {
    await favoriteService.removeFavorite(lessonId)
    favorites.value = favorites.value.filter(f => f.lesson_id !== lessonId)
  } catch (e: any) {
    alert(e.message || '操作失败')
  }
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

const getDifficultyClass = (level: string): string => {
  const map: Record<string, string> = {
    'beginner': 'bg-green-100 text-green-700',
    'intermediate': 'bg-yellow-100 text-yellow-700',
    'advanced': 'bg-red-100 text-red-700'
  }
  return map[level] || 'bg-gray-100 text-gray-700'
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

