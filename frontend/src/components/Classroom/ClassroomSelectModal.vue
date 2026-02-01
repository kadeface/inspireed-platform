<template>
  <Transition name="modal">
    <div
      v-if="show"
      class="modal-backdrop"
      @click.self="handleCancel"
    >
      <div class="modal-content" @click.stop>
        <!-- 弹窗头部 -->
        <div class="modal-header">
          <div>
            <h3 class="modal-title">选择班级</h3>
            <p class="modal-subtitle">请选择要上课的班级，学生将加入该班级的课堂</p>
          </div>
          <button
            type="button"
            class="modal-close-btn"
            @click="handleCancel"
            aria-label="关闭"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 弹窗内容 -->
        <div class="modal-body">
          <!-- 加载状态 -->
          <div v-if="loading" class="loading-state">
            <svg class="loading-spinner" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span class="loading-text">加载班级中...</span>
          </div>

          <!-- 空状态 -->
          <div v-else-if="classrooms.length === 0" class="empty-state">
            当前没有可选的班级，请联系管理员配置班级信息。
          </div>

          <!-- 班级列表 -->
          <div v-else class="classroom-list">
            <label
              v-for="classroom in classrooms"
              :key="classroom.id"
              class="classroom-item"
              :class="{ 'classroom-item-selected': modelValue === classroom.id }"
            >
              <input
                type="radio"
                name="classroom-select"
                :value="classroom.id"
                :checked="modelValue === classroom.id"
                @change="$emit('update:modelValue', classroom.id)"
                class="classroom-radio"
              />
              <div class="classroom-info">
                <p class="classroom-name">{{ classroom.name }}</p>
                <p class="classroom-details">
                  年级：{{ formatGradeName(classroom.grade_id) }}
                  <span v-if="classroom.code" class="ml-2">班级编码：{{ classroom.code }}</span>
                </p>
              </div>
            </label>
          </div>

          <!-- 错误提示 -->
          <p v-if="error" class="error-message">
            {{ error }}
          </p>
        </div>

        <!-- 弹窗底部 -->
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-cancel"
            @click="handleCancel"
          >
            取消
          </button>
          <button
            type="button"
            class="btn btn-confirm"
            :disabled="loading || classrooms.length === 0 || !modelValue"
            @click="handleConfirm"
          >
            确认创建
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import type { LessonClassroom } from '../../types/lesson'

interface Props {
  show: boolean
  classrooms: LessonClassroom[]
  loading?: boolean
  modelValue?: number | null
  error?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  modelValue: null,
  error: null,
})

const emit = defineEmits<{
  'update:modelValue': [value: number]
  'update:show': [value: boolean]
  cancel: []
  confirm: []
}>()

function formatGradeName(gradeId: number): string {
  const gradeNames: Record<number, string> = {
    1: '一年级',
    2: '二年级',
    3: '三年级',
    4: '四年级',
    5: '五年级',
    6: '六年级',
    7: '七年级',
    8: '八年级',
    9: '九年级',
    10: '高一',
    11: '高二',
    12: '高三',
  }
  return gradeNames[gradeId] ?? `年级 ${gradeId}`
}

function handleCancel() {
  emit('update:show', false)
  emit('cancel')
}

function handleConfirm() {
  if (!props.modelValue) return
  emit('confirm')
}
</script>

<style scoped>
/* 弹窗背景 */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(17, 24, 39, 0.5);
  padding: 1rem 1.5rem;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 弹窗内容 */
.modal-content {
  width: 100%;
  max-width: 36rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 弹窗头部 */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e5e7eb;
  padding: 1rem 1.5rem;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.modal-subtitle {
  font-size: 0.75rem;
  color: #6b7280;
  margin: 0.25rem 0 0 0;
}

.modal-close-btn {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close-btn:hover {
  color: #4b5563;
  background: #f3f4f6;
}

/* 弹窗主体 */
.modal-body {
  max-height: 24rem;
  overflow-y: auto;
  padding: 1rem 1.5rem;
}

.modal-body::-webkit-scrollbar {
  width: 6px;
}

.modal-body::-webkit-scrollbar-track {
  background: #f3f4f6;
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* 加载状态 */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 0;
  color: #6b7280;
  gap: 0.5rem;
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

.loading-text {
  font-size: 0.875rem;
}

/* 空状态 */
.empty-state {
  background: #fefce8;
  border-radius: 0.375rem;
  padding: 1rem;
  font-size: 0.875rem;
  color: #a16207;
  text-align: center;
}

/* 班级列表 */
.classroom-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.classroom-item {
  display: flex;
  cursor: pointer;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.classroom-item:hover {
  border-color: #60a5fa;
  background: #eff6ff;
}

.classroom-item-selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.classroom-radio {
  margin-top: 0.25rem;
  width: 1rem;
  height: 1rem;
  color: #2563eb;
  cursor: pointer;
  flex-shrink: 0;
}

.classroom-radio:focus {
  outline: none;
  ring: 2px;
  ring-color: #2563eb;
  ring-offset: 2px;
}

.classroom-info {
  flex: 1;
  min-width: 0;
}

.classroom-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
  margin: 0 0 0.25rem 0;
}

.classroom-details {
  font-size: 0.75rem;
  color: #6b7280;
  margin: 0;
}

.ml-2 {
  margin-left: 0.5rem;
}

/* 错误提示 */
.error-message {
  margin-top: 1rem;
  font-size: 0.875rem;
  color: #dc2626;
}

/* 弹窗底部 */
.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
  padding: 1rem 1.5rem;
  border-radius: 0 0 0.5rem 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-cancel {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-cancel:hover {
  background: #f3f4f6;
}

.btn-confirm {
  background: #2563eb;
  color: white;
}

.btn-confirm:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-confirm:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

/* Vue Transition动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: translateY(20px);
  opacity: 0;
}
</style>
