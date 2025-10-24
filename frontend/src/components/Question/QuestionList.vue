<template>
  <div class="question-list">
    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <span class="ml-3 text-gray-600">加载中...</span>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!questions || questions.length === 0" class="text-center py-8">
      <div class="text-gray-400 text-5xl mb-3">💭</div>
      <p class="text-gray-600">暂无问题</p>
      <p class="text-sm text-gray-500 mt-1">成为第一个提问的人吧！</p>
    </div>

    <!-- 问题列表 -->
    <div v-else class="space-y-3">
      <div
        v-for="question in questions"
        :key="question.id"
        class="question-card bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
        @click="handleQuestionClick(question.id)"
      >
        <!-- 头部 -->
        <div class="flex items-start justify-between mb-2">
          <div class="flex items-center space-x-2 flex-1">
            <!-- 置顶标记 -->
            <span v-if="question.is_pinned" class="px-2 py-0.5 bg-red-100 text-red-700 text-xs font-medium rounded">
              📌 置顶
            </span>

            <!-- 状态标记 -->
            <span
              v-if="question.status === QuestionStatus.RESOLVED"
              class="px-2 py-0.5 bg-green-100 text-green-700 text-xs font-medium rounded"
            >
              ✓ 已解决
            </span>
            <span
              v-else-if="question.status === QuestionStatus.ANSWERED"
              class="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs font-medium rounded"
            >
              已回答
            </span>
            <span
              v-else
              class="px-2 py-0.5 bg-yellow-100 text-yellow-700 text-xs font-medium rounded"
            >
              待回答
            </span>
          </div>

          <!-- 统计信息 -->
          <div class="flex items-center space-x-3 text-sm text-gray-500">
            <span class="flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              {{ question.views }}
            </span>
            <span class="flex items-center">
              💬 {{ question.answer_count }}
            </span>
            <span v-if="question.upvotes > 0" class="flex items-center">
              👍 {{ question.upvotes }}
            </span>
          </div>
        </div>

        <!-- 问题标题 -->
        <h3 class="text-base font-semibold text-gray-800 mb-2 hover:text-blue-600 transition-colors">
          {{ question.title }}
        </h3>

        <!-- 问题预览 -->
        <p class="text-sm text-gray-600 line-clamp-2 mb-3">
          {{ question.content }}
        </p>

        <!-- 底部信息 -->
        <div class="flex items-center justify-between text-xs text-gray-500">
          <div class="flex items-center space-x-3">
            <!-- 提问者 -->
            <span class="flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              {{ question.student.username }}
            </span>

            <!-- 关联单元 -->
            <span v-if="question.cell" class="flex items-center text-blue-600">
              📍 单元{{ question.cell.order + 1 }}
            </span>

            <!-- 回答类型 -->
            <span v-if="question.has_ai_answer" class="flex items-center">
              🤖 AI已回答
            </span>
            <span v-if="question.has_teacher_answer" class="flex items-center">
              👨‍🏫 教师已回答
            </span>
          </div>

          <!-- 时间 -->
          <span>
            {{ formatTime(question.created_at) }}
          </span>
        </div>
      </div>
    </div>

    <!-- 加载更多 -->
    <div v-if="hasMore && !loading" class="text-center py-4">
      <button
        @click="$emit('load-more')"
        class="px-4 py-2 text-blue-600 hover:text-blue-700 font-medium"
      >
        加载更多
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { QuestionStatus, type QuestionListItem } from '@/types/question'

// Props
interface Props {
  questions: QuestionListItem[]
  loading?: boolean
  hasMore?: boolean
}

defineProps<Props>()

// Emits
const emit = defineEmits<{
  'question-click': [id: number]
  'load-more': []
}>()

// 点击问题
const handleQuestionClick = (id: number) => {
  emit('question-click', id)
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

  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

