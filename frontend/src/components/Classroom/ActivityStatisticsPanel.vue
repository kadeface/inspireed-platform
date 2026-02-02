<template>
  <div v-if="showPanel" class="activity-statistics-panel" data-testid="activity-statistics">
    <!-- 统计信息头部 -->
    <div class="activity-stats-header">
      <h4 class="activity-stats-title">活动统计</h4>
      <div v-if="!loading" class="activity-stats-submission" data-testid="submission-info">
        提交: <span data-testid="submitted-count">{{ submittedCount }}</span>/<span data-testid="total-students">{{ totalStudents }}</span>
        <span class="ml-2 text-xs text-gray-500" data-testid="submission-rate">
          ({{ submissionRate }}%)
        </span>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="activity-stats-loading">
      <svg class="loading-spinner" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <span>加载统计数据中...</span>
    </div>

    <!-- 空状态 -->
    <div v-else-if="choiceItems.length === 0" class="activity-stats-empty">
      <p>暂无统计数据</p>
    </div>

    <!-- 选择题统计列表 -->
    <div v-else class="activity-choice-stats">
      <div
        v-for="item in choiceItems"
        :key="item.itemId"
        class="activity-choice-item"
      >
        <!-- 题目头部 -->
        <div class="activity-choice-header">
          <span class="activity-choice-order">{{ item.order + 1 }}. {{ item.question }}</span>
          <span class="activity-choice-type">{{ getItemTypeLabel(item.type) }}</span>
        </div>

        <!-- 选项列表 -->
        <div class="activity-choice-options">
          <div
            v-for="option in item.options"
            :key="option.id"
            class="activity-option-item"
            :class="{ 'is-correct': option.isCorrect }"
          >
            <span class="activity-option-label">{{ option.label }}</span>
            <span class="activity-option-percentage">{{ option.percentage }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface ChoiceOption {
  id: string
  label: string
  isCorrect?: boolean
  count: number
  percentage: number
}

interface ChoiceItem {
  itemId: string
  order: number
  type: string
  question: string
  options: ChoiceOption[]
}

interface ActivityStatistics {
  totalStudents: number
  submittedCount: number
  itemStatistics: Record<string, any> | null
}

interface Props {
  currentCell?: any
  activityStatistics?: ActivityStatistics | null
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  currentCell: null,
  activityStatistics: null,
  loading: false,
})

// 计算属性：是否显示面板
const showPanel = computed(() => {
  return props.currentCell?.type === 'activity'
})

// 计算属性：选择题及其统计
const choiceItems = computed((): ChoiceItem[] => {
  try {
    if (!props.currentCell || props.currentCell.type !== 'activity' ||
        !props.currentCell.content?.items || !props.activityStatistics?.itemStatistics) {
      return []
    }

    const choiceTypes = ['single-choice', 'multiple-choice', 'true-false']
    const items = props.currentCell.content.items.filter((item: any) =>
      item && choiceTypes.includes(item.type)
    )

    if (items.length === 0) {
      return []
    }

    return items.map((item: any, index: number) => {
      const itemId = item.id
      const itemStats = props.activityStatistics?.itemStatistics?.[itemId]
      const optionDistribution = itemStats?.option_distribution || itemStats?.options || {}

      let options: ChoiceOption[] = []

      try {
        if (item.type === 'single-choice' && 'config' in item && item.config &&
            Array.isArray(item.config.options)) {
          const totalResponses = (Object.values(optionDistribution).reduce(
            (sum: number, count: any) => sum + (Number(count) || 0), 0
          ) as number) || props.activityStatistics.submittedCount || 1

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
        } else if (item.type === 'multiple-choice' && 'config' in item && item.config &&
                   Array.isArray(item.config.options)) {
          const totalResponses = props.activityStatistics.submittedCount || 1

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
          const totalResponses = (Object.values(optionDistribution).reduce(
            (sum: number, count: any) => sum + (Number(count) || 0), 0
          ) as number) || props.activityStatistics.submittedCount || 1

          const config = 'config' in item ? item.config : null
          options = [
            {
              id: 'true',
              label: '正确',
              isCorrect: config && 'correctAnswer' in config ? config.correctAnswer === true : false,
              count: Number(optionDistribution.true || optionDistribution['true'] || 0),
              percentage: totalResponses > 0 ?
                Math.round((Number(optionDistribution.true || optionDistribution['true'] || 0) / totalResponses) * 100) : 0,
            },
            {
              id: 'false',
              label: '错误',
              isCorrect: config && 'correctAnswer' in config ? config.correctAnswer === false : false,
              count: Number(optionDistribution.false || optionDistribution['false'] || 0),
              percentage: totalResponses > 0 ?
                Math.round((Number(optionDistribution.false || optionDistribution['false'] || 0) / totalResponses) * 100) : 0,
            },
          ]
        }
      } catch (error) {
        console.error('处理选择题选项时出错:', error, item)
        options = []
      }

      return {
        itemId,
        order: index,
        type: item.type,
        question: item.question || `题目 ${index + 1}`,
        options,
      }
    }).filter((item: ChoiceItem) => item && item.options && item.options.length > 0)
  } catch (error) {
    console.error('计算选择题统计时出错:', error)
    return []
  }
})

// 计算属性：总学生数
const totalStudents = computed(() => {
  return props.activityStatistics?.totalStudents || 0
})

// 计算属性：提交数
const submittedCount = computed(() => {
  return props.activityStatistics?.submittedCount || 0
})

// 计算属性：提交率
const submissionRate = computed(() => {
  if (totalStudents.value === 0) return 0
  return Math.round((submittedCount.value / totalStudents.value) * 100)
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
</script>

<style scoped>
/* 活动统计面板 */
.activity-statistics-panel {
  background: white;
  border-radius: 0.5rem;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

/* 统计信息头部 */
.activity-stats-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.activity-stats-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.activity-stats-submission {
  font-size: 0.875rem;
  color: #2563eb;
  font-weight: 500;
}

.ml-2 {
  margin-left: 0.5rem;
}

.text-xs {
  font-size: 0.75rem;
}

.text-gray-500 {
  color: #6b7280;
}

/* 加载状态 */
.activity-stats-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem 0;
  color: #6b7280;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.loading-spinner {
  width: 1.25rem;
  height: 1.25rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 空状态 */
.activity-stats-empty {
  text-align: center;
  padding: 1.25rem 0;
  font-size: 0.875rem;
  color: #6b7280;
}

.activity-stats-empty p {
  margin: 0;
}

/* 选择题统计列表 */
.activity-choice-stats {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.activity-choice-item {
  background: #f9fafb;
  border-radius: 0.5rem;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
}

/* 题目头部 */
.activity-choice-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.activity-choice-order {
  font-size: 0.75rem;
  font-weight: 500;
  color: #374151;
  flex: 1;
}

.activity-choice-type {
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 9999px;
  font-weight: 500;
  flex-shrink: 0;
}

/* 选项列表 */
.activity-choice-options {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.activity-option-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem;
  background: white;
  border-radius: 0.25rem;
  border: 1px solid #e5e7eb;
}

.activity-option-item.is-correct {
  border-color: #86efac;
  background: #f0fdf4;
}

.activity-option-label {
  font-size: 0.75rem;
  color: #374151;
}

.activity-option-percentage {
  font-size: 0.75rem;
  font-weight: 600;
  color: #2563eb;
}

.activity-option-item.is-correct .activity-option-percentage {
  color: #16a34a;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .activity-stats-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .activity-choice-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>
