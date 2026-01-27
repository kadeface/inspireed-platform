<template>
    <div class="lesson-list">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <span>加载教案中...</span>
      </div>
  
      <!-- Lesson List -->
      <div v-else-if="lessons.length > 0" class="lessons">
        <div v-for="lesson in lessons" :key="lesson.id" class="lesson-item">
          <div class="lesson-icon">
            📄
          </div>
          
          <div class="lesson-info">
            <div class="lesson-title">
              {{ lesson.title }}
              <span v-if="lesson.status === 'published'" class="status-badge published">已发布</span>
              <span v-else-if="lesson.status === 'draft'" class="status-badge draft">草稿</span>
              <span v-else-if="lesson.status === 'archived'" class="status-badge archived">已归档</span>
            </div>
            <div class="lesson-meta">
              <span v-if="lesson.description" class="meta-item">
                {{ lesson.description }}
              </span>
              <span class="meta-item">
                {{ formatDate(lesson.created_at) }}
              </span>
              <span v-if="lesson.cell_count > 0" class="meta-item">
                {{ lesson.cell_count }} 个单元格
              </span>
              <span v-if="lesson.creator_name" class="meta-item">
                创建者: {{ lesson.creator_name }}
              </span>
            </div>
          </div>
  
          <div class="lesson-actions">
            <button
              @click="handleView(lesson)"
              class="action-btn action-btn-secondary"
              title="查看教案"
            >
              <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              查看
            </button>
            <button
              @click="handleDelete(lesson)"
              class="action-btn action-btn-danger"
              title="删除教案"
            >
              <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              删除
            </button>
          </div>
        </div>
      </div>
  
      <!-- Empty State -->
      <div v-else class="empty-state">
        <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="empty-text">暂无教案</p>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, watch } from 'vue'
  import { lessonService } from '@/services/lesson'
  import { useToast } from '@/composables/useToast'
  import type { Lesson } from '@/types/lesson'
  
  interface Props {
    subjectId?: number
    gradeId?: number
    courseId?: number
  }
  
  const props = defineProps<Props>()
  
  const emit = defineEmits<{
    view: [lesson: Lesson]
    refresh: []
    deleted: [lessonId: number]
  }>()
  
  const toast = useToast()
  const loading = ref(false)
  const lessons = ref<Lesson[]>([])
  
  // 加载教案列表
  async function loadLessons() {
    // 至少需要提供一个筛选条件
    if (!props.subjectId && !props.gradeId && !props.courseId) {
      lessons.value = []
      return
    }
    
    loading.value = true
    try {
      const params = {
        page: 1,
        page_size: 100, // 获取所有教案
        subject_id: props.subjectId,
        grade_id: props.gradeId,
        course_id: props.courseId,
        creator_only: false // 教研员可以看到所有教案
      }
      console.log('Loading lessons with params:', params)
      const response = await lessonService.fetchLessons(params)
      console.log('Lessons response:', response)
      lessons.value = response.items || []
      console.log('Loaded lessons count:', lessons.value.length)
    } catch (error: any) {
      console.error('Failed to load lessons:', error)
      console.error('Error details:', error.response?.data || error.message)
      toast.error(error.response?.data?.detail || error.message || '加载教案失败')
    } finally {
      loading.value = false
    }
  }
  
  // 查看教案
  function handleView(lesson: Lesson) {
    emit('view', lesson)
  }

  // 删除教案
  async function handleDelete(lesson: Lesson) {
    if (!confirm(`确定要删除教案"${lesson.title}"吗？此操作不可撤销。`)) {
      return
    }

    try {
      await lessonService.deleteLesson(lesson.id)
      toast.success('教案删除成功')
      // 从列表中移除
      lessons.value = lessons.value.filter(l => l.id !== lesson.id)
      // 触发删除事件
      emit('deleted', lesson.id)
      // 触发刷新事件
      emit('refresh')
    } catch (error: any) {
      console.error('Failed to delete lesson:', error)
      toast.error(error.response?.data?.detail || error.message || '删除教案失败')
    }
  }
  
  // 格式化日期
  function formatDate(dateString: string): string {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)
    
    if (minutes < 1) return '刚刚'
    if (minutes < 60) return `${minutes}分钟前`
    if (hours < 24) return `${hours}小时前`
    if (days < 7) return `${days}天前`
    
    return date.toLocaleDateString('zh-CN')
  }
  
  // 监听筛选条件变化
  watch([() => props.subjectId, () => props.gradeId, () => props.courseId], () => {
    loadLessons()
  }, { immediate: true })
  
  // 暴露刷新方法
  defineExpose({
    refresh: loadLessons
  })
  </script>
  
  <style scoped>
  .lesson-list {
    padding: 0.5rem 0;
  }
  
  .loading-state {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    padding: 2rem;
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
  
  .lessons {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .lesson-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.75rem;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    transition: all 0.2s;
  }
  
  .lesson-item:hover {
    background: #f3f4f6;
    border-color: #d1d5db;
  }
  
  .lesson-icon {
    font-size: 1.5rem;
    flex-shrink: 0;
  }
  
  .lesson-info {
    flex: 1;
    min-width: 0;
  }
  
  .lesson-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 500;
    font-size: 0.875rem;
    color: #111827;
    margin-bottom: 0.25rem;
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
  
  .status-badge.archived {
    background: #e5e7eb;
    color: #374151;
  }
  
  .lesson-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    font-size: 0.75rem;
    color: #6b7280;
    margin-bottom: 0.25rem;
  }
  
  .meta-item {
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .lesson-actions {
    display: flex;
    gap: 0.375rem;
    flex-shrink: 0;
  }

  .action-btn {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.375rem 0.75rem;
    font-size: 0.75rem;
    font-weight: 500;
    border: none;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .icon {
    width: 1rem;
    height: 1rem;
  }

  .action-btn-secondary {
    background: white;
    color: #374151;
    border: 1px solid #d1d5db;
  }

  .action-btn-secondary:hover {
    background: #f9fafb;
  }

  .action-btn-danger {
    background: white;
    color: #dc2626;
    border: 1px solid #fca5a5;
  }

  .action-btn-danger:hover {
    background: #fef2f2;
    border-color: #dc2626;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    text-align: center;
  }

  .empty-icon {
    width: 3rem;
    height: 3rem;
    color: #d1d5db;
    margin-bottom: 0.75rem;
  }

  .empty-text {
    font-size: 0.938rem;
    color: #6b7280;
    font-weight: 500;
    margin: 0;
  }
</style>

  