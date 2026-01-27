<template>
  <div class="space-y-6">
    <!-- 功能说明 -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <p class="text-sm text-blue-800">
        💡 <strong>功能说明：</strong>统一管理教师和学生档案，包括教学任务分配、职务类型配置、班级成员管理等人员相关功能。
      </p>
    </div>

    <!-- 人员类型切换标签 -->
    <el-tabs v-model="activeTab" class="personnel-tabs">
      <!-- 教师管理 -->
      <el-tab-pane label="教师管理" name="teachers">
        <TeacherManagementTab />
      </el-tab-pane>

      <!-- 学生管理 -->
      <el-tab-pane label="学生管理" name="students">
        <StudentManagementTab />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import TeacherManagementTab from './TeacherManagementTab.vue'
import StudentManagementTab from './StudentManagementTab.vue'

// 当前激活的标签页
const activeTab = ref<'teachers' | 'students'>('teachers')
</script>

<style scoped>
.personnel-tabs :deep(.el-tabs__header) {
  background: white;
  border-radius: 8px;
  padding: 0 20px;
  margin-bottom: 20px;
}

.personnel-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.personnel-tabs :deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 500;
  padding: 0 30px;
  height: 50px;
  line-height: 50px;
}

.personnel-tabs :deep(.el-tabs__item.is-active) {
  color: #409eff;
}

.personnel-tabs :deep(.el-tabs__active-bar) {
  height: 3px;
}
</style>
