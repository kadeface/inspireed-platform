<template>
  <div class="session-control-buttons" data-testid="session-control-buttons">
    <!-- 无会话状态：显示创建按钮 -->
    <template v-if="!hasSession">
      <button
        data-testid="create-session-button"
        @click="$emit('create')"
        :disabled="loading"
        class="btn btn-primary"
      >
        📚 创建课堂
      </button>
    </template>

    <!-- PREPARING 状态：讲授型（无学生）或互动型（有学生）均可开始上课 -->
    <template v-else-if="sessionStatus === 'PREPARING' || sessionStatus === 'preparing'">
      <button
        data-testid="start-teaching-button"
        @click="$emit('start')"
        :disabled="loading"
        class="btn btn-primary"
        :title="activeStudentsCount === 0 ? '开始上课（讲授型/幻灯片模式）' : '开始上课（互动型模式）'"
      >
        ▶️ 开始上课
        <span v-if="activeStudentsCount === 0" class="ml-2 text-xs opacity-75">(讲授型)</span>
        <span v-else class="ml-2 text-xs opacity-75">(互动型)</span>
      </button>
      <button
        data-testid="end-session-button"
        @click="$emit('end')"
        :disabled="loading"
        class="btn btn-danger"
        title="结束当前会话，以便创建新会话"
      >
        ⏹️ 结束
      </button>
    </template>

    <!-- TEACHING 状态：上课中 -->
    <template v-else-if="sessionStatus === 'TEACHING' || sessionStatus === 'teaching'">
      <button
        data-testid="end-session-button"
        @click="$emit('end')"
        :disabled="loading"
        class="btn btn-danger"
        title="结束当前课程"
      >
        ⏹️ 结束授课
      </button>
    </template>

    <!-- ENDED 状态：已结束 -->
    <template v-else>
      <button
        data-testid="create-session-button"
        @click="$emit('create')"
        :disabled="loading"
        class="btn btn-primary"
      >
        📚 创建新课堂
      </button>
    </template>
  </div>
</template>

<script setup lang="ts">
interface Props {
  hasSession?: boolean
  sessionStatus?: string
  loading?: boolean
  activeStudentsCount?: number
}

withDefaults(defineProps<Props>(), {
  hasSession: false,
  sessionStatus: 'ended',
  loading: false,
  activeStudentsCount: 0
})

defineEmits<{
  create: []
  start: []
  end: []
}>()
</script>

<style scoped>
.session-control-buttons {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

.btn-disabled-hint {
  position: relative;
}

.btn-disabled-hint:disabled::after {
  content: attr(title);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #1f2937;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  white-space: nowrap;
  margin-bottom: 0.25rem;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s;
}

.btn-disabled-hint:hover::after {
  opacity: 1;
}
</style>
