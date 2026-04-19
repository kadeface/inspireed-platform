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
        创建课堂
      </button>
    </template>

    <!-- PREPARING / PENDING：讲授型（无学生）或互动型（有学生）均可开始上课 -->
    <template
      v-else-if="
        sessionStatus === 'PREPARING' ||
        sessionStatus === 'preparing' ||
        sessionStatus === 'PENDING' ||
        sessionStatus === 'pending'
      "
    >
      <button
        data-testid="start-teaching-button"
        @click="$emit('start')"
        :disabled="loading"
        class="btn btn-primary"
        :title="
          mergeStartWithMinimalUi
            ? activeStudentsCount === 0
              ? '开始上课并进入极简导播（讲授型 / 幻灯片）'
              : '开始上课并进入极简导播（互动型）'
            : activeStudentsCount === 0
              ? '开始上课（讲授型/幻灯片模式）'
              : '开始上课（互动型模式）'
        "
      >
        开始授课
        <span v-if="mergeStartWithMinimalUi" class="ml-2 text-xs opacity-75">
          <template v-if="activeStudentsCount === 0">(讲授型 · 极简)</template>
          <template v-else>(互动型 · 极简)</template>
        </span>
        <span v-else-if="activeStudentsCount === 0" class="ml-2 text-xs opacity-75">(讲授型)</span>
        <span v-else class="ml-2 text-xs opacity-75">(互动型)</span>
      </button>
      <button
        data-testid="end-session-button"
        @click="$emit('end')"
        :disabled="loading"
        class="btn btn-danger"
        title="结束当前会话，以便创建新会话"
      >
        结束课堂
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
        结束授课
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
        创建新课堂
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
  /** 与导播台「极简授课」合并：准备中只保留本按钮，点击后开始上课并进入极简布局 */
  mergeStartWithMinimalUi?: boolean
}

withDefaults(defineProps<Props>(), {
  hasSession: false,
  sessionStatus: 'ended',
  loading: false,
  activeStudentsCount: 0,
  mergeStartWithMinimalUi: false,
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
  gap: 0.625rem;
  align-items: center;
  flex-wrap: wrap;
}

.btn {
  padding: 0.55rem 1rem;
  border-radius: 0.625rem;
  font-size: 0.875rem;
  font-weight: 600;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  min-height: 36px;
  letter-spacing: 0.01em;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%);
  border-color: #1d4ed8;
  color: white;
  box-shadow: 0 6px 14px rgba(37, 99, 235, 0.22);
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(180deg, #1d4ed8 0%, #1e40af 100%);
  transform: translateY(-1px);
  box-shadow: 0 10px 16px rgba(37, 99, 235, 0.3);
}

.btn-danger {
  background: #ffffff;
  border-color: #fecaca;
  color: #b91c1c;
  box-shadow: 0 2px 8px rgba(185, 28, 28, 0.08);
}

.btn-danger:hover:not(:disabled) {
  background: #fef2f2;
  border-color: #fca5a5;
  color: #991b1b;
}

.btn-danger:active:not(:disabled),
.btn-primary:active:not(:disabled) {
  transform: translateY(0);
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
