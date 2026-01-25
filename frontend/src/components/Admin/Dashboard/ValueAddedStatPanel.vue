<template>
  <div class="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-lg font-bold flex items-center text-slate-800">
        <div
          class="w-8 h-8 rounded-lg bg-orange-50 flex items-center justify-center mr-3 text-orange-600"
        >
          <el-icon :size="18"><TrendCharts /></el-icon>
        </div>
        增值评价
      </h2>
      <router-link
        to="/district-admin/value-added"
        class="text-sm font-medium text-orange-600 hover:text-orange-700 flex items-center transition-colors"
      >
        查看详情 <el-icon class="ml-1"><ArrowRight /></el-icon>
      </router-link>
    </div>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="stat-item group">
        <div class="label">评价报告</div>
        <div class="value text-slate-800">{{ stats.totalReports }}</div>
        <div class="sub-label text-slate-400">份报告</div>
      </div>
      <div class="stat-item group">
        <div class="label">平均进步</div>
        <div class="value text-emerald-600">
          +{{ stats.avgProgress }}<span class="text-lg">%</span>
        </div>
        <div class="sub-label text-emerald-200">增值幅度</div>
      </div>
      <div class="stat-item group">
        <div class="label">进步学校</div>
        <div class="value text-blue-600">{{ stats.improvedSchools }}</div>
        <div class="sub-label text-blue-200">所学校</div>
      </div>
      <div class="stat-item group">
        <div class="label">优秀班级</div>
        <div class="value text-purple-600">{{ stats.excellentClasses }}</div>
        <div class="sub-label text-purple-200">个班级</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { TrendCharts, ArrowRight } from '@element-plus/icons-vue'

interface ValueAddedStats {
  totalReports: number
  avgProgress: number
  improvedSchools: number
  excellentClasses: number
}

defineProps<{
  stats: ValueAddedStats
}>()
</script>

<style scoped>
.stat-item {
  @apply p-4 rounded-xl bg-slate-50 border border-slate-100 text-center transition-all duration-300;
}
.stat-item:hover {
  @apply bg-white border-orange-100 shadow-md transform -translate-y-1;
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
