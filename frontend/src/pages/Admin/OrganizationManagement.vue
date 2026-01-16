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
      <p class="text-gray-600 mt-2">管理区域、学校和班级成员信息</p>
    </div>

    <!-- 功能卡片网格 -->
    <el-row :gutter="20" class="mb-6">
      <!-- 区域管理卡片 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
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
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
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

      <!-- 班级成员管理卡片 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
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
            <h3>班级成员管理</h3>
            <p>添加教师和学生到班级，管理班级成员关系</p>
          </div>
        </el-card>
      </el-col>

      <!-- 教师教学任务卡片 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card
          class="function-card"
          shadow="hover"
          @click="activeTab = 'teacher-assignments'"
          :class="{ 'active-card': activeTab === 'teacher-assignments' }"
        >
          <div class="card-icon">
            <el-icon :size="40" color="#909399">
              <component :is="'Document'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>教师教学任务</h3>
            <p>管理教师与班级、学科的关联关系，分配教学任务</p>
          </div>
        </el-card>
      </el-col>

      <!-- 职务类型管理卡片 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card
          class="function-card"
          shadow="hover"
          @click="activeTab = 'position-types'"
          :class="{ 'active-card': activeTab === 'position-types' }"
        >
          <div class="card-icon">
            <el-icon :size="40" color="#f56c6c">
              <component :is="'Setting'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>职务类型管理</h3>
            <p>自定义教师职务类型，如校长、教研室主任等</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 功能说明提示 -->
    <div v-if="activeTab === 'position-types'" class="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
      <svg class="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      <div class="text-sm text-gray-700">
        <p class="font-medium text-gray-900 mb-1">功能说明</p>
        <p>管理教师职务类型，支持自定义职务（如：校长、教研室主任等）。系统预设的职务类型（班主任、学科教师）不能删除，只能停用。</p>
      </div>
    </div>

    <!-- 区域管理 -->
    <RegionManagementCard v-if="activeTab === 'regions'" />

    <!-- 学校管理 -->
    <SchoolManagementCard v-if="activeTab === 'schools'" />

    <!-- 班级成员管理 -->
    <ClassroomManagementCard v-if="activeTab === 'classrooms'" />

    <!-- 教师教学任务 -->
    <TeacherAssignmentCard v-if="activeTab === 'teacher-assignments'" />

    <!-- 职务类型管理 -->
    <PositionTypeCard v-if="activeTab === 'position-types'" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import RegionManagementCard from './OrganizationManagement/RegionManagementCard.vue'
import SchoolManagementCard from './OrganizationManagement/SchoolManagementCard.vue'
import ClassroomManagementCard from './OrganizationManagement/ClassroomManagementCard.vue'
import TeacherAssignmentCard from './OrganizationManagement/TeacherAssignmentCard.vue'
import PositionTypeCard from './OrganizationManagement/PositionTypeCard.vue'

// 标签页状态
const activeTab = ref<'regions' | 'schools' | 'classrooms' | 'teacher-assignments' | 'position-types'>('regions')
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
