<template>
  <div class="activity-cell">
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
      
      <!-- 学生提交列表 -->
      <div v-if="actualCellId > 0">
        <SubmissionList
          :cell-id="actualCellId"
          :activity="cell.content"
        />
      </div>
      <div v-else class="text-center py-8 text-gray-500 border border-gray-200 rounded-lg">
        <p class="mb-2">⚠️ 无法加载学生提交列表</p>
        <p class="text-sm">Cell ID 解析失败，请确保该活动已保存到数据库</p>
        <p class="text-xs mt-2 text-gray-400">Cell ID: {{ cell.id }}</p>
      </div>
    </div>

    <!-- 学生查看/答题模式 -->
    <div v-else class="activity-viewer">
      <ActivityViewer
        :cell="cell"
        :lesson-id="lessonId"
        @submit="handleSubmit"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '../../store/user'
import { UserRole } from '../../types/user'
import type { ActivityCell } from '../../types/cell'
import ActivityCellEditor from '../Activity/ActivityCellEditor.vue'
import ActivityViewer from '../Activity/ActivityViewer.vue'
import SubmissionList from '../Activity/Teacher/SubmissionList.vue'

interface Props {
  cell: ActivityCell
  editable?: boolean
  lessonId?: number  // 可选的 lessonId prop
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
  lessonId: undefined,
})

const route = useRoute()
const userStore = useUserStore()

// 判断是否为教师
const isTeacher = computed(() => {
  return userStore.user?.role === UserRole.TEACHER
})

// 从 props 或 route 获取 lessonId
const lessonId = computed(() => {
  if (props.lessonId !== undefined) {
    return props.lessonId
  }
  // 从路由参数获取（适用于 LessonView 页面）
  const routeLessonId = route.params.id
  if (routeLessonId) {
    return Number(routeLessonId)
  }
  return undefined
})

// 解析 cellId：如果是 UUID 字符串，需要解析为数字 ID
// 注意：cell对象可能有两种格式：
// 1. 从数据库返回：cell.id 是数字
// 2. 从lesson.content返回：cell.id 可能是UUID字符串，但cell对象可能有_dbId字段存储数据库ID
const actualCellId = computed(() => {
  // 如果cell.id是数字，直接使用
  if (typeof props.cell.id === 'number') {
    return props.cell.id
  }
  
  // 如果是字符串，尝试转换
  const numericId = parseInt(props.cell.id as string)
  if (!isNaN(numericId)) {
    return numericId
  }
  
  // 如果是UUID，检查cell对象是否有_dbId字段（某些API可能返回）
  const cellObj = props.cell as any
  if (cellObj._dbId) {
    return cellObj._dbId
  }
  
  // 如果都没有，尝试使用cell.id（如果后端支持UUID的话）
  // 否则返回0，会导致API调用失败，但至少不会崩溃
  console.warn('⚠️ Cannot resolve cell ID to numeric ID, using 0 as fallback', {
    cellId: props.cell.id,
    cell: props.cell
  })
  return 0
})

const emit = defineEmits<{
  update: [cell: ActivityCell]
}>()

function handleUpdate(updatedCell: ActivityCell) {
  emit('update', updatedCell)
}

function handleSubmit(submissionData: any) {
  console.log('Activity submitted:', submissionData)
  // 提交逻辑将在 ActivityViewer 中处理
}
</script>

<style scoped>
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

