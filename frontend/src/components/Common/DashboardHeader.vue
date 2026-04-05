<template>
  <header class="bg-white border-b border-slate-200 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex h-16 justify-between items-center">
        <!-- Logo & Title -->
        <div class="flex items-center gap-4">
          <div
            class="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-md shadow-indigo-200"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
              ></path>
            </svg>
          </div>
          <div>
            <h1 class="text-xl font-bold text-slate-800 tracking-tight leading-none">
              {{ title }}
            </h1>
            <p v-if="subtitle" class="text-xs text-slate-500 font-medium mt-1">
              {{ subtitle }}
            </p>
          </div>
        </div>

        <!-- Right Side: User Profile Dropdown -->
        <div class="flex items-center gap-4">
          <!-- Organization Info (Hidden on mobile) -->
          <div
            v-if="organizationInfo.length"
            class="hidden md:flex items-center gap-3 text-xs text-slate-500 mr-4 border-r border-slate-200 pr-4 h-8"
          >
            <span v-for="(info, index) in organizationInfo" :key="index" class="flex items-center">
              {{ info }}
            </span>
          </div>

          <el-dropdown trigger="click" @command="handleCommand">
            <div
              class="flex items-center gap-3 cursor-pointer group p-1.5 rounded-lg hover:bg-slate-50 transition-colors"
            >
              <div class="text-right hidden sm:block">
                <div
                  class="text-sm font-semibold text-slate-700 group-hover:text-indigo-600 transition-colors"
                >
                  {{ userName }}
                </div>
                <div class="text-xs text-slate-400">{{ roleName ?? '管理员' }}</div>
              </div>
              <el-avatar
                :size="36"
                class="bg-indigo-100 text-indigo-600 font-semibold border border-indigo-50"
              >
                {{ userName.charAt(0).toUpperCase() }}
              </el-avatar>
              <el-icon class="text-slate-400 group-hover:text-slate-600 transition-colors"
                ><CaretBottom
              /></el-icon>
            </div>

            <template #dropdown>
              <el-dropdown-menu class="min-w-[200px] p-2">
                <div class="px-4 py-3 border-b border-slate-100 mb-1">
                  <div class="text-xs text-slate-400 mb-1">登录账号</div>
                  <div class="text-sm font-semibold text-slate-800">{{ userName }}</div>
                </div>

                <el-dropdown-item command="profile" v-if="showProfileButton">
                  <el-icon><User /></el-icon> 个人中心
                </el-dropdown-item>
                <el-dropdown-item command="settings" disabled>
                  <el-icon><Setting /></el-icon> 系统设置
                </el-dropdown-item>

                <div class="h-px bg-slate-100 my-1"></div>

                <el-dropdown-item
                  command="logout"
                  class="text-rose-500 hover:text-rose-600 hover:bg-rose-50"
                >
                  <el-icon><SwitchButton /></el-icon> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- Optional Toolbar Slot -->
      <div v-if="$slots.default" class="py-3 border-t border-slate-100 mt-2">
        <slot />
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, toRefs } from 'vue'
import { CaretBottom, User, Setting, SwitchButton } from '@element-plus/icons-vue'

const props = defineProps<{
  title: string
  subtitle?: string
  userName: string
  roleName?: string
  showProfileButton?: boolean
  regionName?: string | null
  schoolName?: string | null
  gradeName?: string | null
  classroomName?: string | null
}>()

const { title, userName, roleName, regionName, schoolName, gradeName, classroomName } = toRefs(props)

const organizationInfo = computed(() => {
  const info: string[] = []
  if (regionName?.value) info.push(regionName.value)
  if (schoolName?.value) info.push(schoolName.value)
  return info
})

const emit = defineEmits<{
  (e: 'logout'): void
  (e: 'profile'): void
}>()

function handleCommand(command: string) {
  if (command === 'logout') {
    emit('logout')
  } else if (command === 'profile') {
    emit('profile')
  }
}
</script>

<style scoped>
:deep(.el-dropdown-menu__item) {
  border-radius: 6px;
  margin-bottom: 2px;
}
</style>
