<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
    <AdminFunctionCard
      title="组织架构"
      description="管理区域、学校、班级和人员"
      :icon="OfficeBuilding"
      icon-color="#3B82F6"
      icon-bg-color="#EFF6FF"
      text-color="#1E293B"
      description-color="#64748B"
      custom-class="bg-white border border-slate-200 nav-card"
      @click="router.push('/admin/organization')"
    />
    <AdminFunctionCard
      title="考试管理"
      description="考试组织和成绩管理"
      :icon="DataLine"
      icon-color="#8B5CF6"
      icon-bg-color="#F5F3FF"
      text-color="#1E293B"
      description-color="#64748B"
      custom-class="bg-white border border-slate-200 nav-card"
      @click="router.push('/district-admin/exam-management')"
    />
    <AdminFunctionCard
      title="增值评价"
      description="教学效果分析与评价报告"
      :icon="TrendCharts"
      icon-color="#F59E0B"
      icon-bg-color="#FFFBEB"
      text-color="#1E293B"
      description-color="#64748B"
      custom-class="bg-white border border-slate-200 nav-card"
      @click="router.push('/district-admin/value-added')"
    />
    <AdminFunctionCard
      title="系统设置"
      description="管理员和权限配置"
      :icon="Setting"
      icon-color="#64748B"
      icon-bg-color="#F1F5F9"
      text-color="#1E293B"
      description-color="#64748B"
      custom-class="bg-white border border-slate-200 nav-card"
      @click="router.push('/admin/settings')"
    />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { OfficeBuilding, DataLine, TrendCharts, Setting } from '@element-plus/icons-vue'
import AdminFunctionCard from '../AdminFunctionCard.vue'

const router = useRouter()
</script>

<style scoped>
:deep(.nav-card) {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
:deep(.nav-card:hover) {
  transform: translateY(-4px);
  box-shadow: 0 12px 20px -8px rgba(0, 0, 0, 0.08);
  border-color: #3b82f6;
}
</style>
