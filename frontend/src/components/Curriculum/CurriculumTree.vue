<template>
  <div class="curriculum-tree bg-white rounded-lg shadow p-4">
    <h3 class="text-lg font-semibold mb-4">课程筛选</h3>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-4 text-gray-500">
      加载中...
    </div>

    <!-- Tree Content -->
    <div v-else-if="curriculumTree" class="tree-content">
      <!-- All Lessons Option -->
      <div
        class="tree-item p-2 rounded cursor-pointer mb-2"
        :class="{ 'bg-blue-100 text-blue-700 font-medium': !selectedCourseId }"
        @click="selectAll"
      >
        <span class="text-sm">📚 全部教案</span>
        <span class="text-xs text-gray-600 ml-2">({{ curriculumTree.total_lessons }})</span>
      </div>

      <!-- Subjects -->
      <div
        v-for="subject in curriculumTree.subjects"
        :key="subject.id"
        class="subject-item mb-2"
      >
        <div 
          class="subject-header flex items-center justify-between p-2 rounded cursor-pointer hover:bg-gray-50"
          @click="toggleSubject(subject.id)"
        >
          <div class="flex items-center gap-2">
            <span class="text-sm">{{ expandedSubjects.has(subject.id) ? '▼' : '▶' }}</span>
            <span class="font-medium text-sm">{{ subject.name }}</span>
            <span class="text-xs text-gray-500">({{ subject.lesson_count }})</span>
          </div>
        </div>

        <!-- Grades -->
        <div v-if="expandedSubjects.has(subject.id)" class="grades ml-4 mt-1">
          <div
            v-for="grade in subject.grades"
            :key="grade.id"
            class="grade-item mb-1"
          >
            <div 
              class="grade-header flex items-center justify-between p-2 rounded cursor-pointer hover:bg-gray-50"
              @click="toggleGrade(subject.id, grade.id)"
            >
              <div class="flex items-center gap-2">
                <span class="text-xs">{{ expandedGrades.has(`${subject.id}-${grade.id}`) ? '▼' : '▶' }}</span>
                <span class="text-sm">{{ grade.name }}</span>
                <span class="text-xs text-gray-500">({{ grade.lesson_count }})</span>
              </div>
            </div>

            <!-- Courses -->
            <div v-if="expandedGrades.has(`${subject.id}-${grade.id}`)" class="courses ml-4 mt-1">
              <div
                v-for="course in grade.courses"
                :key="course.id"
                class="course-item p-2 rounded cursor-pointer mb-1 hover:bg-gray-50"
                :class="{ 'bg-blue-100 text-blue-700 font-medium': selectedCourseId === course.id }"
                @click="selectCourse(course.id)"
              >
                <div class="flex items-center justify-between">
                  <span class="text-sm">{{ course.name }}</span>
                  <span class="text-xs text-gray-500">({{ course.lesson_count }})</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-4 text-gray-500 text-sm">
      暂无数据
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import curriculumService from '@/services/curriculum'
import type { CurriculumTree as CurriculumTreeType } from '@/types/curriculum'

const emit = defineEmits<{
  'course-selected': [courseId: number | null]
}>()

const loading = ref(false)
const curriculumTree = ref<CurriculumTreeType | null>(null)
const expandedSubjects = ref(new Set<number>())
const expandedGrades = ref(new Set<string>())
const selectedCourseId = ref<number | null>(null)

onMounted(() => {
  loadCurriculumTree()
})

async function loadCurriculumTree() {
  loading.value = true
  try {
    curriculumTree.value = await curriculumService.getCurriculumTree()
  } catch (error) {
    console.error('Failed to load curriculum tree:', error)
  } finally {
    loading.value = false
  }
}

function toggleSubject(subjectId: number) {
  if (expandedSubjects.value.has(subjectId)) {
    expandedSubjects.value.delete(subjectId)
  } else {
    expandedSubjects.value.add(subjectId)
  }
}

function toggleGrade(subjectId: number, gradeId: number) {
  const key = `${subjectId}-${gradeId}`
  if (expandedGrades.value.has(key)) {
    expandedGrades.value.delete(key)
  } else {
    expandedGrades.value.add(key)
  }
}

function selectCourse(courseId: number) {
  selectedCourseId.value = courseId
  emit('course-selected', courseId)
}

function selectAll() {
  selectedCourseId.value = null
  emit('course-selected', null)
}
</script>

<style scoped>
.curriculum-tree {
  max-height: 500px;
  overflow-y: auto;
}

.tree-content {
  font-size: 0.875rem;
}
</style>

