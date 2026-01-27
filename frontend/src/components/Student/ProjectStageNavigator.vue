<template>
  <div class="flex flex-col gap-2 p-4 bg-white rounded-lg border border-gray-200 shadow-sm">
    <h3 class="text-sm font-semibold text-gray-700 mb-2">5E 阶段导航</h3>
    <div class="space-y-2">
      <button
        v-for="stage in stages"
        :key="stage.key"
        @click="handleStageChange(stage.key)"
        :class="[
          'w-full flex items-center justify-between p-3 rounded-lg transition-all duration-200',
          active_stage === stage.key
            ? stage.active_class
            : 'bg-gray-50 hover:bg-gray-100 border border-gray-200'
        ]"
      >
        <div class="flex items-center gap-3 flex-1">
          <div :class="[
            'w-10 h-10 rounded-lg flex items-center justify-center text-lg',
            active_stage === stage.key ? 'bg-white/20' : 'bg-white'
          ]">
            {{ stage.icon }}
          </div>
          <div class="flex-1 text-left">
            <div :class="[
              'font-medium',
              active_stage === stage.key ? 'text-white' : 'text-gray-700'
            ]">
              {{ stage.label }}
            </div>
            <div :class="[
              'text-xs mt-0.5',
              active_stage === stage.key ? 'text-white/80' : 'text-gray-500'
            ]">
              {{ stage.description }}
            </div>
          </div>
        </div>
        <div class="flex flex-col items-end gap-1">
          <div :class="[
            'text-xs font-bold',
            active_stage === stage.key ? 'text-white' : 'text-gray-600'
          ]">
            {{ completion[stage.key] }}%
          </div>
          <div class="w-16 bg-white/30 rounded-full h-1.5">
            <div
              :class="stage.progress_class"
              class="h-1.5 rounded-full transition-all duration-300"
              :style="{ width: `${completion[stage.key]}%` }"
            ></div>
          </div>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ProjectStage } from '../../types/student_project'

interface Props {
  active_stage: ProjectStage
  completion: {
    engage: number
    explore: number
    explain: number
    elaborate: number
    evaluate: number
  }
}

const props = defineProps<Props>()

const emit = defineEmits<{
  stage_change: [stage: ProjectStage]
}>()

const stages = [
  {
    key: 'engage' as ProjectStage,
    label: 'Engage',
    description: '参与投入',
    icon: '💡',
    active_class: 'bg-gradient-to-r from-orange-500 to-yellow-500 text-white shadow-lg border border-orange-300',
    progress_class: 'bg-white',
  },
  {
    key: 'explore' as ProjectStage,
    label: 'Explore',
    description: '探索发现',
    icon: '🧪',
    active_class: 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-lg border border-blue-300',
    progress_class: 'bg-white',
  },
  {
    key: 'explain' as ProjectStage,
    label: 'Explain',
    description: '解释建构',
    icon: '🧠',
    active_class: 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg border border-green-300',
    progress_class: 'bg-white',
  },
  {
    key: 'elaborate' as ProjectStage,
    label: 'Elaborate',
    description: '深化拓展',
    icon: '🚀',
    active_class: 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg border border-purple-300',
    progress_class: 'bg-white',
  },
  {
    key: 'evaluate' as ProjectStage,
    label: 'Evaluate',
    description: '评价反思',
    icon: '📊',
    active_class: 'bg-gradient-to-r from-red-500 to-rose-500 text-white shadow-lg border border-red-300',
    progress_class: 'bg-white',
  },
]

function handleStageChange(stage: ProjectStage) {
  emit('stage_change', stage)
}
</script>
