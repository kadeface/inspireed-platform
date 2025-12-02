<template>
  <div
    ref="rootRef"
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
    <div ref="scrollContainerRef" class="p-2 space-y-2 overflow-y-auto" style="max-height: calc(100vh - 80px)">
      <button
        v-for="cellType in cellTypes"
        :key="cellType.type"
        @click="handleAddCell(cellType.type)"
        :disabled="isAdding"
        :class="[
          'w-full text-left rounded-lg transition-all duration-200',
          collapsed ? 'p-2' : 'p-3',
          isAdding && addingCellType === cellType.type
            ? 'bg-green-50 border-2 border-green-200 text-green-700'
            : 'hover:bg-blue-50 border-2 border-transparent hover:border-blue-200 hover:scale-[1.02] active:scale-[0.98]',
          isAdding ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'
        ]"
        :title="collapsed ? cellType.name : ''"
      >
        <div :class="['flex items-center', collapsed ? 'justify-center' : 'gap-3']">
          <div class="relative">
            <span class="text-2xl">{{ cellType.icon }}</span>
            <!-- 加载动画 -->
            <div
              v-if="isAdding && addingCellType === cellType.type"
              class="absolute inset-0 flex items-center justify-center"
            >
              <div class="w-4 h-4 border-2 border-green-400 border-t-transparent rounded-full animate-spin"></div>
            </div>
          </div>
          <div v-if="!collapsed" class="flex-1">
            <div class="text-sm font-medium">
              {{ cellType.name }}
              <span v-if="isAdding && addingCellType === cellType.type" class="text-green-600 ml-1">✓</span>
            </div>
            <div class="text-xs text-gray-500">{{ cellType.description }}</div>
          </div>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
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

const isAdding = ref(false)
const addingCellType = ref<CellType | null>(null)
const scrollContainerRef = ref<HTMLElement | null>(null)
const rootRef = ref<HTMLElement | null>(null)

// 暴露滚动容器引用给父组件
defineExpose({
  scrollContainer: scrollContainerRef,
  getScrollContainer: () => scrollContainerRef.value,
  rootElement: rootRef,
})

// Cell 类型定义
const cellTypes = [
  {
    type: CellType.TEXT,
    name: '文本单元',
    icon: '📝',
    description: '富文本编辑器',
  },
  {
    type: CellType.VIDEO,
    name: '视频单元',
    icon: '🎥',
    description: '视频教学内容',
  },
  {
    type: CellType.CODE,
    name: '代码单元',
    icon: '💻',
    description: 'Python/JavaScript/HTML',
  },
  {
    type: CellType.ACTIVITY,
    name: '活动单元',
    icon: '✅',
    description: '测验/问卷/作业/评价',
  },
  {
    type: CellType.SIM,
    name: '仿真单元',
    icon: '🎮',
    description: '3D仿真/物理引擎',
  },
  {
    type: CellType.FLOWCHART,
    name: '流程图单元',
    icon: '📊',
    description: '流程图/思维导图',
  },
  {
    type: CellType.CHART,
    name: '图表单元',
    icon: '📈',
    description: '数据可视化',
  },
  {
    type: CellType.CONTEST,
    name: '竞赛单元',
    icon: '🏆',
    description: '竞技排行榜',
  },
  {
    type: CellType.PARAM,
    name: '参数单元',
    icon: '⚙️',
    description: '参数配置表单',
  },
  {
    type: CellType.BROWSER,
    name: '浏览器单元',
    icon: '🌐',
    description: '嵌入网页内容',
  },
]

async function handleAddCell(cellType: CellType) {
  if (isAdding.value) return
  
  isAdding.value = true
  addingCellType.value = cellType
  
  try {
    // 添加短暂延迟以显示加载状态
    await new Promise(resolve => setTimeout(resolve, 300))
    
    emit('addCell', cellType)
  } finally {
    // 延迟重置状态以显示成功反馈
    setTimeout(() => {
      isAdding.value = false
      addingCellType.value = null
    }, 500)
  }
}
</script>

