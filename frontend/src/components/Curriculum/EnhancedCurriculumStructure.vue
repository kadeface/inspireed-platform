<template>
  <div class="enhanced-curriculum-structure bg-white rounded-lg shadow-sm">
    <!-- 顶部标题栏 -->
    <div class="flex items-center justify-between p-6 border-b border-gray-200">
      <div class="flex items-center space-x-4">
        <h2 class="text-xl font-bold text-gray-900">教材资源与课程大纲</h2>
      </div>
      <div class="flex items-center space-x-2">
        <button
          @click="showTextbookModal = true"
          class="px-4 py-2 text-sm text-blue-600 hover:text-blue-700 border border-blue-300 rounded-md hover:bg-blue-50 transition-colors"
        >
          切换教材
        </button>
      </div>
    </div>

    <div class="flex h-96">
      <!-- 左侧：教材选择和课程大纲 -->
      <div class="w-80 border-r border-gray-200 p-6 overflow-y-auto">
        <!-- 当前教材信息 -->
        <div class="mb-6">
          <div class="text-sm text-gray-600 mb-2">当前教材</div>
          <div class="text-lg font-medium text-gray-900 mb-3">
            {{ currentTextbook?.grade?.name }}·{{ currentTextbook?.subject?.name }}·{{ currentTextbook?.version?.name }}·{{ currentTextbook?.semester === 'up' ? '上册' : '下册' }}
          </div>
          
          <!-- 教材封面 -->
          <div class="w-32 h-20 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border border-blue-200 flex items-center justify-center">
            <div class="text-center">
              <div class="text-sm font-bold text-blue-800">{{ currentTextbook?.subject?.name }}</div>
              <div class="text-xs text-blue-600">{{ currentTextbook?.grade?.name }}·{{ currentTextbook?.semester === 'up' ? '上册' : '下册' }}·{{ currentTextbook?.version?.name }}</div>
            </div>
          </div>
        </div>

        <!-- 课程大纲 -->
        <div>
          <div class="text-sm font-medium text-gray-900 mb-3">课程大纲</div>
          <div class="space-y-1">
            <div
              v-for="chapter in courseOutline"
              :key="chapter.id"
              class="chapter-item"
            >
              <div
                class="flex items-center justify-between p-2 rounded-md hover:bg-gray-50 cursor-pointer"
                @click="toggleChapter(chapter.id)"
              >
                <div class="flex items-center space-x-2">
                  <svg
                    :class="[
                      'w-4 h-4 text-gray-400 transition-transform',
                      chapter.is_expanded ? 'rotate-90' : ''
                    ]"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                  </svg>
                  <span class="text-sm text-gray-900">{{ chapter.title }}</span>
                  <span v-if="chapter.lesson_count > 0" class="text-xs text-gray-500">({{ chapter.lesson_count }})</span>
                </div>
              </div>
              
              <!-- 子章节 -->
              <div v-if="chapter.is_expanded && chapter.children" class="ml-6 space-y-1">
                <div
                  v-for="child in chapter.children"
                  :key="child.id"
                  class="flex items-center p-2 rounded-md hover:bg-gray-50 cursor-pointer"
                  @click="selectChapter(child.id)"
                >
                  <div class="w-1 h-1 bg-gray-400 rounded-full mr-3"></div>
                  <span class="text-sm text-gray-700">{{ child.title }}</span>
                  <span v-if="child.lesson_count > 0" class="text-xs text-gray-500 ml-2">({{ child.lesson_count }})</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：资源展示 -->
      <div class="flex-1 p-6">
        <!-- 资源筛选和排序 -->
        <div class="flex items-center justify-between mb-6">
          <div class="flex space-x-1 bg-gray-100 rounded-lg p-1">
            <button
              v-for="filter in resourceFilters"
              :key="filter.value"
              @click="currentFilter = filter.value"
              :class="[
                'px-4 py-2 text-sm rounded-md transition-colors',
                currentFilter === filter.value
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              ]"
            >
              {{ filter.label }}
            </button>
          </div>
          
          <div class="flex items-center space-x-2">
            <span class="text-sm text-gray-600">智能排序</span>
            <select
              v-model="sortBy"
              class="text-sm border border-gray-300 rounded-md px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="default">默认排序</option>
              <option value="rating">评分排序</option>
              <option value="views">观看量排序</option>
              <option value="likes">点赞数排序</option>
              <option value="date">时间排序</option>
            </select>
          </div>
        </div>

        <!-- 资源列表 -->
        <div class="space-y-4">
          <div
            v-for="resource in filteredResources"
            :key="resource.id"
            class="resource-card flex space-x-4 p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow cursor-pointer"
            @click="selectResource(resource.id)"
          >
            <!-- 缩略图 -->
            <div class="w-32 h-20 bg-gradient-to-br from-green-50 to-green-100 rounded-lg border border-green-200 flex-shrink-0 flex items-center justify-center">
              <div class="text-center">
                <div class="text-xs text-green-800 font-medium">国家中小学课程资源</div>
                <div class="text-sm font-bold text-green-900 mt-1">{{ resource.title }}</div>
                <div class="text-xs text-green-700 mt-1">
                  <div>年级: {{ resource.grade }}</div>
                  <div>主讲人: {{ resource.instructor }}</div>
                  <div>学科: {{ resource.subject }}</div>
                </div>
              </div>
            </div>

            <!-- 资源信息 -->
            <div class="flex-1">
              <div class="flex items-start justify-between mb-2">
                <div class="flex items-center space-x-2">
                  <span
                    :class="[
                      'px-2 py-1 text-xs rounded-full',
                      resource.type === 'course_package' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'
                    ]"
                  >
                    {{ getResourceTypeLabel(resource.type) }}
                  </span>
                  <h3 class="text-lg font-medium text-gray-900">{{ resource.title }}</h3>
                </div>
                <div class="flex items-center space-x-1">
                  <svg class="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                  </svg>
                  <span class="text-sm text-gray-600">{{ resource.rating }}</span>
                </div>
              </div>

              <div class="text-sm text-gray-600 mb-2">
                <span class="font-medium">主讲人：</span>{{ resource.instructor }} · 
                <span class="font-medium">出版社：</span>{{ resource.publisher }} · 
                <span class="font-medium">时间：</span>{{ resource.publish_date }}
              </div>

              <div class="flex items-center space-x-4 text-sm text-gray-500">
                <span>👁️ {{ formatNumber(resource.view_count) }}</span>
                <span>👍 {{ formatNumber(resource.like_count) }}</span>
                <span v-if="resource.duration">⏱️ {{ resource.duration }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="filteredResources.length === 0" class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <p class="text-gray-500">暂无相关资源</p>
        </div>
      </div>
    </div>

    <!-- 教材选择模态框 -->
    <div
      v-if="showTextbookModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="showTextbookModal = false"
    >
      <div
        class="bg-white rounded-lg p-6 w-96 max-h-96 overflow-y-auto"
        @click.stop
      >
        <h3 class="text-lg font-medium text-gray-900 mb-4">选择教材</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">学段</label>
            <select v-model="selectedStage" class="w-full border border-gray-300 rounded-md px-3 py-2">
              <option value="">请选择学段</option>
              <option value="1">小学</option>
              <option value="2">初中</option>
              <option value="3">高中</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">年级</label>
            <select v-model="selectedGrade" class="w-full border border-gray-300 rounded-md px-3 py-2">
              <option value="">请选择年级</option>
              <option v-for="grade in availableGrades" :key="grade.id" :value="grade.id">
                {{ grade.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">学科</label>
            <select v-model="selectedSubject" class="w-full border border-gray-300 rounded-md px-3 py-2">
              <option value="">请选择学科</option>
              <option v-for="subject in availableSubjects" :key="subject.id" :value="subject.id">
                {{ subject.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">版本</label>
            <select v-model="selectedVersion" class="w-full border border-gray-300 rounded-md px-3 py-2">
              <option value="">请选择版本</option>
              <option v-for="version in availableVersions" :key="version.id" :value="version.id">
                {{ version.name }}
              </option>
            </select>
          </div>
        </div>
        <div class="flex justify-end space-x-3 mt-6">
          <button
            @click="showTextbookModal = false"
            class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
          >
            取消
          </button>
          <button
            @click="confirmTextbookSelection"
            class="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            确定
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { 
  Textbook, 
  Chapter, 
  CourseResource, 
  Subject, 
  Grade, 
  TextbookVersion 
} from '@/types/curriculum'

const emit = defineEmits<{
  'resource-selected': [resourceId: number]
  'chapter-selected': [chapterId: number]
}>()

// 状态管理
const showTextbookModal = ref(false)
const currentFilter = ref('all')
const sortBy = ref('default')
const selectedStage = ref('')
const selectedGrade = ref('')
const selectedSubject = ref('')
const selectedVersion = ref('')

// 当前选中的教材
const currentTextbook = ref<Textbook | null>(null)

// 资源筛选选项
const resourceFilters = [
  { label: '全部', value: 'all' },
  { label: '课程', value: 'course' },
  { label: '课程包', value: 'course_package' }
]

// 模拟数据
const mockTextbook: Textbook = {
  id: 1,
  subject_id: 1,
  grade_id: 1,
  version_id: 1,
  name: '小学语文统编版',
  semester: 'up',
  is_active: true,
  created_at: '2024-01-01',
  updated_at: '2024-01-01',
  subject: { id: 1, name: '语文', code: 'chinese', is_active: true, display_order: 1, created_at: '2024-01-01', updated_at: '2024-01-01' },
  grade: { id: 1, name: '一年级', level: 1, stage_id: 1, is_active: true, created_at: '2024-01-01', updated_at: '2024-01-01' },
  version: { id: 1, name: '统编版', code: 'unified', publisher: '人民教育出版社', is_active: true, created_at: '2024-01-01', updated_at: '2024-01-01' }
}

const mockChapters: Chapter[] = [
  {
    id: 1,
    textbook_id: 1,
    title: '我上学了',
    order: 1,
    is_expanded: true,
    lesson_count: 4,
    children: [
      { id: 11, textbook_id: 1, parent_id: 1, title: '我是中国人', order: 1, is_expanded: false, lesson_count: 1 },
      { id: 12, textbook_id: 1, parent_id: 1, title: '我爱我们的祖国', order: 2, is_expanded: false, lesson_count: 1 },
      { id: 13, textbook_id: 1, parent_id: 1, title: '我是小学生', order: 3, is_expanded: false, lesson_count: 1 },
      { id: 14, textbook_id: 1, parent_id: 1, title: '我爱学语文', order: 4, is_expanded: false, lesson_count: 1 }
    ]
  },
  {
    id: 2,
    textbook_id: 1,
    title: '第一单元·识字',
    order: 2,
    is_expanded: false,
    lesson_count: 8
  },
  {
    id: 3,
    textbook_id: 1,
    title: '第二单元·汉语拼音',
    order: 3,
    is_expanded: false,
    lesson_count: 12
  },
  {
    id: 4,
    textbook_id: 1,
    title: '第三单元·汉语拼音',
    order: 4,
    is_expanded: false,
    lesson_count: 10
  },
  {
    id: 5,
    textbook_id: 1,
    title: '第四单元·汉语拼音',
    order: 5,
    is_expanded: false,
    lesson_count: 8
  },
  {
    id: 6,
    textbook_id: 1,
    title: '第五单元·阅读',
    order: 6,
    is_expanded: false,
    lesson_count: 6
  },
  {
    id: 7,
    textbook_id: 1,
    title: '第六单元·识字',
    order: 7,
    is_expanded: false,
    lesson_count: 8
  }
]

const mockResources: CourseResource[] = [
  {
    id: 1,
    chapter_id: 11,
    title: '我是中国人',
    type: 'course_package',
    instructor: '窦丽娜',
    publisher: '人民教育出版社',
    publish_date: '2024/12/02',
    view_count: 1380000,
    like_count: 89000,
    rating: 4.9,
    duration: '45分钟',
    is_featured: true,
    tags: ['语文', '一年级', '统编版'],
    grade: '一年级',
    subject: '语文(统编版)'
  },
  {
    id: 2,
    chapter_id: 12,
    title: '我爱我们的祖国',
    type: 'course_package',
    instructor: '樊微微',
    publisher: '人民教育出版社',
    publish_date: '2024/11/06',
    view_count: 412000,
    like_count: 61000,
    rating: 5.0,
    duration: '40分钟',
    is_featured: true,
    tags: ['语文', '一年级', '统编版'],
    grade: '一年级',
    subject: '语文(统编版)'
  },
  {
    id: 3,
    chapter_id: 13,
    title: '我是小学生',
    type: 'course_package',
    instructor: '樊微微',
    publisher: '人民教育出版社',
    publish_date: '2024/09/10',
    view_count: 295000,
    like_count: 41000,
    rating: 5.0,
    duration: '38分钟',
    is_featured: false,
    tags: ['语文', '一年级', '统编版'],
    grade: '一年级',
    subject: '语文(统编版)'
  }
]

// 计算属性
const courseOutline = ref<Chapter[]>(mockChapters)
const availableGrades = ref<Grade[]>([
  { id: 1, name: '一年级', level: 1, stage_id: 1, is_active: true, created_at: '2024-01-01', updated_at: '2024-01-01' },
  { id: 2, name: '二年级', level: 2, stage_id: 1, is_active: true, created_at: '2024-01-01', updated_at: '2024-01-01' },
  { id: 3, name: '三年级', level: 3, stage_id: 1, is_active: true, created_at: '2024-01-01', updated_at: '2024-01-01' }
])

const availableSubjects = ref<Subject[]>([
  { id: 1, name: '语文', code: 'chinese', is_active: true, display_order: 1, created_at: '2024-01-01', updated_at: '2024-01-01' },
  { id: 2, name: '数学', code: 'math', is_active: true, display_order: 2, created_at: '2024-01-01', updated_at: '2024-01-01' }
])

const availableVersions = ref<TextbookVersion[]>([
  { id: 1, name: '统编版', code: 'unified', publisher: '人民教育出版社', is_active: true, created_at: '2024-01-01', updated_at: '2024-01-01' },
  { id: 2, name: '人教版', code: 'pep', publisher: '人民教育出版社', is_active: true, created_at: '2024-01-01', updated_at: '2024-01-01' }
])

const filteredResources = computed(() => {
  let resources = [...mockResources]
  
  // 按类型筛选
  if (currentFilter.value !== 'all') {
    resources = resources.filter(resource => resource.type === currentFilter.value)
  }
  
  // 排序
  switch (sortBy.value) {
    case 'rating':
      resources.sort((a, b) => b.rating - a.rating)
      break
    case 'views':
      resources.sort((a, b) => b.view_count - a.view_count)
      break
    case 'likes':
      resources.sort((a, b) => b.like_count - a.like_count)
      break
    case 'date':
      resources.sort((a, b) => new Date(b.publish_date).getTime() - new Date(a.publish_date).getTime())
      break
  }
  
  return resources
})

// 方法
function toggleChapter(chapterId: number) {
  const chapter = courseOutline.value.find(c => c.id === chapterId)
  if (chapter) {
    chapter.is_expanded = !chapter.is_expanded
  }
}

function selectChapter(chapterId: number) {
  emit('chapter-selected', chapterId)
}

function selectResource(resourceId: number) {
  emit('resource-selected', resourceId)
}

function getResourceTypeLabel(type: string) {
  const labels: Record<string, string> = {
    'course': '课程',
    'course_package': '课程包'
  }
  return labels[type] || type
}

function formatNumber(num: number) {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toString()
}

function confirmTextbookSelection() {
  // 这里应该根据选择的学段、年级、学科、版本来查找对应的教材
  // 暂时使用模拟数据
  currentTextbook.value = mockTextbook
  showTextbookModal.value = false
}

onMounted(() => {
  currentTextbook.value = mockTextbook
})
</script>

<style scoped>
.enhanced-curriculum-structure {
  min-height: 500px;
}

.chapter-item {
  border-radius: 6px;
}

.resource-card:hover {
  transform: translateY(-1px);
}

/* 滚动条样式 */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>