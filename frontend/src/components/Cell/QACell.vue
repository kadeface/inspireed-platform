<template>
  <div class="qa-cell cell-container p-4">
    <h3 class="text-lg font-semibold mb-3">{{ cell.title || '问答互动' }}</h3>
    
    <!-- 问题显示区域 -->
    <div v-if="cell.content.question" class="question-area mb-4">
      <div class="flex items-center justify-between mb-2">
        <div class="text-sm font-medium text-gray-700">问题:</div>
        <div class="flex gap-2">
          <button
            v-if="editable"
            @click="editQuestion"
            class="text-xs px-2 py-1 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded"
          >
            编辑
          </button>
          <button
            v-if="!cell.content.answer && !isAsking"
            @click="askAI"
            class="text-xs px-2 py-1 bg-green-500 text-white hover:bg-green-600 rounded"
          >
            问AI
          </button>
        </div>
      </div>
      <div class="bg-blue-50 p-3 rounded-lg">
        {{ cell.content.question }}
      </div>
    </div>

    <!-- 回答显示区域 -->
    <div v-if="cell.content.answer" class="answer-area mb-4">
      <div class="flex items-center justify-between mb-2">
        <div class="text-sm font-medium text-gray-700 flex items-center gap-2">
          回答 {{ cell.content.isAIAnswer ? '(AI)' : '' }}:
          <span v-if="cell.content.isAIAnswer && aiConfidence" class="text-xs text-gray-500">
            (置信度: {{ Math.round(aiConfidence * 100) }}%)
          </span>
        </div>
        <div class="flex gap-2">
          <button
            v-if="editable"
            @click="editAnswer"
            class="text-xs px-2 py-1 text-green-600 hover:text-green-800 hover:bg-green-50 rounded"
          >
            编辑
          </button>
          <button
            v-if="cell.content.isAIAnswer"
            @click="evaluateAnswer"
            class="text-xs px-2 py-1 text-purple-600 hover:text-purple-800 hover:bg-purple-50 rounded"
          >
            评估
          </button>
        </div>
      </div>
      <div class="bg-green-50 p-3 rounded-lg">
        <div v-html="formattedAnswer"></div>
      </div>
      
      <!-- 回答质量评估 -->
      <div v-if="answerEvaluation" class="mt-2 p-2 bg-gray-50 rounded text-xs">
        <div class="font-medium mb-1">回答质量评估:</div>
        <div class="grid grid-cols-2 gap-2">
          <div>相关性: {{ Math.round(answerEvaluation.relevance_score * 100) }}%</div>
          <div>完整性: {{ Math.round(answerEvaluation.completeness_score * 100) }}%</div>
          <div>清晰度: {{ Math.round(answerEvaluation.clarity_score * 100) }}%</div>
          <div>总体: {{ Math.round(answerEvaluation.overall_score * 100) }}%</div>
        </div>
      </div>
    </div>

    <!-- 问题输入区域 -->
    <div v-if="editable && !cell.content.question" class="input-area">
      <div class="mb-3">
        <label class="block text-sm font-medium text-gray-700 mb-2">输入问题:</label>
        <textarea
          v-model="questionInput"
          placeholder="输入你的问题..."
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows="3"
        ></textarea>
      </div>
      
      <div class="flex gap-2">
        <button
          @click="submitQuestion(false)"
          :disabled="!questionInput.trim() || isAsking"
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          提交给教师
        </button>
        <button
          @click="submitQuestion(true)"
          :disabled="!questionInput.trim() || isAsking"
          class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="isAsking">AI思考中...</span>
          <span v-else>问AI</span>
        </button>
      </div>
    </div>

    <!-- 相关问题建议 -->
    <div v-if="suggestions.length > 0" class="suggestions-area mt-4">
      <div class="text-sm font-medium text-gray-700 mb-2">相关问题建议:</div>
      <div class="space-y-1">
        <button
          v-for="(suggestion, index) in suggestions"
          :key="index"
          @click="useSuggestion(suggestion)"
          class="block w-full text-left text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 p-2 rounded"
        >
          {{ suggestion }}
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="isAsking" class="loading-area mt-4 p-4 bg-yellow-50 rounded-lg">
      <div class="flex items-center gap-2">
        <svg class="animate-spin h-4 w-4 text-yellow-600" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="text-sm text-yellow-700">AI正在思考中，请稍候...</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { QACell as QACellType } from '../../types/cell'
import { api } from '../../services/api'

interface Props {
  cell: QACellType
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
})

const emit = defineEmits<{
  update: [cell: QACellType]
}>()

// 响应式数据
const questionInput = ref('')
const isAsking = ref(false)
const suggestions = ref<string[]>([])
const answerEvaluation = ref<any>(null)
const aiConfidence = ref<number | null>(null)

// 计算属性
const formattedAnswer = computed(() => {
  if (!props.cell.content.answer) return ''
  
  // 简单的Markdown格式转换
  return props.cell.content.answer
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/```([\s\S]*?)```/g, '<pre class="bg-gray-100 p-2 rounded text-sm"><code>$1</code></pre>')
    .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 rounded text-sm">$1</code>')
    .replace(/\n/g, '<br>')
})

// 方法
async function submitQuestion(askAI: boolean = false) {
  if (!questionInput.value.trim()) return
  
  isAsking.value = true
  
  try {
    if (askAI) {
      // 调用AI问答API
      console.log('Cell ID:', props.cell.id, typeof props.cell.id)
      const cellId = parseInt(props.cell.id)
      console.log('Parsed Cell ID:', cellId)
      
      if (isNaN(cellId) || props.cell.id.startsWith('temp-')) {
        throw new Error('此 Cell 尚未保存到数据库，无法使用 AI 问答功能')
      }
      
      const response = await api.post(`/cells/${cellId}/ask`, {
        question: questionInput.value,
        ask_ai: true
      })
      
      // 更新Cell内容
      props.cell.content.question = questionInput.value
      props.cell.content.answer = response.answer
      props.cell.content.isAIAnswer = response.is_ai_answer
      
      // 保存置信度
      if (response.confidence) {
        aiConfidence.value = response.confidence
      }
      
      // 获取相关问题建议
      await loadSuggestions()
    } else {
      // 提交给教师
      props.cell.content.question = questionInput.value
      props.cell.content.answer = "此问题已提交给教师，请等待回复。"
      props.cell.content.isAIAnswer = false
    }
    
    emit('update', props.cell)
    questionInput.value = ''
  } catch (error: any) {
    console.error('提交问题失败:', error)
    console.error('详细错误信息:', error.response?.data)
    
    // 处理错误消息
    let errorMessage = '提交问题失败，请重试'
    if (error.response?.data?.detail) {
      if (Array.isArray(error.response.data.detail)) {
        // Pydantic validation errors
        errorMessage = error.response.data.detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ')
      } else if (typeof error.response.data.detail === 'string') {
        errorMessage = error.response.data.detail
      } else {
        errorMessage = JSON.stringify(error.response.data.detail)
      }
    } else if (error.message) {
      errorMessage = error.message
    }
    
    alert(errorMessage)
  } finally {
    isAsking.value = false
  }
}

async function askAI() {
  if (!props.cell.content.question) return
  
  isAsking.value = true
  
  try {
    console.log('Cell ID:', props.cell.id, typeof props.cell.id)
    const cellId = parseInt(props.cell.id)
    console.log('Parsed Cell ID:', cellId)
    
    if (isNaN(cellId) || props.cell.id.startsWith('temp-')) {
      throw new Error('此 Cell 尚未保存到数据库，无法使用 AI 问答功能')
    }
    
    const response = await api.post(`/cells/${cellId}/ask`, {
      question: props.cell.content.question,
      ask_ai: true
    })
    
    props.cell.content.answer = response.answer
    props.cell.content.isAIAnswer = response.is_ai_answer
    
    if (response.confidence) {
      aiConfidence.value = response.confidence
    }
    
    emit('update', props.cell)
    await loadSuggestions()
  } catch (error: any) {
    console.error('AI问答失败:', error)
    console.error('详细错误信息:', error.response?.data)
    
    // 处理错误消息
    let errorMessage = 'AI问答失败，请重试'
    if (error.response?.data?.detail) {
      if (Array.isArray(error.response.data.detail)) {
        // Pydantic validation errors
        errorMessage = error.response.data.detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ')
      } else if (typeof error.response.data.detail === 'string') {
        errorMessage = error.response.data.detail
      } else {
        errorMessage = JSON.stringify(error.response.data.detail)
      }
    } else if (error.message) {
      errorMessage = error.message
    }
    
    alert(errorMessage)
  } finally {
    isAsking.value = false
  }
}

async function loadSuggestions() {
  try {
    const cellId = parseInt(props.cell.id)
    const response = await api.get(`/cells/${cellId}/qa/suggestions`)
    suggestions.value = response.suggestions || []
  } catch (error) {
    console.error('获取建议失败:', error)
  }
}

async function evaluateAnswer() {
  try {
    const cellId = parseInt(props.cell.id)
    const response = await api.post(`/cells/${cellId}/qa/evaluate`)
    answerEvaluation.value = response.evaluation
  } catch (error) {
    console.error('评估回答失败:', error)
    alert('评估回答失败，请重试')
  }
}

function editQuestion() {
  questionInput.value = props.cell.content.question || ''
  // 这里可以添加编辑模式的状态管理
}

function editAnswer() {
  // 这里可以添加编辑回答的功能
  console.log('编辑回答')
}

function useSuggestion(suggestion: string) {
  questionInput.value = suggestion
}

// 组件挂载时加载建议
onMounted(() => {
  if (props.cell.content.question) {
    loadSuggestions()
  }
})
</script>

