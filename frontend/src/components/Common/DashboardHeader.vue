<template>
  <header class="relative overflow-hidden border-b border-gray-200 bg-white/90 backdrop-blur">
    <div class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-blue-200/40 to-transparent"></div>
    <div class="absolute inset-y-0 left-0 w-48 bg-gradient-to-br from-blue-50/60 via-transparent to-transparent pointer-events-none"></div>
    <div class="absolute -bottom-8 -right-8 h-32 w-32 rounded-full bg-blue-100/40 blur-3xl pointer-events-none"></div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="flex flex-col gap-5">
        <div class="header-top flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <!-- 左侧：标题和欢迎信息 -->
        <div class="relative z-10">
          <div class="flex items-center gap-3">
            <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-500/10 text-blue-600 shadow-inner">
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v12m8-6H4" />
              </svg>
            </div>
            <div>
              <h1 class="text-2xl font-semibold text-gray-900 tracking-tight">{{ title }}</h1>
              <p v-if="subtitle" class="text-sm text-gray-500 mt-1">
                {{ subtitle }}
              </p>
            </div>
          </div>
        </div>

        <!-- 右侧：用户信息和操作 -->
        <div class="relative z-10 flex items-center gap-4">
          <!-- 用户信息 -->
          <div class="flex flex-col items-end text-right">
            <div class="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-800 bg-gray-100 rounded-full shadow-inner">
              <svg class="h-4 w-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span>{{ userName }}</span>
            </div>
            <div
              v-if="organizationInfo.length"
              class="mt-2 flex flex-wrap justify-end gap-2 text-xs text-gray-500"
            >
              <span
                v-for="(info, index) in organizationInfo"
                :key="index"
                class="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2.5 py-1 text-blue-600"
              >
                <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A13.937 13.937 0 0112 15c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 10-6 0 3 3 0 006 0z" />
                </svg>
                {{ info }}
              </span>
            </div>
          </div>

          <div class="h-10 w-px bg-gradient-to-b from-transparent via-gray-200 to-transparent"></div>

          <!-- 个人中心按钮（可选） -->
          <button
            v-if="showProfileButton"
            @click="$emit('profile')"
            class="flex items-center gap-2 px-3.5 py-2 text-sm font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-xl transition-all shadow-sm"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            个人中心
          </button>

          <!-- 退出登录按钮 -->
          <button
            @click="$emit('logout')"
            class="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-gradient-to-r from-rose-500 to-rose-600 rounded-xl shadow-md hover:shadow-lg hover:from-rose-600 hover:to-rose-700 transition-all"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12H3m12 0l-4 4m4-4l-4-4m13 8v-8" />
            </svg>
            退出登录
          </button>
        </div>
        </div>

        <div v-if="$slots.default" class="relative z-10">
          <div class="header-toolbar">
            <slot />
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, toRefs } from 'vue'

const props = defineProps<{
  title: string
  subtitle?: string
  userName: string
  showProfileButton?: boolean
  regionName?: string | null
  schoolName?: string | null
  gradeName?: string | null
}>()

const { title, subtitle, userName, showProfileButton, regionName, schoolName, gradeName } = toRefs(props)

const organizationInfo = computed(() => {
  const info: string[] = []
  if (regionName.value) {
    info.push(`区域：${regionName.value}`)
  }
  if (schoolName.value) {
    info.push(`学校：${schoolName.value}`)
  }
  if (gradeName.value) {
    info.push(`年级：${gradeName.value}`)
  }
  return info
})

defineEmits<{
  (e: 'logout'): void
  (e: 'profile'): void
}>()
</script>

<style scoped>
.header-top {
  display: flex;
}

.header-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(79, 70, 229, 0.05));
  border: 1px solid rgba(99, 102, 241, 0.18);
  border-radius: 1rem;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
}
</style>

