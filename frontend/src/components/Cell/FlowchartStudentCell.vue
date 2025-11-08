<template>
  <div class="student-flowchart-cell">
    <div class="header">
      <div class="header-left">
        <span class="badge">学生任务</span>
        <h3 class="title">流程图创作</h3>
      </div>
      <div class="header-right" v-if="isStudentEditable">
        <div class="save-indicator" :class="saveStatus">
          <template v-if="saveStatus === 'saving'">保存中…</template>
          <template v-else-if="saveStatus === 'saved'">
            <span class="dot dot-success" />
            <span>已保存{{ lastSavedDisplay }}</span>
          </template>
          <template v-else-if="saveStatus === 'error'">
            <span class="dot dot-error" />
            <span>保存失败</span>
          </template>
        </div>
        <button
          v-if="hasLocalChanges"
          class="secondary-action"
          @click="resetToTeacher"
        >
          恢复教师版本
        </button>
      </div>
    </div>

    <div
      v-if="localLoadError"
      class="load-error-banner"
    >
      <span class="icon">⚠️</span>
      <span>{{ localLoadError }}</span>
    </div>

    <div
      v-if="!isStudentEditable"
      class="not-editable"
    >
      <div class="notice">
        <span class="icon">ℹ️</span>
        <span>教师暂未开放学生编辑，本流程图为只读模式。</span>
      </div>
      <FlowchartViewer
        :content="teacherContent"
        :show-minimap="cell.config?.showMinimap ?? true"
      />
    </div>

    <div v-else class="content">
      <div
        v-if="teacherUpdated"
        class="teacher-update-banner"
      >
        <span class="icon">🔔</span>
        <div class="message">
          <strong>教师已更新范例流程图。</strong>
          <p class="hint">你可以继续保留自己的作品，或点击“恢复教师版本”重新开始。</p>
        </div>
      </div>

      <div class="tabs">
        <button
          class="tab"
          :class="{ active: activeTab === 'student' }"
          @click="activeTab = 'student'"
        >
          我的流程图
        </button>
        <button
          class="tab"
          :class="{ active: activeTab === 'teacher' }"
          @click="activeTab = 'teacher'"
        >
          教师示例
        </button>
      </div>

      <div v-if="activeTab === 'teacher'" class="teacher-view">
        <FlowchartViewer
          :content="teacherContent"
          :show-minimap="cell.config?.showMinimap ?? true"
        />
        <p class="hint-text">可以参考教师提供的流程图范例，再切换回「我的流程图」进行创作。</p>
      </div>

      <div v-else class="editor-wrapper">
        <FlowchartEditor
          :key="editorKey"
          :content="studentContent"
          :show-minimap="cell.config?.showMinimap ?? true"
          @update="handleStudentUpdate"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useDebounceFn } from '@vueuse/core'
import FlowchartEditor from '@/components/Flowchart/FlowchartEditor.vue'
import FlowchartViewer from '@/components/Flowchart/FlowchartViewer.vue'
import type { FlowchartCell, FlowchartCellContent, FlowchartEdge, FlowchartNode } from '@/types/cell'

interface Props {
  cell: FlowchartCell
  editable?: boolean
}

const props = defineProps<Props>()

const route = useRoute()

const activeTab = ref<'student' | 'teacher'>('student')
const saveStatus = ref<'idle' | 'saving' | 'saved' | 'error'>('idle')
const lastSavedAt = ref<number | null>(null)
const teacherUpdated = ref(false)
const savedTeacherSignature = ref<string | null>(null)
const localLoadError = ref<string | null>(null)

const teacherContent = ref<FlowchartCellContent>(normalizeContent(props.cell.content))
const studentContent = ref<FlowchartCellContent>(normalizeContent(props.cell.content))

const editorKey = ref(0)

const lessonId = computed(() => route.params.id ? Number(route.params.id) : null)

const localStorageKey = computed(() => {
  if (!lessonId.value) return null
  return `lesson_${lessonId.value}_flowchart_${props.cell.id}`
})

const isStudentEditable = computed(() => {
  const configValue = props.cell.config?.editable
  return configValue === undefined ? true : Boolean(configValue)
})

const teacherSignature = computed(() => JSON.stringify(teacherContent.value))

const hasLocalChanges = computed(() => {
  return JSON.stringify(studentContent.value) !== JSON.stringify(teacherContent.value)
})

const lastSavedDisplay = computed(() => {
  if (!lastSavedAt.value) return ''
  const diffMs = Date.now() - lastSavedAt.value
  const diffMinutes = Math.floor(diffMs / 60000)
  if (diffMinutes <= 0) {
    return '（刚刚）'
  }
  if (diffMinutes < 60) {
    return `（${diffMinutes} 分钟前）`
  }
  const diffHours = Math.floor(diffMinutes / 60)
  if (diffHours < 24) {
    return `（${diffHours} 小时前）`
  }
  const diffDays = Math.floor(diffHours / 24)
  return `（${diffDays} 天前）`
})

const persistStudentContent = useDebounceFn(() => {
  if (!localStorageKey.value) return
  try {
    const payload = {
      version: 1,
      updatedAt: Date.now(),
      content: studentContent.value,
      teacherSignature: teacherSignature.value,
    }
    localStorage.setItem(localStorageKey.value, JSON.stringify(payload))
    lastSavedAt.value = payload.updatedAt
    saveStatus.value = 'saved'
  } catch (error) {
    console.error('Failed to persist student flowchart', error)
    saveStatus.value = 'error'
  }
}, 600)

function normalizeContent(content: FlowchartCellContent): FlowchartCellContent {
  return {
    nodes: (content?.nodes || []).map((node) => ({
      id: node.id,
      type: node.type,
      label: node.label,
      position: {
        x: node.position?.x ?? 0,
        y: node.position?.y ?? 0,
      },
      data: node.data ? JSON.parse(JSON.stringify(node.data)) : undefined,
    })) as FlowchartNode[],
    edges: (content?.edges || []).map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.label,
    })) as FlowchartEdge[],
    style: {
      theme: content?.style?.theme ?? 'light',
      layoutDirection: content?.style?.layoutDirection ?? 'TB',
    },
  }
}

function loadFromLocalStorage() {
  if (!localStorageKey.value) return

  const raw = localStorage.getItem(localStorageKey.value)
  if (!raw) {
    savedTeacherSignature.value = teacherSignature.value
    return
  }

  try {
    const parsed = JSON.parse(raw)
    if (parsed?.content) {
      studentContent.value = normalizeContent(parsed.content)
    }
    if (parsed?.updatedAt) {
      lastSavedAt.value = parsed.updatedAt
      saveStatus.value = 'saved'
    }
    if (parsed?.teacherSignature) {
      savedTeacherSignature.value = parsed.teacherSignature
      if (parsed.teacherSignature !== teacherSignature.value) {
        teacherUpdated.value = true
      }
    }
  } catch (error) {
    localLoadError.value = '无法加载上次保存的流程图，已为你恢复教师版本。'
    console.error('Failed to load student flowchart from localStorage', error)
    studentContent.value = normalizeContent(teacherContent.value)
    savedTeacherSignature.value = teacherSignature.value
  }
}

function handleStudentUpdate(content: FlowchartCellContent) {
  studentContent.value = normalizeContent(content)
  saveStatus.value = 'saving'
  persistStudentContent()
}

function resetToTeacher() {
  studentContent.value = normalizeContent(teacherContent.value)
  teacherUpdated.value = false
  savedTeacherSignature.value = teacherSignature.value
  editorKey.value += 1
  saveStatus.value = 'saving'
  persistStudentContent()
}

watch(
  () => props.cell.content,
  (newContent) => {
    teacherContent.value = normalizeContent(newContent)
  },
  { deep: true }
)

watch(teacherSignature, (newSignature) => {
  if (savedTeacherSignature.value && savedTeacherSignature.value !== newSignature) {
    teacherUpdated.value = true
  }
})

onMounted(() => {
  teacherContent.value = normalizeContent(props.cell.content)
  studentContent.value = normalizeContent(props.cell.content)

  if (isStudentEditable.value) {
    loadFromLocalStorage()
  }
})
</script>

<style scoped>
.student-flowchart-cell {
  @apply bg-white rounded-xl border border-gray-200 shadow-sm;
}

.header {
  @apply flex items-center justify-between gap-4 px-5 py-4 border-b border-gray-200 bg-gray-50 rounded-t-xl;
}

.header-left {
  @apply flex items-center gap-3;
}

.badge {
  @apply inline-flex items-center px-2.5 py-1 text-xs font-semibold bg-blue-100 text-blue-700 rounded-full;
}

.title {
  @apply text-base font-semibold text-gray-900;
}

.header-right {
  @apply flex items-center gap-3 text-sm;
}

.save-indicator {
  @apply flex items-center gap-2 text-gray-500;
}

.save-indicator.saved {
  @apply text-green-600;
}

.save-indicator.error {
  @apply text-red-600;
}

.dot {
  @apply inline-block w-2 h-2 rounded-full;
}

.dot-success {
  @apply bg-green-500;
}

.dot-error {
  @apply bg-red-500;
}

.secondary-action {
  @apply px-3 py-1.5 text-sm rounded-md border border-gray-300 text-gray-700 hover:bg-gray-100 transition-colors;
}

.not-editable {
  @apply p-6 space-y-4;
}

.notice {
  @apply flex items-center gap-3 px-4 py-3 bg-blue-50 text-blue-700 rounded-lg border border-blue-100;
}

.notice .icon {
  @apply text-lg;
}

.load-error-banner {
  @apply mx-5 mt-4 px-4 py-3 bg-red-50 border border-red-200 text-red-700 rounded-lg flex items-center gap-2;
}

.content {
  @apply p-5 space-y-4;
}

.teacher-update-banner {
  @apply flex items-start gap-3 px-4 py-3 bg-amber-50 border border-amber-200 text-amber-700 rounded-lg;
}

.teacher-update-banner .icon {
  @apply text-xl;
}

.teacher-update-banner .message {
  @apply text-sm leading-relaxed;
}

.tabs {
  @apply flex items-center gap-2;
}

.tab {
  @apply px-3 py-1.5 text-sm font-medium border border-gray-300 rounded-md text-gray-600 hover:bg-gray-100 transition-colors;
}

.tab.active {
  @apply bg-blue-600 border-blue-600 text-white shadow-sm;
}

.teacher-view,
.editor-wrapper {
  @apply bg-white border border-gray-200 rounded-lg overflow-hidden;
}

.teacher-view {
  @apply space-y-4;
}

.hint-text {
  @apply px-4 pb-4 text-sm text-gray-500;
}

.editor-wrapper {
  @apply min-h-[420px];
}
</style>


