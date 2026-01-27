<template>
  <div class="flowchart-cell-x6">
    <DiagramEditor
      :mode="mode"
      :content="diagramContent"
      :editable="editable"
      :show-sidebar="editable"
      :show-minimap="cell.config?.showMinimap ?? true"
      @update="handleUpdate"
      @mode-change="handleModeChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import DiagramEditor from '@/components/DiagramEditor/DiagramEditor.vue'
import { autoMigrateData, migrateX6ToVueFlow } from '@/utils/diagramMigration'
import type { FlowchartCell } from '@/types/cell'
import type { DiagramContent, DiagramMode } from '@/types/diagram'

interface Props {
  cell: FlowchartCell
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
})

const emit = defineEmits<{
  update: [cell: FlowchartCell]
}>()

// 当前模式（流程图或思维导图）
const mode = ref<DiagramMode>('flowchart')

// 缓存已迁移的内容，避免重复转换导致引用变化
let cachedContent: DiagramContent | null = null
let lastCellContentStr: string | null = null

// 将 FlowchartCell 的内容转换为 DiagramContent
const diagramContent = computed<DiagramContent>(() => {
  if (!props.cell.content) {
    return {
      cells: [],
      metadata: {
        mode: mode.value,
        updatedAt: Date.now(),
      },
    }
  }

  // 检查内容是否真的变了（避免引用变化导致的重复计算）
  const currentContentStr = JSON.stringify(props.cell.content)
  if (currentContentStr === lastCellContentStr && cachedContent) {
    return cachedContent
  }

  // 自动迁移旧数据格式
  const migrated = autoMigrateData(props.cell.content)
  
  // 缓存结果
  lastCellContentStr = currentContentStr
  cachedContent = migrated
  
  return migrated
})

function handleUpdate(content: DiagramContent) {
  const vueFlowContent = migrateX6ToVueFlow(content)

  emit('update', {
    ...props.cell,
    content: vueFlowContent,
  })
}

function handleModeChange(newMode: DiagramMode) {
  mode.value = newMode
}

// 监听 cell 内容变化，检测是否需要切换模式
watch(
  () => props.cell.content,
  (newContent) => {
    if (newContent && (newContent as any).metadata?.mode) {
      mode.value = (newContent as any).metadata.mode
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.flowchart-cell-x6 {
  @apply min-h-[500px] w-full;
  overflow: visible;
}

.flowchart-cell-x6 :deep(.diagram-editor) {
  min-height: 500px;
  height: 500px;
  width: 100%;
  overflow: visible;
}
</style>

