<template>
  <div class="whiteboard-cell">
    <div v-if="editable && !sessionId" class="whiteboard-editor-hint">
      <p class="text-sm text-gray-600">
        协作白板：课堂开始后，学生将在教师划定的小组区域内同步绘制。可在预览中体验工具。
      </p>
      <iframe
        ref="iframeRef"
        class="whiteboard-iframe"
        :src="previewSrc"
        title="白板预览"
      />
    </div>
    <iframe
      v-else
      ref="iframeRef"
      class="whiteboard-iframe"
      :src="iframeSrc"
      title="协作白板"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useUserStore } from '@/store/user'
import type { WhiteboardCell } from '@/types/cell'
import { whiteboardService } from '@/services/whiteboard'
import {
  sendWhiteboardOp,
  subscribeWhiteboardCell,
} from '@/composables/useWhiteboard'
import { getCellId, toNumericId } from '@/utils/cellId'

interface Props {
  cell: WhiteboardCell
  editable?: boolean
  sessionId?: number
  lessonId?: number
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
})

const emit = defineEmits<{ update: [cell: WhiteboardCell] }>()

const iframeRef = ref<HTMLIFrameElement | null>(null)
const userStore = useUserStore()
const myGroupIndex = ref(0)
const boardMode = ref<'setup' | 'collaborate' | 'locked'>('setup')

const numericCellId = computed(() => {
  const id = getCellId(props.cell)
  return toNumericId(id) ?? toNumericId(props.cell.id) ?? null
})

const role = computed(() =>
  props.editable || userStore.user?.role === 'teacher' ? 'teacher' : 'student'
)

const previewSrc = computed(() => {
  const base = '/whiteboard/index.html'
  return `${base}?role=teacher&embedded=0`
})

const iframeSrc = computed(() => {
  const base = '/whiteboard/index.html'
  const q = new URLSearchParams({
    role: role.value,
    embedded: '1',
  })
  if (myGroupIndex.value) q.set('groupIndex', String(myGroupIndex.value))
  return `${base}?${q.toString()}`
})

function postToFrame(type: string, data: Record<string, unknown>) {
  const win = iframeRef.value?.contentWindow
  if (!win) return
  win.postMessage({ source: 'inspireed', type, data }, '*')
}

function buildOpFromLocal(data: Record<string, unknown>) {
  return data.op as Record<string, unknown>
}

async function loadGroupsAndState() {
  if (!props.sessionId || !numericCellId.value) return
  try {
    const groups = await whiteboardService.getGroups(props.sessionId)
    const me = userStore.user?.id
    const member = groups.members.find((m) => m.user_id === me)
    myGroupIndex.value = member?.group_index ?? 0
    const state = await whiteboardService.getState(props.sessionId, numericCellId.value)
    boardMode.value = (state.document.mode as typeof boardMode.value) || 'setup'
    postToFrame('WB_INIT', {
      role: role.value,
      groupIndex: myGroupIndex.value,
      mode: boardMode.value,
      document: state.document,
      userId: userStore.user?.id,
      userName: userStore.user?.full_name || userStore.user?.username,
    })
  } catch (e) {
    console.error('白板状态加载失败', e)
  }
}

let unsubWs: (() => void) | null = null
let unsubMessage: (() => void) | null = null

function onWindowMessage(event: MessageEvent) {
  const msg = event.data
  if (!msg || msg.source !== 'whiteboard') return
  if (!props.sessionId || !numericCellId.value) return

  if (msg.type === 'WB_READY') {
    loadGroupsAndState()
    return
  }

  if (msg.type === 'WB_OP_LOCAL') {
    const op = buildOpFromLocal(msg.data || {})
    sendWhiteboardOp(props.sessionId, numericCellId.value, op)
  }
}

onMounted(() => {
  window.addEventListener('message', onWindowMessage)
  unsubMessage = () => window.removeEventListener('message', onWindowMessage)

  if (props.sessionId && numericCellId.value) {
    unsubWs = subscribeWhiteboardCell(
      props.sessionId,
      numericCellId.value,
      (type, data) => {
        if (type === 'whiteboard.sync') {
          postToFrame('WB_FULL_SYNC', {
            document: data.document,
            version: data.version,
          })
          if (data.document && typeof data.document === 'object') {
            const m = (data.document as { mode?: string }).mode
            if (m === 'setup' || m === 'collaborate' || m === 'locked') {
              boardMode.value = m
            }
          }
        } else if (type === 'whiteboard.op') {
          postToFrame('WB_REMOTE_OP', { op: data.op, version: data.version })
        } else if (type === 'whiteboard.mode') {
          boardMode.value = (data.mode as typeof boardMode.value) || boardMode.value
          postToFrame('WB_MODE', { mode: data.mode })
        } else if (type === 'whiteboard.groups') {
          const me = userStore.user?.id
          const members = (data.members as Array<{ user_id: number; group_index: number }>) || []
          const member = members.find((m) => m.user_id === me)
          if (member) {
            myGroupIndex.value = member.group_index
            postToFrame('WB_GROUPS', { groupIndex: member.group_index })
          }
        }
      }
    )
  }
})

onUnmounted(() => {
  unsubWs?.()
  unsubMessage?.()
})

watch(
  () => [props.sessionId, numericCellId.value],
  () => {
    if (props.sessionId && numericCellId.value) {
      loadGroupsAndState()
    }
  }
)
</script>

<style scoped>
.whiteboard-cell {
  width: 100%;
  min-height: 520px;
}
.whiteboard-iframe {
  width: 100%;
  height: min(72vh, 720px);
  border: none;
  border-radius: 8px;
  background: #0f1419;
}
.whiteboard-editor-hint {
  padding: 12px 0;
}
</style>
