<template>
  <div class="question-detail-page min-h-screen bg-gray-50">
    <!-- 顶部导航 -->
    <div class="sticky top-0 z-10 border-b border-slate-200 bg-white">
      <div class="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
        <button
          @click="goBack"
          class="inline-flex h-9 items-center gap-1.5 rounded-xl bg-white px-3 text-sm font-medium text-slate-700 shadow-sm ring-1 ring-inset ring-slate-200 transition-all hover:bg-slate-50 hover:ring-slate-300"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          返回
        </button>

        <div class="text-sm text-gray-600">
          问题详情 #{{ questionId }}
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="max-w-5xl mx-auto px-4 py-12 flex items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
      <span class="ml-3 text-gray-600">加载中...</span>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="max-w-5xl mx-auto px-4 py-12 text-center">
      <div class="text-red-500 text-5xl mb-4">⚠️</div>
      <p class="text-gray-700 text-lg mb-2">加载失败</p>
      <p class="text-gray-500 text-sm mb-4">{{ error }}</p>
      <button
        @click="loadQuestion"
        class="inline-flex h-9 items-center rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 px-4 text-sm font-medium text-white shadow-lg shadow-emerald-500/30 transition-all hover:from-emerald-600 hover:to-teal-600"
      >
        重试
      </button>
    </div>

    <!-- 问题内容 -->
    <div v-else-if="question" class="max-w-5xl mx-auto px-4 py-6">
      <!-- 问题卡片 -->
      <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
        <!-- 头部 -->
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center space-x-2">
            <span
              v-if="question.is_pinned"
              class="px-2 py-1 bg-red-100 text-red-700 text-sm font-medium rounded"
            >
              📌 置顶
            </span>
            <span
              v-if="question.status === QuestionStatus.RESOLVED"
              class="px-2 py-1 bg-green-100 text-green-700 text-sm font-medium rounded"
            >
              ✓ 已解决
            </span>
            <span
              v-else-if="question.status === QuestionStatus.ANSWERED"
              class="px-2 py-1 bg-blue-100 text-blue-700 text-sm font-medium rounded"
            >
              已回答
            </span>
            <span
              v-else
              class="px-2 py-1 bg-yellow-100 text-yellow-700 text-sm font-medium rounded"
            >
              待回答
            </span>
          </div>

          <!-- 统计 -->
          <div class="flex items-center space-x-4 text-sm text-gray-500">
            <span class="flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              {{ question.views }}次查看
            </span>
            <span v-if="question.upvotes > 0">
              👍 {{ question.upvotes }}
            </span>
          </div>
        </div>

        <!-- 问题标题 -->
        <h1 class="text-2xl font-bold text-gray-900 mb-4">
          ❓ {{ question.title }}
        </h1>

        <!-- 问题详情 -->
        <div class="prose max-w-none mb-4">
          <p class="text-gray-700 whitespace-pre-wrap">{{ question.content }}</p>
        </div>

        <!-- 元信息 -->
        <div class="flex items-center justify-between pt-4 border-t text-sm text-gray-600">
          <div class="flex items-center space-x-4">
            <span class="flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              {{ question.student.username }}
            </span>
            <span>
              提问于 {{ formatDateTime(question.created_at) }}
            </span>
            <span v-if="question.cell" class="text-blue-600">
              📍 关联单元{{ question.cell.order + 1 }}
            </span>
          </div>

          <!-- 操作按钮（提问者） -->
          <div v-if="isMyQuestion && question.status === QuestionStatus.ANSWERED" class="flex items-center space-x-2">
            <button
              @click="handleResolve"
              class="inline-flex h-9 items-center rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 px-4 text-sm font-medium text-white shadow-lg shadow-emerald-500/30 transition-all hover:from-emerald-600 hover:to-teal-600"
            >
              ✓ 标记为已解决
            </button>
          </div>
        </div>
      </div>

      <!-- 回答列表 -->
      <div v-if="question.answers && question.answers.length > 0" class="space-y-4">
        <h2 class="text-xl font-semibold text-gray-800 mb-4">
          💬 回答 ({{ question.answers.length }})
        </h2>

        <div
          v-for="answer in question.answers"
          :key="answer.id"
          class="bg-white rounded-lg shadow-sm overflow-hidden"
        >
          <!-- 回答头部 -->
          <div class="px-6 py-4 bg-gray-50 border-b flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <!-- 回答者类型 -->
              <span v-if="answer.answerer_type === AnswererType.AI" class="flex items-center text-purple-600 font-medium">
                🤖 AI回答
                <span v-if="answer.ai_model" class="ml-2 text-xs text-gray-500">({{ answer.ai_model }})</span>
              </span>
              <span v-else class="flex items-center text-blue-600 font-medium">
                👨‍🏫 {{ answer.answerer?.username || '教师' }}的回答
              </span>

              <!-- 最佳答案标记 -->
              <span v-if="answer.is_accepted" class="px-2 py-0.5 bg-green-100 text-green-700 text-xs font-medium rounded">
                ✓ 最佳答案
              </span>
            </div>

            <div class="flex items-center space-x-4">
              <!-- 评分显示 -->
              <div v-if="answer.rating" class="flex items-center text-yellow-500">
                <span v-for="i in 5" :key="i" class="text-lg">
                  {{ i <= answer.rating ? '⭐' : '☆' }}
                </span>
              </div>
              <!-- 评分按钮（提问者） -->
              <button
                v-else-if="isMyQuestion"
                @click="handleRate(answer)"
                class="text-sm text-blue-600 hover:text-blue-700"
              >
                评分
              </button>

              <!-- 点赞 -->
              <span v-if="answer.upvotes > 0" class="text-sm text-gray-600">
                👍 {{ answer.upvotes }}
              </span>

              <span class="text-sm text-gray-500">
                {{ formatDateTime(answer.created_at) }}
              </span>
            </div>
          </div>

          <!-- 回答内容（使用Cell组件展示） -->
          <div class="p-6">
            <div v-if="answer.content && answer.content.length > 0" class="space-y-4">
              <!-- 核心：复用CellContainer组件显示回答 -->
              <CellContainer
                v-for="(cell, cellIndex) in answer.content"
                :key="`answer-${answer.id}-cell-${cellIndex}`"
                :cell="cell"
                :editable="false"
              />
            </div>
            <div v-else class="text-gray-500 italic">
              暂无回答内容
            </div>
          </div>
        </div>
      </div>

      <!-- 无回答状态 -->
      <div v-else class="bg-white rounded-lg shadow-sm p-8 text-center">
        <div class="text-gray-400 text-5xl mb-3">⏳</div>
        <p class="text-gray-600 font-medium mb-2">等待回答中...</p>
        <p class="text-sm text-gray-500">
          {{ question.ask_type === AskType.AI ? 'AI正在生成回答' : '老师看到后会尽快回复' }}
        </p>
      </div>
    </div>

    <!-- 评分对话框 -->
    <RatingModal
      v-if="ratingAnswer"
      :show="showRatingModal"
      @close="showRatingModal = false"
      @submit="handleRatingSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import questionService from '@/services/question'
import CellContainer from '@/components/Cell/CellContainer.vue'
import RatingModal from '@/components/Question/RatingModal.vue'
import { QuestionStatus, AskType, AnswererType, type QuestionDetail, type Answer } from '@/types/question'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 问题ID
const questionId = computed(() => parseInt(route.params.id as string))

// 数据
const question = ref<QuestionDetail | null>(null)
const loading = ref(false)
const error = ref('')

// 评分相关
const showRatingModal = ref(false)
const ratingAnswer = ref<Answer | null>(null)

// 是否是我的问题
const isMyQuestion = computed(() => {
  return question.value?.student_id === userStore.user?.id
})

// 加载问题详情
const loadQuestion = async () => {
  if (!questionId.value) return

  try {
    loading.value = true
    error.value = ''
    question.value = await questionService.getQuestionDetail(questionId.value)
  } catch (err: any) {
    console.error('Failed to load question:', err)
    error.value = err.message || '加载失败'
  } finally {
    loading.value = false
  }
}

// 返回
const goBack = () => {
  router.back()
}

// 标记为已解决
const handleResolve = async () => {
  if (!confirm('确定标记此问题为已解决吗？')) return

  try {
    await questionService.resolveQuestion(questionId.value)
    alert('✅ 已标记为已解决')
    await loadQuestion()  // 重新加载
  } catch (err: any) {
    alert('❌ 操作失败：' + err.message)
  }
}

// 打开评分对话框
const handleRate = (answer: Answer) => {
  ratingAnswer.value = answer
  showRatingModal.value = true
}

// 提交评分
const handleRatingSubmit = async (rating: number) => {
  if (!ratingAnswer.value) return

  try {
    await questionService.rateAnswer(ratingAnswer.value.id, { rating })
    alert(`✅ 评分成功：${rating}星`)
    showRatingModal.value = false
    ratingAnswer.value = null
    await loadQuestion()  // 重新加载
  } catch (err: any) {
    alert('❌ 评分失败：' + err.message)
  }
}

// 格式化日期时间
const formatDateTime = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 组件挂载时加载数据
onMounted(() => {
  loadQuestion()
})
</script>

<style scoped>
.prose {
  max-width: none;
}
</style>

