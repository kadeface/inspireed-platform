<template>
  <div class="external-browser-page">
    <div v-if="!targetUrl" class="external-browser-error">
      <p>链接无效或已过期</p>
      <button type="button" class="dock-btn dock-btn-primary" @click="handleContinueLesson">
        返回
      </button>
    </div>
    <template v-else>
      <div class="external-browser-frame-wrap">
        <iframe
          :key="iframeKey"
          :src="targetUrl"
          class="external-browser-iframe"
          title="外部网页"
          sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox allow-downloads allow-top-navigation-by-user-activation allow-modals"
        />
      </div>
      <BrowserExternalDockBar
        :title="pageTitle"
        variant="external"
        :embedded="true"
        :show-dismiss="false"
        @continue-lesson="handleContinueLesson"
        @reload-content="reloadIframe"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import BrowserExternalDockBar from '@/components/Cell/BrowserExternalDockBar.vue'
import { useExternalBrowser } from '@/composables/useExternalBrowser'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const { focusLessonTab } = useExternalBrowser()
const toast = useToast()

const iframeKey = ref(0)

const targetUrl = computed(() => {
  const raw = route.query.url
  const u = typeof raw === 'string' ? raw.trim() : ''
  if (!u) return null
  try {
    const parsed = new URL(u)
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') return null
    return parsed.toString()
  } catch {
    return null
  }
})

const pageTitle = computed(() => {
  const t = route.query.title
  if (typeof t === 'string' && t.trim()) return t.trim()
  if (targetUrl.value) {
    try {
      return new URL(targetUrl.value).hostname
    } catch {
      return '外部网页'
    }
  }
  return '外部网页'
})

watch(
  () => route.query,
  () => {
    iframeKey.value += 1
  }
)

function reloadIframe() {
  iframeKey.value += 1
}

function handleContinueLesson() {
  const ok = focusLessonTab({
    lessonId: route.query.lessonId,
    cellId: route.query.cellId,
    returnUrl: typeof route.query.returnUrl === 'string' ? route.query.returnUrl : undefined,
  })

  if (ok) {
    toast.success('已切回授课页面', '继续听课')
  } else {
    toast.warning('无法自动切回授课页，请手动点击浏览器中的授课标签页')
  }
}
</script>

<style scoped>
.external-browser-page {
  @apply flex h-screen flex-col overflow-hidden bg-gray-100;
}

.external-browser-frame-wrap {
  @apply min-h-0 flex-1;
}

.external-browser-iframe {
  @apply block h-full w-full border-0 bg-white;
}

.external-browser-error {
  @apply flex flex-1 flex-col items-center justify-center gap-4 p-8 text-gray-600;
}

.dock-btn-primary {
  @apply rounded-lg bg-cyan-500 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-400;
}
</style>
