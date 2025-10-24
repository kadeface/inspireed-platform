<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="closeModal">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto m-4">
      <!-- 头部 -->
      <div class="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
        <h2 class="text-xl font-semibold text-gray-800">
          📝 {{ isAIOnly ? '向AI提问' : '向老师提问' }}
        </h2>
        <button @click="closeModal" class="text-gray-400 hover:text-gray-600 transition-colors">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 表单内容 -->
      <form @submit.prevent="handleSubmit" class="p-6 space-y-5">
        <!-- 问题标题 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            问题标题 <span class="text-red-500">*</span>
          </label>
          <input
            v-model="formData.title"
            type="text"
            placeholder="简要描述您的问题..."
            maxlength="200"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
          <div class="text-xs text-gray-500 mt-1 text-right">
            {{ formData.title.length }}/200
          </div>
        </div>

        <!-- 问题详情 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            问题详情 <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="formData.content"
            rows="6"
            placeholder="请详细描述您的问题，包括：&#10;1. 遇到的具体困难&#10;2. 已经尝试过的方法&#10;3. 希望得到什么样的帮助"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            required
          ></textarea>
        </div>

        <!-- 关联单元（可选） -->
        <div v-if="cells && cells.length > 0">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            📍 关联单元（可选）
          </label>
          <select
            v-model="formData.cell_id"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option :value="undefined">不关联具体单元</option>
            <option v-for="(cell, index) in cells" :key="cell.id" :value="cell.id">
              单元{{ index + 1 }}: {{ getCellTitle(cell) }}
            </option>
          </select>
          <p class="text-xs text-gray-500 mt-1">
            关联单元可以帮助老师更快定位问题
          </p>
        </div>

        <!-- 提问对象 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-3">
            提问对象 <span class="text-red-500">*</span>
          </label>
          <div class="space-y-3">
            <label class="flex items-start space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
              <input
                v-model="formData.ask_type"
                type="radio"
                :value="AskType.TEACHER"
                class="mt-1 text-blue-600 focus:ring-blue-500"
              />
              <div class="flex-1">
                <div class="font-medium text-gray-800">👨‍🏫 向教师提问</div>
                <div class="text-sm text-gray-600">教师会在看到后回复，回答更专业、更有针对性</div>
              </div>
            </label>

            <label class="flex items-start space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
              <input
                v-model="formData.ask_type"
                type="radio"
                :value="AskType.AI"
                class="mt-1 text-blue-600 focus:ring-blue-500"
              />
              <div class="flex-1">
                <div class="font-medium text-gray-800">🤖 向AI提问</div>
                <div class="text-sm text-gray-600">立即获得AI回答，快速解决常见问题</div>
              </div>
            </label>

            <label class="flex items-start space-x-3 p-3 border-2 border-blue-200 bg-blue-50 rounded-lg hover:bg-blue-100 cursor-pointer transition-colors">
              <input
                v-model="formData.ask_type"
                type="radio"
                :value="AskType.BOTH"
                class="mt-1 text-blue-600 focus:ring-blue-500"
              />
              <div class="flex-1">
                <div class="font-medium text-blue-700 flex items-center">
                  ⚡ 同时向教师和AI提问
                  <span class="ml-2 px-2 py-0.5 bg-blue-200 text-blue-800 text-xs rounded-full">推荐</span>
                </div>
                <div class="text-sm text-blue-900">先获得AI回答，教师会在此基础上补充更详细的内容</div>
              </div>
            </label>
          </div>
        </div>

        <!-- 公开设置 -->
        <div class="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
          <input
            v-model="formData.is_public"
            id="is-public"
            type="checkbox"
            class="mt-1 text-blue-600 focus:ring-blue-500 rounded"
          />
          <label for="is-public" class="flex-1 cursor-pointer">
            <div class="font-medium text-gray-800">公开此问题</div>
            <div class="text-sm text-gray-600">
              其他同学可以看到这个问题和回答，帮助更多人
            </div>
          </label>
        </div>

        <!-- 按钮组 -->
        <div class="flex items-center justify-end space-x-3 pt-4 border-t">
          <button
            type="button"
            @click="closeModal"
            class="px-5 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            :disabled="submitting"
          >
            取消
          </button>
          <button
            type="submit"
            class="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            :disabled="submitting || !isFormValid"
          >
            <svg v-if="submitting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ submitting ? '提交中...' : '提交问题' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { AskType, type QuestionFormData } from '@/types/question'
import questionService from '@/services/question'

// Props
interface Props {
  show: boolean
  lessonId: number
  cells?: any[]  // Cell列表，用于选择关联单元
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  close: []
  success: [questionId: number]
}>()

// 表单数据
const formData = ref<QuestionFormData>({
  title: '',
  content: '',
  cell_id: undefined,
  ask_type: AskType.BOTH,  // 默认推荐同时提问
  is_public: true  // 默认公开
})

// 提交状态
const submitting = ref(false)

// 表单验证
const isFormValid = computed(() => {
  return formData.value.title.trim().length > 0 &&
         formData.value.content.trim().length > 0
})

// 是否仅AI提问
const isAIOnly = computed(() => {
  return formData.value.ask_type === AskType.AI
})

// 获取Cell标题
const getCellTitle = (cell: any): string => {
  if (cell.title) return cell.title
  if (cell.cell_type === 'text') return '文本单元'
  if (cell.cell_type === 'code') return '代码单元'
  if (cell.cell_type === 'qa') return '问答单元'
  return `${cell.cell_type}单元`
}

// 关闭弹窗
const closeModal = () => {
  if (!submitting.value) {
    emit('close')
  }
}

// 重置表单
const resetForm = () => {
  formData.value = {
    title: '',
    content: '',
    cell_id: undefined,
    ask_type: AskType.BOTH,
    is_public: true
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!isFormValid.value || submitting.value) return

  try {
    submitting.value = true

    const questionData = {
      ...formData.value,
      lesson_id: props.lessonId
    }

    const result = await questionService.createQuestion(questionData)

    // 提交成功
    alert(formData.value.ask_type === AskType.AI 
      ? '✅ 问题已提交！AI已为您生成回答' 
      : formData.value.ask_type === AskType.TEACHER
      ? '✅ 问题已提交！老师看到后会回复您'
      : '✅ 问题已提交！AI已为您生成回答，老师会进一步补充')

    emit('success', result.id)
    emit('close')
    resetForm()

  } catch (error: any) {
    console.error('Submit question failed:', error)
    alert('❌ 提交失败：' + (error.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

// 监听show变化，重置表单
watch(() => props.show, (newShow) => {
  if (!newShow) {
    // 延迟重置，等待动画完成
    setTimeout(resetForm, 300)
  }
})
</script>

<style scoped>
/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>

