<template>
  <div
    class="group bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow duration-200 overflow-hidden cursor-pointer"
    @click="handleView"
  >
    <!-- 封面图 -->
    <div class="h-40 bg-gradient-to-br from-blue-500 to-purple-600 relative">
      <img
        v-if="lesson.cover_image_url"
        :src="lesson.cover_image_url"
        :alt="lesson.title"
        class="w-full h-full object-cover"
      />
      <div v-else class="absolute inset-0 flex items-center justify-center">
        <svg
          class="w-16 h-16 text-white opacity-50"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
          />
        </svg>
      </div>
      
      <!-- 状态标签 -->
      <div class="absolute top-2 right-2">
        <span :class="statusBadgeClass">
          {{ statusLabel }}
        </span>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="p-4">
      <!-- 标题 -->
      <h3 class="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
        {{ lesson.title }}
      </h3>

      <!-- 描述 -->
      <p class="text-sm text-gray-600 mb-4 line-clamp-2 min-h-[2.5rem]">
        {{ lesson.description || '暂无描述' }}
      </p>

      <!-- 标签 -->
      <div v-if="lesson.tags && lesson.tags.length > 0" class="flex flex-wrap gap-2 mb-4">
        <span
          v-for="tag in lesson.tags.slice(0, 3)"
          :key="tag"
          class="inline-flex items-center px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded"
        >
          {{ tag }}
        </span>
        <span
          v-if="lesson.tags.length > 3"
          class="inline-flex items-center px-2 py-1 text-xs font-medium bg-gray-100 text-gray-500 rounded"
        >
          +{{ lesson.tags.length - 3 }}
        </span>
      </div>

      <!-- 课程和章节信息 -->
      <div v-if="lesson.course || lesson.chapter" class="mb-3">
        <div v-if="lesson.course" class="text-xs text-blue-600 mb-1">
          📚 {{ lesson.course.name }}
        </div>
        <div v-if="lesson.chapter" class="text-xs text-purple-600">
          📖 {{ lesson.chapter.name }}
        </div>
      </div>

      <!-- 底部信息 -->
      <div class="flex items-center justify-between text-xs text-gray-500 mb-3">
        <span>更新于 {{ formattedDate }}</span>
        <span>{{ lesson.content.length }} 个单元</span>
      </div>

      <!-- 操作按钮 -->
      <div v-if="showActions" class="flex gap-2 pt-3 border-t border-gray-100" @click.stop>
        <button
          @click="handleEdit"
          :class="[
            'flex-1 px-3 py-1.5 text-sm font-medium rounded transition-colors',
            lesson.status === 'published' 
              ? 'text-orange-600 bg-orange-50 hover:bg-orange-100' 
              : 'text-blue-600 bg-blue-50 hover:bg-blue-100'
          ]"
          :title="lesson.status === 'published' ? '编辑已发布教案' : '编辑教案'"
        >
          {{ lesson.status === 'published' ? '编辑*' : '编辑' }}
        </button>
        <button
          @click="handleDuplicate"
          class="px-3 py-1.5 text-sm font-medium text-gray-600 bg-gray-50 rounded hover:bg-gray-100 transition-colors"
          title="复制"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
            />
          </svg>
        </button>
        <button
          v-if="lesson.status === 'draft'"
          @click="handlePublish"
          class="px-3 py-1.5 text-sm font-medium text-green-600 bg-green-50 rounded hover:bg-green-100 transition-colors"
          title="发布"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M5 13l4 4L19 7"
            />
          </svg>
        </button>
        <button
          @click="handleDelete"
          class="px-3 py-1.5 text-sm font-medium text-red-600 bg-red-50 rounded hover:bg-red-100 transition-colors"
          title="删除"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import dayjs from 'dayjs'
import type { Lesson } from '../../types/lesson'
import { LessonStatus } from '../../types/lesson'

interface Props {
  lesson: Lesson
  showActions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showActions: true,
})

const emit = defineEmits<{
  edit: [lessonId: number]
  'edit-published': [lessonId: number]
  duplicate: [lessonId: number]
  delete: [lessonId: number]
  publish: [lessonId: number]
  unpublish: [lessonId: number]
  view: [lessonId: number]
}>()

const statusLabel = computed(() => {
  const labelMap = {
    [LessonStatus.DRAFT]: '草稿',
    [LessonStatus.PUBLISHED]: '已发布',
    [LessonStatus.ARCHIVED]: '已归档',
  }
  return labelMap[props.lesson.status]
})

const statusBadgeClass = computed(() => {
  const classMap = {
    [LessonStatus.DRAFT]: 'px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded',
    [LessonStatus.PUBLISHED]: 'px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded',
    [LessonStatus.ARCHIVED]: 'px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-700 rounded',
  }
  return classMap[props.lesson.status]
})

const formattedDate = computed(() => {
  return dayjs(props.lesson.updated_at).format('YYYY-MM-DD HH:mm')
})

function handleEdit() {
  if (props.lesson.status === 'published') {
    // 编辑已发布教案时显示确认对话框
    if (confirm('此教案已发布，点击确定后教案将切换为草稿状态进行编辑。编辑完成后可重新发布。\n\n确定要继续吗？')) {
      // 发送一个特殊的编辑事件，标记需要先取消发布
      emit('edit-published', props.lesson.id)
    }
  } else {
    emit('edit', props.lesson.id)
  }
}

function handleDuplicate() {
  emit('duplicate', props.lesson.id)
}

function handleDelete() {
  emit('delete', props.lesson.id)
}

function handlePublish() {
  emit('publish', props.lesson.id)
}

function handleView() {
  emit('view', props.lesson.id)
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

