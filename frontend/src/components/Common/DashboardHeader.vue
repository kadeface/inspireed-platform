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
          <!-- 用户名 -->
          <span class="text-sm text-gray-700">{{ userName }}</span>

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
defineProps<{
  title: string
  subtitle?: string
  userName: string
  showProfileButton?: boolean
}>()

defineEmits<{
  (e: 'logout'): void
  (e: 'profile'): void
}>()
</script>

