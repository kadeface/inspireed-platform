<template>
  <div class="lesson-resource-item">
    <div class="resource-card">
      <!-- 教案图标 -->
      <div class="resource-icon">
        <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      
      <!-- 教案信息 -->
      <div class="resource-info">
        <div class="resource-title">{{ lesson.title }}</div>
        <div class="resource-meta">
          <span v-if="lesson.cell_count">{{ lesson.cell_count }}个单元</span>
          <span v-if="lesson.estimated_duration">{{ lesson.estimated_duration }}分钟</span>
          <span>{{ lesson.view_count }}次查看</span>
          <span class="personal-badge">个人教案</span>
        </div>
        <div v-if="lesson.description" class="resource-description">
          {{ lesson.description }}
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="resource-actions">
      <button
        @click="$emit('edit', lesson.id)"
        class="action-btn edit-btn"
        title="编辑教案"
      >
        <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
        编辑
      </button>
      
      <button
        @click="$emit('view', lesson.id)"
        class="action-btn view-btn"
        title="查看教案"
      >
        <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
        查看
      </button>
      
      <button
        v-if="lesson.status === 'draft'"
        @click="$emit('publish', lesson.id)"
        class="action-btn publish-btn"
        title="发布教案"
      >
        <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
        </svg>
        发布
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Lesson } from '../../types/lesson'

interface Props {
  lesson: Lesson
}

defineProps<Props>()

defineEmits<{
  'edit': [lessonId: number]
  'view': [lessonId: number]
  'publish': [lessonId: number]
}>()
</script>

<style scoped>
.lesson-resource-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.lesson-resource-item:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.resource-card {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  flex: 1;
}

.resource-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 0.5rem;
  flex-shrink: 0;
}

.resource-icon .icon {
  width: 1.25rem;
  height: 1.25rem;
  color: white;
}

.resource-info {
  flex: 1;
  min-width: 0;
}

.resource-title {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
  line-height: 1.4;
}

.resource-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.75rem;
  color: #64748b;
}

.personal-badge {
  background: #dbeafe;
  color: #1e40af;
  padding: 0.125rem 0.5rem;
  border-radius: 0.75rem;
  font-weight: 500;
}

.resource-description {
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.resource-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex-shrink: 0;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.edit-btn {
  background: #3b82f6;
  color: white;
}

.edit-btn:hover {
  background: #2563eb;
}

.view-btn {
  background: #10b981;
  color: white;
}

.view-btn:hover {
  background: #059669;
}

.publish-btn {
  background: #f59e0b;
  color: white;
}

.publish-btn:hover {
  background: #d97706;
}

.btn-icon {
  width: 1rem;
  height: 1rem;
}

@media (max-width: 768px) {
  .lesson-resource-item {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .resource-actions {
    flex-direction: row;
    justify-content: flex-start;
  }
}
</style>
