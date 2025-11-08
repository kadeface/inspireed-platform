<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <header class="bg-white shadow-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h1 class="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              InspireEd
            </h1>
          </div>

          <!-- 搜索栏 -->
          <div class="hidden md:flex flex-1 max-w-2xl mx-8">
            <div class="relative w-full">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="搜索课程、模拟实验..."
                class="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <svg class="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          <!-- 用户菜单 -->
          <div class="flex items-center space-x-4">
            <button @click="router.push('/student')" class="text-gray-600 hover:text-gray-900">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
            </button>
            <button @click="handleLogout" class="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg hover:from-blue-700 hover:to-indigo-700">
              退出登录
            </button>
          </div>
        </div>
      </div>

      <!-- 移动端搜索栏 -->
      <div class="md:hidden px-4 pb-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索课程、模拟实验..."
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
    </header>

    <!-- Hero 区域 -->
    <section class="bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 text-white py-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h1 class="text-4xl md:text-5xl font-bold mb-4">
          交互式模拟实验，让学习更有趣
        </h1>
        <p class="text-xl md:text-2xl mb-8 text-blue-100">
          探索物理、化学、生物、数学等多学科的互动学习体验
        </p>
        
        <!-- 统计数据 -->
        <div class="flex flex-wrap justify-center gap-12 mt-12">
          <div class="text-center">
            <div class="text-4xl md:text-5xl font-bold mb-2">{{ totalLessons }}+</div>
            <div class="text-blue-100">互动课程</div>
          </div>
          <div class="text-center">
            <div class="text-4xl md:text-5xl font-bold mb-2">{{ totalSimulations }}+</div>
            <div class="text-blue-100">模拟实验</div>
          </div>
          <div class="text-center">
            <div class="text-4xl md:text-5xl font-bold mb-2">10K+</div>
            <div class="text-blue-100">学习者</div>
          </div>
        </div>
      </div>
    </section>

    <!-- 学科分类 -->
    <section class="py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="text-3xl font-bold text-gray-900 mb-8 text-center">探索学科</h2>
        
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <button
            v-for="category in categories"
            :key="category.id"
            @click="selectCategory(category.id)"
            :class="[
              'relative group overflow-hidden rounded-xl p-6 text-center transition-all duration-300 transform hover:scale-105 hover:shadow-2xl',
              selectedCategory === category.id ? 'ring-4 ring-offset-2' : '',
              category.bgClass
            ]"
          >
            <div class="relative z-10">
              <div class="w-14 h-14 mx-auto mb-3 flex items-center justify-center text-4xl leading-none">{{ category.icon }}</div>
              <h3 class="text-lg font-bold text-white mb-1">{{ category.name }}</h3>
              <p class="text-sm text-white opacity-90">{{ category.count }} 门课程</p>
            </div>
            
            <!-- 渐变背景 -->
            <div :class="['absolute inset-0 opacity-90 group-hover:opacity-100 transition-opacity', category.gradientClass]"></div>
          </button>
        </div>
      </div>
    </section>

    <!-- PhET 模拟实验专区 -->
    <section class="py-12 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between mb-8">
          <div>
            <h2 class="text-3xl font-bold text-gray-900 mb-2">PhET 互动模拟实验</h2>
            <p class="text-gray-600">来自科罗拉多大学的优质教育资源</p>
          </div>
          <button
            @click="togglePHETFilter"
            class="px-4 py-2 text-sm font-medium text-blue-600 border-2 border-blue-600 rounded-lg hover:bg-blue-50"
          >
            {{ showOnlyPHET ? '显示全部' : '仅看 PhET' }}
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="sim in filteredPHETSimulations.slice(0, 6)"
            :key="sim.id"
            class="bg-gradient-to-br from-orange-400 to-pink-500 rounded-xl shadow-lg hover:shadow-2xl transition-all transform hover:scale-105 cursor-pointer overflow-hidden group"
            @click="openSimulation(sim)"
          >
            <div class="p-6 text-white">
              <div class="flex items-start justify-between mb-4">
                <div class="flex-1">
                  <h3 class="text-xl font-bold mb-2">{{ sim.nameCn }}</h3>
                  <p class="text-sm text-orange-100">{{ sim.name }}</p>
                </div>
                <span class="px-2 py-1 bg-white bg-opacity-20 rounded-lg text-xs font-medium">
                  {{ getCategoryName(sim.category) }}
                </span>
              </div>
              
              <p class="text-sm text-white opacity-90 mb-4">{{ sim.descriptionCn }}</p>
              
              <div class="flex items-center justify-between">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="(topic, idx) in sim.topics.slice(0, 2)"
                    :key="idx"
                    class="px-2 py-1 bg-white bg-opacity-20 rounded text-xs"
                  >
                    {{ topic }}
                  </span>
                </div>
                <svg class="w-6 h-6 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <div class="text-center mt-8">
          <button
            @click="showAllSimulations = !showAllSimulations"
            class="px-6 py-3 bg-gradient-to-r from-orange-500 to-pink-500 text-white rounded-lg hover:from-orange-600 hover:to-pink-600 font-medium shadow-lg"
          >
            {{ showAllSimulations ? '收起' : '浏览所有模拟实验' }} →
          </button>
        </div>
      </div>
    </section>

    <!-- 课程列表 -->
    <section class="py-12 bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between mb-8">
          <h2 class="text-3xl font-bold text-gray-900">
            {{ selectedCategory ? getCategoryDisplayName(selectedCategory) : '全部课程' }}
          </h2>
          
          <!-- 排序和筛选 -->
          <div class="flex items-center space-x-4">
            <select
              v-model="sortBy"
              class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="default">默认排序</option>
              <option value="rating">评分最高</option>
              <option value="popular">最受欢迎</option>
              <option value="newest">最新发布</option>
            </select>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <p class="mt-4 text-gray-600">加载中...</p>
        </div>

        <!-- 课程网格 -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <div
            v-for="lesson in filteredLessons"
            :key="lesson.id"
            class="bg-white rounded-xl shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1 cursor-pointer overflow-hidden group"
            @click="viewLesson(lesson.id)"
          >
            <!-- 课程封面 -->
            <div :class="['h-40 flex items-center justify-center relative', getRandomGradient()]">
              <svg class="w-16 h-16 text-white opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              
              <!-- 收藏按钮 -->
              <button
                @click.stop="toggleFavorite(lesson.id)"
                class="absolute top-3 right-3 p-2 bg-white rounded-full shadow-md hover:bg-red-50 transition-colors"
                :class="{ 'text-red-500': isFavorited(lesson.id), 'text-gray-400': !isFavorited(lesson.id) }"
              >
                <svg class="w-5 h-5" :fill="isFavorited(lesson.id) ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </button>
            </div>

            <!-- 课程信息 -->
            <div class="p-5">
              <h3 class="text-lg font-bold text-gray-900 mb-2 line-clamp-2 group-hover:text-blue-600">
                {{ lesson.title }}
              </h3>
              
              <div class="flex items-center mb-3">
                <div class="flex items-center text-yellow-500">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                  <span class="ml-1 text-sm font-medium text-gray-700">
                    {{ lesson.average_rating?.toFixed(1) || '0.0' }}
                  </span>
                </div>
                <span class="mx-2 text-gray-300">•</span>
                <span class="text-sm text-gray-600">{{ lesson.view_count || 0 }} 次学习</span>
              </div>

              <div class="flex items-center justify-between">
                <span
                  v-if="lesson.difficulty_level"
                  :class="['text-xs px-2 py-1 rounded-full font-medium', getDifficultyClass(lesson.difficulty_level)]"
                >
                  {{ getDifficultyText(lesson.difficulty_level) }}
                </span>
                <span class="text-xs text-gray-500">{{ lesson.estimated_duration || 45 }} 分钟</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="!loading && filteredLessons.length === 0" class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="mt-4 text-lg text-gray-600">暂无课程</p>
        </div>
      </div>
    </section>

    <!-- 底部信息 -->
    <footer class="bg-gray-900 text-white py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 class="text-lg font-bold mb-4">关于 InspireEd</h3>
            <p class="text-gray-400 text-sm">
              打造高效互动的现代化教学体验，让每一位学习者都能享受优质的教育资源。
            </p>
          </div>
          <div>
            <h3 class="text-lg font-bold mb-4">快速链接</h3>
            <ul class="space-y-2 text-sm">
              <li><a href="#" class="text-gray-400 hover:text-white">课程浏览</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white">学习路径</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white">我的收藏</a></li>
            </ul>
          </div>
          <div>
            <h3 class="text-lg font-bold mb-4">合作伙伴</h3>
            <ul class="space-y-2 text-sm">
              <li><a href="https://phet.colorado.edu" target="_blank" class="text-gray-400 hover:text-white">PhET 交互式模拟</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white">更多教育资源</a></li>
            </ul>
          </div>
          <div>
            <h3 class="text-lg font-bold mb-4">语言</h3>
            <select class="bg-gray-800 text-white px-4 py-2 rounded-lg text-sm">
              <option>简体中文</option>
              <option>English</option>
            </select>
          </div>
        </div>
        
        <div class="mt-8 pt-8 border-t border-gray-800 text-center text-sm text-gray-400">
          <p>© 2025 InspireEd. 专注于提供优质的教育科技解决方案</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { lessonService } from '@/services/lesson'
import { curriculumService } from '@/services/curriculum'
import { favoriteService } from '@/services/favorite'
import { PHET_SIMULATIONS, PHET_CATEGORIES, type PhETSimulation } from '@/data/phet-simulations'
import type { Lesson } from '@/types/lesson'

const router = useRouter()
const userStore = useUserStore()

// 状态
const loading = ref(false)
const searchQuery = ref('')
const selectedCategory = ref<string>('')
const sortBy = ref('default')
const showOnlyPHET = ref(false)
const showAllSimulations = ref(false)
const availableLessons = ref<Lesson[]>([])
const favoritedLessonIds = ref<Set<number>>(new Set())

// 学科分类
const categories = ref([
  {
    id: 'ai',
    name: '人工智能',
    icon: '🤖',
    count: 0,
    bgClass: 'bg-orange-500',
    gradientClass: 'bg-gradient-to-br from-orange-500 to-orange-600'
  },
  {
    id: 'physics',
    name: '物理',
    icon: '⚛️',
    count: 0,
    bgClass: 'bg-blue-500',
    gradientClass: 'bg-gradient-to-br from-blue-500 to-blue-600'
  },
  {
    id: 'math',
    name: '数学',
    icon: '📐',
    count: 0,
    bgClass: 'bg-green-500',
    gradientClass: 'bg-gradient-to-br from-green-500 to-green-600'
  },
  {
    id: 'chemistry',
    name: '化学',
    icon: '🧪',
    count: 0,
    bgClass: 'bg-purple-500',
    gradientClass: 'bg-gradient-to-br from-purple-500 to-purple-600'
  },
  {
    id: 'biology',
    name: '生物',
    icon: '🧬',
    count: 0,
    bgClass: 'bg-pink-500',
    gradientClass: 'bg-gradient-to-br from-pink-500 to-pink-600'
  },
  {
    id: 'earth',
    name: '地球科学',
    icon: '🌍',
    count: 0,
    bgClass: 'bg-yellow-500',
    gradientClass: 'bg-gradient-to-br from-yellow-500 to-yellow-600'
  }
])

// 计算属性
const totalLessons = computed(() => availableLessons.value.length)
const totalSimulations = computed(() => PHET_SIMULATIONS.length)

const filteredPHETSimulations = computed(() => {
  let result = PHET_SIMULATIONS
  
  if (selectedCategory.value) {
    result = result.filter(sim => sim.category === selectedCategory.value)
  }
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(sim =>
      sim.nameCn.toLowerCase().includes(query) ||
      sim.name.toLowerCase().includes(query) ||
      sim.descriptionCn.toLowerCase().includes(query)
    )
  }
  
  return result
})

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
  
  // 按分类过滤（这里需要根据您的课程数据结构调整）
  if (selectedCategory.value) {
    // 假设课程有 category 或 subject 字段
    result = result.filter(lesson => {
      // 这里需要根据实际数据结构调整
      return true // 临时返回所有
    })
  }
  
  // 排序
  if (sortBy.value === 'rating') {
    result.sort((a, b) => (b.average_rating || 0) - (a.average_rating || 0))
  } else if (sortBy.value === 'popular') {
    result.sort((a, b) => (b.view_count || 0) - (a.view_count || 0))
  } else if (sortBy.value === 'newest') {
    result.sort((a, b) =>
      new Date(b.published_at || b.created_at).getTime() -
      new Date(a.published_at || a.created_at).getTime()
    )
  }
  
  return result
})

// 方法
const selectCategory = (categoryId: string) => {
  selectedCategory.value = selectedCategory.value === categoryId ? '' : categoryId
}

const getCategoryName = (categoryId: string): string => {
  const category = PHET_CATEGORIES.find(c => c.id === categoryId)
  return category?.name || categoryId
}

const getCategoryDisplayName = (categoryId: string): string => {
  const category = categories.value.find(c => c.id === categoryId)
  return category?.name || '全部课程'
}

const togglePHETFilter = () => {
  showOnlyPHET.value = !showOnlyPHET.value
}

const openSimulation = (sim: PhETSimulation) => {
  window.open(sim.url, '_blank')
}

const getRandomGradient = (): string => {
  const gradients = [
    'bg-gradient-to-br from-blue-500 to-blue-600',
    'bg-gradient-to-br from-purple-500 to-purple-600',
    'bg-gradient-to-br from-pink-500 to-pink-600',
    'bg-gradient-to-br from-green-500 to-green-600',
    'bg-gradient-to-br from-yellow-500 to-yellow-600',
    'bg-gradient-to-br from-indigo-500 to-indigo-600',
    'bg-gradient-to-br from-red-500 to-red-600',
  ]
  return gradients[Math.floor(Math.random() * gradients.length)]!
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

const viewLesson = (lessonId: number) => {
  router.push(`/student/lesson/${lessonId}`)
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const fetchData = async () => {
  loading.value = true
  
  try {
    // 获取已发布的课程列表
    const response = await lessonService.fetchLessons({
      status: 'published',
      page: 1,
      page_size: 100
    })
    availableLessons.value = response.items
    
    // 加载收藏列表
    try {
      const favorites = await favoriteService.getMyFavorites()
      favoritedLessonIds.value = new Set(favorites.map(f => f.lesson_id))
    } catch (e) {
      console.error('Failed to load favorites:', e)
    }
  } catch (e: any) {
    console.error('Failed to fetch data:', e)
  } finally {
    loading.value = false
  }
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

