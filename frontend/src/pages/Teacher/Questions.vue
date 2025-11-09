<template>
  <div class="teacher-assessment-page min-h-screen bg-gray-50">
    <!-- 顶部抬头 -->
    <div class="bg-white border-b">
      <div
        class="max-w-7xl mx-auto px-4 py-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between"
      >
        <div>
          <p class="text-xs uppercase tracking-wide text-blue-600 font-semibold">Check</p>
          <h1 class="text-2xl font-bold text-gray-900">过程性评估总览</h1>
          <p class="text-sm text-gray-500 mt-1">
            汇集课堂提交、流程表现与互动反馈，全景洞察学习进展
          </p>
        </div>
        <div class="flex items-center gap-3">
          <select
            v-model="selectedLessonId"
            class="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          >
            <option v-if="lessons.length === 0" value="">暂无课程</option>
            <option
              v-for="lesson in lessons"
              :key="lesson.id"
              :value="lesson.id"
            >
              {{ lesson.title }}
            </option>
          </select>
          <button
            @click="handleRefresh"
            class="inline-flex items-center gap-2 px-3 py-2 text-sm rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-100 transition-colors"
            :disabled="overviewLoading"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            刷新
          </button>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 py-6 space-y-8">
      <!-- 课程加载状态 -->
      <div
        v-if="lessonLoading"
        class="flex items-center justify-center py-16 text-gray-500"
      >
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mr-3"></div>
        正在加载课程...
      </div>

      <template v-else>
        <div
          v-if="!selectedLessonId"
          class="bg-white border border-dashed border-gray-200 rounded-xl p-12 text-center text-gray-500"
        >
          暂无可用课程，创建课程后即可查看过程性评估数据。
        </div>

        <div v-else>
          <!-- 概览卡片 -->
          <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div class="overview-card">
              <div class="overview-label">参与学生</div>
              <div class="overview-value">
                {{ overviewMetrics.totalStudents }}
              </div>
              <p class="overview-subtle">
                已纳入评估的学生总数
              </p>
            </div>
            <div class="overview-card">
              <div class="overview-label">提交率</div>
              <div class="overview-value">
                {{ formatPercentage(overviewMetrics.submissionRate) }}
              </div>
              <p class="overview-subtle">
                提交或已评分：{{ overviewMetrics.submittedStudentCount }}/{{ overviewMetrics.totalStudents }}
              </p>
            </div>
            <div class="overview-card">
              <div class="overview-label">平均成绩</div>
              <div class="overview-value">
                {{ overviewMetrics.averageScore !== null ? `${overviewMetrics.averageScore.toFixed(1)} 分` : '—' }}
              </div>
              <p class="overview-subtle">
                基于所有活动的平均得分
              </p>
            </div>
            <div class="overview-card">
              <div class="overview-label">风险提醒</div>
              <div class="overview-value">
                {{ riskCounts.total }}
              </div>
              <p class="overview-subtle">
                高风险 {{ riskCounts.high }} · 中风险 {{ riskCounts.medium }}
              </p>
            </div>
          </div>

          <!-- 加载状态 -->
          <div
            v-if="overviewLoading"
            class="flex items-center justify-center py-16 text-gray-500"
          >
            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mr-3"></div>
            正在获取评估数据...
          </div>

          <template v-else>
            <!-- 风险学生 -->
            <section class="section-card">
              <header class="section-header">
                <div>
                  <h2 class="section-title">学习风险雷达</h2>
                  <p class="section-subtitle">
                    根据过程数据判定的高风险与关注学生，便于快速干预
                  </p>
                </div>
              </header>

              <div v-if="riskStudents.length === 0" class="empty-block">
                <div class="text-4xl mb-3">✅</div>
                <p class="text-gray-600 font-medium">暂无风险提醒</p>
                <p class="text-gray-400 text-sm">
                  最新学习行为稳定，当出现异常波动时会即时提示。
                </p>
              </div>

              <div v-else class="overflow-x-auto">
                <table class="min-w-full text-left">
                  <thead class="text-xs uppercase text-gray-400 border-b">
                    <tr>
                      <th class="py-2 pr-6">学生</th>
                      <th class="py-2 pr-6">风险等级</th>
                      <th class="py-2 pr-6">平均成绩</th>
                      <th class="py-2 pr-6">平均用时</th>
                      <th class="py-2">建议</th>
                    </tr>
                  </thead>
                  <tbody class="text-sm text-gray-700">
                    <tr
                      v-for="record in riskStudents"
                      :key="record.studentId + (record.phase || '')"
                      class="border-b last:border-transparent"
                    >
                      <td class="py-3 pr-6 font-medium text-gray-900">
                        学生 #{{ record.studentId }}
                      </td>
                      <td class="py-3 pr-6">
                        <span
                          :class="[
                            'inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold',
                            record.riskLevel === 'high'
                              ? 'bg-red-100 text-red-700'
                              : record.riskLevel === 'medium'
                                ? 'bg-yellow-100 text-yellow-700'
                                : 'bg-gray-100 text-gray-500'
                          ]"
                        >
                          {{ riskLevelLabel(record.riskLevel) }}
                        </span>
                      </td>
                      <td class="py-3 pr-6">
                        {{ record.metrics?.average_score !== undefined ? `${record.metrics.average_score?.toFixed(1)} 分` : '—' }}
                      </td>
                      <td class="py-3 pr-6">
                        {{ formatDuration(record.metrics?.average_time_spent) }}
                      </td>
                      <td class="py-3">
                        <ul class="list-disc list-inside text-gray-500 space-y-1 text-xs">
                          <li v-for="tip in record.recommendations || []" :key="tip.type">
                            {{ tip.message }}
                          </li>
                          <li v-if="!record.recommendations || record.recommendations.length === 0">
                            建议跟进学习进度或提供针对性辅导。
                          </li>
                        </ul>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            <!-- 活动表现 -->
            <section class="section-card">
              <header class="section-header">
                <div>
                  <h2 class="section-title">课堂活动表现</h2>
                  <p class="section-subtitle">
                    对比各教学活动的提交率、表现水平与薄弱题目
                  </p>
                </div>
              </header>

              <div
                v-if="activitySummaries.length === 0"
                class="empty-block"
              >
                <div class="text-4xl mb-3">📝</div>
                <p class="text-gray-600 font-medium">尚未采集教学活动数据</p>
                <p class="text-gray-400 text-sm">
                  添加测验或作业等单元后，学生提交会自动汇总到这里。
                </p>
              </div>

              <div
                v-else
                class="grid gap-4 md:grid-cols-2 xl:grid-cols-3"
              >
                <div
                  v-for="summary in activitySummaries"
                  :key="summary.cellId"
                  class="border border-gray-200 rounded-xl bg-white p-4 shadow-sm hover:shadow transition-shadow"
                >
                  <div class="flex items-start justify-between mb-3">
                    <div>
                      <p class="text-xs uppercase text-gray-400 font-semibold">活动单元</p>
                      <h3 class="text-lg font-semibold text-gray-900">
                        {{ summary.title }}
                      </h3>
                    </div>
                    <span v-if="summary.stats?.gradedCount" class="text-xs text-blue-500 bg-blue-50 border border-blue-100 px-2 py-1 rounded-full">
                      已评分 {{ summary.stats.gradedCount }}
                    </span>
                  </div>

                  <div v-if="summary.stats" class="space-y-2 text-sm text-gray-600">
                    <div class="flex justify-between">
                      <span>提交率</span>
                      <span class="font-semibold text-gray-900">
                        {{ formatPercentage(activitySubmissionRate(summary.stats)) }}
                      </span>
                    </div>
                    <div class="flex justify-between">
                      <span>平均成绩</span>
                      <span class="font-semibold text-gray-900">
                        {{ summary.stats.averageScore !== null ? `${summary.stats.averageScore.toFixed(1)} 分` : '—' }}
                      </span>
                    </div>
                    <div class="flex justify-between">
                      <span>平均用时</span>
                      <span class="font-semibold text-gray-900">
                        {{ formatDuration(summary.stats.averageTimeSpent) }}
                      </span>
                    </div>
                    <div
                      v-if="summary.stats.itemStatistics && Object.keys(summary.stats.itemStatistics).length > 0"
                      class="pt-2 border-t border-dashed mt-2"
                    >
                      <p class="text-xs uppercase text-gray-400">重点关注题目</p>
                      <ul class="text-xs text-gray-600 mt-1 space-y-1">
                        <li
                          v-for="(item, key) in weakItems(summary.stats.itemStatistics)"
                          :key="key"
                        >
                          题目 {{ key }} · 正确率 {{ formatPercentage(item.accuracy) }}
                        </li>
                      </ul>
                    </div>
                  </div>

                  <div v-else class="text-sm text-gray-400">
                    暂无学生提交
                  </div>
                </div>
              </div>
            </section>

            <!-- 流程图统计 -->
            <section v-if="flowchartSummaries.length > 0" class="section-card">
              <header class="section-header">
                <div>
                  <h2 class="section-title">流程图表现</h2>
                  <p class="section-subtitle">
                    追踪学生流程构建的版本迭代、复杂度与活跃程度
                  </p>
                </div>
              </header>

              <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <div class="mini-card">
                  <p class="mini-card-label">累计快照</p>
                  <p class="mini-card-value">{{ flowchartAggregate.snapshotCount }}</p>
                  <p class="mini-card-subtle">涵盖所有流程图单元</p>
                </div>
                <div class="mini-card">
                  <p class="mini-card-label">最新更新时间</p>
                  <p class="mini-card-value">
                    {{ flowchartAggregate.latestUpdated ? formatRelativeTime(flowchartAggregate.latestUpdated) : '—' }}
                  </p>
                  <p class="mini-card-subtle">展示最近一次学生提交的时间</p>
                </div>
                <div class="mini-card">
                  <p class="mini-card-label">最高版本号</p>
                  <p class="mini-card-value">
                    {{ flowchartAggregate.maxVersion ?? '—' }}
                  </p>
                  <p class="mini-card-subtle">显示迭代次数</p>
                </div>
                <div class="mini-card">
                  <p class="mini-card-label">平均节点数</p>
                  <p class="mini-card-value">
                    {{ flowchartAggregate.avgNodeCount ?? '—' }}
                  </p>
                  <p class="mini-card-subtle">衡量流程图复杂度</p>
                </div>
              </div>
            </section>

            <!-- 问答概况 -->
            <section class="section-card">
              <header class="section-header">
                <div>
                  <h2 class="section-title">学生问答概况</h2>
                  <p class="section-subtitle">
                    汇总课堂提问与响应速度，保障互动闭环
                  </p>
                </div>
                <button
                  class="inline-flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700"
                  @click="loadQuestions()"
                >
                  刷新问答
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
              </header>

              <div class="grid gap-4 md:grid-cols-3">
                <div class="qa-card bg-yellow-50 text-yellow-700 border-yellow-200">
                  <p class="qa-card-label">待答问题</p>
                  <p class="qa-card-value">{{ stats?.pending ?? 0 }}</p>
                  <p class="qa-card-subtle">及时响应，维护课堂节奏</p>
                </div>
                <div class="qa-card bg-blue-50 text-blue-700 border-blue-200">
                  <p class="qa-card-label">已答数量</p>
                  <p class="qa-card-value">{{ stats?.answered ?? 0 }}</p>
                  <p class="qa-card-subtle">教师或 AI 已给出答复</p>
                </div>
                <div class="qa-card bg-green-50 text-green-700 border-green-200">
                  <p class="qa-card-label">学生已解决</p>
                  <p class="qa-card-value">{{ stats?.resolved ?? 0 }}</p>
                  <p class="qa-card-subtle">学生确认理解与掌握</p>
                </div>
              </div>

              <div class="mt-6">
                <div class="flex items-center justify-between mb-3">
                  <h3 class="text-sm font-semibold text-gray-700">最新问题</h3>
                  <div class="flex items-center gap-3">
                    <select
                      v-model="sortBy"
                      class="px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="created_at">最新提问</option>
                      <option value="upvotes">最多点赞</option>
                    </select>
                  </div>
                </div>

                <!-- 问答列表 -->
                <div v-if="loading" class="flex items-center justify-center py-8 text-gray-500">
                  <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-3"></div>
                  加载问答中...
                </div>

                <div
                  v-else-if="questions.length === 0"
                  class="empty-block py-12"
                >
                  <div class="text-4xl mb-3">💭</div>
                  <p class="text-gray-600 font-medium">{{ emptyMessage }}</p>
                  <p class="text-gray-400 text-sm">{{ emptyHint }}</p>
                </div>

                <div v-else class="space-y-3">
                  <div
                    v-for="question in questions"
                    :key="question.id"
                    class="bg-white border border-gray-200 rounded-lg px-4 py-3 hover:border-blue-200 hover:shadow-sm transition-colors"
                  >
                    <div class="flex items-start justify-between">
                      <div class="flex-1 pr-4">
                        <div class="flex items-center gap-2 text-xs text-gray-500 mb-1">
                          <span>{{ question.lesson.title }}</span>
                          <span v-if="question.cell">单元 {{ question.cell.order + 1 }}</span>
                          <span>{{ formatRelativeTime(question.created_at) }}</span>
                        </div>
                        <h4
                          class="text-sm font-semibold text-gray-900 hover:text-blue-600 cursor-pointer"
                          @click="viewQuestion(question.id)"
                        >
                          {{ question.title }}
                        </h4>
                        <p class="text-xs text-gray-500 mt-1 line-clamp-2">
                          {{ question.content }}
                        </p>
                      </div>
                      <div class="flex flex-col items-end gap-2">
                        <div class="flex items-center gap-3 text-xs text-gray-500">
                          <span>👍 {{ question.upvotes }}</span>
                          <span>💬 {{ question.answer_count }}</span>
                        </div>
                        <div class="flex items-center gap-2">
                          <button
                            @click="viewQuestion(question.id)"
                            class="px-3 py-1 text-xs border border-gray-300 text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
                          >
                            查看
                          </button>
                          <button
                            v-if="!question.has_teacher_answer"
                            @click="answerQuestion(question.id)"
                            class="px-3 py-1 text-xs bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                          >
                            回答
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div v-if="pagination.has_more" class="text-center pt-3">
                    <button
                      @click="loadMore"
                      :disabled="loading"
                      class="px-4 py-2 text-sm border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors disabled:opacity-50"
                    >
                      加载更多
                    </button>
                  </div>
                </div>
              </div>
            </section>
          </template>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import activityService from '@/services/activity'
import { lessonService } from '@/services/lesson'
import questionService from '@/services/question'
import type { Lesson } from '@/types/lesson'
import type {
  ActivityStatistics,
  FormativeAssessmentRecord,
  ActivityItemStatistic,
} from '@/types/activity'
import type { QuestionListItem, QuestionStats } from '@/types/question'
import type { Cell } from '@/types/cell'

interface ActivitySummary {
  cellId: number
  title: string
  stats: ActivityStatistics | null
}

const router = useRouter()

const lessons = ref<Lesson[]>([])
const lessonLoading = ref(true)
const selectedLessonId = ref<number | ''>('')
const selectedLesson = ref<Lesson | null>(null)

const overviewLoading = ref(false)
const activitySummaries = ref<ActivitySummary[]>([])
const formativeRecords = ref<FormativeAssessmentRecord[]>([])
const qaStats = ref<QuestionStats | null>(null)

const questions = ref<QuestionListItem[]>([])
const loading = ref(false)
const pagination = ref({
  page: 1,
  page_size: 10,
  total: 0,
  has_more: false,
})
const sortBy = ref<'created_at' | 'upvotes'>('created_at')

const stats = qaStats
const currentTab = ref<'pending' | 'all'>('pending')
const emptyMessage = computed(() =>
  currentTab.value === 'pending' ? '暂无待回答的问题' : '暂无问题'
)
const emptyHint = computed(() =>
  currentTab.value === 'pending' ? '太棒了！所有问题都已回答' : '学生提问后会显示在这里'
)

const loadLessons = async () => {
  try {
    lessonLoading.value = true
    const response = await lessonService.fetchLessons({
      page_size: 50,
      status: 'published',
    })
    lessons.value = response.items
    if (!selectedLessonId.value && lessons.value.length > 0) {
      selectedLessonId.value = lessons.value[0].id
    }
  } catch (error) {
    console.error('Failed to load lessons:', error)
  } finally {
    lessonLoading.value = false
  }
}

const loadOverview = async (lessonId: number) => {
  overviewLoading.value = true
  activitySummaries.value = []
  formativeRecords.value = []

  try {
    const lesson = await lessonService.fetchLessonById(lessonId)
    selectedLesson.value = lesson

    const cells = (lesson.content || []).filter((cell: Cell) =>
      ['activity', 'flowchart'].includes(cell.type)
    )

    const statsResults = await Promise.all(
      cells.map(async (cell) => {
        const cellId =
          typeof cell.id === 'string' ? Number(cell.id) : (cell.id as number)
        if (Number.isNaN(cellId)) {
          return null
        }
        try {
          const stats = await activityService.getStatistics(cellId)
          return {
            cellId,
            title: cell.title || `单元 ${cell.order + 1}`,
            stats,
          } as ActivitySummary
        } catch (error) {
          console.warn('Failed to load activity statistics:', error)
          return {
            cellId,
            title: cell.title || `单元 ${cell.order + 1}`,
            stats: null,
          }
        }
      })
    )

    activitySummaries.value = statsResults.filter(
      (item): item is ActivitySummary => item !== null
    )

    try {
      formativeRecords.value = await activityService.getFormativeAssessments(lessonId)
    } catch (error) {
      console.warn('Failed to load formative assessments:', error)
    }

    await loadQuestionSummary(lessonId)
  } finally {
    overviewLoading.value = false
  }
}

const loadQuestionSummary = async (lessonId: number) => {
  try {
    qaStats.value = await questionService.getQuestionStats(lessonId)
  } catch (error) {
    console.warn('Failed to load question stats:', error)
    qaStats.value = null
  }
  await loadQuestions(false, lessonId)
}

const loadQuestions = async (append = false, lessonId?: number) => {
  if (!selectedLessonId.value) return

  try {
    loading.value = true
    if (!append) {
      pagination.value.page = 1
    }

    const response = await questionService.getTeacherPendingQuestions({
      lesson_id: lessonId ?? (selectedLessonId.value as number),
      sort: sortBy.value,
      page: pagination.value.page,
      page_size: pagination.value.page_size,
    })

    if (append) {
      questions.value = [...questions.value, ...response.items]
    } else {
      questions.value = response.items
    }

    pagination.value.total = response.total
    pagination.value.has_more = response.has_more
  } catch (error) {
    console.error('Failed to load questions:', error)
    if (!append) {
      questions.value = []
    }
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  pagination.value.page++
  loadQuestions(true)
}

const handleRefresh = () => {
  if (selectedLessonId.value) {
    loadOverview(selectedLessonId.value as number)
  }
}

const viewQuestion = (id: number) => {
  router.push(`/teacher/questions/${id}`)
}

const answerQuestion = (id: number) => {
  router.push(`/teacher/questions/${id}/answer`)
}

const riskLevelLabel = (level?: string | null) => {
  if (level === 'high') return '高风险'
  if (level === 'medium') return '中风险'
  return '低风险'
}

const formatPercentage = (value: number | null | undefined) => {
  if (value === null || value === undefined) return '—'
  return `${Math.round(value * 100)}%`
}

const formatDuration = (seconds?: number | null) => {
  if (!seconds || seconds <= 0) return '—'
  if (seconds < 60) return `${Math.round(seconds)} 秒`
  const minutes = Math.floor(seconds / 60)
  const remain = seconds % 60
  if (minutes >= 60) {
    const hours = Math.floor(minutes / 60)
    const restMinutes = minutes % 60
    return `${hours} 小时 ${restMinutes} 分`
  }
  return `${minutes} 分 ${Math.round(remain)} 秒`
}

const formatRelativeTime = (dateStr?: string | null) => {
  if (!dateStr) return '—'
  const target = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - target.getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes} 分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} 小时前`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days} 天前`
  return target.toLocaleDateString('zh-CN')
}

const activitySubmissionRate = (stats: ActivityStatistics) => {
  const total = stats.totalStudents || 0
  if (total === 0) return 0
  const completed = (stats.submittedCount || 0) + (stats.gradedCount || 0)
  return completed / total
}

const weakItems = (itemStats: Record<string, ActivityItemStatistic>) => {
  return Object.entries(itemStats)
    .map(([key, value]) => ({
      key,
      accuracy: value.accuracy ?? value.correctCount / Math.max(value.attempts || 1, 1),
    }))
    .sort((a, b) => a.accuracy - b.accuracy)
    .slice(0, 3)
}

const overviewMetrics = computed(() => {
  const statsList = activitySummaries.value
    .map((summary) => summary.stats)
    .filter((stats): stats is ActivityStatistics => Boolean(stats))

  if (statsList.length === 0) {
    return {
      totalStudents: 0,
      submittedStudentCount: 0,
      submissionRate: 0,
      averageScore: null as number | null,
    }
  }

  const totalStudents = Math.max(...statsList.map((stats) => stats.totalStudents || 0))
  const submittedStudentCount = Math.max(
    ...statsList.map(
      (stats) => (stats.submittedCount || 0) + (stats.gradedCount || 0)
    )
  )
  const submissionRate =
    totalStudents > 0 ? submittedStudentCount / totalStudents : 0

  const scores = statsList
    .map((stats) => stats.averageScore)
    .filter((score): score is number => score !== null && score !== undefined)

  const averageScore =
    scores.length > 0
      ? scores.reduce((sum, score) => sum + score, 0) / scores.length
      : null

  return {
    totalStudents,
    submittedStudentCount,
    submissionRate,
    averageScore,
  }
})

const riskCounts = computed(() => {
  const high = formativeRecords.value.filter(
    (record) => record.riskLevel === 'high'
  ).length
  const medium = formativeRecords.value.filter(
    (record) => record.riskLevel === 'medium'
  ).length
  return {
    high,
    medium,
    total: high + medium,
  }
})

const riskStudents = computed(() => {
  const priority = { high: 0, medium: 1, low: 2 }
  return formativeRecords.value
    .filter((record) => record.riskLevel && record.riskLevel !== 'low')
    .sort(
      (a, b) =>
        (priority[a.riskLevel as keyof typeof priority] ?? 2) -
        (priority[b.riskLevel as keyof typeof priority] ?? 2)
    )
    .slice(0, 6)
})

const flowchartSummaries = computed(() =>
  activitySummaries.value.filter(
    (summary) => summary.stats && summary.stats.flowchartMetrics
  )
)

const flowchartAggregate = computed(() => {
  if (flowchartSummaries.value.length === 0) {
    return {
      snapshotCount: 0,
      latestUpdated: null as string | null,
      maxVersion: null as number | null,
      avgNodeCount: null as number | null,
    }
  }

  const metricsList = flowchartSummaries.value
    .map((summary) => summary.stats?.flowchartMetrics)
    .filter((metrics): metrics is Record<string, any> => Boolean(metrics))

  const snapshotCount = metricsList.reduce(
    (sum, metrics) => sum + (metrics.snapshot_count || metrics.snapshotCount || 0),
    0
  )

  const latestUpdatedRaw = metricsList
    .map((metrics) => metrics.latest_updated_at || metrics.latestUpdatedAt)
    .filter(Boolean) as string[]

  const latestUpdated =
    latestUpdatedRaw.length > 0
      ? latestUpdatedRaw.sort((a, b) => (a > b ? -1 : 1))[0]
      : null

  const maxVersionRaw = metricsList
    .map((metrics) => metrics.max_version ?? metrics.maxVersion)
    .filter((value): value is number => value !== null && value !== undefined)

  const nodeCounts = Object.values(metricsList).flatMap((metrics) => {
    const value =
      metrics.avg_node_count ??
      metrics.avgNodeCount ??
      metrics.average_node_count ??
      metrics.nodeCount
    return value !== undefined && value !== null ? [Number(value)] : []
  })

  return {
    snapshotCount,
    latestUpdated,
    maxVersion: maxVersionRaw.length > 0 ? Math.max(...maxVersionRaw) : null,
    avgNodeCount:
      nodeCounts.length > 0
        ? Number(
            (
              nodeCounts.reduce((sum, count) => sum + count, 0) /
              nodeCounts.length
            ).toFixed(1)
          )
        : null,
  }
})

watch(
  () => selectedLessonId.value,
  (lessonId) => {
    if (lessonId) {
      loadOverview(lessonId as number)
    } else {
      selectedLesson.value = null
      activitySummaries.value = []
      formativeRecords.value = []
      questions.value = []
      qaStats.value = null
    }
  }
)

watch(sortBy, () => {
  loadQuestions()
})

onMounted(async () => {
  await loadLessons()
  if (selectedLessonId.value) {
    await loadOverview(selectedLessonId.value as number)
  }
})
</script>

<style scoped>
.overview-card {
  @apply bg-white border border-gray-200 rounded-xl shadow-sm p-5 flex flex-col gap-1;
}
.overview-label {
  @apply text-xs uppercase font-semibold text-gray-400 tracking-wide;
}
.overview-value {
  @apply text-3xl font-bold text-gray-900;
}
.overview-subtle {
  @apply text-xs text-gray-500;
}
.section-card {
  @apply bg-white border border-gray-200 rounded-xl shadow-sm p-6 space-y-5;
}
.section-header {
  @apply flex items-start justify-between gap-3 flex-wrap;
}
.section-title {
  @apply text-lg font-semibold text-gray-900;
}
.section-subtitle {
  @apply text-sm text-gray-500;
}
.empty-block {
  @apply border border-dashed border-gray-200 rounded-xl p-8 text-center text-gray-500;
}
.mini-card {
  @apply bg-gray-50 border border-gray-200 rounded-xl p-4;
}
.mini-card-label {
  @apply text-xs uppercase text-gray-400 font-semibold;
}
.mini-card-value {
  @apply text-xl font-bold text-gray-900 mt-1;
}
.mini-card-subtle {
  @apply text-xs text-gray-500;
}
.qa-card {
  @apply border rounded-xl p-4 shadow-sm;
}
.qa-card-label {
  @apply text-xs uppercase font-semibold;
}
.qa-card-value {
  @apply text-2xl font-bold;
}
.qa-card-subtle {
  @apply text-xs;
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>


