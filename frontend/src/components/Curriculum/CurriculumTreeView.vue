<template>
  <div class="curriculum-tree-view">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p class="text-gray-500">加载课程体系...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <p class="text-red-600">{{ error }}</p>
      <button @click="loadData" class="retry-btn">重试</button>
    </div>

    <!-- 课程体系树 -->
    <div v-else class="tree-container">
      <!-- 顶部统计 -->
      <div class="stats-summary">
        <div class="stat-item">
          <span class="stat-label">学科</span>
          <span class="stat-value">{{ curriculumTree?.total_subjects || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">课程</span>
          <span class="stat-value">{{ curriculumTree?.total_courses || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">教案</span>
          <span class="stat-value">{{ curriculumTree?.total_lessons || 0 }}</span>
        </div>
      </div>

      <!-- 学科列表 -->
      <div v-if="curriculumTree?.subjects.length" class="subjects-list">
        <div 
          v-for="subject in curriculumTree.subjects" 
          :key="subject.id"
          class="subject-item"
        >
          <!-- 学科标题 -->
          <div 
            class="subject-header"
            :class="{ 'expanded': expandedSubjects.has(subject.id) }"
            @click="toggleSubject(subject.id)"
          >
            <div class="subject-info">
              <span class="expand-icon">
                {{ expandedSubjects.has(subject.id) ? '▼' : '▶' }}
              </span>
              <h3 class="subject-name">{{ subject.name }}</h3>
              <span class="lesson-badge" v-if="subject.lesson_count > 0">
                {{ subject.lesson_count }} 个教案
              </span>
            </div>
          </div>

          <!-- 年级列表 -->
          <Transition name="expand">
            <div v-if="expandedSubjects.has(subject.id)" class="grades-list">
              <div
                v-for="grade in subject.grades"
                :key="grade.id"
                class="grade-item"
              >
                <!-- 年级标题 -->
                <div 
                  class="grade-header"
                  :class="{ 'expanded': expandedGrades.has(grade.id) }"
                  @click="toggleGrade(grade.id)"
                >
                  <div class="grade-info">
                    <span class="expand-icon">
                      {{ expandedGrades.has(grade.id) ? '▼' : '▶' }}
                    </span>
                    <h4 class="grade-name">{{ grade.name }}</h4>
                    <span class="lesson-badge" v-if="grade.lesson_count > 0">
                      {{ grade.lesson_count }} 个教案
                    </span>
                  </div>
                </div>

                <!-- 课程列表 -->
                <Transition name="expand">
                  <div v-if="expandedGrades.has(grade.id)" class="courses-list">
                    <div
                      v-for="course in grade.courses"
                      :key="course.id"
                      class="course-item"
                      :class="{ 'selected': selectedCourse?.id === course.id }"
                    >
                      <!-- 课程标题 -->
                      <div 
                        class="course-header"
                        @click="selectCourse(course.id)"
                      >
                        <div class="course-info">
                          <span class="course-icon">📚</span>
                          <h5 class="course-name">{{ course.name }}</h5>
                          <span class="lesson-badge" v-if="course.lesson_count > 0">
                            {{ course.lesson_count }} 个教案
                          </span>
                        </div>
                        <button
                          v-if="selectedCourse?.id === course.id"
                          class="view-details-btn"
                          @click.stop="loadCourseDetails(course.id)"
                        >
                          查看章节
                        </button>
                      </div>
                    </div>
                  </div>
                </Transition>
              </div>
            </div>
          </Transition>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <div class="empty-icon">📚</div>
        <p class="text-gray-500">暂无课程体系数据</p>
      </div>
    </div>

    <!-- 课程详情侧边栏 -->
    <Transition name="slide">
      <div v-if="showCourseDetails && courseDetails" class="course-details-sidebar">
        <div class="sidebar-header">
          <h3 class="sidebar-title">{{ courseDetails.name }}</h3>
          <button @click="closeCourseDetails" class="close-btn">✕</button>
        </div>

        <div class="sidebar-content">
          <!-- 课程信息 -->
          <div class="course-meta">
            <div class="meta-item">
              <span class="meta-label">学科</span>
              <span class="meta-value">{{ courseDetails.subject?.name }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">年级</span>
              <span class="meta-value">{{ courseDetails.grade?.name }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">章节数</span>
              <span class="meta-value">{{ courseDetails.total_chapters }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">教案数</span>
              <span class="meta-value">{{ courseDetails.total_lessons }}</span>
            </div>
          </div>

          <!-- 章节树 -->
          <div class="chapters-section">
            <h4 class="section-title">章节目录</h4>
            <div v-if="courseDetails.chapters.length" class="chapters-tree">
              <ChapterTreeNode
                v-for="chapter in courseDetails.chapters"
                :key="chapter.id"
                :chapter="chapter"
                :level="0"
                @create-lesson="handleCreateLesson"
                @view-lessons="handleViewLessons"
              />
            </div>
            <div v-else class="empty-chapters">
              <p class="text-gray-500 text-sm">暂无章节</p>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { curriculumService } from '@/services/curriculum'
import type { 
  CurriculumTree, 
  CourseTreeNode, 
  CourseWithChapters 
} from '@/types/curriculum'
import ChapterTreeNode from './ChapterTreeNode.vue'

const emit = defineEmits<{
  'create-lesson': [chapterId: number, courseId: number]
  'view-lessons': [chapterId: number]
}>()

// 数据状态
const loading = ref(true)
const error = ref<string | null>(null)
const curriculumTree = ref<CurriculumTree | null>(null)
const courseDetails = ref<CourseWithChapters | null>(null)
const showCourseDetails = ref(false)

// 展开状态
const expandedSubjects = ref<Set<number>>(new Set())
const expandedGrades = ref<Set<number>>(new Set())
const selectedCourse = ref<CourseTreeNode | null>(null)

// 加载课程体系树
async function loadData() {
  loading.value = true
  error.value = null
  
  try {
    curriculumTree.value = await curriculumService.getCurriculumTree(false)
    
    // 默认展开第一个学科和年级
    if (curriculumTree.value.subjects.length > 0) {
      const firstSubject = curriculumTree.value.subjects[0]
      expandedSubjects.value.add(firstSubject.id)
      
      if (firstSubject.grades.length > 0) {
        const firstGrade = firstSubject.grades[0]
        expandedGrades.value.add(firstGrade.id)
      }
    }
  } catch (err) {
    console.error('Failed to load curriculum tree:', err)
    error.value = '加载课程体系失败，请重试'
  } finally {
    loading.value = false
  }
}

// 切换学科展开状态
function toggleSubject(subjectId: number) {
  if (expandedSubjects.value.has(subjectId)) {
    expandedSubjects.value.delete(subjectId)
  } else {
    expandedSubjects.value.add(subjectId)
  }
}

// 切换年级展开状态
function toggleGrade(gradeId: number) {
  if (expandedGrades.value.has(gradeId)) {
    expandedGrades.value.delete(gradeId)
  } else {
    expandedGrades.value.add(gradeId)
  }
}

// 选择课程
function selectCourse(courseId: number) {
  // 在课程树中找到对应的课程
  for (const subject of curriculumTree.value?.subjects || []) {
    for (const grade of subject.grades) {
      const course = grade.courses.find(c => c.id === courseId)
      if (course) {
        selectedCourse.value = course
        return
      }
    }
  }
}

// 加载课程详情
async function loadCourseDetails(courseId: number) {
  try {
    courseDetails.value = await curriculumService.getCourseWithChapters(courseId)
    showCourseDetails.value = true
  } catch (err) {
    console.error('Failed to load course details:', err)
    error.value = '加载课程详情失败'
  }
}

// 关闭课程详情
function closeCourseDetails() {
  showCourseDetails.value = false
  courseDetails.value = null
}

// 处理创建教案
function handleCreateLesson(chapterId: number, courseId: number) {
  emit('create-lesson', chapterId, courseId)
}

// 处理查看章节教案
function handleViewLessons(chapterId: number) {
  emit('view-lessons', chapterId)
}

// 组件挂载时加载数据
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.curriculum-tree-view {
  display: flex;
  gap: 1.5rem;
  min-height: 500px;
}

/* 加载和错误状态 */
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  width: 100%;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.retry-btn {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #3b82f6;
  color: white;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.retry-btn:hover {
  background-color: #2563eb;
}

/* 树形容器 */
.tree-container {
  flex: 1;
  background: white;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

/* 统计摘要 */
.stats-summary {
  display: flex;
  gap: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, rgba(18, 184, 152, 1) 0%, rgba(120, 226, 205, 1) 100%);
  color: white;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  opacity: 0.9;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
}

/* 学科列表 */
.subjects-list {
  padding: 1rem;
}

.subject-item {
  margin-bottom: 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
}

.subject-header {
  padding: 1rem;
  background: #f9fafb;
  cursor: pointer;
  transition: background-color 0.2s;
}

.subject-header:hover {
  background: #f3f4f6;
}

.subject-header.expanded {
  background: #eff6ff;
}

.subject-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.expand-icon {
  font-size: 0.75rem;
  color: #6b7280;
  transition: transform 0.2s;
}

.subject-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  flex: 1;
}

/* 年级列表 */
.grades-list {
  padding: 0.5rem 0.5rem 0.5rem 2rem;
}

.grade-item {
  margin-bottom: 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  overflow: hidden;
}

.grade-header {
  padding: 0.75rem;
  background: white;
  cursor: pointer;
  transition: background-color 0.2s;
}

.grade-header:hover {
  background: #f9fafb;
}

.grade-header.expanded {
  background: #f0fdf4;
}

.grade-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.grade-name {
  font-size: 1rem;
  font-weight: 500;
  color: #374151;
  flex: 1;
}

/* 课程列表 */
.courses-list {
  padding: 0.5rem 0.5rem 0.5rem 1.5rem;
}

.course-item {
  margin-bottom: 0.375rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  overflow: hidden;
  transition: all 0.2s;
}

.course-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 1px 3px rgba(59, 130, 246, 0.1);
}

.course-item.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.course-header {
  padding: 0.75rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.course-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.course-icon {
  font-size: 1rem;
}

.course-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1f2937;
  flex: 1;
}

.lesson-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.view-details-btn {
  padding: 0.375rem 0.75rem;
  background: #3b82f6;
  color: white;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  transition: background-color 0.2s;
  white-space: nowrap;
}

.view-details-btn:hover {
  background: #2563eb;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

/* 课程详情侧边栏 */
.course-details-sidebar {
  width: 400px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 800px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, rgba(18, 184, 152, 1) 0%, rgba(120, 226, 205, 1) 100%);
  color: white;
}

.sidebar-title {
  font-size: 1.125rem;
  font-weight: 600;
}

.close-btn {
  padding: 0.25rem 0.5rem;
  font-size: 1.25rem;
  color: white;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.close-btn:hover {
  opacity: 1;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

/* 课程元数据 */
.course-meta {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.meta-label {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.meta-value {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

/* 章节部分 */
.chapters-section {
  margin-top: 1rem;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.chapters-tree {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.empty-chapters {
  padding: 2rem;
  text-align: center;
}

/* 过渡动画 */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 2000px;
  opacity: 1;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>

