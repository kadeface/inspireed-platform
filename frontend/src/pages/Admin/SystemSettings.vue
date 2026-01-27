<template>
  <div class="system-settings p-6">
    <div class="header flex items-center gap-4 mb-8">
      <el-button @click="router.back()" circle>
        <el-icon><ArrowLeft /></el-icon>
      </el-button>
      <div>
        <h1 class="text-3xl font-bold text-gray-900">系统设置</h1>
        <p class="text-gray-600 mt-2">管理员专属 - 管理系统配置和权限</p>
      </div>
    </div>

    <!-- 功能卡片网格 -->
    <el-row :gutter="20" class="mb-6">
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <AdminFunctionCard
          title="管理员管理"
          description="管理超级管理员、区县管理员、学校管理员"
          :icon="User"
          icon-color="#4F46E5"
          icon-bg-color="#EEF2FF"
          text-color="#1E293B"
          description-color="#64748B"
          :active="activeTab === 'admins'"
          custom-class="bg-white border border-slate-200"
          @click="activeTab = 'admins'"
        />
      </el-col>

      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <AdminFunctionCard
          title="教研员管理"
          description="管理区县和学校教研员账号"
          :icon="Document"
          icon-color="#EA580C"
          icon-bg-color="#FFF7ED"
          text-color="#1E293B"
          description-color="#64748B"
          :active="activeTab === 'researchers'"
          custom-class="bg-white border border-slate-200"
          @click="activeTab = 'researchers'"
        />
      </el-col>

      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <AdminFunctionCard
          title="权限管理"
          description="配置角色权限和访问控制"
          :icon="Lock"
          icon-color="#059669"
          icon-bg-color="#ECFDF5"
          text-color="#1E293B"
          description-color="#64748B"
          :active="activeTab === 'permissions'"
          custom-class="bg-white border border-slate-200"
          @click="activeTab = 'permissions'"
        />
      </el-col>

      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <AdminFunctionCard
          title="系统配置"
          description="学期、年级、学科等基础配置"
          :icon="Setting"
          icon-color="#7C3AED"
          icon-bg-color="#F5F3FF"
          text-color="#1E293B"
          description-color="#64748B"
          :active="activeTab === 'config'"
          custom-class="bg-white border border-slate-200"
          @click="activeTab = 'config'"
        />
      </el-col>
    </el-row>

    <!-- 管理员管理 -->
    <AdminManagementCard v-if="activeTab === 'admins'" />

    <!-- 教研员管理 -->
    <ResearcherManagementCard v-if="activeTab === 'researchers'" />

    <!-- 权限管理 -->
    <PermissionManagementCard v-if="activeTab === 'permissions'" />

    <!-- 系统配置 -->
    <SystemConfigCard v-if="activeTab === 'config'" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, User, Document, Lock, Setting } from '@element-plus/icons-vue'
import AdminFunctionCard from '@/components/Admin/AdminFunctionCard.vue'
import AdminManagementCard from './SystemSettings/AdminManagementCard.vue'
import ResearcherManagementCard from './SystemSettings/ResearcherManagementCard.vue'
import PermissionManagementCard from './SystemSettings/PermissionManagementCard.vue'
import SystemConfigCard from './SystemSettings/SystemConfigCard.vue'

// 标签页状态
const router = useRouter()
const activeTab = ref<'admins' | 'researchers' | 'permissions' | 'config'>('admins')
</script>

<style scoped>
.system-settings {
  padding: 20px;
  min-height: 100vh;
  background: #f8fafc;
}
</style>
