<template>
  <div class="organization-management p-6 bg-gray-50 min-h-screen">
    <div class="header flex items-center gap-4 mb-8">
      <el-button @click="router.back()" circle>
        <el-icon><ArrowLeft /></el-icon>
      </el-button>
      <div>
        <h1 class="text-3xl font-bold text-gray-900">组织架构管理</h1>
        <p class="text-gray-600 mt-2">构建教育组织层级，统一管理区域、学校、班级及师生档案</p>
      </div>
    </div>

    <!-- 功能卡片分组布局 -->
    <div class="space-y-10">
      <!-- 第一组：基础支撑 -->
      <section class="group-section">
        <div class="section-header flex items-center gap-3 mb-6">
          <div class="w-1.5 h-6 bg-blue-500 rounded-full"></div>
          <div>
            <h2 class="text-xl font-bold text-gray-800">基础支撑</h2>
            <p class="text-xs text-gray-400 mt-0.5">管理行政区域、学校实体及物理教学空间</p>
          </div>
        </div>
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8">
            <AdminFunctionCard
              title="区域管理"
              description="管理省、市、区等区域层级信息"
              icon="Location"
              icon-color="#409eff"
              icon-bg-color="#eff6ff"
              :active="activeTab === 'regions'"
              @click="activeTab = 'regions'"
            />
          </el-col>

          <el-col :xs="24" :sm="12" :md="8">
            <AdminFunctionCard
              title="学校管理"
              description="管理学校基本信息及所属区域"
              icon="OfficeBuilding"
              icon-color="#67c23a"
              icon-bg-color="#f0f9eb"
              :active="activeTab === 'schools'"
              @click="activeTab = 'schools'"
            />
          </el-col>

          <el-col :xs="24" :sm="12" :md="8">
            <AdminFunctionCard
              title="课室管理"
              description="管理物理课室及实验室空间"
              icon="House"
              icon-color="#f56c6c"
              icon-bg-color="#fef2f2"
              :active="activeTab === 'rooms'"
              @click="activeTab = 'rooms'"
            />
          </el-col>
        </el-row>
      </section>

      <!-- 第二组：核心组织 -->
      <section class="group-section">
        <div class="section-header flex items-center gap-3 mb-6">
          <div class="w-1.5 h-6 bg-green-500 rounded-full"></div>
          <div>
            <h2 class="text-xl font-bold text-gray-800">核心组织</h2>
            <p class="text-xs text-gray-400 mt-0.5">管理教学班级及师生人员档案</p>
          </div>
        </div>
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="12">
            <AdminFunctionCard
              title="班级管理"
              description="管理班级信息、年级设置及批量导入"
              icon="UserFilled"
              icon-color="#e6a23c"
              icon-bg-color="#fdf6ec"
              :active="activeTab === 'classrooms'"
              @click="activeTab = 'classrooms'"
            />
          </el-col>

          <el-col :xs="24" :sm="12" :md="12">
            <AdminFunctionCard
              title="人员管理"
              description="统一管理教师、学生档案及职务配置"
              icon="User"
              icon-color="#909399"
              icon-bg-color="#f4f4f5"
              :active="activeTab === 'personnel'"
              @click="activeTab = 'personnel'"
            />
          </el-col>
        </el-row>
      </section>

      <!-- 第三组：业务入口 -->
      <section class="group-section">
        <div class="section-header flex items-center gap-3 mb-6">
          <div class="w-1.5 h-6 bg-purple-500 rounded-full"></div>
          <div>
            <h2 class="text-xl font-bold text-gray-800">教务业务</h2>
            <p class="text-xs text-gray-400 mt-0.5">直接进入考试管理与增值评价分析系统</p>
          </div>
        </div>
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="12">
            <AdminFunctionCard
              title="考试管理系统"
              description="创建考试、导入成绩、管理考场及考号"
              icon="DataAnalysis"
              icon-color="#a855f7"
              icon-bg-color="#f5f3ff"
              is-business
              custom-class="border-purple-500"
              @click="$router.push('/district-admin/exam-management')"
            />
          </el-col>

          <el-col :xs="24" :sm="12" :md="12">
            <AdminFunctionCard
              title="增值评价分析"
              description="生成分析报告、查看学校及学科对比"
              icon="TrendCharts"
              icon-color="#f97316"
              icon-bg-color="#fff7ed"
              is-business
              custom-class="border-orange-500"
              @click="$router.push('/district-admin/value-added')"
            />
          </el-col>
        </el-row>
      </section>
    </div>

    <!-- 详情内容区 -->
    <div class="mt-12 pt-8 border-t border-gray-200">
      <div v-if="activeTab" class="bg-white rounded-xl shadow-sm p-2">
        <RegionManagementCard v-if="activeTab === 'regions'" />
        <SchoolManagementCard v-if="activeTab === 'schools'" />
        <ClassroomManagementCard v-if="activeTab === 'classrooms'" />
        <RoomManagementCard v-if="activeTab === 'rooms'" />
        <PersonnelManagementCard v-if="activeTab === 'personnel'" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import AdminFunctionCard from '@/components/Admin/AdminFunctionCard.vue'
import RegionManagementCard from './OrganizationManagement/RegionManagementCard.vue'
import SchoolManagementCard from './OrganizationManagement/SchoolManagementCard.vue'
import ClassroomManagementCard from './OrganizationManagement/ClassroomManagementCard.vue'
import RoomManagementCard from './OrganizationManagement/RoomManagementCard.vue'
import PersonnelManagementCard from './OrganizationManagement/PersonnelManagementCard.vue'

// 标签页状态
const router = useRouter()
const activeTab = ref<'regions' | 'schools' | 'classrooms' | 'rooms' | 'personnel'>('regions')
</script>

<style scoped>
.organization-management {
  background-color: #f8fafc;
}
</style>
