<template>
  <div class="resource-statistics">
    <div class="stats-header">
      <h3 class="stats-title">资源统计</h3>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <!-- 查看次数 -->
      <div class="stat-card">
        <div class="stat-icon stat-icon-blue">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-label">查看次数</div>
          <div class="stat-value">{{ resource.view_count }}</div>
        </div>
      </div>

      <!-- 下载次数 -->
      <div class="stat-card">
        <div class="stat-icon stat-icon-green">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-label">下载次数</div>
          <div class="stat-value">{{ resource.download_count }}</div>
        </div>
      </div>

      <!-- 教案数量 -->
      <div class="stat-card">
        <div class="stat-icon stat-icon-purple">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-label">关联教案</div>
          <div class="stat-value">{{ lessonsCount }}</div>
        </div>
      </div>
    </div>

    <!-- 关联教案列表 -->
    <div v-if="lessonsCount > 0" class="lessons-section">
      <div class="section-header">
        <h4 class="section-title">基于此资源创建的教案</h4>
        <button
          v-if="!showLessons"
          @click="loadLessons"
          class="expand-btn"
        >
          <span>查看</span>
          <svg class="expand-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      <!-- 教案列表 -->
      <Transition name="expand">
        <div v-if="showLessons" class="lessons-list">
          <!-- 加载状态 -->
          <div v-if="isLoadingLessons" class="loading-state">
            <div class="spinner"></div>
            <span>加载教案列表...</span>
          </div>

          <!-- 教案项 -->
          <div v-else-if="lessons.length > 0" class="lessons-grid">
            <div
              v-for="lesson in lessons"
              :key="lesson.id"
              class="lesson-item"
              @click="handleViewLesson(lesson.id)"
            >
              <div class="lesson-header">
                <div class="lesson-title">{{ lesson.title }}</div>
                <span :class="['lesson-status', `status-${lesson.status}`]">
                  {{ getStatusLabel(lesson.status) }}
                </span>
              </div>
              <div v-if="lesson.description" class="lesson-description">
                {{ lesson.description }}
              </div>
              <div class="lesson-meta">
                <span>{{ lesson.cell_count }} 个单元</span>
                <span v-if="lesson.estimated_duration">
                  预计 {{ lesson.estimated_duration }} 分钟
                </span>
                <span>更新于 {{ formatDate(lesson.updated_at) }}</span>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-else class="empty-state">
            <p>暂无教案</p>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import type { Resource } from '../../types/resource'
import type { Lesson, LessonStatus } from '../../types/lesson'
import { lessonService } from '../../services/lesson'
import dayjs from 'dayjs'

interface Props {
  resource: Resource
  lessonsCount?: number
}

const props = defineProps<Props>()

const router = useRouter()

// 状态
const showLessons = ref(false)
const isLoadingLessons = ref(false)
const lessons = ref<Lesson[]>([])

// 计算教案数量
const lessonsCount = computed(() => {
  return props.lessonsCount || 0
})

// 加载教案列表
async function loadLessons() {
  if (lessons.value.length > 0) {
    showLessons.value = !showLessons.value
    return
  }
  
  isLoadingLessons.value = true
  showLessons.value = true
  
  try {
    // TODO: 添加按 reference_resource_id 筛选的API
    // 暂时获取所有教案然后过滤
    const response = await lessonService.fetchLessons({
      page: 1,
      page_size: 100
    })
    
    lessons.value = response.items.filter(
      lesson => lesson.reference_resource_id === props.resource.id
    )
  } catch (error) {
    console.error('Failed to load lessons:', error)
  } finally {
    isLoadingLessons.value = false
  }
}

// 查看教案
function handleViewLesson(lessonId: number) {
  router.push(`/teacher/lesson/${lessonId}`)
}

// 获取状态标签
function getStatusLabel(status: LessonStatus): string {
  const labels: Record<LessonStatus, string> = {
    draft: '草稿',
    published: '已发布',
    archived: '已归档'
  }
  return labels[status] || status
}

// 格式化日期
function formatDate(date: string): string {
  return dayjs(date).format('YYYY-MM-DD')
}
</script>

<style scoped>
.resource-statistics {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.stats-header {
  margin-bottom: 1.5rem;
}

.stats-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon svg {
  width: 1.5rem;
  height: 1.5rem;
}

.stat-icon-blue {
  background: #dbeafe;
  color: #1e40af;
}

.stat-icon-green {
  background: #dcfce7;
  color: #15803d;
}

.stat-icon-purple {
  background: #f3e8ff;
  color: #7e22ce;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.813rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
}

.lessons-section {
  border-top: 1px solid #e5e7eb;
  padding-top: 1.5rem;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.expand-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  color: #374151;
  font-size: 0.813rem;
  cursor: pointer;
  transition: all 0.2s;
}

.expand-btn:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.expand-icon {
  width: 1rem;
  height: 1rem;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
  color: #6b7280;
}

.spinner {
  width: 1.5rem;
  height: 1.5rem;
  border: 2px solid #f3f4f6;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.lessons-grid {
  display: grid;
  gap: 0.75rem;
}

.lesson-item {
  padding: 1rem;
  background: #fafafa;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.lesson-item:hover {
  background: white;
  border-color: #3b82f6;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.lesson-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.lesson-title {
  flex: 1;
  font-weight: 600;
  color: #111827;
  font-size: 0.938rem;
}

.lesson-status {
  padding: 0.25rem 0.625rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-draft {
  background: #f3f4f6;
  color: #6b7280;
}

.status-published {
  background: #d1fae5;
  color: #065f46;
}

.status-archived {
  background: #fef3c7;
  color: #92400e;
}

.lesson-description {
  font-size: 0.813rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.lesson-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: #9ca3af;
}

.empty-state {
  padding: 2rem;
  text-align: center;
  color: #9ca3af;
}

/* 动画 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 1000px;
  opacity: 1;
}
</style>

