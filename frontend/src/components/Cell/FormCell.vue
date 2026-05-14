<template>
  <div class="form-cell cell-container" ref="containerRef">
    <!-- 教师模式 -->
    <FormCellEditor
      v-if="isTeacher && editable"
      :cell="cell"
      @save="handleSave"
      @start="handleStart"
      @stop="handleStop"
    />

    <!-- 学生模式 -->
    <FormCellStudent
      v-else-if="!isTeacher"
      :cell="cell"
      :is-active="isFormActive"
      @submit="handleSubmit"
    />

    <!-- 结果展示 -->
    <FormCellResults
      v-if="showResults && (isTeacher || (cell.settings?.show_results && !isTeacher))"
      :cell="cell"
      :is-teacher="isTeacher"
    />

    <!-- 连接状态指示器 -->
    <div v-if="showConnectionStatus" class="connection-status">
      <span :class="['status-dot', { connected: isConnected, disconnected: !isConnected }]"></span>
      <span class="status-text">{{ connectionStatusText }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useFormStore } from '../../store/form'
import { useAuthStore } from '../../store/auth'
import type { Cell } from '../../types/cell'
import type { FormCellCreate, FormCellUpdate, Answer } from '../../types/form'
import FormCellEditor from './FormCellEditor.vue'
import FormCellStudent from './FormCellStudent.vue'
import FormCellResults from './FormCellResults.vue'

interface Props {
  cell: Cell
  editable?: boolean
  showResults?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: true,
  showResults: false,
})

const emit = defineEmits<{
  (e: 'save', data: FormCellCreate | FormCellUpdate): void
  (e: 'delete'): void
}>()

// Stores
const formStore = useFormStore()
const authStore = useAuthStore()

// 状态
const isTeacher = computed(() => authStore.user?.role === 'teacher')
const isFormActive = computed(() => formStore.isFormActive)
const isConnected = computed(() => formStore.isConnected)
const showConnectionStatus = computed(() => !isTeacher.value && isFormActive.value)
const connectionStatusText = computed(() =>
  isConnected.value ? '实时连接中' : '连接断开，重连中...'
)

// 生命周期
onMounted(async () => {
  try {
    // 获取表单数据
    await formStore.fetchForm(props.cell.id)

    // 连接WebSocket
    formStore.connectWebSocket(props.cell.id)
  } catch (error) {
    console.error('初始化表单失败:', error)
  }
})

onUnmounted(() => {
  // 断开WebSocket连接
  formStore.disconnectWebSocket()
})

// 监听cell变化
watch(
  () => props.cell.id,
  (newId) => {
    if (newId) {
      formStore.reset()
      formStore.fetchForm(newId)
      formStore.connectWebSocket(newId)
    }
  }
)

// 事件处理
async function handleSave(data: FormCellCreate | FormCellUpdate) {
  try {
    await formStore.updateForm(props.cell.id, data)
    emit('save', data)
  } catch (error) {
    console.error('保存表单失败:', error)
    throw error
  }
}

function handleStart() {
  formStore.startForm()
}

function handleStop() {
  formStore.stopForm()
}

async function handleSubmit(answers: Answer[]) {
  try {
    await formStore.submitResponse(props.cell.id, answers)
  } catch (error) {
    console.error('提交答案失败:', error)
    throw error
  }
}
</script>

<style scoped>
.form-cell {
  @apply relative p-6 bg-white rounded-lg shadow-sm;
}

.connection-status {
  @apply absolute top-4 right-4 flex items-center gap-2 px-3 py-1.5 bg-gray-50 rounded-full text-sm;
}

.status-dot {
  @apply w-2 h-2 rounded-full bg-gray-300;
  transition: background-color 0.3s ease;
}

.status-dot.connected {
  @apply bg-green-500;
}

.status-dot.disconnected {
  @apply bg-red-500;
  animation: pulse 1.5s ease-in-out infinite;
}

.status-text {
  @apply text-gray-600;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
