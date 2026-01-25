<template>
  <div class="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-lg font-bold flex items-center text-slate-800">
        <div
          class="w-8 h-8 rounded-lg bg-yellow-50 flex items-center justify-center mr-3 text-yellow-600"
        >
          <el-icon :size="18"><Trophy /></el-icon>
        </div>
        优秀学生展示
        <span class="ml-3 text-xs font-normal text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full"
          >本学期</span
        >
      </h2>
      <el-button link type="primary" size="small">查看全部</el-button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- 进步之星 -->
      <div class="bg-slate-50/50 rounded-xl p-5 border border-slate-100">
        <div class="flex items-center gap-3 mb-4">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0 bg-white shadow-sm text-indigo-500 border border-slate-100"
          >
            <el-icon :size="20"><TrendCharts /></el-icon>
          </div>
          <div>
            <h3 class="text-base font-bold text-slate-800">进步之星</h3>
            <p class="text-xs text-slate-500">进步幅度最大</p>
          </div>
        </div>
        <div class="flex flex-col gap-3">
          <div
            v-for="(student, index) in topImprovers"
            :key="student.id"
            class="flex items-center gap-3 p-3 bg-white rounded-xl border border-slate-100 hover:border-indigo-200 hover:shadow-md transition-all duration-300 group cursor-default"
          >
            <div
              class="w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs shrink-0"
              :class="getRankBadgeClass(index)"
            >
              {{ index + 1 }}
            </div>
            <div class="flex-1 min-w-0">
              <div
                class="font-semibold text-slate-700 text-sm truncate group-hover:text-indigo-600 transition-colors"
              >
                {{ student.name }}
              </div>
              <div class="text-xs text-slate-400 truncate">{{ student.school }}</div>
            </div>
            <div class="font-bold text-sm text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md">
              +{{ student.improvement }}%
            </div>
          </div>
        </div>
      </div>

      <!-- 成绩优异 -->
      <div class="bg-slate-50/50 rounded-xl p-5 border border-slate-100">
        <div class="flex items-center gap-3 mb-4">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0 bg-white shadow-sm text-rose-500 border border-slate-100"
          >
            <el-icon :size="20"><Medal /></el-icon>
          </div>
          <div>
            <h3 class="text-base font-bold text-slate-800">成绩优异</h3>
            <p class="text-xs text-slate-500">总分最高</p>
          </div>
        </div>
        <div class="flex flex-col gap-3">
          <div
            v-for="(student, index) in topStudents"
            :key="student.id"
            class="flex items-center gap-3 p-3 bg-white rounded-xl border border-slate-100 hover:border-rose-200 hover:shadow-md transition-all duration-300 group cursor-default"
          >
            <div
              class="w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs shrink-0"
              :class="getRankBadgeClass(index)"
            >
              {{ index + 1 }}
            </div>
            <div class="flex-1 min-w-0">
              <div
                class="font-semibold text-slate-700 text-sm truncate group-hover:text-rose-600 transition-colors"
              >
                {{ student.name }}
              </div>
              <div class="text-xs text-slate-400 truncate">{{ student.school }}</div>
            </div>
            <div class="font-bold text-sm text-rose-600 bg-rose-50 px-2 py-0.5 rounded-md">
              {{ student.score }}
            </div>
          </div>
        </div>
      </div>

      <!-- 单科状元 -->
      <div class="bg-slate-50/50 rounded-xl p-5 border border-slate-100">
        <div class="flex items-center gap-3 mb-4">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0 bg-white shadow-sm text-cyan-500 border border-slate-100"
          >
            <el-icon :size="20"><Reading /></el-icon>
          </div>
          <div>
            <h3 class="text-base font-bold text-slate-800">单科状元</h3>
            <p class="text-xs text-slate-500">各科最高分</p>
          </div>
        </div>
        <div class="flex flex-col gap-3">
          <div
            v-for="(item, index) in subjectToppers"
            :key="index"
            class="flex items-center gap-3 p-3 bg-white rounded-xl border border-slate-100 hover:border-cyan-200 hover:shadow-md transition-all duration-300 group cursor-default"
          >
            <div class="shrink-0">
              <span class="text-xs font-bold px-2 py-1 rounded bg-slate-100 text-slate-600">{{
                item.subject
              }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <div
                class="font-semibold text-slate-700 text-sm truncate group-hover:text-cyan-600 transition-colors"
              >
                {{ item.name }}
              </div>
              <div class="text-xs text-slate-400 truncate">{{ item.school }}</div>
            </div>
            <div class="font-bold text-sm text-cyan-600 bg-cyan-50 px-2 py-0.5 rounded-md">
              {{ item.score }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Trophy, TrendCharts, Medal, Reading } from '@element-plus/icons-vue'

export interface StudentImprover {
  id: number
  name: string
  school: string
  class: string
  improvement: number
}

export interface TopStudent {
  id: number
  name: string
  school: string
  class: string
  score: number
}

export interface SubjectTopper {
  subject: string
  name: string
  school: string
  score: number
}

defineProps<{
  topImprovers: StudentImprover[]
  topStudents: TopStudent[]
  subjectToppers: SubjectTopper[]
}>()

function getRankBadgeClass(index: number): string {
  const classes = [
    'bg-yellow-100 text-yellow-700', // Gold
    'bg-slate-200 text-slate-600', // Silver
    'bg-orange-100 text-orange-700', // Bronze
  ]
  return classes[index] || 'bg-slate-50 text-slate-400'
}
</script>
