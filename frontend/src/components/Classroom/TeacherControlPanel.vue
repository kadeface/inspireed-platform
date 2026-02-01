<template>
  <div ref="containerRef" class="teacher-control-panel" :class="{ 'panel-fullscreen': isPanelFullscreen }">
    <!-- 🎯 优化后的顶部控制栏（固定，始终可见） -->
    <div class="top-control-bar">
      <!-- 第一行：标题和操作按钮 -->
      <div class="top-control-row">
        <div class="top-control-left">
          <div class="title-with-mode-toggle">
            <h2 class="panel-title">InspireEd 教师导播台</h2>
            <!-- 模式切换按钮 -->
            <button
              v-if="lessonContentCells.length > 0"
              type="button"
              @click="toggleSelectionMode"
              :disabled="loading"
              :class="[
                'mode-toggle-btn-compact',
                isMultiSelectMode ? 'mode-multi' : 'mode-single'
              ]"
              :title="isMultiSelectMode ? '当前：多选模式（点击切换为单选）' : '当前：单选模式（点击切换为多选）'"
            >
              <svg v-if="!isMultiSelectMode" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              <span class="ml-1 text-xs font-medium">{{ isMultiSelectMode ? '多选' : '单选' }}</span>
            </button>
          </div>
          <!-- v2.0: 使用子组件显示学生人数 -->
          <StudentCountDisplay
            v-if="session"
            :active-count="activeStudents.length"
            :total-count="totalStudents"
            label="人已进入"
          />
          <!-- v2.0: 使用子组件显示模块数量 -->
          <ModuleCountDisplay
            v-if="lessonContentCells.length > 0"
            :count="lessonContentCells.length"
            label="个模块"
          />
          <!-- v2.0: 使用子组件显示课程时长 -->
          <SessionDurationDisplay
            v-if="session && normalizedSessionStatus !== 'pending'"
            :status="session.status"
            :duration="displayDuration"
            :remaining="remainingTime"
          />
        </div>
        <div class="header-controls">
          <!-- v2.0: 使用子组件显示会话控制按钮 -->
          <SessionControlButtons
            :has-session="!!session"
            :session-status="session?.status"
            :loading="loading"
            :active-students-count="activeStudents.length"
            @create="handleCreateSession"
            @start="handleBeginClass"
            @end="handleEnd"
          />
        
        <!-- ACTIVE 状态：上课中 -->
        <template v-if="session && (session.status === 'teaching' || session.status === 'TEACHING')">
          <!-- 显示模式切换按钮 -->
          <div class="display-mode-controls">
            <button 
              @click="handleToggleDisplayMode"
              :disabled="loading"
              class="btn btn-display-mode"
              :class="{ 'active': currentDisplayMode === 'fullscreen' }"
              :title="currentDisplayMode === 'fullscreen' ? '当前：全屏模式' : '当前：窗口模式'"
            >
              <svg v-if="currentDisplayMode === 'window'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
              </svg>
              <span class="ml-1">{{ currentDisplayMode === 'fullscreen' ? '全屏' : '窗口' }}</span>
            </button>
          </div>
          <button 
            @click="handlePause"
            :disabled="loading"
            class="btn btn-secondary"
          >
            ⏸️ 暂停
          </button>
          <button 
            @click="handleEnd"
            :disabled="loading"
            class="btn btn-danger"
          >
            ⏹️ 结束
          </button>
        </template>
        
        <!-- PAUSED 状态：已暂停 -->
        <template v-if="session && (session.status === 'teaching' || session.status === 'TEACHING')">
          <!-- 显示模式切换按钮 -->
          <div class="display-mode-controls">
            <button 
              @click="handleToggleDisplayMode"
              :disabled="loading"
              class="btn btn-display-mode"
              :class="{ 'active': currentDisplayMode === 'fullscreen' }"
              :title="currentDisplayMode === 'fullscreen' ? '当前：全屏模式' : '当前：窗口模式'"
            >
              <svg v-if="currentDisplayMode === 'window'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
              </svg>
              <span class="ml-1">{{ currentDisplayMode === 'fullscreen' ? '全屏' : '窗口' }}</span>
            </button>
          </div>
          <button 
            @click="handleResume"
            :disabled="loading"
            class="btn btn-primary"
          >
            ▶️ 继续
          </button>
          <button 
            @click="handleEnd"
            :disabled="loading"
            class="btn btn-danger"
          >
            ⏹️ 结束
          </button>
        </template>
        </div>
      </div>
    </div>
    
    <!-- PENDING 状态：等待学生加入提示区域 -->
    <WaitingForStudentsBanner
      v-if="session"
      :session-status="session.status"
      :active-count="activeStudents.length"
    />

    <!-- 已加入学生列表 -->
    <JoinedStudentsList
      v-if="session && session.status === 'PREPARING'"
      :students="activeStudents"
      :max-display="12"
    />

    <!-- 主布局：左侧模块列表，右侧预览和监控 -->
    <div class="main-layout" :class="{ 'module-fullscreen-mode': modulePanelFullscreen }">
      <!-- 左侧：教学模块 -->
      <div class="panel teaching-modules teaching-modules-fullwidth" :class="{ 'module-panel-fullscreen': modulePanelFullscreen }">
        <ModuleList
          :cells="lessonContentCells"
          :current-module-index="currentModuleIndex"
          :loading="loading"
          :is-multi-select-mode="isMultiSelectMode"
          :display-cell-orders="displayCellOrders"
          :session-current-activity-id="session?.current_activity_id"
          @item-click="handleModuleItemClick"
          @checkbox-click="handleModuleCheckboxClick"
          @checkbox-change="handleModuleCheckboxChange"
          @prev-module="handlePrevModule"
          @next-module="handleNextModule"
        />

        <!-- 活动统计面板 -->
        <ActivityStatisticsPanel
          v-if="currentCell"
          :current-cell="currentCell"
          :activity-statistics="activityStatistics"
          :loading="loadingActivityStats"
        />
      </div>
    </div>
  </div>

  <!-- 班级选择弹窗（用于创建会话时选择班级） -->
  <ClassroomSelectModal
    :show="showClassroomSelectModal"
    :classrooms="availableClassrooms"
    :loading="loadingClassrooms"
    v-model="selectedClassroomId"
    :error="classroomSelectError"
    @update:show="showClassroomSelectModal = $event"
    @cancel="handleClassroomSelectCancel"
    @confirm="handleClassroomSelectConfirm"
  />
</template>

<script setup lang="ts">
// ============================================================================
// 1. Vue 核心
// ============================================================================
import { ref, computed, onMounted, onBeforeUnmount, onUnmounted, watch, provide, nextTick } from 'vue'

// ============================================================================
// 2. 类型定义
// ============================================================================
import type { Lesson } from '../../types/lesson'
import type { LessonClassroom } from '../../types/lesson'
import type { Cell, ActivityCell } from '../../types/cell'

// ============================================================================
// 3. Store
// ============================================================================
import { useLessonStore } from '../../store/lesson'

// ============================================================================
// 4. 服务
// ============================================================================
import classroomSessionService from '../../services/classroomSession'
import activityService from '../../services/activity'

// ============================================================================
// 5. 子组件
// ============================================================================
import SessionDurationDisplay from './SessionDurationDisplay.vue'
import StudentCountDisplay from './StudentCountDisplay.vue'
import SessionControlButtons from './SessionControlButtons.vue'
import ModuleCountDisplay from './ModuleCountDisplay.vue'
import WaitingForStudentsBanner from './WaitingForStudentsBanner.vue'
import JoinedStudentsList from './JoinedStudentsList.vue'
import ModuleList from './ModuleList.vue'
import ClassroomSelectModal from './ClassroomSelectModal.vue'
import ActivityStatisticsPanel from './ActivityStatisticsPanel.vue'
import CellTypeIcon from './CellTypeIcon.vue'

// ============================================================================
// 6. Composables
// ============================================================================
import { useSessionManager } from './composables/useSessionManager'
import { usePolling } from './composables/usePolling'
import { useDurationTimer } from './composables/useDurationTimer'
import { useNavigation } from './composables/useNavigation'
import { useDataLoader } from './composables/useDataLoader'
import { useFullscreen } from './composables/useFullscreen'
import { useSelectionMode } from './composables/useSelectionMode'

// ============================================================================
// 7. 工具函数
// ============================================================================
import logger from '@/utils/logger'
import { getCellId as getCellIdUtil, toNumericId, isUUID } from '../../utils/cellId'
import { isContentWithSections, sectionsToFlatCells, normalizeContentToSections } from '../../utils/lessonContent'

// 学生监控工具
import {
  getStudentStatusClass,
  getStudentTooltip,
  getStudentAccount,
  calculateParticipationRate,
  calculateAverageScore,
  calculateStudentsBehindCount,
  hasAlerts as checkHasAlerts,
  checkLowSubmissionRate
} from './studentMonitoring'

// Cell 工具函数
import {
  getCellTypeLabel,
  getCellTypeEmoji,
  isModuleActive,
  isModuleActivityActive,
  getModuleTooltip,
  getCurrentModuleIndex,
  getCellByOrder,
  getTextPreview,
  getCodePreview,
  handleThumbnailError,
  setModuleItemRef,
  scrollToSelectedModule
} from './cellUtils'

// 格式化工具函数
import {
  formatDuration,
  formatRemainingTime,
} from './formatUtils'

// ============================================================================
// 8. 组件定义
// ============================================================================

interface Props {
  lessonId: number
  lesson?: Lesson
}

const props = defineProps<Props>()

// ============================================================================
// Props & Emits
// ============================================================================

// 🔧 定义事件，通知父组件 session 变化
const emit = defineEmits<{
  'session-changed': [session: any | null]
}>()

// ============================================================================
// Store
// ============================================================================

const lessonStore = useLessonStore()

// ============================================================================
// Composables 初始化
// ============================================================================

// v2.0: 使用composables管理会话状态
const sessionManager = useSessionManager({
  lessonId: props.lessonId,
  onSessionCreated: (newSession) => {
    console.log('✅ TeacherControlPanel: 会话已创建，sessionId =', newSession.id, '状态 =', newSession.status)
    // 立即加载一次学生列表
    loadParticipants()
    console.log('✅ 初始学生列表加载完成，学生数:', activeStudents.value.length)
  },
  onSessionStarted: (updatedSession) => {
    // v2.0: 使用 durationTimer composable 管理计时
    durationTimer.startDurationTimer()
    // 加载统计信息
    loadStatistics()
  },
  onSessionEnded: () => {
    durationTimer.stopDurationTimer()
    pollingManager.clearAllPollingIntervals()
    activeStudents.value = []
  },
})

// v2.0: 使用composables管理轮询
const pollingManager = usePolling({
  isComponentVisible: () => containerRef.value?.isConnected ?? false,
  getSessionStatus: () => sessionManager.normalizedSessionStatus.value,
  hasSession: () => !!session.value,
  loadParticipants,
  loadStatistics,
  loadActivityStatistics,
  isCurrentCellActivity: () => currentCell.value?.type === 'activity' && !!currentActivityDbCell.value,
})

// v2.0: 使用composables管理计时器
const durationTimer = useDurationTimer({
  getSessionStatus: () => sessionManager.normalizedSessionStatus.value,
  lessonDuration: 40 * 60, // 40分钟
  onTimerStateChange: (isRunning) => {
    // 可选：在计时器状态变化时执行操作
    console.log('⏱️ 计时器状态:', isRunning ? '运行中' : '已停止')
  },
})

// 监听会话状态变化，自动启动/停止计时器
durationTimer.watchSessionStatus(sessionManager.normalizedSessionStatus)

// v2.0: 使用composables管理数据加载
const dataLoader = useDataLoader({
  session,
  lessonId: props.lessonId,
  currentCell,
  currentActivityDbCell,
  containerRef,
  pollingManager,
  dbCells,
})

// 从 dataLoader 解构数据加载相关状态和方法
const {
  loadingStudents,
  loadingActivityStats,
  activeStudents,
  sessionStatistics,
  activityStatistics,
  studentSubmissionStatus,
  loadParticipants,
  loadStatistics,
  loadActivityStatistics,
  loadDbCells,
  ensureActivityCellExists,
  watchCurrentCell,
} = dataLoader

// v2.0: 使用composables管理全屏控制
const fullscreenManager = useFullscreen()

// 从 fullscreenManager 解构全屏相关状态和方法
const {
  modulePanelFullscreen,
  isPanelFullscreen,
  toggleModulePanelFullscreen,
  togglePanelFullscreen,
  setupFullscreenListeners,
  cleanupFullscreenListeners,
} = fullscreenManager

// v2.0: 使用composables管理选择模式（需要在 navigationManager 之前初始化，因为它提供 isMultiSelectMode）
const selectionModeManager = useSelectionMode({
  loading,
  session,
  displayCellOrders,
  lessonContentCells,
  // handleControlBoardNavigate 将在 navigationManager 初始化后可用
})

// 从 selectionModeManager 解构
const { isMultiSelectMode, toggleSelectionMode } = selectionModeManager

// v2.0: 使用composables管理导航（需要在 dataLoader 之后，因为它依赖 dataLoader 的函数）
const navigationManager = useNavigation({
  session,
  loading,
  selectedCellIndex,
  lessonContentCells,
  isMultiSelectMode,
  normalizedSessionStatus: sessionManager.normalizedSessionStatus,
  currentModuleIndex,
  isModuleActive: isModuleActiveWrapper,
  scrollToSelectedModule: scrollToSelectedModuleWrapper,
  loadParticipants,
  ensureActivityCellExists,
  loadDbCells,
  dbCells,
})

// 从 navigationManager 解构导航相关方法
const {
  canGoPrev,
  canGoNext,
  handleControlBoardNavigate,
  handleModuleItemClick,
  handlePrevModule,
  handleNextModule,
  handleModuleCheckboxClick,
  handleModuleCheckboxChange,
  handleHideAll,
} = navigationManager

// 从 composable 解构会话相关状态和方法
const {
  session,
  loading,
  showClassroomSelectModal,
  selectedClassroomId,
  classroomSelectError,
  availableClassrooms,
  loadingClassrooms,
  normalizedSessionStatus,
  statusTitle,
  statusClass,
  currentDisplayMode,
  handleCreateSession,
  handleClassroomSelectConfirm,
  handleClassroomSelectCancel,
  handleBeginClass,
  handleCancelSession,
  handlePause,
  handleResume,
  handleEnd,
  handleToggleDisplayMode,
  handleStartActivity,
  handleEndActivity,
} = sessionManager

// 组件 Refs
const containerRef = ref<HTMLElement | null>(null) // 用于检查组件是否在 DOM 中
const moduleListRef = ref<HTMLElement | null>(null) // 模块列表容器
const moduleItemRefs = ref<Map<number, HTMLElement>>(new Map()) // 模块项引用
// v2.0: 以下状态已移至 useDataLoader composable
// const activeStudents, const loadingStudents, const sessionStatistics
// const activityStatistics, const studentSubmissionStatus, const loadingActivityStats
// 现在从 dataLoader 导入

// 🔧 提供 sessionId 给子组件（通过 provide/inject）
provide('classroomSessionId', computed(() => session.value?.id))
provide('classroomSession', session)

// 🔧 监听 session 变化，通知父组件
watch(session, (newSession) => {
  logger.debug("TeacherControlPanel: session 变化，通知父组件", {
    sessionId: newSession?.id,
    status: newSession?.status,
    timestamp: new Date().toLocaleTimeString(),
  })
  emit('session-changed', newSession)
}, { immediate: true, deep: true })

// v2.0: 以下状态已移至 useDataLoader composable
// const loadingStudents, const sessionStatistics, const activityStatistics
// const studentSubmissionStatus, const loadingActivityStats
// 现在从 dataLoader 导入
// v2.0: 以下状态已移至 useSelectionMode composable
// const isMultiSelectMode 现在从 selectionModeManager 导入
const selectedCellIndex = ref(-1)  // -1表示隐藏所有内容
const dbCells = ref<Array<{ id: number; order: number; cell_type: string }>>([])  // 数据库中的 Cell 记录（用于 ID 匹配）
// v2.0: 以下状态已移至 useFullscreen composable
// const modulePanelFullscreen, const isPanelFullscreen
// 现在从 fullscreenManager 导入

// v2.0: 从 durationTimer composable 获取 sessionDuration
const { sessionDuration } = durationTimer

// 一节课的标准时长（40分钟 = 2400秒）
const LESSON_DURATION = 40 * 60

// 显示的课程时长（只有在 active 状态才显示实际时长）
const displayDuration = computed(() => {
  // v2.0: 使用 durationTimer composable 的方法
  return durationTimer.getDisplayDuration()
})

// 计算剩余时间
const remainingTime = computed(() => {
  // v2.0: 使用 durationTimer composable 的方法
  return durationTimer.getRemainingTime()
})

// v2.0: 以下computed属性已移至 useSessionManager.ts
// const normalizedSessionStatus
// const statusTitle
// const statusClass
// const currentDisplayMode

const totalStudents = computed(() => {
  return session.value?.total_students || 0
})

// 显示的学生列表（最多8个用于指示器）
const displayStudents = computed(() => {
  return activeStudents.value.slice(0, 8)
})

// 将 lesson.content 转换为 flat cells 数组（支持新旧两种格式）
const lessonContentCells = computed(() => {
  if (!props.lesson?.content) return []
  
  // 如果已经是数组格式（旧格式），直接返回
  if (Array.isArray(props.lesson.content)) {
    return props.lesson.content
  }
  
  // 如果是 sections 格式（新格式），转换为 flat cells
  if (isContentWithSections(props.lesson.content)) {
    const sections = normalizeContentToSections(props.lesson.content)
    return sectionsToFlatCells(sections)
  }
  
  return []
})

// v2.0: 学生监控工具函数已移至 studentMonitoring.ts
// getStudentStatusClass, getStudentTooltip, getStudentAccount 现在从工具文件导入

// 参与度（基于在线学生和总学生的比例，以及平均进度）
const participationRate = computed(() => {
  if (totalStudents.value === 0) return 0
  const avgProgress = sessionStatistics.value?.average_progress || 0
  return calculateParticipationRate(activeStudents.value, totalStudents.value, avgProgress)
})

// 平均得分
const averageScore = computed(() => {
  if (sessionStatistics.value?.average_score !== undefined) {
    return calculateAverageScore(sessionStatistics.value.average_score, 0)
  }
  // 如果没有得分数据，基于进度估算
  const avgProgress = sessionStatistics.value?.average_progress || 0
  return calculateAverageScore(undefined, avgProgress)
})



const currentCell = computed(() => {
  if (!lessonContentCells.value.length || !session.value) {
    return null
  }
  
  // 如果 selectedCellIndex 有效，优先使用它
  if (selectedCellIndex.value >= 0 && selectedCellIndex.value < lessonContentCells.value.length) {
    return lessonContentCells.value[selectedCellIndex.value]
  }
  
  // 否则使用 current_cell_id 查找
  const currentId = session.value.current_cell_id
  if (!currentId || currentId === 0) {
    return null
  }
  
  // 查找匹配的Cell
  const foundCell = lessonContentCells.value.find((cell, index) => {
    const cellId = getCellId(cell)
    // 尝试匹配数字ID
    if (typeof cellId === 'number' && cellId === currentId) return true
    // 尝试匹配字符串ID（转换为数字）
    if (typeof cellId === 'string') {
      const numId = parseInt(cellId)
      if (!isNaN(numId) && numId === currentId) return true
    }
    // 尝试通过索引匹配（如果currentId是顺序索引）
    if (index === currentId) return true
    // 尝试通过order匹配
    if (cell.order !== undefined && cell.order === currentId) return true
    return false
  })
  
  return foundCell || null
})

// 获取当前活动 Cell 的数据库 ID（用于查询提交数据）
// 计算 displayCellOrders（从 session.settings 中获取）
const displayCellOrders = computed(() => {
  if (!session.value?.settings) return []
  const settings = session.value.settings as any
  if (settings?.display_cell_orders && Array.isArray(settings.display_cell_orders)) {
    return settings.display_cell_orders
  }
  return []
})

// 获取当前选中模块的索引
const currentModuleIndex = computed(() => {
  if (!lessonContentCells.value.length) return -1
  
  // 多选模式：使用 displayCellOrders 中的第一个
  if (displayCellOrders.value !== undefined && Array.isArray(displayCellOrders.value) && displayCellOrders.value.length > 0) {
    const firstOrder = displayCellOrders.value[0]
    const index = lessonContentCells.value.findIndex((cell, idx) => {
      const cellOrder = cell.order !== undefined ? cell.order : idx
      return cellOrder === firstOrder
    })
    if (index >= 0) return index
  }
  
  // 单选模式：直接使用 selectedCellIndex（它会在点击时立即更新）
  if (selectedCellIndex.value >= 0 && selectedCellIndex.value < lessonContentCells.value.length) {
    return selectedCellIndex.value
  }
  
  // 如果 selectedCellIndex 无效，尝试从 session.current_cell_id 获取
  if (session.value?.current_cell_id) {
    const currentId = session.value.current_cell_id
    if (currentId === 0) return -1
    
    const index = lessonContentCells.value.findIndex((cell, idx) => {
      const cellId = getCellId(cell)
      if (typeof cellId === 'number' && cellId === currentId) return true
      if (typeof cellId === 'string') {
        const numId = parseInt(cellId)
        if (!isNaN(numId) && numId === currentId) return true
      }
      if (idx === currentId) return true
      if (cell.order !== undefined && cell.order === currentId) return true
      return false
    })
    if (index >= 0) return index
  }
  
  return -1
})

// v2.0: 以下computed属性已移至 useNavigation composable
// const canGoPrev, const canGoNext 现在从 navigationManager 导入

const currentActivityDbCell = computed(() => {
  if (!currentCell.value || currentCell.value.type !== 'activity') {
    return null
  }
  
  if (!dbCells.value || dbCells.value.length === 0) {
    return null
  }
  
  // 通过 order 查找对应的数据库 Cell
  const order = currentCell.value.order
  if (order === undefined) {
    return null
  }
  
  // 尝试匹配 cell_type（可能是 'ACTIVITY' 或 'activity'）
  const matchedDbCell = dbCells.value.find(dbCell => {
    const cellTypeMatch = dbCell.cell_type === 'ACTIVITY' || 
                          dbCell.cell_type === 'activity' ||
                          dbCell.cell_type?.toUpperCase() === 'ACTIVITY'
    return dbCell.order === order && cellTypeMatch
  })
  
  return matchedDbCell || null
})


// v2.0: Cell工具函数已移至 cellUtils.ts
// getCellId, getCellTypeLabel, getCellTypeEmoji, isModuleActive, isModuleActivityActive,
// getModuleTooltip, getCurrentModuleIndex, getCellByOrder, getTextPreview, getCodePreview,
// handleThumbnailError, setModuleItemRef, scrollToSelectedModule
// 现在从工具文件导入

// 方法
// 使用工具函数获取 Cell ID（保留此函数名以兼容现有代码）
function getCellId(cell: Cell): number | string | null {
  return getCellIdUtil(cell)
}

// v2.0: 以下函数已移至 cellUtils.ts
// function getCellTypeLabel(type: string): string
// function getCellTypeEmoji(type: string): string
// function isModuleActiveWrapper(cell, index): boolean
// function isModuleActivityActive(cell, index): boolean
// function setModuleItemRef(el, index): void
// function scrollToSelectedModuleWrapper(): void
// function getModuleTooltip(cell, index): string
// function getCurrentModuleIndex(): number
// function getCellByOrder(order): Cell | null
// function getTextPreview(cell, maxLength): string
// function getCodePreview(cell): string
// function handleThumbnailError(event): void

// v2.0: 包装函数 - 调用cellUtils中的工具函数
function isModuleActiveWrapper(cell: Cell, index: number): boolean {
  return isModuleActive(cell, index, session.value, displayCellOrders.value, selectedCellIndex.value)
}

function isModuleActivityActiveWrapper(cell: Cell, index: number): boolean {
  return isModuleActivityActive(cell, index, session.value)
}

function getModuleTooltipWrapper(cell: Cell, index: number): string {
  const isActive = isModuleActiveWrapper(cell, index)
  return getModuleTooltip(cell, index, isActive)
}

function scrollToSelectedModuleWrapper() {
  scrollToSelectedModule(moduleListRef, moduleItemRefs.value, selectedCellIndex.value)
}

// v2.0: 以下函数已移至 useNavigation composable
// function handleModuleItemClick, handlePrevModule, handleNextModule
// function handleModuleCheckboxClick, handleModuleCheckboxChange, handleHideAll
// function handleControlBoardNavigate
// 现在从 navigationManager 导入

// 获取模块提示信息
// v2.0: 已移至 cellUtils.ts as getModuleTooltip

// 获取当前模块索引
// v2.0: 已移至 cellUtils.ts as getCurrentModuleIndex

// 计算进度落后学生数量（进度 < 50%）
const studentsBehindCount = computed(() => {
  return calculateStudentsBehindCount(activeStudents.value)
})

// 是否有预警（用于高亮预警栏）
const hasAlerts = computed(() => {
  return checkHasAlerts(
    studentsBehindCount.value,
    checkLowSubmissionRate(currentCell.value, sessionStatistics.value)
  )
})

// v2.0: 以下状态和函数已移至 useDataLoader composable
// function getCellByOrder(order): Cell | null
// function getTextPreview(cell, maxLength): string
// function getCodePreview(cell): string
// function handleThumbnailError(event): void

// v2.0: 以下函数已移至 useFullscreen composable
// function toggleModulePanelFullscreen, togglePanelFullscreen, handleFullscreenChange
// 现在从 fullscreenManager 导入

// v2.0: 切换选择模式函数已移至 useSelectionMode composable
// async function toggleSelectionMode(...) {...}
// 现在从 selectionModeManager 导入

// 隐藏所有内容（通过导播台的"隐藏"节点调用）
// v2.0: 已移至 useNavigation composable

// v2.0: 以下函数已移至 useDataLoader composable
// function loadParticipants, loadStatistics, loadDbCells, ensureActivityCellExists
// 现在从 dataLoader 导入

// v2.0: 定时器管理已移至 useDurationTimer composable

// v2.0: 监听会话状态变化，自动启动/停止轮询
watch(() => sessionManager.normalizedSessionStatus.value, (status, oldStatus) => {
  // 当会话被创建或状态改变时，启动轮询
  if (status && status !== oldStatus) {
    pollingManager.startPollingIfNeeded()
    console.log('✅ 会话状态变化，已启动轮询，新状态:', status)
  }
  // 当会话结束时，清理轮询
  if (status === 'ended' || status === null) {
    pollingManager.clearAllPollingIntervals()
  }
}, { immediate: false })

// 监听 selectedCellIndex 变化，自动滚动到对应模块
watch(selectedCellIndex, (newIndex, oldIndex) => {
  if (newIndex >= 0 && newIndex !== oldIndex) {
    // 延迟滚动，确保 DOM 已更新
    nextTick(() => {
      setTimeout(() => {
        scrollToSelectedModuleWrapper()
      }, 150)
    })
  }
})

// v2.0: 监听 displayCellOrders 变化已移至 useSelectionMode composable
// watch(displayCellOrders, ...) {...}

// 监听session变化，更新selectedCellIndex和displayCellIds
watch(() => session.value, (newSession) => {
  if (!props.lesson?.content || !newSession) return
  
  // 使用 display_cell_orders
  const settings = newSession.settings as any
  if (settings?.display_cell_orders && Array.isArray(settings.display_cell_orders)) {
    const orders = settings.display_cell_orders
    
    // 如果有选中的 orders，使用第一个的索引
    if (orders.length > 0) {
      // 🆕 通过 order 查找对应的数组索引
      const index = lessonContentCells.value.findIndex((cell, idx) => {
        const cellOrder = cell.order !== undefined ? cell.order : idx
        return cellOrder === orders[0]
      })
      selectedCellIndex.value = index >= 0 ? index : orders[0]
      return
    }
  }
  
  // 单选模式：更新 selectedCellIndex
  const cellId = newSession.current_cell_id
  if (!cellId || cellId === 0) {
    selectedCellIndex.value = -1
    return
  }
  
  // 查找匹配的Cell
  const index = lessonContentCells.value.findIndex(cell => {
    const id = getCellId(cell)
    // 尝试匹配数字ID
    if (typeof id === 'number' && id === cellId) return true
    // 尝试匹配字符串ID（转换为数字）
    if (typeof id === 'string') {
      const numId = parseInt(id)
      if (!isNaN(numId) && numId === cellId) return true
    }
    return false
  })
  
  if (index >= 0) {
    selectedCellIndex.value = index
  } else {
    // 如果没找到，设置为-1（隐藏状态）
    selectedCellIndex.value = -1
  }
}, { immediate: true, deep: true })

// v2.0: 监听 currentCell 的逻辑已移至 useDataLoader composable
// 现在通过 dataLoader.watchCurrentCell() 调用

// v2.0: 以下函数已移至 useDataLoader composable
// function loadDbCells, ensureActivityCellExists
// 现在从 dataLoader 导入

// 初始化
onMounted(async () => {
  // 静默执行，不输出日志

  // v2.0: 设置全屏监听器
  setupFullscreenListeners()

  // 加载数据库 Cell 记录（用于 ID 匹配）
  await loadDbCells()

  // v2.0: 监听 currentCell 变化，自动加载活动统计
  watchCurrentCell()

  // ✅ 重要：不自动加载会话和启动轮询
  // 只有在用户明确点击"创建课堂"或"准备上课"时才加载会话
  // 这样可以避免在非授课模式下不必要的轮询

  // 确保没有遗留的轮询定时器
  pollingManager.clearAllPollingIntervals()
})

// 组件卸载前清理
onBeforeUnmount(() => {
  pollingManager.clearAllPollingIntervals()
})

onUnmounted(() => {
  // v2.0: 使用 durationTimer composable 停止计时
  durationTimer.stopDurationTimer()

  // 清理所有轮询定时器（双重保险）
  pollingManager.clearAllPollingIntervals()

  // v2.0: 清理全屏监听器
  cleanupFullscreenListeners()
})

// 🔧 暴露 session 给父组件（LessonEditor）使用
defineExpose({
  session,
  sessionId: computed(() => session.value?.id),
  activeStudents,
  totalStudents,
  displayDuration,
  remainingTime,
  formatDuration,
  formatRemainingTime,
  handleToggleDisplayMode,
  handlePause,
  handleEnd,
  // 添加调试日志
  getSessionId: () => {
    const id = session.value?.id
    console.log('🔍 TeacherControlPanel defineExpose getSessionId:', id, session.value)
    return id
  },
})
</script>

<style scoped>
.teacher-control-panel {
  @apply bg-white rounded-lg border border-gray-200;
  min-height: auto;
  position: relative;
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
  box-sizing: border-box;
}

/* 导播台全屏模式 */
.teacher-control-panel.panel-fullscreen {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  z-index: 9999 !important;
  border-radius: 0 !important;
  border: none !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow-y: auto;
}

.teacher-control-panel.panel-fullscreen .top-control-bar {
  position: sticky;
  top: 0;
  z-index: 100;
}

.teacher-control-panel.panel-fullscreen .main-layout {
  padding: 24px;
  min-height: calc(100vh - 280px);
  height: auto;
}

.teacher-control-panel.panel-fullscreen .teaching-modules {
  height: auto !important;
  min-height: auto !important;
  max-height: none !important;
}


/* 🎯 优化后的顶部控制栏 */
.top-control-bar {
  @apply bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm;
}

.top-control-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
}

.top-control-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.lesson-info {
  @apply text-sm text-gray-600;
}

.lesson-title {
  @apply font-medium text-gray-800;
}

.student-count-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  @apply bg-emerald-50 border border-emerald-200 rounded-lg;
  margin-left: 16px;
}

.student-count-icon {
  font-size: 18px;
  line-height: 1;
}

.student-count-text {
  display: flex;
  align-items: baseline;
  gap: 4px;
  @apply text-sm font-medium;
}

.student-count-value {
  @apply text-emerald-700 font-bold text-base;
}

.student-count-total {
  @apply text-emerald-600;
}

.student-count-label {
  @apply text-emerald-600;
  margin-left: 2px;
}

.module-count-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  @apply bg-blue-50 border border-blue-200 rounded-lg;
  margin-left: 16px;
}

.module-count-icon {
  font-size: 18px;
  line-height: 1;
}

.module-count-text {
  display: flex;
  align-items: baseline;
  gap: 4px;
  @apply text-sm font-medium;
}

.module-count-value {
  @apply text-blue-700 font-bold text-base;
}

.module-count-label {
  @apply text-blue-600;
  margin-left: 2px;
}

.duration-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  @apply bg-blue-50 border border-blue-200 rounded-lg;
  margin-left: 16px;
}

.duration-info.duration-warning {
  @apply bg-orange-50 border-orange-200;
}

.duration-info.duration-danger {
  @apply bg-red-50 border-red-200;
}

.duration-icon {
  font-size: 18px;
  line-height: 1;
}

.duration-text {
  display: flex;
  align-items: baseline;
  gap: 8px;
  @apply text-sm font-medium;
  flex-wrap: wrap;
}

.duration-value {
  @apply font-bold text-base;
}

.duration-remaining {
  @apply text-gray-600 text-xs;
}

/* 关键指标行 - 首页风格卡片 */
.top-control-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 12px 16px;
  @apply bg-gray-50 border-t border-gray-200;
  overflow-x: auto;
}

@media (max-width: 1200px) {
  .top-control-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .top-control-metrics {
    grid-template-columns: 1fr;
  }
}

/* 指标卡片 - 首页风格 */
.metric-card {
  position: relative;
  overflow: hidden;
  @apply rounded-xl border border-gray-100 bg-white/80 backdrop-blur-sm p-4 shadow-md;
  transition: all 0.3s ease;
  transform: translateY(0);
}

.metric-card:hover {
  @apply shadow-2xl;
  transform: translateY(-4px);
}

.metric-accent-bar {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 3px;
}

.metric-card-content {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metric-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}

.metric-header-text {
  flex: 1;
  min-width: 0;
}

.metric-card-label {
  @apply text-xs font-semibold uppercase tracking-wide text-gray-500;
  margin-bottom: 2px;
}

.metric-card-title {
  @apply text-sm font-bold text-gray-900;
  line-height: 1.2;
}

.metric-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.metric-icon-text {
  font-size: 18px;
  line-height: 1;
}

.metric-card-value-group {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-top: 2px;
}

.metric-card-value {
  @apply text-2xl font-bold;
  line-height: 1;
}

.metric-card-value-small {
  @apply text-base font-bold;
  line-height: 1.2;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.metric-card-description {
  @apply text-xs text-gray-600;
  margin-top: 2px;
  line-height: 1.3;
}

/* 警告和危险状态 */
.metric-card.metric-warning .metric-accent-bar {
  @apply bg-gradient-to-r from-orange-500 to-amber-500;
}

.metric-card.metric-danger .metric-accent-bar {
  @apply bg-gradient-to-r from-red-500 to-rose-500;
}

.metric-card.metric-warning {
  @apply border-orange-200 bg-orange-50/50;
}

.metric-card.metric-danger {
  @apply border-red-200 bg-red-50/50;
}

/* 📺 学生预览面板样式 */
/* 样式已在上面定义，此处不再重复 */

/* 预览内容样式已在上面定义 */

.preview-item-compact {
  @apply bg-gray-50 border border-gray-200 rounded-lg p-2.5;
  transition: all 0.2s ease;
  flex-shrink: 0;
  min-height: 90px;
}

.preview-item-compact:hover {
  @apply border-gray-300 shadow-sm;
  transform: translateY(-1px);
}

.preview-item-header-compact {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  gap: 8px;
}

.preview-item-number {
  @apply text-xs font-bold text-gray-500 bg-gray-200 px-2 py-0.5 rounded;
}

.preview-item-type-compact {
  @apply text-xs text-gray-600 bg-white px-2 py-0.5 rounded border border-gray-300;
}

.preview-item-title-compact {
  @apply text-xs font-semibold text-gray-900 mb-1.5;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.preview-item-body-compact {
  @apply text-xs text-gray-600;
  min-height: 60px;
  max-height: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  overflow: hidden;
}

/* 缩略图包装器 */
.preview-thumbnail-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-bottom: 4px;
}

/* 缩略图 */
.preview-thumbnail {
  width: 100%;
  height: 60px;
  border-radius: 6px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;
}

.preview-thumbnail-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: #f3f4f6;
}

.preview-thumbnail-content {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.preview-thumbnail-icon {
  width: 24px;
  height: 24px;
  color: white;
}

/* 不同类型模块的缩略图背景色 */
.preview-thumbnail-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.preview-thumbnail-text .preview-thumbnail-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.preview-thumbnail-video {
  background: #1f2937;
}

.preview-thumbnail-video .preview-thumbnail-content {
  background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
}

.preview-thumbnail-code {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.preview-thumbnail-code .preview-thumbnail-content {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.preview-thumbnail-activity {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.preview-thumbnail-activity .preview-thumbnail-content {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.preview-thumbnail-default {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
}

.preview-thumbnail-default .preview-thumbnail-content {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
}

/* 文本预览（紧凑版） */
.preview-text-compact {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.preview-text-snippet {
  @apply text-xs text-gray-600;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
}

.preview-text-snippet :deep(p) {
  margin: 0;
  display: inline;
}

/* 图标预览（紧凑版） */
.preview-video-compact,
.preview-code-compact,
.preview-activity-compact,
.preview-default-compact {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
}

.preview-icon-small {
  width: 32px;
  height: 32px;
  @apply text-gray-400;
}

.preview-icon-wrapper-small {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  @apply text-gray-400;
}

.preview-icon-label {
  @apply text-xs text-gray-500;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

/* 更多模块提示（紧凑版） */
.preview-more-compact {
  @apply bg-gradient-to-br from-gray-100 to-gray-200 border-dashed border-2 border-gray-300;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80px;
}

.preview-more-content-compact {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  @apply text-gray-500;
}

.preview-more-icon {
  @apply text-xl font-bold;
}

.preview-more-text-compact {
  @apply text-xs;
}

/* 实时数据部分样式已合并到监控模块中 */

.preview-item {
  @apply bg-gray-50 border border-gray-200 rounded-xl p-4;
  transition: all 0.2s ease;
  min-height: 180px;
  display: flex;
  flex-direction: column;
}

.preview-item:hover {
  @apply border-gray-300 shadow-md;
  transform: translateY(-2px);
}

.preview-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  gap: 8px;
}

.preview-item-badge {
  @apply text-sm font-semibold text-gray-900;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview-item-type {
  @apply text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded;
  flex-shrink: 0;
}

.preview-item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 文本预览 */
.preview-text-content {
  flex: 1;
  @apply bg-white rounded-lg p-3 border border-gray-200;
  max-height: 120px;
  overflow-y: auto;
}

.preview-text-html {
  @apply text-sm text-gray-700;
  line-height: 1.6;
}

.preview-text-html :deep(p) {
  margin: 0 0 8px 0;
}

.preview-text-html :deep(p:last-child) {
  margin-bottom: 0;
}

/* 视频预览 */
.preview-video-content {
  flex: 1;
  @apply bg-gray-900 rounded-lg flex items-center justify-center;
  min-height: 120px;
}

.preview-video-thumbnail {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  @apply text-white;
}

.preview-video-icon {
  width: 48px;
  height: 48px;
}

.preview-video-title {
  @apply text-sm font-medium;
  text-align: center;
  padding: 0 12px;
}

/* 代码预览 */
.preview-code-content {
  flex: 1;
  @apply bg-gray-900 rounded-lg p-3;
  max-height: 120px;
  overflow-y: auto;
}

.preview-code-snippet {
  @apply text-xs text-green-400 font-mono;
  line-height: 1.5;
}

.preview-code-snippet code {
  @apply text-green-400;
}

/* 活动预览 */
.preview-activity-content {
  flex: 1;
  @apply bg-purple-50 rounded-lg flex items-center justify-center;
  min-height: 120px;
}

.preview-activity-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  @apply text-purple-700;
}

.preview-activity-icon {
  width: 40px;
  height: 40px;
}

/* 流程图预览 */
.preview-flowchart-content {
  flex: 1;
  @apply bg-indigo-50 rounded-lg flex items-center justify-center;
  min-height: 120px;
}

.preview-flowchart-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  @apply text-indigo-700;
}

.preview-flowchart-icon {
  width: 40px;
  height: 40px;
}

/* 默认预览 */
.preview-default-content {
  flex: 1;
  @apply bg-gray-100 rounded-lg flex flex-col items-center justify-center gap-3;
  min-height: 120px;
}

.preview-default-icon {
  @apply text-gray-400;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-default-text {
  @apply text-sm text-gray-600;
}

/* 更多模块提示 */
.preview-item-more {
  @apply bg-gradient-to-br from-gray-100 to-gray-200 border-dashed border-2 border-gray-300;
  justify-content: center;
  align-items: center;
}

.preview-more-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  @apply text-gray-500;
}

.preview-more-text {
  @apply text-2xl font-bold;
}

.preview-more-label {
  @apply text-xs;
}

/* ⚠️ 预警提示栏 */
.alert-bar {
  padding: 12px 24px;
  @apply border-b border-gray-200;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: all 0.3s ease;
}

.alert-bar.has-alerts {
  @apply bg-yellow-50 border-yellow-200;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.alert-warning {
  @apply bg-orange-50 text-orange-800 border border-orange-200;
}

.alert-info {
  @apply bg-blue-50 text-blue-800 border border-blue-200;
}

.alert-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.alert-action {
  margin-left: auto;
  padding: 4px 12px;
  @apply bg-white border border-current rounded-md text-sm font-medium;
  cursor: pointer;
  transition: all 0.2s ease;
}

.alert-action:hover {
  @apply bg-opacity-80;
}

/* 顶部标题栏（保留兼容性） */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 24px;
  @apply bg-white border border-gray-200 rounded-lg;
}

.panel-title {
  font-size: 24px;
  font-weight: bold;
  @apply text-gray-900;
  margin: 0;
}

/* 标题与模式切换按钮容器 */
.title-with-mode-toggle {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 紧凑版模式切换按钮 */
.mode-toggle-btn-compact {
  @apply px-2.5 py-1 text-xs font-medium rounded-md transition-all;
  @apply flex items-center justify-center;
  @apply border cursor-pointer;
  @apply disabled:opacity-50 disabled:cursor-not-allowed;
  @apply shadow-sm;
  min-width: 60px;
  height: 28px;
}

.mode-toggle-btn-compact.mode-single {
  @apply bg-blue-50 text-blue-700 border-blue-300 hover:bg-blue-100 hover:border-blue-400;
}

.mode-toggle-btn-compact.mode-multi {
  @apply bg-purple-50 text-purple-700 border-purple-300 hover:bg-purple-100 hover:border-purple-400;
}

.mode-toggle-btn-compact:hover:not(:disabled) {
  @apply shadow-md transform scale-105;
}

.mode-toggle-btn-compact:active:not(:disabled) {
  @apply transform scale-95;
}

.header-controls {
  display: flex;
  gap: 12px;
}

/* 主布局 - 单栏：仅显示教学模块 */
.main-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  margin-bottom: 16px;
  padding: 16px;
  position: relative;
  align-items: start;
  min-height: auto;
  width: 100%;
  max-width: 100%;
  overflow: hidden;
  box-sizing: border-box;
}

/* 确保教学模块面板能够正常显示 */
.main-layout .teaching-modules {
  width: 100% !important;
  max-width: 100% !important;
  overflow: visible;
  box-sizing: border-box;
  /* 确保面板占据全宽 */
  flex: 1 1 100%;
  /* 确保在 grid 中占据全宽 */
  grid-column: 1 / -1;
  min-width: 0;
}

/* 模块面板全屏模式时的布局 */
.main-layout.module-fullscreen-mode {
  grid-template-columns: 1fr !important;
  transition: grid-template-columns 0.3s ease;
}

.main-layout.module-fullscreen-mode .teaching-modules {
  height: auto !important;
  min-height: auto !important;
  max-height: none !important;
}

/* 通用面板样式 */
.panel {
  @apply bg-white rounded-lg border border-gray-200 p-4;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box;
  overflow: visible;
  /* 确保面板占据全宽 */
  flex: 1 1 100%;
  min-width: 0;
}

.panel h3.panel-title {
  font-size: 16px;
  font-weight: 600;
  @apply text-gray-900;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  @apply border-b border-gray-200;
}

/* 左侧：教学模块 */
.teaching-modules {
  display: flex;
  flex-direction: column;
  height: auto;
  min-height: auto;
  max-height: none;
  overflow: visible;
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box;
  /* 确保占据全宽 */
  flex: 1 1 100%;
  min-width: 0;
}

/* 教学模块全宽模式 - 减少 padding 以充分利用空间 */
.teaching-modules-fullwidth {
  padding-left: 12px !important;
  padding-right: 12px !important;
  padding-top: 12px !important;
  padding-bottom: 12px !important;
}

.module-panel-fullscreen {
  height: calc(100vh - 48px) !important;
  min-height: auto !important;
  max-height: calc(100vh - 48px) !important;
}

.module-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 8px;
  @apply border-b border-gray-200;
  flex-shrink: 0;
}

.module-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.module-header-actions {
  display: flex;
  gap: 8px;
}

.module-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  @apply bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.module-action-btn:hover {
  @apply bg-gray-200;
  transform: scale(1.05);
}

.module-count {
  font-size: 12px;
  @apply text-gray-600;
}

.module-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 8px;
  padding-bottom: 8px;
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box;
  /* 网格自动换行，无需横向滚动 */
  align-items: stretch;
  /* 限制只显示2行，超出部分可垂直滚动 */
  max-height: calc(52px * 2 + 8px); /* 2行高度：每行52px + 1个gap 8px */
  overflow-y: auto;
  overflow-x: hidden;
}

.module-list::-webkit-scrollbar {
  width: 6px;
}

.module-list::-webkit-scrollbar-track {
  @apply bg-gray-100;
  border-radius: 3px;
}

.module-list::-webkit-scrollbar-thumb {
  @apply bg-gray-400;
  border-radius: 3px;
}

.module-list::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-500;
}

.module-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  padding-right: 36px; /* 为单选框预留空间（已缩小） */
  @apply bg-white border-2 border-gray-200 rounded-lg;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 52px;
  height: auto;
  width: 100%; /* 网格项自动填充列宽 */
  min-width: 0; /* 允许在网格中收缩 */
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  box-sizing: border-box;
}

/* 全屏模式下模块项可以更大 */
.module-panel-fullscreen .module-item {
  min-height: 60px;
  height: auto;
  padding: 10px 12px;
  gap: 8px;
}

.module-panel-fullscreen .module-item-icon {
  width: 32px;
  height: 32px;
}

.module-panel-fullscreen .module-item-title {
  font-size: 13px;
}

.module-item:hover:not(.module-item-disabled) {
  @apply border-gray-300 shadow-lg;
  transform: translateY(-2px);
}

.module-item-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 不同类型模块的颜色主题 */
.module-item-type-video {
  @apply border-blue-200 bg-blue-50;
}

.module-item-type-video:hover:not(.module-item-disabled) {
  @apply border-blue-300 bg-blue-100;
}

.module-item-type-text {
  @apply border-amber-300 bg-amber-50;
  border-width: 2px;
}

.module-item-type-text:hover:not(.module-item-disabled) {
  @apply border-amber-400 bg-amber-100;
}

.module-item-type-browser {
  @apply border-cyan-300 bg-cyan-100;
  border-width: 2px;
}

.module-item-type-browser:hover:not(.module-item-disabled) {
  @apply border-cyan-400 bg-cyan-200;
}

.module-item-type-activity {
  @apply border-purple-200 bg-purple-50;
}

.module-item-type-activity:hover:not(.module-item-disabled) {
  @apply border-purple-300 bg-purple-100;
}

.module-item-type-code {
  @apply border-green-200 bg-green-50;
}

.module-item-type-code:hover:not(.module-item-disabled) {
  @apply border-green-300 bg-green-100;
}

.module-item-type-flowchart {
  @apply border-indigo-200 bg-indigo-50;
}

.module-item-type-flowchart:hover:not(.module-item-disabled) {
  @apply border-indigo-300 bg-indigo-100;
}

.module-item-type-qa {
  @apply border-yellow-200 bg-yellow-50;
}

.module-item-type-qa:hover:not(.module-item-disabled) {
  @apply border-yellow-300 bg-yellow-100;
}

/* 激活状态 */
.module-item-active {
  @apply shadow-xl ring-4 ring-offset-2;
  transform: translateY(-2px) scale(1.02);
  z-index: 10;
}

.module-item-type-video.module-item-active {
  @apply bg-blue-500 border-blue-600 ring-blue-300;
}

.module-item-type-text.module-item-active {
  @apply bg-amber-500 border-amber-600 ring-amber-300;
}

.module-item-type-browser.module-item-active {
  @apply bg-cyan-500 border-cyan-600 ring-cyan-300;
}

.module-item-type-activity.module-item-active {
  @apply bg-purple-500 border-purple-600 ring-purple-300;
}

.module-item-type-code.module-item-active {
  @apply bg-green-500 border-green-600 ring-green-300;
}

.module-item-type-flowchart.module-item-active {
  @apply bg-indigo-500 border-indigo-600 ring-indigo-300;
}

.module-item-type-qa.module-item-active {
  @apply bg-yellow-500 border-yellow-600 ring-yellow-300;
}

/* 激活状态下的 hover 效果 - 保持深色背景以确保白色文字可见 */
.module-item-type-video.module-item-active:hover:not(.module-item-disabled) {
  @apply bg-blue-600 border-blue-700 ring-blue-400;
}

.module-item-type-text.module-item-active:hover:not(.module-item-disabled) {
  @apply bg-amber-600 border-amber-700 ring-amber-400;
}

.module-item-type-browser.module-item-active:hover:not(.module-item-disabled) {
  @apply bg-cyan-600 border-cyan-700 ring-cyan-400;
}

.module-item-type-activity.module-item-active:hover:not(.module-item-disabled) {
  @apply bg-purple-600 border-purple-700 ring-purple-400;
}

.module-item-type-code.module-item-active:hover:not(.module-item-disabled) {
  @apply bg-green-600 border-green-700 ring-green-400;
}

.module-item-type-flowchart.module-item-active:hover:not(.module-item-disabled) {
  @apply bg-indigo-600 border-indigo-700 ring-indigo-400;
}

.module-item-type-qa.module-item-active:hover:not(.module-item-disabled) {
  @apply bg-yellow-600 border-yellow-700 ring-yellow-400;
}

.module-item-hidden {
  @apply bg-orange-50 border-orange-200;
  /* 隐藏按钮在网格中自适应宽度 */
  width: 100%;
  min-width: 0;
  padding: 8px 10px;
  justify-content: center;
  gap: 6px;
}

.module-item-hidden .module-item-icon {
  flex-shrink: 0;
}

.module-item-hidden .module-item-label {
  flex-shrink: 0;
  white-space: nowrap;
  font-size: 13px;
  font-weight: 500;
}

/* 导航控制栏（固定在模块列表上方） */
.module-navigation-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

/* 导航按钮样式 */
.module-nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  @apply bg-blue-50 border border-blue-200 rounded-lg;
  @apply text-blue-700 font-medium text-sm;
  cursor: pointer;
  transition: all 0.2s ease;
  flex: 1;
  min-width: 0;
}

.module-nav-btn:hover:not(:disabled) {
  @apply bg-blue-100 border-blue-300;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.module-nav-btn:active:not(:disabled) {
  transform: translateY(0);
}

.module-nav-btn:disabled,
.module-nav-btn.module-nav-btn-disabled {
  @apply bg-gray-100 border-gray-200 text-gray-400 cursor-not-allowed opacity-60;
}

.module-nav-btn:disabled:hover,
.module-nav-btn.module-nav-btn-disabled:hover {
  transform: none;
  box-shadow: none;
}

.module-nav-btn svg {
  flex-shrink: 0;
}

.module-item-hidden:hover:not(.module-item-disabled) {
  @apply bg-orange-100 border-orange-300;
}

.module-item-hidden.module-item-active {
  @apply bg-orange-500 border-orange-600 ring-orange-300;
}

.module-item-hidden.module-item-active:hover:not(.module-item-disabled) {
  @apply bg-orange-600 border-orange-700 ring-orange-400;
}

.module-item-number {
  @apply absolute -top-2 -left-2 w-6 h-6 rounded-full;
  @apply flex items-center justify-center text-xs font-bold;
  @apply bg-white border-2 border-gray-300 text-gray-700;
  @apply shadow-sm;
  z-index: 2;
  transition: all 0.3s ease;
  flex-shrink: 0;
  font-size: 11px;
}

.module-item-type-video .module-item-number {
  @apply border-blue-400 text-blue-600;
}

.module-item-type-activity .module-item-number {
  @apply border-purple-400 text-purple-600;
}

.module-item-type-code .module-item-number {
  @apply border-green-400 text-green-600;
}

.module-item-type-flowchart .module-item-number {
  @apply border-indigo-400 text-indigo-600;
}

.module-item-type-qa .module-item-number {
  @apply border-yellow-400 text-yellow-600;
}

.module-item-type-text .module-item-number {
  @apply border-amber-500 text-amber-700;
}

.module-item-type-browser .module-item-number {
  @apply border-cyan-500 text-cyan-700;
}

.module-item-active .module-item-number {
  @apply bg-white scale-110 shadow-lg;
}

.module-item-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  @apply bg-white border-2 rounded-md;
  flex-shrink: 0;
  transition: all 0.3s ease;
  /* 增强图标可见性 */
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* 不同类型图标的边框颜色 */
.module-item-icon.icon-text {
  @apply border-amber-300;
}

.module-item-icon.icon-code {
  @apply border-green-300;
}

.module-item-icon.icon-activity {
  @apply border-purple-300;
}

.module-item-icon.icon-video {
  @apply border-blue-300;
}

.module-item-icon.icon-flowchart {
  @apply border-indigo-300;
}

.module-item-icon.icon-qa {
  @apply border-yellow-300;
}

.module-item-icon.icon-browser {
  @apply border-cyan-300;
}

.module-item-icon.icon-interactive {
  @apply border-purple-400;
}

.module-item-icon.icon-reference_material {
  @apply border-slate-300;
}

.module-item-active .module-item-icon {
  @apply bg-white scale-110;
  border-color: transparent;
}

.icon-text {
  @apply text-amber-700;
}

.icon-browser {
  @apply text-cyan-600;
}

.icon-video {
  @apply text-blue-600;
}

.icon-activity {
  @apply text-purple-600;
}

.icon-code {
  @apply text-green-600;
}

.icon-flowchart {
  @apply text-indigo-600;
}

.icon-qa {
  @apply text-yellow-600;
}

.icon-interactive {
  @apply text-purple-600;
}

.icon-reference_material {
  @apply text-slate-600;
}

.module-item-active .module-item-icon {
  @apply text-white;
}

.module-item-content {
  flex: 1;
  min-width: 0;
  padding-right: 4px; /* 紧凑模式下减少预留空间 */
  overflow: hidden; /* 确保文字不会溢出 */
}

.module-item-title {
  font-size: 13px;
  font-weight: 600;
  @apply text-gray-800;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: all 0.3s ease;
  max-width: 100%; /* 确保不超过容器 */
  line-height: 1.3;
}

.module-item-subtitle {
  /* 紧凑模式下隐藏副标题以提升信息密度 */
  display: none;
  font-size: 11px;
  @apply text-gray-500;
  transition: all 0.3s ease;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
  line-height: 1.2;
}

.module-item-active .module-item-title,
.module-item-active .module-item-subtitle {
  @apply text-white font-semibold;
}


.module-item-activity-badge {
  position: absolute;
  bottom: 6px;
  right: 6px;
  padding: 2px 6px;
  @apply bg-purple-500 text-white rounded-full;
  font-size: 9px;
  font-weight: 600;
  white-space: nowrap;
  animation: pulse-badge 2s infinite;
}


/* 单选框样式 */
.module-item-checkbox {
  @apply absolute bottom-1.5 right-1.5 z-10;
  @apply bg-white rounded-md shadow-sm p-0.5;
  transition: all 0.3s ease;
  min-width: 24px;
  min-height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  /* 确保单选框不会遮挡内容 */
  pointer-events: auto;
}

.module-item-checkbox:hover {
  @apply shadow-lg scale-110;
  @apply bg-gray-50;
}

.checkbox-input {
  @apply w-4 h-4 cursor-pointer;
  @apply border-2 border-gray-400;
  @apply focus:ring-2 focus:ring-blue-500 focus:ring-offset-2;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

/* 单选框样式（圆形） */
input[type="radio"].checkbox-input {
  @apply rounded-full;
}

/* 复选框样式（方形） */
input[type="checkbox"].checkbox-input {
  @apply rounded;
}

.module-item-type-video .checkbox-input:checked {
  accent-color: #3b82f6;
}

.module-item-type-activity .checkbox-input:checked {
  accent-color: #a855f7;
}

.module-item-type-code .checkbox-input:checked {
  accent-color: #22c55e;
}

.module-item-type-flowchart .checkbox-input:checked {
  accent-color: #6366f1;
}

.module-item-type-qa .checkbox-input:checked {
  accent-color: #eab308;
}

.module-item-type-text .checkbox-input:checked {
  accent-color: #f59e0b;
}

.module-item-type-browser .checkbox-input:checked {
  accent-color: #06b6d4;
}

.checkbox-input:disabled {
  @apply cursor-not-allowed opacity-50;
}

@keyframes pulse-badge {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}

.module-empty {
  text-align: center;
  padding: 40px 20px;
  @apply text-gray-500;
}

/* 中间：课堂监控 */
/* 监控模块样式已在上面定义 */

.monitoring-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.student-indicators {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 12px;
}

.indicator-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  @apply bg-gray-50 border border-gray-200 rounded-lg;
  transition: all 0.2s ease;
}

.indicator-item:hover {
  @apply bg-gray-100 border-gray-300;
}

.indicator-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  @apply border-2 border-gray-300;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.indicator-student-info {
  flex: 1;
  min-width: 0;
}

.indicator-student-name {
  @apply text-sm font-medium text-gray-900;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.indicator-student-account {
  @apply text-xs text-gray-500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.indicator-student-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  width: 100%;
}

.indicator-progress-bar {
  flex: 1;
  height: 4px;
  @apply bg-gray-200 rounded-full overflow-hidden;
}

.indicator-progress-fill {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 4px;
}

.indicator-progress-fill.indicator-green {
  @apply bg-green-500;
}

.indicator-progress-fill.indicator-yellow {
  @apply bg-yellow-500;
}

.indicator-progress-fill.indicator-red {
  @apply bg-red-500;
}

.indicator-progress-text {
  @apply text-xs text-gray-600 font-medium;
  min-width: 35px;
  text-align: right;
}

.indicator-empty-text {
  @apply text-gray-400;
}

.indicator-item.student-behind {
  @apply bg-orange-50 border-orange-200;
}

.indicator-green {
  @apply bg-green-500 border-green-600;
}

.indicator-yellow {
  @apply bg-yellow-500 border-yellow-600;
}

.indicator-red {
  @apply bg-red-500 border-red-600;
}

.indicator-empty {
  @apply bg-gray-200 border-gray-300;
  opacity: 0.5;
}

/* 学生列表样式 */
.student-list-extra {
  margin-top: 12px;
  margin-bottom: 12px;
  @apply border-t border-gray-200 pt-3;
}

.student-list-header {
  margin-bottom: 8px;
}

.student-list-title {
  @apply text-sm font-semibold text-gray-700;
}

.student-list-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  padding-right: 4px;
}

.student-list-content::-webkit-scrollbar {
  width: 4px;
}

.student-list-content::-webkit-scrollbar-track {
  @apply bg-gray-100;
  border-radius: 2px;
}

.student-list-content::-webkit-scrollbar-thumb {
  @apply bg-gray-300;
  border-radius: 2px;
}

.student-list-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  @apply bg-gray-50 border border-gray-200 rounded-lg;
  transition: all 0.2s ease;
}

.student-list-item:hover {
  @apply bg-gray-100 border-gray-300;
}

.student-list-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.student-list-item.indicator-green .student-list-indicator {
  @apply bg-green-500;
}

.student-list-item.indicator-yellow .student-list-indicator {
  @apply bg-yellow-500;
}

.student-list-item.indicator-red .student-list-indicator {
  @apply bg-red-500;
}

.student-list-info {
  flex: 1;
  min-width: 0;
}

.student-list-name {
  @apply text-sm font-medium text-gray-900;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.student-list-account {
  @apply text-xs text-gray-500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.student-list-progress {
  @apply text-xs font-semibold text-gray-600;
  flex-shrink: 0;
  min-width: 40px;
  text-align: right;
}

.student-progress-bar-container {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 120px;
}

.student-progress-bar {
  flex: 1;
  height: 6px;
  @apply bg-gray-200 rounded-full overflow-hidden;
}

.student-progress-fill {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 4px;
}

.student-progress-fill.indicator-green {
  @apply bg-green-500;
}

.student-progress-fill.indicator-yellow {
  @apply bg-yellow-500;
}

.student-progress-fill.indicator-red {
  @apply bg-red-500;
}

.student-list-item.student-behind {
  @apply bg-orange-50 border-orange-300;
}

.students-behind-section {
  margin-top: 12px;
  margin-bottom: 12px;
  @apply border-t border-orange-200 pt-3;
}

.students-behind-section .student-list-header {
  @apply mb-3;
}

.students-behind-section .student-list-title {
  @apply text-orange-700 font-semibold;
}

.student-list-empty {
  margin-top: 16px;
  margin-bottom: 16px;
  text-align: center;
}

.monitoring-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
  @apply border-t border-gray-200 pt-4;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  @apply border-b border-gray-200;
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-label {
  @apply text-gray-600;
  font-size: 14px;
}

.stat-value {
  @apply text-gray-900;
  font-size: 18px;
  font-weight: 600;
}

/* 实时数据样式已合并到监控模块中 */

.data-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  @apply bg-white border border-gray-200 rounded-lg;
  @apply text-gray-600;
  flex-shrink: 0;
}

.data-icon-red {
  @apply text-red-600;
}

.data-icon-green {
  @apply text-green-600;
}

.data-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.data-label {
  @apply text-gray-600;
  font-size: 12px;
}

.data-value {
  @apply text-gray-900;
  font-size: 18px;
  font-weight: 600;
}

.progress-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.progress-item {
  height: 8px;
  @apply bg-gray-200;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-purple {
  background: linear-gradient(90deg, #a855f7 0%, #9333ea 100%);
}

.progress-lavender {
  background: linear-gradient(90deg, #c084fc 0%, #a855f7 100%);
}

.progress-green {
  background: linear-gradient(90deg, #22c55e 0%, #16a34a 100%);
}

/* 按钮样式 */
.btn {
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #3b82f6;
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-secondary {
  @apply bg-gray-100 text-gray-700;
}

.btn-secondary:hover:not(:disabled) {
  @apply bg-gray-200;
}

.btn-danger {
  background: #ef4444;
  color: #ffffff;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .main-layout {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .panel {
    padding: 16px;
  }
  
  .teaching-modules {
    height: auto;
    min-height: auto;
    max-height: none;
  }
}

@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .header-controls {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .module-buttons {
    gap: 12px;
  }
  
  .module-btn {
    padding: 16px;
  }
  
  .student-indicators {
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }
  
  .indicator-circle {
    width: 40px;
    height: 40px;
  }
}

.session-status-bar {
  @apply rounded-lg p-5 border-2 shadow-sm;
}

.session-status-bar.status-active {
  @apply bg-green-50 border-green-300;
}

.session-status-bar.status-paused {
  @apply bg-yellow-50 border-yellow-300;
}

.session-status-bar.status-pending {
  @apply bg-gray-50 border-gray-300;
}

.status-content {
  @apply flex items-center gap-5;
}

.status-indicator {
  @apply flex items-center justify-center w-12 h-12 rounded-full;
}

.pulse-dot {
  @apply w-4 h-4 bg-green-600 rounded-full animate-pulse;
}

.status-text {
  @apply flex-1 flex flex-col gap-1.5;
}

.status-title {
  @apply text-lg font-semibold text-gray-900 leading-tight;
}

.duration {
  @apply flex items-center gap-2 text-sm;
}

.duration-label {
  @apply text-gray-600;
}

.duration-value {
  @apply font-mono font-semibold text-gray-900 text-base;
}

.duration-value.duration-warning {
  @apply text-orange-600;
}

.duration-value.duration-danger {
  @apply text-red-600 animate-pulse;
}

.control-actions {
  @apply flex gap-3;
}

.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}

.btn-secondary {
  @apply bg-gray-100 text-gray-700 hover:bg-gray-200;
}

.btn-danger {
  @apply bg-red-600 text-white hover:bg-red-700;
}

.btn-display-mode {
  @apply bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-300;
  @apply flex items-center justify-center gap-1;
}

.btn-display-mode.active {
  @apply bg-blue-100 text-blue-700 border-blue-400;
}

.btn-fullscreen {
  @apply bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-300;
  @apply flex items-center justify-center gap-1;
}

.btn-fullscreen:hover {
  @apply bg-gray-200;
}

.display-mode-controls {
  @apply flex items-center;
}

.btn-lg {
  @apply px-6 py-3 text-lg;
}

.btn-sm {
  @apply px-3 py-1 text-sm;
}

.students-panel,
.content-control {
  @apply border border-gray-200 rounded-lg p-4;
}

.panel-header {
  @apply flex items-center justify-between mb-4 pb-2 border-b border-gray-200;
}

.panel-header h4 {
  @apply text-lg font-semibold text-gray-900;
}

.panel-stats {
  @apply flex items-center gap-3;
}

.stat-badge {
  @apply flex items-center gap-1.5 px-2.5 py-1 bg-gray-100 rounded-md text-sm;
}

.stat-label {
  @apply text-gray-600;
}

.stat-value {
  @apply font-semibold text-gray-900;
}

.loading-state {
  @apply flex flex-col items-center justify-center py-8;
}

.spinner {
  @apply w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-2;
}

.students-grid {
  @apply grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3;
}

.student-card {
  @apply flex items-center gap-3 p-3 border border-gray-200 rounded-lg bg-white hover:shadow-md transition-shadow;
}

.student-card.at-current-cell {
  @apply border-blue-400 bg-blue-50;
}

.student-avatar {
  @apply w-10 h-10 rounded-full bg-blue-500 text-white flex items-center justify-center font-semibold;
}

.student-info {
  @apply flex-1 min-w-0;
}

.student-name {
  @apply text-sm font-medium text-gray-900 truncate;
}

.student-progress {
  @apply flex items-center gap-2 mt-1;
}

.progress-bar-mini {
  @apply flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden;
}

.progress-fill {
  @apply h-full bg-blue-500 transition-all duration-300;
}

.progress-text {
  @apply text-xs text-gray-600 whitespace-nowrap;
}

.sync-indicator {
  @apply text-green-600 font-bold;
}

.empty-students {
  @apply text-center py-8 text-gray-500;
}

.waiting-students-panel {
  @apply bg-blue-50 border-2 border-blue-200 rounded-lg p-6 space-y-4;
}

.waiting-header {
  @apply flex items-start gap-4;
}

.waiting-icon {
  @apply text-4xl;
}

.waiting-content {
  @apply flex-1;
}

.waiting-title {
  @apply text-xl font-bold text-gray-900 mb-1;
}

.waiting-subtitle {
  @apply text-sm text-gray-600;
}

.waiting-stats {
  @apply flex items-center gap-6 pt-4 border-t border-blue-200;
}

.stat-item {
  @apply flex items-center gap-2;
}

.stat-label {
  @apply text-sm text-gray-600;
}

.stat-value {
  @apply text-lg font-semibold text-gray-900;
}

.stat-value.highlight {
  @apply text-blue-600 text-2xl;
}

.content-control {
  @apply space-y-4;
}

.control-board-preview {
  @apply bg-white rounded-lg border border-gray-200 p-6;
}

.control-board-preview .board-header {
  @apply flex items-center justify-between mb-6 pb-4 border-b border-gray-200;
}

.control-board-preview .board-title {
  @apply text-lg font-semibold text-gray-900;
}

.control-board-preview .board-stats {
  @apply flex items-center gap-4 text-sm text-gray-600;
}

.control-board-preview .stat-item {
  @apply px-2 py-1 bg-gray-100 rounded;
}

.control-board-preview .control-chain {
  @apply flex items-center;
  overflow-x: auto;
  padding: 1rem 0;
}

.control-board-preview .chain-node {
  @apply flex flex-col items-center justify-center relative;
  @apply min-w-[80px] w-[80px] p-3 rounded-lg;
  @apply bg-gray-50 border-2 border-gray-200;
  flex-shrink: 0;
}

.chain-node-preview {
  @apply opacity-60 cursor-default;
  pointer-events: none;
}

.control-board-preview .node-number {
  @apply absolute -top-2 -left-2 w-6 h-6 bg-gray-600 text-white rounded-full;
  @apply flex items-center justify-center text-xs font-bold;
}

.control-board-preview .node-icon {
  @apply w-10 h-10 flex items-center justify-center;
  @apply text-gray-600 mb-2;
}

.control-board-preview .node-label {
  @apply text-xs text-center text-gray-700 font-medium;
  @apply line-clamp-2;
  max-width: 100%;
}

.control-board-preview .chain-connector {
  @apply flex-shrink-0;
  width: 2rem;
  height: 2px;
  background: linear-gradient(to right, #e5e7eb, #9ca3af);
  margin: 0 0.5rem;
}

.current-cell-info {
  @apply mt-4 p-3 bg-gray-50 rounded-lg;
}

.cell-header {
  @apply flex items-center gap-2 mb-2;
}

.cell-type-badge {
  @apply px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded;
}

.cell-title {
  @apply text-sm font-medium text-gray-900;
}

.activity-control {
  @apply mt-3;
}

/* 响应式布局 */
@media (max-width: 1600px) {
  .main-layout {
    grid-template-columns: 1.8fr 1.3fr 1.8fr;
  }
}

@media (max-width: 1400px) {
  .main-layout {
    grid-template-columns: 1.5fr 1.2fr 1.5fr;
  }
  
  .stats-grid-compact {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1200px) {
  .main-layout {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
}

@media (max-width: 768px) {
  .top-control-metrics {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .student-indicators {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stats-grid-compact {
    grid-template-columns: 1fr;
  }
  
  /* 移动端导航栏 */
  .module-navigation-bar {
    gap: 6px;
    margin-bottom: 10px;
    padding-bottom: 10px;
  }
  
  .module-nav-btn {
    padding: 6px 12px;
    font-size: 12px;
    gap: 4px;
  }
  
  .module-nav-btn svg {
    width: 14px;
    height: 14px;
  }
  
  /* 移动端网格自动调整为更少的列数 */
  .module-list {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 6px;
    /* 移动端也限制为2行 */
    max-height: calc(48px * 2 + 6px); /* 2行高度：每行48px + 1个gap 6px */
  }
  
  .module-item {
    padding: 6px 8px;
    padding-right: 32px;
    min-height: 48px;
    gap: 5px;
  }
  
  .module-item-icon {
    width: 24px;
    height: 24px;
  }
  
  .module-item-title {
    font-size: 12px;
  }
}

/* 等待学生加入提示区域 */
.waiting-students-banner {
  @apply bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 border-b-2 border-blue-200 shadow-sm;
  padding: 20px 24px;
  margin-bottom: 16px;
}

.waiting-banner-content {
  @apply flex items-center gap-4;
}

.waiting-banner-icon {
  @apply text-4xl;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.waiting-banner-text {
  @apply flex-1;
}

.waiting-banner-title {
  @apply text-lg font-bold text-gray-900 mb-1 flex items-center gap-2;
}

.student-count-badge {
  @apply px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800;
}

.waiting-banner-subtitle {
  @apply text-sm text-gray-600;
}

.joined-students-list {
  @apply mt-4 pt-4 border-t border-blue-200;
}

.joined-students-header {
  @apply mb-3;
}

.joined-students-title {
  @apply text-sm font-semibold text-gray-700;
}

.joined-students-grid {
  @apply grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-12 gap-3;
}

.joined-student-item {
  @apply flex flex-col items-center gap-2 p-2 rounded-lg bg-white border border-gray-200 hover:border-blue-400 hover:shadow-sm transition-all;
}

.joined-student-item.joined-student-more {
  @apply bg-gray-50 border-dashed;
}

.student-avatar {
  @apply w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 text-white flex items-center justify-center font-semibold text-sm shadow-sm;
}

.joined-student-more .student-avatar {
  @apply bg-gray-400;
}

.student-name {
  @apply text-xs text-gray-700 text-center truncate w-full;
  max-width: 80px;
}

.btn-disabled-hint {
  @apply opacity-60 cursor-not-allowed;
}

@media (max-width: 768px) {
  .joined-students-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

</style>

