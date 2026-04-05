<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
    <!-- 输入接入码 -->
    <div v-if="!sessionInfo" class="w-full max-w-md">
      <div class="bg-white rounded-2xl shadow-xl p-8">
        <div class="text-center mb-6">
          <h1 class="text-2xl font-bold text-gray-800">InspireEd</h1>
          <p class="text-gray-500 mt-1">访客观摩模式</p>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              请输入课堂接入码
            </label>
            <input
              v-model="accessCode"
              type="text"
              maxlength="6"
              placeholder="6位接入码"
              class="w-full px-4 py-3 text-center text-2xl font-mono tracking-[0.5em] border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none uppercase"
              @keyup.enter="lookupSession"
              autofocus
            />
          </div>

          <div v-if="error" class="text-sm text-red-600 text-center">
            {{ error }}
          </div>

          <button
            @click="lookupSession"
            :disabled="accessCode.length < 6 || loading"
            class="w-full py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {{ loading ? '查找中...' : '进入课堂' }}
          </button>
        </div>

        <div class="mt-6 text-center">
          <router-link to="/login" class="text-sm text-blue-600 hover:underline">
            已有账号？去登录
          </router-link>
        </div>
      </div>
    </div>

    <!-- 课堂观摩界面 -->
    <div v-else class="w-full max-w-4xl">
      <div class="bg-white rounded-2xl shadow-xl overflow-hidden">
        <!-- 顶部信息栏 -->
        <div class="bg-blue-600 text-white px-6 py-4">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-lg font-bold">{{ sessionInfo.lessonTitle || '课堂观摩' }}</h1>
              <div class="text-blue-100 text-sm mt-1">
                {{ sessionInfo.teacherName }} · {{ sessionInfo.classroomName }}
              </div>
            </div>
            <div class="flex items-center gap-3">
              <span
                class="px-2 py-1 text-xs rounded-full"
                :class="sessionInfo.status === 'TEACHING' ? 'bg-green-500' : 'bg-yellow-500'"
              >
                {{ sessionInfo.status === 'TEACHING' ? '上课中' : '准备中' }}
              </span>
              <button
                @click="exitGuest"
                class="text-blue-100 hover:text-white text-sm underline"
              >
                退出
              </button>
            </div>
          </div>
        </div>

        <!-- 访客提示 -->
        <div class="bg-yellow-50 border-b border-yellow-100 px-6 py-2 text-sm text-yellow-700">
          访客观摩模式 — 您正在只读观摩此课堂，无法提交活动或参与互动
        </div>

        <!-- Cell 内容区域 -->
        <div class="p-6">
          <div v-if="cellsLoading" class="text-center py-12 text-gray-400">
            加载课堂内容中...
          </div>

          <div v-else-if="cells.length === 0" class="text-center py-12 text-gray-400">
            <div class="text-4xl mb-4">📚</div>
            <p>{{ sessionInfo.status === 'TEACHING' ? '等待教师展示内容...' : '课堂尚未开始，请稍候' }}</p>
          </div>

          <div v-else class="space-y-6">
            <div
              v-for="cell in cells"
              :key="cell.id"
              class="border border-gray-200 rounded-xl p-5 transition-all"
              :class="{ 'ring-2 ring-blue-400 bg-blue-50/30': cell.id === sessionInfo.currentCellId }"
            >
              <div class="flex items-center gap-2 mb-3">
                <span class="px-2 py-0.5 text-xs rounded bg-gray-100 text-gray-600 font-mono">
                  {{ cell.cell_type }}
                </span>
                <span v-if="cell.title" class="text-sm font-medium text-gray-700">
                  {{ cell.title }}
                </span>
              </div>

              <!-- TEXT cell -->
              <div
                v-if="cell.cell_type === 'TEXT'"
                class="prose prose-sm max-w-none"
                v-html="cell.content?.html || cell.content?.text || ''"
              />

              <!-- VIDEO cell -->
              <div v-else-if="cell.cell_type === 'VIDEO'" class="text-gray-500 text-sm">
                <video
                  v-if="cell.content?.url"
                  :src="cell.content.url"
                  controls
                  class="w-full rounded-lg"
                />
                <p v-else>视频内容</p>
              </div>

              <!-- CODE cell -->
              <div v-else-if="cell.cell_type === 'CODE'" class="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                <pre>{{ cell.content?.code || cell.content?.source || '' }}</pre>
              </div>

              <!-- ACTIVITY cell — 访客只读 -->
              <div v-else-if="cell.cell_type === 'ACTIVITY'" class="bg-gray-50 p-4 rounded-lg text-gray-500 text-sm">
                <p>教学活动（访客模式下不可参与）</p>
              </div>

              <!-- 其他类型 -->
              <div v-else class="text-gray-500 text-sm">
                {{ cell.cell_type }} 内容
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import classroomSessionService from '@/services/classroomSession'
import type { GuestSessionInfo } from '@/types/classroomSession'

const route = useRoute()
const router = useRouter()

const accessCode = ref('')
const loading = ref(false)
const error = ref('')
const sessionInfo = ref<GuestSessionInfo | null>(null)
const cells = ref<any[]>([])
const cellsLoading = ref(false)

let ws: WebSocket | null = null
let pollTimer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  const code = route.query.code as string
  if (code) {
    accessCode.value = code.toUpperCase()
    lookupSession()
  }
})

onUnmounted(() => {
  cleanup()
})

function cleanup() {
  if (ws) {
    ws.close()
    ws = null
  }
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function lookupSession() {
  if (accessCode.value.length < 6) return
  loading.value = true
  error.value = ''

  try {
    const info = await classroomSessionService.guestLookupSession(accessCode.value)
    sessionInfo.value = info
    await loadCells()
    connectWS()
    startPolling()
  } catch (err: any) {
    const detail = err.response?.data?.detail || err.message || '查找失败'
    error.value = detail
  } finally {
    loading.value = false
  }
}

async function loadCells() {
  if (!sessionInfo.value) return
  cellsLoading.value = true
  try {
    const data = await classroomSessionService.guestGetCells(
      sessionInfo.value.sessionId,
      accessCode.value,
    )
    cells.value = data.cells || []
    if (data.current_cell_id) {
      sessionInfo.value!.currentCellId = data.current_cell_id
    }
  } catch {
    // silently fail, will retry via polling
  } finally {
    cellsLoading.value = false
  }
}

function connectWS() {
  if (!sessionInfo.value) return
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  const url = `${protocol}//${host}/api/v1/classroom-sessions/sessions/${sessionInfo.value.sessionId}/ws/guest?code=${accessCode.value}`

  ws = new WebSocket(url)

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data)
      handleWsMessage(msg)
    } catch { /* ignore */ }
  }

  ws.onclose = () => {
    setTimeout(() => {
      if (sessionInfo.value) connectWS()
    }, 3000)
  }

  // Heartbeat
  const pingInterval = setInterval(() => {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }))
    } else {
      clearInterval(pingInterval)
    }
  }, 30000)
}

function handleWsMessage(msg: any) {
  const type = msg.type
  if (type === 'cell_changed' || type === 'connected') {
    const data = msg.data || {}
    if (data.display_cell_orders && sessionInfo.value) {
      sessionInfo.value.displayCellOrders = data.display_cell_orders
    }
    if (data.current_cell_id !== undefined && sessionInfo.value) {
      sessionInfo.value.currentCellId = data.current_cell_id
    }
    if (data.current_state) {
      if (data.current_state.display_cell_orders && sessionInfo.value) {
        sessionInfo.value.displayCellOrders = data.current_state.display_cell_orders
      }
      if (data.current_state.current_cell_id !== undefined && sessionInfo.value) {
        sessionInfo.value.currentCellId = data.current_state.current_cell_id
      }
    }
    loadCells()
  } else if (type === 'session_ended') {
    if (sessionInfo.value) {
      sessionInfo.value.status = 'ended'
    }
    cleanup()
  } else if (type === 'session_status_changed') {
    const data = msg.data || {}
    if (data.status && sessionInfo.value) {
      sessionInfo.value.status = data.status.toLowerCase()
    }
  }
}

function startPolling() {
  pollTimer = setInterval(async () => {
    if (!sessionInfo.value) return
    await loadCells()
  }, 10000)
}

function exitGuest() {
  cleanup()
  sessionInfo.value = null
  cells.value = []
  accessCode.value = ''
  router.push('/guest')
}
</script>
