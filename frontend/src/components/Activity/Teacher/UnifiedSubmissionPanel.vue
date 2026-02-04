  <template>
    <div class="unified-submission-panel">
      <!-- 提示：没有 sessionId 时显示 -->
      <div v-if="!sessionId" class="session-warning">
        <div class="warning-content">
          <span class="warning-icon">ℹ️</span>
          <div class="warning-text">
            <strong>等待进入课堂模式</strong>
            <p>请先启动课堂会话，才能查看该活动的学生提交数据。当前不在课堂模式下，不会显示任何数据。</p>
          </div>
        </div>
      </div>
      
      <!-- 顶部：统计信息卡片 -->
      <div v-else class="statistics-section">
        <div class="section-header">
          <h3 class="section-title">
            <span class="title-icon">📊</span>
            实时统计
          </h3>
          <div class="header-actions">
            <div v-if="isConnected" class="connection-status connected">
              <span class="status-dot"></span>
              <span class="status-text">实时更新中</span>
            </div>
            <div v-else-if="isConnecting" class="connection-status connecting">
              <span class="status-dot"></span>
              <span class="status-text">连接中...</span>
            </div>
            <div v-else class="connection-status disconnected">
              <span class="status-dot"></span>
              <span class="status-text">未连接</span>
            </div>
            <button 
              @click="refreshAll" 
              class="refresh-btn"
              :disabled="refreshing"
              title="刷新数据"
            >
              <svg class="w-4 h-4" :class="{ 'animate-spin': refreshing }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span class="ml-1">{{ refreshing ? '刷新中...' : '刷新' }}</span>
            </button>
          </div>
        </div>
  
        <!-- 基础统计卡片 -->
        <div class="stats-grid-compact">
          <!-- 总学生数 -->
          <div class="stat-card stat-card-primary">
            <div class="stat-icon-wrapper">
              <span class="stat-icon">👥</span>
            </div>
            <div class="stat-content">
              <div class="stat-label">总学生数</div>
              <div class="stat-value">{{ statistics.totalStudents }}</div>
            </div>
          </div>
  
          <!-- 已提交 -->
          <div class="stat-card stat-card-success">
            <div class="stat-icon-wrapper">
              <span class="stat-icon">✅</span>
            </div>
            <div class="stat-content">
              <div class="stat-label">已提交</div>
              <div class="stat-value text-green-600">{{ statistics.submittedCount }}</div>
              <div class="stat-percentage" v-if="statistics.totalStudents > 0">
                {{ Math.round((statistics.submittedCount / statistics.totalStudents) * 100) }}%
              </div>
            </div>
          </div>
  
          <!-- 草稿中 -->
          <div class="stat-card stat-card-warning">
            <div class="stat-icon-wrapper">
              <span class="stat-icon">📝</span>
            </div>
            <div class="stat-content">
              <div class="stat-label">草稿中</div>
              <div class="stat-value text-yellow-600">{{ statistics.draftCount }}</div>
              <div class="stat-percentage" v-if="statistics.totalStudents > 0">
                {{ Math.round((statistics.draftCount / statistics.totalStudents) * 100) }}%
              </div>
            </div>
          </div>
  
          <!-- 平均分 -->
          <div class="stat-card stat-card-info">
            <div class="stat-icon-wrapper">
              <span class="stat-icon">⭐</span>
            </div>
            <div class="stat-content">
              <div class="stat-label">平均分</div>
              <div class="stat-value text-blue-600">
                {{ statistics.averageScore !== null ? statistics.averageScore.toFixed(1) : '-' }}
              </div>
              <div class="stat-subtext" v-if="statistics.averageScore !== null && maxScore">
                / {{ maxScore }}
              </div>
            </div>
          </div>
        </div>

        <!-- 选择题选项分布 -->
        <div v-if="choiceItemsWithStats.length > 0" class="choice-statistics-section">
          <h4 class="choice-section-title">📊 选择题选项分布</h4>
          <div class="choice-items-grid">
            <div 
              v-for="itemStat in choiceItemsWithStats" 
              :key="itemStat.itemId"
              class="choice-item-card"
            >
              <div class="choice-item-header">
                <span class="choice-item-order">第 {{ itemStat.order + 1 }} 题</span>
                <span class="choice-item-type">{{ getItemTypeLabel(itemStat.type) }}</span>
              </div>
              <div class="choice-item-question">{{ itemStat.question }}</div>
              <div class="choice-options-list">
                <div 
                  v-for="option in itemStat.options" 
                  :key="option.id"
                  class="choice-option-item"
                  :class="{ 'is-correct': option.isCorrect }"
                >
                  <div class="option-header">
                    <span class="option-label">{{ option.label }}</span>
                    <span class="option-count">{{ option.count }}人</span>
                    <span class="option-percentage">{{ option.percentage }}%</span>
                  </div>
                  <div class="option-progress-bar">
                    <div 
                      class="option-progress-fill" 
                      :style="{ width: `${option.percentage}%` }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
  
        <!-- 提交进度条 -->
        <div class="progress-section">
          <div class="progress-header">
            <span class="progress-label">提交进度</span>
            <span class="progress-text">
              {{ statistics.submittedCount }} / {{ statistics.totalStudents }} 
              ({{ progressPercent }}%)
            </span>
          </div>
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: `${progressPercent}%` }"
            ></div>
          </div>
        </div>
      </div>
  
      <!-- 底部：学生提交列表 -->
      <div v-if="sessionId" class="submission-list-section">
        <div class="section-header">
          <h3 class="section-title">
            <span class="title-icon">📝</span>
            学生提交列表
          </h3>
          <div class="filter-bar">
            <select v-model="statusFilter" class="filter-select" @change="loadSubmissions">
              <option value="">全部状态</option>
              <option value="not_started">未开始</option>
              <option value="draft">草稿</option>
              <option value="submitted">已提交</option>
              <option value="graded">已评分</option>
              <option value="returned">已退回</option>
            </select>
          </div>
        </div>
  
        <!-- 批量操作 -->
        <div v-if="selectedSubmissions.length > 0" class="bulk-actions">
          <span class="text-sm text-gray-600">已选择 {{ selectedSubmissions.length }} 项</span>
          <div class="flex gap-2">
            <button @click="handleBulkGrade" class="btn-sm btn-primary">
              批量评分
            </button>
            <button @click="handleBulkReturn" class="btn-sm btn-secondary">
              批量退回
            </button>
            <button @click="selectedSubmissions = []" class="btn-sm btn-secondary">
              取消选择
            </button>
          </div>
        </div>
  
        <!-- 加载状态 -->
        <div v-if="loading && submissions.length === 0" class="loading-state">
          <div class="spinner"></div>
          <p>加载提交数据...</p>
        </div>
  
        <!-- 提交列表 -->
        <div v-else-if="submissions.length > 0" class="submissions-table">
          <table class="w-full">
            <thead>
              <tr>
                <th class="table-header">
                  <input
                    type="checkbox"
                    :checked="allSelected"
                    @change="toggleSelectAll"
                  />
                </th>
                <th class="table-header">学生</th>
                <th class="table-header">状态</th>
                <th class="table-header">分数</th>
                <th class="table-header">提交时间</th>
                <th class="table-header">用时</th>
                <th class="table-header">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="submission in submissions"
                :key="submission.id"
                class="table-row"
              >
                <td class="table-cell">
                  <input
                    type="checkbox"
                    :value="submission.id"
                    v-model="selectedSubmissions"
                  />
                </td>
                <td class="table-cell">
                  <div class="student-info">
                    <div class="font-medium">{{ submission.studentName }}</div>
                    <div class="text-xs text-gray-500">{{ submission.studentEmail }}</div>
                  </div>
                </td>
                <td class="table-cell">
                  <span :class="getStatusBadgeClass(submission.status)">
                    {{ getStatusLabel(submission.status) }}
                  </span>
                  <span v-if="submission.isLate" class="late-badge">迟交</span>
                </td>
                <td class="table-cell">
                  <div v-if="submission.score !== null" class="score-display">
                    <span class="font-semibold">{{ submission.score }}</span>
                    <span class="text-gray-500 text-sm">/ {{ submission.maxScore }}</span>
                  </div>
                  <span v-else class="text-gray-400">-</span>
                </td>
                <td class="table-cell text-sm text-gray-600">
                  {{ formatDateTime(submission.submittedAt || (submission as any).submitted_at) }}
                </td>
                <td class="table-cell text-sm text-gray-600">
                  {{ (submission.timeSpent !== undefined && submission.timeSpent !== null) 
                      ? formatTime(submission.timeSpent) 
                      : ((submission as any).time_spent !== undefined && (submission as any).time_spent !== null)
                        ? formatTime((submission as any).time_spent)
                        : '-' }}
                </td>
                <td class="table-cell">
                  <div class="flex gap-2">
                    <button
                      v-if="submission.status !== 'not_started' && submission.id"
                      @click="viewSubmission(submission)"
                      class="btn-xs btn-view"
                      title="查看详情"
                    >
                      查看
                    </button>
                    <button
                      v-if="submission.status === 'submitted' && submission.id"
                      @click="gradeSubmission(submission)"
                      class="btn-xs btn-grade"
                      title="评分"
                    >
                      评分
                    </button>
                    <span v-if="submission.status === 'not_started'" class="text-xs text-gray-400">
                      暂无操作
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
  
        <!-- 空状态 -->
        <div v-else class="empty-state">
          <div class="text-4xl mb-4">📭</div>
          <p class="text-gray-500">暂无提交记录</p>
        </div>
      </div>
  
      <!-- 评分模态框 -->
      <Teleport to="body">
        <GradingModal
          v-if="gradingSubmission"
          :key="gradingSubmission?.id || 'grading-modal'"
          :submission="gradingSubmission"
          :activity="activity"
          @close="gradingSubmission = null"
          @graded="handleGraded"
        />
      </Teleport>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, computed, onMounted, onUnmounted, watch, inject, type ComputedRef } from 'vue'
  import type { ActivitySubmission } from '../../../types/activity'
  import type { ActivityCellContent } from '../../../types/activity'
  import activityService from '../../../services/activity'
  import GradingModal from './GradingModal.vue'
  import { useRealtimeChannel } from '@/composables/useRealtimeChannel'
  import type { WebSocketMessage } from '@/composables/useRealtimeChannel'
  import { useUserStore } from '@/store/user'
  import { authService } from '@/services/auth'
  import { isUUID, toNumericId } from '@/utils/cellId'
  import logger from '@/utils/logger'
  
interface Props {
  cellId: number | string  // 支持数字和UUID字符串
  activity: ActivityCellContent
  sessionId?: number  // 从 props 传递的 sessionId（优先使用）
  lessonId?: number
  cellOrder?: number  // Cell 的 order（用于 UUID 到数字 ID 的转换）
}
  
  const props = defineProps<Props>()
  const userStore = useUserStore()
  
  // 🔧 从 inject 获取 sessionId（作为降级方案）
  const injectedSessionId = inject<ComputedRef<number | undefined> | undefined>('classroomSessionId', undefined)
  
  // 优先使用 props.sessionId，如果没有则使用 inject（兼容两种方式）
  const sessionId = computed(() => {
    // 优先级1: props.sessionId（从 ActivityCell 传递）
    if (props.sessionId !== undefined) {
      return props.sessionId
    }
    // 优先级2: inject（从 LessonEditor 的 provide）
    return injectedSessionId?.value
  })
  
  // 统计数据
  const statistics = ref({
    totalStudents: 0,
    submittedCount: 0,
    draftCount: 0,
    averageScore: null as number | null,
    averageTimeSpent: 0,
    itemStatistics: null as Record<string, any> | null,
  })
  
  // 提交列表
  const submissions = ref<any[]>([])
  const loading = ref(false)
  const refreshing = ref(false)
  const statusFilter = ref('')
  const selectedSubmissions = ref<number[]>([])
  const gradingSubmission = ref<any | null>(null)
  
  // 计算属性
  const progressPercent = computed(() => {
    if (statistics.value.totalStudents === 0) return 0
    return Math.round((statistics.value.submittedCount / statistics.value.totalStudents) * 100)
  })
  
  const allSelected = computed(() => {
    return submissions.value.length > 0 && selectedSubmissions.value.length === submissions.value.length
  })
  
  // 从活动配置获取满分
  const maxScore = computed(() => {
    return props.activity?.grading?.totalPoints ?? null
  })
  
  // 获取选择题及其统计
  const choiceItemsWithStats = computed(() => {
    try {
      if (!props.activity?.items) {
        if (process.env.NODE_ENV === 'development') {
          console.debug('UnifiedSubmissionPanel: activity.items 为空')
        }
        return []
      }
      
      // 🔧 添加调试日志，检查统计数据
      if (!statistics.value.itemStatistics) {
        if (process.env.NODE_ENV === 'development') {
          console.debug('UnifiedSubmissionPanel: itemStatistics 为空', {
            submittedCount: statistics.value.submittedCount,
            totalStudents: statistics.value.totalStudents,
            hasActivity: !!props.activity,
            hasItems: !!props.activity?.items,
            itemsCount: props.activity?.items?.length || 0,
            statisticsKeys: statistics.value.itemStatistics ? Object.keys(statistics.value.itemStatistics) : [],
          })
        }
        return []
      }
      
      // 开发环境下输出完整的统计数据用于调试
      if (process.env.NODE_ENV === 'development') {
        console.debug('UnifiedSubmissionPanel: itemStatistics 数据', {
          itemStatisticsKeys: Object.keys(statistics.value.itemStatistics),
          itemStatisticsSample: Object.keys(statistics.value.itemStatistics).slice(0, 2).reduce((acc, key) => {
            acc[key] = statistics.value.itemStatistics![key]
            return acc
          }, {} as Record<string, any>),
          activityItemsCount: props.activity?.items?.length || 0,
          activityItemsIds: props.activity?.items?.map(item => ({ id: item.id, type: item.type })) || [],
        })
      }
      
      const choiceTypes = ['single-choice', 'multiple-choice', 'true-false']
      const items = props.activity.items.filter(item => item && choiceTypes.includes(item.type))
      
      if (items.length === 0 && process.env.NODE_ENV === 'development') {
        console.debug('UnifiedSubmissionPanel: 没有找到选择题类型的题目')
        return []
      }
      
      return items.map((item, index) => {
      const itemId = item.id
      // 🔧 尝试多种方式匹配 itemId（字符串 vs 数字）
      // 先尝试所有可能的 key 格式
      const itemStatsKeys = Object.keys(statistics.value.itemStatistics || {})
      const itemStats = statistics.value.itemStatistics?.[itemId] 
        || statistics.value.itemStatistics?.[String(itemId)]
        || statistics.value.itemStatistics?.[Number(itemId)]
        || (itemStatsKeys.length > 0 ? statistics.value.itemStatistics?.[itemStatsKeys[0]] : null)
      
      // 仅在开发环境输出详细匹配日志（只输出第一个作为示例）
      if (process.env.NODE_ENV === 'development' && index === 0) {
        console.debug('UnifiedSubmissionPanel: 匹配题目统计示例', {
          itemId,
          itemIdType: typeof itemId,
          itemType: item.type,
          hasItemStats: !!itemStats,
          itemStatsKeys: itemStatsKeys.slice(0, 3), // 只显示前3个key
          itemStats: itemStats ? {
            attempts: itemStats.attempts,
            correct_count: itemStats.correct_count,
            hasOptionDist: !!itemStats.option_distribution,
            optionDistKeys: itemStats.option_distribution ? Object.keys(itemStats.option_distribution) : [],
          } : null,
        })
      }
      
      const optionDistribution = itemStats?.option_distribution || itemStats?.options || {}
      
      // 获取选项列表
      let options: Array<{ id: string; label: string; isCorrect?: boolean; count: number; percentage: number }> = []
      
      try {
        if (item.type === 'single-choice' && 'config' in item && item.config && Array.isArray(item.config.options)) {
          // 单选题：从配置中获取选项
          const totalResponses: number = (Object.values(optionDistribution).reduce((sum: number, count: any) => sum + (Number(count) || 0), 0) as number) || statistics.value.submittedCount || 1
          options = item.config.options.map((opt: any) => {
            const count = Number(optionDistribution[opt.id] || optionDistribution[String(opt.id)] || 0)
            return {
              id: opt.id,
              label: opt.text || opt.label || opt.id,
              isCorrect: opt.isCorrect,
              count,
              percentage: totalResponses > 0 ? Math.round((count / totalResponses) * 100) : 0,
            }
          })
        } else if (item.type === 'multiple-choice' && 'config' in item && item.config && Array.isArray(item.config.options)) {
          // 多选题：从配置中获取选项
          const totalResponses = statistics.value.submittedCount || 1
          options = item.config.options.map((opt: any) => {
            const count = Number(optionDistribution[opt.id] || optionDistribution[String(opt.id)] || 0)
            return {
              id: opt.id,
              label: opt.text || opt.label || opt.id,
              isCorrect: opt.isCorrect,
              count,
              percentage: totalResponses > 0 ? Math.round((count / totalResponses) * 100) : 0,
            }
          })
        } else if (item.type === 'true-false') {
          // 判断题：固定两个选项
          const totalResponses: number = (Object.values(optionDistribution).reduce((sum: number, count: any) => sum + (Number(count) || 0), 0) as number) || statistics.value.submittedCount || 1
          const config = 'config' in item ? item.config : null
          options = [
            {
              id: 'true',
              label: '正确',
              isCorrect: config && 'correctAnswer' in config ? config.correctAnswer === true : false,
              count: Number(optionDistribution.true || optionDistribution['true'] || 0),
              percentage: totalResponses > 0 ? Math.round((Number(optionDistribution.true || optionDistribution['true'] || 0) / totalResponses) * 100) : 0,
            },
            {
              id: 'false',
              label: '错误',
              isCorrect: config && 'correctAnswer' in config ? config.correctAnswer === false : false,
              count: Number(optionDistribution.false || optionDistribution['false'] || 0),
              percentage: totalResponses > 0 ? Math.round((Number(optionDistribution.false || optionDistribution['false'] || 0) / totalResponses) * 100) : 0,
            },
          ]
        }
      } catch (error) {
        logger.error('处理选择题选项时出错:', error, item)
        options = []
      }
      
        const result = {
          itemId,
          order: index,
          type: item.type,
          question: item.question || `题目 ${index + 1}`,
          options,
        }
        
        // 仅在开发环境输出统计结果（只输出第一个作为示例）
        if (process.env.NODE_ENV === 'development' && index === 0) {
          console.debug('UnifiedSubmissionPanel: 选择题统计结果示例', {
            itemId,
            type: item.type,
            optionsCount: options.length,
          })
        }
        
        return result
      }).filter(item => {
        const hasOptions = item && item.options && item.options.length > 0
        // 仅在开发环境输出过滤日志
        if (!hasOptions && process.env.NODE_ENV === 'development') {
          console.debug('UnifiedSubmissionPanel: 过滤掉没有选项的题目', {
            itemId: item?.itemId,
            type: item?.type,
          })
        }
        return hasOptions
      })
    } catch (error) {
      logger.error('计算选择题统计时出错:', error)
      return []
    }
  })
  
  // 获取题目类型标签
  function getItemTypeLabel(type: string): string {
    const labels: Record<string, string> = {
      'single-choice': '单选题',
      'multiple-choice': '多选题',
      'true-false': '判断题',
    }
    return labels[type] || type
  }
  
  // 工具函数：规范化 cellId 用于比较
  function normalizeCellId(cellId: string | number | null | undefined): string {
    if (cellId === null || cellId === undefined) return ''
    // 统一转换为字符串进行比较
    return String(cellId)
  }
  
  // 检查 cellId 是否匹配（统一使用 UUID 字符串比较）
  function isCellIdMatch(cellId1: string | number, cellId2: string | number): boolean {
    // 统一转换为字符串进行比较
    const str1 = String(cellId1)
    const str2 = String(cellId2)
    return str1 === str2
  }
  
  // 格式化时间
  function formatTime(seconds: number): string {
    if (!seconds) return '-'
    if (seconds < 60) return `${seconds}秒`
    const minutes = Math.floor(seconds / 60)
    return `${minutes}分钟`
  }
  
  function formatDateTime(dateStr: string | null): string {
    if (!dateStr) return '-'
    try {
      // 处理可能没有时区信息的时间字符串
      let processedDateStr = String(dateStr).trim()
      
      // 检查是否已有时区信息（Z 或 +/- 时区偏移）
      const hasTimezone = processedDateStr.endsWith('Z') || /[+-]\d{2}:?\d{2}$/.test(processedDateStr)
      
      if (!hasTimezone) {
        // 如果没有时区信息，假设它是 UTC 时间并添加 Z 后缀
        // 处理格式：YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DDTHH:MM:SS
        if (processedDateStr.includes(' ')) {
          // 空格格式转换为 ISO 格式
          processedDateStr = processedDateStr.replace(' ', 'T') + 'Z'
        } else if (processedDateStr.includes('T')) {
          // 已经是 ISO 格式，只需添加 Z
          processedDateStr = processedDateStr + 'Z'
        } else {
          // 其他格式，尝试解析后再处理
          processedDateStr = processedDateStr + 'Z'
        }
      }
      
      const date = new Date(processedDateStr)
      
      // 检查日期是否有效
      if (isNaN(date.getTime())) {
        console.warn('Invalid date string:', dateStr)
        return '-'
      }
      
      // 转换为中国时区 (UTC+8)
      // 使用 toLocaleString 并指定时区为 Asia/Shanghai
      return date.toLocaleString('zh-CN', {
        timeZone: 'Asia/Shanghai',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
      })
    } catch (error) {
      console.error('格式化时间失败:', dateStr, error)
      return '-'
    }
  }
  
  // 获取状态标签
  function getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      not_started: '未开始',
      draft: '草稿',
      submitted: '已提交',
      graded: '已评分',
      returned: '已退回',
    }
    return labels[status] || status
  }
  
  // 获取状态徽章样式
  function getStatusBadgeClass(status: string): string {
    const classes: Record<string, string> = {
      not_started: 'status-badge status-not-started',
      draft: 'status-badge status-draft',
      submitted: 'status-badge status-submitted',
      graded: 'status-badge status-graded',
      returned: 'status-badge status-returned',
    }
    return classes[status] || 'status-badge'
  }
  
  // 注意：现在统一使用 UUID，不再需要转换为数字 ID
  // 保留此函数以兼容旧代码，但直接返回 UUID 字符串
  async function resolveCellIdToNumeric(cellId: string | number): Promise<string | number | null> {
    // 统一使用 UUID，直接返回
    return cellId
  }

  // 加载统计数据
  async function loadStatistics() {
    refreshing.value = true
    try {
      // 移除频繁的轮询日志
      
      // 统一使用 UUID，直接传递
      const stats = await activityService.getStatistics(
        props.cellId,
        sessionId.value,
        props.lessonId
      )
      
      // 转换 API 返回的格式
      const statsAny = stats as any
      const totalStudents = stats.totalStudents || statsAny.total_students || 0
      const submittedCount = stats.submittedCount || statsAny.submitted_count || 0
      const draftCount = stats.draftCount || statsAny.draft_count || 0
      
      statistics.value = {
        totalStudents,
        submittedCount,
        draftCount,
        averageScore: stats.averageScore ?? statsAny.average_score ?? null,
        averageTimeSpent: stats.averageTimeSpent ?? statsAny.average_time_spent ?? 0,
        itemStatistics: stats.itemStatistics ?? statsAny.item_statistics ?? null,
      }
      
      // 静默加载统计数据
    } catch (error: any) {
      logger.error('加载统计数据失败:', error)
    } finally {
      refreshing.value = false
    }
  }
  
  // 加载提交列表
  async function loadSubmissions() {
    loading.value = true
    try {
      // 移除频繁的调试日志，只在必要时输出
      
      // 统一使用 UUID，直接传递
      const data = await activityService.getCellSubmissions(
        props.cellId,
        statusFilter.value || undefined,
        sessionId.value,
        props.lessonId
      )
      
      // 🔧 数据转换：将后端返回的蛇形命名转换为驼峰命名
      submissions.value = data.map((s: any) => ({
        ...s,
        // 学生信息字段（支持两种格式）
        studentName: s.studentName || s.student_name || '',
        studentEmail: s.studentEmail || s.student_email || '',
        // 时间字段转换
        submittedAt: s.submittedAt || s.submitted_at || null,
        startedAt: s.startedAt || s.started_at || null,
        gradedAt: s.gradedAt || s.graded_at || null,
        // 用时字段转换
        timeSpent: s.timeSpent !== undefined ? s.timeSpent : (s.time_spent !== undefined ? s.time_spent : null),
        // 其他字段（保持兼容）
        cellId: s.cellId || s.cell_id,
        lessonId: s.lessonId || s.lesson_id,
        studentId: s.studentId || s.student_id,
        sessionId: s.sessionId || s.session_id,
        maxScore: s.maxScore || s.max_score,
        autoGraded: s.autoGraded !== undefined ? s.autoGraded : (s.auto_graded !== undefined ? s.auto_graded : false),
        teacherFeedback: s.teacherFeedback || s.teacher_feedback,
        gradedBy: s.gradedBy || s.graded_by,
        processTrace: s.processTrace || s.process_trace,
        submissionCount: s.submissionCount !== undefined ? s.submissionCount : (s.submission_count !== undefined ? s.submission_count : 1),
        attemptNo: s.attemptNo !== undefined ? s.attemptNo : (s.attempt_no !== undefined ? s.attempt_no : 1),
        isLate: s.isLate !== undefined ? s.isLate : (s.is_late !== undefined ? s.is_late : false),
        activityPhase: s.activityPhase || s.activity_phase,
        createdAt: s.createdAt || s.created_at,
        updatedAt: s.updatedAt || s.updated_at,
        // 确保 responses 字段存在
        responses: s.responses || {},
      }))
    } catch (error: any) {
      logger.error('加载提交列表失败:', error)
      submissions.value = []
    } finally {
      loading.value = false
    }
  }
  
  // 刷新所有数据
  async function refreshAll() {
    await Promise.all([loadStatistics(), loadSubmissions()])
  }
  
  // 切换全选
  function toggleSelectAll() {
    if (allSelected.value) {
      selectedSubmissions.value = []
    } else {
      selectedSubmissions.value = submissions.value.map(s => s.id)
    }
  }
  
  // 查看提交详情
  function viewSubmission(submission: any) {
    gradingSubmission.value = submission
  }
  
  // 评分
  function gradeSubmission(submission: any) {
    gradingSubmission.value = submission
  }
  
  // 评分完成
  function handleGraded() {
    gradingSubmission.value = null
    refreshAll() // 重新加载所有数据
  }
  
  // 批量评分
  async function handleBulkGrade() {
    const score = prompt('请输入统一分数：')
    if (!score) return
  
    const scoreNum = parseFloat(score)
    if (isNaN(scoreNum)) {
      alert('请输入有效的分数')
      return
    }
  
    try {
      await activityService.bulkGrade(selectedSubmissions.value, scoreNum)
      alert('批量评分成功')
      selectedSubmissions.value = []
      refreshAll()
    } catch (error) {
      logger.error('Bulk grade failed:', error)
      alert('批量评分失败')
    }
  }
  
  // 批量退回
  async function handleBulkReturn() {
    const feedback = prompt('请输入退回原因：')
    if (!feedback) return
  
    try {
      await activityService.bulkReturn(selectedSubmissions.value, feedback)
      alert('批量退回成功')
      selectedSubmissions.value = []
      refreshAll()
    } catch (error) {
      logger.error('Bulk return failed:', error)
      alert('批量退回失败')
    }
  }
  
  // WebSocket 实时更新
  const channelDescriptor = computed(() => {
    if (sessionId.value) {
      return { scope: 'session' as const, id: sessionId.value }
    }
    return { scope: 'lesson' as const, id: props.lessonId! }
  })
  
  const {
    isConnected,
    isConnecting,
    connect: connectRealtime,
    disconnect: disconnectRealtime,
    registerListener,
    unregisterAll,
    requestStatistics: requestStats,
  } = useRealtimeChannel(channelDescriptor)
  
  // 处理统计更新消息
  function handleStatisticsUpdate(message: WebSocketMessage) {
    console.log('📊 UnifiedSubmissionPanel: 收到统计更新消息', {
      messageType: message.type,
      messageCellId: message.data.cell_id,
      propsCellId: props.cellId,
      sessionId: sessionId.value,
      timestamp: new Date().toLocaleTimeString(),
      messageData: message.data,
    })
    
    const messageCellId = message.data.cell_id
    const propsCellId = props.cellId
    
    // 使用改进的 cellId 匹配逻辑
    if (!isCellIdMatch(messageCellId, propsCellId)) {
      console.log('⚠️ Cell ID 不匹配，忽略消息:', { messageCellId, propsCellId })
      return
    }
    
    console.log('✅ Cell ID 匹配，更新统计数据')
    // 更新统计数据
    statistics.value = {
      totalStudents: message.data.total_students || 0,
      submittedCount: message.data.submitted_count || 0,
      draftCount: message.data.draft_count || 0,
      averageScore: message.data.average_score,
      averageTimeSpent: message.data.average_time_spent || 0,
      itemStatistics: message.data.item_statistics || null,
    }
    
    // 统计更新时也刷新列表
    loadSubmissions()
  }
  
  // 处理新提交通知
  function handleNewSubmission(message: WebSocketMessage) {
    console.log('📝 UnifiedSubmissionPanel: 收到新提交通知', {
      messageType: message.type,
      messageCellId: message.data.cell_id,
      propsCellId: props.cellId,
      sessionId: sessionId.value,
      timestamp: new Date().toLocaleTimeString(),
      messageData: message.data,
    })
    
    const messageCellId = message.data.cell_id
    const propsCellId = props.cellId
    
    // 使用改进的 cellId 匹配逻辑
    if (!isCellIdMatch(messageCellId, propsCellId)) {
      console.log('⚠️ Cell ID 不匹配，忽略消息:', { messageCellId, propsCellId })
      return
    }
    
    console.log('✅ Cell ID 匹配，刷新提交列表和统计')
    // 刷新列表和统计
    refreshAll()
  }
  
  let pollingInterval: ReturnType<typeof setInterval> | null = null
  
  // 监听 sessionId 变化，动态连接/断开 WebSocket
  watch(sessionId, async (newSessionId, oldSessionId) => {
    // 只在真正变化时输出日志
    
    // 如果 sessionId 从无到有，加载数据并连接 WebSocket
    if (newSessionId && !oldSessionId) {
      const isDev = process.env.NODE_ENV === 'development'
      if (isDev) {
        console.log('✅ UnifiedSubmissionPanel: sessionId 从无到有，开始加载数据', {
          sessionId: newSessionId,
        })
      }
      
      // 加载数据
      await refreshAll()
      
      try {
        await connectRealtime()
        if (isDev) {
          console.debug('UnifiedSubmissionPanel: WebSocket 连接成功', {
            sessionId: newSessionId,
            isConnected: isConnected.value,
          })
        }
        
        registerListener('new_submission', handleNewSubmission)
        registerListener('submission_statistics_updated', handleStatisticsUpdate)
        
        // 停止轮询
        if (pollingInterval) {
          clearInterval(pollingInterval)
          pollingInterval = null
        }
      } catch (error) {
        logger.warn('⚠️ UnifiedSubmissionPanel: WebSocket 连接失败，继续使用轮询', error)
      }
    }
    // 如果 sessionId 从有到无，断开 WebSocket，但不启动轮询
    // 因为没有 sessionId 意味着不是课堂模式，不需要实时更新
    else if (!newSessionId && oldSessionId) {
      disconnectRealtime()
      unregisterAll()
      // ✅ 停止轮询（如果有的话）
      if (pollingInterval) {
        clearInterval(pollingInterval)
        pollingInterval = null
      }
      // sessionId 已移除，静默处理
      // 不启动轮询，只保留当前数据
    }
  }, { immediate: false })

  onMounted(async () => {
    const isDev = process.env.NODE_ENV === 'development'
    
    // 只在开发环境输出初始状态
    if (isDev) {
      if (!sessionId.value) {
        console.warn('⚠️ UnifiedSubmissionPanel: sessionId 为空', {
          cellId: props.cellId,
          lessonId: props.lessonId,
          hasInjectedSessionId: !!injectedSessionId,
        })
      } else {
        console.debug('UnifiedSubmissionPanel 已挂载', {
          cellId: props.cellId,
          sessionId: sessionId.value,
        })
      }
    }
    
    // 🔧 只有在有 sessionId 时才加载数据（课堂模式）
    // 没有 sessionId 时，不加载数据，避免显示所有会话的混合数据
    if (sessionId.value) {
      // 初始加载数据（只加载一次，不自动轮询）
      await refreshAll()
      
      // 连接 WebSocket
      try {
        // 确保用户信息已加载
        if (!userStore.user && userStore.token) {
          try {
            const user = await authService.getCurrentUser()
            userStore.setUser(user)
          } catch (error) {
            logger.error('加载用户信息失败:', error)
          }
        }
        
        await connectRealtime()
        if (process.env.NODE_ENV === 'development') {
          console.debug('UnifiedSubmissionPanel: WebSocket 连接成功', {
            sessionId: sessionId.value,
            isConnected: isConnected.value,
          })
        }
        
        registerListener('new_submission', handleNewSubmission)
        registerListener('submission_statistics_updated', handleStatisticsUpdate)
        
        // ✅ WebSocket 连接成功时，不启动轮询，完全依赖实时推送
        // 只在 WebSocket 失败时才降级到轮询模式
        
        // 请求统计（用于实时更新）
        setTimeout(() => {
          // 统一使用 UUID，直接传递
          if (props.lessonId) {
            requestStats(props.cellId, props.lessonId)
          }
        }, 500)
      } catch (error) {
        logger.warn('⚠️ UnifiedSubmissionPanel: WebSocket 连接失败，降级到轮询模式（每5秒）', error)
        // WebSocket 失败时，定期刷新（每5秒）作为备用
        pollingInterval = setInterval(() => {
          refreshAll()
        }, 5000)
      }
    } else {
      // ✅ 没有 sessionId 时，不加载数据
      // 因为没有 sessionId 意味着不是课堂模式，不应该显示数据
      // 数据会在进入课堂模式（有 sessionId）后自动加载
      if (process.env.NODE_ENV === 'development') {
        console.debug('UnifiedSubmissionPanel: 没有 sessionId，等待进入课堂模式')
      }
    }
  })
  
  onUnmounted(() => {
    // 清理评分模态框
    gradingSubmission.value = null
    
    // 清理实时通道
    unregisterAll()
    disconnectRealtime()
    
    // 清理轮询定时器
    if (pollingInterval) {
      clearInterval(pollingInterval)
      pollingInterval = null
    }
  })
  </script>
  
  <style scoped>
  .unified-submission-panel {
    @apply bg-white rounded-lg border border-gray-200 shadow-sm;
  }
  
  /* 统计部分 */
  .statistics-section {
    @apply p-6 border-b border-gray-200;
  }
  
  .section-header {
    @apply flex items-center justify-between mb-4;
  }
  
  .section-title {
    @apply text-xl font-bold text-gray-900 flex items-center gap-2;
  }
  
  .title-icon {
    @apply text-2xl;
  }
  
  .header-actions {
    @apply flex items-center gap-3;
  }
  
  .connection-status {
    @apply flex items-center gap-2 text-sm;
  }
  
  .status-dot {
    @apply w-2 h-2 rounded-full;
  }
  
  .connected {
    @apply text-green-600;
  }
  
  .connected .status-dot {
    @apply bg-green-600 animate-pulse;
  }
  
  .connecting {
    @apply text-yellow-600;
  }
  
  .connecting .status-dot {
    @apply bg-yellow-600 animate-pulse;
  }
  
  .disconnected {
    @apply text-gray-400;
  }
  
  .disconnected .status-dot {
    @apply bg-gray-400;
  }
  
  .refresh-btn {
    @apply flex items-center gap-2 px-3 py-1.5 text-sm bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
  }
  
  .stats-grid {
    @apply grid grid-cols-2 md:grid-cols-3 gap-4 mb-6;
  }
  
  .stats-grid-compact {
    @apply grid grid-cols-2 md:grid-cols-4 gap-4 mb-6;
  }
  
  .stat-card {
    @apply bg-gray-50 rounded-lg p-4 transition-all hover:shadow-md flex items-center gap-3;
  }
  
  .stat-icon-wrapper {
    @apply flex-shrink-0 w-12 h-12 rounded-lg flex items-center justify-center;
  }
  
  .stat-icon {
    @apply text-2xl;
  }
  
  .stat-content {
    @apply flex-1 min-w-0;
  }
  
  .stat-label {
    @apply text-sm text-gray-600 mb-1;
  }
  
  .stat-value {
    @apply text-2xl font-bold;
  }
  
  .stat-percentage {
    @apply text-xs text-gray-500 mt-1;
  }
  
  .stat-subtext {
    @apply text-xs text-gray-500 mt-1;
  }
  
  .stat-card-primary .stat-icon-wrapper {
    @apply bg-blue-100;
  }
  
  .stat-card-success .stat-icon-wrapper {
    @apply bg-green-100;
  }
  
  .stat-card-warning .stat-icon-wrapper {
    @apply bg-yellow-100;
  }
  
  .stat-card-gray .stat-icon-wrapper {
    @apply bg-gray-100;
  }
  
  .stat-card-info .stat-icon-wrapper {
    @apply bg-blue-100;
  }
  
  .stat-card-purple .stat-icon-wrapper {
    @apply bg-purple-100;
  }
  
  .progress-section {
    @apply mt-4;
  }
  
  .progress-header {
    @apply flex items-center justify-between mb-2;
  }
  
  .progress-label {
    @apply text-sm font-medium text-gray-700;
  }
  
  .progress-text {
    @apply text-sm text-gray-600;
  }
  
  .progress-bar {
    @apply w-full h-3 bg-gray-200 rounded-full overflow-hidden;
  }
  
  .progress-fill {
    @apply h-full bg-blue-600 transition-all duration-300 ease-in-out;
  }
  
  /* 提交列表部分 */
  .submission-list-section {
    @apply p-6;
  }
  
  .filter-bar {
    @apply flex items-center gap-3;
  }
  
  .filter-select {
    @apply px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500;
  }
  
  .bulk-actions {
    @apply flex items-center justify-between px-4 py-3 bg-blue-50 border-b border-blue-200 mb-4;
  }
  
  .loading-state {
    @apply flex flex-col items-center justify-center py-12;
  }
  
  .spinner {
    @apply w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-3;
  }
  
  .submissions-table {
    @apply overflow-x-auto;
  }
  
  .table-header {
    @apply px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider bg-gray-50 border-b border-gray-200;
  }
  
  .table-row {
    @apply hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0;
  }
  
  .table-cell {
    @apply px-4 py-4 whitespace-nowrap;
  }
  
  .student-info {
    @apply min-w-[150px];
  }
  
  .status-badge {
    @apply inline-flex items-center px-2 py-1 text-xs font-medium rounded-full;
  }
  
  .status-draft {
    @apply bg-gray-100 text-gray-700;
  }
  
  .status-submitted {
    @apply bg-blue-100 text-blue-800;
  }
  
  .status-graded {
    @apply bg-green-100 text-green-800;
  }
  
  .status-returned {
    @apply bg-yellow-100 text-yellow-800;
  }
  
  .status-not-started {
    @apply bg-gray-100 text-gray-600;
  }
  
  .late-badge {
    @apply ml-2 inline-flex items-center px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full;
  }
  
  .score-display {
    @apply flex items-baseline gap-1;
  }
  
  .btn-xs {
    @apply px-3 py-1 text-xs rounded-lg transition-colors;
  }
  
  .btn-view {
    @apply bg-gray-100 text-gray-700 hover:bg-gray-200;
  }
  
  .btn-grade {
    @apply bg-blue-100 text-blue-700 hover:bg-blue-200;
  }
  
  .btn-sm {
    @apply px-3 py-1 text-sm rounded-lg transition-colors;
  }
  
  .btn-primary {
    @apply bg-blue-600 text-white hover:bg-blue-700;
  }
  
  .btn-secondary {
    @apply bg-gray-100 text-gray-700 hover:bg-gray-200;
  }
  
  .empty-state {
    @apply flex flex-col items-center justify-center py-16 text-center;
  }
  
  /* 选择题选项分布样式 */
  .choice-statistics-section {
    @apply mt-6 pt-6 border-t border-gray-200;
  }
  
  .choice-section-title {
    @apply text-lg font-semibold text-gray-900 mb-4;
  }
  
  .choice-items-grid {
    @apply grid grid-cols-1 lg:grid-cols-2 gap-4;
  }
  
  .choice-item-card {
    @apply bg-gray-50 rounded-lg p-4 border border-gray-200;
  }
  
  .choice-item-header {
    @apply flex items-center justify-between mb-2;
  }
  
  .choice-item-order {
    @apply text-sm font-medium text-gray-700;
  }
  
  .choice-item-type {
    @apply text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full;
  }
  
  .choice-item-question {
    @apply text-sm text-gray-800 mb-3 line-clamp-2;
  }
  
  .choice-options-list {
    @apply space-y-2;
  }
  
  .choice-option-item {
    @apply bg-white rounded p-2 border border-gray-200;
  }
  
  .choice-option-item.is-correct {
    @apply border-green-300 bg-green-50;
  }
  
  .option-header {
    @apply flex items-center justify-between mb-1;
  }
  
  .option-label {
    @apply text-sm font-medium text-gray-800 flex-1;
  }
  
  .option-count {
    @apply text-xs text-gray-600 mr-2;
  }
  
  .option-percentage {
    @apply text-xs font-semibold text-blue-600 min-w-[3rem] text-right;
  }
  
  .option-progress-bar {
    @apply w-full h-2 bg-gray-200 rounded-full overflow-hidden;
  }
  
  .option-progress-fill {
    @apply h-full bg-blue-500 transition-all duration-300;
  }
  
  .choice-option-item.is-correct .option-progress-fill {
    @apply bg-green-500;
  }
  </style>