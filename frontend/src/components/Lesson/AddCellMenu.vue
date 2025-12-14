<template>
  <div class="relative my-4 flex justify-center">
    <button
      @click.stop="toggleMenu"
      @keydown.enter.stop.prevent="toggleMenu"
      type="button"
      class="flex h-12 w-12 items-center justify-center rounded-full border-2 border-dashed border-gray-300 bg-white text-gray-400 shadow-sm transition-all hover:-translate-y-0.5 hover:border-blue-500 hover:text-blue-500 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-400"
      aria-haspopup="true"
      :aria-expanded="showMenu"
      aria-label="插入单元"
    >
      <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
      </svg>
    </button>

    <!-- 下拉菜单 -->
    <Transition name="menu">
      <div
        v-if="showMenu"
        v-click-outside="() => (showMenu = false)"
        class="absolute left-1/2 z-50 mt-3 w-64 -translate-x-1/2 transform rounded-xl border border-gray-200 bg-white/95 shadow-2xl backdrop-blur-sm"
      >
        <div class="flex items-center justify-between px-4 py-2">
          <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">选择要插入的单元</span>
          <button
            class="rounded-full p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            type="button"
            @click="showMenu = false"
            aria-label="关闭插入菜单"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="max-h-72 space-y-1 overflow-y-auto px-3 pb-3">
          <button
            v-for="cellType in cellTypes"
            :key="cellType.type"
            @click="handleAddCell(cellType.type)"
            :disabled="isAdding"
            :class="[
              'flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm transition-all duration-200',
              isAdding && addingCellType === cellType.type
                ? 'bg-green-50 border border-green-200 text-green-700'
                : 'hover:bg-blue-50 hover:scale-[1.02] active:scale-[0.98]',
              isAdding ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'
            ]"
          >
            <div class="relative">
              <span class="text-xl">{{ cellType.icon }}</span>
              <!-- 加载动画 -->
              <div
                v-if="isAdding && addingCellType === cellType.type"
                class="absolute inset-0 flex items-center justify-center"
              >
                <div class="w-4 h-4 border-2 border-green-400 border-t-transparent rounded-full animate-spin"></div>
              </div>
            </div>
            <div class="flex-1 leading-tight">
              <div class="text-sm font-medium text-gray-800">
                {{ cellType.name }}
                <span v-if="isAdding && addingCellType === cellType.type" class="text-green-600 ml-1">✓</span>
              </div>
              <div class="text-xs text-gray-500">{{ cellType.description }}</div>
            </div>
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { CellType } from '../../types/cell'

interface Props {
  insertIndex: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  add: [cellType: CellType, index: number]
}>()

const showMenu = ref(false)
const isAdding = ref(false)
const addingCellType = ref<CellType | null>(null)

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
    icon: '🎯',
    description: '互动任务、课堂练习',
  },
  {
    type: CellType.SIM,
    name: '仿真单元',
    icon: '🎮',
    description: '3D仿真',
  },
  {
    type: CellType.CHART,
    name: '图表单元',
    icon: '📊',
    description: '数据可视化',
  },
  {
    type: CellType.FLOWCHART,
    name: '流程图单元',
    icon: '🗺️',
    description: '步骤梳理、思维导图',
  },
  {
    type: CellType.PARAM,
    name: '参数单元',
    icon: '⚙️',
    description: '参数配置',
  },
  {
    type: CellType.CONTEST,
    name: '竞赛单元',
    icon: '🏆',
    description: '积分竞赛、排行榜',
  },
  {
    type: CellType.BROWSER,
    name: '浏览器单元',
    icon: '🌐',
    description: '嵌入网页内容',
  },
  {
    type: CellType.INTERACTIVE,
    name: '交互式课件单元',
    icon: '🎮',
    description: 'HTML交互式课件',
  },
]

function toggleMenu() {
  showMenu.value = !showMenu.value
}

async function handleAddCell(cellType: CellType) {
  if (isAdding.value) return
  
  isAdding.value = true
  addingCellType.value = cellType
  
  try {
    // 添加短暂延迟以显示加载状态
    await new Promise(resolve => setTimeout(resolve, 300))
    
    emit('add', cellType, props.insertIndex)
    showMenu.value = false
  } finally {
    // 延迟重置状态以显示成功反馈
    setTimeout(() => {
      isAdding.value = false
      addingCellType.value = null
    }, 500)
  }
}

// 自定义指令：点击外部关闭
const vClickOutside = {
  mounted(el: HTMLElement & { clickOutsideEvent?: (event: Event) => void }, binding: any) {
    el.clickOutsideEvent = (event: Event) => {
      if (!(el === event.target || el.contains(event.target as Node))) {
        binding.value()
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el: HTMLElement & { clickOutsideEvent?: (event: Event) => void }) {
    if (el.clickOutsideEvent) {
      document.removeEventListener('click', el.clickOutsideEvent)
    }
  },
}
</script>

<style scoped>
.menu-enter-active,
.menu-leave-active {
  transition: all 0.2s ease;
}

.menu-enter-from,
.menu-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}
</style>

