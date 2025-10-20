<template>
  <div class="curriculum-with-resources">
    <!-- 课程选择器 -->
    <div class="course-selector">
      <div class="selector-header">
        <h3 class="selector-title">课程资源</h3>
        <button
          v-if="selectedCourse"
          @click="clearSelection"
          class="clear-btn"
          title="清除选择"
        >
          <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 课程选择表单 -->
      <div v-if="!selectedCourse" class="selection-form">
        <div class="form-group">
          <label class="form-label">学科</label>
          <select
            v-model="selectedSubjectId"
            @change="loadCourses"
            class="form-select"
          >
            <option value="">请选择学科</option>
            <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
              {{ subject.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">年级</label>
          <select
            v-model="selectedGradeId"
            @change="loadCourses"
            class="form-select"
          >
            <option value="">请选择年级</option>
            <option v-for="grade in grades" :key="grade.id" :value="grade.id">
              {{ grade.name }}
            </option>
          </select>
        </div>

        <div v-if="availableCourse" class="course-card">
          <div class="course-info">
            <div class="course-name">{{ availableCourse.name }}</div>
            <div class="course-meta">
              {{ availableCourse.subject?.name }} · {{ availableCourse.grade?.name }}
            </div>
          </div>
          <button
            @click="selectCourse(availableCourse)"
            class="select-course-btn"
          >
            查看章节
          </button>
        </div>
      </div>

      <!-- 已选择的课程信息 -->
      <div v-else class="selected-course-info">
        <div class="course-badge">
          <div class="badge-icon">📚</div>
          <div class="badge-text">
            <div class="badge-title">{{ selectedCourse.name }}</div>
            <div class="badge-subtitle">
              {{ selectedCourse.subject?.name }} · {{ selectedCourse.grade?.name }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 章节和资源列表 -->
    <div v-if="selectedCourse" class="content-area">
      <!-- 加载状态 -->
      <div v-if="isLoadingChapters" class="loading-state">
        <div class="spinner"></div>
        <p>加载章节中...</p>
      </div>

      <!-- 章节列表 -->
      <div v-else-if="chapters.length > 0" class="chapters-list">
        <div
          v-for="chapter in chapters"
          :key="chapter.id"
          class="chapter-node"
        >
          <!-- 主章节头部 -->
          <div class="chapter-header" @click="toggleChapter(chapter)">
            <svg
              :class="['expand-icon', { 'expanded': chapter.is_expanded }]"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            <span class="chapter-name">{{ chapter.name }}</span>
            <span v-if="chapter.resources_count > 0" class="resource-count">
              {{ chapter.resources_count }} 个资源
            </span>
            <span v-if="chapter.children && chapter.children.length > 0" class="children-count">
              {{ chapter.children.length }} 个子章节
            </span>
          </div>

          <!-- 章节内容（展开时显示） -->
          <Transition name="expand">
            <div v-if="chapter.is_expanded" class="chapter-content">
              <!-- 主章节资源（优先显示） -->
              <div v-if="chapterResources[chapter.id]?.length > 0" class="main-chapter-resources">
                <div class="section-title">
                  <svg class="section-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span>章节资源</span>
                </div>
                
                <!-- 加载资源 -->
                <div v-if="loadingChapterId === chapter.id" class="loading-resources">
                  <div class="spinner-small"></div>
                  <span>加载资源中...</span>
                </div>

                <!-- 资源列表 -->
                <div v-else class="resources-list">
                  <PDFResourceItem
                    v-for="resource in chapterResources[chapter.id]"
                    :key="resource.id"
                    :resource="resource"
                    @preview="handlePreviewPDF"
                    @create-lesson="handleCreateLesson"
                  />
                </div>
              </div>

              <!-- 子章节列表 -->
              <div v-if="chapter.children && chapter.children.length > 0" class="sub-chapters">
                <div class="section-title">
                  <svg class="section-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                  <span>子章节</span>
                </div>
                
                <div
                  v-for="subChapter in chapter.children"
                  :key="subChapter.id"
                  class="sub-chapter-node"
                >
                  <!-- 子章节头部 -->
                  <div class="sub-chapter-header" @click="toggleSubChapter(subChapter)">
                    <svg
                      :class="['expand-icon-small', { 'expanded': subChapter.is_expanded }]"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                    <span class="sub-chapter-name">{{ subChapter.name }}</span>
                    <span v-if="subChapter.resources_count > 0" class="resource-count-small">
                      {{ subChapter.resources_count }} 个资源
                    </span>
                  </div>

                  <!-- 子章节资源（展开时显示） -->
                  <Transition name="expand">
                    <div v-if="subChapter.is_expanded" class="sub-chapter-content">
                      <!-- 加载资源 -->
                      <div v-if="loadingChapterId === subChapter.id" class="loading-resources">
                        <div class="spinner-small"></div>
                        <span>加载资源中...</span>
                      </div>

                      <!-- 资源列表 -->
                      <div v-else-if="chapterResources[subChapter.id]?.length > 0" class="resources-list">
                        <PDFResourceItem
                          v-for="resource in chapterResources[subChapter.id]"
                          :key="resource.id"
                          :resource="resource"
                          @preview="handlePreviewPDF"
                          @create-lesson="handleCreateLesson"
                        />
                      </div>

                      <!-- 空状态 -->
                      <div v-else class="empty-resources">
                        <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                        </svg>
                        <p>暂无资源</p>
                      </div>
                    </div>
                  </Transition>
                </div>
              </div>

              <!-- 空状态（当既没有资源也没有子章节时） -->
              <div v-if="(!chapterResources[chapter.id] || chapterResources[chapter.id].length === 0) && (!chapter.children || chapter.children.length === 0)" class="empty-resources">
                <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                <p>暂无内容</p>
              </div>
            </div>
          </Transition>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-chapters">
        <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
        <p>该课程暂无章节</p>
      </div>
    </div>

    <!-- PDF 预览模态框 -->
    <PDFViewerModal
      v-model="showPDFViewer"
      :resource-id="selectedPDFId"
      @create-lesson="handleCreateLesson"
    />

    <!-- 创建教案模态框 -->
    <CreateLessonFromResourceModal
      v-model="showCreateModal"
      :resource-id="selectedResourceId"
      @success="handleLessonCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { Subject, Grade, Course } from '../../types/curriculum'
import type { Resource, ChapterWithChildren } from '../../types/resource'
import curriculumService from '../../services/curriculum'
import { chapterService, resourceService } from '../../services/resource'
import PDFResourceItem from '../Resource/PDFResourceItem.vue'
import PDFViewerModal from '../Resource/PDFViewerModal.vue'
import CreateLessonFromResourceModal from '../Resource/CreateLessonFromResourceModal.vue'

const emit = defineEmits<{
  'lesson-created': [lessonId: number]
}>()

// 基础数据
const subjects = ref<Subject[]>([])
const grades = ref<Grade[]>([])
const selectedSubjectId = ref<number | string>('')
const selectedGradeId = ref<number | string>('')
const availableCourse = ref<Course | null>(null)
const selectedCourse = ref<Course | null>(null)

// 章节和资源
const chapters = ref<(ChapterWithChildren & { is_expanded?: boolean })[]>([])
const chapterResources = ref<Record<number, Resource[]>>({})
const isLoadingChapters = ref(false)
const loadingChapterId = ref<number | null>(null)

// 模态框状态
const showPDFViewer = ref(false)
const selectedPDFId = ref<number | null>(null)
const showCreateModal = ref(false)
const selectedResourceId = ref<number | null>(null)

// 加载课程体系数据（与管理员端保持一致）
onMounted(async () => {
  try {
    // 使用与管理员端相同的数据源
    const curriculumData = await curriculumService.getCurriculumTree(false)
    
    // 从课程体系树中提取学科和年级数据
    subjects.value = curriculumData.subjects || []
    
    // 提取所有年级
    const allGrades: Grade[] = []
    curriculumData.subjects?.forEach(subject => {
      if (subject.grades) {
        subject.grades.forEach(grade => {
          // 避免重复添加年级
          if (!allGrades.find(g => g.id === grade.id)) {
            allGrades.push(grade)
          }
        })
      }
    })
    grades.value = allGrades
  } catch (error) {
    console.error('Failed to load curriculum data:', error)
  }
})

// 加载课程（从课程体系树中查找）
async function loadCourses() {
  if (!selectedSubjectId.value || !selectedGradeId.value) {
    availableCourse.value = null
    return
  }

  try {
    // 从已加载的课程体系数据中查找对应的课程
    const subject = subjects.value.find(s => s.id === Number(selectedSubjectId.value))
    if (subject && subject.grades) {
      const grade = subject.grades.find(g => g.id === Number(selectedGradeId.value))
      if (grade && grade.courses && grade.courses.length > 0) {
        availableCourse.value = grade.courses[0] // 取第一个课程
      } else {
        availableCourse.value = null
      }
    } else {
      availableCourse.value = null
    }
  } catch (error) {
    console.error('Failed to load course:', error)
    availableCourse.value = null
  }
}

// 选择课程
async function selectCourse(course: Course) {
  selectedCourse.value = course
  await loadChapters(course.id)
}

// 清除选择
function clearSelection() {
  selectedCourse.value = null
  chapters.value = []
  chapterResources.value = {}
}

// 加载章节
async function loadChapters(courseId: number) {
  isLoadingChapters.value = true
  
  try {
    const data = await chapterService.getCourseChapters(courseId, true)
    // 确保 data 是数组
    if (Array.isArray(data)) {
      chapters.value = data.map(ch => ({ ...ch, is_expanded: false }))
    } else {
      console.warn('Chapters data is not an array:', data)
      chapters.value = []
    }
  } catch (error) {
    console.error('Failed to load chapters:', error)
    chapters.value = []
  } finally {
    isLoadingChapters.value = false
  }
}

// 切换章节展开/折叠
async function toggleChapter(chapter: ChapterWithChildren & { is_expanded?: boolean }) {
  chapter.is_expanded = !chapter.is_expanded
  
  // 如果展开且还没有加载资源，则加载
  if (chapter.is_expanded && !chapterResources.value[chapter.id]) {
    await loadChapterResources(chapter.id)
  }
}

// 切换子章节展开/折叠
async function toggleSubChapter(subChapter: ChapterWithChildren & { is_expanded?: boolean }) {
  subChapter.is_expanded = !subChapter.is_expanded
  
  // 如果展开且还没有加载资源，则加载
  if (subChapter.is_expanded && !chapterResources.value[subChapter.id]) {
    await loadChapterResources(subChapter.id)
  }
}

// 加载章节资源
async function loadChapterResources(chapterId: number) {
  loadingChapterId.value = chapterId
  
  try {
    const response = await resourceService.getChapterResources(chapterId)
    chapterResources.value[chapterId] = response.items
  } catch (error) {
    console.error('Failed to load chapter resources:', error)
    chapterResources.value[chapterId] = []
  } finally {
    loadingChapterId.value = null
  }
}

// 预览 PDF
function handlePreviewPDF(resourceId: number) {
  selectedPDFId.value = resourceId
  showPDFViewer.value = true
}

// 创建教案
function handleCreateLesson(resourceId: number) {
  selectedResourceId.value = resourceId
  showCreateModal.value = true
}

// 教案创建成功
function handleLessonCreated(lessonId: number) {
  emit('lesson-created', lessonId)
}
</script>

<style scoped>
.curriculum-with-resources {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.course-selector {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.selector-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.selector-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.clear-btn {
  padding: 0.5rem;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 0.375rem;
  color: #dc2626;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: #fecaca;
}

.selection-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.form-select {
  padding: 0.625rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.course-card {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 0.5rem;
  margin-top: 0.5rem;
}

.course-info {
  flex: 1;
}

.course-name {
  font-weight: 600;
  color: #0c4a6e;
  margin-bottom: 0.25rem;
}

.course-meta {
  font-size: 0.813rem;
  color: #075985;
}

.select-course-btn {
  padding: 0.5rem 1rem;
  background: #0284c7;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.select-course-btn:hover {
  background: #0369a1;
}

.selected-course-info {
  display: flex;
  align-items: center;
}

.course-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.125rem;
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  border: 1px solid #93c5fd;
  border-radius: 0.5rem;
  flex: 1;
}

.badge-icon {
  font-size: 1.5rem;
}

.badge-title {
  font-weight: 600;
  color: #1e3a8a;
  margin-bottom: 0.125rem;
}

.badge-subtitle {
  font-size: 0.813rem;
  color: #3b82f6;
}

.content-area {
  padding: 1.5rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 0;
  color: #6b7280;
}

.spinner {
  width: 2.5rem;
  height: 2.5rem;
  border: 4px solid #f3f4f6;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 0.75rem;
}

.chapters-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.chapter-node {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
}

.chapter-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #f9fafb;
  cursor: pointer;
  transition: all 0.2s;
}

.chapter-header:hover {
  background: #f3f4f6;
}

.expand-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: #6b7280;
  transition: transform 0.2s;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.chapter-name {
  flex: 1;
  font-weight: 600;
  color: #111827;
  font-size: 0.938rem;
}

.resource-count {
  font-size: 0.813rem;
  color: #6b7280;
  background: #e5e7eb;
  padding: 0.25rem 0.625rem;
  border-radius: 1rem;
}

.children-count {
  font-size: 0.813rem;
  color: #3b82f6;
  background: #dbeafe;
  padding: 0.25rem 0.625rem;
  border-radius: 1rem;
}

.chapter-content {
  padding: 1rem;
  background: white;
}

/* 章节分组标题 */
.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  margin: 0.75rem 0;
  font-weight: 600;
  color: #475569;
  font-size: 0.875rem;
}

.section-icon {
  width: 1rem;
  height: 1rem;
  color: #6366f1;
}

/* 主章节资源区域 */
.main-chapter-resources {
  margin-bottom: 1.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
  background: white;
}

.main-chapter-resources .resources-list {
  padding: 0.75rem;
}

.sub-chapters {
  margin-bottom: 1rem;
}

.sub-chapter-node {
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  margin-bottom: 0.5rem;
  overflow: hidden;
}

.sub-chapter-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.2s;
  margin-left: 1rem;
}

.sub-chapter-header:hover {
  background: #f1f5f9;
}

.expand-icon-small {
  width: 1rem;
  height: 1rem;
  color: #6b7280;
  transition: transform 0.2s;
}

.expand-icon-small.expanded {
  transform: rotate(90deg);
}

.sub-chapter-name {
  flex: 1;
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.resource-count-small {
  font-size: 0.75rem;
  color: #6b7280;
  background: #e5e7eb;
  padding: 0.125rem 0.5rem;
  border-radius: 0.75rem;
}

.sub-chapter-content {
  padding: 0.75rem;
  background: white;
  margin-left: 1rem;
}

.main-chapter-resources {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.loading-resources {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.spinner-small {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid #f3f4f6;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.resources-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.empty-resources,
.empty-chapters {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: #9ca3af;
}

.empty-icon {
  width: 3rem;
  height: 3rem;
  margin-bottom: 0.5rem;
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
}

/* 动画 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

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
  max-height: 1000px;
  opacity: 1;
}
</style>

