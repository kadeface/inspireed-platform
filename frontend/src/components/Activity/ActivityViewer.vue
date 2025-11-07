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
            >
              <input
                v-model="answers[item.id]"
                type="radio"
                :value="option.id"
                :name="`item-${item.id}`"
                @change="saveAnswer(item.id)"
              />
              <span>{{ option.text }}</span>
            </label>
          </div>

          <!-- 多选题 -->
          <div v-if="item.type === 'multiple-choice'" class="space-y-2">
            <label
              v-for="option in item.config.options"
              :key="option.id"
              class="option-label"
            >
              <input
                v-model="answers[item.id]"
                type="checkbox"
                :value="option.id"
                @change="saveAnswer(item.id)"
              />
              <span>{{ option.text }}</span>
            </label>
          </div>

          <!-- 判断题 -->
          <div v-if="item.type === 'true-false'" class="space-y-2">
            <label class="option-label">
              <input
                v-model="answers[item.id]"
                type="radio"
                :value="true"
                :name="`item-${item.id}`"
                @change="saveAnswer(item.id)"
              />
              <span>正确</span>
            </label>
            <label class="option-label">
              <input
                v-model="answers[item.id]"
                type="radio"
                :value="false"
                :name="`item-${item.id}`"
                @change="saveAnswer(item.id)"
              />
              <span>错误</span>
            </label>
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
      <button @click="handleSaveDraft" class="btn-secondary" :disabled="submitting">
        💾 保存草稿
      </button>
      <button @click="handleSubmit" class="btn-primary" :disabled="!canSubmit || submitting">
        {{ submitting ? '提交中...' : '✅ 提交答案' }}
      </button>
    </div>

    <!-- 提示信息 -->
    <div v-if="!canSubmit" class="alert-warning">
      ⚠️ 请完成所有必答题后再提交
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import type { ActivityCell } from '../../types/cell'
import type { ActivityItemType } from '../../types/activity'
import activityService from '../../services/activity'
import { useOfflineActivity } from '../../composables/useOfflineActivity'

interface Props {
  cell: ActivityCell
}

const props = defineProps<Props>()

const emit = defineEmits<{
  submit: [data: any]
}>()

// 状态
const answers = ref<Record<string, any>>({})
const submitting = ref(false)
const startTime = ref(new Date())
const submissionId = ref<number | null>(null)
const currentStudentId = ref(1) // TODO: 从用户 store 获取真实 ID

// 离线支持
const {
  isOnline,
  isSyncing,
  lastSyncTime,
  hasUnsyncedChanges,
  loadFromIndexedDB,
  syncToServer,
  setupAutoSave,
} = useOfflineActivity(
  typeof props.cell.id === 'number' ? props.cell.id : parseInt(props.cell.id as string),
  props.cell.content.title ? 1 : 1, // TODO: 从 context 获取真实 lessonId
  currentStudentId.value
)

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

  if (!confirm('确定要提交吗？提交后将无法修改。')) {
    return
  }

  try {
    submitting.value = true
    
    const timeSpent = Math.floor((new Date().getTime() - startTime.value.getTime()) / 1000)

    if (submissionId.value) {
      // 如果已有提交ID，调用正式提交API
      await activityService.submitActivity(submissionId.value, {
        responses: answers.value,
        timeSpent,
      })
    } else {
      // 先创建提交再提交
      const submission = await activityService.createSubmission({
        cellId: typeof props.cell.id === 'number' ? props.cell.id : parseInt(props.cell.id as string),
        lessonId: 1, // TODO: 获取真实 lessonId
        responses: answers.value,
        startedAt: startTime.value.toISOString(),
      })
      submissionId.value = submission.id
      
      // 正式提交
      await activityService.submitActivity(submission.id, {
        responses: answers.value,
        timeSpent,
      })
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
  
  // 1. 尝试从 IndexedDB 加载离线数据
  const offlineData = await loadFromIndexedDB()
  if (offlineData) {
    answers.value = offlineData
    console.log('✅ Loaded from offline storage')
  }
  
  // 2. 如果在线，尝试从服务器加载最新数据
  if (isOnline.value) {
    try {
      const cellId = typeof props.cell.id === 'number' ? props.cell.id : parseInt(props.cell.id as string)
      const submission = await activityService.getMyCellSubmission(cellId)
      
      if (submission) {
        submissionId.value = submission.id
        answers.value = submission.responses || {}
        console.log('✅ Loaded from server')
      }
    } catch (error) {
      console.log('📱 Using offline data')
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

