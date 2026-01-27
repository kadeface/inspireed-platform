<template>
  <div class="activity-viewer">
    <!-- 注意：已移除离线模式和自动同步相关UI（简化版） -->

    <!-- 活动标题和信息 -->
    <div class="activity-header">
      <h2 class="activity-title">{{ cell.content.title }}</h2>
      <p v-if="cell.content.description" class="activity-description">
        {{ cell.content.description }}
      </p>

      <!-- 活动信息卡片 -->
      <div class="info-cards">
        <div class="info-card">
          <span class="info-label">类型</span>
          <span class="info-value">{{ activityTypeLabel }}</span>
        </div>
        <div v-if="cell.content.grading.enabled" class="info-card">
          <span class="info-label">总分</span>
          <span class="info-value">{{ cell.content.grading.totalPoints }}分</span>
        </div>
        <div v-if="cell.content.timing.duration" class="info-card">
          <span class="info-label">时长</span>
          <span class="info-value">{{ cell.content.timing.duration }}分钟</span>
        </div>
        <div class="info-card">
          <span class="info-label">题目数</span>
          <span class="info-value">{{ cell.content.items.length }}题</span>
        </div>
      </div>

      <!-- 问卷专用提示 -->
      <p v-if="props.cell.content.activityType === 'survey'" class="survey-hint">
        📊 当前为问卷活动：仅用于收集和统计学生反馈，不计入分数。
      </p>

      <!-- 截止时间提示 -->
      <div v-if="cell.content.timing.deadline" class="deadline-alert">
        ⏰ 截止时间: {{ formatDeadline(cell.content.timing.deadline) }}
      </div>
    </div>

    <!-- 进度条 -->
    <div v-if="cell.content.display.showProgress" class="progress-section">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
      </div>
      <p class="progress-text">
        已完成 {{ answeredCount }} / {{ cell.content.items.length }} 题 ({{ progress }}%)
      </p>
    </div>

    <!-- 题目列表 -->
    <div class="items-section">
      <div
        v-for="(item, index) in cell.content.items"
        :key="item.id"
        class="item-container"
      >
        <div class="item-header">
          <span class="item-number">{{ index + 1 }}.</span>
          <span class="item-type-badge">{{ getItemTypeLabel(item.type) }}</span>
          <span v-if="item.required" class="required-badge">必答</span>
          <span v-if="item.points" class="points-badge">{{ item.points }}分</span>
        </div>

        <div class="item-question">{{ item.question }}</div>

        <!-- 根据题型渲染不同的答题组件 -->
        <div class="item-answer">
          <ItemRenderer
            :item="item"
            v-model="answers[item.id]"
            :is-submitted="isSubmitted"
            :answer-data="getItemAnswer(item.id)"
            @update:model-value="answers[item.id] = $event"
          />
        </div>
      </div>
    </div>

    <!-- 提交按钮 -->
    <div class="submit-section">
      <button v-if="!isSubmitted" @click="handleSubmit" class="btn-primary" :disabled="!canSubmit || submitting">
        {{ submitting ? '提交中...' : '✅ 提交答案' }}
      </button>
      <div v-else class="submitted-info">
        <div class="submitted-badge">✓ 已提交</div>
        <div v-if="submissionData?.score !== undefined && submissionData?.maxScore !== undefined" class="score-display">
          总分：{{ submissionData.score }} / {{ submissionData.maxScore }} 分
        </div>
      </div>
    </div>

    <!-- 提示信息 -->
    <div v-if="!canSubmit" class="alert-warning">
      ⚠️ 请完成所有必答题后再提交
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '../../store/user'
import type { ActivityCell } from '../../types/cell'
import type { ActivityItemType } from '../../types/activity'
import activityService from '../../services/activity'
import { useCellIdResolver } from '../../composables/useCellIdResolver'
import { useActivityState } from '../../composables/useActivityState'
import { useActivitySubmission } from '../../composables/useActivitySubmission'
import { useOfflineActivity } from '../../composables/useOfflineActivity'
import ItemRenderer from './ItemTypes/ItemRenderer.vue'

interface Props {
  cell: ActivityCell
  lessonId?: number  // 从父组件传递 lessonId
  sessionId?: number  // 课堂会话ID（课堂模式必须传递）
}

const props = withDefaults(defineProps<Props>(), {
  lessonId: undefined,
  sessionId: undefined,
})


// 🔧 本地保存 sessionId（因为 props.sessionId 可能在组件加载时还是 undefined）
const localSessionId = ref<number | undefined>(props.sessionId)

// 监听 props.sessionId 变化，更新本地状态
watch(() => props.sessionId, (newSessionId) => {
  if (newSessionId !== undefined) {
    localSessionId.value = newSessionId
  }
}, { immediate: true })

// 🔧 动态获取最新的 sessionId
const currentSessionId = computed(() => {
  return localSessionId.value
})

const emit = defineEmits<{
  submit: [data: any]
}>()

const route = useRoute()
const userStore = useUserStore()

// 从用户 store 获取当前学生 ID
const currentStudentId = computed(() => {
  return userStore.user?.id || 1
})

// 从 props 或 route 获取 lessonId
const lessonId = computed(() => {
  if (props.lessonId !== undefined) {
    return props.lessonId
  }
  // 从路由参数获取（适用于 LessonView 页面）
  const routeLessonId = route.params.id
  if (routeLessonId) {
    return Number(routeLessonId)
  }
  // 如果都没有，尝试从 lesson store 获取
  console.warn('⚠️ lessonId not found, using fallback value 1')
  return 1
})

// 使用 composables 管理状态
const cellIdResolver = useCellIdResolver({
  cell: props.cell,
  lessonId: lessonId.value,
})

const activityState = useActivityState({
  cell: props.cell,
})

// 解构状态（注意：answeredCount, progress, canSubmit, getItemAnswer 已经在 composable 中定义）
const {
  answers,
  isSubmitted,
  submissionData,
  submitting,
  startTime,
  submissionId,
  answeredCount,
  progress,
  canSubmit,
  getItemAnswer,
  setAnswers,
  setSubmitted,
  setSubmissionId,
  setSubmitting,
} = activityState

// 初始化提交管理（需要等待 cellId 解析完成）
let activitySubmission: ReturnType<typeof useActivitySubmission> | null = null

// 安全地解析 cellId
// 注意：如果 cell.id 是 UUID，我们需要通过 API 查找对应的数字 ID
async function resolveCellId(cellId: number | string | undefined): Promise<number> {
  if (typeof cellId === 'number') {
    if (isNaN(cellId)) {
      console.error('❌ cellId is NaN')
      throw new Error('cellId is NaN')
    }
    return cellId
  }
  
  if (typeof cellId === 'string') {
    // 尝试解析为数字
    const parsed = parseInt(cellId, 10)
    if (!isNaN(parsed)) {
      return parsed
    }
    
    // 如果是 UUID 格式，需要通过 API 查找
    // UUID 格式: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
    if (uuidPattern.test(cellId)) {
      // 如果 cell.id 是 UUID，尝试从 lesson 的 content 中找到对应的 cell
      // 这需要从父组件或 context 获取 lesson 数据
      // 暂时抛出错误，提示需要实现 UUID 到数字 ID 的映射
      throw new Error(`Cell ID is UUID (${cellId}), but numeric ID is required. Please check lesson content for cell mapping.`)
    }
    
    console.error('❌ Invalid cellId string:', cellId)
    throw new Error(`Invalid cellId: ${cellId}`)
  }
  
  console.error('❌ cellId is undefined or null', { cellId, cell: props.cell })
  throw new Error('cellId is required')
}

// 存储 UUID 到数字 ID 的映射
const cellIdMap = ref<Map<string, number>>(new Map())
const resolvingCellId = ref(false)

// 通过 API 解析 UUID 到数字 ID
// 如果 cells 只存在于 lesson.content 中（不在独立的 cells 表中），我们需要创建 cell 记录
async function resolveCellIdFromApi(uuid: string): Promise<number | null> {
  if (cellIdMap.value.has(uuid)) {
    return cellIdMap.value.get(uuid) || null
  }

  if (resolvingCellId.value) {
    // 如果正在解析，等待一下
    await new Promise(resolve => setTimeout(resolve, 100))
    return cellIdMap.value.get(uuid) || null
  }

  try {
    resolvingCellId.value = true
    
    // 首先尝试从 API 获取 lesson 的所有 cells
    const { api } = await import('../../services/api')
    let response
    try {
      response = await api.get(`/cells/lesson/${lessonId.value}`)
    } catch (error: any) {
      console.warn('⚠️ Failed to fetch cells from API, will try to create cell:', error)
      response = { data: [] }
    }
    
    const cells = response.data || []
    
    // 尝试通过 order 和 type 匹配 cell
    const currentCellOrder = props.cell.order
    const currentCellType = props.cell.type
    
    // 首先尝试精确匹配：order 和 type 都匹配
    let matchedCell = cells.find((c: any) => {
      return c.order === currentCellOrder && c.cell_type === currentCellType
    })
    
    // 如果精确匹配失败，尝试只匹配 order
    if (!matchedCell) {
      matchedCell = cells.find((c: any) => {
        return c.order === currentCellOrder
      })
    }
    
    // 如果还是找不到，尝试通过 title 匹配
    if (!matchedCell && props.cell.title) {
      matchedCell = cells.find((c: any) => {
        return c.title === props.cell.title && c.cell_type === currentCellType
      })
    }
    
    if (matchedCell && matchedCell.id) {
      const numericId = typeof matchedCell.id === 'number' ? matchedCell.id : parseInt(matchedCell.id, 10)
      if (!isNaN(numericId)) {
        cellIdMap.value.set(uuid, numericId)
        return numericId
      }
    }
    
    // 如果找不到匹配的 cell，尝试创建一个新的 cell 记录
    try {
      const cellCreateData = {
        lesson_id: lessonId.value,
        cell_type: currentCellType,
        title: props.cell.title || '',
        content: props.cell.content || {},
        config: props.cell.config || {},
        order: currentCellOrder,
        editable: props.cell.editable ?? false,
      }
      
      const createResponse = await api.post('/cells', cellCreateData) as any
      const newCell = createResponse.data
      
      if (newCell && newCell.id) {
        const numericId = typeof newCell.id === 'number' ? newCell.id : parseInt(newCell.id, 10)
        if (!isNaN(numericId)) {
          cellIdMap.value.set(uuid, numericId)
          return numericId
        }
      }
    } catch (createError: any) {
      console.error('Failed to create cell:', createError)
    }
    
    return null
  } catch (error: any) {
    console.error('Failed to resolve cell ID from API:', error)
    return null
  } finally {
    resolvingCellId.value = false
  }
}

// 计算 cellId（异步解析版本）
const cellId = ref<number>(0)

// 初始化时解析 cellId
// 注意：后端现在支持 UUID 字符串，所以如果无法解析为数字，我们可以直接使用 UUID
async function initCellId() {
  const id = props.cell.id
  
  if (typeof id === 'number') {
    if (!isNaN(id)) {
      cellId.value = id
      return
    }
  }
  
  if (typeof id === 'string') {
    const parsed = parseInt(id, 10)
    if (!isNaN(parsed)) {
      cellId.value = parsed
      return
    }
    
    // 如果是 UUID，后端现在支持直接使用 UUID
    const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
    if (uuidPattern.test(id)) {
      // 使用 0 作为标记，表示需要使用 UUID
      cellId.value = 0
      // 存储原始 UUID
      ;(cellId as any).uuid = id
      return
    }
    
    console.error('Invalid cellId string (not UUID and not numeric):', id)
  }
  
  console.error('Invalid cellId:', id)
  cellId.value = 0
}

// 获取实际的 cellId（可能是数字或 UUID 字符串）
function getActualCellId(): number | string {
  if (cellId.value === 0 && (cellId as any).uuid) {
    return (cellId as any).uuid
  }
  return cellId.value
}

// 离线支持（延迟初始化，等待 cellId 解析完成）
let offlineActivity: ReturnType<typeof useOfflineActivity> | null = null

// 初始化离线支持
function initOfflineActivity() {
  const actualCellId = getActualCellId()
  // 对于 UUID，我们使用一个基于 UUID 的哈希值作为临时数字 ID（仅用于 IndexedDB key）
  let cellIdForStorage: number
  if (typeof actualCellId === 'string') {
    // 使用 UUID 的前 8 个字符的哈希值作为临时数字 ID
    const hash = actualCellId.split('-')[0]
    cellIdForStorage = parseInt(hash, 16) % 1000000  // 转换为 0-999999 的数字
  } else {
    cellIdForStorage = actualCellId
  }
  
  if (cellIdForStorage > 0 && !offlineActivity) {
    offlineActivity = useOfflineActivity(
      cellIdForStorage,
      lessonId.value,
      currentStudentId.value
    )
  }
  return offlineActivity
}

// 计算属性包装
const isOnline = computed(() => initOfflineActivity()?.isOnline.value ?? ref(navigator.onLine).value)
const isSyncing = computed(() => initOfflineActivity()?.isSyncing.value ?? ref(false).value)
const hasUnsyncedChanges = computed(() => initOfflineActivity()?.hasUnsyncedChanges.value ?? ref(false).value)
const loadFromIndexedDB = async () => {
  const activity = initOfflineActivity()
  return activity ? await activity.loadFromIndexedDB() : null
}
// 注意：已移除 syncToServer、setupAutoSave 等自动保存相关函数
// 简化版只支持点击提交按钮时一次性提交

// 计算属性
const activityTypeLabel = computed(() => {
  const labels = {
    quiz: '测验',
    survey: '问卷',
    assignment: '作业',
    rubric: '评价量表',
    mixed: '混合活动',
  }
  return labels[props.cell.content.activityType]
})

// 注意：answeredCount, progress, canSubmit, getItemAnswer 已经在 useActivityState 中定义，不需要重复定义

// 方法
function getItemTypeLabel(type: ActivityItemType): string {
  const labels: Record<ActivityItemType, string> = {
    'single-choice': '单选',
    'multiple-choice': '多选',
    'true-false': '判断',
    'short-answer': '简答',
    'long-answer': '论述',
    'file-upload': '上传',
    'code-submission': '编程',
    'scale': '量表',
    'rubric-item': '评价',
  }
  return labels[type]
}

function formatDeadline(deadline: string): string {
  return new Date(deadline).toLocaleString('zh-CN')
}

// 注意：已移除自动保存和草稿保存功能，只在点击提交按钮时一次性提交

// 提交答案（简化版：直接提交，不保存草稿）
async function handleSubmit() {
  if (!canSubmit.value) {
    alert('请完成所有必答题')
    return
  }

  // ✅ 直接使用 props.cell.id（UUID 或数字），让后端处理映射
  // 从 lesson.content 来的 cell，id 应该是 UUID；从数据库 API 来的，id 是数字
  const cellIdToSubmit = props.cell.id
  
  console.log('🔍 ActivityViewer 准备提交:', {
    cellIdToSubmit,
    cellIdType: typeof cellIdToSubmit,
    isUUID: typeof cellIdToSubmit === 'string' && /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(cellIdToSubmit),
    cellObject: props.cell,
    cellIdFromCell: props.cell.id,
  })
  
  if (!cellIdToSubmit) {
    console.error('❌ Invalid cellId: cell.id is empty', props.cell)
    alert('无法提交：Cell ID 无效。请刷新页面重试。')
    return
  }

  if (!confirm('确定要提交吗？提交后将无法修改。')) {
    return
  }

  try {
    submitting.value = true
    
    const timeSpent = Math.floor((new Date().getTime() - startTime.value.getTime()) / 1000)
    
    // 获取当前最新的 sessionId
    const sessionIdToUse = currentSessionId.value
    
    // ✅ 方案2：在课堂模式下，确保总是传递 session_id
    // 判断是否在课堂模式：如果 sessionIdToUse 有值，说明在课堂模式
    const isInClassroomMode = sessionIdToUse !== undefined
    
    // 如果 localSessionId 曾经被设置过（不是初始的 undefined），但现在又是 undefined
    // 说明可能在课堂模式但 sessionId 丢失了，这种情况应该阻止提交
    // 注意：localSessionId 初始值是 props.sessionId，如果 props.sessionId 是 undefined，localSessionId 也是 undefined
    // 但如果 props.sessionId 曾经有值，localSessionId 也会有值
    const hadSessionIdBefore = localSessionId.value !== undefined
    
    if (hadSessionIdBefore && sessionIdToUse === undefined) {
      // 曾经有 sessionId 但现在丢失了，可能是课堂模式但 sessionId 异常
      console.error('课堂模式下 sessionId 丢失，无法提交')
      alert('无法提交：课堂会话信息异常。请刷新页面重试。\n\n这可以确保提交记录正确关联到当前课堂会话，避免统计混乱。')
      submitting.value = false
      return
    }
    
    // 确保 answers 不是空对象
    if (!answers.value || Object.keys(answers.value).length === 0) {
      alert('请先完成答题再提交')
      return
    }
    
    // 使用合并API：一步完成创建和提交
    const submittedSubmission = await activityService.createAndSubmit({
      cellId: cellIdToSubmit as any,  // ✅ 直接传递 UUID 后端会处理映射
      lessonId: lessonId.value,
      sessionId: sessionIdToUse,  // 使用动态获取的 sessionId
      responses: answers.value,
      startedAt: startTime.value.toISOString(),
      timeSpent,
    })
    
    // 保存提交后的数据（包含正确答案）
    submissionData.value = submittedSubmission
    submissionId.value = submittedSubmission.id
    isSubmitted.value = true
    
    // 更新 answers 为包含正确答案的完整数据
    if (submittedSubmission.responses) {
      answers.value = submittedSubmission.responses
    }
    
    alert('提交成功！')
    emit('submit', { responses: answers.value, timeSpent })
  } catch (error: any) {
    console.error('Submit failed:', error)
    alert(`提交失败：${error?.response?.data?.detail || error?.message || '请重试'}`)
  } finally {
    submitting.value = false
  }
}

// 加载已提交的答案（仅检查是否已经提交过，不加载草稿）
onMounted(async () => {
  // 首先解析 cellId（如果是 UUID）
  await initCellId()
  
  // 如果在线，检查是否已经提交过（只加载已提交的内容，不加载草稿）
  if (isOnline.value) {
    try {
      const actualCellId = getActualCellId()
      if (typeof actualCellId === 'number' && actualCellId > 0) {
        const submission = await activityService.getMyCellSubmission(actualCellId)
        
        if (submission) {
          // 只加载已提交或已评分的内容（不加载草稿）
          if (submission.status === 'submitted' || submission.status === 'graded') {
            submissionId.value = submission.id
            answers.value = submission.responses || {}
            isSubmitted.value = true
            submissionData.value = submission
          }
        }
      }
    } catch (error: any) {
      // 404 错误是正常的（表示还没有提交），静默处理，不输出日志
      if (error.response?.status === 404) {
        // 静默处理，不输出日志（这是正常情况：学生还没有提交）
        return
      }
      // 其他错误才需要记录
      console.error('Failed to load submission from server:', error)
    }
  }
})

// 组件卸载时清理
onUnmounted(() => {
  // 已移除自动保存清理逻辑
})
</script>

<style scoped>
.activity-viewer {
  @apply max-w-4xl mx-auto;
}

.status-banner {
  @apply mb-6;
}

.offline-banner {
  @apply px-4 py-3 bg-orange-50 border border-orange-200 rounded-lg text-orange-800 flex items-center gap-2;
}

.unsync-banner {
  @apply px-4 py-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800 flex items-center gap-2;
}

.syncing-banner {
  @apply px-4 py-3 bg-blue-50 border border-blue-200 rounded-lg text-blue-800 flex items-center gap-2;
}

.activity-header {
  @apply mb-8 pb-6 border-b border-gray-200;
}

.activity-title {
  @apply text-3xl font-bold text-gray-900 mb-3;
}

.activity-description {
  @apply text-gray-600 mb-4;
}

.info-cards {
  @apply flex flex-wrap gap-4 mb-4;
}

.info-card {
  @apply flex flex-col px-4 py-2 bg-blue-50 rounded-lg;
}

.info-label {
  @apply text-xs text-gray-500;
}

.info-value {
  @apply text-sm font-semibold text-gray-900;
}

.deadline-alert {
  @apply px-4 py-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800;
}

.progress-section {
  @apply mb-8;
}

.progress-bar {
  @apply w-full h-3 bg-gray-200 rounded-full overflow-hidden;
}

.progress-fill {
  @apply h-full bg-blue-600 transition-all duration-300;
}

.progress-text {
  @apply text-sm text-gray-600 mt-2;
}

.items-section {
  @apply space-y-8;
}

.item-container {
  @apply bg-white border border-gray-200 rounded-lg p-6;
}

.item-header {
  @apply flex items-center gap-2 mb-3;
}

.item-number {
  @apply text-lg font-bold text-gray-900;
}

.item-type-badge {
  @apply px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded;
}

.required-badge {
  @apply px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded;
}

.points-badge {
  @apply px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded;
}

.item-question {
  @apply text-lg text-gray-900 mb-4 font-medium;
}

.item-answer {
  @apply pl-6;
}

.submitted-info {
  @apply flex items-center gap-4;
}

.submitted-badge {
  @apply px-4 py-2 bg-green-100 text-green-800 font-semibold rounded-lg;
}

.score-display {
  @apply text-lg font-semibold text-gray-900;
}

.survey-hint {
  @apply mt-2 text-sm text-gray-600 italic;
}


.submit-section {
  @apply flex justify-end gap-4 mt-8 pt-6 border-t border-gray-200;
}

.btn-primary {
  @apply px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-secondary {
  @apply px-6 py-3 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.alert-warning {
  @apply mt-4 px-4 py-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800 text-center;
}
</style>

