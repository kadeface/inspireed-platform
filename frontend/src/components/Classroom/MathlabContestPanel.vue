<template>
  <section
    v-if="sessionId && isMathlabSim && sessionTeaching"
    class="mathlab-contest-panel mt-3 rounded-lg border border-teal-200 bg-teal-50/80 p-3"
    data-testid="mathlab-contest-panel"
  >
    <div class="flex items-center justify-between gap-2 mb-2">
      <h4 class="text-sm font-semibold text-teal-900">🏁 MathLab 竞赛</h4>
      <span
        v-if="activeContest?.status === 'running'"
        class="text-xs px-2 py-0.5 rounded-full bg-teal-600 text-white"
      >
        进行中
      </span>
    </div>

    <template v-if="!activeContest || activeContest.status === 'ended'">
      <p class="text-xs text-teal-800 mb-2">
        默认任务：<code class="bg-white/70 px-1 rounded">{{ defaultTaskId || '（请在 SimCell 配置 mathlabTask）' }}</code>
      </p>
      <div class="flex flex-wrap gap-2 items-end">
        <label class="text-xs text-teal-900 flex flex-col gap-0.5">
          任务 ID
          <input
            v-model="startTaskId"
            type="text"
            class="text-sm border border-teal-300 rounded px-2 py-1 w-28"
            placeholder="p2t1"
          />
        </label>
        <label class="text-xs text-teal-900 flex flex-col gap-0.5">
          限时(秒)
          <input
            v-model.number="startTimeLimit"
            type="number"
            min="0"
            class="text-sm border border-teal-300 rounded px-2 py-1 w-20"
            placeholder="无"
          />
        </label>
        <button
          type="button"
          class="text-sm px-3 py-1.5 rounded bg-teal-600 text-white hover:bg-teal-700 disabled:opacity-50"
          :disabled="loading || !cellId || !startTaskId"
          @click="handleStart"
        >
          开始竞赛
        </button>
      </div>
      <p v-if="error" class="text-xs text-red-600 mt-1">{{ error }}</p>
    </template>

    <template v-else>
      <p class="text-xs text-teal-900 mb-1">
        任务 <strong>{{ activeContest.taskId }}</strong>
        · 已提交 {{ leaderboard?.submittedCount ?? 0 }}/{{ leaderboard?.totalStudents ?? '—' }}
      </p>
      <div class="flex flex-wrap gap-2 mb-2">
        <input
          v-model="changeTaskId"
          type="text"
          class="text-sm border border-teal-300 rounded px-2 py-1 w-24"
          :placeholder="activeContest.taskId"
        />
        <button
          type="button"
          class="text-xs px-2 py-1 rounded border border-teal-500 text-teal-800 hover:bg-teal-100"
          :disabled="loading || !changeTaskId"
          @click="handleChangeTask"
        >
          换题
        </button>
        <button
          type="button"
          class="text-xs px-2 py-1 rounded bg-red-600 text-white hover:bg-red-700"
          :disabled="loading"
          @click="handleEnd"
        >
          结束竞赛
        </button>
        <button
          type="button"
          class="text-xs px-2 py-1 rounded border border-teal-400 text-teal-800"
          :disabled="loading"
          @click="refreshLeaderboard(activeContest.id)"
        >
          刷新排行
        </button>
      </div>

      <div v-if="leaderboard?.submissions?.length" class="max-h-40 overflow-y-auto">
        <table class="w-full text-xs border-collapse">
          <thead>
            <tr class="text-left text-teal-800 border-b border-teal-200">
              <th class="py-1 pr-2">#</th>
              <th class="py-1 pr-2">学生</th>
              <th class="py-1 pr-2 text-right">分</th>
              <th class="py-1">达标</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in leaderboard.submissions"
              :key="row.id"
              class="border-b border-teal-100/80"
            >
              <td class="py-1 pr-2">{{ row.rank }}</td>
              <td class="py-1 pr-2 truncate max-w-[6rem]" :title="row.studentName">
                {{ row.studentName || row.studentId }}
              </td>
              <td class="py-1 pr-2 text-right">
                <input
                  type="number"
                  min="0"
                  max="100"
                  class="w-12 text-right border rounded px-0.5"
                  :value="row.finalScore"
                  @change="(e) => handleScoreChange(row, e)"
                />
              </td>
              <td class="py-1">{{ row.passed ? '✓' : '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="text-xs text-teal-700">暂无提交</p>
    </template>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { CellType, type Cell } from '@/types/cell'
import { mathlabContestService } from '@/services/mathlabContest'
import { useMathlabContestState } from '@/composables/useMathlabContest'
import { getCellId as getCellIdUtil } from '@/utils/cellId'

const props = defineProps<{
  currentCell: Cell | null
  sessionId?: number
  sessionStatus?: string
}>()

const { activeContest, leaderboard, loading, error, refreshActive, refreshLeaderboard } =
  useMathlabContestState()

const sessionTeaching = computed(
  () => props.sessionStatus === 'teaching' || props.sessionStatus === 'TEACHING'
)

const isMathlabSim = computed(() => {
  const c = props.currentCell
  if (!c || c.type !== CellType.SIM) return false
  const content = c.content as { type?: string; mathlabTask?: string; mathlabSim?: string }
  return content?.type === 'mathlab'
})

const defaultTaskId = computed(() => {
  if (!props.currentCell || props.currentCell.type !== CellType.SIM) return ''
  const content = props.currentCell.content as { mathlabTask?: string }
  return content?.mathlabTask || ''
})

const cellId = computed(() => {
  if (!props.currentCell) return undefined
  const id = getCellIdUtil(props.currentCell as Parameters<typeof getCellIdUtil>[0])
  if (typeof id === 'number' && !Number.isNaN(id)) return id
  if (typeof id === 'string') {
    const n = parseInt(id, 10)
    if (!Number.isNaN(n)) return n
  }
  return undefined
})

const startTaskId = ref('')
const startTimeLimit = ref<number | undefined>(undefined)
const changeTaskId = ref('')

watch(
  defaultTaskId,
  (t) => {
    if (t && !startTaskId.value) startTaskId.value = t
  },
  { immediate: true }
)

watch(
  () => props.sessionId,
  (sid) => {
    if (sid) refreshActive()
  },
  { immediate: true }
)

async function handleStart() {
  if (!props.sessionId || !cellId.value || !startTaskId.value) return
  loading.value = true
  error.value = null
  try {
    activeContest.value = await mathlabContestService.start(props.sessionId, {
      cellId: cellId.value,
      taskId: startTaskId.value,
      timeLimitSec: startTimeLimit.value || undefined,
    })
    await refreshLeaderboard(activeContest.value.id)
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '开赛失败'
  } finally {
    loading.value = false
  }
}

async function handleEnd() {
  if (!activeContest.value) return
  loading.value = true
  try {
    activeContest.value = await mathlabContestService.end(activeContest.value.id)
  } finally {
    loading.value = false
  }
}

async function handleChangeTask() {
  if (!activeContest.value || !changeTaskId.value) return
  loading.value = true
  try {
    activeContest.value = await mathlabContestService.updateTask(
      activeContest.value.id,
      changeTaskId.value
    )
    changeTaskId.value = ''
  } finally {
    loading.value = false
  }
}

async function handleScoreChange(
  row: { id: number; passed: boolean },
  e: Event
) {
  const v = Number((e.target as HTMLInputElement).value)
  if (Number.isNaN(v)) return
  loading.value = true
  try {
    await mathlabContestService.updateScore(row.id, v, v >= (activeContest.value?.passThreshold ?? 85))
    if (activeContest.value) await refreshLeaderboard(activeContest.value.id)
  } finally {
    loading.value = false
  }
}

defineExpose({ refreshActive })
</script>

<style scoped>
.mathlab-contest-panel code {
  font-size: 0.75rem;
}
</style>
