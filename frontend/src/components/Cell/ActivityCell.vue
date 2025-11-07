<template>
  <div class="activity-cell">
    <!-- 教师编辑模式 -->
    <div v-if="editable" class="activity-editor">
      <ActivityCellEditor
        :cell="cell"
        @update="handleUpdate"
      />
    </div>

    <!-- 学生查看/答题模式 -->
    <div v-else class="activity-viewer">
      <ActivityViewer
        :cell="cell"
        @submit="handleSubmit"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ActivityCell } from '../../types/cell'
import ActivityCellEditor from '../Activity/ActivityCellEditor.vue'
import ActivityViewer from '../Activity/ActivityViewer.vue'

interface Props {
  cell: ActivityCell
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
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
</style>

