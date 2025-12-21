<template>
  <div
    class="group relative flex h-full flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white/80 backdrop-blur-sm shadow-lg transition-all duration-300 hover:-translate-y-1 hover:border-emerald-300 hover:shadow-2xl hover:shadow-emerald-500/20"
    @click="handleView"
  >
    <!-- 封面图 -->
    <div class="relative h-44 bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500 overflow-hidden">
      <img
        v-if="project.cover_image_url && !image_load_error"
        :src="project.cover_image_url"
        :alt="project.title"
        class="h-full w-full object-cover transition-transform duration-200 group-hover:scale-105"
        @error="image_load_error = true"
        @load="image_load_error = false"
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
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>
        <span class="text-sm font-semibold tracking-wide text-white/90 drop-shadow-sm">项目封面</span>
      </div>

      <div class="absolute inset-0 bg-gradient-to-t from-slate-900/60 via-slate-900/20 to-slate-900/0"></div>

      <!-- 状态标签 -->
      <div class="absolute top-3 right-3">
        <span :class="status_badge_class">
          {{ status_label }}
        </span>
      </div>

      <!-- 进度指示器 -->
      <div class="absolute bottom-3 left-3 right-3">
        <div class="bg-white/20 backdrop-blur-md rounded-lg p-2">
          <div class="flex items-center justify-between text-xs text-white mb-1">
            <span class="font-medium">完成度</span>
            <span class="font-bold">{{ overall_completion }}%</span>
          </div>
          <div class="w-full bg-white/30 rounded-full h-2">
            <div
              class="bg-gradient-to-r from-emerald-400 to-teal-400 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${overall_completion}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="flex flex-1 flex-col gap-4 p-5">
      <div class="flex items-start justify-between gap-3">
        <div class="space-y-2 flex-1">
          <!-- 标题 -->
          <h3 class="text-lg font-semibold text-gray-900 transition-colors duration-200 group-hover:text-emerald-600 line-clamp-2">
            {{ project.title }}
          </h3>

          <!-- 描述 -->
          <p class="text-sm leading-relaxed text-gray-600 line-clamp-2 min-h-[2.75rem]">
            {{ display_description }}
          </p>
        </div>
      </div>

      <!-- 5E阶段进度 -->
      <div class="grid grid-cols-5 gap-2">
        <div
          v-for="stage in stages"
          :key="stage.key"
          class="flex flex-col items-center gap-1"
        >
          <div class="text-xs font-medium text-gray-600">{{ stage.label }}</div>
          <div class="relative w-full bg-gray-200 rounded-full h-1.5">
            <div
              :class="stage.color_class"
              class="h-1.5 rounded-full transition-all duration-300"
              :style="{ width: `${project.completion[stage.key]}%` }"
            ></div>
          </div>
          <div class="text-xs text-gray-500">{{ project.completion[stage.key] }}%</div>
        </div>
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
          更新 {{ formatted_date }}
        </span>
      </div>

      <!-- 操作按钮 -->
      <div
        class="mt-auto flex flex-wrap items-center gap-2 rounded-xl border border-gray-100 bg-gray-50/80 backdrop-blur-sm p-2 transition-all duration-200 group-hover:border-emerald-200 group-hover:bg-emerald-50/60"
        @click.stop
      >
        <button
          @click="handleEdit"
          class="flex-1 min-w-[90px] rounded-xl px-3 py-2 text-sm font-medium transition-all shadow-sm bg-gradient-to-r from-emerald-100 to-teal-100 text-emerald-700 hover:from-emerald-200 hover:to-teal-200"
          title="编辑项目"
        >
          编辑
        </button>
        <button
          @click="handleDelete"
          class="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-white text-red-600 ring-1 ring-inset ring-red-200 transition-all hover:bg-red-50 hover:ring-red-300 shadow-sm"
          title="删除项目"
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
import type { StudentProject, ProjectStatus } from '../../types/student_project'

interface Props {
  project: StudentProject
}

const props = defineProps<Props>()

// 图片加载错误状态
const image_load_error = ref(false)

// 监听封面图片URL变化，重置错误状态
watch(() => props.project.cover_image_url, () => {
  image_load_error.value = false
})

const emit = defineEmits<{
  edit: [projectId: number]
  delete: [projectId: number]
  view: [projectId: number]
}>()

const status_label = computed(() => {
  const label_map: Record<ProjectStatus, string> = {
    draft: '草稿',
    in_progress: '进行中',
    completed: '已完成',
    submitted: '已提交',
  }
  return label_map[props.project.status]
})

const status_badge_class = computed(() => {
  const class_map: Record<ProjectStatus, string> = {
    draft: 'inline-flex items-center gap-1 rounded-full bg-white/90 backdrop-blur-md px-2.5 py-1 text-xs font-semibold text-gray-700 shadow-lg border border-white/30',
    in_progress: 'inline-flex items-center gap-1 rounded-full bg-blue-100/90 backdrop-blur-md px-2.5 py-1 text-xs font-semibold text-blue-700 shadow-lg border border-blue-200/50',
    completed: 'inline-flex items-center gap-1 rounded-full bg-emerald-100/90 backdrop-blur-md px-2.5 py-1 text-xs font-semibold text-emerald-700 shadow-lg border border-emerald-200/50',
    submitted: 'inline-flex items-center gap-1 rounded-full bg-purple-100/90 backdrop-blur-md px-2.5 py-1 text-xs font-semibold text-purple-700 shadow-lg border border-purple-200/50',
  }
  return class_map[props.project.status]
})

const formatted_date = computed(() => {
  return dayjs(props.project.updated_at).format('YYYY-MM-DD HH:mm')
})

const display_description = computed(() => {
  const desc = props.project.description?.trim()
  return desc && desc.length > 0 ? desc : '暂无描述'
})

const overall_completion = computed(() => {
  const completion = props.project.completion
  const total = completion.engage + completion.explore + completion.explain + completion.elaborate + completion.evaluate
  return Math.round(total / 5)
})

const stages = computed(() => [
  { key: 'engage', label: 'Engage', color_class: 'bg-orange-400' },
  { key: 'explore', label: 'Explore', color_class: 'bg-blue-400' },
  { key: 'explain', label: 'Explain', color_class: 'bg-green-400' },
  { key: 'elaborate', label: 'Elaborate', color_class: 'bg-purple-400' },
  { key: 'evaluate', label: 'Evaluate', color_class: 'bg-red-400' },
])

function handleEdit() {
  emit('edit', props.project.id)
}

function handleDelete() {
  emit('delete', props.project.id)
}

function handleView() {
  emit('view', props.project.id)
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
