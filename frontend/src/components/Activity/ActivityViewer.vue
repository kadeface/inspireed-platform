<template>
  <div class="activity-viewer">
    <!-- 在线状态指示器 -->
    <div v-if="!isOnline || hasUnsyncedChanges" class="status-banner">
      <div v-if="!isOnline" class="offline-banner">
        📱 离线模式 - 您的答案将保存在本地，联网后自动同步
      </div>
      <div v-else-if="hasUnsyncedChanges && !isSyncing" class="unsync-banner">
        ⚠️ 有未同步的更改 - 正在自动同步...
      </div>
      <div v-else-if="isSyncing" class="syncing-banner">
        🔄 同步中...
      </div>
    </div>

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
          <!-- 单选题 -->
          <div v-if="item.type === 'single-choice'" class="space-y-2">
            <label
              v-for="option in item.config.options"
              :key="option.id"
              class="option-label"
              :class="{
                'option-correct': isSubmitted && isCorrectAnswerForSingle(item.id, option.id),
                'option-selected': answers[item.id] === option.id,
                'option-wrong': isSubmitted && answers[item.id] === option.id && !getItemAnswer(item.id)?.correct
              }"
            >
              <input
                v-model="answers[item.id]"
                type="radio"
                :value="option.id"
                :name="`item-${item.id}`"
                :disabled="isSubmitted"
                @change="saveAnswer(item.id)"
              />
              <span>{{ option.text }}</span>
              <span v-if="isSubmitted && isCorrectAnswerForSingle(item.id, option.id)" class="correct-badge">✓ 正确答案</span>
            </label>
            <!-- 反馈信息 -->
            <div v-if="isSubmitted && getItemAnswer(item.id)" class="feedback-info">
              <div v-if="getItemAnswer(item.id)?.correct" class="feedback-correct">
                ✓ 回答正确！正确答案：{{ getItemAnswer(item.id)?.correctAnswer }}
              </div>
              <div v-else class="feedback-wrong">
                ✗ 回答错误。正确答案：{{ getItemAnswer(item.id)?.correctAnswer }}
              </div>
              <div v-if="getItemAnswer(item.id)?.score !== undefined" class="feedback-score">
                得分：{{ getItemAnswer(item.id)?.score }} / {{ item.points || 0 }} 分
              </div>
            </div>
          </div>

          <!-- 多选题 -->
          <div v-if="item.type === 'multiple-choice'" class="space-y-2">
            <label
              v-for="option in item.config.options"
              :key="option.id"
              class="option-label"
              :class="{
                'option-correct': isSubmitted && isCorrectAnswer(item.id, option.id),
                'option-selected': Array.isArray(answers[item.id]) && answers[item.id].includes(option.id),
                'option-wrong': isSubmitted && Array.isArray(answers[item.id]) && answers[item.id].includes(option.id) && !isCorrectAnswer(item.id, option.id)
              }"
            >
              <input
                v-model="answers[item.id]"
                type="checkbox"
                :value="option.id"
                :disabled="isSubmitted"
                @change="saveAnswer(item.id)"
              />
              <span>{{ option.text }}</span>
              <span v-if="isSubmitted && isCorrectAnswer(item.id, option.id)" class="correct-badge">✓ 正确答案</span>
            </label>
            <!-- 反馈信息 -->
            <div v-if="isSubmitted && getItemAnswer(item.id)" class="feedback-info">
              <div v-if="getItemAnswer(item.id)?.correct" class="feedback-correct">
                ✓ 回答正确！正确答案：{{ getItemAnswer(item.id)?.correctAnswer }}
              </div>
              <div v-else class="feedback-wrong">
                ✗ 回答错误。正确答案：{{ getItemAnswer(item.id)?.correctAnswer }}
              </div>
              <div v-if="getItemAnswer(item.id)?.score !== undefined" class="feedback-score">
                得分：{{ getItemAnswer(item.id)?.score }} / {{ item.points || 0 }} 分
              </div>
            </div>
          </div>

          <!-- 判断题 -->
          <div v-if="item.type === 'true-false'" class="space-y-2">
            <label class="option-label" :class="{
              'option-correct': isSubmitted && getItemAnswer(item.id)?.correctAnswer === '正确' && answers[item.id] === true,
              'option-selected': answers[item.id] === true,
              'option-wrong': isSubmitted && answers[item.id] === true && !getItemAnswer(item.id)?.correct
            }">
              <input
                v-model="answers[item.id]"
                type="radio"
                :value="true"
                :name="`item-${item.id}`"
                :disabled="isSubmitted"
                @change="saveAnswer(item.id)"
              />
              <span>正确</span>
            </label>
            <label class="option-label" :class="{
              'option-correct': isSubmitted && getItemAnswer(item.id)?.correctAnswer === '错误' && answers[item.id] === false,
              'option-selected': answers[item.id] === false,
              'option-wrong': isSubmitted && answers[item.id] === false && !getItemAnswer(item.id)?.correct
            }">
              <input
                v-model="answers[item.id]"
                type="radio"
                :value="false"
                :name="`item-${item.id}`"
                :disabled="isSubmitted"
                @change="saveAnswer(item.id)"
              />
              <span>错误</span>
            </label>
            <!-- 反馈信息 -->
            <div v-if="isSubmitted && getItemAnswer(item.id)" class="feedback-info">
              <div v-if="getItemAnswer(item.id)?.correct" class="feedback-correct">
                ✓ 回答正确！正确答案：{{ getItemAnswer(item.id)?.correctAnswer }}
              </div>
              <div v-else class="feedback-wrong">
                ✗ 回答错误。正确答案：{{ getItemAnswer(item.id)?.correctAnswer }}
              </div>
              <div v-if="getItemAnswer(item.id)?.score !== undefined" class="feedback-score">
                得分：{{ getItemAnswer(item.id)?.score }} / {{ item.points || 0 }} 分
              </div>
            </div>
          </div>

          <!-- 简答题/论述题 -->
          <div v-if="item.type === 'short-answer' || item.type === 'long-answer'">
            <textarea
              v-model="answers[item.id]"
              class="answer-textarea"
              :rows="item.type === 'long-answer' ? 8 : 4"
              :placeholder="item.config.placeholder || '请在此输入答案'"
              :minlength="item.config.minLength"
              :maxlength="item.config.maxLength"
              @input="saveAnswer(item.id)"
            />
            <p v-if="item.config.maxLength" class="text-xs text-gray-500 mt-1">
              {{ (answers[item.id]?.length || 0) }} / {{ item.config.maxLength }} 字
            </p>
          </div>

          <!-- 量表评分 -->
          <div v-if="item.type === 'scale'" class="scale-container">
            <div class="scale-labels">
              <span>{{ item.config.minLabel }}</span>
              <span>{{ item.config.maxLabel }}</span>
            </div>
            <div class="scale-options">
              <label
                v-for="value in scaleRange(item.config.min, item.config.max)"
                :key="value"
                class="scale-option"
              >
                <input
                  v-model.number="answers[item.id]"
                  type="radio"
                  :value="value"
                  :name="`item-${item.id}`"
                  @change="saveAnswer(item.id)"
                />
                <span>{{ value }}</span>
              </label>
            </div>
          </div>

          <!-- 其他题型占位 -->
          <div v-if="['file-upload', 'code-submission', 'rubric-item'].includes(item.type)" class="placeholder">
            <p class="text-gray-500">此题型的答题界面正在开发中...</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 提交按钮 -->
    <div class="submit-section">
      <button v-if="!isSubmitted" @click="handleSaveDraft" class="btn-secondary" :disabled="submitting">
        💾 保存草稿
      </button>
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
import { useOfflineActivity } from '../../composables/useOfflineActivity'

interface Props {
  cell: ActivityCell
  lessonId?: number  // 从父组件传递 lessonId
}

const props = withDefaults(defineProps<Props>(), {
  lessonId: undefined,
})

const emit = defineEmits<{
  submit: [data: any]
}>()

const route = useRoute()
const userStore = useUserStore()

// 提交状态
const isSubmitted = ref(false)
const submissionData = ref<any>(null)  // 存储提交后的完整数据（包含正确答案）

// 状态
const answers = ref<Record<string, any>>({})
const submitting = ref(false)
const startTime = ref(new Date())
const submissionId = ref<number | null>(null)

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

// 安全地解析 cellId
// 注意：如果 cell.id 是 UUID，我们需要通过 API 查找对应的数字 ID
async function resolveCellId(cellId: number | string | undefined): Promise<number> {
  console.log('🔍 Resolving cellId:', { cellId, type: typeof cellId, cell: props.cell })
  
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
      console.warn('⚠️ cellId is UUID, need to find numeric ID. Using lesson content to find cell.')
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
    console.log('🔍 Resolving UUID to numeric ID:', uuid, 'for lesson:', lessonId.value)
    console.log('📋 Current cell info:', {
      uuid,
      order: props.cell.order,
      type: props.cell.type,
      title: props.cell.title,
    })
    
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
    console.log('📦 Fetched cells from API:', cells.length, 'cells')
    
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
        console.log('✅ Resolved UUID to numeric ID:', uuid, '->', numericId)
        return numericId
      }
    }
    
    // 如果找不到匹配的 cell，尝试创建一个新的 cell 记录
    console.log('⚠️ No matching cell found, attempting to create cell record...')
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
      
      console.log('📤 Creating cell:', cellCreateData)
      const createResponse = await api.post('/cells', cellCreateData)
      const newCell = createResponse.data
      
      if (newCell && newCell.id) {
        const numericId = typeof newCell.id === 'number' ? newCell.id : parseInt(newCell.id, 10)
        if (!isNaN(numericId)) {
          cellIdMap.value.set(uuid, numericId)
          console.log('✅ Created new cell and resolved UUID to numeric ID:', uuid, '->', numericId)
          return numericId
        }
      }
    } catch (createError: any) {
      console.error('❌ Failed to create cell:', createError)
      console.error('Create error details:', {
        message: createError.message,
        response: createError.response?.data,
        status: createError.response?.status,
      })
    }
    
    console.warn('⚠️ Could not resolve or create cell for UUID:', uuid)
    return null
  } catch (error: any) {
    console.error('❌ Failed to resolve cell ID from API:', error)
    console.error('Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
    })
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
  console.log('🔍 Initializing cellId, input:', id, 'type:', typeof id, 'cell:', props.cell)
  
  if (typeof id === 'number') {
    if (!isNaN(id)) {
      cellId.value = id
      console.log('✅ Using numeric cellId:', id)
      return
    }
  }
  
  if (typeof id === 'string') {
    const parsed = parseInt(id, 10)
    if (!isNaN(parsed)) {
      cellId.value = parsed
      console.log('✅ Parsed string cellId to number:', parsed)
      return
    }
    
    // 如果是 UUID，后端现在支持直接使用 UUID
    // 但为了兼容性，我们仍然尝试解析为数字 ID
    const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
    if (uuidPattern.test(id)) {
      console.log('🔍 Detected UUID, backend will handle it. Using UUID directly.')
      // 后端现在支持 UUID，所以我们可以直接使用 UUID 字符串
      // 但为了保持类型一致性，我们使用一个特殊值表示 UUID
      // 实际上，我们应该修改前端代码，直接传递 UUID 字符串给后端
      // 但为了最小化改动，我们暂时使用 0，然后在 API 调用时传递 UUID
      cellId.value = 0  // 使用 0 作为标记，表示需要使用 UUID
      // 存储原始 UUID
      ;(cellId as any).uuid = id
      console.log('✅ Will use UUID string for API calls:', id)
      return
    }
    
    console.error('❌ Invalid cellId string (not UUID and not numeric):', id)
  }
  
  console.error('❌ Invalid cellId:', id, 'cell:', props.cell)
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
const syncToServer = async (responses: Record<string, any>, status: string = 'draft') => {
  const actualCellId = getActualCellId()
  
  // 验证 cellId 是否有效
  if (!actualCellId) {
    console.error('❌ Cannot sync: invalid cellId')
    return null
  }
  
  const cellIdType = typeof actualCellId
  const isZero = cellIdType === 'number' && actualCellId === 0
  if (isZero) {
    console.error('❌ Cannot sync: cellId is 0')
    return null
  }
  
  // 如果是 UUID 字符串，直接调用 API
  if (cellIdType === 'string') {
    try {
      const submission = await activityService.createSubmission({
        cellId: actualCellId,
        lessonId: lessonId.value,
        responses,
        startedAt: new Date().toISOString(),
      })
      return submission
    } catch (error) {
      console.error('❌ UUID sync failed:', error)
      return null
    }
  }
  
  // 如果是数字 ID，使用离线支持
  const activity = initOfflineActivity()
  if (!activity) {
    console.warn('⚠️ Offline activity not initialized yet, using direct API call')
    try {
      const submission = await activityService.createSubmission({
        cellId: actualCellId,
        lessonId: lessonId.value,
        responses,
        startedAt: new Date().toISOString(),
      })
      return submission
    } catch (error) {
      console.error('❌ Direct API call failed:', error)
      return null
    }
  }
  
  return await activity.syncToServer(responses, status)
}
const setupAutoSave = (responses: Record<string, any>, interval: number = 30000) => {
  const activity = initOfflineActivity()
  if (!activity) {
    return () => {}
  }
  return activity.setupAutoSave(responses, interval)
}

// 设置自动保存
let cleanupAutoSave: (() => void) | null = null

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

const answeredCount = computed(() => {
  return Object.keys(answers.value).filter(key => {
    const answer = answers.value[key]
    return answer !== undefined && answer !== null && answer !== ''
  }).length
})

const progress = computed(() => {
  const total = props.cell.content.items.length
  return total > 0 ? Math.round((answeredCount.value / total) * 100) : 0
})

const canSubmit = computed(() => {
  // 检查所有必答题是否已完成
  const requiredItems = props.cell.content.items.filter(item => item.required)
  return requiredItems.every(item => {
    const answer = answers.value[item.id]
    return answer !== undefined && answer !== null && answer !== ''
  })
})

// 获取题目的答案数据（包含正确性判断）
function getItemAnswer(itemId: string): any {
  if (!submissionData.value || !submissionData.value.responses) {
    return null
  }
  return submissionData.value.responses[itemId]
}

// 判断选项是否为正确答案（单选题）
function isCorrectAnswerForSingle(itemId: string, optionId: string): boolean {
  const answer = getItemAnswer(itemId)
  if (!answer) return false
  
  // 优先使用 correctAnswerId（如果存在）
  if (answer.correctAnswerId) {
    return String(answer.correctAnswerId) === String(optionId)
  }
  
  // 否则比较选项文本
  if (answer.correctAnswer) {
    const item = props.cell.content.items.find((it: any) => it.id === itemId)
    if (!item) return false
    const option = item.config.options.find((opt: any) => opt.id === optionId)
    if (!option) return false
    return answer.correctAnswer === option.text || answer.correctAnswer === option.id
  }
  
  return false
}

// 判断选项是否为正确答案（多选题）
function isCorrectAnswer(itemId: string, optionId: string): boolean {
  const answer = getItemAnswer(itemId)
  if (!answer || !answer.correctAnswer) return false
  
  // 多选题的正确答案可能是逗号分隔的字符串
  const correctAnswers = answer.correctAnswer.split(',').map((s: string) => s.trim())
  return correctAnswers.some((text: string) => {
    // 找到对应的选项
    const item = props.cell.content.items.find((it: any) => it.id === itemId)
    if (!item) return false
    const option = item.config.options.find((opt: any) => opt.id === optionId)
    return option && (text === option.text || text === option.id)
  })
}

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

function scaleRange(min: number, max: number): number[] {
  const range = []
  for (let i = min; i <= max; i++) {
    range.push(i)
  }
  return range
}

function formatDeadline(deadline: string): string {
  return new Date(deadline).toLocaleString('zh-CN')
}

// 保存单个答案（草稿） - 集成离线支持
async function saveAnswer(itemId: string) {
  console.log('💾 Auto-saving answer:', itemId, answers.value[itemId])
  
  try {
    // 使用离线支持自动保存
    await syncToServer(answers.value, 'draft')
  } catch (error) {
    // 保存失败会自动存到 IndexedDB
    console.log('📱 Saved offline')
  }
}

// 保存草稿
async function handleSaveDraft() {
  try {
    submitting.value = true
    
    await syncToServer(answers.value, 'draft')
    
    alert('草稿已保存' + (isOnline.value ? '' : '（离线模式）'))
  } catch (error) {
    console.error('Save draft failed:', error)
    alert('保存成功（离线模式）')
  } finally {
    submitting.value = false
  }
}

// 提交答案
async function handleSubmit() {
  if (!canSubmit.value) {
    alert('请完成所有必答题')
    return
  }

  // 验证 cellId 是否有效（可以是数字或 UUID 字符串）
  const actualCellId = getActualCellId()
  if (!actualCellId || (typeof actualCellId === 'number' && actualCellId === 0)) {
    console.error('❌ Invalid cellId:', actualCellId, 'cell.id:', props.cell.id)
    alert('无法提交：Cell ID 无效。请刷新页面重试。')
    return
  }

  if (!confirm('确定要提交吗？提交后将无法修改。')) {
    return
  }

  try {
    submitting.value = true
    
    const timeSpent = Math.floor((new Date().getTime() - startTime.value.getTime()) / 1000)

    let submittedSubmission: any
    
    if (submissionId.value) {
      // 如果已有提交ID，调用正式提交API
      submittedSubmission = await activityService.submitActivity(submissionId.value, {
        responses: answers.value,
        timeSpent,
      })
    } else {
      // 先创建提交再提交
      const submission = await activityService.createSubmission({
        cellId: getActualCellId(),  // 可能是数字或 UUID 字符串
        lessonId: lessonId.value,
        responses: answers.value,
        startedAt: startTime.value.toISOString(),
      })
      submissionId.value = submission.id
      
      // 正式提交
      submittedSubmission = await activityService.submitActivity(submission.id, {
        responses: answers.value,
        timeSpent,
      })
    }
    
    // 保存提交后的数据（包含正确答案）
    submissionData.value = submittedSubmission
    isSubmitted.value = true
    
    // 更新 answers 为包含正确答案的完整数据
    if (submittedSubmission.responses) {
      answers.value = submittedSubmission.responses
    }
    
    alert('提交成功！')
    emit('submit', { responses: answers.value, timeSpent })
  } catch (error) {
    console.error('Submit failed:', error)
    alert('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

// 加载已保存的答案
onMounted(async () => {
  console.log('📂 Loading activity...')
  
  // 0. 首先解析 cellId（如果是 UUID）
  await initCellId()
  
  // 1. 尝试从 IndexedDB 加载离线数据
  const offlineData = await loadFromIndexedDB()
  if (offlineData) {
    answers.value = offlineData
    console.log('✅ Loaded from offline storage')
  }
  
  // 2. 如果在线，尝试从服务器加载最新数据
  if (isOnline.value) {
    try {
      // getMyCellSubmission 需要数字 ID，如果是 UUID，跳过这个调用
      const actualCellId = getActualCellId()
      if (typeof actualCellId === 'number' && actualCellId > 0) {
        const submission = await activityService.getMyCellSubmission(actualCellId)
        
        if (submission) {
          submissionId.value = submission.id
          answers.value = submission.responses || {}
          
          // 检查是否已提交
          if (submission.status === 'submitted' || submission.status === 'graded') {
            isSubmitted.value = true
            submissionData.value = submission
          }
          
          // 保存 submissionId 到 IndexedDB
          try {
            const database = await (await import('idb')).openDB('inspireed-activity', 1)
            // 对于 UUID，使用哈希值作为 key 的一部分
            const cellIdForKey = typeof actualCellId === 'string' 
              ? actualCellId.split('-')[0] 
              : actualCellId
            const key = `${cellIdForKey}-${currentStudentId.value}`
            const existing = await database.get('submissions', key).catch(() => null)
            if (existing) {
              await database.put('submissions', {
                ...existing,
                submissionId: submission.id,
                lessonId: lessonId.value,
                responses: submission.responses || {},
                synced: true,
              })
            }
          } catch (dbError) {
            console.warn('Failed to save submissionId to IndexedDB:', dbError)
          }
          
          console.log('✅ Loaded from server')
        } else {
          console.log('ℹ️ No existing submission found, starting fresh')
        }
      }
    } catch (error: any) {
      // 404 错误是正常的（表示还没有提交），其他错误才需要记录
      if (error.response?.status !== 404) {
        console.error('❌ Failed to load submission from server:', error)
      } else {
        console.log('ℹ️ No existing submission found (404)')
      }
    }
  }
  
  // 3. 设置自动保存（每30秒）
  cleanupAutoSave = setupAutoSave(answers.value, 30000)
})

// 组件卸载时清理
onUnmounted(() => {
  if (cleanupAutoSave) {
    cleanupAutoSave()
  }
})

// 监听答案变化，防抖保存
let saveTimeout: number | null = null
watch(answers, () => {
  if (saveTimeout) {
    clearTimeout(saveTimeout)
  }
  saveTimeout = window.setTimeout(() => {
    // 答案改变后 3 秒自动保存
    syncToServer(answers.value, 'draft').catch(() => {
      console.log('📱 Auto-save to offline storage')
    })
  }, 3000)
}, { deep: true })
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

.option-label {
  @apply flex items-start gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors;
}

.option-label input {
  @apply mt-1;
}

.option-label:has(input:disabled) {
  @apply opacity-75 cursor-not-allowed;
}

.option-correct {
  @apply bg-green-50 border-green-300;
}

.option-selected {
  @apply bg-blue-50 border-blue-300;
}

.option-wrong {
  @apply bg-red-50 border-red-300;
}

.correct-badge {
  @apply ml-auto px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded;
}

.feedback-info {
  @apply mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200;
}

.feedback-correct {
  @apply text-green-700 font-semibold mb-2;
}

.feedback-wrong {
  @apply text-red-700 font-semibold mb-2;
}

.feedback-score {
  @apply text-gray-600 text-sm mt-2;
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

.answer-textarea {
  @apply w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

.scale-container {
  @apply space-y-3;
}

.scale-labels {
  @apply flex justify-between text-sm text-gray-600;
}

.scale-options {
  @apply flex justify-between gap-2;
}

.scale-option {
  @apply flex flex-col items-center gap-1 cursor-pointer;
}

.scale-option input {
  @apply w-5 h-5;
}

.placeholder {
  @apply py-8 text-center bg-gray-50 rounded-lg border-2 border-dashed border-gray-300;
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

