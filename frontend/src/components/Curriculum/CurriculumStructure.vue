<template>
  <div class="curriculum-structure bg-white rounded-lg shadow-sm p-6">
    <div class="mb-6">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold text-gray-900 mb-2">课程教学</h2>
          <p class="text-sm text-gray-600">选择学段和学科，浏览相关课程内容</p>
        </div>
        <button
          v-if="selectedGrade"
          @click="clearGradeSelection"
          class="px-4 py-2 text-sm text-blue-600 hover:text-blue-700 border border-blue-300 rounded-md hover:bg-blue-50 transition-colors"
        >
          清除筛选
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <div class="inline-flex items-center">
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        加载中...
      </div>
    </div>

    <!-- Curriculum Structure -->
    <div v-else-if="curriculumTree" class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <!-- 小学课程 -->
      <div class="lg:col-span-2">
        <div class="stage-card bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 h-full">
          <div class="flex items-center mb-4">
            <div class="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center mr-4">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900">小学课程</h3>
              <p class="text-sm text-gray-600">Primary School</p>
            </div>
          </div>
          
          <div class="space-y-2">
            <div
              v-for="grade in primaryGrades"
              :key="grade.id"
              class="grade-item flex items-center justify-between p-3 bg-white rounded-lg hover:shadow-md transition-shadow cursor-pointer"
              @click="selectGrade(grade.id)"
            >
              <div class="flex items-center">
                <span class="text-sm font-medium text-gray-900">{{ grade.name }}</span>
                <span class="ml-2 text-xs text-gray-500">({{ grade.lesson_count }})</span>
              </div>
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- 初中课程 -->
      <div class="lg:col-span-1">
        <div class="stage-card bg-gradient-to-br from-blue-50 to-purple-100 rounded-xl p-6 h-full">
          <div class="flex items-center mb-4">
            <div class="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center mr-4">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900">初中课程</h3>
              <p class="text-sm text-gray-600">Junior High</p>
            </div>
          </div>
          
          <div class="space-y-2">
            <div
              v-for="grade in juniorGrades"
              :key="grade.id"
              class="grade-item flex items-center justify-between p-3 bg-white rounded-lg hover:shadow-md transition-shadow cursor-pointer"
              @click="selectGrade(grade.id)"
            >
              <div class="flex items-center">
                <span class="text-sm font-medium text-gray-900">{{ grade.name }}</span>
                <span class="ml-2 text-xs text-gray-500">({{ grade.lesson_count }})</span>
              </div>
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- 高中课程 -->
      <div class="lg:col-span-1">
        <div class="stage-card bg-gradient-to-br from-orange-50 to-pink-100 rounded-xl p-6 h-full">
          <div class="flex items-center mb-4">
            <div class="w-12 h-12 bg-orange-500 rounded-lg flex items-center justify-center mr-4">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900">高中课程</h3>
              <p class="text-sm text-gray-600">Senior High</p>
            </div>
          </div>
          
          <div class="space-y-2">
            <div
              v-for="grade in seniorGrades"
              :key="grade.id"
              class="grade-item flex items-center justify-between p-3 bg-white rounded-lg hover:shadow-md transition-shadow cursor-pointer"
              @click="selectGrade(grade.id)"
            >
              <div class="flex items-center">
                <span class="text-sm font-medium text-gray-900">{{ grade.name }}</span>
                <span class="ml-2 text-xs text-gray-500">({{ grade.lesson_count }})</span>
              </div>
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Additional Features -->
    <div v-if="curriculumTree" class="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- 基础性作业 -->
      <div class="feature-card bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
        <div class="flex items-center">
          <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
          </div>
          <div>
            <h4 class="text-sm font-medium text-gray-900">基础性作业</h4>
            <p class="text-xs text-gray-500">Basic Assignments</p>
          </div>
        </div>
      </div>

      <!-- 精品课遴选 -->
      <div class="feature-card bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
        <div class="flex items-center">
          <div class="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center mr-3">
            <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"></path>
            </svg>
          </div>
          <div>
            <h4 class="text-sm font-medium text-gray-900">2025年 精品课遴选</h4>
            <p class="text-xs text-gray-500">Quality Course Selection</p>
          </div>
        </div>
      </div>

      <!-- 教师备课授课 -->
      <div class="feature-card bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
        <div class="flex items-center">
          <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>
          </div>
          <div>
            <h4 class="text-sm font-medium text-gray-900">教师备课授课</h4>
            <p class="text-xs text-gray-500">Teacher Preparation</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-8 text-gray-500">
      <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
      </svg>
      <p class="text-sm">暂无课程数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import curriculumService from '@/services/curriculum'
import type { CurriculumTree, GradeTreeNode } from '@/types/curriculum'

const emit = defineEmits<{
  'grade-selected': [gradeId: number | null]
}>()

const loading = ref(false)
const curriculumTree = ref<CurriculumTree | null>(null)
const selectedGrade = ref<number | null>(null)

// 模拟数据 - 实际应该从API获取
const mockData: CurriculumTree = {
  stages: [
    {
      id: 1,
      name: '小学',
      code: 'primary',
      level: 1,
      is_active: true,
      lesson_count: 0,
      subjects: [
        {
          id: 1,
          name: '语文',
          code: 'chinese',
          is_active: true,
          lesson_count: 0,
          grades: [
            { id: 1, name: '一年级', level: 1, stage_id: 1, is_active: true, lesson_count: 5, courses: [] },
            { id: 2, name: '二年级', level: 2, stage_id: 1, is_active: true, lesson_count: 8, courses: [] },
            { id: 3, name: '三年级', level: 3, stage_id: 1, is_active: true, lesson_count: 12, courses: [] },
            { id: 4, name: '四年级', level: 4, stage_id: 1, is_active: true, lesson_count: 15, courses: [] },
            { id: 5, name: '五年级', level: 5, stage_id: 1, is_active: true, lesson_count: 18, courses: [] },
            { id: 6, name: '六年级', level: 6, stage_id: 1, is_active: true, lesson_count: 20, courses: [] }
          ]
        },
        {
          id: 2,
          name: '数学',
          code: 'math',
          is_active: true,
          lesson_count: 0,
          grades: [
            { id: 1, name: '一年级', level: 1, stage_id: 1, is_active: true, lesson_count: 6, courses: [] },
            { id: 2, name: '二年级', level: 2, stage_id: 1, is_active: true, lesson_count: 9, courses: [] },
            { id: 3, name: '三年级', level: 3, stage_id: 1, is_active: true, lesson_count: 13, courses: [] },
            { id: 4, name: '四年级', level: 4, stage_id: 1, is_active: true, lesson_count: 16, courses: [] },
            { id: 5, name: '五年级', level: 5, stage_id: 1, is_active: true, lesson_count: 19, courses: [] },
            { id: 6, name: '六年级', level: 6, stage_id: 1, is_active: true, lesson_count: 22, courses: [] }
          ]
        }
      ]
    },
    {
      id: 2,
      name: '初中',
      code: 'junior',
      level: 2,
      is_active: true,
      lesson_count: 0,
      subjects: [
        {
          id: 3,
          name: '语文',
          code: 'chinese',
          is_active: true,
          lesson_count: 0,
          grades: [
            { id: 7, name: '七年级', level: 7, stage_id: 2, is_active: true, lesson_count: 25, courses: [] },
            { id: 8, name: '八年级', level: 8, stage_id: 2, is_active: true, lesson_count: 28, courses: [] },
            { id: 9, name: '九年级', level: 9, stage_id: 2, is_active: true, lesson_count: 30, courses: [] }
          ]
        },
        {
          id: 4,
          name: '数学',
          code: 'math',
          is_active: true,
          lesson_count: 0,
          grades: [
            { id: 7, name: '七年级', level: 7, stage_id: 2, is_active: true, lesson_count: 26, courses: [] },
            { id: 8, name: '八年级', level: 8, stage_id: 2, is_active: true, lesson_count: 29, courses: [] },
            { id: 9, name: '九年级', level: 9, stage_id: 2, is_active: true, lesson_count: 32, courses: [] }
          ]
        }
      ]
    },
    {
      id: 3,
      name: '高中',
      code: 'senior',
      level: 3,
      is_active: true,
      lesson_count: 0,
      subjects: [
        {
          id: 5,
          name: '语文',
          code: 'chinese',
          is_active: true,
          lesson_count: 0,
          grades: [
            { id: 10, name: '高一', level: 10, stage_id: 3, is_active: true, lesson_count: 35, courses: [] },
            { id: 11, name: '高二', level: 11, stage_id: 3, is_active: true, lesson_count: 38, courses: [] },
            { id: 12, name: '高三', level: 12, stage_id: 3, is_active: true, lesson_count: 40, courses: [] }
          ]
        },
        {
          id: 6,
          name: '数学',
          code: 'math',
          is_active: true,
          lesson_count: 0,
          grades: [
            { id: 10, name: '高一', level: 10, stage_id: 3, is_active: true, lesson_count: 36, courses: [] },
            { id: 11, name: '高二', level: 11, stage_id: 3, is_active: true, lesson_count: 39, courses: [] },
            { id: 12, name: '高三', level: 12, stage_id: 3, is_active: true, lesson_count: 42, courses: [] }
          ]
        }
      ]
    }
  ],
  total_stages: 3,
  total_subjects: 6,
  total_grades: 12,
  total_courses: 0,
  total_lessons: 0
}

// 计算各学段的年级
const primaryGrades = computed(() => {
  const primaryStage = curriculumTree.value?.stages.find(stage => stage.level === 1)
  if (!primaryStage) return []
  
  // 合并所有学科的年级数据
  const gradeMap = new Map<number, GradeTreeNode>()
  primaryStage.subjects.forEach(subject => {
    subject.grades.forEach(grade => {
      if (gradeMap.has(grade.id)) {
        gradeMap.get(grade.id)!.lesson_count += grade.lesson_count
      } else {
        gradeMap.set(grade.id, { ...grade })
      }
    })
  })
  
  return Array.from(gradeMap.values()).sort((a, b) => a.level - b.level)
})

const juniorGrades = computed(() => {
  const juniorStage = curriculumTree.value?.stages.find(stage => stage.level === 2)
  if (!juniorStage) return []
  
  const gradeMap = new Map<number, GradeTreeNode>()
  juniorStage.subjects.forEach(subject => {
    subject.grades.forEach(grade => {
      if (gradeMap.has(grade.id)) {
        gradeMap.get(grade.id)!.lesson_count += grade.lesson_count
      } else {
        gradeMap.set(grade.id, { ...grade })
      }
    })
  })
  
  return Array.from(gradeMap.values()).sort((a, b) => a.level - b.level)
})

const seniorGrades = computed(() => {
  const seniorStage = curriculumTree.value?.stages.find(stage => stage.level === 3)
  if (!seniorStage) return []
  
  const gradeMap = new Map<number, GradeTreeNode>()
  seniorStage.subjects.forEach(subject => {
    subject.grades.forEach(grade => {
      if (gradeMap.has(grade.id)) {
        gradeMap.get(grade.id)!.lesson_count += grade.lesson_count
      } else {
        gradeMap.set(grade.id, { ...grade })
      }
    })
  })
  
  return Array.from(gradeMap.values()).sort((a, b) => a.level - b.level)
})

onMounted(() => {
  loadCurriculumData()
})

async function loadCurriculumData() {
  loading.value = true
  try {
    // 暂时使用模拟数据，实际应该调用API
    // curriculumTree.value = await curriculumService.getCurriculumTree()
    curriculumTree.value = mockData
  } catch (error) {
    console.error('Failed to load curriculum data:', error)
  } finally {
    loading.value = false
  }
}

function selectGrade(gradeId: number) {
  selectedGrade.value = gradeId
  emit('grade-selected', gradeId)
}

function clearGradeSelection() {
  selectedGrade.value = null
  emit('grade-selected', null)
}
</script>

<style scoped>
.stage-card {
  min-height: 300px;
}

.grade-item:hover {
  transform: translateY(-1px);
}

.feature-card:hover {
  transform: translateY(-1px);
}
</style>
