<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center min-h-screen">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <p class="mt-4 text-gray-600">加载中...</p>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="flex items-center justify-center min-h-screen">
      <div class="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
        <p class="text-red-600 mb-4">{{ error }}</p>
        <button
          @click="router.back()"
          class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
        >
          返回
        </button>
      </div>
    </div>

    <!-- 主要内容 -->
    <div v-else-if="lesson" class="flex h-screen">
      <!-- 左侧：课程内容 -->
      <div class="flex-1 overflow-y-auto">
        <!-- 顶部导航栏 -->
        <header class="bg-white shadow-sm sticky top-0 z-10">
          <div class="px-6 py-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-4">
                <button
                  @click="router.push('/student')"
                  class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  title="返回"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                  </svg>
                </button>
                <div>
                  <h1 class="text-xl font-bold text-gray-900">{{ lesson.title }}</h1>
                  <p class="text-sm text-gray-500 mt-1">
                    <span v-if="lesson.course">{{ lesson.course.name }}</span>
                    <span v-if="lesson.chapter"> / {{ lesson.chapter.name }}</span>
                  </p>
                </div>
              </div>
              <div class="flex items-center gap-4">
                <!-- 学习进度 -->
                <div class="flex items-center gap-2">
                  <span class="text-sm text-gray-600">学习进度:</span>
                  <span class="text-sm font-semibold text-blue-600">{{ progress }}%</span>
                </div>
                <!-- 完成按钮 -->
                <button
                  v-if="progress < 100"
                  @click="markAsCompleted"
                  class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm"
                >
                  标记为完成
                </button>
                <div v-else class="flex items-center gap-2 text-green-600">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span class="text-sm font-semibold">已完成</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        <!-- 课程描述 -->
        <div v-if="lesson.description" class="bg-blue-50 border-l-4 border-blue-500 px-6 py-4">
          <p class="text-gray-700">{{ lesson.description }}</p>
        </div>

        <!-- Cell 内容 -->
        <div class="px-6 py-8 max-w-5xl">
          <div v-if="lesson.content && lesson.content.length > 0" class="space-y-6">
            <div
              v-for="(cell, index) in lesson.content"
              :key="cell.id"
              :class="['cell-wrapper', { 'completed': completedCells.has(cell.id) }]"
            >
              <!-- Cell 头部：显示序号和完成状态 -->
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-gray-500">单元 {{ index + 1 }}</span>
                  <span v-if="cell.title" class="text-sm text-gray-600">- {{ cell.title }}</span>
                </div>
                <button
                  v-if="!completedCells.has(cell.id)"
                  @click="markCellAsCompleted(cell.id)"
                  class="text-xs px-3 py-1 text-green-600 border border-green-600 rounded hover:bg-green-50"
                >
                  标记完成
                </button>
                <div v-else class="flex items-center gap-1 text-green-600 text-xs">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  已完成
                </div>
              </div>

              <!-- 渲染不同类型的 Cell -->
              <component
                :is="getCellComponent(cell.type)"
                :cell="cell"
                :editable="false"
              />
            </div>
          </div>

          <!-- 空状态 -->
          <div v-else class="text-center py-12">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="mt-4 text-lg text-gray-600">该课程暂无内容</p>
          </div>
        </div>
      </div>

      <!-- 右侧：笔记面板 -->
      <div class="w-96 bg-white shadow-lg border-l border-gray-200 flex flex-col">
        <!-- 笔记头部 -->
        <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            学习笔记
          </h2>
        </div>

        <!-- 笔记内容 -->
        <div class="flex-1 overflow-y-auto px-6 py-4">
          <textarea
            v-model="notes"
            @input="autoSaveNotes"
            placeholder="在这里记录学习笔记..."
            class="w-full h-full resize-none border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          ></textarea>
        </div>

        <!-- 笔记底部：保存状态 -->
        <div class="px-6 py-3 border-t border-gray-200 bg-gray-50">
          <div class="flex items-center justify-between text-xs text-gray-500">
            <span v-if="notesSaving">保存中...</span>
            <span v-else-if="notesSaved" class="text-green-600">✓ 已保存</span>
            <span v-else>未保存</span>
            <span>{{ notes.length }} 字符</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { lessonService } from '@/services/lesson'
import type { Lesson } from '@/types/lesson'
import type { Cell, CellType } from '@/types/cell'

// 导入所有 Cell 组件
import TextCell from '@/components/Cell/TextCell.vue'
import CodeCell from '@/components/Cell/CodeCell.vue'
import ParamCell from '@/components/Cell/ParamCell.vue'
import SimCell from '@/components/Cell/SimCell.vue'
import QACell from '@/components/Cell/QACell.vue'
import ChartCell from '@/components/Cell/ChartCell.vue'
import ContestCell from '@/components/Cell/ContestCell.vue'

const route = useRoute()
const router = useRouter()

// 状态
const loading = ref(false)
const error = ref<string | null>(null)
const lesson = ref<Lesson | null>(null)
const completedCells = ref<Set<string>>(new Set())
const notes = ref('')
const notesSaving = ref(false)
const notesSaved = ref(false)

// 自动保存定时器
let notesAutoSaveTimer: ReturnType<typeof setTimeout> | null = null

// 计算属性
const lessonId = computed(() => Number(route.params.id))

const progress = computed(() => {
  if (!lesson.value?.content || lesson.value.content.length === 0) {
    return 0
  }
  const completed = completedCells.value.size
  const total = lesson.value.content.length
  return Math.round((completed / total) * 100)
})

// 方法
const getCellComponent = (type: CellType) => {
  const components = {
    text: TextCell,
    code: CodeCell,
    param: ParamCell,
    sim: SimCell,
    qa: QACell,
    chart: ChartCell,
    contest: ContestCell,
  }
  return components[type] || TextCell
}

const loadLesson = async () => {
  loading.value = true
  error.value = null

  try {
    lesson.value = await lessonService.fetchLessonById(lessonId.value)
    
    // 加载该课程的完成状态
    loadCompletedCells()
    loadNotes()
  } catch (e: any) {
    error.value = e.message || '加载课程失败'
    console.error('Failed to load lesson:', e)
  } finally {
    loading.value = false
  }
}

const loadCompletedCells = () => {
  const key = `lesson_${lessonId.value}_completed_cells`
  const saved = localStorage.getItem(key)
  if (saved) {
    try {
      const cellIds = JSON.parse(saved)
      completedCells.value = new Set(cellIds)
    } catch (e) {
      console.error('Failed to load completed cells:', e)
    }
  }
}

const saveCompletedCells = () => {
  const key = `lesson_${lessonId.value}_completed_cells`
  const cellIds = Array.from(completedCells.value)
  localStorage.setItem(key, JSON.stringify(cellIds))
  
  // 更新总体学习进度
  updateLessonProgress()
}

const markCellAsCompleted = (cellId: string) => {
  completedCells.value.add(cellId)
  saveCompletedCells()
}

const markAsCompleted = () => {
  if (!lesson.value?.content) return
  
  // 标记所有 Cell 为完成
  lesson.value.content.forEach(cell => {
    completedCells.value.add(cell.id)
  })
  
  saveCompletedCells()
}

const updateLessonProgress = () => {
  const key = 'student_lesson_progress'
  const saved = localStorage.getItem(key)
  let progressData: Record<number, number> = {}
  
  if (saved) {
    try {
      progressData = JSON.parse(saved)
    } catch (e) {
      console.error('Failed to load progress data:', e)
    }
  }
  
  progressData[lessonId.value] = progress.value
  localStorage.setItem(key, JSON.stringify(progressData))
}

const loadNotes = () => {
  const key = `lesson_${lessonId.value}_notes`
  const saved = localStorage.getItem(key)
  if (saved) {
    notes.value = saved
  }
}

const saveNotes = () => {
  const key = `lesson_${lessonId.value}_notes`
  localStorage.setItem(key, notes.value)
  notesSaved.value = true
  notesSaving.value = false
  
  // 3秒后隐藏"已保存"提示
  setTimeout(() => {
    notesSaved.value = false
  }, 3000)
}

const autoSaveNotes = () => {
  notesSaved.value = false
  notesSaving.value = true
  
  // 清除之前的定时器
  if (notesAutoSaveTimer) {
    clearTimeout(notesAutoSaveTimer)
  }
  
  // 1秒后自动保存
  notesAutoSaveTimer = setTimeout(() => {
    saveNotes()
  }, 1000)
}

// 生命周期
onMounted(() => {
  loadLesson()
})

onUnmounted(() => {
  // 组件卸载时保存笔记
  if (notes.value) {
    saveNotes()
  }
  
  // 清理定时器
  if (notesAutoSaveTimer) {
    clearTimeout(notesAutoSaveTimer)
  }
})
</script>

<style scoped>
.cell-wrapper {
  @apply bg-white rounded-lg shadow-sm border border-gray-200 p-6 transition-all;
}

.cell-wrapper:hover {
  @apply shadow-md border-blue-200;
}

.cell-wrapper.completed {
  @apply border-green-200 bg-green-50;
}
</style>
