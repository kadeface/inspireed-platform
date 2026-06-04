<template>
  <footer class="w-full border-t border-slate-800/80 bg-slate-900 text-white">
    <div class="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
      <!-- 主栏：随屏宽自动重排 -->
      <div
        class="grid w-full grid-cols-1 items-center gap-5 sm:grid-cols-2 sm:gap-6 lg:grid-cols-12 lg:gap-x-6 xl:gap-x-10"
      >
        <!-- 品牌 -->
        <div
          class="flex min-w-0 items-center justify-center gap-3 sm:justify-start lg:col-span-3"
        >
          <div
            class="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 shadow-md shadow-emerald-900/30 sm:h-9 sm:w-9"
          >
            <svg class="h-4 w-4 text-white sm:h-5 sm:w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
              />
            </svg>
          </div>
          <div class="min-w-0 text-center sm:text-left">
            <p class="text-base font-bold tracking-tight sm:text-lg">InspireEd</p>
            <p class="truncate text-[10px] text-slate-500 sm:text-xs">
              Evidence-based Learning & Teaching
            </p>
          </div>
        </div>

        <!-- 版权 -->
        <p
          class="min-w-0 text-center text-xs leading-relaxed text-slate-400 sm:col-span-2 sm:text-sm lg:col-span-5 lg:text-left"
        >
          © {{ currentYear }} InspireEd · 循证教学与学习支持平台
        </p>

        <!-- 访客统计：窄屏整行铺满，宽屏靠右 -->
        <div
          class="w-full min-w-0 sm:justify-self-end lg:col-span-4 lg:justify-self-end"
          aria-label="访客统计"
        >
          <!-- 超窄屏（≤400px）：单行紧凑条 -->
          <div
            class="flex w-full items-center justify-between gap-2 rounded-xl border border-slate-700/60 bg-slate-800/50 px-3 py-2.5 min-[401px]:hidden"
          >
            <span class="inline-flex shrink-0 items-center gap-1.5 text-[10px] font-medium text-slate-500">
              <span
                class="h-1.5 w-1.5 shrink-0 rounded-full"
                :class="statsError ? 'bg-slate-500' : visitorStats ? 'bg-emerald-400' : 'bg-slate-600'"
              />
              访客
            </span>
            <span class="tabular-nums text-xs text-slate-400">
              累计 <strong class="font-semibold text-emerald-400/90">{{ displayTotal }}</strong>
            </span>
            <span class="tabular-nums text-xs text-slate-400">
              今日 <strong class="font-semibold text-teal-400/90">{{ displayToday }}</strong>
            </span>
          </div>

          <!-- 常规屏（>400px）：标签 + 双卡（宽度随容器伸缩） -->
          <div
            class="hidden min-[401px]:flex min-[401px]:flex-col min-[401px]:items-stretch min-[401px]:gap-2 sm:flex-row sm:items-center sm:justify-center sm:gap-3 md:justify-end lg:flex-col lg:items-end lg:gap-2 xl:flex-row xl:items-center"
          >
            <div
              class="inline-flex shrink-0 items-center justify-center gap-1.5 self-center rounded-full border border-slate-700/80 bg-slate-800/60 px-3 py-1 text-[10px] font-medium uppercase tracking-wider text-slate-500 sm:text-[11px] md:self-auto lg:self-end xl:self-center"
            >
              <span class="relative flex h-1.5 w-1.5 shrink-0">
                <span
                  v-if="visitorStats && !statsError"
                  class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60"
                />
                <span
                  class="relative inline-flex h-1.5 w-1.5 rounded-full"
                  :class="statsError ? 'bg-slate-500' : visitorStats ? 'bg-emerald-400' : 'bg-slate-600'"
                />
              </span>
              访客统计
            </div>
            <div class="grid w-full grid-cols-2 gap-2 sm:w-auto sm:min-w-[11rem] md:min-w-[12rem]">
              <div
                class="min-w-0 flex-1 rounded-lg border border-slate-700/60 bg-slate-800/40 px-2 py-2 text-center sm:px-3 sm:py-2.5"
              >
                <p class="text-[10px] font-medium text-slate-500 sm:text-[11px]">累计访问</p>
                <p
                  class="mt-0.5 truncate tabular-nums text-base font-semibold text-emerald-400/90 sm:text-lg"
                >
                  {{ displayTotal }}
                </p>
              </div>
              <div
                class="min-w-0 flex-1 rounded-lg border border-slate-700/60 bg-slate-800/40 px-2 py-2 text-center sm:px-3 sm:py-2.5"
              >
                <p class="text-[10px] font-medium text-slate-500 sm:text-[11px]">今日访问</p>
                <p
                  class="mt-0.5 truncate tabular-nums text-base font-semibold text-teal-400/90 sm:text-lg"
                >
                  {{ displayToday }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 开发者信息 -->
      <div
        class="mt-5 flex w-full min-w-0 flex-col items-center gap-2 border-t border-slate-800 pt-4 text-center text-xs text-slate-400 sm:col-span-2 sm:mt-6 sm:flex-row sm:flex-wrap sm:justify-center sm:gap-x-3 sm:pt-5 sm:text-sm lg:col-span-12 lg:justify-start lg:pt-5"
      >
        <span class="inline-flex max-w-full items-center justify-center gap-1.5 break-words text-slate-500 sm:justify-start">
          <svg class="h-3.5 w-3.5 shrink-0 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <span class="text-balance">
            开发者：广东省开平市教师发展中心 · 廖作东
          </span>
        </span>
        <span class="hidden shrink-0 text-slate-700 sm:inline" aria-hidden="true">|</span>
        <a
          href="mailto:382241106@qq.com"
          aria-label="发送邮件至 382241106@qq.com"
          class="inline-flex max-w-full shrink-0 items-center justify-center gap-1.5 break-all text-slate-300 transition-colors hover:text-emerald-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900 sm:justify-start"
        >
          <svg class="h-3.5 w-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <span class="border-b border-dashed border-slate-600/80 pb-px hover:border-emerald-500/60">382241106@qq.com</span>
        </a>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { loadAndTrackVisitorStats, type SiteVisitorStats } from '@/services/siteAnalytics'

const visitorStats = ref<SiteVisitorStats | null>(null)
const statsError = ref(false)

const currentYear = new Date().getFullYear()

const displayTotal = computed(() => {
  if (statsError.value) return '—'
  if (!visitorStats.value) return '…'
  return formatCount(visitorStats.value.total_visits)
})

const displayToday = computed(() => {
  if (statsError.value) return '—'
  if (!visitorStats.value) return '…'
  return formatCount(visitorStats.value.today_visits)
})

function formatCount(value: number): string {
  return value.toLocaleString('zh-CN')
}

onMounted(async () => {
  statsError.value = false
  try {
    visitorStats.value = await loadAndTrackVisitorStats()
  } catch (error) {
    statsError.value = true
    console.error('Failed to load visitor statistics:', error)
  }
})
</script>
