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
                :class="
                  sessionInfo.status === 'teaching'
                    ? 'bg-green-500'
                    : sessionInfo.status === 'ended'
                      ? 'bg-gray-500'
                      : 'bg-yellow-500'
                "
              >
                {{
                  sessionInfo.status === 'teaching'
                    ? '上课中'
                    : sessionInfo.status === 'ended'
                      ? '已结束'
                      : '准备中'
                }}
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
        <div class="bg-yellow-50 border-b border-yellow-100 px-6 py-2 text-sm text-yellow-700 space-y-1">
          <p>访客观摩模式 — 您正在只读观摩此课堂，无法提交活动或参与互动。</p>
          <p class="text-yellow-800/90 text-xs leading-relaxed">
            下方正文与学生端一致：仅展示教师在导播台当前勾选/投屏的模块；未勾选的模块不会显示内容（并非系统遗漏）。
          </p>
        </div>

        <!-- Cell 内容区域 -->
        <div class="p-6">
          <div v-if="cellsLoading" class="text-center py-12 text-gray-400">
            加载课堂内容中...
          </div>

          <div v-else-if="cells.length === 0" class="text-center py-12 text-gray-400">
            <div class="text-4xl mb-4">📚</div>
            <p v-if="sessionInfo.status === 'ended'">课堂已结束</p>
            <p v-else-if="sessionInfo.status === 'teaching'">等待教师展示内容...</p>
            <p v-else>课堂尚未开始，请稍候</p>
          </div>

          <div v-else class="space-y-6">
            <div
              v-for="cell in cells"
              :key="guestCellKey(cell)"
              class="border border-gray-200 rounded-xl p-5 transition-all"
              :class="{ 'ring-2 ring-blue-400 bg-blue-50/30': isGuestCurrentCell(cell) }"
            >
              <div class="flex items-center gap-2 mb-3">
                <span class="px-2 py-0.5 text-xs rounded bg-gray-100 text-gray-600 font-mono">
                  {{ cell.cell_type }}
                </span>
                <span v-if="cell.title" class="text-sm font-medium text-gray-700">
                  {{ cell.title }}
                </span>
              </div>

              <!-- TEXT cell：与 TextCell 一致支持 html / markdown / json 纯文本兜底 -->
              <div
                v-if="isGuestTextCellType(cell)"
                class="prose prose-sm max-w-none"
              >
                <template v-for="tx in [getGuestTextCellParts(cell)]" :key="'tx-' + guestCellKey(cell)">
                  <div v-if="tx.kind === 'html'" v-html="tx.html" />
                  <div
                    v-else-if="tx.kind === 'plain'"
                    class="whitespace-pre-wrap text-sm text-gray-800"
                  >
                    {{ tx.text }}
                  </div>
                  <p v-else class="text-sm text-gray-500">暂无文本内容</p>
                </template>
              </div>

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

              <!-- CODE cell：与学生端 CodeCell 一致，HTML 用 iframe srcdoc 预览 -->
              <div v-else-if="cell.cell_type === 'CODE'" class="space-y-2">
                <div
                  v-if="guestCodeIsHtml(cell) && guestCodeSource(cell).trim()"
                  class="w-full overflow-hidden rounded-lg border border-gray-200 bg-white"
                >
                  <iframe
                    :srcdoc="guestCodeSource(cell)"
                    class="h-[min(70vh,800px)] min-h-[320px] w-full border-0"
                    title="HTML 预览"
                    sandbox="allow-scripts allow-same-origin"
                  />
                </div>
                <div
                  v-else
                  class="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto"
                >
                  <pre>{{ guestCodeSource(cell) }}</pre>
                </div>
              </div>

              <!-- BROWSER cell（正文常仅来自教案 JSON） -->
              <div v-else-if="cell.cell_type === 'BROWSER'" class="space-y-2 text-sm text-gray-700">
                <p v-if="cell.content?.description" class="text-gray-600">{{ cell.content.description }}</p>
                <div
                  v-if="cell.content?.url"
                  class="w-full overflow-hidden rounded-lg border border-gray-200 bg-white"
                  style="min-height: 480px"
                >
                  <iframe
                    :src="cell.content.url"
                    class="h-[70vh] min-h-[480px] w-full border-0"
                    title="浏览器单元"
                    sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox"
                  />
                </div>
                <p v-else class="text-gray-500">未配置网址</p>
              </div>

              <!-- INTERACTIVE cell -->
              <div v-else-if="cell.cell_type === 'INTERACTIVE'" class="space-y-2 text-sm text-gray-700">
                <p v-if="cell.content?.description" class="text-gray-600">{{ cell.content.description }}</p>
                <div
                  v-if="cell.content?.url"
                  class="w-full overflow-hidden rounded-lg border border-gray-200 bg-white"
                  style="min-height: 480px"
                >
                  <iframe
                    :src="cell.content.url"
                    class="h-[70vh] min-h-[480px] w-full border-0"
                    title="交互式课件"
                    sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox"
                  />
                </div>
                <div
                  v-else-if="cell.content?.html_code"
                  class="rounded-lg border border-gray-200 bg-white p-2 prose prose-sm max-w-none"
                  v-html="cell.content.html_code"
                />
                <p v-else class="text-gray-500">暂无可嵌入的交互课件地址</p>
              </div>

              <!-- ACTIVITY cell — 访客只读：可看题干与选项，不可作答 -->
              <div v-else-if="cell.cell_type === 'ACTIVITY'" class="rounded-lg border border-gray-200 bg-gray-50/80 p-4 text-sm">
                <div class="mb-3 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
                  访客仅可浏览题目，不能作答或提交。
                </div>
                <div v-if="!cell.content" class="text-gray-500">暂无活动详情</div>
                <div v-else class="space-y-4 text-gray-800">
                  <div>
                    <h3 class="text-lg font-semibold text-gray-900">
                      {{ cell.content.title || cell.title || '教学活动' }}
                    </h3>
                    <p
                      v-if="cell.content.description"
                      class="mt-1 whitespace-pre-wrap text-sm text-gray-600"
                    >
                      {{ cell.content.description }}
                    </p>
                    <div class="mt-2 flex flex-wrap gap-2 text-xs text-gray-500">
                      <span class="rounded border border-gray-200 bg-white px-2 py-0.5">
                        {{ guestActivityTypeLabel(cell.content.activityType) }}
                      </span>
                      <span
                        v-if="guestActivityItems(cell.content).length"
                        class="rounded border border-gray-200 bg-white px-2 py-0.5"
                      >
                        {{ guestActivityItems(cell.content).length }} 题
                      </span>
                    </div>
                  </div>

                  <div
                    v-for="(item, idx) in guestActivityItems(cell.content)"
                    :key="item.id ?? idx"
                    class="rounded-lg border border-gray-200 bg-white p-4"
                  >
                    <div class="mb-2 flex flex-wrap items-center gap-2 text-xs">
                      <span class="font-medium text-gray-500">{{ idx + 1 }}.</span>
                      <span class="rounded bg-gray-100 px-2 py-0.5 text-gray-600">
                        {{ guestItemTypeLabel(item.type) }}
                      </span>
                      <span v-if="item.required" class="text-red-500">必答</span>
                      <span v-if="item.points" class="text-gray-500">{{ item.points }} 分</span>
                    </div>
                    <p class="whitespace-pre-wrap text-sm text-gray-900">{{ item.question }}</p>

                    <ul v-if="item.config?.options?.length" class="mt-3 list-disc space-y-1 pl-5">
                      <li v-for="opt in item.config.options" :key="opt.id" class="text-sm text-gray-700">
                        {{ opt.text }}
                      </li>
                    </ul>
                    <p v-else-if="item.type === 'true-false'" class="mt-2 text-sm text-gray-500">
                      判断：正确 / 错误
                    </p>
                    <div v-else-if="item.type === 'scale' && item.config" class="mt-2 text-sm text-gray-600">
                      量表：{{ item.config.min }} — {{ item.config.max }}
                      <span v-if="item.config.minLabel || item.config.maxLabel">
                        （{{ item.config.minLabel || '—' }} ~ {{ item.config.maxLabel || '—' }}）
                      </span>
                    </div>
                    <div v-else-if="item.type === 'rubric-item' && item.config?.levels?.length" class="mt-3 space-y-1">
                      <p v-if="item.config.criterion" class="text-xs text-gray-500">
                        维度：{{ item.config.criterion }}
                      </p>
                      <ul class="space-y-1 text-sm text-gray-700">
                        <li
                          v-for="lv in item.config.levels"
                          :key="lv.level"
                          class="rounded bg-gray-50 px-2 py-1"
                        >
                          {{ lv.name }}（{{ lv.points }} 分）
                          <span v-if="lv.description" class="text-gray-500"> — {{ lv.description }}</span>
                        </li>
                      </ul>
                    </div>
                    <div v-else-if="item.type === 'file-upload' && item.config" class="mt-2 text-xs text-gray-500">
                      文件上传题 · 允许：{{
                        (item.config.acceptedTypes || []).length
                          ? item.config.acceptedTypes.join(', ')
                          : '未指定'
                      }}
                    </div>
                    <div v-else-if="item.type === 'code-submission' && item.config" class="mt-2 text-xs text-gray-500">
                      <span>代码题 · 语言：{{ item.config.language }}</span>
                      <pre
                        v-if="item.config.template"
                        class="mt-2 max-h-40 overflow-auto rounded bg-gray-900 p-2 font-mono text-xs text-green-300"
                      >{{ item.config.template }}</pre>
                    </div>
                    <p v-else-if="guestIsSubjectiveItem(item.type)" class="mt-2 text-xs text-gray-500">
                      主观题（访客不可作答）
                    </p>
                  </div>

                  <p
                    v-if="guestActivityItems(cell.content).length === 0"
                    class="text-sm text-gray-500"
                  >
                    教师尚未添加题目
                  </p>
                </div>
              </div>

              <!-- 其他类型 -->
              <div v-else class="text-gray-500 text-sm">
                {{ cell.cell_type }} 内容
              </div>
            </div>

            <!-- 全课目录统计：放在正文下方，默认折叠，避免长列表遮挡投屏内容 -->
            <details
              v-if="lessonOutline.length > 0"
              class="guest-lesson-outline rounded-lg border border-slate-200 bg-slate-50 text-slate-600"
            >
              <summary
                class="flex cursor-pointer list-none items-center justify-between gap-3 px-4 py-2.5 text-left text-xs text-slate-700 hover:bg-slate-100/90 rounded-lg [&::-webkit-details-marker]:hidden"
              >
                <span>
                  全课 <strong class="text-slate-900">{{ lessonOutline.length }}</strong> 个模块（与导播台一致）
                  <template v-if="undisplayedLessonModules.length > 0">
                    · 另有 <strong class="text-slate-900">{{ undisplayedLessonModules.length }}</strong> 个未投屏
                  </template>
                  <template v-else> · 当前均已投屏</template>
                </span>
                <span class="guest-outline-toggle shrink-0 text-[11px] text-slate-400" aria-hidden="true" />
              </summary>
              <div class="border-t border-slate-200/80 px-4 pb-3 pt-2">
                <p v-if="undisplayedLessonModules.length > 0" class="mb-2 text-[11px] leading-relaxed text-slate-500">
                  下列为未投屏模块标题（无正文）；投屏内容见上方。
                </p>
                <p v-else class="text-[11px] text-slate-500">
                  教师当前展示的内容见上方白色卡片区域。
                </p>
                <ul
                  v-if="undisplayedLessonModules.length > 0"
                  class="max-h-[min(36vh,280px)] list-disc space-y-0.5 overflow-y-auto pl-4 text-[11px] leading-snug text-slate-600 sm:pl-5"
                >
                  <li v-for="m in undisplayedLessonModules" :key="m.id" class="break-words">
                    <span class="font-mono text-slate-500">{{ m.cell_type }}</span>
                    · {{ m.title || `order=${m.order ?? '-'}` }}
                  </li>
                </ul>
              </div>
            </details>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import classroomSessionService, {
  normalizeClassSessionStatus,
} from '@/services/classroomSession'
import api from '@/services/api'
import { markdownToHtml } from '@/utils/lessonEditorHelpers'
import type { GuestSessionInfo } from '@/types/classroomSession'

const route = useRoute()
const router = useRouter()

const accessCode = ref('')
const loading = ref(false)
const error = ref('')
const sessionInfo = ref<GuestSessionInfo | null>(null)
const cells = ref<any[]>([])
const cellsLoading = ref(false)
/** 教案全部模块元数据（与 display_cell_orders 无关），用于提示未投屏模块 */
const lessonOutline = ref<
  { id: number; order: number | null; title: string; cell_type: string }[]
>([])

const undisplayedLessonModules = computed(() => {
  if (!sessionInfo.value) return []
  const shown = new Set(sessionInfo.value.displayCellOrders ?? [])
  return lessonOutline.value.filter((m) => m.order != null && !shown.has(m.order))
})

let ws: WebSocket | null = null
let pollTimer: ReturnType<typeof setInterval> | null = null
let wsPingTimer: ReturnType<typeof setInterval> | null = null
/** 合并短时间内的多次拉取（WS 连上时可能连续多条消息） */
let reloadCellsDebounce: ReturnType<typeof setTimeout> | null = null
/** 仅第一次拉 cells 时全屏「加载中」，避免轮询/推送把正文整块换掉 */
const isInitialCellFetch = ref(true)

const GUEST_POLL_MS = 25000

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
  if (reloadCellsDebounce) {
    clearTimeout(reloadCellsDebounce)
    reloadCellsDebounce = null
  }
  if (wsPingTimer) {
    clearInterval(wsPingTimer)
    wsPingTimer = null
  }
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
    isInitialCellFetch.value = true
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
  const showBlockingSpinner = isInitialCellFetch.value
  if (showBlockingSpinner) {
    cellsLoading.value = true
  }
  try {
    const data = await classroomSessionService.guestGetCells(
      sessionInfo.value.sessionId,
      accessCode.value,
    )
    cells.value = data.cells || []
    if (Array.isArray(data.lesson_outline)) {
      lessonOutline.value = data.lesson_outline
    }
    if (data.status !== undefined) {
      sessionInfo.value!.status = normalizeClassSessionStatus(data.status)
    }
    if (data.display_cell_orders !== undefined) {
      sessionInfo.value!.displayCellOrders = data.display_cell_orders ?? []
    }
    if (data.current_cell_id !== undefined) {
      sessionInfo.value!.currentCellId = data.current_cell_id ?? undefined
    }
  } catch {
    // silently fail, will retry via polling
  } finally {
    isInitialCellFetch.value = false
    if (showBlockingSpinner) {
      cellsLoading.value = false
    }
  }
}

function scheduleLoadCells() {
  if (reloadCellsDebounce) {
    clearTimeout(reloadCellsDebounce)
  }
  reloadCellsDebounce = setTimeout(() => {
    reloadCellsDebounce = null
    loadCells()
  }, 500)
}

function connectWS() {
  if (!sessionInfo.value) return
  if (wsPingTimer) {
    clearInterval(wsPingTimer)
    wsPingTimer = null
  }
  if (ws) {
    try {
      ws.close()
    } catch {
      /* ignore */
    }
    ws = null
  }

  const sid = sessionInfo.value.sessionId
  const code = encodeURIComponent(accessCode.value)
  const url = api.buildClassroomWebSocketUrl(
    `classroom-sessions/sessions/${sid}/ws/guest?code=${code}`,
  )

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

  wsPingTimer = setInterval(() => {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }))
    }
  }, 30000)
}

function handleWsMessage(msg: any) {
  const type = msg.type
  if (type === 'cell_changed' || type === 'connected') {
    const data = msg.data || {}
    if (data.display_cell_orders !== undefined && sessionInfo.value) {
      sessionInfo.value.displayCellOrders = data.display_cell_orders ?? []
    }
    if (data.current_cell_id !== undefined && sessionInfo.value) {
      sessionInfo.value.currentCellId = data.current_cell_id
    }
    if (data.current_state) {
      if (data.current_state.display_cell_orders !== undefined && sessionInfo.value) {
        sessionInfo.value.displayCellOrders = data.current_state.display_cell_orders ?? []
      }
      if (data.current_state.current_cell_id !== undefined && sessionInfo.value) {
        sessionInfo.value.currentCellId = data.current_state.current_cell_id
      }
      if (data.current_state.status !== undefined && sessionInfo.value) {
        sessionInfo.value.status = normalizeClassSessionStatus(data.current_state.status)
      }
    }
    scheduleLoadCells()
  } else if (type === 'session_ended') {
    if (sessionInfo.value) {
      sessionInfo.value.status = 'ended'
    }
    cleanup()
  } else if (type === 'session_status_changed') {
    const data = msg.data || {}
    if (data.status !== undefined && sessionInfo.value) {
      sessionInfo.value.status = normalizeClassSessionStatus(data.status)
    }
    // 开始上课等会初始化 display_cell_orders，访客需拉最新 cells
    scheduleLoadCells()
  }
}

function startPolling() {
  pollTimer = setInterval(async () => {
    if (!sessionInfo.value) return
    await loadCells()
  }, GUEST_POLL_MS)
}

function exitGuest() {
  cleanup()
  sessionInfo.value = null
  cells.value = []
  lessonOutline.value = []
  isInitialCellFetch.value = true
  cellsLoading.value = false
  accessCode.value = ''
  router.push('/guest')
}

function guestCellKey(cell: Record<string, any>) {
  return `${String(cell.id)}-${cell.order ?? 'x'}-${cell.cell_type ?? ''}`
}

function isGuestTextCellType(cell: Record<string, any>) {
  return String(cell?.cell_type ?? '').toUpperCase() === 'TEXT'
}

/** 与 CodeCell 使用同一字段：code 为主，兼容 source */
function guestCodeSource(cell: Record<string, any>): string {
  const c = cell?.content
  if (!c || typeof c !== 'object') return ''
  const raw = (c as Record<string, unknown>).code ?? (c as Record<string, unknown>).source
  return raw != null ? String(raw) : ''
}

function guestCodeIsHtml(cell: Record<string, any>): boolean {
  const lang = cell?.content?.language
  return String(lang ?? '').toLowerCase() === 'html'
}

function tiptapJsonToPlainText(node: unknown): string {
  if (!node || typeof node !== 'object') return ''
  const n = node as Record<string, unknown>
  if (n.type === 'text' && typeof n.text === 'string') return n.text
  if (Array.isArray(n.content)) {
    const sep = n.type === 'paragraph' || n.type === 'heading' ? '\n' : ''
    return n.content.map((ch) => tiptapJsonToPlainText(ch)).join(sep)
  }
  return ''
}

type GuestTextParts =
  | { kind: 'html'; html: string }
  | { kind: 'plain'; text: string }
  | { kind: 'empty' }

/** 对齐 TextCell：html → markdown → text 字段 → TipTap json 抽纯文本 */
function getGuestTextCellParts(cell: Record<string, any>): GuestTextParts {
  const c = cell?.content
  if (typeof c === 'string') {
    const t = c.trim()
    return t ? { kind: 'plain', text: t } : { kind: 'empty' }
  }
  if (!c || typeof c !== 'object') return { kind: 'empty' }

  const htmlRaw = c.html
  if (htmlRaw != null && String(htmlRaw).trim()) {
    return { kind: 'html', html: String(htmlRaw) }
  }

  const md = c.markdown
  if (md != null && String(md).trim()) {
    return { kind: 'html', html: markdownToHtml(String(md)) }
  }

  const tx = c.text
  if (tx != null && String(tx).trim()) {
    return { kind: 'plain', text: String(tx) }
  }

  if (c.json) {
    const plain = tiptapJsonToPlainText(c.json).trim()
    if (plain) return { kind: 'plain', text: plain }
  }

  return { kind: 'empty' }
}

/** 教师切到仅 JSON 存在的模块时 current_cell_id 可能为空，用 display_cell_orders[0] 对齐高亮 */
function isGuestCurrentCell(cell: Record<string, any>) {
  if (!sessionInfo.value) return false
  const cid = sessionInfo.value.currentCellId
  if (cid != null && cell.id === cid) return true
  const orders = sessionInfo.value.displayCellOrders ?? []
  if (orders.length === 0) return false
  return cell.order === orders[0]
}

const GUEST_ACTIVITY_TYPE_LABELS: Record<string, string> = {
  quiz: '测验',
  survey: '问卷',
  assignment: '作业',
  rubric: '评价量表',
  mixed: '混合活动',
}

const GUEST_ITEM_TYPE_LABELS: Record<string, string> = {
  'single-choice': '单选题',
  'multiple-choice': '多选题',
  'true-false': '判断题',
  'short-answer': '简答题',
  'long-answer': '论述题',
  'file-upload': '文件上传',
  'code-submission': '代码题',
  scale: '量表',
  'rubric-item': '评价项',
}

function guestActivityItems(content: Record<string, any> | undefined): any[] {
  const items = content?.items
  return Array.isArray(items) ? items : []
}

function guestActivityTypeLabel(t: string | undefined) {
  if (!t) return '教学活动'
  return GUEST_ACTIVITY_TYPE_LABELS[t] || t
}

function guestItemTypeLabel(t: string | undefined) {
  if (!t) return '题目'
  return GUEST_ITEM_TYPE_LABELS[t] || t
}

function guestIsSubjectiveItem(type: string | undefined) {
  return type === 'short-answer' || type === 'long-answer'
}
</script>

<style scoped>
.guest-lesson-outline > summary .guest-outline-toggle::after {
  content: '展开目录';
}
.guest-lesson-outline[open] > summary .guest-outline-toggle::after {
  content: '收起';
}
</style>
