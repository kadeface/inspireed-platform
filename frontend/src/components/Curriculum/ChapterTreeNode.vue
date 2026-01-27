<template>
  <div class="chapter-tree-node">
    <div 
      class="chapter-item"
      :class="{ 'has-children': hasChildren, 'expanded': isExpanded }"
      :style="{ paddingLeft: `${level * 1.5}rem` }"
    >
      <!-- 章节信息 -->
      <div class="chapter-info" @click="toggleExpand">
        <span v-if="hasChildren" class="expand-icon">
          {{ isExpanded ? '▼' : '▶' }}
        </span>
        <span v-else class="no-expand-spacer"></span>
        
        <div class="chapter-content">
          <h5 class="chapter-name">{{ chapter.name }}</h5>
          <span v-if="chapter.code" class="chapter-code">{{ chapter.code }}</span>
        </div>

        <div class="chapter-actions">
          <span v-if="chapter.lesson_count > 0" class="lesson-count">
            {{ chapter.lesson_count }} 个教案
          </span>
          <button
            class="action-btn view-btn"
            @click.stop="viewLessons"
            v-if="chapter.lesson_count > 0"
            title="查看教案"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </button>
          <button
            class="action-btn create-btn"
            @click.stop="createLesson"
            title="创建教案"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 子章节 -->
    <Transition name="expand">
      <div v-if="isExpanded && hasChildren" class="children-container">
        <ChapterTreeNode
          v-for="child in chapter.children"
          :key="child.id"
          :chapter="child"
          :level="level + 1"
          @create-lesson="$emit('create-lesson', $event, courseId)"
          @view-lessons="$emit('view-lessons', $event)"
        />
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ChapterTreeNode as ChapterNode } from '@/types/curriculum'

interface Props {
  chapter: ChapterNode
  level?: number
  courseId?: number
}

const props = withDefaults(defineProps<Props>(), {
  level: 0
})

const emit = defineEmits<{
  'create-lesson': [chapterId: number, courseId: number]
  'view-lessons': [chapterId: number]
}>()

const isExpanded = ref(false)

const hasChildren = computed(() => {
  return props.chapter.children && props.chapter.children.length > 0
})

function toggleExpand() {
  if (hasChildren.value) {
    isExpanded.value = !isExpanded.value
  }
}

function createLesson() {
  emit('create-lesson', props.chapter.id, props.courseId || 0)
}

function viewLessons() {
  emit('view-lessons', props.chapter.id)
}
</script>

<style scoped>
.chapter-tree-node {
  width: 100%;
}

.chapter-item {
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  background: white;
  transition: all 0.2s;
  margin-bottom: 0.375rem;
}

.chapter-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 1px 3px rgba(59, 130, 246, 0.1);
}

.chapter-item.expanded {
  background: #f0fdf4;
}

.chapter-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  cursor: pointer;
}

.expand-icon {
  font-size: 0.625rem;
  color: #6b7280;
  flex-shrink: 0;
  width: 1rem;
  transition: transform 0.2s;
}

.no-expand-spacer {
  width: 1rem;
  flex-shrink: 0;
}

.chapter-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.chapter-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chapter-code {
  font-size: 0.75rem;
  color: #6b7280;
  background: #f3f4f6;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  white-space: nowrap;
}

.chapter-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.lesson-count {
  font-size: 0.75rem;
  color: #059669;
  font-weight: 500;
  background: #d1fae5;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  white-space: nowrap;
}

.action-btn {
  padding: 0.375rem;
  border-radius: 0.375rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  transform: scale(1.05);
}

.view-btn {
  color: #3b82f6;
  background: #eff6ff;
}

.view-btn:hover {
  background: #dbeafe;
}

.create-btn {
  color: #059669;
  background: #d1fae5;
}

.create-btn:hover {
  background: #a7f3d0;
}

.children-container {
  padding-left: 1rem;
  margin-top: 0.375rem;
}

/* 过渡动画 */
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

