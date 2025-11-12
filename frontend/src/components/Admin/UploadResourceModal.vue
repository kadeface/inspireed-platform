<template>
  <Transition name="modal">
    <div
      v-if="modelValue"
      class="modal-overlay"
      @click.self="close"
    >
      <div class="modal-dialog">
        <!-- 头部 -->
        <div class="modal-header">
          <h3 class="modal-title">上传官方教学设计</h3>
          <button @click="close" class="close-btn">
            <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 内容 -->
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <!-- 步骤 1: 选择章节 -->
            <div class="form-section">
              <h4 class="section-title">步骤 1：选择章节</h4>
              
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">学科 <span class="required">*</span></label>
                  <select
                    v-model="selectedSubjectId"
                    @change="handleSubjectChange"
                    class="form-select"
                    required
                  >
                    <option value="">请选择学科</option>
                    <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                      {{ subject.name }}
                    </option>
                  </select>
                </div>

                <div class="form-group">
                  <label class="form-label">年级 <span class="required">*</span></label>
                  <select
                    v-model="selectedGradeId"
                    @change="handleGradeChange"
                    :disabled="!selectedSubjectId"
                    class="form-select"
                    required
                  >
                    <option value="">请选择年级</option>
                    <option v-for="grade in grades" :key="grade.id" :value="grade.id">
                      {{ grade.name }}
                    </option>
                  </select>
                </div>
              </div>

              <div v-if="availableCourses.length > 0" class="form-group">
                <label class="form-label">课程 <span class="required">*</span></label>
                <select
                  v-model="selectedCourseId"
                  class="form-select"
                  required
                >
                  <option value="">请选择课程</option>
                  <option
                    v-for="courseOption in availableCourses"
                    :key="courseOption.id"
                    :value="courseOption.id"
                  >
                    {{ courseOption.name }}
                  </option>
                </select>
              </div>

              <div v-if="selectedCourse" class="course-display">
                <div class="course-badge">
                  <span class="badge-icon">📚</span>
                  <span class="badge-text">课程：{{ selectedCourse.name }}</span>
                </div>
              </div>

              <div v-if="selectedCourse" class="form-group">
                <label class="form-label">章节 <span class="required">*</span></label>
                <select
                  v-model="selectedChapterId"
                  class="form-select"
                  required
                >
                  <option value="">请选择章节</option>
                  <optgroup v-for="chapter in chapters" :key="chapter.id" :label="chapter.name">
                    <option :value="chapter.id">{{ chapter.name }}</option>
                    <option
                      v-for="child in chapter.children"
                      :key="child.id"
                      :value="child.id"
                    >
                      └─ {{ child.name }}
                    </option>
                  </optgroup>
                </select>
              </div>
            </div>

            <!-- 步骤 2: 资源信息 -->
            <div class="form-section">
              <h4 class="section-title">步骤 2：资源信息</h4>
              
              <div class="form-group">
                <label for="title" class="form-label">
                  资源标题 <span class="required">*</span>
                </label>
                <input
                  id="title"
                  v-model="formData.title"
                  type="text"
                  required
                  placeholder="例如：集合的概念 - 教学设计"
                  class="form-input"
                  :class="{ 'input-error': errors.title }"
                />
                <p v-if="errors.title" class="error-text">{{ errors.title }}</p>
              </div>

              <div class="form-group">
                <label for="description" class="form-label">资源描述</label>
                <textarea
                  id="description"
                  v-model="formData.description"
                  rows="3"
                  placeholder="简要描述教学设计内容..."
                  class="form-input"
                />
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">资源类型</label>
                  <select v-model="formData.resource_type" class="form-select">
                    <option value="pdf">PDF 文档</option>
                    <option value="video">视频</option>
                    <option value="document">文档</option>
                    <option value="link">链接</option>
                  </select>
                </div>

                <div class="form-group">
                  <label class="form-label">排序</label>
                  <input
                    v-model.number="formData.display_order"
                    type="number"
                    min="0"
                    class="form-input"
                  />
                </div>
              </div>

              <div class="checkbox-group">
                <label class="checkbox-label">
                  <input
                    v-model="formData.is_official"
                    type="checkbox"
                    class="checkbox-input"
                  />
                  <span>官方资源</span>
                </label>
                <label class="checkbox-label">
                  <input
                    v-model="formData.is_downloadable"
                    type="checkbox"
                    class="checkbox-input"
                  />
                  <span>允许下载</span>
                </label>
              </div>
            </div>

            <!-- 步骤 3: 上传文件 -->
            <div class="form-section">
              <h4 class="section-title">步骤 3：上传文件</h4>
              
              <div class="upload-area">
                <input
                  ref="fileInputRef"
                  type="file"
                  accept=".pdf,application/pdf"
                  @change="handleFileSelect"
                  class="hidden"
                />

                <div
                  v-if="!selectedFile"
                  @click="triggerFileSelect"
                  @dragover.prevent
                  @drop.prevent="handleFileDrop"
                  class="upload-zone"
                >
                  <svg class="upload-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p class="upload-text">拖拽文件到此处或点击上传</p>
                  <p class="upload-hint">支持 PDF 格式，最大 100MB</p>
                </div>

                <div v-else class="file-preview">
                  <div class="file-info">
                    <div class="file-icon">📋</div>
                    <div class="file-details">
                      <div class="file-name">{{ selectedFile.name }}</div>
                      <div class="file-size">{{ formatFileSize(selectedFile.size) }}</div>
                    </div>
                  </div>
                  <button
                    @click="clearFile"
                    type="button"
                    class="remove-btn"
                    title="移除文件"
                  >
                    <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </form>
        </div>

        <!-- 底部 -->
        <div class="modal-footer">
          <button
            type="button"
            @click="close"
            class="btn btn-secondary"
          >
            取消
          </button>
          <button
            type="button"
            @click="handleSubmit"
            :disabled="isUploading || !canSubmit"
            class="btn btn-primary"
          >
            <svg v-if="isUploading" class="btn-icon animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isUploading ? `上传中... ${uploadProgress}%` : '上传' }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import type { Subject, Grade, Course } from '../../types/curriculum'
import type { ChapterWithChildren, ResourceCreate } from '../../types/resource'
import { ResourceType, formatFileSize } from '../../types/resource'
import curriculumService from '../../services/curriculum'
import { chapterService, resourceService } from '../../services/resource'

interface Props {
  modelValue: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': [resourceId: number]
}>()

// 基础数据
const subjects = ref<Subject[]>([])
const grades = ref<Grade[]>([])
const selectedSubjectId = ref<number | string>('')
const selectedGradeId = ref<number | string>('')
const selectedCourse = ref<Course | null>(null)
const selectedCourseId = ref<number | ''>('')
const availableCourses = ref<Course[]>([])
const chapters = ref<ChapterWithChildren[]>([])
const selectedChapterId = ref<number | string>('')

// 表单数据
const formData = ref<ResourceCreate>({
  chapter_id: 0,
  title: '',
  description: '',
  resource_type: ResourceType.PDF,
  is_official: true,
  is_downloadable: true,
  display_order: 0
})

// 文件上传
const fileInputRef = ref<HTMLInputElement>()
const selectedFile = ref<File | null>(null)
const isUploading = ref(false)
const uploadProgress = ref(0)
const errors = ref<Record<string, string>>({})

// 计算属性
const canSubmit = computed(() => {
  return selectedChapterId.value && 
         formData.value.title.trim() && 
         selectedFile.value
})

// 加载基础数据
onMounted(async () => {
  try {
    const [subjectsData, gradesData] = await Promise.all([
      curriculumService.getSubjects(),
      curriculumService.getGrades()
    ])
    subjects.value = subjectsData
    grades.value = gradesData
  } catch (error) {
    console.error('Failed to load data:', error)
  }
})

// 学科变更
async function handleSubjectChange() {
  selectedGradeId.value = ''
  selectedCourse.value = null
  selectedCourseId.value = ''
  availableCourses.value = []
  chapters.value = []
  selectedChapterId.value = ''
}

// 年级变更
async function handleGradeChange() {
  if (!selectedSubjectId.value || !selectedGradeId.value) {
    selectedCourse.value = null
    selectedCourseId.value = ''
    availableCourses.value = []
    chapters.value = []
    selectedChapterId.value = ''
    return
  }
  
  try {
    availableCourses.value = await curriculumService.getCourseBySubjectAndGrade(
      Number(selectedSubjectId.value),
      Number(selectedGradeId.value)
    )
    selectedCourse.value = availableCourses.value[0] ?? null
    selectedCourseId.value = selectedCourse.value?.id ?? ''
    
    if (selectedCourse.value) {
      const chaptersData = await chapterService.getCourseChapters(selectedCourse.value.id, true)
      chapters.value = chaptersData
    } else {
      chapters.value = []
    }
  } catch (error) {
    console.error('Failed to load course or chapters:', error)
    selectedCourse.value = null
    selectedCourseId.value = ''
    availableCourses.value = []
    chapters.value = []
  }
}

watch(selectedCourseId, async value => {
  if (!value) {
    selectedCourse.value = null
    chapters.value = []
    selectedChapterId.value = ''
    return
  }

  const courseId = typeof value === 'string' ? Number(value) : value
  const course = availableCourses.value.find(courseItem => courseItem.id === courseId) ?? null
  selectedCourse.value = course

  if (course) {
    const chaptersData = await chapterService.getCourseChapters(course.id, true)
    chapters.value = chaptersData
  } else {
    chapters.value = []
  }
})

// 触发文件选择
function triggerFileSelect() {
  fileInputRef.value?.click()
}

// 文件选择
function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    validateAndSetFile(target.files[0])
  }
}

// 文件拖放
function handleFileDrop(event: DragEvent) {
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    validateAndSetFile(event.dataTransfer.files[0])
  }
}

// 验证并设置文件
function validateAndSetFile(file: File) {
  // 验证文件类型
  if (formData.value.resource_type === ResourceType.PDF) {
    if (!file.type.includes('pdf')) {
      alert('请选择 PDF 文件')
      return
    }
  }
  
  // 验证文件大小（100MB）
  const maxSize = 100 * 1024 * 1024
  if (file.size > maxSize) {
    alert('文件大小不能超过 100MB')
    return
  }
  
  selectedFile.value = file
  
  // 自动填充标题（如果为空）
  if (!formData.value.title) {
    formData.value.title = file.name.replace(/\.[^/.]+$/, '')
  }
}

// 清除文件
function clearFile() {
  selectedFile.value = null
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

// 表单验证
function validateForm(): boolean {
  errors.value = {}
  
  if (!selectedChapterId.value) {
    alert('请选择章节')
    return false
  }
  
  if (!formData.value.title.trim()) {
    errors.value.title = '请输入资源标题'
    return false
  }
  
  if (!selectedFile.value) {
    alert('请选择要上传的文件')
    return false
  }
  
  return true
}

// 提交表单
async function handleSubmit() {
  if (!validateForm()) return
  
  isUploading.value = true
  uploadProgress.value = 0
  
  try {
    // 模拟上传进度
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10
      }
    }, 200)
    
    // 创建资源
    const resourceData: ResourceCreate = {
      ...formData.value,
      chapter_id: Number(selectedChapterId.value)
    }
    
    const resource = await resourceService.createResource(
      resourceData,
      selectedFile.value!
    )
    
    clearInterval(progressInterval)
    uploadProgress.value = 100
    
    // 成功提示
    emit('success', resource.id)
    
    // 延迟关闭，让用户看到100%
    setTimeout(() => {
      close()
    }, 500)
  } catch (error: any) {
    console.error('Failed to upload resource:', error)
    alert(error.message || '上传失败，请重试')
  } finally {
    isUploading.value = false
    uploadProgress.value = 0
  }
}

// 重置表单
function resetForm() {
  selectedSubjectId.value = ''
  selectedGradeId.value = ''
  selectedCourse.value = null
  selectedCourseId.value = ''
  availableCourses.value = []
  chapters.value = []
  selectedChapterId.value = ''
  
  formData.value = {
    chapter_id: 0,
    title: '',
    description: '',
    resource_type: ResourceType.PDF,
    is_official: true,
    is_downloadable: true,
    display_order: 0
  }
  
  selectedFile.value = null
  errors.value = {}
  isUploading.value = false
  uploadProgress.value = 0
}

// 关闭对话框
function close() {
  emit('update:modelValue', false)
}

// 监听对话框关闭
watch(() => props.modelValue, (isOpen) => {
  if (!isOpen) {
    setTimeout(resetForm, 300)
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 1rem;
}

.modal-dialog {
  background: white;
  border-radius: 0.75rem;
  width: 100%;
  max-width: 700px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
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
  padding: 0.5rem;
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  border-radius: 0.375rem;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #111827;
}

.icon {
  width: 1.5rem;
  height: 1.5rem;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.form-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e5e7eb;
}

.form-group {
  margin-bottom: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.required {
  color: #ef4444;
}

.form-input,
.form-select {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-select:disabled {
  background: #f3f4f6;
  color: #9ca3af;
  cursor: not-allowed;
}

.form-input.input-error {
  border-color: #ef4444;
}

.error-text {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #ef4444;
}

.course-display {
  margin-top: 1rem;
}

.course-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  border-radius: 0.5rem;
}

.badge-icon {
  font-size: 1.25rem;
}

.badge-text {
  font-weight: 500;
  color: #065f46;
}

.checkbox-group {
  display: flex;
  gap: 1.5rem;
  margin-top: 0.75rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #374151;
  cursor: pointer;
}

.checkbox-input {
  width: 1.125rem;
  height: 1.125rem;
  border-radius: 0.25rem;
  cursor: pointer;
}

.upload-area {
  margin-top: 0.75rem;
}

.upload-zone {
  border: 2px dashed #d1d5db;
  border-radius: 0.75rem;
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-zone:hover {
  border-color: #3b82f6;
  background: #f0f9ff;
}

.upload-icon {
  width: 3rem;
  height: 3rem;
  margin: 0 auto 1rem;
  color: #9ca3af;
}

.upload-text {
  font-size: 0.938rem;
  color: #374151;
  margin: 0 0 0.5rem;
}

.upload-hint {
  font-size: 0.813rem;
  color: #9ca3af;
  margin: 0;
}

.file-preview {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 0.5rem;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.file-icon {
  font-size: 2rem;
}

.file-name {
  font-weight: 500;
  color: #0c4a6e;
  margin-bottom: 0.125rem;
}

.file-size {
  font-size: 0.813rem;
  color: #0369a1;
}

.remove-btn {
  padding: 0.5rem;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 0.375rem;
  color: #dc2626;
  cursor: pointer;
  transition: all 0.2s;
}

.remove-btn:hover {
  background: #fecaca;
}

.hidden {
  display: none;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover:not(:disabled) {
  background: #f9fafb;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

/* 动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-dialog,
.modal-leave-active .modal-dialog {
  transition: transform 0.3s ease;
}

.modal-enter-from .modal-dialog,
.modal-leave-to .modal-dialog {
  transform: translateY(-1rem);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>

