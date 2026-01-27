<template>
  <div class="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-lg font-bold flex items-center text-slate-800">
        <div
          class="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center mr-3 text-blue-600"
        >
          <el-icon :size="18"><School /></el-icon>
        </div>
        学校亮点
        <span class="ml-3 text-xs font-normal text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full"
          >本学期</span
        >
      </h2>
      <el-button link type="primary" size="small">查看全部</el-button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- 最佳进步学校 -->
      <div class="bg-slate-50/50 rounded-xl p-5 border border-slate-100">
        <div class="flex items-center gap-3 mb-4">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center bg-white shadow-sm text-blue-500 border border-slate-100"
          >
            <el-icon :size="20"><TrendCharts /></el-icon>
          </div>
          <h3 class="text-base font-bold text-slate-800">最佳进步学校</h3>
        </div>
        <div class="flex flex-col gap-3">
          <div
            v-for="(school, index) in topImprovedSchools"
            :key="school.id"
            class="flex items-center gap-3 p-3 bg-white rounded-xl border border-slate-100 hover:border-blue-200 hover:shadow-md transition-all duration-300 group cursor-default"
          >
            <div
              class="w-6 h-6 flex items-center justify-center font-bold text-sm shrink-0"
              :class="getRankColor(index)"
            >
              {{ index + 1 }}
            </div>
            <div class="flex-1 min-w-0">
              <div
                class="font-semibold text-slate-700 text-sm truncate group-hover:text-blue-600 transition-colors mb-0.5"
              >
                {{ school.name }}
              </div>
              <div class="text-xs font-medium text-emerald-600 bg-emerald-50 w-fit px-1.5 rounded">
                +{{ school.improvement }}% 进步
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 教学质量优秀 -->
      <div class="bg-slate-50/50 rounded-xl p-5 border border-slate-100">
        <div class="flex items-center gap-3 mb-4">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center bg-white shadow-sm text-rose-500 border border-slate-100"
          >
            <el-icon :size="20"><StarFilled /></el-icon>
          </div>
          <h3 class="text-base font-bold text-slate-800">教学质量优秀</h3>
        </div>
        <div class="flex flex-col gap-3">
          <div
            v-for="(school, index) in topQualitySchools"
            :key="school.id"
            class="flex items-center gap-3 p-3 bg-white rounded-xl border border-slate-100 hover:border-rose-200 hover:shadow-md transition-all duration-300 group cursor-default"
          >
            <div
              class="w-6 h-6 flex items-center justify-center font-bold text-sm shrink-0"
              :class="getRankColor(index)"
            >
              {{ index + 1 }}
            </div>
            <div class="flex-1 min-w-0">
              <div
                class="font-semibold text-slate-700 text-sm truncate group-hover:text-rose-600 transition-colors mb-0.5"
              >
                {{ school.name }}
              </div>
              <div class="text-xs font-medium text-rose-600 bg-rose-50 w-fit px-1.5 rounded">
                均分 {{ school.avgScore }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 增值评价突出 -->
      <div class="bg-slate-50/50 rounded-xl p-5 border border-slate-100">
        <div class="flex items-center gap-3 mb-4">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center bg-white shadow-sm text-amber-500 border border-slate-100"
          >
            <el-icon :size="20"><Aim /></el-icon>
          </div>
          <h3 class="text-base font-bold text-slate-800">增值评价突出</h3>
        </div>
        <div class="flex flex-col gap-3">
          <div
            v-for="(school, index) in topValueAddedSchools"
            :key="school.id"
            class="flex items-center gap-3 p-3 bg-white rounded-xl border border-slate-100 hover:border-amber-200 hover:shadow-md transition-all duration-300 group cursor-default"
          >
            <div
              class="w-6 h-6 flex items-center justify-center font-bold text-sm shrink-0"
              :class="getRankColor(index)"
            >
              {{ index + 1 }}
            </div>
            <div class="flex-1 min-w-0">
              <div
                class="font-semibold text-slate-700 text-sm truncate group-hover:text-amber-600 transition-colors mb-0.5"
              >
                {{ school.name }}
              </div>
              <div class="text-xs font-medium text-amber-600 bg-amber-50 w-fit px-1.5 rounded">
                指数 {{ school.valueIndex }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { School, TrendCharts, StarFilled, Aim } from '@element-plus/icons-vue'

export interface SchoolImproved {
  id: number
  name: string
  improvement: number
}

export interface SchoolQuality {
  id: number
  name: string
  avgScore: number
}

export interface SchoolValueAdded {
  id: number
  name: string
  valueIndex: number
}

defineProps<{
  topImprovedSchools: SchoolImproved[]
  topQualitySchools: SchoolQuality[]
  topValueAddedSchools: SchoolValueAdded[]
}>()

function getRankColor(index: number) {
  const colors = ['text-yellow-600', 'text-slate-400', 'text-orange-600']
  return colors[index] || 'text-slate-300'
}
</script>
