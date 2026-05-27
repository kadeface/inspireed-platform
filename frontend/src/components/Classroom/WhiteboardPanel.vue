<template>
  <div
    v-if="visible"
    class="whiteboard-panel mt-3 rounded-lg border border-indigo-200 bg-indigo-50/80 p-3"
  >
    <h4 class="text-sm font-semibold text-indigo-900 mb-2">协作白板</h4>
    <div class="flex flex-wrap items-center gap-2 mb-2">
      <label class="text-xs text-gray-600">组数</label>
      <input
        v-model.number="groupCount"
        type="number"
        min="1"
        max="12"
        class="w-14 rounded border px-2 py-1 text-sm"
      />
      <button
        type="button"
        class="btn-sm rounded bg-indigo-600 text-white px-3 py-1 text-xs"
        :disabled="loading"
        @click="setupGroups"
      >
        随机分组
      </button>
    </div>
    <div class="flex flex-wrap gap-2">
      <button
        v-for="m in modes"
        :key="m.value"
        type="button"
        class="rounded px-3 py-1 text-xs border"
        :class="
          currentMode === m.value
            ? 'bg-indigo-600 text-white border-indigo-600'
            : 'bg-white text-indigo-800 border-indigo-200'
        "
        :disabled="loading || !cellId"
        @click="setMode(m.value)"
      >
        {{ m.label }}
      </button>
    </div>
    <p v-if="memberCount" class="text-xs text-gray-500 mt-2">
      已分配 {{ memberCount }} 名学生到 {{ groupCount }} 个组
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { whiteboardService } from '@/services/whiteboard'
import { getCellId, toNumericId } from '@/utils/cellId'
import type { Cell } from '@/types/cell'
import { CellType } from '@/types/cell'

const props = defineProps<{
  sessionId?: number
  currentCell?: Cell | null
}>()

const groupCount = ref(4)
const loading = ref(false)
const currentMode = ref<'setup' | 'collaborate' | 'locked'>('setup')
const memberCount = ref(0)

const visible = computed(
  () => props.currentCell?.type === CellType.WHITEBOARD && !!props.sessionId
)

const cellId = computed(() => {
  if (!props.currentCell) return null
  const id = getCellId(props.currentCell)
  return toNumericId(id) ?? toNumericId(props.currentCell.id)
})

const modes = [
  { value: 'setup' as const, label: '划分区域' },
  { value: 'collaborate' as const, label: '开始协作' },
  { value: 'locked' as const, label: '锁定全板' },
]

async function setupGroups() {
  if (!props.sessionId) return
  loading.value = true
  try {
    const res = await whiteboardService.setupGroups(
      props.sessionId,
      groupCount.value,
      true
    )
    memberCount.value = res.members.length
  } finally {
    loading.value = false
  }
}

async function setMode(mode: 'setup' | 'collaborate' | 'locked') {
  if (!props.sessionId || !cellId.value) return
  loading.value = true
  try {
    await whiteboardService.setMode(props.sessionId, cellId.value, mode)
    currentMode.value = mode
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.sessionId, visible.value],
  async () => {
    if (!props.sessionId || !visible.value) return
    try {
      const g = await whiteboardService.getGroups(props.sessionId)
      memberCount.value = g.members.length
      if (g.groups.length) groupCount.value = g.groups.length
    } catch {
      /* ignore */
    }
  },
  { immediate: true }
)
</script>
