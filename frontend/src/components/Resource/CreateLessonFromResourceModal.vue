<template>
  <Transition name="modal">
    <div
      v-if="modelValue"
      class="modal-overlay"
      @click.self="close"
    >
      <div class="modal-dialog">
        <!-- 对话框头部 -->
        <div class="modal-header">
          <h3 class="modal-title">参考官方教学设计创建教案</h3>
          <button @click="close" class="close-btn" title="关闭">
            <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 对话框内容 -->
        <div class="modal-body">
          <!-- 加载状态 -->
          <div v-if="isLoadingResource" class="loading-state">
            <div class="spinner"></div>
            <p>加载资源信息中...</p>
          </div>

          <!-- 表单 -->
          <form v-else @submit.prevent="handleSubmit">
            <!-- 参考资源信息 -->
            <div class="reference-section">
              <label class="section-label">✓ 参考资源</label>
              <div v-if="resource" class="resource-card">
                <div class="resource-icon">📋</div>
                <div class="resource-info">
                  <div class="resource-title">{{ resource.title }}</div>
                  <div class="resource-path" v-if="chapterPath">
                    章节：{{ chapterPath }}
                  </div>
                  <div class="resource-meta">
                    <span v-if="resource.file_size">{{ formatFileSize(resource.file_size) }}</span>
                    <span v-if="resource.page_count">{{ resource.page_count }} 页</span>
                    <span v-if="resource.is_official" class="official-badge">官方资源</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 教案信息 -->
            <div class="form-section">
              <div class="form-group">
                <label for="title" class="form-label">
                  教案标题 <span class="required">*</span>
                </label>
                <input
                  id="title"
                  v-model="formData.title"
                  type="text"
                  required
                  placeholder="例如：集合的概念 - 高一(1)班"
                  class="form-input"
                  :class="{ 'input-error': errors.title }"
                />
                <p v-if="errors.title" class="error-text">{{ errors.title }}</p>
              </div>

              <div class="form-group">
                <label for="description" class="form-label">
                  教案描述
                </label>
                <textarea
                  id="description"
                  v-model="formData.description"
                  rows="3"
                  placeholder="简要描述您的教学设计思路..."
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label for="notes" class="form-label">
                  参考笔记（可选）
                  <span class="label-hint">记录您从 PDF 中获得的启发</span>
                </label>
                <textarea
                  id="notes"
                  v-model="formData.reference_notes"
                  rows="5"
                  placeholder="例如：PDF中的教学目标很完整，需要重点关注第二部分的实例讲解..."
                  class="form-input notes-input"
                />
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label for="tags" class="form-label">标签</label>
                  <input
                    id="tags"
                    v-model="tagsInput"
                    type="text"
                    placeholder="用逗号分隔，例如：集合, 高一, 基础"
                    class="form-input"
                  />
                </div>

                <div class="form-group">
                  <label for="duration" class="form-label">预计时长（分钟）</label>
                  <input
                    id="duration"
                    v-model.number="formData.estimated_duration"
                    type="number"
                    min="1"
                    max="300"
                    placeholder="45"
                    class="form-input"
                  />
                </div>
              </div>
            </div>

            <!-- 提示信息 -->
            <div class="info-tip">
              <svg class="tip-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>创建后，您可以添加文本、代码、问答等多种类型的教学单元</span>
            </div>
          </form>
        </div>

        <!-- 对话框底部 -->
        <div class="modal-footer">
          <button
            type="button"
            @click="close"
            class="btn btn-secondary"
          >
            取消
          </button>
          <button
            type="button"
            @click="handleSubmit"
            :disabled="isSubmitting || isLoadingResource"
            class="btn btn-primary"
          >
            {{ isSubmitting ? '创建中...' : '创建教案' }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import type { Resource, CreateFromResourceRequest } from '../../types/resource'
import { formatFileSize } from '../../types/resource'
import { resourceService } from '../../services/resource'
import { lessonService } from '../../services/lesson'

interface Props {
  modelValue: boolean
  resourceId: number | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': [lessonId: number]
}>()

const router = useRouter()

// 状态
const resource = ref<Resource | null>(null)
const isLoadingResource = ref(false)
const isSubmitting = ref(false)
const errors = ref<Record<string, string>>({})

// 表单数据
const formData = ref({
  title: '',
  description: '',
  reference_notes: '',
  estimated_duration: 45
})

const tagsInput = ref('')

// 计算章节路径
const chapterPath = computed(() => {
  if (!resource.value?.chapter) return ''
  // TODO: 从完整数据中构建路径
  return resource.value.chapter.name
})

// 监听 resourceId 变化
watch(() => props.resourceId, (newId) => {
  if (newId && props.modelValue) {
    loadResource()
  }
})

// 监听模态框打开
watch(() => props.modelValue, (isOpen) => {
  if (isOpen && props.resourceId) {
    loadResource()
  } else if (!isOpen) {
    resetForm()
  }
})

// 加载资源信息
async function loadResource() {
  if (!props.resourceId) return
  
  isLoadingResource.value = true
  
  try {
    resource.value = await resourceService.getResource(props.resourceId)
    
    // 预填充标题（去除 "- 教学设计" 后缀）
    if (resource.value) {
      formData.value.title = resource.value.title.replace(/\s*[-–—]\s*教学设计\s*$/i, '')
    }
  } catch (error) {
    console.error('Failed to load resource:', error)
    alert('加载资源信息失败')
  } finally {
    isLoadingResource.value = false
  }
}

// 表单验证
function validateForm(): boolean {
  errors.value = {}
  
  if (!formData.value.title.trim()) {
    errors.value.title = '请输入教案标题'
    return false
  }
  
  if (formData.value.title.length > 200) {
    errors.value.title = '标题不能超过200个字符'
    return false
  }
  
  return true
}

// 提交表单
async function handleSubmit() {
  if (!validateForm() || !props.resourceId) return
  
  isSubmitting.value = true
  
  try {
    // 解析标签
    const tags = tagsInput.value
      .split(',')
      .map(t => t.trim())
      .filter(t => t.length > 0)
    
    // 构建请求数据
    const requestData: CreateFromResourceRequest = {
      reference_resource_id: props.resourceId,
      title: formData.value.title.trim(),
      description: formData.value.description.trim() || undefined,
      reference_notes: formData.value.reference_notes.trim() || undefined,
      tags: tags.length > 0 ? tags : undefined,
      estimated_duration: formData.value.estimated_duration || undefined
    }
    
    // 创建教案
    const lesson = await lessonService.createFromResource(requestData)
    
    // 成功后跳转到编辑器
    emit('success', lesson.id)
    router.push(`/teacher/lesson/${lesson.id}`)
    
    close()
  } catch (error: any) {
    console.error('Failed to create lesson:', error)
    alert(error.message || '创建教案失败，请重试')
  } finally {
    isSubmitting.value = false
  }
}

// 重置表单
function resetForm() {
  formData.value = {
    title: '',
    description: '',
    reference_notes: '',
    estimated_duration: 45
  }
  tagsInput.value = ''
  errors.value = {}
  isSubmitting.value = false
}

// 关闭对话框
function close() {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 1rem;
}

.modal-dialog {
  background: white;
  border-radius: 0.75rem;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.close-btn {
  padding: 0.5rem;
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  border-radius: 0.375rem;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #111827;
}

.icon {
  width: 1.5rem;
  height: 1.5rem;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 0;
  color: #6b7280;
}

.spinner {
  width: 2.5rem;
  height: 2.5rem;
  border: 4px solid #f3f4f6;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.reference-section {
  margin-bottom: 1.5rem;
}

.section-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.75rem;
}

.resource-card {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: #f0f7ff;
  border: 1px solid #bfdbfe;
  border-radius: 0.5rem;
}

.resource-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.resource-info {
  flex: 1;
  min-width: 0;
}

.resource-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1e40af;
  margin-bottom: 0.25rem;
}

.resource-path {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.resource-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.official-badge {
  color: #059669;
  font-weight: 500;
}

.form-section {
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.label-hint {
  font-weight: 400;
  color: #9ca3af;
  margin-left: 0.5rem;
}

.required {
  color: #ef4444;
}

.form-input {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  ring: 2px;
  ring-color: rgba(59, 130, 246, 0.1);
}

.form-input.input-error {
  border-color: #ef4444;
}

.notes-input {
  font-family: inherit;
  resize: vertical;
}

.error-text {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #ef4444;
}

.info-tip {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.875rem;
  background: #fef3c7;
  border: 1px solid #fde68a;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: #78350f;
}

.tip-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
  color: #d97706;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover:not(:disabled) {
  background: #f9fafb;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* 模态框动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-dialog,
.modal-leave-active .modal-dialog {
  transition: transform 0.3s ease;
}

.modal-enter-from .modal-dialog,
.modal-leave-to .modal-dialog {
  transform: translateY(-1rem);
}
</style>

