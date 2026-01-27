<template>
  <div :class="['curriculum-with-resources', { 'is-compact': isCompact }]">
    <!-- 课程选择器 -->
    <div :class="['selection-bar', { 'selection-bar-compact': isCompact }]">
      <div class="selection-inputs">
        <div class="form-group">
          <label class="sr-only">学科</label>
          <div class="form-control-wrap">
            <svg class="form-control-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l6.16-3.422A12.083 12.083 0 0112 21.5c-2.764-1.94-6.16-3.421-6.16-3.421L12 14z" />
            </svg>
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
        </div>

        <div class="form-group">
          <label class="sr-only">年级</label>
          <div class="form-control-wrap">
            <svg class="form-control-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v12m6-6H6" />
            </svg>
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
        </div>
      </div>
      <button
        v-if="selectedCourse"
        @click="clearSelection"
        class="clear-btn"
        title="重新选择课程"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
        重选课程
      </button>
    </div>

    <Transition name="fade">
      <template v-if="availableCourse">
        <div v-if="!isCompact" class="course-card">
          <div class="course-info">
            <div class="course-chip">
              <span>{{ availableCourse.subject?.name }}</span>
              <span>·</span>
              <span>{{ availableCourse.grade?.name }}</span>
            </div>
            <div class="course-name">{{ availableCourse.name }}</div>
            <p class="course-description">
              即可预览官方章节资源与历史教案，支持一键引用。
            </p>
          </div>
          <button
            @click="selectCourse(availableCourse)"
            class="select-course-btn"
          >
            查看章节
          </button>
        </div>
      </template>
      <template v-else-if="selectedCourse && !isCompact">
        <div class="selected-course-info">
          <div class="course-summary">
            <div class="course-summary-icon">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v12m8-6H4" />
              </svg>
            </div>
            <div class="course-summary-text">
              <div class="course-summary-title">{{ selectedCourse.name }}</div>
              <div class="course-summary-subtitle">
                {{ selectedCourse.subject?.name }} · {{ selectedCourse.grade?.name }}
              </div>
            </div>
          </div>
          <p class="course-summary-tip">
            已为你展开课程章节，可直接预览资源或创建教案。
          </p>
        </div>
      </template>
    </Transition>

    <!-- 章节和资源列表 -->
    <div v-if="selectedCourse && !isCompact" class="content-area">
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
              <div v-if="chapterResources[chapter.id]?.length" class="main-chapter-resources">
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
                  <!-- 官方资源 -->
                  <PDFResourceItem
                    v-for="resource in chapterResources[chapter.id]"
                    :key="`resource-${resource.id}`"
                    :resource="resource"
                    @preview="handlePreviewPDF"
                    @create-lesson="handleCreateLesson"
                  />
                  
                  <!-- 加载教案状态 -->
                  <div v-if="loadingLessonsChapterId === chapter.id" class="loading-lessons">
                    <div class="spinner-small"></div>
                    <span>加载个人教案中...</span>
                  </div>
                  
                  <!-- 教师个人教案 -->
                  <LessonResourceItem
                    v-for="lesson in chapterLessons[chapter.id]"
                    :key="`lesson-${lesson.id}`"
                    :lesson="lesson"
                    @edit="handleEditLesson"
                    @view="handleViewLesson"
                    @publish="handlePublishLesson"
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
                      <div v-else-if="chapterResources[subChapter.id]?.length || chapterLessons[subChapter.id]?.length" class="resources-list">
                        <!-- 官方资源 -->
                        <PDFResourceItem
                          v-for="resource in chapterResources[subChapter.id]"
                          :key="`resource-${resource.id}`"
                          :resource="resource"
                          @preview="handlePreviewPDF"
                          @create-lesson="handleCreateLesson"
                        />
                        
                        <!-- 加载教案状态 -->
                        <div v-if="loadingLessonsChapterId === subChapter.id" class="loading-lessons">
                          <div class="spinner-small"></div>
                          <span>加载个人教案中...</span>
                        </div>
                        
                        <!-- 教师个人教案 -->
                        <LessonResourceItem
                          v-for="lesson in chapterLessons[subChapter.id]"
                          :key="`lesson-${lesson.id}`"
                          :lesson="lesson"
                          @edit="handleEditLesson"
                          @view="handleViewLesson"
                          @publish="handlePublishLesson"
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
              <div v-if="!chapterResources[chapter.id]?.length && !chapterLessons[chapter.id]?.length && !chapter.children?.length" class="empty-resources">
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

    <!-- 资源预览模态框 -->
    <ResourcePreviewModal
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
import { ref, onMounted, computed } from 'vue'
import type { Grade, Course, SubjectTreeNode } from '../../types/curriculum'
import type { Resource, ChapterWithChildren } from '../../types/resource'
import type { Lesson } from '../../types/lesson'
import curriculumService from '../../services/curriculum'
import { chapterService, resourceService } from '../../services/resource'
import { lessonService } from '../../services/lesson'
import PDFResourceItem from '../Resource/PDFResourceItem.vue'
import ResourcePreviewModal from '../Resource/ResourcePreviewModal.vue'
import CreateLessonFromResourceModal from '../Resource/CreateLessonFromResourceModal.vue'
import LessonResourceItem from '../Resource/LessonResourceItem.vue'

const emit = defineEmits<{
  'lesson-created': [lessonId: number]
}>()

const props = defineProps<{
  compact?: boolean
}>()

const isCompact = computed(() => props.compact === true)

// 基础数据
const subjects = ref<SubjectTreeNode[]>([])
const grades = ref<Grade[]>([])
const selectedSubjectId = ref<number | string>('')
const selectedGradeId = ref<number | string>('')
const availableCourse = ref<Course | null>(null)
const selectedCourse = ref<Course | null>(null)

// 扩展类型以包含 is_expanded 属性
interface ChapterWithExpanded extends Omit<ChapterWithChildren, 'children'> {
  is_expanded?: boolean
  children?: ChapterWithExpanded[]
}

// 章节和资源
const chapters = ref<ChapterWithExpanded[]>([])
const chapterResources = ref<Record<number, Resource[]>>({})
const chapterLessons = ref<Record<number, Lesson[]>>({})  // 章节教案
const isLoadingChapters = ref(false)
const loadingChapterId = ref<number | null>(null)
const loadingLessonsChapterId = ref<number | null>(null)  // 正在加载教案的章节ID

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
        subject.grades.forEach(gradeNode => {
          // 避免重复添加年级
          if (!allGrades.find((g: Grade) => g.id === gradeNode.id)) {
            // 将 GradeTreeNode 转换为 Grade
            allGrades.push({
              id: gradeNode.id,
              name: gradeNode.name,
              level: gradeNode.level,
              stage_id: gradeNode.stage_id,
              is_active: gradeNode.is_active,
              created_at: '',
              updated_at: ''
            })
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
        const courseNode = grade.courses[0]
        if (courseNode) {
          // 将 CourseTreeNode 转换为 Course
          availableCourse.value = {
            id: courseNode.id,
            subject_id: subject.id,
            grade_id: grade.id,
            name: courseNode.name,
            code: courseNode.code,
            description: courseNode.description,
            is_active: courseNode.is_active,
            display_order: 0,
            created_at: '',
            updated_at: '',
            subject: {
              id: subject.id,
              name: subject.name,
              code: subject.code,
              description: subject.description,
              is_active: subject.is_active,
              display_order: 0,
              created_at: '',
              updated_at: ''
            },
            grade: {
              id: grade.id,
              name: grade.name,
              level: grade.level,
              stage_id: grade.stage_id,
              is_active: grade.is_active,
              created_at: '',
              updated_at: ''
            }
          }
        } else {
          availableCourse.value = null
        }
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
  if (!isCompact.value) {
    await loadChapters(course.id)
  }
}

// 清除选择
function clearSelection() {
  selectedCourse.value = null
  chapters.value = []
  chapterResources.value = {}
}

// 加载章节
async function loadChapters(courseId: number) {
  if (isCompact.value) return
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
async function toggleChapter(chapter: ChapterWithExpanded) {
  chapter.is_expanded = !chapter.is_expanded
  
  // 如果展开且还没有加载资源，则加载
  if (chapter.is_expanded) {
    if (!chapterResources.value[chapter.id]) {
      await loadChapterResources(chapter.id)
    }
    if (!chapterLessons.value[chapter.id]) {
      await loadChapterLessons(chapter.id)
    }
  }
}

// 切换子章节展开/折叠
async function toggleSubChapter(subChapter: ChapterWithExpanded) {
  subChapter.is_expanded = !subChapter.is_expanded
  
  // 如果展开且还没有加载资源，则加载
  if (subChapter.is_expanded) {
    if (!chapterResources.value[subChapter.id]) {
      await loadChapterResources(subChapter.id)
    }
    if (!chapterLessons.value[subChapter.id]) {
      await loadChapterLessons(subChapter.id)
    }
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

// 加载章节教案
async function loadChapterLessons(chapterId: number) {
  loadingLessonsChapterId.value = chapterId
  
  try {
    const response = await lessonService.fetchChapterLessons(chapterId)
    chapterLessons.value[chapterId] = response.items
  } catch (error) {
    console.error('Failed to load chapter lessons:', error)
    chapterLessons.value[chapterId] = []
  } finally {
    loadingLessonsChapterId.value = null
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

// 教案操作处理
function handleEditLesson(lessonId: number) {
  // 跳转到教案编辑器
  window.open(`/teacher/lesson/${lessonId}`, '_blank')
}

function handleViewLesson(lessonId: number) {
  // 跳转到教案查看页面
  window.open(`/teacher/lesson/${lessonId}?mode=preview`, '_blank')
}

function handlePublishLesson(lessonId: number) {
  // 发布教案逻辑（可以在这里添加确认对话框）
  console.log('Publishing lesson:', lessonId)
  // TODO: 实现发布教案的API调用
}
</script>

<style scoped>
.curriculum-with-resources {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.curriculum-with-resources.is-compact {
  border: none;
  box-shadow: none;
  padding: 0;
  background: transparent;
}

.selection-bar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.15);
  background: linear-gradient(135deg, #ffffff 0%, #f4f7ff 100%);
}

.selection-bar-compact {
  padding: 0;
  border: none;
  background: transparent;
}

.selection-inputs {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
}

.curriculum-with-resources.is-compact .selection-inputs {
  gap: 0.5rem;
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
  width: 100%;
  padding: 0.7rem 2.5rem 0.7rem 2.75rem;
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: 999px;
  font-size: 0.9rem;
  background: linear-gradient(180deg, #ffffff 0%, #eef2ff 100%);
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: inset 0 1px 3px rgba(15, 23, 42, 0.05);
}

.form-select:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.form-control-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.form-control-icon {
  position: absolute;
  left: 0.9rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1rem;
  height: 1rem;
  color: rgba(79, 70, 229, 0.65);
}

.clear-btn {
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.55rem 0.9rem;
  border-radius: 999px;
  background: rgba(248, 113, 113, 0.1);
  color: #dc2626;
  border: 1px solid rgba(248, 113, 113, 0.25);
  font-size: 0.8rem;
  font-weight: 600;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: rgba(248, 113, 113, 0.2);
}

.course-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(56, 189, 248, 0.08));
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 1.1rem;
  margin-top: 0.5rem;
  box-shadow: 0 12px 25px -15px rgba(79, 70, 229, 0.4);
}

.course-info {
  flex: 1;
}

.course-name {
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 0.4rem;
  font-size: 1.15rem;
}

.course-meta {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #4338ca;
  background: rgba(99, 102, 241, 0.12);
  padding: 0.35rem 0.85rem;
  border-radius: 999px;
  box-shadow: inset 0 0 0 1px rgba(99, 102, 241, 0.2);
}

.select-course-btn {
  align-self: flex-start;
  padding: 0.65rem 1.35rem;
  background: linear-gradient(135deg, #4338ca, #2563eb);
  color: white;
  border: none;
  border-radius: 0.9rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 10px 25px -12px rgba(59, 130, 246, 0.7);
}

.select-course-btn:hover {
  background: linear-gradient(135deg, #3730a3, #1d4ed8);
  transform: translateY(-1px);
}

.selected-course-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.course-badge {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  padding: 1rem 1.3rem;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.15), rgba(59, 130, 246, 0.1));
  border: 1px solid rgba(139, 92, 246, 0.25);
  border-radius: 1rem;
  box-shadow: inset 0 0 0 1px rgba(94, 129, 244, 0.15);
}

.badge-icon {
  font-size: 1.85rem;
}

.badge-title {
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.2rem;
  font-size: 1.05rem;
}

.badge-subtitle {
  font-size: 0.85rem;
  color: #4c1d95;
}

.course-summary {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.course-summary-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  border-radius: 0.95rem;
  background: rgba(99, 102, 241, 0.15);
  color: #4338ca;
}

.course-summary-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.2rem;
}

.course-summary-subtitle {
  font-size: 0.85rem;
  color: #4b5563;
}

.course-summary-tip {
  font-size: 0.85rem;
  color: #6b7280;
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

.loading-resources,
.loading-lessons {
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

