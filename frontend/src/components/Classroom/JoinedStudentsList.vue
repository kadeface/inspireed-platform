<template>
  <div v-if="students.length > 0" class="joined-students-list">
    <div class="joined-students-header">
      <span class="joined-students-title">已加入学生（{{ students.length }} 人）</span>
    </div>
    <div class="joined-students-grid">
      <div
        v-for="student in displayStudents"
        :key="student.id || student.user_id || student.username"
        class="joined-student-item"
      >
        <div class="student-avatar">
          {{ getStudentInitial(student) }}
        </div>
        <div class="student-name">
          {{ student.full_name || student.username || '学生' }}
        </div>
      </div>
      <div v-if="students.length > maxDisplay" class="joined-student-item joined-student-more">
        <div class="student-avatar">+{{ students.length - maxDisplay }}</div>
        <div class="student-name">更多</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Student {
  id?: number
  user_id?: number
  username?: string
  full_name?: string
}

interface Props {
  students: Student[]
  maxDisplay?: number
}

const props = withDefaults(defineProps<Props>(), {
  students: () => [],
  maxDisplay: 12
})

// 限制显示的学生数量
const displayStudents = computed(() => {
  return props.students.slice(0, props.maxDisplay)
})

// 获取学生姓名的首字母
function getStudentInitial(student: Student): string {
  const name = student.full_name || student.username || '学生'
  return name.charAt(0).toUpperCase()
}
</script>

<style scoped>
.joined-students-list {
  margin-bottom: 1rem;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.joined-students-header {
  margin-bottom: 0.75rem;
  padding: 0 0.5rem;
}

.joined-students-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
}

.joined-students-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.5rem;
}

.joined-student-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.375rem;
  padding: 0.75rem 0.5rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.joined-student-item:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
  transform: translateY(-2px);
}

.joined-student-more {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #3b82f6;
}

.student-avatar {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 1rem;
  font-weight: 700;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
}

.student-name {
  font-size: 0.75rem;
  font-weight: 500;
  color: #374151;
  text-align: center;
  word-break: break-all;
  line-height: 1.2;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
</style>
