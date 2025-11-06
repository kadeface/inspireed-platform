<template>
  <div class="chapter-tree-node-student">
    <div 
      class="chapter-item"
      :class="{ 'has-children': hasChildren, 'expanded': isExpanded, 'has-lessons': chapter.lesson_count > 0 }"
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
            {{ chapter.lesson_count }} 个课程
          </span>
          <button
            class="action-btn start-btn"
            @click.stop="viewLessons"
            v-if="chapter.lesson_count > 0"
            title="开始学习"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="action-text">开始学习</span>
          </button>
          <span v-else class="empty-tag">暂无内容</span>
        </div>
      </div>
    </div>

    <!-- 子章节 -->
    <Transition name="expand">
      <div v-if="isExpanded && hasChildren" class="children-container">
        <ChapterTreeNodeStudent
          v-for="child in chapter.children"
          :key="child.id"
          :chapter="child"
          :level="level + 1"
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
}

const props = withDefaults(defineProps<Props>(), {
  level: 0
})

const emit = defineEmits<{
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

function viewLessons() {
  emit('view-lessons', props.chapter.id)
}
</script>

<style scoped>
.chapter-tree-node-student {
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
  border-color: #10b981;
  box-shadow: 0 1px 3px rgba(16, 185, 129, 0.1);
}

.chapter-item.has-lessons {
  background: linear-gradient(to right, #ecfdf5 0%, white 3%);
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
  color: #047857;
  font-weight: 500;
  background: #d1fae5;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  white-space: nowrap;
}

.empty-tag {
  font-size: 0.75rem;
  color: #9ca3af;
  font-style: italic;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
  transition: all 0.2s;
  font-size: 0.75rem;
  font-weight: 500;
}

.action-btn:hover {
  transform: scale(1.05);
}

.start-btn {
  color: white;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.start-btn:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
}

.action-text {
  white-space: nowrap;
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

