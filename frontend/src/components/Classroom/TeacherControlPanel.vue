<template>
  <div class="teacher-control-panel">
    <!-- 会话状态栏 -->
    <div class="session-status-bar" :class="statusClass">
      <div class="status-content">
        <div class="status-indicator">
          <span v-if="session?.status === 'active'" class="pulse-dot"></span>
          <span v-else-if="session?.status === 'paused'" class="pause-icon">⏸️</span>
          <span v-else class="pending-icon">⏸️</span>
        </div>
        <div class="status-text">
          <h3 class="status-title">{{ statusTitle }}</h3>
          <p v-if="session?.status === 'active' && sessionDuration !== null && sessionDuration !== undefined" class="duration">
            <span class="duration-label">剩余时间:</span>
            <span class="duration-value" :class="{ 'duration-warning': remainingTime <= 300, 'duration-danger': remainingTime <= 60 }">
              {{ formatRemainingTime(remainingTime) }}
            </span>
          </p>
          <p v-else-if="session?.status === 'paused' && sessionDuration !== null && sessionDuration !== undefined" class="duration">
            <span class="duration-label">剩余时间:</span>
            <span class="duration-value">{{ formatRemainingTime(remainingTime) }}</span>
          </p>
          <p v-else-if="session?.status === 'pending'" class="pending-text">
            等待学生加入（{{ activeStudents.length }} 人已加入）
          </p>
        </div>
      </div>
    </div>

    <!-- 控制按钮组 -->
    <div class="control-actions">
      <!-- 没有会话时，显示"创建课堂"按钮 -->
      <button 
        v-if="!session"
        @click="handleCreateSession"
        :disabled="loading"
        class="btn btn-primary btn-lg"
      >
        📚 创建课堂
      </button>
      
      <!-- PENDING 状态：等待学生登录 -->
      <template v-if="session && session.status === 'pending'">
        <button 
          @click="handleBeginClass"
          :disabled="loading || activeStudents.length === 0"
          class="btn btn-primary btn-lg"
          :title="activeStudents.length === 0 ? '请等待学生加入课堂' : '开始上课'"
        >
          ▶️ 开始上课
        </button>
        <button 
          @click="handleCancelSession"
          :disabled="loading"
          class="btn btn-secondary"
        >
          ❌ 取消课堂
        </button>
      </template>
      
      <!-- ACTIVE 状态：上课中 -->
      <template v-if="session && session.status === 'active'">
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
          ⏹️ 结束课程
        </button>
      </template>
      
      <!-- PAUSED 状态：已暂停 -->
      <template v-if="session && session.status === 'paused'">
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
          ⏹️ 结束课程
        </button>
      </template>
    </div>
    
    <!-- 等待学生登录界面（PENDING 状态） -->
    <div v-if="session && session.status === 'pending'" class="waiting-students-panel">
      <div class="waiting-header">
        <div class="waiting-icon">⏳</div>
        <div class="waiting-content">
          <h3 class="waiting-title">等待学生加入课堂</h3>
          <p class="waiting-subtitle">学生加入后，点击"开始上课"按钮开始授课</p>
        </div>
      </div>
      
      <div class="waiting-stats">
        <div class="stat-item">
          <span class="stat-label">已加入学生</span>
          <span class="stat-value highlight">{{ activeStudents.length }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">总学生数</span>
          <span class="stat-value">{{ totalStudents }}</span>
        </div>
      </div>
    </div>

    <!-- 在线学生列表 -->
    <div v-if="session && (session.status === 'pending' || session.status === 'active' || session.status === 'paused')" class="students-panel">
      <div class="panel-header">
        <h4>在线学生</h4>
        <div class="panel-stats">
          <span class="stat-badge">
            <span class="stat-label">在线:</span>
            <span class="stat-value">{{ activeStudents.length }} / {{ totalStudents }}</span>
          </span>
          <span v-if="sessionStatistics" class="stat-badge">
            <span class="stat-label">已完成:</span>
            <span class="stat-value">{{ sessionStatistics.completed_students }}</span>
          </span>
          <span v-if="sessionStatistics" class="stat-badge">
            <span class="stat-label">平均进度:</span>
            <span class="stat-value">{{ Math.round(sessionStatistics.average_progress) }}%</span>
          </span>
        </div>
      </div>
      
      <div v-if="loadingStudents" class="loading-state">
        <div class="spinner"></div>
        <p>加载学生列表...</p>
      </div>
      
      <div v-else-if="activeStudents.length > 0" class="students-grid">
        <div 
          v-for="student in activeStudents" 
          :key="student.id"
          class="student-card"
          :class="{ 
            'at-current-cell': (student.currentCellId || student.current_cell_id) === (session.currentCellId || session.current_cell_id)
          }"
        >
          <div class="student-avatar">
            {{ (student.studentName || student.student_name)?.[0] || 'S' }}
          </div>
          <div class="student-info">
            <div class="student-name">{{ student.studentName || student.student_name }}</div>
            <div class="student-progress">
              <div class="progress-bar-mini">
                <div 
                  class="progress-fill" 
                  :style="{ width: `${student.progressPercentage || student.progress_percentage || 0}%` }"
                ></div>
              </div>
              <span class="progress-text">{{ Math.round(student.progressPercentage || student.progress_percentage || 0) }}%</span>
            </div>
          </div>
          <div v-if="(student.currentCellId || student.current_cell_id) === (session.currentCellId || session.current_cell_id)" class="sync-indicator">
            ✓
          </div>
        </div>
      </div>
      
      <div v-else class="empty-students">
        <p>暂无学生在线</p>
      </div>
    </div>

    <!-- 导播台 -->
    <div v-if="lesson && lesson.content && lesson.content.length > 0" class="content-control">
      <!-- 调试信息（开发时可见） -->
      <div v-if="!session" class="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div class="flex items-center gap-2 text-yellow-800">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="text-sm font-medium">请先开始上课以使用导播台</span>
        </div>
        <p class="text-xs text-yellow-600 mt-1">点击"开始上课"按钮创建课堂会话</p>
      </div>
      
      <!-- 有 session：显示实际控制板 -->
      <template v-if="session">
        <ClassroomControlBoard
          :cells="lesson.content"
          :current-cell-id="session.current_cell_id"
          :current-cell-index="selectedCellIndex"
          :current-activity-id="session.current_activity_id"
          :db-cells="dbCells"
          :loading="loading"
          @navigate-to-cell="handleControlBoardNavigate"
          @navigateToCell="handleControlBoardNavigate"
          @start-activity="handleStartActivity"
          @end-activity="handleEndActivity"
        />
        
        <!-- 调试信息（开发时可见） -->
        <div v-if="currentCell" class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-xs">
          <div class="font-semibold mb-2">🔍 调试信息:</div>
          <div>currentCell.type: {{ currentCell.type }}</div>
          <div>currentCell.order: {{ currentCell.order }}</div>
          <div>selectedCellIndex: {{ selectedCellIndex }}</div>
          <div>currentActivityDbCell: {{ currentActivityDbCell ? `ID=${currentActivityDbCell.id}` : 'null' }}</div>
          <div>dbCells.length: {{ dbCells.length }}</div>
          <div>dbCells: {{ JSON.stringify(dbCells.map(c => ({ id: c.id, order: c.order, type: c.cell_type }))) }}</div>
        </div>
        
        <!-- 活动统计面板（当前 Cell 是 activity 类型时显示） -->
        <div v-if="currentCell && currentCell.type === 'activity' && currentActivityDbCell" class="activity-panel mt-6">
          <SubmissionStatistics
            :cell-id="currentActivityDbCell.id"
            :lesson-id="lesson?.id || lessonId"
            :session-id="session.id"
          />
          
          <!-- 学生提交详细列表 -->
          <div class="mt-4">
            <SubmissionList
              :cell-id="currentActivityDbCell.id"
              :activity="currentCell.content"
              :session-id="session.id"
              :lesson-id="lesson?.id || lessonId"
            />
          </div>
        </div>
        
        <!-- 如果 currentCell 是 activity 但没有 currentActivityDbCell，显示提示 -->
        <div v-else-if="currentCell && currentCell.type === 'activity' && !currentActivityDbCell" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-red-800 font-semibold">⚠️ 无法显示统计信息</p>
          <p class="text-red-600 text-sm mt-2">原因：找不到对应的数据库 Cell 记录</p>
          <p class="text-red-600 text-xs mt-1">currentCell.order: {{ currentCell.order }}</p>
          <p class="text-red-600 text-xs">dbCells: {{ dbCells.length }} 条记录</p>
        </div>
      </template>
      
      <!-- 没有 session：显示预览模式（只读） -->
      <div v-else class="control-board-preview">
        <div class="board-header">
          <h4 class="board-title">📺 导播台（预览）</h4>
          <div class="board-stats">
            <span class="stat-item">共 {{ lesson.content.length }} 个模块</span>
          </div>
        </div>
        <div class="control-chain">
          <template v-for="(cell, index) in lesson.content" :key="cell.id || index">
            <div class="chain-node chain-node-preview">
              <div class="node-number">{{ index + 1 }}</div>
              <div class="node-icon">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </div>
              <div class="node-label">{{ cell.title || cell.type || `模块 ${index + 1}` }}</div>
            </div>
            <div v-if="index < lesson.content.length - 1" class="chain-connector"></div>
          </template>
        </div>
        <div class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
          💡 开始上课后，点击节点即可切换模块显示给学生
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { Lesson } from '../../types/lesson'
import type { Cell } from '../../types/cell'
import classroomSessionService from '../../services/classroomSession'
import ClassroomSwitcher from './ClassroomSwitcher.vue'
import ClassroomControlBoard from './ClassroomControlBoard.vue'
import SubmissionStatistics from '../Activity/SubmissionStatistics.vue'
import SubmissionList from '../Activity/Teacher/SubmissionList.vue'
import { getCellId as getCellIdUtil, buildNavigateRequest, toNumericId } from '../../utils/cellId'

interface Props {
  lessonId: number
  lesson?: Lesson
}

const props = defineProps<Props>()

const route = useRoute()
const session = ref<any>(null)
const loading = ref(false)
const activeStudents = ref<any[]>([])
const loadingStudents = ref(false)
const sessionStatistics = ref<any>(null)
const selectedCellIndex = ref(-1)  // -1表示隐藏所有内容
const sessionDuration = ref(0)
const durationInterval = ref<number | null>(null)
const dbCells = ref<Array<{ id: number; order: number; cell_type: string }>>([])  // 数据库中的 Cell 记录（用于 ID 匹配）

// 一节课的标准时长（40分钟 = 2400秒）
const LESSON_DURATION = 40 * 60

// 计算剩余时间
const remainingTime = computed(() => {
  if (sessionDuration.value === null || sessionDuration.value === undefined) return LESSON_DURATION
  const remaining = LESSON_DURATION - sessionDuration.value
  return remaining > 0 ? remaining : 0
})

// 计算属性
const statusTitle = computed(() => {
  if (!session.value) return '未创建会话'
  const statusMap: Record<string, string> = {
    pending: '准备中',
    active: '上课中',
    paused: '已暂停',
    ended: '已结束',
  }
  return statusMap[session.value.status] || '未知状态'
})

const statusClass = computed(() => {
  if (!session.value) return 'status-pending'
  return `status-${session.value.status}`
})

const totalStudents = computed(() => {
  return session.value?.total_students || 0
})

const currentCell = computed(() => {
  if (!props.lesson?.content || !session.value) {
    console.log('🔍 currentCell: 缺少必要数据', {
      hasLesson: !!props.lesson,
      hasContent: !!props.lesson?.content,
      hasSession: !!session.value,
    })
    return null
  }
  
  // 如果 selectedCellIndex 有效，优先使用它
  if (selectedCellIndex.value >= 0 && selectedCellIndex.value < props.lesson.content.length) {
    const cell = props.lesson.content[selectedCellIndex.value]
    console.log('✅ currentCell: 使用 selectedCellIndex', {
      selectedCellIndex: selectedCellIndex.value,
      cellType: cell?.type,
      cellTitle: cell?.title,
      cellOrder: cell?.order,
    })
    return cell
  }
  
  // 否则使用 current_cell_id 查找
  const currentId = session.value.current_cell_id
  if (!currentId || currentId === 0) {
    console.log('🔍 currentCell: current_cell_id 无效', {
      currentId,
      selectedCellIndex: selectedCellIndex.value,
    })
    return null
  }
  
  // 查找匹配的Cell
  const foundCell = props.lesson.content.find((cell, index) => {
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
  
  console.log('🔍 currentCell: 通过 current_cell_id 查找', {
    currentId,
    foundCell: foundCell ? { type: foundCell.type, title: foundCell.title } : null,
  })
  
  return foundCell || null
})

// 获取当前活动 Cell 的数据库 ID（用于查询提交数据）
const currentActivityDbCell = computed(() => {
  if (!currentCell.value || currentCell.value.type !== 'activity') {
    console.log('🔍 currentActivityDbCell: 不是活动模块', {
      hasCurrentCell: !!currentCell.value,
      cellType: currentCell.value?.type,
    })
    return null
  }
  
  if (!dbCells.value || dbCells.value.length === 0) {
    console.log('🔍 currentActivityDbCell: dbCells 为空', {
      dbCellsLength: dbCells.value?.length || 0,
    })
    return null
  }
  
  // 通过 order 查找对应的数据库 Cell
  const order = currentCell.value.order
  if (order === undefined) {
    console.log('🔍 currentActivityDbCell: currentCell.order 未定义', {
      currentCell: currentCell.value,
    })
    return null
  }
  
  // 尝试匹配 cell_type（可能是 'ACTIVITY' 或 'activity'）
  const matchedDbCell = dbCells.value.find(dbCell => {
    const cellTypeMatch = dbCell.cell_type === 'ACTIVITY' || 
                          dbCell.cell_type === 'activity' ||
                          dbCell.cell_type?.toUpperCase() === 'ACTIVITY'
    return dbCell.order === order && cellTypeMatch
  })
  
  console.log('🔍 currentActivityDbCell 查找结果:', {
    currentCellOrder: order,
    dbCells: dbCells.value.map(c => ({ id: c.id, order: c.order, type: c.cell_type })),
    matchedDbCell: matchedDbCell ? { id: matchedDbCell.id, order: matchedDbCell.order } : null,
  })
  
  return matchedDbCell || null
})


// 方法
// 使用工具函数获取 Cell ID（保留此函数名以兼容现有代码）
function getCellId(cell: Cell): number | string | null {
  return getCellIdUtil(cell)
}

function getCellTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    text: '文本',
    code: '代码',
    activity: '活动',
    video: '视频',
    flowchart: '流程图',
  }
  return labels[type] || type
}

function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

function formatRemainingTime(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 会话操作
// 创建课堂会话（保持 PENDING 状态，等待学生加入）
async function handleCreateSession() {
  loading.value = true
  try {
    // 首先需要创建会话，这里需要classroom_id
    // 暂时从路由或props中获取，或者提示用户选择班级
    const classroomId = route.params.classroomId as string || '1'
    
    try {
      console.log('🚀 Creating session...')
      // 创建会话（状态为 PENDING）
      const newSession = await classroomSessionService.createSession(props.lessonId, {
        classroom_id: parseInt(classroomId),
      })
      
      console.log('✅ Session created, received:', newSession)
      
      // 检查响应
      if (!newSession || !newSession.id) {
        console.error('❌ Invalid session response:', newSession)
        throw new Error('创建会话失败：服务器返回的数据格式不正确')
      }
      
      // 保持 PENDING 状态，不立即开始
      session.value = newSession
      console.log('✅ Session created in PENDING state, waiting for students...')
      
      // 加载学生列表（开始轮询）
      loadParticipants()
      
      // 设置定时刷新学生列表（每3秒）
      const refreshInterval = setInterval(() => {
        if (session.value && session.value.status === 'pending') {
          loadParticipants()
        } else {
          clearInterval(refreshInterval)
        }
      }, 3000)
      
      // 组件卸载时清除定时器
      onUnmounted(() => {
        clearInterval(refreshInterval)
      })
    } catch (createError: any) {
      // 如果创建失败，检查是否是因为已有活跃会话
      const errorDetail = createError.response?.data?.detail || createError.message || ''
      
      if (errorDetail.includes('已有活跃的课堂会话') || createError.response?.status === 400) {
        // 尝试查找并加载现有会话
        console.log('检测到已有活跃会话，尝试加载...')
        
        // 首先尝试从错误信息中提取会话ID
        const sessionIdMatch = errorDetail.match(/ID:\s*(\d+)/)
        let activeSessions: any[] = []
        
        if (sessionIdMatch) {
          // 如果错误信息中包含会话ID，直接使用它
          const sessionId = parseInt(sessionIdMatch[1])
          console.log(`从错误信息中提取到会话ID: ${sessionId}`)
          try {
            const existingSession = await classroomSessionService.getSession(sessionId)
            if (existingSession) {
              activeSessions = [existingSession]
              console.log(`成功通过ID获取会话:`, existingSession)
            }
          } catch (getError: any) {
            console.error('通过ID获取会话失败:', getError)
            // 如果通过ID获取失败，尝试查询列表
          }
        }
        
        // 如果通过ID获取失败或没有提取到ID，尝试查询列表
        if (activeSessions.length === 0) {
          try {
            const allSessions = await classroomSessionService.listSessions(props.lessonId)
            console.log(`📋 查询到 ${allSessions.length} 个会话`)
            // 过滤活跃会话，并且如果知道classroomId，也按classroomId过滤
            activeSessions = allSessions.filter(s => {
              const isActive = s.status === 'active' || s.status === 'paused' || s.status === 'pending'
              if (!isActive) return false
              // 尝试匹配 classroomId（如果有的话）
              const sessionClassroomId = s.classroomId || (s as any).classroom_id
              const targetClassroomId = parseInt(classroomId)
              if (sessionClassroomId && targetClassroomId) {
                return sessionClassroomId === targetClassroomId
              }
              // 如果没有 classroomId，匹配所有活跃会话
              return true
            })
            console.log(`✅ 通过列表查询找到 ${activeSessions.length} 个活跃会话（classroom_id=${classroomId}）`)
          } catch (e: any) {
            console.error('查询会话列表失败:', e)
            const listErrorDetail = e.response?.data?.detail || e.message || ''
            console.error('查询失败详情:', listErrorDetail)
            // 如果列表查询也失败，尝试再次从错误信息中提取ID
            if (!sessionIdMatch) {
              const fallbackIdMatch = listErrorDetail.match(/ID:\s*(\d+)/) || errorDetail.match(/ID:\s*(\d+)/)
              if (fallbackIdMatch) {
                const fallbackSessionId = parseInt(fallbackIdMatch[1])
                try {
                  const existingSession = await classroomSessionService.getSession(fallbackSessionId)
                  if (existingSession) {
                    activeSessions = [existingSession]
                    console.log(`通过备用方法获取会话成功`)
                  }
                } catch (fallbackError: any) {
                  console.error('备用方法也失败:', fallbackError)
                  // 检查是否是权限问题
                  if (fallbackError.response?.status === 403) {
                    console.warn('⚠️ 无权限访问该会话，可能是会话不属于当前用户')
                  } else if (fallbackError.response?.status === 404) {
                    console.warn('⚠️ 会话不存在，可能已被删除')
                  }
                }
              }
            }
          }
        }
        
        if (activeSessions.length > 0) {
          // 找到现有会话，直接使用
          const existingSession = activeSessions[0]
          session.value = existingSession
          
          // 如果会话是pending状态，不自动开始，保持等待状态
          // 让教师手动点击"开始上课"按钮
          
          // 开始计时和加载数据
          if (session.value.status === 'active') {
            startDurationTimer()
          }
          loadParticipants()
          loadStatistics()
          
          // 如果会话是 pending 状态，设置定时刷新学生列表
          if (session.value.status === 'pending') {
            const refreshInterval = setInterval(() => {
              if (session.value && session.value.status === 'pending') {
                loadParticipants()
              } else {
                clearInterval(refreshInterval)
              }
            }, 3000)
            
            onUnmounted(() => {
              clearInterval(refreshInterval)
            })
          }
          
          // 提示用户已加载现有会话
          const statusText = {
            'active': '进行中',
            'paused': '已暂停',
            'pending': '等待学生加入'
          }[existingSession.status] || '未知'
          console.log(`✅ 已自动加载现有会话 (ID: ${existingSession.id}, 状态: ${statusText})`)
          
          // 如果会话是暂停状态，提示用户
          if (existingSession.status === 'paused') {
            // 不显示alert，让用户看到界面状态即可
            console.log('💡 会话当前处于暂停状态，可以点击"继续"按钮恢复')
          }
          
          return // 成功加载，退出函数
        } else {
          // 没有找到活跃会话
          console.warn('⚠️ 虽然检测到已有活跃会话，但无法加载会话详情')
          console.warn('原始错误:', createError.response?.data || createError.message)
          
          // 尝试最后一次：直接从错误信息中提取ID
          const finalIdMatch = errorDetail.match(/ID:\s*(\d+)/)
          if (finalIdMatch) {
            const finalSessionId = parseInt(finalIdMatch[1])
            console.log(`🔄 最后尝试：直接使用会话ID ${finalSessionId}`)
            try {
              const finalSession = await classroomSessionService.getSession(finalSessionId)
              if (finalSession) {
                session.value = finalSession
                
                // 如果会话是pending状态，不自动开始，保持等待状态
                
                // 开始计时和加载数据
                if (session.value.status === 'active') {
                  startDurationTimer()
                }
                loadParticipants()
                loadStatistics()
                
                // 如果会话是 pending 状态，设置定时刷新学生列表
                if (session.value.status === 'pending') {
                  const refreshInterval = setInterval(() => {
                    if (session.value && session.value.status === 'pending') {
                      loadParticipants()
                    } else {
                      clearInterval(refreshInterval)
                    }
                  }, 3000)
                  
                  onUnmounted(() => {
                    clearInterval(refreshInterval)
                  })
                }
                
                console.log(`✅ 成功！已加载会话 ID: ${finalSessionId}`)
                return
              }
            } catch (finalError: any) {
              console.error('❌ 最后尝试也失败:', finalError)
              console.error('❌ 错误详情:', {
                message: finalError.message,
                response: finalError.response,
                status: finalError.response?.status,
                data: finalError.response?.data,
              })
              // 检查具体错误类型
              if (finalError.response?.status === 403) {
                console.error('⚠️ 无权限访问该会话，可能是会话不属于当前用户')
                throw new Error('无权限访问该会话。会话可能属于其他教师，请确保您是该会话的创建者。')
              } else if (finalError.response?.status === 404) {
                console.error('⚠️ 会话不存在，可能已被删除')
                throw new Error('会话不存在，可能已被删除。请刷新页面重试。')
              } else if (finalError.response?.status === 400) {
                // 400 错误可能包含详细信息
                const errorDetail = finalError.response?.data?.detail || finalError.message || '无法加载会话'
                console.error('⚠️ 请求错误 (400):', errorDetail)
                throw new Error(`无法加载现有会话：${errorDetail}`)
              } else {
                // 其他错误，抛出更友好的错误信息
                const finalErrorMessage = finalError.response?.data?.detail || finalError.message || '无法加载会话'
                console.error('⚠️ 未知错误:', finalErrorMessage)
                throw new Error(`无法加载现有会话：${finalErrorMessage}`)
              }
            }
          }
          
          // 如果所有方法都失败，抛出更友好的错误信息
          const friendlyError = new Error(
            '无法加载现有活跃会话。请尝试刷新页面，或联系管理员检查会话状态。'
          )
          throw friendlyError
        }
      } else {
        // 其他错误，直接抛出
        throw createError
      }
    }
  } catch (error: any) {
    console.error('Failed to create session:', error)
    // 提取更友好的错误信息
    let errorMessage = error.message || error.response?.data?.detail || '创建课堂失败'
    
    // 如果是已知的错误类型，显示更友好的提示
    if (errorMessage.includes('无权限')) {
      errorMessage = '无法访问该会话。请确保您是该会话的创建者。'
    } else if (errorMessage.includes('不存在')) {
      errorMessage = '会话不存在，请刷新页面重试。'
    } else if (errorMessage.includes('已有活跃的课堂会话')) {
      // 这种情况应该已经被处理了，但如果仍然出现，说明加载失败
      errorMessage = '检测到已有活跃会话，但无法自动加载。请刷新页面重试。'
    }
    
    alert(errorMessage)
  } finally {
    loading.value = false
  }
}

// 开始上课（将 PENDING 状态变为 ACTIVE）
async function handleBeginClass() {
  if (!session.value || session.value.status !== 'pending') return
  
  loading.value = true
  try {
    console.log('🎬 Starting session with id:', session.value.id)
    session.value = await classroomSessionService.startSession(session.value.id)
    console.log('✅ Session started successfully:', session.value)
    
    // 检查开始会话的响应
    if (!session.value) {
      throw new Error('开始会话失败：服务器返回的数据格式不正确')
    }
    
    // 开始计时（新会话从0开始）
    if (session.value.status === 'active') {
      sessionDuration.value = 0  // 新会话从0开始
      startDurationTimer()
    }
    
    // 加载统计信息
    loadStatistics()
    
    // 设置定时刷新学生列表和统计（每5秒）
    const refreshInterval = setInterval(() => {
      if (session.value && (session.value.status === 'active' || session.value.status === 'paused')) {
        loadParticipants()
        loadStatistics()
      } else {
        clearInterval(refreshInterval)
      }
    }, 5000)
    
    // 组件卸载时清除定时器
    onUnmounted(() => {
      clearInterval(refreshInterval)
    })
  } catch (error: any) {
    console.error('Failed to start session:', error)
    const errorMessage = error.message || error.response?.data?.detail || '开始上课失败'
    alert(errorMessage)
  } finally {
    loading.value = false
  }
}

// 取消课堂（删除 PENDING 状态的会话）
async function handleCancelSession() {
  if (!session.value || session.value.status !== 'pending') return
  if (!confirm('确定要取消课堂吗？这将删除当前会话。')) return
  
  loading.value = true
  try {
    // 注意：这里可能需要一个删除会话的API，如果没有，可以结束会话
    // 暂时先提示用户
    alert('取消课堂功能需要后端支持删除会话API')
    // TODO: 实现删除会话的逻辑
    // await classroomSessionService.deleteSession(session.value.id)
    // session.value = null
  } catch (error: any) {
    console.error('Failed to cancel session:', error)
    alert('取消课堂失败')
  } finally {
    loading.value = false
  }
}

async function handlePause() {
  if (!session.value) return
  loading.value = true
  try {
    session.value = await classroomSessionService.pauseSession(session.value.id)
    stopDurationTimer()
  } catch (error: any) {
    console.error('Failed to pause session:', error)
    alert('暂停失败')
  } finally {
    loading.value = false
  }
}

async function handleResume() {
  if (!session.value) return
  loading.value = true
  try {
    session.value = await classroomSessionService.resumeSession(session.value.id)
    startDurationTimer()
  } catch (error: any) {
    console.error('Failed to resume session:', error)
    alert('继续失败')
  } finally {
    loading.value = false
  }
}

async function handleEnd() {
  if (!session.value) return
  if (!confirm('确定要结束课程吗？')) return
  
  loading.value = true
  try {
    session.value = await classroomSessionService.endSession(session.value.id)
    stopDurationTimer()
  } catch (error: any) {
    console.error('Failed to end session:', error)
    alert('结束课程失败')
  } finally {
    loading.value = false
  }
}

// 隐藏所有内容（通过导播台的"隐藏"节点调用）
async function handleHideAll() {
  if (!session.value) return
  
  loading.value = true
  try {
    // 使用cell_id=0来隐藏所有内容（后端已支持）
    session.value = await classroomSessionService.navigateToCell(session.value.id, {
      cellId: 0,
    })
    selectedCellIndex.value = -1
  } catch (error: any) {
    console.error('Failed to hide content:', error)
    const errorMessage = error.response?.data?.detail || error.message || '隐藏内容失败'
    alert(errorMessage)
  } finally {
    loading.value = false
  }
}


// 活动控制
async function handleStartActivity() {
  if (!session.value || !currentCell.value) return
  
  // 使用session中的current_cell_id，这是当前显示的Cell
  const currentCellId = session.value.current_cell_id
  if (!currentCellId) {
    alert('无法开始活动：当前没有显示任何Cell')
    return
  }
  
  loading.value = true
  try {
    session.value = await classroomSessionService.startActivity(session.value.id, {
      cellId: currentCellId,
    })
  } catch (error: any) {
    console.error('Failed to start activity:', error)
    const errorMessage = error.response?.data?.detail || error.message || '开始活动失败'
    alert(errorMessage)
  } finally {
    loading.value = false
  }
}

async function handleEndActivity() {
  if (!session.value) return
  
  loading.value = true
  try {
    session.value = await classroomSessionService.endActivity(session.value.id)
  } catch (error: any) {
    console.error('Failed to end activity:', error)
    alert('结束活动失败')
  } finally {
    loading.value = false
  }
}

// 导播台导航处理
async function handleControlBoardNavigate(
  cellId: number | string | null, 
  cellOrder: number | null,
  action: 'toggle' | 'add' | 'remove' = 'toggle',
  multiSelect: boolean = false
) {
  console.log('📬 收到导播台导航事件:', { cellId, cellOrder, action, multiSelect })
  
  if (!session.value) {
    console.warn('⚠️ 无法导航：会话不存在')
    return
  }
  
  console.log('🎯 导播台导航请求:', { 
    cellId, 
    cellOrder, 
    cellIdType: typeof cellId, 
    action, 
    multiSelect,
    sessionId: session.value.id,
  })
  
  loading.value = true
  try {
    // 🆕 新方式：使用 display_cell_orders（推荐）
    // 获取当前选中的 orders（从 settings 中获取，如果有的话）
    let displayOrders: number[] = []
    const currentSettings = session.value.settings as any
    if (currentSettings?.display_cell_orders) {
      displayOrders = [...currentSettings.display_cell_orders]
    } else if (currentSettings?.display_cell_ids && props.lesson?.content) {
      // 向后兼容：如果只有 display_cell_ids，转换成 orders
      displayOrders = currentSettings.display_cell_ids
        .map((id: number) => {
          const cell = props.lesson!.content.find((c: any) => getCellId(c) === id)
          return cell ? (cell.order !== undefined ? cell.order : props.lesson!.content.indexOf(cell)) : -1
        })
        .filter((order: number) => order >= 0)
    }
    
    // 如果是隐藏所有（cellId === 0 或 null）且不是多选模式
    if ((cellId === 0 || cellId === null) && cellOrder === null && !multiSelect) {
      displayOrders = []
    } else if (cellOrder !== null) {
      // 根据 action 更新 displayOrders
      if (action === 'add') {
        if (!displayOrders.includes(cellOrder)) {
          displayOrders.push(cellOrder)
        }
      } else if (action === 'remove') {
        displayOrders = displayOrders.filter(o => o !== cellOrder)
      } else if (action === 'toggle') {
        if (displayOrders.includes(cellOrder)) {
          displayOrders = displayOrders.filter(o => o !== cellOrder)
        } else {
          displayOrders = multiSelect ? [...displayOrders, cellOrder] : [cellOrder]
        }
      }
    }
    
    // 发送新方式的请求
    const requestData = {
      displayCellOrders: displayOrders,
      action,
    }
    console.log('📤 发送导航请求（新方式）:', requestData)
    const updatedSession = await classroomSessionService.navigateToCell(session.value.id, requestData)
    
    // 确保更新后的会话状态正确（不要丢失状态）
    if (updatedSession) {
      session.value = {
        ...session.value,
        ...updatedSession,
        status: session.value.status, // 保持原有状态，导航不应该改变会话状态
        id: session.value.id,
      }
      
      // 使用 display_cell_orders
      const updatedSettings = updatedSession.settings as any
      if (updatedSettings?.display_cell_orders) {
        const orders = updatedSettings.display_cell_orders
        console.log('✅ 使用 display_cell_orders:', orders)
      }
      console.log('✅ 更新显示 Cell 列表, settings:', updatedSession.settings)
    }
    
    // 导航后立即刷新学生列表
    loadParticipants()
    
    // 🆕 如果点击的是活动模块，确保数据库记录存在
    if (cellOrder !== null && props.lesson?.content) {
      const clickedCell = props.lesson.content.find((cell, idx) => {
        const cellOrderValue = cell.order !== undefined ? cell.order : idx
        return cellOrderValue === cellOrder
      })
      
      if (clickedCell && clickedCell.type === 'activity') {
        console.log('🎯 点击了活动模块，确保数据库记录存在...')
        const createdCellId = await ensureActivityCellExists(clickedCell, cellOrder)
        // 重新加载 dbCells 以获取最新数据
        await loadDbCells()
        
        // 🆕 如果创建成功，等待一小段时间让数据库记录生效
        if (createdCellId) {
          console.log('✅ 活动模块数据库记录已创建，等待生效...')
          await new Promise(resolve => setTimeout(resolve, 500))
          // 再次加载确保获取到最新数据
          await loadDbCells()
        }
      }
    }
    
    // 🆕 如果 dbCells 为空，重新加载（可能活动模块刚创建）
    if (dbCells.value.length === 0) {
      console.log('🔄 dbCells 为空，重新加载...')
      await loadDbCells()
    }
    
    // 更新selectedCellIndex
    if (cellId === 0) {
      selectedCellIndex.value = -1
    } else if (cellOrder !== null && cellOrder !== undefined && props.lesson?.content) {
      // 🆕 通过 cellOrder 查找对应的数组索引（而不是直接使用 cellOrder）
      const index = props.lesson.content.findIndex((cell, idx) => {
        const cellOrderValue = cell.order !== undefined ? cell.order : idx
        return cellOrderValue === cellOrder
      })
      if (index >= 0) {
        selectedCellIndex.value = index
        console.log('✅ 通过 cellOrder 找到索引:', index, 'cellOrder:', cellOrder)
      } else {
        // 如果找不到，尝试使用 cellOrder 作为索引（向后兼容）
        selectedCellIndex.value = cellOrder < props.lesson.content.length ? cellOrder : -1
        console.log('⚠️ 未找到匹配的 cell，使用 cellOrder 作为索引:', cellOrder)
      }
    } else if (cellId && props.lesson?.content) {
      // 通过 cellId 查找索引
      const index = props.lesson.content.findIndex((cell) => {
        const id = getCellId(cell)
        if (typeof id === 'number' && id === cellId) return true
        if (typeof id === 'string') {
          const numId = parseInt(id, 10)
          if (!isNaN(numId) && numId === cellId) return true
        }
        return false
      })
      if (index >= 0) {
        selectedCellIndex.value = index
        console.log('✅ 通过 cellId 找到索引:', index)
      } else {
        console.warn('⚠️ 未找到匹配的 cell，使用 cellOrder 作为 fallback')
        // 如果找不到，尝试使用返回的 currentCellId 对应的索引
        if (updatedSession?.currentCellId) {
          const currentId = updatedSession.currentCellId
          const foundIndex = props.lesson.content.findIndex((cell) => {
            const id = getCellId(cell)
            return id === currentId || (typeof id === 'string' && String(id) === String(currentId))
          })
          if (foundIndex >= 0) {
            selectedCellIndex.value = foundIndex
          }
        }
      }
    }
  } catch (error: any) {
    console.error('Failed to navigate from control board:', error)
    const errorMessage = error.response?.data?.detail || error.message || '切换内容失败'
    alert(errorMessage)
  } finally {
    loading.value = false
  }
}

// 加载数据
async function loadParticipants() {
  if (!session.value) {
    console.warn('⚠️ 无法加载学生列表：会话不存在')
    return
  }
  
  console.log('🔄 开始加载在线学生列表，会话ID:', session.value.id)
  loadingStudents.value = true
  try {
    // 获取所有在线学生（is_active=true）
    const participants = await classroomSessionService.getParticipants(session.value.id, true)
    
    // 确保是数组且只包含在线学生
    const activeParticipants = Array.isArray(participants) 
      ? participants.filter(p => p.isActive !== false)
      : []
    
    activeStudents.value = activeParticipants
    console.log(`👥 加载在线学生完成: ${activeStudents.value.length} 人`, activeStudents.value.map(s => ({
      id: s.id,
      name: s.studentName || s.student_name,
      isActive: s.isActive || s.is_active,
    })))
    
    // 更新会话统计中的在线学生数
    if (session.value) {
      session.value.activeStudents = activeStudents.value.length
      console.log('📊 更新会话统计，在线学生数:', session.value.activeStudents)
    }
  } catch (error: any) {
    console.error('❌ 加载学生列表失败:', error)
    console.error('❌ 错误详情:', {
      message: error.message,
      response: error.response,
      status: error.response?.status,
      data: error.response?.data,
    })
    activeStudents.value = []
  } finally {
    loadingStudents.value = false
  }
}

async function loadStatistics() {
  if (!session.value) return
  
  try {
    sessionStatistics.value = await classroomSessionService.getStatistics(session.value.id)
  } catch (error) {
    console.error('Failed to load statistics:', error)
  }
}

// 定时器
function startDurationTimer() {
  if (durationInterval.value) return
  
  // 如果还没有开始计时（值为0或未定义），从0开始
  // 如果已经有值（比如暂停后继续），保持当前值继续计时
  if (sessionDuration.value === 0 || sessionDuration.value === null || sessionDuration.value === undefined) {
    sessionDuration.value = 0
  }
  
  // 每秒递增，直到达到课程时长
  durationInterval.value = setInterval(() => {
    sessionDuration.value = Math.min(sessionDuration.value + 1, LESSON_DURATION)
  }, 1000)
}

function stopDurationTimer() {
  if (durationInterval.value) {
    clearInterval(durationInterval.value)
    durationInterval.value = null
  }
}

// 监听session变化，更新selectedCellIndex和displayCellIds
watch(() => session.value, (newSession) => {
  if (!props.lesson?.content || !newSession) return
  
  // 使用 display_cell_orders
  const settings = newSession.settings as any
  if (settings?.display_cell_orders && Array.isArray(settings.display_cell_orders)) {
    const orders = settings.display_cell_orders
    console.log('✅ watch: 使用 display_cell_orders:', orders)
    
    // 如果有选中的 orders，使用第一个的索引
    if (orders.length > 0) {
      selectedCellIndex.value = orders[0]
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
  const index = props.lesson.content.findIndex(cell => {
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

// 加载数据库中的 Cell 记录
async function loadDbCells() {
  try {
    const { api } = await import('../../services/api')
    const response = await api.get(`/cells/lesson/${props.lessonId}`)
    dbCells.value = Array.isArray(response) ? response : ([] as any)
    console.log('📦 加载数据库 Cell 记录:', dbCells.value.length, '个', dbCells.value)
  } catch (error: any) {
    console.warn('⚠️ 加载数据库 Cell 记录失败:', error)
    dbCells.value = []
  }
}

// 🆕 确保活动模块的数据库记录存在
async function ensureActivityCellExists(cell: Cell, order: number): Promise<number | null> {
  // 如果 dbCells 中已经有匹配的记录，直接返回
  const existing = dbCells.value.find(dbCell => 
    dbCell.order === order && 
    (dbCell.cell_type === 'ACTIVITY' || dbCell.cell_type === 'activity' || dbCell.cell_type?.toUpperCase() === 'ACTIVITY')
  )
  if (existing) {
    console.log('✅ 活动模块数据库记录已存在:', existing.id)
    return existing.id
  }
  
  // 尝试创建数据库记录
  try {
    console.log('📤 创建活动模块数据库记录...', {
      lessonId: props.lessonId,
      order,
      title: cell.title,
      type: cell.type,
    })
    
    const { api } = await import('../../services/api')
    const cellCreateData = {
      lesson_id: props.lessonId,
      cell_type: 'ACTIVITY',  // 后端使用大写枚举值
      title: cell.title || '',
      content: cell.content || {},
      config: cell.config || {},
      order: order,
      editable: cell.editable ?? false,
    }
    
    console.log('📤 发送创建 Cell 请求:', cellCreateData)
    const createResponse = await api.post('/cells', cellCreateData)
    const newCell = createResponse
    console.log('📥 创建 Cell 响应:', newCell)
    
    if (newCell && newCell.id) {
      const cellId = typeof newCell.id === 'number' ? newCell.id : parseInt(newCell.id, 10)
      if (!isNaN(cellId)) {
        console.log('✅ 成功创建活动模块数据库记录:', cellId)
        
        // 添加到 dbCells 数组
        dbCells.value.push({
          id: cellId,
          order: order,
          cell_type: 'ACTIVITY',
        })
        
        return cellId
      }
    }
  } catch (error: any) {
    console.error('❌ 创建活动模块数据库记录失败:', error)
    console.error('错误详情:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
    })
  }
  
  return null
}

// 初始化
onMounted(async () => {
  // 加载数据库 Cell 记录（用于 ID 匹配）
  await loadDbCells()
  
  // 检查是否有现有的活跃会话
  try {
    // 查询所有会话，然后过滤出活跃的
    const allSessions = await classroomSessionService.listSessions(props.lessonId)
    const activeSessions = allSessions.filter(s => 
      s.status === 'active' || s.status === 'paused' || s.status === 'pending'
    )
    
    console.log('🔍 检查现有会话:', { total: allSessions.length, active: activeSessions.length })
    
    // 添加空值检查
    if (activeSessions && Array.isArray(activeSessions) && activeSessions.length > 0) {
      session.value = activeSessions[0]
      console.log('✅ 加载现有会话:', session.value)
      
      if (session.value.status === 'active') {
        startDurationTimer()
      }
      
      // 加载学生列表和统计
      loadParticipants()
      loadStatistics()
      
      // 设置定时刷新学生列表（每5秒）
      const refreshInterval = setInterval(() => {
        if (session.value && (session.value.status === 'active' || session.value.status === 'paused')) {
          loadParticipants()
          loadStatistics()
        } else {
          clearInterval(refreshInterval)
        }
      }, 5000)
      
      // 如果会话是 pending 状态，也设置定时刷新
      if (session.value.status === 'pending') {
        const pendingRefreshInterval = setInterval(() => {
          if (session.value && session.value.status === 'pending') {
            loadParticipants()
          } else {
            clearInterval(pendingRefreshInterval)
          }
        }, 3000)
        
        onUnmounted(() => {
          clearInterval(pendingRefreshInterval)
        })
      }
      
      // 组件卸载时清除定时器
      onUnmounted(() => {
        clearInterval(refreshInterval)
      })
    } else {
      console.log('ℹ️ 没有找到现有会话')
    }
  } catch (error: any) {
    console.error('❌ 加载现有会话失败:', error)
    // 如果是404或其他错误，不显示错误提示（可能是正常的，没有现有会话）
    if (error.response?.status !== 404) {
      console.warn('加载现有会话时出错，但可以继续创建新会话')
    }
  }
})

onUnmounted(() => {
  stopDurationTimer()
})
</script>

<style scoped>
/* 活动统计面板样式 */
.activity-panel {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.teacher-control-panel {
  @apply bg-white rounded-lg border border-gray-200 p-6 space-y-6;
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

</style>

