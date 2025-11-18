<template>
  <div 
    :class="[
      'cell-wrapper',
      'relative transition-all duration-300',
      {
        'locked': isLocked,
        'mastered': isMastered,
        'in-progress': isInProgress
      }
    ]"
  >
    <!-- 锁定状态遮罩 -->
    <div 
      v-if="isLocked" 
      class="absolute inset-0 bg-gray-900 bg-opacity-50 rounded-lg z-10 flex items-center justify-center backdrop-blur-sm"
    >
      <div class="bg-white rounded-lg p-6 max-w-md mx-4 shadow-2xl">
        <div class="text-center">
          <svg class="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">
            🔒 该单元暂未解锁
          </h3>
          <p class="text-sm text-gray-600 mb-4">
            请先完成以下前置单元：
          </p>
          <ul class="text-left space-y-2 mb-4">
            <li 
              v-for="prereq in prerequisiteNames" 
              :key="prereq.id"
              class="flex items-center text-sm"
            >
              <svg 
                v-if="prereq.completed" 
                class="w-5 h-5 text-green-500 mr-2 flex-shrink-0" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <svg 
                v-else 
                class="w-5 h-5 text-gray-400 mr-2 flex-shrink-0" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span :class="prereq.completed ? 'text-gray-700 line-through' : 'text-gray-900 font-medium'">
                {{ prereq.title }}
              </span>
            </li>
          </ul>
          <p class="text-xs text-gray-500">
            💡 按照学习路径逐步前进，学习效果更佳
          </p>
        </div>
      </div>
    </div>

    <!-- 主体内容区 -->
    <div :class="{ 'pointer-events-none opacity-30': isLocked }">
      <!-- Cell 头部信息栏 -->
      <div class="flex items-center justify-between mb-3 p-3 bg-gray-50 rounded-t-lg border-b-2 border-gray-200">
        <div class="flex items-center gap-3">
          <!-- 认知层级标签 -->
          <span 
            v-if="cell.cognitive_level"
            :class="getCognitiveLevelClass(cell.cognitive_level)"
            class="text-xs px-3 py-1 rounded-full font-medium"
          >
            {{ getCognitiveLevelText(cell.cognitive_level) }}
          </span>
          
          <!-- 单元标题 -->
          <div>
            <span class="text-sm font-medium text-gray-500">单元 {{ cellIndex + 1 }}</span>
            <span v-if="cell.title" class="text-sm text-gray-700 ml-2">- {{ cell.title }}</span>
          </div>
        </div>

        <!-- 掌握度状态 -->
        <div class="flex items-center gap-2">
          <!-- 掌握度百分比 -->
          <div class="text-right mr-2">
            <div class="text-xs text-gray-500">掌握度</div>
            <div 
              :class="[
                'text-sm font-bold',
                masteryScore >= 80 ? 'text-green-600' : 
                masteryScore >= 60 ? 'text-yellow-600' : 'text-gray-600'
              ]"
            >
              {{ masteryScore }}%
            </div>
          </div>

          <!-- 完成状态按钮 -->
          <button
            v-if="!isCompleted && masteryScore >= 80"
            @click="markAsCompleted"
            class="text-xs px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
          >
            标记完成
          </button>
          <div 
            v-else-if="isCompleted"
            class="flex items-center gap-1 text-green-600 text-xs font-medium"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            已完成
          </div>
        </div>
      </div>

      <!-- 掌握度进度条 -->
      <div class="px-3 pb-3 bg-gray-50">
        <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
          <div
            class="h-2 transition-all duration-500 rounded-full"
            :class="getMasteryBarClass(masteryScore)"
            :style="{ width: `${masteryScore}%` }"
          >
            <div class="h-full w-full opacity-50 bg-white animate-pulse"></div>
          </div>
        </div>
        
        <!-- 掌握度提示 -->
        <div v-if="masteryScore < 80 && masteryScore > 0" class="mt-2 text-xs text-gray-600 flex items-center gap-1">
          <svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>建议达到 80% 掌握度后再继续下一单元</span>
        </div>
      </div>

      <!-- Cell 实际内容 -->
      <div class="p-6 bg-white rounded-b-lg border border-gray-200">
        <slot></slot>
      </div>
    </div>

    <!-- 达标徽章（Gamification） -->
    <transition name="badge">
      <div 
        v-if="isMastered && showBadge" 
        class="absolute -top-3 -right-3 z-20"
      >
        <div class="relative">
          <div class="bg-yellow-400 text-yellow-900 rounded-full p-2 shadow-lg animate-bounce">
            <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </div>
          <div class="absolute top-full left-1/2 transform -translate-x-1/2 mt-1 whitespace-nowrap bg-yellow-900 text-white text-xs px-2 py-1 rounded shadow-lg">
            已掌握！
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import type { Cell } from '@/types/cell'

interface Props {
  cell: Cell
  cellIndex: number
  allCells: Cell[]
  completedCellIds: Set<string>
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'complete', cellId: string): void
}>()

// 状态
const masteryScore = ref(0)
const isCompleted = ref(false)
const showBadge = ref(false)

// 计算属性
const isLocked = computed(() => {
  if (!props.cell.prerequisite_cells || props.cell.prerequisite_cells.length === 0) {
    return false
  }
  
  // 检查所有前置Cell是否都已完成
  return props.cell.prerequisite_cells.some((prereqId: string) => {
    return !props.completedCellIds.has(prereqId)
  })
})

const isMastered = computed(() => masteryScore.value >= 80)
const isInProgress = computed(() => masteryScore.value > 0 && masteryScore.value < 80)

const prerequisiteNames = computed(() => {
  if (!props.cell.prerequisite_cells) return []
  
  return props.cell.prerequisite_cells.map((prereqId: string) => {
    const prereqCell = props.allCells.find(c => c.id === prereqId)
    return {
      id: prereqId,
      title: prereqCell?.title || `单元 ${prereqId}`,
      completed: props.completedCellIds.has(prereqId)
    }
  })
})

// 方法
const getCognitiveLevelText = (level: string): string => {
  const labels: Record<string, string> = {
    'remember': '📝 记忆',
    'understand': '💡 理解',
    'apply': '🔧 应用',
    'analyze': '🔍 分析',
    'evaluate': '⚖️ 评价',
    'create': '🎨 创造'
  }
  return labels[level] || level
}

const getCognitiveLevelClass = (level: string): string => {
  const classes: Record<string, string> = {
    'remember': 'bg-blue-100 text-blue-700',
    'understand': 'bg-green-100 text-green-700',
    'apply': 'bg-yellow-100 text-yellow-700',
    'analyze': 'bg-purple-100 text-purple-700',
    'evaluate': 'bg-orange-100 text-orange-700',
    'create': 'bg-pink-100 text-pink-700'
  }
  return classes[level] || 'bg-gray-100 text-gray-700'
}

const getMasteryBarClass = (score: number): string => {
  if (score >= 80) return 'bg-gradient-to-r from-green-500 to-green-600'
  if (score >= 60) return 'bg-gradient-to-r from-yellow-500 to-yellow-600'
  return 'bg-gradient-to-r from-gray-400 to-gray-500'
}

const markAsCompleted = () => {
  if (masteryScore.value >= 80) {
    isCompleted.value = true
    emit('complete', String(props.cell.id))
    
    // 显示达标徽章动画
    showBadge.value = true
    setTimeout(() => {
      showBadge.value = false
    }, 3000)
  }
}

const loadMasteryScore = () => {
  // 从 localStorage 加载掌握度
  const key = `cell_${props.cell.id}_mastery`
  const saved = localStorage.getItem(key)
  if (saved) {
    masteryScore.value = parseInt(saved, 10)
  }
}

const saveMasteryScore = () => {
  const key = `cell_${props.cell.id}_mastery`
  localStorage.setItem(key, masteryScore.value.toString())
}

// 监听完成状态
watch(() => props.completedCellIds.has(String(props.cell.id)), (completed) => {
  isCompleted.value = completed
})

// 生命周期
onMounted(() => {
  loadMasteryScore()
  isCompleted.value = props.completedCellIds.has(String(props.cell.id))
})

// 暴露方法供父组件调用
defineExpose({
  updateMasteryScore(score: number) {
    masteryScore.value = Math.max(0, Math.min(100, score))
    saveMasteryScore()
  },
  getMasteryScore() {
    return masteryScore.value
  }
})
</script>

<style scoped>
.cell-wrapper {
  @apply rounded-lg shadow-sm transition-all;
}

.cell-wrapper:hover:not(.locked) {
  @apply shadow-md;
}

.cell-wrapper.locked {
  @apply relative;
}

.cell-wrapper.mastered {
  @apply ring-2 ring-green-400 shadow-lg;
}

.cell-wrapper.in-progress {
  @apply ring-2 ring-yellow-400;
}

/* 徽章动画 */
.badge-enter-active {
  animation: badge-in 0.5s ease-out;
}

.badge-leave-active {
  animation: badge-out 0.3s ease-in;
}

@keyframes badge-in {
  from {
    transform: scale(0) rotate(-180deg);
    opacity: 0;
  }
  to {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
}

@keyframes badge-out {
  from {
    transform: scale(1);
    opacity: 1;
  }
  to {
    transform: scale(0);
    opacity: 0;
  }
}
</style>

