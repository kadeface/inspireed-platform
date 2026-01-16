<template>
  <div class="organization-management p-6">
    <!-- 面包屑导航 -->
    <div class="mb-4">
      <router-link
        to="/admin"
        class="text-blue-600 hover:text-blue-800 flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        返回管理员首页
      </router-link>
    </div>

    <div class="header mb-6">
      <h1 class="text-3xl font-bold text-gray-900">组织架构管理</h1>
      <p class="text-gray-600 mt-2">管理区域、学校、班级和教师相关信息</p>
    </div>

    <!-- 功能卡片网格 -->
    <el-row :gutter="20" class="mb-6">
      <!-- 区域管理卡片 -->
      <el-col :xs="24" :sm="12" :md="6" :lg="6">
        <el-card
          class="function-card"
          shadow="hover"
          @click="activeTab = 'regions'"
          :class="{ 'active-card': activeTab === 'regions' }"
        >
          <div class="card-icon">
            <el-icon :size="40" color="#409eff">
              <component :is="'Location'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>区域管理</h3>
            <p>管理省、市、区等区域层级信息，建立完整的区域组织架构</p>
          </div>
        </el-card>
      </el-col>

      <!-- 学校管理卡片 -->
      <el-col :xs="24" :sm="12" :md="6" :lg="6">
        <el-card
          class="function-card"
          shadow="hover"
          @click="activeTab = 'schools'"
          :class="{ 'active-card': activeTab === 'schools' }"
        >
          <div class="card-icon">
            <el-icon :size="40" color="#67c23a">
              <component :is="'OfficeBuilding'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>学校管理</h3>
            <p>管理学校基本信息，包括学校名称、代码、所属区域等</p>
          </div>
        </el-card>
      </el-col>

      <!-- 班级管理卡片 -->
      <el-col :xs="24" :sm="12" :md="6" :lg="6">
        <el-card
          class="function-card"
          shadow="hover"
          @click="activeTab = 'classrooms'"
          :class="{ 'active-card': activeTab === 'classrooms' }"
        >
          <div class="card-icon">
            <el-icon :size="40" color="#e6a23c">
              <component :is="'UserFilled'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>班级管理</h3>
            <p>管理班级信息、批量导入班级</p>
          </div>
        </el-card>
      </el-col>

      <!-- 课室管理卡片 -->
      <el-col :xs="24" :sm="12" :md="6" :lg="6">
        <el-card
          class="function-card"
          shadow="hover"
          @click="activeTab = 'rooms'"
          :class="{ 'active-card': activeTab === 'rooms' }"
        >
          <div class="card-icon">
            <el-icon :size="40" color="#f56c6c">
              <component :is="'House'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>课室管理</h3>
            <p>管理物理课室、实验室、多媒体教室等教学空间</p>
          </div>
        </el-card>
      </el-col>

      <!-- 人员管理卡片 -->
      <el-col :xs="24" :sm="12" :md="6" :lg="6">
        <el-card
          class="function-card"
          shadow="hover"
          @click="activeTab = 'personnel'"
          :class="{ 'active-card': activeTab === 'personnel' }"
        >
          <div class="card-icon">
            <el-icon :size="40" color="#909399">
              <component :is="'User'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>人员管理</h3>
            <p>管理教师和学生档案、教学任务、职务类型配置</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 区域管理 -->
    <RegionManagementCard v-if="activeTab === 'regions'" />

    <!-- 学校管理 -->
    <SchoolManagementCard v-if="activeTab === 'schools'" />

    <!-- 班级管理 -->
    <ClassroomManagementCard v-if="activeTab === 'classrooms'" />

    <!-- 课室管理 -->
    <RoomManagementCard v-if="activeTab === 'rooms'" />

    <!-- 人员管理 -->
    <PersonnelManagementCard v-if="activeTab === 'personnel'" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import RegionManagementCard from './OrganizationManagement/RegionManagementCard.vue'
import SchoolManagementCard from './OrganizationManagement/SchoolManagementCard.vue'
import ClassroomManagementCard from './OrganizationManagement/ClassroomManagementCard.vue'
import RoomManagementCard from './OrganizationManagement/RoomManagementCard.vue'
import PersonnelManagementCard from './OrganizationManagement/PersonnelManagementCard.vue'

// 标签页状态
const activeTab = ref<'regions' | 'schools' | 'classrooms' | 'rooms' | 'personnel'>('regions')
</script>

<style scoped>
.organization-management {
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
