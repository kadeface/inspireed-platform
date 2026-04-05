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
      <div class="text-xs text-gray-500 mb-1">访客接入码</div>
      <div class="flex items-center gap-2">
        <span class="text-2xl font-mono font-bold tracking-widest text-blue-700">
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import classroomSessionService from '@/services/classroomSession'

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

const isEnabled = computed(() => props.guestAccessEnabled)
const accessCode = computed(() => props.guestAccessCode)

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
