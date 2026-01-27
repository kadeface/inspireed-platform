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
        class="absolute left-1/2 z-50 mb-3 -translate-x-1/2 bottom-full transform rounded-2xl border border-gray-200 bg-white/95 shadow-xl backdrop-blur-sm origin-bottom"
      >
        <div
          class="flex items-center gap-1 p-2 overflow-x-auto max-w-[90vw] lg:max-w-4xl no-scrollbar"
        >
          <button
            v-for="cellType in cellTypes"
            :key="cellType.type"
            @click="handleAddCell(cellType.type)"
            :disabled="isAdding"
            :title="cellType.description"
            :class="[
              'flex flex-col items-center justify-center gap-1.5 rounded-xl p-3 min-w-[88px] w-[88px] h-[88px] transition-all duration-200 flex-shrink-0',
              isAdding && addingCellType === cellType.type
                ? 'bg-green-50 border border-green-200 text-green-700'
                : 'hover:bg-blue-50 hover:scale-105 active:scale-95 border border-transparent hover:border-blue-100 text-gray-700 hover:text-blue-600',
              isAdding ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer',
            ]"
          >
            <div class="relative">
              <span class="text-3xl filter drop-shadow-sm">{{ cellType.icon }}</span>
              <!-- 加载动画 -->
              <div
                v-if="isAdding && addingCellType === cellType.type"
                class="absolute inset-0 flex items-center justify-center bg-white/50 rounded-full"
              >
                <div
                  class="w-5 h-5 border-2 border-green-500 border-t-transparent rounded-full animate-spin"
                ></div>
              </div>
            </div>
            <div class="text-xs font-medium truncate w-full text-center leading-tight">
              {{ cellType.name.replace('单元', '') }}
            </div>
          </button>
        </div>

        <!-- 底部小箭头 -->
        <div
          class="absolute -bottom-2 left-1/2 -translate-x-1/2 w-4 h-4 bg-white border-b border-r border-gray-200 transform rotate-45"
        ></div>
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
    await new Promise((resolve) => setTimeout(resolve, 300))

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
  transform: translateX(-50%) translateY(10px) scale(0.95);
}

/* 隐藏滚动条 */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
