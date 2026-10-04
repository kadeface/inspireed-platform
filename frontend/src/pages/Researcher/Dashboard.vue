<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50/30 to-teal-50/50">
    <!-- 统一头部 -->
    <DashboardHeader
      title="教研工作台"
      subtitle="管理课程体系和教学资源"
      :user-name="userName"
      :role-name="roleName"
      @logout="handleLogout"
    />

    <!-- 主内容区 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 快捷入口 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      <!-- 课程体系管理 -->
      <router-link 
        to="/researcher/curriculum"
        class="quick-link-card rounded-2xl border border-gray-100 bg-white/80 p-6 shadow-lg backdrop-blur-sm transition-all hover:-translate-y-1 hover:shadow-xl"
      >
        <div class="flex items-center mb-4">
          <span class="text-4xl mr-3">📚</span>
          <h2 class="text-xl font-semibold">课程体系管理</h2>
        </div>
        <p class="text-gray-600">管理学科、年级、课程和章节</p>
        <div class="mt-4 inline-flex items-center rounded-xl px-3 py-1.5 text-sm font-medium text-emerald-700 transition-all hover:bg-emerald-50">进入管理 →</div>
      </router-link>

      <!-- 官方资源管理 -->
      <div class="quick-link-card rounded-2xl border border-gray-100 bg-white/80 p-6 shadow-lg opacity-60">
        <div class="flex items-center mb-4">
          <span class="text-4xl mr-3">📁</span>
          <h2 class="text-xl font-semibold">官方资源管理</h2>
        </div>
        <p class="text-gray-600">上传和管理教学资源</p>
        <div class="mt-4 text-gray-400 font-medium">开发中...</div>
      </div>

      <!-- 教研观摩 -->
      <router-link 
        to="/researcher/curriculum"
        class="quick-link-card rounded-2xl border border-gray-100 bg-white/80 p-6 shadow-lg backdrop-blur-sm transition-all hover:-translate-y-1 hover:shadow-xl"
      >
        <div class="flex items-center mb-4">
          <span class="text-4xl mr-3">👀</span>
          <h2 class="text-xl font-semibold">导入教师教案</h2>
        </div>
        <p class="text-gray-600">导入其他教师编写的教案到系统中</p>
        <div class="mt-4 inline-flex items-center rounded-xl px-3 py-1.5 text-sm font-medium text-emerald-700 transition-all hover:bg-emerald-50">进入导入 →</div>
      </router-link>

      <!-- 数据分析 -->
      <div class="quick-link-card rounded-2xl border border-gray-100 bg-white/80 p-6 shadow-lg opacity-60">
        <div class="flex items-center mb-4">
          <span class="text-4xl mr-3">📊</span>
          <h2 class="text-xl font-semibold">数据分析</h2>
        </div>
        <p class="text-gray-600">课程使用和教师活跃度统计</p>
        <div class="mt-4 text-gray-400 font-medium">开发中...</div>
      </div>
    </div>

    <!-- 系统说明 -->
    <div class="mt-8 rounded-2xl border border-emerald-100 bg-white/80 p-6 shadow-sm">
      <h3 class="mb-3 text-lg font-semibold text-slate-900">教研员职责</h3>
      <ul class="space-y-2 text-slate-700">
        <li class="flex items-start">
          <span class="mr-2">✓</span>
          <span>管理课程体系：创建和维护学科、年级、课程结构</span>
        </li>
        <li class="flex items-start">
          <span class="mr-2">✓</span>
          <span>管理官方资源：上传、编辑教学资源并关联到章节</span>
        </li>
        <li class="flex items-start">
          <span class="mr-2">✓</span>
          <span>教研观摩：查看所有教师教案，推荐优秀案例</span>
        </li>
        <li class="flex items-start">
          <span class="mr-2">✓</span>
          <span>数据分析：统计课程使用情况和教师活跃度</span>
        </li>
      </ul>
    </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { getRoleDisplayName } from '@/types/user'
import DashboardHeader from '@/components/Common/DashboardHeader.vue'

const router = useRouter()
const userStore = useUserStore()

// 用户名
const userName = computed(() => userStore.user?.full_name || userStore.user?.username || '教研员')
const roleName = computed(() => getRoleDisplayName(userStore.user?.role))

// 退出登录
function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.quick-link-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.quick-link-card:not(.opacity-60):hover {
  transform: translateY(-4px);
}
</style>

