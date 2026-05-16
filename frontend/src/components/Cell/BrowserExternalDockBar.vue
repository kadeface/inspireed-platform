<template>
  <div
    class="browser-external-dock-bar"
    :class="{ 'browser-external-dock-bar--embedded': embedded }"
    role="region"
    aria-label="外部网页托管条"
  >
    <div class="browser-external-dock-inner">
      <div class="browser-external-dock-text">
        <p class="browser-external-dock-title">
          <template v-if="variant === 'external'">
            「{{ displayTitle }}」
          </template>
          <template v-else>
            「{{ displayTitle }}」已在外部页面打开
          </template>
        </p>
        <p class="browser-external-dock-sub">
          <template v-if="variant === 'external'">
            登录或下载完成后，点击下方「继续听课」返回授课页面。
          </template>
          <template v-else>
            登录或下载完成后，请切回本标签页继续听课；也可点击下方按钮切换回外部页面。
          </template>
        </p>
      </div>
      <div class="browser-external-dock-actions">
        <button
          v-if="variant === 'lesson'"
          type="button"
          class="dock-btn dock-btn-secondary"
          @click="emit('focus-external')"
        >
          切换外部窗口
        </button>
        <button
          v-if="variant === 'external'"
          type="button"
          class="dock-btn dock-btn-secondary"
          @click="emit('reload-content')"
        >
          刷新页面
        </button>
        <button type="button" class="dock-btn dock-btn-primary" @click="emit('continue-lesson')">
          继续听课
        </button>
        <button
          v-if="variant === 'lesson' && showDismiss"
          type="button"
          class="dock-btn dock-btn-ghost"
          aria-label="关闭提示"
          @click="emit('dismiss')"
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
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    title?: string
    variant?: 'lesson' | 'external'
    embedded?: boolean
    showDismiss?: boolean
  }>(),
  {
    title: '外部网页',
    variant: 'external',
    embedded: true,
    showDismiss: true,
  }
)

const emit = defineEmits<{
  'continue-lesson': []
  'focus-external': []
  'reload-content': []
  dismiss: []
}>()

const displayTitle = computed(() => props.title?.trim() || '外部网页')
</script>

<style scoped>
.browser-external-dock-bar {
  @apply shrink-0 border-t border-cyan-200/30 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 px-3 py-3 text-white shadow-[0_-4px_24px_rgba(0,0,0,0.15)] sm:px-5 sm:py-4;
}

.browser-external-dock-bar--embedded {
  @apply relative z-10;
}

.browser-external-dock-inner {
  @apply mx-auto flex max-w-5xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between sm:gap-4;
}

.browser-external-dock-title {
  @apply text-sm font-semibold sm:text-base;
}

.browser-external-dock-sub {
  @apply mt-1 text-xs text-slate-300 sm:text-sm;
}

.browser-external-dock-actions {
  @apply flex shrink-0 items-center gap-2;
}

.dock-btn {
  @apply rounded-lg px-3 py-2 text-sm font-medium transition-colors;
}

.dock-btn-primary {
  @apply bg-cyan-500 text-white hover:bg-cyan-400;
}

.dock-btn-secondary {
  @apply border border-slate-500 bg-slate-700/80 text-white hover:bg-slate-600;
}

.dock-btn-ghost {
  @apply p-2 text-slate-400 hover:bg-slate-700/50 hover:text-white;
}
</style>
