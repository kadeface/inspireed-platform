<template>
  <div class="relative my-2 group">
    <div class="flex items-center justify-center">
      <button
        @click="showMenu = !showMenu"
        class="flex items-center justify-center w-8 h-8 rounded-full border-2 border-dashed border-gray-300 text-gray-400 hover:border-blue-500 hover:text-blue-500 hover:bg-blue-50 transition-all opacity-0 group-hover:opacity-100"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
      </button>
    </div>

    <!-- 下拉菜单 -->
    <Transition name="menu">
      <div
        v-if="showMenu"
        v-click-outside="() => (showMenu = false)"
        class="absolute left-1/2 transform -translate-x-1/2 mt-2 w-56 rounded-lg shadow-lg bg-white border border-gray-200 z-10"
      >
        <div class="p-2">
          <button
            v-for="cellType in cellTypes"
            :key="cellType.type"
            @click="handleAddCell(cellType.type)"
            class="w-full flex items-center gap-3 px-3 py-2 text-left rounded-md hover:bg-blue-50 transition-colors"
          >
            <span class="text-xl">{{ cellType.icon }}</span>
            <div class="flex-1">
              <div class="text-sm font-medium text-gray-900">{{ cellType.name }}</div>
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
    description: '参数配置',
  },
  {
    type: CellType.SIM,
    name: '仿真单元',
    icon: '🎮',
    description: '3D仿真',
  },
  {
    type: CellType.QA,
    name: '问答单元',
    icon: '💬',
    description: 'AI问答',
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
    description: '竞技排行',
  },
]

function handleAddCell(cellType: CellType) {
  emit('add', cellType, props.insertIndex)
  showMenu.value = false
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

