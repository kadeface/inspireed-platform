<template>
  <div class="guest-access-section">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="text-sm font-medium text-gray-700">访客观摩</span>
        <span
          v-if="isEnabled"
          class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800"
        >
          已开启
        </span>
      </div>
      <button
        @click="toggle"
        :disabled="loading"
        class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        :class="isEnabled ? 'bg-blue-600' : 'bg-gray-200'"
      >
        <span
          class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
          :class="isEnabled ? 'translate-x-6' : 'translate-x-1'"
        />
      </button>
    </div>

    <div v-if="isEnabled && accessCode" class="mt-3 p-3 bg-blue-50 rounded-lg">
      <div class="flex items-start justify-between gap-2">
        <div class="min-w-0">
          <div class="text-xs text-gray-500 mb-1">访客接入码</div>
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-2xl font-mono font-bold tracking-widest text-blue-700 break-all">
              {{ accessCode }}
            </span>
            <button
              @click="copyCode"
              class="text-xs text-blue-600 hover:text-blue-800 underline"
            >
              {{ copied ? '已复制' : '复制' }}
            </button>
          </div>
          <div class="text-xs text-gray-500 mt-1">
            访客人数: {{ guestCount }}
          </div>
          <div class="text-xs text-gray-400 mt-1">
            访客可通过此接入码只读观摩课堂内容，无法提交活动
          </div>
        </div>
        <button
          v-if="qrDataUrl"
          type="button"
          class="shrink-0 text-center"
          @click="showLargeQr = true"
        >
          <img
            :src="qrDataUrl"
            width="88"
            height="88"
            alt="访客观摩二维码"
            class="h-[88px] w-[88px] rounded bg-white"
          />
          <span class="mt-1 block text-[11px] leading-4 text-blue-600">点击放大</span>
        </button>
      </div>
    </div>

    <Teleport to="body">
      <div
        v-if="showLargeQr && qrDataUrl"
        class="fixed inset-0 flex items-center justify-center bg-black/80 p-4"
        style="z-index: 10100"
        @click.self="showLargeQr = false"
      >
        <div
          class="relative w-full max-w-xl rounded-2xl bg-white p-8 shadow-2xl"
          role="dialog"
          aria-modal="true"
          aria-label="访客观摩二维码"
        >
          <button
            type="button"
            class="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            aria-label="关闭"
            @click="showLargeQr = false"
          >
            ×
          </button>
          <img
            :src="qrDataUrl"
            alt="扫码进入访客观摩"
            class="mx-auto bg-white p-2"
            style="width: min(420px, 70vw); height: min(420px, 70vw)"
          />
          <p class="mt-4 text-center text-lg font-semibold text-gray-900">扫码进入访客观摩</p>
          <p class="mt-1 text-center font-mono text-2xl font-bold tracking-widest text-blue-700">
            {{ accessCode }}
          </p>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import QRCode from 'qrcode'
import api from '@/services/api'
import classroomSessionService from '@/services/classroomSession'
import { buildGuestJoinUrl, guestJoinOrigin } from '@/utils/guestSession'

const props = defineProps<{
  sessionId: number
  guestAccessEnabled: boolean
  guestAccessCode: string | null
  guestCount: number
}>()

const emit = defineEmits<{
  (e: 'updated', session: any): void
}>()

const loading = ref(false)
const copied = ref(false)
const qrDataUrl = ref<string | null>(null)
const showLargeQr = ref(false)
const lanHost = ref<string | null>(null)
const lanHostReady = ref(false)

const isEnabled = computed(() => props.guestAccessEnabled)
const accessCode = computed(() => props.guestAccessCode)

function pageIsLoopback(): boolean {
  const host = window.location.hostname
  return host === 'localhost' || host === '127.0.0.1' || host === '::1'
}

onMounted(async () => {
  if (!pageIsLoopback()) {
    lanHostReady.value = true
    return
  }
  try {
    const data = await api.get<{ lan_host: string | null }>('/system/lan-host')
    lanHost.value = data.lan_host
  } catch {
    lanHost.value = null
  } finally {
    lanHostReady.value = true
  }
})

const joinUrl = computed(() => {
  if (!isEnabled.value || !accessCode.value) return null
  if (pageIsLoopback() && !lanHostReady.value) return null
  try {
    return buildGuestJoinUrl(
      guestJoinOrigin(window.location.origin, lanHost.value),
      accessCode.value,
    )
  } catch {
    return null
  }
})

watch(
  joinUrl,
  async (url) => {
    showLargeQr.value = false
    if (!url) {
      qrDataUrl.value = null
      return
    }
    try {
      qrDataUrl.value = await QRCode.toDataURL(url, {
        width: 420,
        margin: 2,
        color: { dark: '#000000', light: '#ffffff' },
      })
    } catch {
      qrDataUrl.value = null
    }
  },
  { immediate: true },
)

function onEscape(event: KeyboardEvent) {
  if (event.key === 'Escape') showLargeQr.value = false
}

watch(showLargeQr, (open) => {
  if (open) window.addEventListener('keydown', onEscape)
  else window.removeEventListener('keydown', onEscape)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onEscape)
})

async function toggle() {
  loading.value = true
  try {
    const session = await classroomSessionService.toggleGuestAccess(
      props.sessionId,
      !isEnabled.value,
    )
    emit('updated', session)
  } catch (err: any) {
    console.error('切换访客模式失败:', err)
    alert(err.message || '操作失败')
  } finally {
    loading.value = false
  }
}

async function copyCode() {
  if (!accessCode.value) return
  try {
    await navigator.clipboard.writeText(accessCode.value)
    copied.value = true
    setTimeout(() => (copied.value = false), 2000)
  } catch {
    const input = document.createElement('input')
    input.value = accessCode.value
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    document.body.removeChild(input)
    copied.value = true
    setTimeout(() => (copied.value = false), 2000)
  }
}
</script>
