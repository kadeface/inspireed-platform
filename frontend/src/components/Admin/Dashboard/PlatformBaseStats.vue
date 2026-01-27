<template>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <!-- 用户统计 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold mb-3 flex items-center text-gray-800">
        <el-icon class="mr-2 text-blue-500" :size="20"><User /></el-icon>
        用户统计
      </h2>
      <div class="grid grid-cols-4 gap-3">
        <div class="p-3 bg-gray-50 rounded-lg text-center">
          <div class="text-xs text-gray-500 mb-1">总用户</div>
          <div class="text-xl font-bold text-gray-800">{{ userStats.total_users }}</div>
        </div>
        <div class="p-3 bg-gray-50 rounded-lg text-center">
          <div class="text-xs text-gray-500 mb-1">教师</div>
          <div class="text-xl font-bold text-blue-600">{{ userStats.teacher_count }}</div>
        </div>
        <div class="p-3 bg-gray-50 rounded-lg text-center">
          <div class="text-xs text-gray-500 mb-1">学生</div>
          <div class="text-xl font-bold text-green-600">{{ userStats.student_count }}</div>
        </div>
        <div class="p-3 bg-gray-50 rounded-lg text-center">
          <div class="text-xs text-gray-500 mb-1">激活率</div>
          <div class="text-xl font-bold text-purple-600">{{ activationRate }}%</div>
        </div>
      </div>
    </div>

    <!-- 内容统计 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold mb-3 flex items-center text-gray-800">
        <el-icon class="mr-2 text-indigo-500" :size="20"><Collection /></el-icon>
        内容统计
      </h2>
      <div class="grid grid-cols-4 gap-3">
        <div class="p-3 bg-gray-50 rounded-lg text-center">
          <div class="text-xs text-gray-500 mb-1">课程</div>
          <div class="text-xl font-bold text-gray-800">{{ contentStats.total_courses }}</div>
        </div>
        <div class="p-3 bg-gray-50 rounded-lg text-center">
          <div class="text-xs text-gray-500 mb-1">教案</div>
          <div class="text-xl font-bold text-blue-600">{{ contentStats.total_lessons }}</div>
        </div>
        <div class="p-3 bg-gray-50 rounded-lg text-center">
          <div class="text-xs text-gray-500 mb-1">资源</div>
          <div class="text-xl font-bold text-green-600">{{ contentStats.total_resources }}</div>
        </div>
        <div class="p-3 bg-gray-50 rounded-lg text-center">
          <div class="text-xs text-gray-500 mb-1">发布率</div>
          <div class="text-xl font-bold text-purple-600">{{ lessonPublishRate }}%</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { User, Collection } from '@element-plus/icons-vue'

interface UserStats {
  total_users: number
  teacher_count: number
  student_count: number
  active_users: number
}

interface ContentStats {
  total_courses: number
  total_lessons: number
  total_resources: number
  published_lessons: number
}

defineProps<{
  userStats: UserStats
  contentStats: ContentStats
  activationRate: number
  lessonPublishRate: number
}>()
</script>
