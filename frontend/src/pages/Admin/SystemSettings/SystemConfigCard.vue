<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-900">系统基础配置</h2>
      <p class="text-gray-600">管理系统的基础数据</p>
    </div>

    <!-- 快速入口卡片 -->
    <el-row :gutter="20" class="mb-6">
      <!-- 学期管理 -->
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="config-card" shadow="hover" @click="goToSemesters">
          <div class="card-icon">
            <el-icon :size="40" color="#409eff">
              <component :is="'Calendar'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>学期管理</h3>
            <p>管理学年学期</p>
          </div>
        </el-card>
      </el-col>

      <!-- 课程体系（学科、年级） -->
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="config-card" shadow="hover" @click="goToCurriculum">
          <div class="card-icon">
            <el-icon :size="40" color="#67c23a">
              <component :is="'Reading'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>课程体系</h3>
            <p>学科、年级、课程管理</p>
          </div>
        </el-card>
      </el-col>

      <!-- 系统参数 -->
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="config-card disabled-card" shadow="hover">
          <div class="card-icon">
            <el-icon :size="40" color="#909399">
              <component :is="'Tools'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>系统参数</h3>
            <p>全局配置（待开发）</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 功能说明 -->
    <el-alert
      title="💡 使用说明"
      type="info"
      :closable="false"
      show-icon
    >
      <template #default>
        <ul class="space-y-1 text-sm">
          <li>• <strong>学期管理：</strong>在考试管理中也可以快捷访问学期设置</li>
          <li>• <strong>课程体系：</strong>统一管理学科、年级和课程，影响考试科目选择</li>
          <li>• <strong>系统参数：</strong>全局系统配置，如文件上传限制、分页大小等</li>
        </ul>
      </template>
    </el-alert>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goToSemesters = () => {
  router.push('/district-admin/semesters')
}

const goToCurriculum = () => {
  router.push('/admin/curriculum')
}
</script>

<style scoped>
.config-card {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
  overflow: hidden;
}

.config-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.config-card.disabled-card {
  opacity: 0.6;
  cursor: not-allowed;
}

.config-card.disabled-card:hover {
  transform: none;
}

.config-card :deep(.el-card__body) {
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
</style>
