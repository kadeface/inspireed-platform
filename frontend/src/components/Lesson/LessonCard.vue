<template>
  <div
    class="group relative flex h-full flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white/80 backdrop-blur-sm shadow-lg transition-all duration-300 hover:-translate-y-1 hover:border-emerald-300 hover:shadow-2xl hover:shadow-emerald-500/20"
    @click="handleView"
  >
    <!-- 封面图 -->
    <div class="relative h-44 bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500 overflow-hidden">
      <img
        v-if="coverImageUrl && !imageLoadError"
        :src="coverImageUrl"
        :alt="lesson.title"
        class="h-full w-full object-cover transition-transform duration-200 group-hover:scale-105"
        @error="imageLoadError = true"
        @load="imageLoadError = false"
      />
      <div
        v-else
        class="absolute inset-0 flex flex-col items-center justify-center gap-3 text-white/90"
      >
        <div class="rounded-2xl bg-white/20 backdrop-blur-md p-4 ring-2 ring-inset ring-white/30 shadow-xl">
          <svg class="h-10 w-10" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.6"
              d="M4.75 5.75A2.75 2.75 0 0 1 7.5 3h9a2.75 2.75 0 0 1 2.75 2.75v14.5l-5.5-3.083L8.25 20.25V5.75"
            />
          </svg>
        </div>
        <span class="text-sm font-semibold tracking-wide text-white/90 drop-shadow-sm">教案封面</span>
      </div>

      <div class="absolute inset-0 bg-gradient-to-t from-slate-900/60 via-slate-900/20 to-slate-900/0"></div>

      <!-- 顶部徽标 -->
      <div class="absolute top-3 left-3 flex flex-wrap gap-2">
        <span
          v-for="tag in displayTags"
          :key="tag"
          class="inline-flex items-center gap-1 rounded-full bg-white/30 backdrop-blur-md px-2.5 py-1 text-xs font-medium text-white shadow-lg border border-white/20"
        >
          <svg viewBox="0 0 24 24" class="h-3.5 w-3.5" fill="none" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="m3.75 4.5 8.25 8.25L20.25 4.5"
            />
          </svg>
          {{ tag }}
        </span>
        <span
          v-if="extraTagCount > 0"
          class="inline-flex items-center rounded-full bg-white/30 backdrop-blur-md px-2.5 py-1 text-xs font-medium text-white shadow-lg border border-white/20"
        >
          +{{ extraTagCount }}
        </span>
      </div>

      <!-- 状态标签 -->
      <div class="absolute top-3 right-3">
        <span :class="statusBadgeClass">
          {{ statusLabel }}
        </span>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="flex flex-1 flex-col gap-4 p-5">
      <div class="flex items-start justify-between gap-3">
        <div class="space-y-2">
          <!-- 标题 -->
          <h3 class="text-lg font-semibold text-gray-900 transition-colors duration-200 group-hover:text-emerald-600 line-clamp-2">
            {{ lesson.title }}
          </h3>

          <!-- 描述 -->
          <p class="text-sm leading-relaxed text-gray-600 line-clamp-2 min-h-[2.75rem]">
            {{ displayDescription }}
          </p>
        </div>

        <button
          v-if="showActions"
          class="hidden shrink-0 rounded-xl border border-gray-200 bg-white/80 backdrop-blur-sm px-3 py-1.5 text-xs font-medium text-gray-600 transition-all duration-200 hover:border-emerald-300 hover:bg-emerald-50 hover:text-emerald-600 group-hover:flex shadow-sm"
          @click.stop="handleEdit"
          :title="lesson.status === 'published' ? '编辑已发布教案' : '编辑教案'"
        >
          快速编辑
        </button>
      </div>

      <!-- 课程和章节信息 -->
      <div v-if="lesson.course || lesson.chapter" class="flex flex-wrap items-center gap-2 text-xs font-medium">
        <span
          v-if="lesson.course"
          class="inline-flex items-center gap-1 rounded-full bg-cyan-50 px-2.5 py-1 text-cyan-700 border border-cyan-100"
        >
          <svg viewBox="0 0 24 24" class="h-3.5 w-3.5" fill="none" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M4.5 6.75A2.25 2.25 0 0 1 6.75 4.5h10.5A2.25 2.25 0 0 1 19.5 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25H6.75A2.25 2.25 0 0 1 4.5 17.25V6.75Z"
            />
            <path stroke-linecap="round" stroke-width="1.5" d="M8.25 9h7.5m-7.5 3h4.5m-4.5 3H12" />
          </svg>
          {{ lesson.course.name }}
        </span>
        <span
          v-if="lesson.chapter"
          class="inline-flex items-center gap-1 rounded-full bg-teal-50 px-2.5 py-1 text-teal-700 border border-teal-100"
        >
          <svg viewBox="0 0 24 24" class="h-3.5 w-3.5" fill="none" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M8.25 7.5v9"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M18.75 7.5v9M12 7.5v9M4.5 6.75A2.25 2.25 0 0 1 6.75 4.5h10.5a2.25 2.25 0 0 1 2.25 2.25v10.5a2.25 2.25 0 0 1-2.25 2.25H6.75A2.25 2.25 0 0 1 4.5 17.25V6.75Z"
            />
          </svg>
          {{ lesson.chapter.name }}
        </span>
      </div>

      <!-- 元信息 -->
      <div class="flex flex-wrap items-center gap-3 text-xs text-gray-500">
        <span class="inline-flex items-center gap-2">
          <svg class="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M12 6v6l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          更新 {{ formattedDate }}
        </span>
        <span v-for="item in metaItems" :key="item.id" class="inline-flex items-center gap-2" :title="item.tooltip">
          <svg class="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              v-for="(path, index) in metaIconPaths[item.icon]"
              :key="`${item.id}-${index}`"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              :d="path"
            />
          </svg>
          {{ item.label }}
        </span>
      </div>

      <!-- 操作按钮 -->
      <div
        v-if="showActions"
        class="mt-auto flex flex-wrap items-center gap-2 rounded-xl border border-gray-100 bg-gray-50/80 backdrop-blur-sm p-2 transition-all duration-200 group-hover:border-emerald-200 group-hover:bg-emerald-50/60"
        @click.stop
      >
        <button
          @click="handleEdit"
          :class="[
            'flex-1 min-w-[90px] rounded-xl px-3 py-2 text-sm font-medium transition-all shadow-sm',
            lesson.status === 'published'
              ? 'bg-gradient-to-r from-amber-100 to-orange-100 text-amber-700 hover:from-amber-200 hover:to-orange-200'
              : 'bg-gradient-to-r from-emerald-100 to-teal-100 text-emerald-700 hover:from-emerald-200 hover:to-teal-200'
          ]"
          :title="lesson.status === 'published' ? '编辑已发布教案' : '编辑教案'"
        >
          {{ lesson.status === 'published' ? '编辑*' : '编辑' }}
        </button>
        <button
          @click="handleDuplicate"
          class="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-white text-gray-500 ring-1 ring-inset ring-gray-200 transition-all hover:text-emerald-600 hover:ring-emerald-300 hover:bg-emerald-50 shadow-sm"
          title="复制"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M8 16H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v2m-6 12h8a2 2 0 0 0 2-2v-8a2 2 0 0 0-2-2h-8a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2z"
            />
          </svg>
        </button>
        <button
          v-if="lesson.status === 'draft'"
          @click="handlePublish"
          class="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-white text-emerald-600 ring-1 ring-inset ring-emerald-200 transition-all hover:bg-emerald-50 hover:ring-emerald-300 shadow-sm"
          title="发布"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M5 13l4 4L19 7"
            />
          </svg>
        </button>
        <button
          @click="handleDelete"
          class="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-white text-red-600 ring-1 ring-inset ring-red-200 transition-all hover:bg-red-50 hover:ring-red-300 shadow-sm"
          title="删除"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M19 7l-.867 12.142A2 2 0 0 1 16.138 21H7.862a2 2 0 0 1-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v3M4 7h16"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import dayjs from 'dayjs'
import type { Lesson } from '../../types/lesson'
import { LessonStatus } from '../../types/lesson'
import { getServerBaseUrl } from '../../utils/url'

interface Props {
  lesson: Lesson
  showActions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showActions: true,
})

// 图片加载错误状态
const imageLoadError = ref(false)

// 构建完整的封面图片URL
const coverImageUrl = computed(() => {
  if (!props.lesson.cover_image_url) {
    return null
  }
  
  const url = props.lesson.cover_image_url
  
  // 如果已经是完整URL（http/https开头），直接返回
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  
  // 如果是相对路径（以/开头），构建完整URL
  if (url.startsWith('/')) {
    return `${getServerBaseUrl()}${url}`
  }
  
  // 其他情况直接返回
  return url
})

// 监听封面图片URL变化，重置错误状态
watch(() => props.lesson.cover_image_url, () => {
  imageLoadError.value = false
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
    [LessonStatus.DRAFT]:
      'inline-flex items-center gap-1 rounded-full bg-white/90 backdrop-blur-md px-2.5 py-1 text-xs font-semibold text-gray-700 shadow-lg border border-white/30',
    [LessonStatus.PUBLISHED]:
      'inline-flex items-center gap-1 rounded-full bg-emerald-100/90 backdrop-blur-md px-2.5 py-1 text-xs font-semibold text-emerald-700 shadow-lg border border-emerald-200/50',
    [LessonStatus.ARCHIVED]:
      'inline-flex items-center gap-1 rounded-full bg-amber-100/90 backdrop-blur-md px-2.5 py-1 text-xs font-semibold text-amber-700 shadow-lg border border-amber-200/50',
  }
  return classMap[props.lesson.status]
})

const formattedDate = computed(() => {
  return dayjs(props.lesson.updated_at).format('YYYY-MM-DD HH:mm')
})

const displayDescription = computed(() => {
  const desc = props.lesson.description?.trim()
  return desc && desc.length > 0 ? desc : '暂无描述'
})

const cellCount = computed(() => {
  if (typeof props.lesson.cell_count === 'number') {
    return props.lesson.cell_count
  }
  return props.lesson.content?.length ?? 0
})

const displayTags = computed(() => {
  return props.lesson.tags ? props.lesson.tags.slice(0, 2) : []
})

const extraTagCount = computed(() => {
  return props.lesson.tags && props.lesson.tags.length > 2 ? props.lesson.tags.length - 2 : 0
})

const metaIconPaths = {
  clock: ['M12 6v6l3 3', 'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z'],
  grid: ['M4 4h6v6H4z', 'M14 4h6v6h-6z', 'M4 14h6v6H4z', 'M14 14h6v6h-6z'],
  eye: ['M1.5 12s4.5-7.5 10.5-7.5S22.5 12 22.5 12 18 19.5 12 19.5 1.5 12 1.5 12z', 'M12 14.25a2.25 2.25 0 1 0 0-4.5 2.25 2.25 0 0 0 0 4.5z'],
} as const

type MetaIcon = keyof typeof metaIconPaths

interface MetaItem {
  id: string
  icon: MetaIcon
  label: string
  tooltip: string
}

const metaItems = computed<MetaItem[]>(() => {
  const items: MetaItem[] = []

  if (props.lesson.estimated_duration) {
    items.push({
      id: 'duration',
      icon: 'clock',
      label: `${props.lesson.estimated_duration} 分钟`,
      tooltip: '预计时长',
    })
  }

  items.push({
    id: 'cells',
    icon: 'grid',
    label: `${cellCount.value} 个单元`,
    tooltip: '单元数量',
  })

  if (props.lesson.view_count) {
    items.push({
      id: 'views',
      icon: 'eye',
      label: `${props.lesson.view_count} 浏览`,
      tooltip: '浏览次数',
    })
  }

  return items.slice(0, 3)
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

