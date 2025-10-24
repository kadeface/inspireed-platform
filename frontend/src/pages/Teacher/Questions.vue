<template>
  <div class="teacher-questions-page min-h-screen bg-gray-50">
    <!-- 头部 -->
    <div class="bg-white border-b">
      <div class="max-w-7xl mx-auto px-4 py-6">
        <div class="flex items-center justify-between mb-4">
          <h1 class="text-2xl font-bold text-gray-900">
            💬 学生问答
          </h1>
          
          <!-- 统计卡片 -->
          <div v-if="stats" class="flex items-center space-x-4">
            <div class="bg-yellow-50 border border-yellow-200 rounded-lg px-4 py-2">
              <div class="text-xs text-yellow-700 mb-1">待回答</div>
              <div class="text-2xl font-bold text-yellow-600">{{ stats.pending }}</div>
            </div>
            <div class="bg-blue-50 border border-blue-200 rounded-lg px-4 py-2">
              <div class="text-xs text-blue-700 mb-1">已回答</div>
              <div class="text-2xl font-bold text-blue-600">{{ stats.answered }}</div>
            </div>
            <div class="bg-green-50 border border-green-200 rounded-lg px-4 py-2">
              <div class="text-xs text-green-700 mb-1">已解决</div>
              <div class="text-2xl font-bold text-green-600">{{ stats.resolved }}</div>
            </div>
          </div>
        </div>

        <!-- 筛选栏 -->
        <div class="flex items-center space-x-4">
          <!-- 状态标签 -->
          <div class="flex items-center space-x-2">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              @click="currentTab = tab.key"
              :class="[
                'px-4 py-2 rounded-lg font-medium transition-colors',
                currentTab === tab.key
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
              ]"
            >
              {{ tab.label }}
              <span v-if="tab.count !== undefined" class="ml-1 text-sm">
                ({{ tab.count }})
              </span>
            </button>
          </div>

          <!-- 课程筛选 -->
          <select
            v-model="filterLessonId"
            class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option :value="undefined">全部课程</option>
            <!-- TODO: 加载教师的课程列表 -->
          </select>

          <!-- 排序 -->
          <select
            v-model="sortBy"
            class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="created_at">最新提问</option>
            <option value="upvotes">最多点赞</option>
          </select>

          <!-- 刷新按钮 -->
          <button
            @click="loadQuestions"
            class="p-2 text-gray-600 hover:text-gray-800 transition-colors"
            title="刷新"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="max-w-7xl mx-auto px-4 py-6">
      <!-- 加载状态 -->
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span class="ml-3 text-gray-600">加载中...</span>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!questions || questions.length === 0" class="bg-white rounded-lg shadow-sm p-12 text-center">
        <div class="text-gray-400 text-6xl mb-4">💭</div>
        <p class="text-gray-700 text-lg mb-2">{{ emptyMessage }}</p>
        <p class="text-sm text-gray-500">{{ emptyHint }}</p>
      </div>

      <!-- 问题列表 -->
      <div v-else class="space-y-4">
        <div
          v-for="question in questions"
          :key="question.id"
          class="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow"
        >
          <div class="p-6">
            <!-- 头部 -->
            <div class="flex items-start justify-between mb-3">
              <div class="flex items-center space-x-2 flex-1">
                <!-- 置顶 -->
                <button
                  v-if="question.is_pinned"
                  @click="handleUnpin(question.id)"
                  class="px-2 py-1 bg-red-100 text-red-700 text-xs font-medium rounded hover:bg-red-200 transition-colors"
                  title="取消置顶"
                >
                  📌 已置顶
                </button>
                <button
                  v-else
                  @click="handlePin(question.id)"
                  class="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded hover:bg-gray-200 transition-colors"
                  title="置顶"
                >
                  📌 置顶
                </button>

                <!-- 优先级标记 -->
                <span v-if="!question.has_teacher_answer && question.upvotes > 5" class="px-2 py-1 bg-orange-100 text-orange-700 text-xs font-medium rounded">
                  🔥 热门问题
                </span>

                <!-- AI已回答 -->
                <span v-if="question.has_ai_answer" class="px-2 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded">
                  🤖 AI已回答
                </span>
              </div>

              <div class="flex items-center space-x-3 text-sm text-gray-500">
                <span>👁️ {{ question.views }}</span>
                <span>👍 {{ question.upvotes }}</span>
                <span>💬 {{ question.answer_count }}</span>
              </div>
            </div>

            <!-- 问题标题 -->
            <h3 class="text-lg font-semibold text-gray-900 mb-2 hover:text-blue-600 cursor-pointer" @click="viewQuestion(question.id)">
              {{ question.title }}
            </h3>

            <!-- 问题预览 -->
            <p class="text-gray-600 text-sm mb-4 line-clamp-2">
              {{ question.content }}
            </p>

            <!-- 底部信息 -->
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-4 text-sm text-gray-600">
                <span class="flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  {{ question.student.username }}
                </span>
                <span>📚 {{ question.lesson.title }}</span>
                <span v-if="question.cell">📍 单元{{ question.cell.order + 1 }}</span>
                <span>{{ formatTime(question.created_at) }}</span>
              </div>

              <!-- 操作按钮 -->
              <div class="flex items-center space-x-2">
                <button
                  @click="viewQuestion(question.id)"
                  class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  查看详情
                </button>
                <button
                  v-if="!question.has_teacher_answer"
                  @click="answerQuestion(question.id)"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  立即回答
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="pagination.has_more" class="text-center py-4">
          <button
            @click="loadMore"
            :disabled="loading"
            class="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            加载更多
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import questionService from '@/services/question'
import type { QuestionListItem, QuestionStats } from '@/types/question'

const router = useRouter()

// 当前标签
const currentTab = ref<'pending' | 'all'>('pending')

// 筛选条件
const filterLessonId = ref<number | undefined>(undefined)
const sortBy = ref<'created_at' | 'upvotes'>('created_at')

// 数据
const questions = ref<QuestionListItem[]>([])
const stats = ref<QuestionStats | null>(null)
const loading = ref(false)
const pagination = ref({
  page: 1,
  page_size: 20,
  total: 0,
  has_more: false
})

// 标签配置
const tabs = computed(() => [
  { key: 'pending' as const, label: '待回答', count: stats.value?.pending },
  { key: 'all' as const, label: '全部问题', count: stats.value?.total }
])

// 空状态文案
const emptyMessage = computed(() => {
  if (currentTab.value === 'pending') {
    return '暂无待回答的问题'
  }
  return '暂无问题'
})

const emptyHint = computed(() => {
  if (currentTab.value === 'pending') {
    return '太棒了！所有问题都已回答'
  }
  return '学生提问后会显示在这里'
})

// 加载统计数据
const loadStats = async () => {
  try {
    stats.value = await questionService.getQuestionStats(filterLessonId.value)
  } catch (err) {
    console.error('Failed to load stats:', err)
  }
}

// 加载问题列表
const loadQuestions = async (append = false) => {
  try {
    loading.value = true

    if (!append) {
      pagination.value.page = 1
    }

    const response = await questionService.getTeacherPendingQuestions({
      lesson_id: filterLessonId.value,
      sort: sortBy.value,
      page: pagination.value.page,
      page_size: pagination.value.page_size
    })

    if (append) {
      questions.value = [...questions.value, ...response.items]
    } else {
      questions.value = response.items
    }

    pagination.value.total = response.total
    pagination.value.has_more = response.has_more

  } catch (err: any) {
    console.error('Failed to load questions:', err)
    alert('❌ 加载失败：' + err.message)
  } finally {
    loading.value = false
  }
}

// 加载更多
const loadMore = () => {
  pagination.value.page++
  loadQuestions(true)
}

// 查看问题详情
const viewQuestion = (id: number) => {
  router.push(`/teacher/questions/${id}`)
}

// 回答问题
const answerQuestion = (id: number) => {
  router.push(`/teacher/questions/${id}/answer`)
}

// 置顶问题
const handlePin = async (id: number) => {
  try {
    await questionService.pinQuestion(id)
    alert('✅ 已置顶')
    await loadQuestions()
  } catch (err: any) {
    alert('❌ 操作失败：' + err.message)
  }
}

// 取消置顶
const handleUnpin = async (id: number) => {
  try {
    await questionService.pinQuestion(id)
    alert('✅ 已取消置顶')
    await loadQuestions()
  } catch (err: any) {
    alert('❌ 操作失败：' + err.message)
  }
}

// 格式化时间
const formatTime = (dateStr: string): string => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  return date.toLocaleDateString('zh-CN')
}

// 监听筛选条件变化
watch([currentTab, filterLessonId, sortBy], () => {
  loadQuestions()
})

// 组件挂载时加载数据
onMounted(() => {
  loadStats()
  loadQuestions()
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

