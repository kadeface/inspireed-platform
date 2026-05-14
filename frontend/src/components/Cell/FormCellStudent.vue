<template>
  <div class="form-cell-student">
    <!-- 等待开始 -->
    <div v-if="!isActive && !hasSubmitted" class="waiting-state">
      <svg class="waiting-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <h3 class="text-lg font-semibold text-gray-900 mt-4">等待教师开始投票...</h3>
      <p class="text-gray-500 mt-2">投票开始后即可参与</p>
    </div>

    <!-- 投票界面 -->
    <div v-else-if="isActive && !hasSubmitted" class="voting-interface">
      <div class="voting-header">
        <h3 class="text-xl font-bold text-gray-900">{{ cell.title }}</h3>
        <p v-if="cell.description" class="text-gray-600 mt-2">{{ cell.description }}</p>

        <div class="voting-info">
          <span class="info-badge">
            {{ voteTypeLabel }}
          </span>
          <span v-if="timeLimit" class="info-badge info-badge-warning">
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ timeDisplay }}
          </span>
        </div>
      </div>

      <!-- 单选 -->
      <div v-if="cellType === 'single_choice'" class="options-container single-choice">
        <button
          v-for="(option, index) in cell.options"
          :key="option.id || index"
          @click="selectSingleOption(option.id || `opt_${index}`)"
          :class="['option-btn', { selected: selectedAnswers.length === 1 && selectedAnswers[0].option_id === (option.id || `opt_${index}`) }]"
        >
          <div class="option-marker">
            <div v-if="selectedAnswers.length === 1 && selectedAnswers[0].option_id === (option.id || `opt_${index}`)" class="marker-inner"></div>
          </div>
          <div class="option-content">
            <div v-if="option.image_url" class="option-image">
              <img :src="option.image_url" :alt="option.text" />
            </div>
            <span class="option-text">{{ option.text }}</span>
          </div>
        </button>
      </div>

      <!-- 多选 -->
      <div v-else-if="cellType === 'multiple_choice'" class="options-container multiple-choice">
        <button
          v-for="(option, index) in cell.options"
          :key="option.id || index"
          @click="toggleMultipleOption(option.id || `opt_${index}`)"
          :class="['option-btn', { selected: isOptionSelected(option.id || `opt_${index}`) }]"
        >
          <div class="option-marker checkbox">
            <svg v-if="isOptionSelected(option.id || `opt_${index}`)" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div class="option-content">
            <div v-if="option.image_url" class="option-image">
              <img :src="option.image_url" :alt="option.text" />
            </div>
            <span class="option-text">{{ option.text }}</span>
          </div>
        </button>
      </div>

      <!-- 排序 -->
      <div v-else-if="cellType === 'ranking'" class="options-container ranking">
        <draggable
          v-model="rankingOptions"
          :disabled="!isActive"
          item-key="id"
          class="ranking-list"
        >
          <template #item="{ element: option, index }">
            <div class="ranking-item">
              <div class="ranking-number">{{ index + 1 }}</div>
              <div class="ranking-content">
                <div v-if="option.image_url" class="option-image">
                  <img :src="option.image_url" :alt="option.text" />
                </div>
                <span class="option-text">{{ option.text }}</span>
              </div>
              <div class="ranking-drag">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                </svg>
              </div>
            </div>
          </template>
        </draggable>
      </div>

      <!-- 提交按钮 -->
      <div class="submit-section">
        <button
          @click="handleSubmit"
          :disabled="!canSubmit"
          class="btn-submit"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          提交答案
        </button>
        <p class="text-sm text-gray-500 mt-2">
          {{ submitHint }}
        </p>
      </div>
    </div>

    <!-- 已提交 -->
    <div v-else-if="hasSubmitted" class="submitted-state">
      <svg class="success-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <h3 class="text-xl font-bold text-gray-900 mt-4">提交成功！</h3>
      <p class="text-gray-500 mt-2">感谢您的参与</p>
    </div>

    <!-- 投票已结束 -->
    <div v-else class="ended-state">
      <svg class="ended-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <h3 class="text-lg font-semibold text-gray-900 mt-4">投票已结束</h3>
      <p class="text-gray-500 mt-2">教师已停止本次投票</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import draggable from 'vuedraggable'
import type { Cell } from '../../types/cell'
import type { Answer } from '../../types/form'

interface Props {
  cell: Cell
  isActive: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'submit', answers: Answer[]): void
}>()

// 状态
const selectedAnswers = ref<Answer[]>([])
const rankingOptions = ref([...props.cell.options].map((opt, index) => ({
  ...opt,
  id: opt.id || `opt_${index}`,
  order: index,
})))
const hasSubmitted = ref(false)
const timeLeft = ref(props.cell.content?.time_limit || 0)
let timer: ReturnType<typeof setInterval> | null = null

// 计算属性
const cellType = computed(() => props.cell.content?.cell_type || 'single_choice')
const voteTypeLabel = computed(() => {
  const labels = {
    single_choice: '单选题',
    multiple_choice: '多选题',
    ranking: '排序题',
  }
  return labels[cellType.value as keyof typeof labels] || '投票'
})

const timeLimit = computed(() => props.cell.content?.time_limit)
const timeDisplay = computed(() => {
  if (!timeLeft.value) return ''
  const minutes = Math.floor(timeLeft.value / 60)
  const seconds = timeLeft.value % 60
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
})

const canSubmit = computed(() => {
  if (cellType.value === 'single_choice') {
    return selectedAnswers.value.length === 1
  } else if (cellType.value === 'multiple_choice') {
    return selectedAnswers.value.length >= 1
  } else if (cellType.value === 'ranking') {
    return rankingOptions.value.length === props.cell.options.length
  }
  return false
})

const submitHint = computed(() => {
  if (cellType.value === 'single_choice') {
    return '选择一个选项后提交'
  } else if (cellType.value === 'multiple_choice') {
    return `已选择 ${selectedAnswers.value.length} 项，至少选择1项`
  } else if (cellType.value === 'ranking') {
    return '拖动选项调整顺序，提交后无法修改'
  }
  return ''
})

// 方法
function selectSingleOption(optionId: string) {
  selectedAnswers.value = [{ option_id: optionId }]
}

function toggleMultipleOption(optionId: string) {
  const index = selectedAnswers.value.findIndex(a => a.option_id === optionId)
  if (index >= 0) {
    selectedAnswers.value.splice(index, 1)
  } else {
    selectedAnswers.value.push({ option_id: optionId })
  }
}

function isOptionSelected(optionId: string): boolean {
  return selectedAnswers.value.some(a => a.option_id === optionId)
}

function handleSubmit() {
  if (!canSubmit.value) return

  let answers: Answer[]

  if (cellType.value === 'ranking') {
    answers = rankingOptions.value.map((opt, index) => ({
      option_id: opt.id || '',
      order: index,
    }))
  } else {
    answers = selectedAnswers.value
  }

  emit('submit', answers)
  hasSubmitted.value = true

  // 停止计时器
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

// 生命周期
onMounted(() => {
  // 启动计时器
  if (timeLimit.value && timeLimit.value > 0) {
    timer = setInterval(() => {
      if (timeLeft.value > 0) {
        timeLeft.value--
      } else {
        // 时间到，自动提交
        handleSubmit()
      }
    }, 1000)
  }
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
})
</script>

<style scoped>
.form-cell-student {
  @apply min-h-[400px];
}

/* 等待状态 */
.waiting-state {
  @apply flex flex-col items-center justify-center h-96 text-center;
}

.waiting-icon {
  @apply w-16 h-16 text-gray-300;
}

/* 投票界面 */
.voting-interface {
  @apply space-y-6;
}

.voting-header {
  @apply space-y-3;
}

.voting-info {
  @apply flex gap-2;
}

.info-badge {
  @apply inline-flex items-center px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-medium;
}

.info-badge-warning {
  @apply bg-orange-50 text-orange-700;
}

/* 选项容器 */
.options-container {
  @apply space-y-3;
}

.option-btn {
  @apply w-full flex items-start gap-3 p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all;
}

.option-btn.selected {
  @apply border-blue-500 bg-blue-50;
}

.option-marker {
  @apply w-5 h-5 flex-shrink-0 border-2 border-gray-300 rounded-full flex items-center justify-center mt-0.5;
}

.option-btn.selected .option-marker {
  @apply border-blue-500;
}

.marker-inner {
  @apply w-3 h-3 bg-blue-500 rounded-full;
}

.option-marker.checkbox {
  @apply rounded;
}

.option-content {
  @apply flex-1 space-y-2;
}

.option-image img {
  @apply w-full h-32 object-cover rounded-md;
}

.option-text {
  @apply text-gray-900;
}

/* 排序题 */
.ranking-list {
  @apply space-y-2;
}

.ranking-item {
  @apply flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-lg;
}

.ranking-number {
  @apply w-8 h-8 flex items-center justify-center bg-blue-500 text-white font-bold rounded-full;
}

.ranking-content {
  @apply flex-1 space-y-2;
}

.ranking-drag {
  @apply cursor-move;
}

/* 提交区域 */
.submit-section {
  @apply text-center;
}

.btn-submit {
  @apply inline-flex items-center px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

/* 已提交状态 */
.submitted-state {
  @apply flex flex-col items-center justify-center h-96 text-center;
}

.success-icon {
  @apply w-16 h-16 text-green-500;
}

/* 已结束状态 */
.ended-state {
  @apply flex flex-col items-center justify-center h-96 text-center;
}

.ended-icon {
  @apply w-16 h-16 text-gray-300;
}
</style>
