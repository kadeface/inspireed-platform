<template>
  <div class="activity-cell cell-container" :class="{ 'fullscreen': isFullscreen }" ref="containerRef">
    <!-- 全屏按钮 - 仅学生模式显示 -->
    <div v-if="!editable && !isTeacher" class="cell-toolbar">
      <button
        class="cell-fullscreen-btn"
        :class="{ 'active': isFullscreen }"
        @click="toggleFullscreen"
        :title="isFullscreen ? '退出全屏 (Esc)' : '全屏查看'"
      >
        <svg v-if="!isFullscreen" class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
        </svg>
        <svg v-else class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
        <span class="text-sm font-medium ml-1">{{ isFullscreen ? '退出全屏' : '全屏' }}</span>
      </button>
    </div>
    
    <!-- 教师编辑模式 -->
    <div v-if="editable" class="activity-editor">
      <ActivityCellEditor
        :cell="cell"
        @update="handleUpdate"
      />
    </div>

    <!-- 教师查看学生提交模式 -->
    <div v-else-if="isTeacher" class="activity-teacher-view">
      <div class="teacher-view-header">
        <h3 class="view-title">{{ cell.content.title || '活动' }}</h3>
        <p v-if="cell.content.description" class="view-description">
          {{ cell.content.description }}
        </p>
      </div>
      
      <!-- 学生提交列表和统计（支持 UUID 和数字 ID） -->
      <UnifiedSubmissionPanel
        :cell-id="cell.id"
        :activity="cell.content"
        :session-id="sessionId"
        :lesson-id="lessonId"
        :cell-order="cell.order"
      />
      <!-- 调试信息 -->
      <div v-if="!sessionId" class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-800">
        ⚠️ 未提供 sessionId，将显示所有会话的提交（包括课后提交）。如果这是课堂模式，请确保传递 sessionId。
      </div>
    </div>

    <!-- 学生查看/答题模式 -->
    <div v-else class="activity-viewer">
      <ActivityViewer
        :cell="cell"
        :lesson-id="lessonId"
        :session-id="sessionId"
        :use-survey-js="useSurveyJS"
        @submit="handleSubmit"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, inject, watch, onMounted, type ComputedRef, type Ref } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '../../store/user'
import { UserRole } from '../../types/user'
import type { ActivityCell } from '../../types/cell'
import ActivityCellEditor from '../Activity/ActivityCellEditor.vue'
import ActivityViewer from '../Activity/ActivityViewer.vue'
import UnifiedSubmissionPanel from '../Activity/Teacher/UnifiedSubmissionPanel.vue'
import { useFullscreen } from '@/composables/useFullscreen'
import { useFeatureFlag } from '@/composables/useFeatureFlag'

interface Props {
  cell: ActivityCell
  editable?: boolean
  lessonId?: number  // 可选的 lessonId prop
  sessionId?: number  // 课堂会话ID（课堂模式传递）
  useSurveyJS?: boolean  // 是否使用 SurveyJS 渲染（默认根据活动类型自动选择）
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
  lessonId: undefined,
  sessionId: undefined,
  useSurveyJS: undefined,  // undefined 表示自动选择
})

// 移除频繁的 props 日志，只在必要时输出

const route = useRoute()
const userStore = useUserStore()

// 判断是否为教师
const isTeacher = computed(() => {
  return userStore.user?.role === UserRole.TEACHER
})

// 获取全局特性开关
const { isEnabled } = useFeatureFlag()

// 决定是否使用 SurveyJS
// 优先级：1. props.useSurveyJS（明确指定） 2. 全局特性开关 3. 自动选择（问卷类型）
const useSurveyJS = computed(() => {
  // 如果明确指定了 useSurveyJS，使用指定值
  if (props.useSurveyJS !== undefined) {
    return props.useSurveyJS
  }
  // 如果全局特性开关启用，所有活动都使用 SurveyJS
  if (isEnabled('use-surveyjs')) {
    return true
  }
  // 自动选择：问卷类型默认使用 SurveyJS
  return props.cell.content.activityType === 'survey'
})

// 🔧 尝试从 provide/inject 获取 sessionId 和 session（如果父组件提供了）
const injectedSessionId = inject<ComputedRef<number | undefined> | undefined>('classroomSessionId', undefined)
const injectedSession = inject<ComputedRef<any> | Ref<any> | undefined>('classroomSession', undefined)

// 从 props、inject 或 route 获取 lessonId
const lessonId = computed(() => {
  if (props.lessonId !== undefined) {
    return props.lessonId
  }
  // 从注入的 session 获取
  if (injectedSession?.value?.lessonId !== undefined) {
    return injectedSession.value.lessonId
  }
  // 从路由参数获取（适用于 LessonView 页面）
  const routeLessonId = route.params.id
  if (routeLessonId) {
    return Number(routeLessonId)
  }
  return undefined
})

// 从 props、inject 或 route 获取 sessionId
// 注意：computed 内部不输出日志，避免每次访问都输出
const sessionId = computed(() => {
  // 优先级 1: props
  if (props.sessionId !== undefined) {
    return props.sessionId
  }
  // 优先级 2: 从 inject 获取 sessionId（直接提供的）
  if (injectedSessionId?.value !== undefined) {
    return injectedSessionId.value
  }
  // 优先级 3: 从 inject 获取 session 对象，然后提取 id
  if (injectedSession) {
    const sessionValue = injectedSession.value
    if (sessionValue?.id !== undefined) {
      return sessionValue.id
    }
  }
  // 优先级 4: 从路由参数获取
  const routeSessionId = route.params.sessionId || route.query.sessionId
  if (routeSessionId) {
    const sessionIdNum = Number(routeSessionId)
    if (!isNaN(sessionIdNum)) {
      return sessionIdNum
    }
  }
  
  return undefined
})

// 使用 watch 监听 sessionId 变化，仅在开发环境输出日志
watch(() => sessionId.value, (newId, oldId) => {
  if (newId !== oldId) {
    const isDev = process.env.NODE_ENV === 'development'
    if (isDev) {
      if (newId !== undefined) {
        console.log('✅ ActivityCell: sessionId 已设置:', newId, {
          source: props.sessionId !== undefined ? 'props' : 
                  injectedSessionId?.value !== undefined ? 'injectedSessionId' : 
                  injectedSession?.value?.id !== undefined ? 'injectedSession' : 'route',
          cellId: props.cell.id,
        })
      } else {
        // 只在真正有问题时输出警告
        if (oldId !== undefined) {
          console.debug('ActivityCell: sessionId 已清除', { cellId: props.cell.id })
        }
      }
    }
  }
}, { immediate: false })

// 组件挂载时输出初始状态（仅在开发环境且 sessionId 为空时输出）
onMounted(() => {
  const isDev = process.env.NODE_ENV === 'development'
  
  // 只在开发环境且 sessionId 为空时输出警告
  if (isDev && !sessionId.value) {
    console.warn('⚠️ ActivityCell: 无法获取 sessionId', {
      cellId: props.cell.id,
      hasInjectedSession: !!injectedSession,
      hasInjectedSessionId: !!injectedSessionId,
      injectedSessionValue: injectedSession?.value,
      injectedSessionIdValue: injectedSessionId?.value,
    })
  } else if (isDev) {
    // 有 sessionId 时使用 debug 级别
    console.debug('ActivityCell 已挂载', {
      cellId: props.cell.id,
      sessionId: sessionId.value,
      isTeacher: isTeacher.value,
    })
  }
})

const emit = defineEmits<{
  update: [cell: ActivityCell]
}>()

const containerRef = ref<HTMLElement | null>(null)
const { isFullscreen, toggleFullscreen } = useFullscreen(containerRef)

function handleUpdate(updatedCell: ActivityCell) {
  emit('update', updatedCell)
}

function handleSubmit(submissionData: any) {
  console.log('Activity submitted:', submissionData)
  // 提交逻辑将在 ActivityViewer 中处理
}
</script>

<style scoped>
/* 全屏按钮样式 */
.cell-toolbar {
  @apply flex justify-end mb-2;
}

.cell-fullscreen-btn {
  @apply flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 rounded-md transition-colors;
}

.cell-fullscreen-btn.active {
  @apply bg-red-50 hover:bg-red-100 text-red-700;
}

.cell-fullscreen-btn .icon {
  @apply w-4 h-4;
}

/* 全屏模式样式 */
.activity-cell.fullscreen {
  @apply fixed inset-0 z-50 bg-white overflow-auto;
}

.activity-cell.fullscreen .activity-viewer {
  @apply p-8 max-w-5xl mx-auto;
}

.activity-cell {
  @apply min-h-[200px];
}

.activity-editor {
  @apply p-4;
}

.activity-viewer {
  @apply p-4;
}

.activity-teacher-view {
  @apply p-4 space-y-4;
}

.teacher-view-header {
  @apply mb-4 pb-4 border-b border-gray-200;
}

.view-title {
  @apply text-2xl font-bold text-gray-900 mb-2;
}

.view-description {
  @apply text-gray-600;
}
</style>

