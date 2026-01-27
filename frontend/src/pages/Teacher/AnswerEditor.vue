<template>
  <div class="answer-editor-page min-h-screen bg-gray-50">
    <!-- 顶部导航 -->
    <div class="bg-white border-b sticky top-0 z-20">
      <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <button
          @click="goBack"
          class="flex items-center text-gray-600 hover:text-gray-800 transition-colors"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          返回
        </button>

        <div class="flex items-center space-x-4">
          <span v-if="saveStatus === 'saving'" class="text-sm text-gray-600">
            🔄 保存中...
          </span>
          <span v-else-if="saveStatus === 'saved'" class="text-sm text-green-600">
            ✓ 已保存
          </span>
          <span v-else-if="saveStatus === 'error'" class="text-sm text-red-600">
            ✗ 保存失败
          </span>

          <button
            @click="handlePreview"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            👁️ 预览
          </button>
          
          <button
            @click="handleSaveDraft"
            :disabled="saving"
            class="px-4 py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors disabled:opacity-50"
          >
            💾 保存草稿
          </button>

          <button
            @click="handleSubmit"
            :disabled="saving || answerCells.length === 0"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ saving ? '提交中...' : '✓ 提交回答' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="max-w-7xl mx-auto px-4 py-12 flex items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      <span class="ml-3 text-gray-600">加载中...</span>
    </div>

    <!-- 主内容区 -->
    <div v-else-if="question" class="max-w-7xl mx-auto px-4 py-6">
      <div class="grid grid-cols-3 gap-6">
        <!-- 左侧：Cell工具栏 -->
        <div class="col-span-1">
          <div class="bg-white rounded-lg shadow-sm p-4 sticky top-24">
            <h3 class="text-sm font-semibold text-gray-700 mb-4 flex items-center">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              添加教学单元
            </h3>

            <!-- 复用CellToolbar -->
            <CellToolbar @add-cell="handleAddCell" />

            <div class="mt-6 p-3 bg-blue-50 rounded-lg text-sm text-blue-700">
              <p class="font-medium mb-1">💡 提示</p>
              <p class="text-xs">您可以使用各种类型的教学单元来回答问题，就像创建教案一样！</p>
            </div>
          </div>
        </div>

        <!-- 右侧：问题详情 + 回答编辑区 -->
        <div class="col-span-2 space-y-6">
          <!-- 问题详情面板 -->
          <div class="bg-white rounded-lg shadow-sm p-6">
            <div class="flex items-start justify-between mb-4">
              <h2 class="text-lg font-semibold text-gray-900">
                📋 学生问题
              </h2>
              <span class="px-2 py-1 bg-yellow-100 text-yellow-700 text-sm font-medium rounded">
                待回答
              </span>
            </div>

            <h3 class="text-xl font-bold text-gray-900 mb-3">
              {{ question.title }}
            </h3>

            <p class="text-gray-700 whitespace-pre-wrap mb-4">
              {{ question.content }}
            </p>

            <div class="flex items-center space-x-4 text-sm text-gray-600 pt-4 border-t">
              <span class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                {{ question.student.username }}
              </span>
              <span>📚 {{ question.lesson.title }}</span>
              <span v-if="question.cell">📍 单元{{ question.cell.order + 1 }}</span>
              <span>{{ formatDateTime(question.created_at) }}</span>
            </div>

            <!-- AI回答（如果有） -->
            <div v-if="hasAIAnswer" class="mt-4 p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <div class="flex items-center mb-2">
                <svg class="w-5 h-5 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                <span class="text-purple-700 font-medium">AI已给出了基础回答</span>
              </div>
              <p class="text-sm text-purple-900">
                您可以在AI回答的基础上，补充更专业、更有针对性的内容。
              </p>
              <button
                @click="viewAIAnswer"
                class="mt-2 text-sm text-purple-600 hover:text-purple-700 underline"
              >
                查看AI回答 →
              </button>
            </div>
          </div>

          <!-- 回答编辑区 -->
          <div class="bg-white rounded-lg shadow-sm p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              我的回答
            </h2>

            <!-- 空状态 -->
            <div v-if="answerCells.length === 0" class="text-center py-12">
              <div class="text-gray-400 text-5xl mb-3">📝</div>
              <p class="text-gray-600 mb-2">还没有添加任何内容</p>
              <p class="text-sm text-gray-500">从左侧工具栏选择单元类型开始回答</p>
            </div>

            <!-- Cell列表 -->
            <div v-else class="space-y-4">
              <div
                v-for="(cell, index) in answerCells"
                :key="cell.id"
                class="cell-wrapper"
              >
                <!-- Cell容器（复用现有组件） -->
                <CellContainer
                  :cell="cell"
                  :editable="true"
                  @update="(updatedCell) => handleUpdateCell(index, updatedCell)"
                  @delete="handleDeleteCell(index)"
                />

                <!-- Cell之间的添加按钮 -->
                <div class="flex items-center justify-center py-2">
                  <button
                    @click="insertCellAfter(index)"
                    class="px-3 py-1 text-sm text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                  >
                    + 在此添加单元
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 预览模态框 -->
    <PreviewModal
      v-if="showPreview"
      :question="question"
      :answer-cells="answerCells"
      @close="showPreview = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import questionService from '@/services/question'
import CellToolbar from '@/components/Lesson/CellToolbar.vue'
import CellContainer from '@/components/Cell/CellContainer.vue'
import PreviewModal from '@/components/Question/PreviewModal.vue'
import type { QuestionDetail } from '@/types/question'

const route = useRoute()
const router = useRouter()

// 问题ID
const questionId = computed(() => parseInt(route.params.id as string))

// 数据
const question = ref<QuestionDetail | null>(null)
const answerCells = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const saveStatus = ref<'idle' | 'saving' | 'saved' | 'error'>('idle')
const showPreview = ref(false)

// 是否有AI回答
const hasAIAnswer = computed(() => {
  return question.value?.answers?.some(a => a.answerer_type === 'ai') || false
})

// 加载问题详情
const loadQuestion = async () => {
  if (!questionId.value) return

  try {
    loading.value = true
    question.value = await questionService.getQuestionDetail(questionId.value)
  } catch (err: any) {
    console.error('Failed to load question:', err)
    alert('❌ 加载失败：' + err.message)
    goBack()
  } finally {
    loading.value = false
  }
}

// 添加Cell
const handleAddCell = (cellType: string) => {
  const newCell = {
    id: `temp-${Date.now()}-${Math.random()}`,
    cell_type: cellType,
    title: '',
    content: {},
    config: {},
    order: answerCells.value.length
  }
  
  answerCells.value.push(newCell)
  autoSave()
}

// 更新Cell
const handleUpdateCell = (index: number, updatedCell: any) => {
  answerCells.value[index] = updatedCell
  autoSave()
}

// 删除Cell
const handleDeleteCell = (index: number) => {
  if (confirm('确定删除这个单元吗？')) {
    answerCells.value.splice(index, 1)
    autoSave()
  }
}

// 在指定位置后插入Cell
const insertCellAfter = (index: number) => {
  // 简化版：暂时添加一个文本单元
  const newCell = {
    id: `temp-${Date.now()}-${Math.random()}`,
    cell_type: 'text',
    title: '',
    content: {},
    config: {},
    order: index + 1
  }

  answerCells.value.splice(index + 1, 0, newCell)
  autoSave()
}

// 自动保存（防抖）
let autoSaveTimer: ReturnType<typeof setTimeout> | null = null
const autoSave = () => {
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
  }

  saveStatus.value = 'saving'
  
  autoSaveTimer = setTimeout(() => {
    // 保存到localStorage作为草稿
    try {
      localStorage.setItem(`answer-draft-${questionId.value}`, JSON.stringify(answerCells.value))
      saveStatus.value = 'saved'
      setTimeout(() => {
        if (saveStatus.value === 'saved') {
          saveStatus.value = 'idle'
        }
      }, 2000)
    } catch (err) {
      console.error('Auto save failed:', err)
      saveStatus.value = 'error'
    }
  }, 1000)
}

// 加载草稿
const loadDraft = () => {
  try {
    const draft = localStorage.getItem(`answer-draft-${questionId.value}`)
    if (draft) {
      answerCells.value = JSON.parse(draft)
    }
  } catch (err) {
    console.error('Failed to load draft:', err)
  }
}

// 保存草稿
const handleSaveDraft = () => {
  try {
    localStorage.setItem(`answer-draft-${questionId.value}`, JSON.stringify(answerCells.value))
    alert('✅ 草稿已保存')
  } catch (err) {
    alert('❌ 保存失败')
  }
}

// 预览
const handlePreview = () => {
  if (answerCells.value.length === 0) {
    alert('❌ 还没有添加任何内容')
    return
  }
  showPreview.value = true
}

// 查看AI回答
const viewAIAnswer = () => {
  // 跳转到问题详情页查看AI回答
  router.push(`/teacher/questions/${questionId.value}`)
}

// 提交回答
const handleSubmit = async () => {
  if (answerCells.value.length === 0) {
    alert('❌ 请至少添加一个单元')
    return
  }

  if (!confirm('确定提交回答吗？提交后学生即可看到。')) {
    return
  }

  try {
    saving.value = true

    await questionService.createAnswer({
      question_id: questionId.value,
      content: answerCells.value
    })

    // 清除草稿
    localStorage.removeItem(`answer-draft-${questionId.value}`)

    alert('✅ 回答已提交！学生可以看到您的回答了。')
    router.push('/teacher/questions')

  } catch (err: any) {
    console.error('Failed to submit answer:', err)
    alert('❌ 提交失败：' + err.message)
  } finally {
    saving.value = false
  }
}

// 返回
const goBack = () => {
  if (answerCells.value.length > 0 && !confirm('有未提交的内容，确定离开吗？')) {
    return
  }
  router.back()
}

// 格式化日期时间
const formatDateTime = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 组件挂载
onMounted(() => {
  loadQuestion()
  loadDraft()
})

// 组件卸载时清理定时器
onUnmounted(() => {
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
  }
})
</script>

<style scoped>
.cell-wrapper {
  position: relative;
}
</style>

