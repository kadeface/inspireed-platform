<template>
  <header class="bg-white shadow-sm border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- 左侧：标题和欢迎信息 -->
        <div>
          <h1 class="text-2xl font-bold text-gray-900">{{ title }}</h1>
          <p v-if="subtitle" class="text-sm text-gray-600 mt-0.5">{{ subtitle }}</p>
        </div>

        <!-- 右侧：用户信息和操作 -->
        <div class="flex items-center gap-4">
          <!-- 用户信息 -->
          <div class="flex flex-col items-end text-right">
            <span class="text-sm font-medium text-gray-700">{{ userName }}</span>
            <div
              v-if="organizationInfo.length"
              class="mt-1 flex flex-wrap justify-end gap-x-3 gap-y-1 text-xs text-gray-500"
            >
              <span v-for="(info, index) in organizationInfo" :key="index" class="whitespace-nowrap">
                {{ info }}
              </span>
            </div>
          </div>

          <!-- 个人中心按钮（可选） -->
          <button
            v-if="showProfileButton"
            @click="$emit('profile')"
            class="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            个人中心
          </button>

          <!-- 退出登录按钮 -->
          <button
            @click="$emit('logout')"
            class="px-4 py-2 text-sm bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
          >
            退出登录
          </button>
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

