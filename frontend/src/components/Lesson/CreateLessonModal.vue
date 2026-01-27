<template>
  <Transition name="modal">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 overflow-y-auto"
      @click.self="handleClose"
    >
      <div class="flex min-h-screen items-start justify-center p-4 py-8">
        <!-- 遮罩层 -->
        <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"></div>

        <!-- 对话框内容 -->
        <div class="relative w-full max-w-5xl max-h-[90vh] transform rounded-lg bg-white p-6 shadow-xl transition-all overflow-y-auto">
          <div class="flex flex-col gap-6 lg:flex-row">
            <div class="flex-1">
              <!-- 标题 -->
              <div class="mb-6">
                <h3 class="text-xl font-semibold text-gray-900">创建新教案</h3>
                <p class="mt-1 text-sm text-gray-500">填写教案基本信息，开始创作</p>
              </div>

              <!-- 表单 -->
              <form @submit.prevent="handleSubmit">
                <!-- 课程选择 -->
                <div class="mb-4 rounded-md bg-blue-50 p-4">
                  <label class="mb-3 block text-sm font-medium text-gray-700">
                    选择课程 <span class="text-red-500">*</span>
                  </label>
                  
                  <!-- 学科选择 -->
                  <div class="mb-3">
                    <select
                      v-model="selectedSubjectId"
                      @change="handleSubjectChange"
                      class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-gray-900 shadow-sm placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    >
                      <option value="">请选择学科</option>
                      <option 
                        v-for="subject in subjects" 
                        :key="subject.id" 
                        :value="subject.id"
                      >
                        {{ subject.name }}
                      </option>
                    </select>
                  </div>

                  <!-- 年级选择 -->
                  <div class="mb-3">
                    <select
                      v-model="selectedGradeId"
                      @change="handleGradeChange"
                      :disabled="!selectedSubjectId"
                      class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-gray-900 shadow-sm placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:bg-gray-100 disabled:text-gray-500"
                      required
                    >
                      <option value="">请选择年级</option>
                      <option 
                        v-for="grade in grades" 
                        :key="grade.id" 
                        :value="grade.id"
                      >
                        {{ grade.name }}
                      </option>
                    </select>
                  </div>

                  <!-- 课程选择 -->
                  <div v-if="availableCourses.length > 0" class="mb-3">
                    <select
                      v-model="selectedCourseId"
                      class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-gray-900 shadow-sm placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
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

                  <!-- 课程显示 -->
                  <div v-if="selectedCourse" class="rounded border border-blue-200 bg-white p-3">
                    <div class="flex items-center gap-2">
                      <span class="text-sm font-medium text-blue-700">已选课程：</span>
                      <span class="text-sm text-gray-900">{{ selectedCourse.name }}</span>
                    </div>
                  </div>
                  <div
                    v-else-if="selectedSubjectId && selectedGradeId && !loadingCourse"
                    class="rounded border border-yellow-200 bg-yellow-50 p-3"
                  >
                    <p class="text-sm text-yellow-700">该学科和年级的课程不存在，请联系管理员创建</p>
                  </div>
                </div>

                <!-- 章节选择（可选但推荐） -->
                <div v-if="selectedCourse" class="mb-4 rounded-md bg-green-50 p-4">
                  <label class="mb-3 block text-sm font-medium text-gray-700">
                    选择章节 <span class="text-gray-500">(推荐)</span>
                  </label>
                  <p class="mb-3 text-xs text-gray-600">
                    💡 选择章节后，教案将与课程体系关联，便于组织和查找
                  </p>
                  
                  <select
                    v-model="formData.chapter_id"
                    :disabled="loadingChapters"
                    class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-gray-900 shadow-sm placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:text-gray-500"
                  >
                    <option :value="null">不关联章节（稍后可以补充）</option>
                    <optgroup 
                      v-for="chapter in chapters" 
                      :key="chapter.id" 
                      :label="chapter.name"
                    >
                      <option :value="chapter.id">{{ chapter.name }}</option>
                      <option 
                        v-for="subChapter in chapter.children" 
                        :key="subChapter.id" 
                        :value="subChapter.id"
                        class="pl-4"
                      >
                        &nbsp;&nbsp;&nbsp;&nbsp;{{ subChapter.name }}
                      </option>
                    </optgroup>
                  </select>

                  <div v-if="loadingChapters" class="mt-2 text-sm text-gray-500">
                    加载章节列表...
                  </div>
                </div>

                <!-- 教案标题 -->
                <div class="mb-4">
                  <label for="title" class="mb-2 block text-sm font-medium text-gray-700">
                    教案标题 <span class="text-red-500">*</span>
                  </label>
                  <input
                    id="title"
                    v-model="formData.title"
                    type="text"
                    required
                    placeholder="例如：Python 基础入门"
                    class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-gray-900 shadow-sm placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    :class="{ 'border-red-500': errors.title }"
                  />
                  <p v-if="errors.title" class="mt-1 text-sm text-red-600">{{ errors.title }}</p>
                </div>

                <!-- 教案描述 -->
                <div class="mb-4">
                  <label for="description" class="mb-2 block text-sm font-medium text-gray-700">
                    教案描述
                  </label>
                  <textarea
                    id="description"
                    v-model="formData.description"
                    rows="3"
                    placeholder="简要描述教案内容和目标..."
                    class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-gray-900 shadow-sm placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  ></textarea>
                </div>

                <!-- 教案标签 -->
                <div class="mb-4">
                  <label for="tags" class="mb-2 block text-sm font-medium text-gray-700">
                    标签（可选）
                  </label>
                  <input
                    id="tags"
                    v-model="tagsInput"
                    type="text"
                    placeholder="用逗号分隔，例如：Python, 编程, 初级"
                    class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-gray-900 shadow-sm placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <!-- 模板选择 -->
                <div class="mb-6">
                  <label class="mb-3 block text-sm font-medium text-gray-700">选择模板</label>
                  <div class="grid grid-cols-3 gap-3">
                    <button
                      type="button"
                      v-for="template in templates"
                      :key="template.id"
                      @click="selectedTemplate = template.id"
                      :class="[
                        'rounded-lg border-2 p-4 text-center transition-all',
                        selectedTemplate === template.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300',
                      ]"
                    >
                      <div class="mb-2 text-2xl">{{ template.icon }}</div>
                      <div class="text-sm font-medium text-gray-900">{{ template.name }}</div>
                      <div class="mt-1 text-xs text-gray-500">{{ template.description }}</div>
                    </button>
                  </div>
                </div>

                <!-- 操作按钮 -->
                <div class="flex justify-end gap-3">
                  <button
                    type="button"
                    @click="handleClose"
                    class="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    取消
                  </button>
                  <button
                    type="submit"
                    :disabled="isSubmitting"
                    class="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {{ isSubmitting ? '创建中...' : '创建教案' }}
                  </button>
                </div>
              </form>
            </div>

            <!-- 关联素材侧栏 -->
            <aside class="w-full shrink-0 lg:w-80 xl:w-96">
              <div class="flex h-full flex-col rounded-lg border border-gray-200 bg-gray-50 p-4">
                <div class="mb-4 flex items-start justify-between gap-3">
                  <div>
                    <h4 class="text-base font-semibold text-gray-900">关联素材</h4>
                    <p class="text-xs text-gray-500">
                      选课后可预览素材、插入引用
                    </p>
                  </div>
                  <button
                    type="button"
                    class="text-xs text-blue-600 hover:text-blue-700 disabled:text-gray-400"
                    :disabled="!selectedCourse || materialsLoading"
                    @click="handleReloadMaterials"
                  >
                    刷新
                  </button>
                </div>

                <div class="grid grid-cols-1 gap-3">
                  <div>
                    <label class="sr-only" for="material-search">搜索素材</label>
                    <div class="relative">
                      <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-gray-400">
                        🔍
                      </span>
                      <input
                        id="material-search"
                        v-model="materialSearch"
                        type="search"
                        placeholder="搜索标题或标签"
                        class="w-full rounded-md border border-gray-300 bg-white pl-9 pr-3 py-2 text-sm text-gray-900 shadow-sm placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:text-gray-500"
                        :disabled="!selectedCourse"
                      />
                    </div>
                  </div>

                  <div class="flex gap-2">
                    <label class="sr-only" for="material-type">素材类型</label>
                    <select
                      id="material-type"
                      v-model="materialTypeFilter"
                      class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:bg-gray-100 disabled:text-gray-500"
                      :disabled="!selectedCourse"
                    >
                      <option value="all">全部类型</option>
                      <option
                        v-for="option in materialTypeOptions"
                        :key="option.value"
                        :value="option.value"
                      >
                        {{ option.label }}
                      </option>
                    </select>
                  </div>
                </div>

                <div class="mt-4 flex-1 overflow-hidden">
                  <div class="h-full overflow-y-auto pr-1">
                    <div v-if="materialsLoading" class="space-y-3">
                      <div v-for="n in 3" :key="n" class="animate-pulse rounded-md bg-white p-3 shadow-sm">
                        <div class="mb-2 h-4 w-2/3 rounded bg-gray-200"></div>
                        <div class="h-3 w-1/2 rounded bg-gray-100"></div>
                      </div>
                    </div>
                    <div v-else-if="materialsError" class="rounded-md bg-white p-4 text-sm text-red-600 shadow-sm">
                      <p class="mb-2">{{ materialsError }}</p>
                      <button
                        type="button"
                        class="text-blue-600 hover:text-blue-700"
                        @click="handleReloadMaterials"
                      >
                        重试
                      </button>
                    </div>
                    <div
                      v-else-if="selectedCourse && filteredMaterials.length > 0"
                      class="space-y-3"
                    >
                      <article
                        v-for="material in filteredMaterials"
                        :key="material.id"
                        class="group relative rounded-md bg-white p-3 shadow-sm ring-1 ring-gray-200 transition hover:shadow-md"
                      >
                        <div class="flex items-start gap-3">
                          <div class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-md bg-blue-50 text-xl">
                            {{ getMaterialIcon(material.resource_type) }}
                          </div>
                          <div class="min-w-0 flex-1">
                            <p class="truncate text-sm font-medium text-gray-900" :title="material.title">
                              {{ material.title }}
                            </p>
                            <p class="mt-1 line-clamp-2 text-xs text-gray-500">
                              {{ material.summary || '暂无摘要描述' }}
                            </p>
                            <p v-if="material.source_lesson_title" class="mt-1 text-xs text-gray-400">
                              来源：{{ material.source_lesson_title }}
                            </p>
                            <p v-if="material.updated_at" class="mt-1 text-xs text-gray-400">
                              更新：{{ formatDate(material.updated_at) }}
                            </p>
                          </div>
                        </div>
                        <div class="mt-3 flex items-center justify-between">
                          <div class="flex flex-wrap gap-1">
                            <span
                              v-if="!material.is_accessible"
                              class="rounded-full bg-yellow-100 px-2 py-0.5 text-[11px] text-yellow-700"
                            >
                              权限受限
                            </span>
                            <span
                              v-for="tag in material.tags?.slice(0, 3)"
                              :key="tag"
                              class="rounded-full bg-blue-100 px-2 py-0.5 text-[11px] text-blue-700"
                            >
                              {{ tag }}
                            </span>
                          </div>
                          <div class="flex gap-2">
                            <button
                              type="button"
                              class="rounded-full border border-gray-200 px-3 py-1 text-xs text-gray-600 hover:border-blue-500 hover:text-blue-600"
                              @click="openMaterialPreview(material)"
                            >
                              预览
                            </button>
                            <button
                              type="button"
                              class="rounded-full border border-gray-200 px-3 py-1 text-xs text-gray-600 hover:border-blue-500 hover:text-blue-600"
                              @click="insertMaterial(material)"
                              :disabled="!material.is_accessible"
                            >
                              插入正文
                            </button>
                            <button
                              type="button"
                              :class="[
                                'rounded-full px-3 py-1 text-xs font-medium',
                                isReferenceSelected(material.id)
                                  ? 'bg-green-100 text-green-700'
                                  : 'border border-blue-500 text-blue-600 hover:bg-blue-50'
                              ]"
                              @click="toggleReference(material)"
                              :disabled="!material.is_accessible"
                            >
                              {{ isReferenceSelected(material.id) ? '已加入' : '加入参考' }}
                            </button>
                          </div>
                        </div>
                      </article>
                    </div>
                    <div
                      v-else-if="selectedCourse"
                      class="rounded-md bg-white p-4 text-sm text-gray-500 shadow-sm"
                    >
                      暂无符合条件的素材，试试调整筛选或稍后再来。
                    </div>
                    <div
                      v-else
                      class="rounded-md bg-white p-4 text-sm text-gray-500 shadow-sm"
                    >
                      请先选择课程以查看推荐素材。
                    </div>
                  </div>
                </div>

                <div
                  v-if="previewMaterial"
                  class="mt-4 rounded-md bg-white p-3 text-sm shadow-sm"
                >
                  <div class="mb-2 flex items-start justify-between gap-3">
                    <div>
                      <h5 class="text-sm font-semibold text-gray-900">{{ previewMaterial.title }}</h5>
                      <p class="mt-1 text-xs text-gray-500">
                        类型：{{ getMaterialTypeName(previewMaterial.resource_type) }}
                      </p>
                    </div>
                    <button
                      type="button"
                      class="text-xs text-gray-400 hover:text-gray-600"
                      @click="closeMaterialPreview"
                    >
                      ✕
                    </button>
                  </div>
                  <p class="mb-2 whitespace-pre-wrap text-xs text-gray-600">
                    {{ previewMaterial.summary || '暂无详细描述，可使用预览链接查看完整内容。' }}
                  </p>
                  <div class="flex flex-col gap-2">
                    <a
                      v-if="previewMaterial.preview_url"
                      :href="previewMaterial.preview_url"
                      target="_blank"
                      rel="noopener"
                      class="text-xs text-blue-600 hover:text-blue-700"
                    >
                      打开预览
                    </a>
                    <a
                      v-if="previewMaterial.download_url"
                      :href="previewMaterial.download_url"
                      target="_blank"
                      rel="noopener"
                      class="text-xs text-blue-600 hover:text-blue-700"
                    >
                      下载素材
                    </a>
                    <button
                      type="button"
                      class="w-full rounded-md border border-blue-500 px-3 py-2 text-xs font-medium text-blue-600 hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-60"
                      :disabled="!previewMaterial.is_accessible"
                      @click="insertMaterial(previewMaterial)"
                    >
                      插入到正文
                    </button>
                    <p
                      v-if="!previewMaterial.preview_url && !previewMaterial.download_url"
                      class="text-xs text-gray-400"
                    >
                      暂无可用的预览或下载链接。
                    </p>
                  </div>
                </div>

                <div
                  v-if="selectedReferences.length > 0"
                  class="mt-4 rounded-md border border-green-200 bg-green-50 p-3 text-xs text-green-700"
                >
                  已选择 {{ selectedReferences.length }} 个素材作为参考。
                </div>
              </div>
            </aside>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import type {
  LessonCreate,
  LessonRelatedMaterial,
  LessonReferenceMaterialInput
} from '../../types/lesson'
import type { Cell } from '../../types/cell'
import { CellType } from '../../types/cell'
import type { Subject, Grade, Course, Chapter } from '../../types/curriculum'
import curriculumService from '../../services/curriculum'
import { lessonService } from '../../services/lesson'
import {
  ResourceType,
  getResourceTypeIcon,
  getResourceTypeName
} from '../../types/resource'

interface Props {
  modelValue: boolean
  initialChapterId?: number | null
  initialCourseId?: number | null
}

const props = withDefaults(defineProps<Props>(), {
  initialChapterId: null,
  initialCourseId: null
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  create: [lessonData: LessonCreate]
  'insert-material': [material: LessonRelatedMaterial]
}>()

// 课程选择数据
const subjects = ref<Subject[]>([])
const grades = ref<Grade[]>([])
const selectedSubjectId = ref<number | string>('')
const selectedGradeId = ref<number | string>('')
const selectedCourse = ref<Course | null>(null)
const selectedCourseId = ref<number | ''>('')
const availableCourses = ref<Course[]>([])
const loadingCourse = ref(false)

// 章节数据
const chapters = ref<Chapter[]>([])
const loadingChapters = ref(false)

// 表单数据
const formData = ref({
  title: '',
  description: '',
  chapter_id: null as number | null,
})

const tagsInput = ref('')
const selectedTemplate = ref('blank')
const isSubmitting = ref(false)
const errors = ref<Record<string, string>>({})

// 关联素材数据
const relatedMaterials = ref<LessonRelatedMaterial[]>([])
const materialsLoading = ref(false)
const materialsError = ref<string | null>(null)
const materialSearch = ref('')
const materialTypeFilter = ref<'all' | ResourceType>('all')
const selectedReferences = ref<LessonReferenceMaterialInput[]>([])
const previewMaterial = ref<LessonRelatedMaterial | null>(null)

const materialTypeOptions = computed(() =>
  Object.values(ResourceType).map((type) => ({
    value: type,
    label: getResourceTypeName(type),
  }))
)

const filteredMaterials = computed(() => {
  let list = [...relatedMaterials.value]
  if (materialTypeFilter.value !== 'all') {
    list = list.filter(
      (material) => resolveResourceType(material.resource_type) === materialTypeFilter.value
    )
  }
  if (materialSearch.value.trim()) {
    const keyword = materialSearch.value.trim().toLowerCase()
    list = list.filter((material) => {
      const titleMatch = material.title.toLowerCase().includes(keyword)
      const tagMatch = material.tags?.some((tag) => tag.toLowerCase().includes(keyword))
      const summary = material.summary?.toLowerCase() ?? ''
      const summaryMatch = summary.includes(keyword)
      return titleMatch || tagMatch || summaryMatch
    })
  }
  return list
})

// 加载学科和年级
onMounted(async () => {
  try {
    const [subjectsData, gradesData] = await Promise.all([
      curriculumService.getSubjects(),
      curriculumService.getGrades()
    ])
    subjects.value = subjectsData
    grades.value = gradesData
  } catch (error) {
    console.error('Failed to load curriculum data:', error)
  }
})

// 处理学科变更
async function handleSubjectChange() {
  selectedGradeId.value = ''
  selectedCourse.value = null
  selectedCourseId.value = ''
  availableCourses.value = []
  resetRelatedMaterials()
}

// 处理年级变更
async function handleGradeChange() {
  if (!selectedSubjectId.value || !selectedGradeId.value) {
    selectedCourse.value = null
    selectedCourseId.value = ''
    availableCourses.value = []
    chapters.value = []
    resetRelatedMaterials()
    return
  }

  loadingCourse.value = true
  try {
    availableCourses.value = await curriculumService.getCourseBySubjectAndGrade(
      Number(selectedSubjectId.value),
      Number(selectedGradeId.value)
    )
    selectedCourse.value = availableCourses.value[0] ?? null
    selectedCourseId.value = selectedCourse.value?.id ?? ''
    
    // 如果找到课程，加载章节
    if (selectedCourse.value) {
      const courseId = selectedCourse.value.id
      await Promise.all([
        loadChapters(courseId),
        loadRelatedMaterials(courseId)
      ])
    } else {
      chapters.value = []
      resetRelatedMaterials()
    }
  } catch (error) {
    console.error('Failed to load course:', error)
    selectedCourse.value = null
    selectedCourseId.value = ''
    availableCourses.value = []
    chapters.value = []
    resetRelatedMaterials()
  } finally {
    loadingCourse.value = false
  }
}

watch(selectedCourseId, async value => {
  if (!value) {
    selectedCourse.value = null
    chapters.value = []
    resetRelatedMaterials()
    return
  }

  const courseId = typeof value === 'string' ? Number(value) : value
  const course = availableCourses.value.find(courseItem => courseItem.id === courseId) ?? null
  selectedCourse.value = course

  if (course) {
    await Promise.all([
      loadChapters(course.id),
      loadRelatedMaterials(course.id)
    ])
  } else {
    chapters.value = []
    resetRelatedMaterials()
  }
})

// 加载章节列表
async function loadChapters(courseId: number) {
  loadingChapters.value = true
  try {
    const chaptersData = await curriculumService.getCourseChapters(courseId, true)
    // 只显示顶层章节和第一级子章节
    chapters.value = chaptersData.filter(ch => !ch.parent_id)
  } catch (error) {
    console.error('Failed to load chapters:', error)
    chapters.value = []
  } finally {
    loadingChapters.value = false
  }
}

async function loadRelatedMaterials(courseId: number) {
  materialsLoading.value = true
  materialsError.value = null
  try {
    const response = await lessonService.fetchRelatedMaterials(courseId)
    relatedMaterials.value = response.items
    if (response.items.length === 0) {
      previewMaterial.value = null
    }
  } catch (error: any) {
    console.error('Failed to load related materials:', error)
    materialsError.value = error?.message || '加载关联素材失败'
    relatedMaterials.value = []
  } finally {
    materialsLoading.value = false
  }
}

function handleReloadMaterials() {
  if (selectedCourse.value) {
    loadRelatedMaterials(selectedCourse.value.id)
  }
}

function resetRelatedMaterials() {
  relatedMaterials.value = []
  materialsError.value = null
  materialsLoading.value = false
  selectedReferences.value = []
  previewMaterial.value = null
  materialSearch.value = ''
  materialTypeFilter.value = 'all'
}

function toggleReference(material: LessonRelatedMaterial) {
  const index = selectedReferences.value.findIndex(
    (item) => item.material_id === material.id
  )
  if (index > -1) {
    selectedReferences.value.splice(index, 1)
  } else {
    if (!material.is_accessible) return
    selectedReferences.value.push({ material_id: material.id })
    emit('insert-material', material)
  }
}

function isReferenceSelected(materialId: number) {
  return selectedReferences.value.some((item) => item.material_id === materialId)
}

function openMaterialPreview(material: LessonRelatedMaterial) {
  previewMaterial.value = material
}

function closeMaterialPreview() {
  previewMaterial.value = null
}

function insertMaterial(material: LessonRelatedMaterial) {
  emit('insert-material', material)
}

function resolveResourceType(type: string | ResourceType): ResourceType | null {
  const candidate = type as ResourceType
  if (Object.values(ResourceType).includes(candidate)) {
    return candidate
  }
  return null
}

function getMaterialIcon(type: string | ResourceType) {
  const resolved = resolveResourceType(type)
  return resolved ? getResourceTypeIcon(resolved) : '📁'
}

function getMaterialTypeName(type: string | ResourceType) {
  const resolved = resolveResourceType(type)
  return resolved ? getResourceTypeName(resolved) : '其他'
}

function formatDate(value?: string) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleDateString()
}

// 模板定义
const templates = [
  {
    id: 'blank',
    name: '空白教案',
    icon: '📄',
    description: '从零开始',
  },
  {
    id: 'theory',
    name: '理论课',
    icon: '📚',
    description: '含文本单元',
  },
  {
    id: 'lab',
    name: '实验课',
    icon: '💻',
    description: '含代码单元',
  },
]

// 解析标签
const parsedTags = computed(() => {
  if (!tagsInput.value.trim()) return []
  return tagsInput.value
    .split(',')
    .map((tag) => tag.trim())
    .filter((tag) => tag.length > 0)
})

// 根据模板生成初始内容
function generateTemplateContent(templateId: string): Cell[] {
  switch (templateId) {
    case 'theory':
      return [
        {
          id: uuidv4(),
          type: CellType.TEXT,
          order: 0,
          editable: true,
          content: {
            html: '<h2>课程概述</h2><p>在此输入课程内容...</p>',
          },
        } as Cell,
      ]
    case 'lab':
      return [
        {
          id: uuidv4(),
          type: CellType.TEXT,
          order: 0,
          editable: true,
          content: {
            html: '<h2>实验说明</h2><p>在此输入实验要求...</p>',
          },
        } as Cell,
        {
          id: uuidv4(),
          type: CellType.CODE,
          order: 1,
          editable: true,
          content: {
            code: '# 在此编写代码\nprint("Hello, World!")',
            language: 'python' as const,
          },
          config: {
            environment: 'jupyterlite' as const,
          },
        } as Cell,
      ]
    default:
      return []
  }
}

// 表单验证
function validateForm(): boolean {
  errors.value = {}
  
  if (!selectedCourse.value) {
    alert('请选择课程')
    return false
  }
  
  if (!formData.value.title.trim()) {
    errors.value.title = '请输入教案标题'
    return false
  }
  
  if (formData.value.title.length > 100) {
    errors.value.title = '标题不能超过100个字符'
    return false
  }
  
  return true
}

// 提交表单
function handleSubmit() {
  if (!validateForm()) return
  
  isSubmitting.value = true
  
  const referenceMaterials =
    selectedReferences.value.length > 0
      ? selectedReferences.value.map((item) => ({ ...item }))
      : undefined

  const lessonData: LessonCreate = {
    title: formData.value.title.trim(),
    description: formData.value.description.trim() || undefined,
    course_id: selectedCourse.value!.id,
    chapter_id: formData.value.chapter_id || undefined,
    tags: parsedTags.value.length > 0 ? parsedTags.value : undefined,
    content: generateTemplateContent(selectedTemplate.value),
    reference_materials: referenceMaterials
  }
  
  emit('create', lessonData)
  
  // 延迟重置，避免闪烁
  setTimeout(() => {
    isSubmitting.value = false
  }, 500)
}

// 关闭对话框
function handleClose() {
  emit('update:modelValue', false)
  // 重置表单
  resetForm()
}

// 重置表单
function resetForm() {
  formData.value = {
    title: '',
    description: '',
    chapter_id: null,
  }
  tagsInput.value = ''
  selectedTemplate.value = 'blank'
  selectedSubjectId.value = ''
  selectedGradeId.value = ''
  selectedCourse.value = null
  selectedCourseId.value = ''
  availableCourses.value = []
  chapters.value = []
  errors.value = {}
  resetRelatedMaterials()
}

// 监听initialCourseId和initialChapterId的变化，自动填充表单
watch(() => [props.modelValue, props.initialCourseId, props.initialChapterId], async ([isOpen, courseId, chapterId]) => {
  const resolvedCourseId = typeof courseId === 'number' ? courseId : null
  if (isOpen && resolvedCourseId !== null) {
    // 从courseId反推subject和grade
    try {
      const courses = await curriculumService.getCourses({})
      const course = courses.find(c => c.id === resolvedCourseId)
      if (course) {
        selectedSubjectId.value = course.subject_id
        selectedGradeId.value = course.grade_id
        selectedCourse.value = course
        selectedCourseId.value = course.id
        availableCourses.value = [course]
        
        // 加载章节
        await Promise.all([
          loadChapters(resolvedCourseId),
          loadRelatedMaterials(resolvedCourseId)
        ])
        
        // 设置初始章节
        if (chapterId) {
          formData.value.chapter_id = chapterId as number
        }
      }
    } catch (error) {
      console.error('Failed to load initial course:', error)
    }
  }
})
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>

