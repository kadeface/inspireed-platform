<template>
  <div class="submission-list">
    <!-- 标题和过滤器 -->
    <div class="list-header">
      <h3 class="list-title">📝 学生提交列表</h3>
      <div class="filter-bar">
        <select v-model="statusFilter" class="filter-select" @change="loadSubmissions">
          <option value="">全部状态</option>
          <option value="not_started">未开始</option>
          <option value="draft">草稿</option>
          <option value="submitted">已提交</option>
          <option value="graded">已评分</option>
          <option value="returned">已退回</option>
        </select>
        <button @click="loadSubmissions" class="btn-refresh" :disabled="loading">
          <svg class="w-4 h-4" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 提交统计 -->
    <div v-if="submissions.length > 0 || !loading" class="submission-stats">
      <div class="stats-grid">
        <div class="stat-card stat-total">
          <div class="stat-icon">👥</div>
          <div class="stat-content">
            <div class="stat-label">总学生数</div>
            <div class="stat-value">{{ statistics.totalStudents }}</div>
          </div>
        </div>
        <div class="stat-card stat-submitted">
          <div class="stat-icon">✅</div>
          <div class="stat-content">
            <div class="stat-label">已提交</div>
            <div class="stat-value">{{ statistics.submittedCount }}</div>
            <div class="stat-percentage">{{ statistics.submittedPercent }}%</div>
          </div>
        </div>
        <div class="stat-card stat-draft">
          <div class="stat-icon">📝</div>
          <div class="stat-content">
            <div class="stat-label">草稿中</div>
            <div class="stat-value">{{ statistics.draftCount }}</div>
            <div class="stat-percentage">{{ statistics.draftPercent }}%</div>
          </div>
        </div>
        <div class="stat-card stat-graded">
          <div class="stat-icon">⭐</div>
          <div class="stat-content">
            <div class="stat-label">已评分</div>
            <div class="stat-value">{{ statistics.gradedCount }}</div>
            <div class="stat-percentage">{{ statistics.gradedPercent }}%</div>
          </div>
        </div>
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
            <th class="table-header">排名</th>
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
            v-for="submission in submissionsWithRank"
            :key="submission.id"
            class="table-row"
            :class="{ 'top-three': submission.rank !== null && submission.rank <= 3 }"
          >
            <td class="table-cell">
              <input
                type="checkbox"
                :value="submission.id"
                v-model="selectedSubmissions"
              />
            </td>
            <td class="table-cell">
              <div class="rank-display">
                <span v-if="submission.rank === 1" class="rank-badge rank-first" title="🏆 冠军">
                  🥇
                </span>
                <span v-else-if="submission.rank === 2" class="rank-badge rank-second" title="🥈 亚军">
                  🥈
                </span>
                <span v-else-if="submission.rank === 3" class="rank-badge rank-third" title="🥉 季军">
                  🥉
                </span>
                <span v-else-if="submission.rank !== null" class="rank-number">
                  {{ submission.rank }}
                </span>
                <span v-else class="rank-unranked">-</span>
              </div>
            </td>
            <td class="table-cell">
              <div class="student-info">
                <div class="font-medium">{{ submission.studentName || submission.student_name || '未知学生' }}</div>
                <div class="text-xs text-gray-500">{{ submission.studentEmail || submission.student_email || '' }}</div>
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
                  v-if="submission.id && submission.id !== 0 && submission.status !== 'draft'"
                  @click="viewSubmission(submission)"
                  class="btn-xs btn-view"
                  title="查看详情"
                >
                  查看
                </button>
                <button
                  v-if="submission.status === 'submitted' && submission.id && submission.id !== 0"
                  @click="gradeSubmission(submission)"
                  class="btn-xs btn-grade"
                  title="评分"
                >
                  评分
                </button>
                <span v-if="!submission.id || submission.id === 0" class="text-xs text-gray-400">
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

    <!-- 选择题选项统计 -->
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

    <!-- 评分模态框 -->
    <GradingModal
      v-if="gradingSubmission"
      :submission="gradingSubmission"
      :activity="activity"
      @close="gradingSubmission = null"
      @graded="handleGraded"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { ActivitySubmission } from '../../../types/activity'
import type { ActivityCellContent } from '../../../types/activity'
import activityService from '../../../services/activity'
import GradingModal from './GradingModal.vue'
import { useRealtimeChannel } from '@/composables/useRealtimeChannel'
import type { WebSocketMessage } from '@/composables/useRealtimeChannel'
import logger from '@/utils/logger'

// 扩展 ActivitySubmission 类型，包含学生信息（API 返回的数据包含这些字段）
interface ActivitySubmissionWithStudent extends ActivitySubmission {
  studentName?: string
  studentEmail?: string
  student_name?: string  // 支持 snake_case（向后兼容）
  student_email?: string  // 支持 snake_case（向后兼容）
  sessionId?: number  // 课堂会话ID
  session_id?: number  // 支持 snake_case（向后兼容）
}

interface Props {
  cellId: number
  activity: ActivityCellContent
  sessionId?: number
  lessonId?: number
}

const props = defineProps<Props>()

const submissions = ref<ActivitySubmissionWithStudent[]>([])
const loading = ref(false)
const statusFilter = ref('')
const selectedSubmissions = ref<number[]>([])
const gradingSubmission = ref<any | null>(null)

// 全选状态（基于原始提交列表）
const allSelected = computed(() => {
  return submissions.value.length > 0 && selectedSubmissions.value.length === submissions.value.length
})

// 提交统计
const statistics = computed(() => {
  const total = submissions.value.length
  const submitted = submissions.value.filter(s => s.status === 'submitted').length
  const draft = submissions.value.filter(s => s.status === 'draft').length
  const graded = submissions.value.filter(s => s.status === 'graded').length
  const notStarted = submissions.value.filter(s => !s.id || s.id === 0).length
  
  // 总学生数（包括未开始的）
  const totalStudents = total
  
  return {
    totalStudents,
    submittedCount: submitted,
    draftCount: draft,
    gradedCount: graded,
    notStartedCount: notStarted,
    submittedPercent: totalStudents > 0 ? Math.round((submitted / totalStudents) * 100) : 0,
    draftPercent: totalStudents > 0 ? Math.round((draft / totalStudents) * 100) : 0,
    gradedPercent: totalStudents > 0 ? Math.round((graded / totalStudents) * 100) : 0,
  }
})

// 带排名的提交列表（按分数排序）
const submissionsWithRank = computed(() => {
  // 分离已评分和未评分的提交
  // 已评分：有分数且不是未开始状态（通过id判断）
  const gradedSubmissions = submissions.value.filter(s => 
    s.score !== null && s.score !== undefined && s.id && s.id !== 0
  )
  const ungradedSubmissions = submissions.value.filter(s => 
    !gradedSubmissions.includes(s)
  )
  
  // 对已评分的提交按分数从高到低排序
  const sortedGraded = [...gradedSubmissions].sort((a, b) => {
    const scoreA = a.score ?? 0
    const scoreB = b.score ?? 0
    // 分数高的在前
    if (scoreB !== scoreA) {
      return scoreB - scoreA
    }
    // 分数相同，按提交时间排序（早提交的在前）
    const timeA = new Date(a.submittedAt || a.createdAt || 0).getTime()
    const timeB = new Date(b.submittedAt || b.createdAt || 0).getTime()
    return timeA - timeB
  })
  
  // 添加排名信息（正确处理并列情况）
  let currentRank = 1
  const rankedSubmissions: Array<ActivitySubmissionWithStudent & { rank: number | null }> = []
  
  for (let i = 0; i < sortedGraded.length; i++) {
    const submission = sortedGraded[i]
    
    // 如果不是第一个，检查是否与前一个分数相同
    if (i > 0) {
      const prevScore = sortedGraded[i - 1].score ?? 0
      const currentScore = submission.score ?? 0
      
      // 如果分数不同，更新排名
      if (currentScore !== prevScore) {
        currentRank = i + 1
      }
      // 如果分数相同，保持相同排名（并列）
    }
    
    rankedSubmissions.push({
      ...submission,
      rank: currentRank,
    })
  }
  
  // 未评分的提交不显示排名，添加到末尾
  const ungradedWithNullRank = ungradedSubmissions.map(s => ({
    ...s,
    rank: null,
  }))
  
  return [...rankedSubmissions, ...ungradedWithNullRank]
})

// 获取选择题及其统计（从提交数据中计算）
const choiceItemsWithStats = computed(() => {
  try {
    if (!props.activity?.items || submissions.value.length === 0) {
      return []
    }
    
    const choiceTypes = ['single-choice', 'multiple-choice', 'true-false']
    const items = props.activity.items.filter((item: any) => item && choiceTypes.includes(item.type))
    
    if (items.length === 0) {
      return []
    }
    
    return items.map((item: any, index: number) => {
      const itemId = item.id
      const itemIdStr = String(itemId)
      
      // 从提交数据中统计选项分布
      const optionDistribution: Record<string, number> = {}
      let totalResponses = 0
      
      // 统计已提交和已评分的答案（也包括草稿，因为草稿也可能有答案）
      const allAnswers = submissions.value
        .filter(s => {
          // 只统计有实际提交ID的（排除未开始的占位符）
          const hasValidId = s.id && s.id !== 0
          const hasResponses = s.responses && typeof s.responses === 'object' && Object.keys(s.responses).length > 0
          
          if (!hasValidId || !hasResponses) {
            return false
          }
          
          return true
        })
        .map(s => {
          // 尝试多种可能的 key 格式
          let answer = s.responses?.[itemId] || 
                       s.responses?.[itemIdStr] || 
                       s.responses?.[String(itemId)] ||
                       null
          
          // 🔍 如果还是找不到，尝试遍历所有 key 看看是否有匹配的
          if (!answer && s.responses) {
            const allKeys = Object.keys(s.responses)
            // 尝试模糊匹配（比如 itemId 是 UUID，但 key 可能是其他格式）
            for (const key of allKeys) {
              if (key === itemId || key === itemIdStr || key === String(itemId)) {
                answer = s.responses[key]
                break
              }
            }
          }
          
          return { submission: s, answer, responseKeys: s.responses ? Object.keys(s.responses) : [] }
        })
        .filter(({ answer }) => answer !== null && answer !== undefined)
      
      totalResponses = allAnswers.length
      
      allAnswers.forEach(({ answer }: any) => {
        if (item.type === 'single-choice' || item.type === 'true-false') {
          // 单选题或判断题：答案是单个选项ID
          // 答案可能是对象 { answer: "A" } 或直接是字符串 "A"
          const optionId = (answer && typeof answer === 'object' && answer.answer) 
            ? String(answer.answer) 
            : String(answer || '')
          
          if (optionId) {
            optionDistribution[optionId] = (optionDistribution[optionId] || 0) + 1
          }
        } else if (item.type === 'multiple-choice') {
          // 多选题：答案是选项ID数组
          const optionIds = (answer && typeof answer === 'object' && answer.answer)
            ? (Array.isArray(answer.answer) ? answer.answer : [answer.answer])
            : (Array.isArray(answer) ? answer : [answer])
          
          optionIds.forEach((optId: any) => {
            const optIdStr = String(optId)
            if (optIdStr) {
              optionDistribution[optIdStr] = (optionDistribution[optIdStr] || 0) + 1
            }
          })
        }
      })
      
      // 获取选项列表
      let options: Array<{ id: string; label: string; isCorrect?: boolean; count: number; percentage: number }> = []
      
      try {
        if (item.type === 'single-choice' && 'config' in item && item.config && Array.isArray(item.config.options)) {
          // 单选题：从配置中获取选项
          options = item.config.options.map((opt: any) => {
            const optId = String(opt.id)
            const count = Number(optionDistribution[optId] || optionDistribution[opt.id] || 0)
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
          options = item.config.options.map((opt: any) => {
            const optId = String(opt.id)
            const count = Number(optionDistribution[optId] || optionDistribution[opt.id] || 0)
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
        console.error('处理选择题选项时出错:', error)
        options = []
      }
      
      return {
        itemId,
        order: index,
        type: item.type,
        question: item.question || `题目 ${index + 1}`,
        options,
      }
    }).filter((item: any) => item && item.options && item.options.length > 0)
  } catch (error) {
    console.error('计算选择题统计时出错:', error)
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

// 切换全选
function toggleSelectAll() {
  if (allSelected.value) {
    selectedSubmissions.value = []
  } else {
    selectedSubmissions.value = submissions.value.map(s => s.id)
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

// 格式化时间
function formatDateTime(dateStr: string | null | undefined): string {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch (error) {
    console.error('格式化时间失败:', dateStr, error)
    return '-'
  }
}

function formatTime(seconds: number): string {
  if (seconds < 60) return `${seconds}秒`
  const minutes = Math.floor(seconds / 60)
  return `${minutes}分钟`
}

// 加载提交列表
async function loadSubmissions() {
  loading.value = true
  try {
    console.log('🔍 加载提交列表:', {
      cellId: props.cellId,
      sessionId: props.sessionId,
      lessonId: props.lessonId,
      statusFilter: statusFilter.value,
    })
    
    const data = await activityService.getCellSubmissions(
      props.cellId,
      statusFilter.value || undefined,
      props.sessionId,
      props.lessonId
    )
    
    console.log('📥 收到提交列表数据:', {
      count: data.length,
      submissions: data.map((s: any) => ({
        id: s.id,
        studentName: s.studentName || s.student_name,
        sessionId: s.sessionId || s.session_id,
        status: s.status,
      })),
    })
    
    // 🔧 转换字段名：将 snake_case 转换为 camelCase
    const normalizedData = data.map((s: any) => {
      // 🔍 确保 responses 字段被正确保留
      const responses = s.responses !== undefined && s.responses !== null 
        ? s.responses 
        : (s.response || {}) // 兼容可能的拼写错误
      
      return {
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
        // 🔧 确保 responses 字段存在且正确保留
        responses: responses,
      }
    })
    
    // 🔧 客户端过滤：确保只显示当前会话的提交（双重保险）
    // 如果有 sessionId，严格过滤，不显示其他会话或课后提交
    let finalData = normalizedData
    if (props.sessionId) {
      finalData = normalizedData.filter((s: any) => {
        const submissionSessionId = s.sessionId || s.session_id
        // 严格匹配：只显示当前 sessionId 的提交
        return submissionSessionId === props.sessionId
      })
      
      // 如果过滤后数据减少，说明后端可能没有正确过滤
      if (finalData.length !== normalizedData.length) {
        console.warn('发现不属于当前会话的提交，已过滤', {
          beforeFilter: normalizedData.length,
          afterFilter: finalData.length,
        })
      }
    }
    
    submissions.value = finalData as ActivitySubmissionWithStudent[]
    
    console.log('✅ 最终提交列表:', {
      total: finalData.length,
      submissions: finalData.map((s: any) => ({
        id: s.id,
        studentName: s.studentName,
        status: s.status,
        sessionId: s.sessionId,
      })),
    })
  } catch (error: any) {
    console.error('❌ 加载提交列表失败:', error)
    console.error('错误详情:', {
      message: error?.message,
      response: error?.response?.data,
      status: error?.response?.status,
    })
    submissions.value = []
  } finally {
    loading.value = false
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
  loadSubmissions() // 重新加载列表
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
    loadSubmissions()
  } catch (error) {
    console.error('Bulk grade failed:', error)
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
    loadSubmissions()
  } catch (error) {
    console.error('Bulk return failed:', error)
    alert('批量退回失败')
  }
}

// WebSocket 实时更新
const channelDescriptor = computed(() => {
  if (props.sessionId) {
    return { scope: 'session' as const, id: props.sessionId }
  }
  return { scope: 'lesson' as const, id: props.lessonId! }
})

const {
  isConnected,
  connect: connectRealtime,
  disconnect: disconnectRealtime,
  registerListener,
  unregisterAll,
} = useRealtimeChannel(channelDescriptor)

// 监听新提交通知
function handleNewSubmission(message: WebSocketMessage) {
  const messageCellId = message.data.cell_id
  const propsCellId = props.cellId
  
  console.log('📨 收到新提交通知:', {
    messageCellId,
    propsCellId,
    messageData: message.data,
    match: String(messageCellId) === String(propsCellId),
  })
  
  // 支持数字和字符串比较
  if (String(messageCellId) !== String(propsCellId)) {
    console.warn('⚠️ CellId 不匹配，忽略消息', {
      messageCellId,
      propsCellId,
    })
    return
  }
  
  console.log('✅ CellId 匹配，刷新提交列表')
  // 自动刷新列表
  loadSubmissions()
}

// 监听统计更新通知（也会触发列表刷新）
function handleStatisticsUpdate(message: WebSocketMessage) {
  const messageCellId = message.data.cell_id
  const propsCellId = props.cellId
  
  console.log('📊 收到统计更新通知:', {
    messageCellId,
    propsCellId,
    messageData: message.data,
    match: String(messageCellId) === String(propsCellId),
  })
  
  // 支持数字和字符串比较
  if (String(messageCellId) !== String(propsCellId)) {
    console.warn('⚠️ CellId 不匹配，忽略统计更新', {
      messageCellId,
      propsCellId,
    })
    return
  }
  
  console.log('✅ CellId 匹配，刷新提交列表')
  // 自动刷新列表
  loadSubmissions()
}

let pollingInterval: ReturnType<typeof setInterval> | null = null

onMounted(async () => {
  // 初始加载
  await loadSubmissions()
  
  // 连接 WebSocket（如果有 sessionId）
  if (props.sessionId) {
    try {
      await connectRealtime()
      registerListener('new_submission', handleNewSubmission)
      registerListener('submission_statistics_updated', handleStatisticsUpdate)
      
      console.log('✅ SubmissionList: WebSocket 连接成功，将仅使用实时推送，不进行轮询')
      // ✅ WebSocket 连接成功时，不启动轮询，完全依赖实时推送
      // 只在 WebSocket 失败时才降级到轮询模式
    } catch (error) {
      console.warn('⚠️ SubmissionList: WebSocket 连接失败，降级到轮询模式（每5秒）', error)
      // WebSocket 失败时，定期刷新（每5秒）作为备用
      pollingInterval = setInterval(() => {
        loadSubmissions()
      }, 5000)
    }
  } else {
    // 没有 sessionId 时，使用轮询（每5秒）
    // 因为没有 sessionId 时无法建立 WebSocket 连接
    console.log('ℹ️ SubmissionList: 无 sessionId，使用轮询模式（每5秒）')
    pollingInterval = setInterval(() => {
      loadSubmissions()
    }, 5000)
  }
})

onUnmounted(() => {
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
.submission-list {
  @apply bg-white rounded-lg border border-gray-200;
}

.list-header {
  @apply flex items-center justify-between p-6 border-b border-gray-200;
}

.list-title {
  @apply text-xl font-bold text-gray-900;
}

.filter-bar {
  @apply flex items-center gap-3;
}

.filter-select {
  @apply px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.btn-refresh {
  @apply flex items-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50;
}

/* 提交统计样式 */
.submission-stats {
  @apply px-6 py-4 border-b border-gray-200 bg-gray-50;
}

.stats-grid {
  @apply grid grid-cols-2 md:grid-cols-4 gap-4;
}

.stat-card {
  @apply bg-white rounded-lg p-4 border border-gray-200 flex items-center gap-3 transition-all hover:shadow-md;
}

.stat-icon {
  @apply text-2xl flex-shrink-0;
}

.stat-content {
  @apply flex-1 min-w-0;
}

.stat-label {
  @apply text-xs text-gray-600 mb-1;
}

.stat-value {
  @apply text-xl font-bold text-gray-900;
}

.stat-percentage {
  @apply text-xs text-gray-500 mt-0.5;
}

.stat-total .stat-icon {
  @apply text-blue-500;
}

.stat-submitted .stat-icon {
  @apply text-green-500;
}

.stat-draft .stat-icon {
  @apply text-yellow-500;
}

.stat-graded .stat-icon {
  @apply text-purple-500;
}

.bulk-actions {
  @apply flex items-center justify-between px-6 py-3 bg-blue-50 border-b border-blue-200;
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

/* 选择题选项统计样式 */
.choice-statistics-section {
  @apply px-6 py-6 border-t border-gray-200;
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

.choice-option-item.is-correct .option-percentage {
  @apply text-green-600;
}

/* 排名样式 */
.rank-display {
  @apply flex items-center justify-center min-w-[60px];
}

.rank-badge {
  @apply text-2xl flex-shrink-0;
  animation: rankPulse 2s ease-in-out infinite;
}

.rank-first {
  filter: drop-shadow(0 2px 4px rgba(255, 215, 0, 0.4));
}

.rank-second {
  filter: drop-shadow(0 2px 4px rgba(192, 192, 192, 0.4));
}

.rank-third {
  filter: drop-shadow(0 2px 4px rgba(205, 127, 50, 0.4));
}

.rank-number {
  @apply inline-flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold text-sm;
}

.rank-unranked {
  @apply text-gray-400 text-sm;
}

.table-row.top-three {
  @apply bg-gradient-to-r from-yellow-50/30 to-transparent;
}

@keyframes rankPulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.9;
  }
}
</style>

