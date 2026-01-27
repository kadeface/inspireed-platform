<template>
  <div class="reference-panel">
    <div class="panel-header">
      <div class="panel-title">
        <span class="title-icon">📋</span>
        <span class="title-text">参考资料：{{ resource.title }}</span>
      </div>
      <div class="panel-actions">
        <button
          @click="handleViewPDF"
          class="action-btn btn-view"
          title="查看PDF"
        >
          <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          <span class="btn-text">查看PDF</span>
        </button>
        <button
          @click="toggleNotes"
          class="action-btn btn-notes"
          :title="showNotes ? '收起笔记' : '编辑笔记'"
        >
          <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          <span class="btn-text">{{ showNotes ? '收起笔记' : '编辑笔记' }}</span>
        </button>
        <button
          @click="emit('close')"
          class="action-btn btn-close"
          title="关闭"
        >
          <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 笔记编辑区 -->
    <Transition name="slide">
      <div v-if="showNotes" class="notes-section">
        <label for="notes" class="notes-label">
          <svg class="label-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          参考笔记
        </label>
        <textarea
          id="notes"
          v-model="localNotes"
          placeholder="记录您从PDF中获得的启发、需要重点关注的部分等..."
          rows="8"
          class="notes-textarea"
          @blur="handleSaveNotes"
        />
        <div class="notes-footer">
          <div class="save-status">
            <span v-if="isSaving" class="status-saving">
              <svg class="status-icon animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              保存中...
            </span>
            <span v-else-if="saveSuccess" class="status-success">
              <svg class="status-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              已保存
            </span>
            <span v-else-if="saveError" class="status-error">
              <svg class="status-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              保存失败
            </span>
          </div>
          <div class="notes-hint">
            💡 笔记会在您编辑完成后自动保存
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Resource } from '../../types/resource'
import { lessonService } from '../../services/lesson'

interface Props {
  lessonId: number
  resource: Resource
  notes?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  'view-pdf': [resourceId: number]
  'notes-updated': [notes: string]
}>()

// 状态
const showNotes = ref(false)
const localNotes = ref(props.notes || '')
const isSaving = ref(false)
const saveSuccess = ref(false)
const saveError = ref(false)

// 监听外部 notes 变化
watch(() => props.notes, (newNotes) => {
  localNotes.value = newNotes || ''
})

// 切换笔记显示
function toggleNotes() {
  showNotes.value = !showNotes.value
}

// 查看 PDF
function handleViewPDF() {
  emit('view-pdf', props.resource.id)
}

// 保存笔记
async function handleSaveNotes() {
  // 如果内容没有变化，不保存
  if (localNotes.value === props.notes) return
  
  isSaving.value = true
  saveSuccess.value = false
  saveError.value = false
  
  try {
    await lessonService.updateReferenceNotes(
      props.lessonId,
      localNotes.value
    )
    
    saveSuccess.value = true
    emit('notes-updated', localNotes.value)
    
    // 2秒后清除成功状态
    setTimeout(() => {
      saveSuccess.value = false
    }, 2000)
  } catch (error) {
    console.error('Failed to save notes:', error)
    saveError.value = true
    
    // 3秒后清除错误状态
    setTimeout(() => {
      saveError.value = false
    }, 3000)
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
.reference-panel {
  background: linear-gradient(135deg, #f0f7ff 0%, #e0f2fe 100%);
  border: 1px solid #bae6fd;
  border-radius: 0.75rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  min-width: 0;
}

.title-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.title-text {
  font-weight: 600;
  color: #0c4a6e;
  font-size: 0.938rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.panel-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  background: white;
  border: 1px solid #bae6fd;
  border-radius: 0.375rem;
  color: #0369a1;
  font-size: 0.813rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f0f9ff;
  border-color: #7dd3fc;
}

.btn-icon {
  width: 1.125rem;
  height: 1.125rem;
}

.btn-text {
  display: none;
}

@media (min-width: 640px) {
  .btn-text {
    display: inline;
  }
}

.btn-close {
  padding: 0.5rem;
  color: #64748b;
}

.btn-close:hover {
  background: #fee2e2;
  border-color: #fecaca;
  color: #dc2626;
}

.notes-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #bae6fd;
}

.notes-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #0c4a6e;
  margin-bottom: 0.5rem;
}

.label-icon {
  width: 1.125rem;
  height: 1.125rem;
}

.notes-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #bae6fd;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-family: inherit;
  line-height: 1.6;
  resize: vertical;
  background: white;
  transition: all 0.2s;
}

.notes-textarea:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

.notes-textarea::placeholder {
  color: #94a3b8;
}

.notes-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.75rem;
}

.save-status {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.status-icon {
  width: 1rem;
  height: 1.rem;
}

.status-saving {
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.status-success {
  color: #16a34a;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.status-error {
  color: #dc2626;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.notes-hint {
  color: #64748b;
}

/* 滑动动画 */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  max-height: 0;
  opacity: 0;
  transform: translateY(-0.5rem);
}

.slide-enter-to {
  max-height: 500px;
  opacity: 1;
  transform: translateY(0);
}

.slide-leave-from {
  max-height: 500px;
  opacity: 1;
}

.slide-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-0.5rem);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>

