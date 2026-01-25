<template>
  <div class="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-lg font-bold flex items-center text-slate-800">
        <div
          class="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center mr-3 text-indigo-600"
        >
          <el-icon :size="18"><DataLine /></el-icon>
        </div>
        考试统计
      </h2>
      <router-link
        to="/district-admin/exam-management"
        class="text-sm font-medium text-indigo-600 hover:text-indigo-700 flex items-center transition-colors"
      >
        查看详情 <el-icon class="ml-1"><ArrowRight /></el-icon>
      </router-link>
    </div>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="stat-item group">
        <div class="label">本学期考试</div>
        <div class="value text-slate-800">{{ stats.totalExams }}</div>
        <div class="sub-label text-slate-400">已完成</div>
      </div>
      <div class="stat-item group">
        <div class="label">参与学生</div>
        <div class="value text-blue-600">{{ stats.totalStudents }}</div>
        <div class="sub-label text-blue-200">人次</div>
      </div>
      <div class="stat-item group">
        <div class="label">成绩录入</div>
        <div class="value text-emerald-600">
          {{ stats.completedRate }}<span class="text-lg">%</span>
        </div>
        <div class="sub-label text-emerald-200">完成率</div>
      </div>
      <div class="stat-item group">
        <div class="label">待处理</div>
        <div class="value text-amber-500">{{ stats.pendingTasks }}</div>
        <div class="sub-label text-amber-200">任务</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { DataLine, ArrowRight } from '@element-plus/icons-vue'

interface ExamStats {
  totalExams: number
  totalStudents: number
  completedRate: number
  pendingTasks: number
}

defineProps<{
  stats: ExamStats
}>()
</script>

<style scoped>
.stat-item {
  @apply p-4 rounded-xl bg-slate-50 border border-slate-100 text-center transition-all duration-300;
}
.stat-item:hover {
  @apply bg-white border-indigo-100 shadow-md transform -translate-y-1;
}
.label {
  @apply text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2;
}
.value {
  @apply text-3xl font-bold leading-none mb-1;
}
.sub-label {
  @apply text-xs font-medium;
}
</style>
