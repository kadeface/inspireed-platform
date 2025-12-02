<template>
  <Transition name="modal">
    <div v-if="isOpen" class="modal-overlay" @click.self="handleClose">
      <div class="modal-container">
        <div class="modal-header">
          <h2 class="modal-title">合并课程</h2>
          <button @click="handleClose" class="close-btn">✕</button>
        </div>

        <div class="modal-body">
          <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <span>加载中...</span>
          </div>

          <div v-else-if="coursesWithSameCode.length === 0" class="empty-state">
            <p class="empty-text">没有找到具有相同课程代码的课程</p>
            <p class="empty-hint">请确保要合并的课程具有相同的课程代码</p>
          </div>

          <div v-else>
            <div class="info-section mb-4">
              <p class="info-text">
                <strong>课程代码：</strong>{{ courseCode }}
              </p>
              <p class="info-text text-sm text-gray-600">
                找到 {{ coursesWithSameCode.length }} 个具有相同代码的课程
              </p>
            </div>

            <!-- 只有一个课程时的提示 -->
            <div v-if="coursesWithSameCode.length === 1" class="warning-box mb-4">
              <div class="flex items-start gap-2">
                <span class="text-blue-600 text-lg">ℹ️</span>
                <div class="flex-1">
                  <p class="warning-title">无法合并</p>
                  <p class="warning-text">
                    当前只有 1 个具有此课程代码的课程，无法进行合并操作。
                    合并功能需要至少 2 个具有相同课程代码的课程。
                  </p>
                </div>
              </div>
            </div>

            <!-- 课程选择 -->
            <div v-else class="section mb-4">
              <label class="section-label">选择目标课程（保留的课程）</label>
              <div class="courses-list">
                <div
                  v-for="course in coursesWithSameCode"
                  :key="course.id"
                  class="course-item"
                  :class="{ 'selected': selectedTargetCourseId === course.id }"
                  @click.stop="selectTargetCourse(course.id)"
                >
                  <div class="course-radio" @click.stop="selectTargetCourse(course.id)">
                    <input
                      type="radio"
                      :checked="selectedTargetCourseId === course.id"
                      @change.stop="selectTargetCourse(course.id)"
                      @click.stop="selectTargetCourse(course.id)"
                    />
                  </div>
                  <div class="course-info" @click.stop="selectTargetCourse(course.id)">
                    <div class="course-name">{{ course.name }}</div>
                    <div class="course-meta">
                      <span>{{ course.subject?.name }} · {{ course.grade?.name }}</span>
                      <span v-if="course.lesson_count !== undefined">
                        · {{ course.lesson_count }} 个教案
                      </span>
                      <span v-if="courseStats[course.id]">
                        · {{ courseStats[course.id].chapter_count }} 个章节
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 合并选项 -->
            <div v-if="coursesWithSameCode.length > 1" class="section mb-4">
              <label class="section-label">合并选项</label>
              <div class="options-list">
                <label class="option-item">
                  <input
                    type="checkbox"
                    v-model="mergeOptions.merge_lessons"
                  />
                  <span>合并教案</span>
                </label>
                <label class="option-item">
                  <input
                    type="checkbox"
                    v-model="mergeOptions.merge_chapters"
                  />
                  <span>合并章节</span>
                </label>
              </div>
            </div>

            <!-- 冲突处理 -->
            <div v-if="coursesWithSameCode.length > 1 && (mergeOptions.merge_lessons || mergeOptions.merge_chapters)" class="section mb-4">
              <label class="section-label">冲突处理方式</label>
              <div class="radio-group">
                <label class="radio-item">
                  <input
                    type="radio"
                    v-model="mergeOptions.handle_conflicts"
                    value="rename"
                  />
                  <span>重命名（推荐）</span>
                  <span class="radio-hint">重命名冲突的项目，保留所有数据</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    v-model="mergeOptions.handle_conflicts"
                    value="skip"
                  />
                  <span>跳过</span>
                  <span class="radio-hint">跳过冲突的项目，不合并</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    v-model="mergeOptions.handle_conflicts"
                    value="overwrite"
                  />
                  <span>覆盖</span>
                  <span class="radio-hint">删除目标课程中的冲突项目，用源课程的数据替换</span>
                </label>
              </div>
            </div>

            <!-- 警告信息 -->
            <div v-if="selectedTargetCourseId && mergeWarning" class="warning-box">
              <div class="flex items-start gap-2">
                <span class="text-orange-600 text-lg">⚠️</span>
                <div class="flex-1">
                  <p class="warning-title">合并警告</p>
                  <p class="warning-text">{{ mergeWarning }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="handleClose" class="btn btn-secondary">取消</button>
          <button
            @click="handleConfirm"
            class="btn btn-primary"
            :disabled="!canMerge || merging || coursesWithSameCode.length <= 1"
          >
            {{ merging ? '合并中...' : '确认合并' }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { curriculumService } from '@/services/curriculum'
import { useToast } from '@/composables/useToast'
import type { Course, CourseMergeRequest } from '@/types/curriculum'

interface Props {
  isOpen: boolean
  courseCode: string
  currentCourseId?: number  // 当前选中的课程ID（用于默认选择）
  service?: any  // 可选的服务对象，如果不提供则使用默认的 curriculumService
}

const props = withDefaults(defineProps<Props>(), {
  service: () => null
})

const emit = defineEmits<{
  close: []
  success: []
}>()

const toast = useToast()
// 使用传入的服务或默认的 curriculumService
const service = computed(() => props.service || curriculumService)
const loading = ref(false)
const merging = ref(false)
const coursesWithSameCode = ref<Course[]>([])
const selectedTargetCourseId = ref<number | null>(null)
const courseStats = ref<Record<number, { lesson_count: number; chapter_count: number }>>({})

const mergeOptions = ref({
  merge_lessons: true,
  merge_chapters: true,
  handle_conflicts: 'rename' as 'rename' | 'skip' | 'overwrite'
})

// 计算是否可以合并
const canMerge = computed(() => {
  return selectedTargetCourseId.value !== null &&
         (mergeOptions.value.merge_lessons || mergeOptions.value.merge_chapters) &&
         coursesWithSameCode.value.length > 1
})

// 计算合并警告
const mergeWarning = computed(() => {
  if (!selectedTargetCourseId.value) return null
  
  const targetCourse = coursesWithSameCode.value.find(c => c.id === selectedTargetCourseId.value)
  if (!targetCourse) return null
  
  const sourceCourses = coursesWithSameCode.value.filter(c => c.id !== selectedTargetCourseId.value)
  const totalLessons = sourceCourses.reduce((sum, c) => sum + (c.lesson_count || 0), 0)
  const totalChapters = sourceCourses.reduce((sum, c) => {
    const stats = courseStats.value[c.id]
    return sum + (stats?.chapter_count || 0)
  }, 0)
  
  if (mergeOptions.value.merge_lessons && mergeOptions.value.merge_chapters) {
    if (totalLessons > 0 || totalChapters > 0) {
      return `将合并 ${sourceCourses.length} 个源课程的 ${totalLessons} 个教案和 ${totalChapters} 个章节到目标课程 "${targetCourse.name}"。合并后源课程将被删除或禁用。`
    }
  } else if (mergeOptions.value.merge_lessons && totalLessons > 0) {
    return `将合并 ${sourceCourses.length} 个源课程的 ${totalLessons} 个教案到目标课程 "${targetCourse.name}"。`
  } else if (mergeOptions.value.merge_chapters && totalChapters > 0) {
    return `将合并 ${sourceCourses.length} 个源课程的 ${totalChapters} 个章节到目标课程 "${targetCourse.name}"。`
  }
  
  return null
})

// 加载具有相同代码的课程
async function loadCoursesWithSameCode() {
  if (!props.courseCode) return
  
  loading.value = true
  try {
    coursesWithSameCode.value = await service.value.getCoursesByCode(props.courseCode)
    
    // 加载每个课程的统计数据
    for (const course of coursesWithSameCode.value) {
      try {
        const courseWithChapters = await service.value.getCourseWithChapters(course.id)
        courseStats.value[course.id] = {
          lesson_count: courseWithChapters.total_lessons || 0,
          chapter_count: courseWithChapters.total_chapters || 0
        }
      } catch (error) {
        console.error(`Failed to load stats for course ${course.id}:`, error)
        courseStats.value[course.id] = { lesson_count: 0, chapter_count: 0 }
      }
    }
    
    // 默认选择当前课程或第一个课程
    if (props.currentCourseId) {
      const currentCourse = coursesWithSameCode.value.find(c => c.id === props.currentCourseId)
      if (currentCourse) {
        selectedTargetCourseId.value = currentCourse.id
      } else if (coursesWithSameCode.value.length > 0) {
        selectedTargetCourseId.value = coursesWithSameCode.value[0].id
      }
    } else if (coursesWithSameCode.value.length > 0) {
      selectedTargetCourseId.value = coursesWithSameCode.value[0].id
    }
  } catch (error: any) {
    console.error('Failed to load courses:', error)
    toast.error('加载课程列表失败')
  } finally {
    loading.value = false
  }
}

// 选择目标课程
function selectTargetCourse(courseId: number) {
  selectedTargetCourseId.value = courseId
}

// 确认合并
async function handleConfirm() {
  if (!canMerge.value || !selectedTargetCourseId.value) return
  
  const sourceCourses = coursesWithSameCode.value.filter(c => c.id !== selectedTargetCourseId.value)
  if (sourceCourses.length === 0) {
    toast.warning('没有可合并的源课程')
    return
  }
  
  if (!confirm(`确定要合并 ${sourceCourses.length} 个课程到 "${coursesWithSameCode.value.find(c => c.id === selectedTargetCourseId.value)?.name}" 吗？此操作不可撤销。`)) {
    return
  }
  
  merging.value = true
  try {
    // 逐个合并源课程到目标课程
    let totalMergedLessons = 0
    let totalMergedChapters = 0
    let totalSkippedLessons = 0
    let totalSkippedChapters = 0
    const allErrors: string[] = []
    
    for (const sourceCourse of sourceCourses) {
      const mergeRequest: CourseMergeRequest = {
        source_course_id: sourceCourse.id,
        target_course_id: selectedTargetCourseId.value,
        merge_lessons: mergeOptions.value.merge_lessons,
        merge_chapters: mergeOptions.value.merge_chapters,
        handle_conflicts: mergeOptions.value.handle_conflicts
      }
      
      try {
        const result = await service.value.mergeCourses(mergeRequest)
        totalMergedLessons += result.merged_lessons_count
        totalMergedChapters += result.merged_chapters_count
        totalSkippedLessons += result.skipped_lessons_count
        totalSkippedChapters += result.skipped_chapters_count
        if (result.errors.length > 0) {
          allErrors.push(...result.errors)
        }
      } catch (error: any) {
        allErrors.push(`合并课程 "${sourceCourse.name}" 失败: ${error.response?.data?.detail || error.message}`)
      }
    }
    
    // 显示合并结果
    if (allErrors.length > 0) {
      toast.warning(`合并完成，但有 ${allErrors.length} 个错误。请查看控制台。`)
      console.error('合并错误:', allErrors)
    } else {
      toast.success(
        `合并成功！已合并 ${totalMergedLessons} 个教案和 ${totalMergedChapters} 个章节。`
      )
    }
    
    emit('success')
    handleClose()
  } catch (error: any) {
    console.error('Failed to merge courses:', error)
    toast.error(error.response?.data?.detail || '合并失败')
  } finally {
    merging.value = false
  }
}

// 关闭模态框
function handleClose() {
  selectedTargetCourseId.value = null
  mergeOptions.value = {
    merge_lessons: true,
    merge_chapters: true,
    handle_conflicts: 'rename'
  }
  emit('close')
}

// 监听模态框打开和课程代码变化
watch(() => props.isOpen, (newVal) => {
  if (newVal && props.courseCode) {
    loadCoursesWithSameCode()
  }
})

watch(() => props.courseCode, () => {
  if (props.isOpen && props.courseCode) {
    loadCoursesWithSameCode()
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #111827;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.spinner {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  padding: 3rem;
  text-align: center;
}

.empty-text {
  font-size: 0.938rem;
  color: #6b7280;
  font-weight: 500;
  margin: 0 0 0.5rem;
}

.empty-hint {
  font-size: 0.813rem;
  color: #9ca3af;
  margin: 0;
}

.info-section {
  padding: 1rem;
  background: #f3f4f6;
  border-radius: 0.5rem;
}

.info-text {
  margin: 0.25rem 0;
  color: #374151;
}

.section {
  margin-bottom: 1.5rem;
}

.section-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.75rem;
}

.courses-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
}

.course-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
  -webkit-user-select: none;
}

.course-item:hover {
  border-color: #d1d5db;
  background: #f9fafb;
}

.course-item.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.course-radio {
  flex-shrink: 0;
  margin-top: 0.25rem;
  pointer-events: auto;
}

.course-radio input[type="radio"] {
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
  pointer-events: auto;
  margin: 0;
}

.course-info {
  flex: 1;
  min-width: 0;
}

.course-name {
  font-weight: 500;
  font-size: 0.938rem;
  color: #111827;
  margin-bottom: 0.25rem;
}

.course-meta {
  font-size: 0.813rem;
  color: #6b7280;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.option-item input[type="checkbox"] {
  width: 1.125rem;
  height: 1.125rem;
  cursor: pointer;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.radio-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.radio-item:hover {
  border-color: #d1d5db;
  background: #f9fafb;
}

.radio-item input[type="radio"] {
  width: 1rem;
  height: 1rem;
  cursor: pointer;
}

.radio-hint {
  font-size: 0.75rem;
  color: #6b7280;
  margin-left: 1.5rem;
}

.warning-box {
  padding: 1rem;
  background: #fef3c7;
  border: 1px solid #fcd34d;
  border-radius: 0.5rem;
}

.warning-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #92400e;
  margin: 0 0 0.25rem;
}

.warning-text {
  font-size: 0.813rem;
  color: #78350f;
  margin: 0;
  line-height: 1.5;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #f9fafb;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>

