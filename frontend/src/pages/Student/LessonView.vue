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
            <!-- 🎓 学习科学优化：使用 CellWrapper 组件实现认知脚手架 -->
            <CellWrapper
              v-for="(cell, index) in lesson.content"
              :key="cell.id"
              :cell="cell"
              :cellIndex="index"
              :allCells="lesson.content"
              :completedCellIds="completedCells"
              @complete="markCellAsCompleted"
            >
              <!-- 渲染不同类型的 Cell -->
              <component
                :is="getCellComponent(cell.type)"
                :cell="cell as any"
                :editable="false"
              />
            </CellWrapper>
          </div>

          <!-- 空状态 -->
          <div v-else class="text-center py-12">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="mt-4 text-lg text-gray-600">该课程暂无内容</p>
          </div>

          <!-- 评分评论区域 -->
          <div class="mt-12 mb-8">
            <ReviewSection :lesson-id="lessonId" @updated="handleReviewUpdated" />
          </div>

          <!-- 课程问答区域 -->
          <div class="mt-8 mb-8 border-t border-gray-200 pt-8">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
                课程问答
              </h2>
              <button
                @click="showQuestionForm = true"
                class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                我要提问
              </button>
            </div>

            <!-- 问题列表 -->
            <QuestionList
              :questions="questions"
              :loading="questionsLoading"
              :has-more="hasMoreQuestions"
              @question-click="handleQuestionClick"
              @load-more="loadMoreQuestions"
            />
          </div>
        </div>
      </div>

      <!-- 右侧：学习空间 -->
      <div class="w-96 bg-white shadow-lg border-l border-gray-200 flex flex-col">
        <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              学习空间
            </h2>
            <span class="text-xs text-gray-500">当前进度 {{ progress }}%</span>
          </div>
          <div class="mt-3 flex gap-2">
            <button
              type="button"
              @click="activeSidebarTab = 'notes'"
              :class="[
                'rounded-md px-3 py-1.5 text-sm font-medium transition',
                activeSidebarTab === 'notes'
                  ? 'bg-blue-600 text-white shadow'
                  : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-100'
              ]"
            >
              学习笔记
            </button>
            <button
              type="button"
              @click="activeSidebarTab = 'assistant'"
              :class="[
                'rounded-md px-3 py-1.5 text-sm font-medium transition flex items-center gap-2',
                activeSidebarTab === 'assistant'
                  ? 'bg-gradient-to-r from-[#4C6EF5] to-[#6C8DFF] text-white shadow'
                  : 'bg-white text-[#4C6EF5] border border-[#4C6EF5] hover:bg-[#ECF0FF]'
              ]"
            >
              <svg class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10 2a6 6 0 00-6 6v1.586l-.707.707A1 1 0 004 12h1v1a4 4 0 004 4v1h2v-1a4 4 0 004-4v-1h1a1 1 0 00.707-1.707L16 9.586V8a6 6 0 00-6-6z" />
              </svg>
              AI 助手
            </button>
          </div>
        </div>

        <div class="flex-1 overflow-hidden">
          <div
            v-if="activeSidebarTab === 'notes'"
            class="flex h-full flex-col"
          >
            <div class="flex-1 overflow-y-auto px-6 py-4">
              <textarea
                v-model="notes"
                @input="autoSaveNotes"
                placeholder="在这里记录学习笔记..."
                class="w-full h-full resize-none border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              ></textarea>
            </div>
            <div class="px-6 py-3 border-t border-gray-200 bg-gray-50">
              <div class="flex items-center justify-between text-xs text-gray-500">
                <span v-if="notesSaving">保存中...</span>
                <span v-else-if="notesSaved" class="text-green-600">✓ 已保存</span>
                <span v-else>未保存</span>
                <span>{{ notes.length }} 字符</span>
              </div>
            </div>
          </div>
          <StudentAiAssistantPanel
            v-else
            :lesson-title="lesson?.title || ''"
            :lesson-outline="lessonOutline"
            :progress="progress"
            :lesson-id="lesson?.id"
            @append-note="appendNoteFromAssistant"
          />
        </div>
      </div>
    </div>

    <!-- 提问表单弹窗 -->
    <QuestionForm
      :show="showQuestionForm"
      :lesson-id="lessonId"
      :cells="lesson?.content"
      @close="showQuestionForm = false"
      @success="handleQuestionSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { lessonService } from '@/services/lesson'
import type { Lesson } from '@/types/lesson'
import type { CellType } from '@/types/cell'

// 导入所有 Cell 组件
import TextCell from '@/components/Cell/TextCell.vue'
import CodeCell from '@/components/Cell/CodeCell.vue'
import ParamCell from '@/components/Cell/ParamCell.vue'
import SimCell from '@/components/Cell/SimCell.vue'
import ChartCell from '@/components/Cell/ChartCell.vue'
import ContestCell from '@/components/Cell/ContestCell.vue'
import VideoCell from '@/components/Cell/VideoCell.vue'
import ActivityCell from '@/components/Cell/ActivityCell.vue'
import ReviewSection from '@/components/Resource/ReviewSection.vue'
import QuestionForm from '@/components/Question/QuestionForm.vue'
import QuestionList from '@/components/Question/QuestionList.vue'
import questionService from '@/services/question'
import type { QuestionListItem } from '@/types/question'
// 🎓 学习科学优化：导入认知脚手架组件
import CellWrapper from '@/components/Cell/CellWrapper.vue'
import FlowchartStudentCell from '@/components/Cell/FlowchartStudentCell.vue'
import StudentAiAssistantPanel from '@/components/Student/StudentAiAssistantPanel.vue'

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
const activeSidebarTab = ref<'notes' | 'assistant'>('notes')

// 问答相关状态
const showQuestionForm = ref(false)
const questions = ref<QuestionListItem[]>([])
const questionsLoading = ref(false)
const hasMoreQuestions = ref(false)
const questionsPage = ref(1)

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

const lessonOutline = computed(() => {
  if (!lesson.value?.content) return ''
  return lesson.value.content
    .slice(0, 6)
    .map((cell, index) => summarizeCell(cell, index))
    .filter((item): item is string => Boolean(item))
    .join('\n')
})

// 方法
const getCellComponent = (type: CellType) => {
  const components = {
    text: TextCell,
    code: CodeCell,
    param: ParamCell,
    sim: SimCell,
    chart: ChartCell,
    contest: ContestCell,
    video: VideoCell,
    activity: ActivityCell,
    flowchart: FlowchartStudentCell,
  }
  return components[type] || TextCell
}

const loadLesson = async () => {
  loading.value = true
  error.value = null

  try {
    // 从服务器获取最新教案数据（不使用缓存）
    lesson.value = await lessonService.fetchLessonById(lessonId.value)
    
    // 检查教案版本是否更新
    checkLessonVersionUpdate()
    
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

// 检查教案版本是否更新
const checkLessonVersionUpdate = () => {
  if (!lesson.value) return
  
  const versionKey = `lesson_${lessonId.value}_version`
  const lastKnownVersion = localStorage.getItem(versionKey)
  
  if (lastKnownVersion) {
    const lastVersion = parseInt(lastKnownVersion, 10)
    if (lesson.value.version > lastVersion) {
      // 教案已更新，清除旧的完成状态，让学生重新学习新内容
      const completedCellsKey = `lesson_${lessonId.value}_completed_cells`
      localStorage.removeItem(completedCellsKey)
      completedCells.value = new Set()
      
      // 显示更新提示（可选）
      console.log('教案内容已更新，版本号:', lesson.value.version)
    }
  }
  
  // 保存当前版本号
  localStorage.setItem(versionKey, String(lesson.value.version))
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
    completedCells.value.add(String(cell.id))
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

const stripHtmlTags = (html: string) =>
  html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()

const summarizeCell = (cell: any, index: number): string | null => {
  const orderLabel = `第${index + 1}单元`
  const typeMap: Record<string, string> = {
    text: '文本',
    code: '代码',
    param: '参数',
    sim: '仿真',
    chart: '图表',
    contest: '竞赛',
    video: '视频',
    activity: '活动',
    flowchart: '流程图',
    reference_material: '参考素材',
  }
  const typeLabel = typeMap[cell.type] || '单元'
  let detail = ''

  if (cell.type === 'text' && cell.content?.html) {
    const plain = stripHtmlTags(cell.content.html)
    if (plain) {
      detail = plain.slice(0, 28)
      if (plain.length > 28) detail += '…'
    }
  } else if (cell.type === 'activity' && cell.content?.title) {
    detail = cell.content.title
  } else if (cell.type === 'video' && cell.content?.title) {
    detail = cell.content.title
  }

  const parts = [orderLabel, typeLabel]
  if (detail) {
    parts.push(`：${detail}`)
  }
  return parts.join('')
}

const appendNoteFromAssistant = (content: string) => {
  const cleaned = content.trim()
  if (!cleaned) return
  notes.value = notes.value ? `${notes.value.trim()}\n\n${cleaned}` : cleaned
  autoSaveNotes()
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

const handleReviewUpdated = () => {
  // 评论更新后，可以选择刷新课程数据以更新评分
  // 目前不需要特别处理，因为评分组件自己管理状态
  console.log('Review updated')
}

// 问答相关方法
const loadQuestions = async () => {
  if (questionsLoading.value) return
  
  try {
    questionsLoading.value = true
    const response = await questionService.getLessonQuestions(lessonId.value, {
      sort: 'recent',
      page: questionsPage.value,
      page_size: 10
    })
    
    questions.value = response.items
    hasMoreQuestions.value = response.has_more
  } catch (err: any) {
    console.error('Failed to load questions:', err)
  } finally {
    questionsLoading.value = false
  }
}

const loadMoreQuestions = async () => {
  if (!hasMoreQuestions.value || questionsLoading.value) return
  
  questionsPage.value++
  try {
    questionsLoading.value = true
    const response = await questionService.getLessonQuestions(lessonId.value, {
      sort: 'recent',
      page: questionsPage.value,
      page_size: 10
    })
    
    questions.value = [...questions.value, ...response.items]
    hasMoreQuestions.value = response.has_more
  } catch (err: any) {
    console.error('Failed to load more questions:', err)
  } finally {
    questionsLoading.value = false
  }
}

const handleQuestionClick = (questionId: number) => {
  router.push(`/student/question/${questionId}`)
}

const handleQuestionSuccess = (_questionId: number) => {
  // 提问成功后重新加载问题列表
  questionsPage.value = 1
  loadQuestions()
  // 可选：跳转到问题详情页
  // router.push(`/student/question/${_questionId}`)
}

// 生命周期
onMounted(() => {
  loadLesson()
  loadQuestions()
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
/* 🎓 学习科学优化：样式已移至 CellWrapper.vue 组件中 */
</style>
