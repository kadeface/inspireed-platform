<template>
  <Transition name="modal">
    <div v-if="isOpen" class="modal-overlay" @click.self="handleClose">
      <div class="modal-container">
        <div class="modal-header">
          <h2 class="modal-title">关联教案到章节</h2>
          <button @click="handleClose" class="close-btn">✕</button>
        </div>

        <div class="modal-body">
          <div v-if="!chapter" class="error-message">
            <p>章节信息缺失</p>
          </div>

          <div v-else>
            <div class="chapter-info">
              <p class="info-label">章节：</p>
              <p class="info-value">{{ chapter.name }}</p>
            </div>

            <!-- Search -->
            <div class="search-section">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="搜索教案标题..."
                class="search-input"
                @input="handleSearch"
              />
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="loading-state">
              <div class="spinner"></div>
              <span>加载教案中...</span>
            </div>

            <!-- Lesson List -->
            <div v-else-if="availableLessons.length > 0" class="lesson-list">
              <div
                v-for="lesson in availableLessons"
                :key="lesson.id"
                class="lesson-item"
                :class="{ 'selected': selectedLessons.has(lesson.id) }"
                @click="toggleLesson(lesson.id)"
              >
                <div class="lesson-checkbox">
                  <input
                    type="checkbox"
                    :checked="selectedLessons.has(lesson.id)"
                    @change="toggleLesson(lesson.id)"
                  />
                </div>
                <div class="lesson-content">
                  <div class="lesson-title">
                    {{ lesson.title }}
                    <span v-if="lesson.chapter_id" class="already-linked-badge">已关联其他章节</span>
                  </div>
                  <div v-if="lesson.description" class="lesson-description">
                    {{ lesson.description }}
                  </div>
                  <div class="lesson-meta">
                    <span v-if="lesson.status === 'published'" class="status-badge published">已发布</span>
                    <span v-else-if="lesson.status === 'draft'" class="status-badge draft">草稿</span>
                    <span class="meta-text">{{ formatDate(lesson.created_at) }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-else class="empty-state">
              <p class="empty-text">没有可用的教案</p>
              <p class="empty-hint">请确保该课程下有教案，且教案未被关联到其他章节</p>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="handleClose" class="btn btn-secondary">取消</button>
          <button
            @click="handleConfirm"
            class="btn btn-primary"
            :disabled="selectedLessons.size === 0 || saving"
          >
            {{ saving ? '关联中...' : `关联 ${selectedLessons.size} 个教案` }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { lessonService } from '@/services/lesson'
import { useToast } from '@/composables/useToast'
import type { Lesson } from '@/types/lesson'
import type { Chapter } from '@/types/curriculum'

interface Props {
  isOpen: boolean
  chapter: Chapter | null
  courseId: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  success: []
}>()

const toast = useToast()
const loading = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const availableLessons = ref<Lesson[]>([])
const selectedLessons = ref<Set<number>>(new Set())

// 加载可用教案列表
async function loadAvailableLessons() {
  if (!props.courseId) return

  loading.value = true
  try {
    // 获取该课程下的所有教案
    const response = await lessonService.fetchLessons({
      course_id: props.courseId,
      page: 1,
      page_size: 100, // 获取所有教案
      search: searchQuery.value || undefined
    })
    
    // 过滤掉已经关联到当前章节的教案（如果当前章节有ID）
    // 但保留已关联到其他章节的教案，允许用户重新关联
    availableLessons.value = response.items || []
  } catch (error: any) {
    console.error('Failed to load lessons:', error)
    toast.error('加载教案列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索教案
function handleSearch() {
  loadAvailableLessons()
}

// 切换教案选择
function toggleLesson(lessonId: number) {
  if (selectedLessons.value.has(lessonId)) {
    selectedLessons.value.delete(lessonId)
  } else {
    selectedLessons.value.add(lessonId)
  }
}

// 确认关联
async function handleConfirm() {
  if (!props.chapter || selectedLessons.value.size === 0) return

  saving.value = true
  try {
    // 批量更新教案的 chapter_id
    const updatePromises = Array.from(selectedLessons.value).map(lessonId =>
      lessonService.updateLesson(lessonId, {
        chapter_id: props.chapter!.id
      })
    )

    await Promise.all(updatePromises)
    
    toast.success(`成功关联 ${selectedLessons.value.size} 个教案`)
    emit('success')
    handleClose()
  } catch (error: any) {
    console.error('Failed to associate lessons:', error)
    toast.error(error.response?.data?.detail || '关联失败')
  } finally {
    saving.value = false
  }
}

// 关闭模态框
function handleClose() {
  selectedLessons.value.clear()
  searchQuery.value = ''
  emit('close')
}

// 格式化日期
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 监听模态框打开和课程ID变化
watch(() => props.isOpen, (newVal) => {
  if (newVal && props.courseId) {
    loadAvailableLessons()
  }
})

watch(() => props.courseId, () => {
  if (props.isOpen && props.courseId) {
    loadAvailableLessons()
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
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
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #111827;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.error-message {
  padding: 2rem;
  text-align: center;
  color: #dc2626;
}

.chapter-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: #f3f4f6;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
}

.info-label {
  font-weight: 500;
  color: #374151;
  margin: 0;
}

.info-value {
  color: #111827;
  margin: 0;
}

.search-section {
  margin-bottom: 1.5rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.spinner {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.lesson-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 400px;
  overflow-y: auto;
}

.lesson-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.lesson-item:hover {
  border-color: #d1d5db;
  background: #f9fafb;
}

.lesson-item.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.lesson-checkbox {
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.lesson-checkbox input[type="checkbox"] {
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
}

.lesson-content {
  flex: 1;
  min-width: 0;
}

.lesson-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  font-size: 0.938rem;
  color: #111827;
  margin-bottom: 0.5rem;
}

.already-linked-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  background: #fef3c7;
  color: #92400e;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 9999px;
}

.lesson-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.lesson-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 9999px;
}

.status-badge.published {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.draft {
  background: #fef3c7;
  color: #92400e;
}

.meta-text {
  color: #9ca3af;
}

.empty-state {
  padding: 3rem;
  text-align: center;
}

.empty-text {
  font-size: 0.938rem;
  color: #6b7280;
  font-weight: 500;
  margin: 0 0 0.5rem;
}

.empty-hint {
  font-size: 0.813rem;
  color: #9ca3af;
  margin: 0;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #f9fafb;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>

