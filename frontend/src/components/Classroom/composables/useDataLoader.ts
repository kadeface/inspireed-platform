/**
 * 数据加载 Composable
 *
 * 管理课堂会话的数据加载逻辑
 */

import { ref, type Ref, watch } from 'vue'
import type { Cell, ActivityCell } from '@/types/cell'
import classroomSessionService from '@/services/classroomSession'
import activityService from '@/services/activity'
import { toNumericId } from '@/utils/cellId'

export interface UseDataLoaderOptions {
  /**
   * 会话对象
   */
  session: Ref<any | null>

  /**
   * 课程 ID
   */
  lessonId: number

  /**
   * 当前选中的 Cell
   */
  currentCell: Ref<Cell | null>

  /**
   * 当前活动模块的数据库记录
   */
  currentActivityDbCell: Ref<{ id: number | string; order: number; cell_type: string } | null>

  /**
   * 组件容器引用（用于检查组件是否在 DOM 中）
   */
  containerRef: Ref<HTMLElement | null>

  /**
   * 轮询管理器（用于清理定时器）
   */
  pollingManager: {
    clearAllPollingIntervals: () => void
  }

  /**
   * 数据库 Cell 记录列表
   */
  dbCells: Ref<Array<{ id: number | string; order: number; cell_type: string }>>
}

export function useDataLoader(options: UseDataLoaderOptions) {
  const {
    session,
    lessonId,
    currentCell,
    currentActivityDbCell,
    containerRef,
    pollingManager,
    dbCells,
  } = options

  // 加载状态
  const loadingStudents = ref(false)
  const loadingActivityStats = ref(false)

  // 数据
  const activeStudents = ref<any[]>([])
  const sessionStatistics = ref<any>(null)
  const activityStatistics = ref({
    totalStudents: 0,
    submittedCount: 0,
    itemStatistics: null as Record<string, any> | null,
  })
  const studentSubmissionStatus = ref<Map<number | string, string>>(new Map())

  /**
   * 加载参与者/学生列表
   */
  async function loadParticipants() {
    // 首先检查组件是否还在 DOM 中（如果被 v-if 隐藏，不应该执行）
    if (!containerRef.value || !containerRef.value.isConnected) {
      console.log('⏸️ loadParticipants: 组件不在 DOM 中，跳过加载并清理轮询')
      pollingManager.clearAllPollingIntervals()
      return
    }

    if (!session.value) {
      console.warn('⏸️ loadParticipants: 会话不存在，跳过加载')
      return
    }

    loadingStudents.value = true
    try {
      console.log('🔄 开始加载学生列表，sessionId:', session.value.id)
      // 获取所有在线学生（is_active=true）
      const participants = await classroomSessionService.getParticipants(session.value.id, true)
      console.log('📥 获取到参与者数据:', participants)

      // 确保是数组且只包含在线学生
      const activeParticipants = Array.isArray(participants)
        ? participants.filter(p => p.isActive !== false)
        : []

      console.log('✅ 过滤后的在线学生:', activeParticipants.length, '人', activeParticipants.map(s => ({
        id: s.id,
        name: s.studentName || s.student_name,
        isActive: s.isActive ?? s.is_active,
      })))

      activeStudents.value = activeParticipants

      // 更新会话统计中的在线学生数
      if (session.value) {
        session.value.activeStudents = activeStudents.value.length
        console.log('📊 更新会话统计，在线学生数:', session.value.activeStudents)
      }
    } catch (error: any) {
      console.error('❌ 加载学生列表失败:', error)
      console.error('错误详情:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
      })
      activeStudents.value = []
    } finally {
      loadingStudents.value = false
    }
  }

  /**
   * 加载会话统计信息
   */
  async function loadStatistics() {
    if (!session.value) return

    try {
      sessionStatistics.value = await classroomSessionService.getStatistics(session.value.id)
    } catch (error) {
      console.error('Failed to load statistics:', error)
    }
  }

  /**
   * 加载活动统计信息
   */
  async function loadActivityStatistics() {
    if (!currentCell.value || currentCell.value.type !== 'activity' || !currentActivityDbCell.value || !session.value) {
      activityStatistics.value = {
        totalStudents: 0,
        submittedCount: 0,
        itemStatistics: null,
      }
      studentSubmissionStatus.value.clear()
      return
    }

    loadingActivityStats.value = true
    try {
      const numericCellId = typeof currentActivityDbCell.value.id === 'number'
        ? currentActivityDbCell.value.id
        : toNumericId(currentActivityDbCell.value.id)

      if (numericCellId === null) {
        console.warn('⚠️ CellId 是 UUID，无法获取统计数据（需要数字 ID）')
        return
      }

      // 并行加载统计数据和提交列表
      const [stats, submissions] = await Promise.all([
        activityService.getStatistics(
          numericCellId,
          session.value.id,
          lessonId
        ),
        activityService.getCellSubmissions(
          numericCellId,
          undefined, // 不过滤状态
          session.value.id,
          lessonId
        ).catch(() => []) // 如果失败，返回空数组
      ])

      // 转换 API 返回的格式
      const statsAny = stats as any
      activityStatistics.value = {
        totalStudents: stats.totalStudents || statsAny.total_students || 0,
        submittedCount: stats.submittedCount || statsAny.submitted_count || 0,
        itemStatistics: stats.itemStatistics ?? statsAny.item_statistics ?? null,
      }

      // 建立学生ID到提交状态的映射
      // 支持多种ID字段：studentId, student_id, userId, user_id
      studentSubmissionStatus.value.clear()
      submissions.forEach((submission: any) => {
        const studentId = submission.studentId || submission.student_id || submission.userId || submission.user_id
        if (studentId !== null && studentId !== undefined) {
          const status = submission.status || 'not_started'
          // 使用字符串作为key，确保类型一致
          studentSubmissionStatus.value.set(String(studentId), status)
        }
      })
    } catch (error: any) {
      console.error('❌ 加载活动统计失败:', error)
    } finally {
      loadingActivityStats.value = false
    }
  }

  /**
   * 加载数据库中的 Cell 记录
   */
  async function loadDbCells() {
    try {
      const { api } = await import('@/services/api')
      const response = await api.get(`/cells/lesson/${lessonId}`)
      dbCells.value = Array.isArray(response) ? response : ([] as any)
    } catch (error: any) {
      console.warn('加载数据库 Cell 记录失败:', error)
      dbCells.value = []
    }
  }

  /**
   * 确保活动模块的数据库记录存在
   * @param cell - Cell 对象
   * @param order - 模块顺序
   * @returns 创建的 Cell ID，如果已存在或创建失败则返回 null
   */
  async function ensureActivityCellExists(cell: Cell, order: number): Promise<number | null> {
    // 如果 dbCells 中已经有匹配的记录，直接返回
    const existing = dbCells.value.find(dbCell =>
      dbCell.order === order &&
      (dbCell.cell_type === 'ACTIVITY' || dbCell.cell_type === 'activity' || dbCell.cell_type?.toUpperCase() === 'ACTIVITY')
    )
    if (existing) {
      return existing.id as number
    }

    // 尝试创建数据库记录
    try {
      const { api } = await import('@/services/api')
      // ActivityCell 有可选的 config 属性
      const activityCell = cell as ActivityCell
      const cellCreateData = {
        lesson_id: lessonId,
        cell_type: 'ACTIVITY',  // 后端使用大写枚举值
        title: cell.title || '',
        content: cell.content || {},
        config: activityCell.config || {},
        order: order,
        editable: cell.editable ?? false,
      }

      const createResponse = await api.post<{ id: number | string }>('/cells', cellCreateData)
      const newCell = createResponse

      if (newCell && newCell.id) {
        const cellId = typeof newCell.id === 'number' ? newCell.id : parseInt(newCell.id, 10)
        if (!isNaN(cellId)) {
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
      console.error('创建活动模块数据库记录失败:', error)
    }

    return null
  }

  /**
   * 监听 currentCell 变化，自动加载活动统计
   */
  function watchCurrentCell() {
    watch([currentCell, currentActivityDbCell, session], () => {
      if (currentCell.value && currentCell.value.type === 'activity' && currentActivityDbCell.value && session.value) {
        loadActivityStatistics()
      } else {
        // 如果不是活动模块，清空统计数据
        activityStatistics.value = {
          totalStudents: 0,
          submittedCount: 0,
          itemStatistics: null,
        }
        studentSubmissionStatus.value.clear()
      }
    }, { immediate: true })
  }

  return {
    // 状态
    loadingStudents,
    loadingActivityStats,
    activeStudents,
    sessionStatistics,
    activityStatistics,
    studentSubmissionStatus,

    // 方法
    loadParticipants,
    loadStatistics,
    loadActivityStatistics,
    loadDbCells,
    ensureActivityCellExists,
    watchCurrentCell,
  }
}
