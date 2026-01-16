<template>
  <div class="teacher-management">
    <!-- 教师管理子标签 -->
    <el-tabs v-model="activeSubTab" class="teacher-sub-tabs">
      <!-- 教师档案 -->
      <el-tab-pane label="教师档案" name="profile">
        <TeacherProfileTab />
      </el-tab-pane>

      <!-- 教学任务 -->
      <el-tab-pane label="教学任务" name="assignment">
        <TeacherAssignmentTab />
      </el-tab-pane>

      <!-- 职务类型配置 -->
      <el-tab-pane label="职务类型配置" name="position-type">
        <PositionTypeTab />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import TeacherProfileTab from './TeacherProfileTab.vue'
import TeacherAssignmentTab from './TeacherAssignmentTab.vue'
import PositionTypeTab from './PositionTypeTab.vue'

// 当前激活的子标签页
const activeSubTab = ref<'profile' | 'assignment' | 'position-type'>('profile')
</script>

<style scoped>
.teacher-sub-tabs :deep(.el-tabs__header) {
  background: white;
  border-radius: 8px;
  padding: 0 20px;
  margin-bottom: 20px;
}

.teacher-sub-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.teacher-sub-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
  padding: 0 25px;
  height: 45px;
  line-height: 45px;
}

.teacher-sub-tabs :deep(.el-tabs__item.is-active) {
  color: #409eff;
}

.teacher-sub-tabs :deep(.el-tabs__active-bar) {
  height: 3px;
}
</style>
