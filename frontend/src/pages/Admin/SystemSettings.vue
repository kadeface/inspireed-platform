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
      <!-- 管理员管理卡片 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card
          class="function-card"
          shadow="hover"
          @click="activeTab = 'admins'"
          :class="{ 'active-card': activeTab === 'admins' }"
        >
          <div class="card-icon">
            <el-icon :size="40" color="#f56c6c">
              <component :is="'User'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>管理员管理</h3>
            <p>管理超级管理员、区县管理员、学校管理员</p>
          </div>
        </el-card>
      </el-col>

      <!-- 教研员管理卡片 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card
          class="function-card"
          shadow="hover"
          @click="activeTab = 'researchers'"
          :class="{ 'active-card': activeTab === 'researchers' }"
        >
          <div class="card-icon">
            <el-icon :size="40" color="#e6a23c">
              <component :is="'Document'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>教研员管理</h3>
            <p>管理区县和学校教研员账号</p>
          </div>
        </el-card>
      </el-col>

      <!-- 权限管理卡片 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card
          class="function-card"
          shadow="hover"
          @click="activeTab = 'permissions'"
          :class="{ 'active-card': activeTab === 'permissions' }"
        >
          <div class="card-icon">
            <el-icon :size="40" color="#409eff">
              <component :is="'Lock'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>权限管理</h3>
            <p>配置角色权限和访问控制</p>
          </div>
        </el-card>
      </el-col>

      <!-- 系统配置卡片 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card
          class="function-card"
          shadow="hover"
          @click="activeTab = 'config'"
          :class="{ 'active-card': activeTab === 'config' }"
        >
          <div class="card-icon">
            <el-icon :size="40" color="#67c23a">
              <component :is="'Setting'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>系统配置</h3>
            <p>学期、年级、学科等基础配置</p>
          </div>
        </el-card>
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
import { ArrowLeft } from '@element-plus/icons-vue'
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
  background: #f5f7fa;
}

.function-card {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
  overflow: hidden;
}

.function-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.function-card.active-card {
  border: 2px solid #409eff;
}

.function-card :deep(.el-card__body) {
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 12px;
  background: #f5f7fa;
}

.card-content {
  flex: 1;
  min-width: 0;
}

.card-content h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.card-content p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .function-card :deep(.el-card__body) {
    padding: 16px;
  }

  .card-icon {
    width: 48px;
    height: 48px;
  }
}
</style>
