<template>
  <div
    :class="[
      'bg-white border-r border-gray-200 transition-all duration-300',
      collapsed ? 'w-16' : 'w-64',
    ]"
  >
    <!-- 工具栏标题 -->
    <div class="p-4 border-b border-gray-200 flex items-center justify-between">
      <h3 v-if="!collapsed" class="text-sm font-semibold text-gray-900">添加单元</h3>
      <button
        @click="$emit('toggle-collapsed')"
        class="p-1 rounded hover:bg-gray-100 text-gray-500"
        :title="collapsed ? '展开' : '收起'"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            v-if="collapsed"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 5l7 7-7 7"
          />
          <path
            v-else
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M15 19l-7-7 7-7"
          />
        </svg>
      </button>
    </div>

    <!-- Cell 类型列表 -->
    <div class="p-2 space-y-2 overflow-y-auto" style="max-height: calc(100vh - 180px)">
      <button
        v-for="cellType in cellTypes"
        :key="cellType.type"
        @click="handleAddCell(cellType.type)"
        :class="[
          'w-full text-left rounded-lg transition-colors',
          collapsed ? 'p-2' : 'p-3',
          'hover:bg-blue-50 border-2 border-transparent hover:border-blue-200',
        ]"
        :title="collapsed ? cellType.name : ''"
      >
        <div :class="['flex items-center', collapsed ? 'justify-center' : 'gap-3']">
          <span class="text-2xl">{{ cellType.icon }}</span>
          <div v-if="!collapsed" class="flex-1">
            <div class="text-sm font-medium text-gray-900">{{ cellType.name }}</div>
            <div class="text-xs text-gray-500">{{ cellType.description }}</div>
          </div>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { CellType } from '../../types/cell'

interface Props {
  collapsed?: boolean
}

withDefaults(defineProps<Props>(), {
  collapsed: false,
})

const emit = defineEmits<{
  addCell: [cellType: CellType]
  'toggle-collapsed': []
}>()

// Cell 类型定义
const cellTypes = [
  {
    type: CellType.TEXT,
    name: '文本单元',
    icon: '📝',
    description: '富文本编辑器',
  },
  {
    type: CellType.CODE,
    name: '代码单元',
    icon: '💻',
    description: 'Python/JavaScript/HTML',
  },
  {
    type: CellType.PARAM,
    name: '参数单元',
    icon: '⚙️',
    description: '参数配置表单',
  },
  {
    type: CellType.SIM,
    name: '仿真单元',
    icon: '🎮',
    description: '3D仿真/物理引擎',
  },
  {
    type: CellType.QA,
    name: '问答单元',
    icon: '💬',
    description: 'AI问答交互',
  },
  {
    type: CellType.CHART,
    name: '图表单元',
    icon: '📊',
    description: '数据可视化',
  },
  {
    type: CellType.CONTEST,
    name: '竞赛单元',
    icon: '🏆',
    description: '竞技排行榜',
  },
]

function handleAddCell(cellType: CellType) {
  emit('addCell', cellType)
}
</script>

