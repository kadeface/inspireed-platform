<template>
  <div
    v-if="activeSession"
    class="fixed inset-x-0 bottom-0 z-[80] border-t border-cyan-200/30 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 px-3 py-3 text-white shadow-[0_-4px_24px_rgba(0,0,0,0.18)] sm:px-5 sm:py-4"
    role="region"
    aria-label="返回课程"
  >
    <div class="mx-auto flex max-w-5xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between sm:gap-4">
      <div>
        <p class="text-sm font-semibold sm:text-base">外部页面已打开</p>
        <p class="mt-1 text-xs text-slate-300 sm:text-sm">
          看完后，在浏览器标签栏点「回课」回到这里。这一节课的外链共用同一个标签。
        </p>
      </div>
      <div class="flex shrink-0 items-center gap-2">
        <button
          type="button"
          class="rounded-lg border border-slate-500 bg-slate-700/80 px-3 py-2 text-sm font-medium text-white hover:bg-slate-600"
          @click="focusExternal"
        >
          打开外部网页
        </button>
        <button
          type="button"
          class="rounded-lg p-2 text-slate-400 hover:bg-slate-700/50 hover:text-white"
          aria-label="关闭提示"
          @click="dismissDock"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import { useExternalBrowser } from '@/composables/useExternalBrowser'

const COURSE_TAB_TITLE = '回课'

const route = useRoute()
const { activeSession, focusExternal, dismissDock } = useExternalBrowser()

let savedTitle: string | null = null

function applyCourseTabTitle() {
  if (!activeSession.value) return
  if (document.title !== COURSE_TAB_TITLE) {
    savedTitle = document.title
  }
  document.title = COURSE_TAB_TITLE
}

function restoreCourseTabTitle() {
  if (savedTitle && savedTitle !== COURSE_TAB_TITLE) {
    document.title = savedTitle
  }
  savedTitle = null
}

watch(activeSession, (session) => {
  if (session) applyCourseTabTitle()
  else restoreCourseTabTitle()
}, { immediate: true })

watch(() => route.fullPath, () => {
  if (activeSession.value) applyCourseTabTitle()
})
</script>
