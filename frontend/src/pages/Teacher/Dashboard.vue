<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-gray-900">教师工作台</h1>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-gray-700">{{ userStore.user?.full_name || userStore.user?.username }}</span>
            <button
              @click="handleLogout"
              class="px-4 py-2 text-sm text-red-600 hover:text-red-700"
            >
              退出登录
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <!-- MVP: 课程和资源浏览（新组件） -->
        <div class="mb-8">
          <CurriculumWithResources 
            @lesson-created="handleLessonCreated"
          />
        </div>

        <!-- 页面标题和操作栏 -->
        <div class="mb-6">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h2 class="text-2xl font-bold text-gray-900">我的教案</h2>
              <p class="mt-1 text-sm text-gray-500">
                共 {{ lessonStore.totalLessons }} 个教案
                <span v-if="selectedGrade" class="ml-2 text-blue-600">
                  - 已筛选: {{ selectedGradeName }}
                </span>
              </p>
            </div>
            <button
              @click="showCreateModal = true"
              class="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              创建新教案
            </button>
          </div>
        </div>

        <!-- 搜索和筛选栏 -->
        <div class="mb-6 flex flex-col sm:flex-row gap-4">
          <!-- 搜索框 -->
          <div class="flex-1">
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="搜索教案标题..."
                class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
          </div>

          <!-- 状态筛选器 -->
          <div class="flex gap-2">
            <button
              v-for="filter in statusFilters"
              :key="filter.value || 'all'"
              @click="currentStatus = filter.value"
              :class="[
                'px-4 py-2 text-sm font-medium rounded-md transition-colors',
                currentStatus === filter.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50',
              ]"
            >
              {{ filter.label }}
            </button>
          </div>
        </div>

        <!-- 错误提示 -->
        <div
          v-if="lessonStore.error"
          class="mb-6 bg-red-50 border border-red-200 rounded-md p-4"
        >
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm text-red-800">{{ lessonStore.error }}</p>
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="lessonStore.isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="i in 6"
            :key="i"
            class="bg-white rounded-lg border border-gray-200 overflow-hidden animate-pulse"
          >
            <div class="h-40 bg-gray-200"></div>
            <div class="p-4">
              <div class="h-6 bg-gray-200 rounded mb-2"></div>
              <div class="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div class="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div
          v-else-if="!lessonStore.isLoading && lessonStore.lessons.length === 0"
          class="bg-white rounded-lg border border-gray-200 p-12 text-center"
        >
          <svg
            class="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">暂无教案</h3>
          <p class="mt-1 text-sm text-gray-500">
            {{ searchQuery || currentStatus ? '未找到符合条件的教案' : '开始创建您的第一个教案吧' }}
          </p>
          <div class="mt-6">
            <button
              v-if="!searchQuery && !currentStatus"
              @click="showCreateModal = true"
              class="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              创建新教案
            </button>
          </div>
        </div>

        <!-- 教案列表 -->
        <div
          v-else
          class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          <LessonCard
            v-for="lesson in lessonStore.lessons"
            :key="lesson.id"
            :lesson="lesson"
            @edit="handleEdit"
            @duplicate="handleDuplicate"
            @delete="handleDeleteClick"
            @publish="handlePublish"
            @view="handleView"
          />
        </div>

        <!-- 分页控件 -->
        <div
          v-if="!lessonStore.isLoading && lessonStore.lessons.length > 0 && lessonStore.totalLessons > lessonStore.pageSize"
          class="mt-6 flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6 rounded-lg"
        >
          <div class="flex flex-1 justify-between sm:hidden">
            <button
              @click="handlePrevPage"
              :disabled="lessonStore.currentPage === 1"
              class="relative inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              上一页
            </button>
            <button
              @click="handleNextPage"
              :disabled="lessonStore.currentPage >= totalPages"
              class="relative ml-3 inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              下一页
            </button>
          </div>
          <div class="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                显示第
                <span class="font-medium">{{ (lessonStore.currentPage - 1) * lessonStore.pageSize + 1 }}</span>
                到
                <span class="font-medium">{{ Math.min(lessonStore.currentPage * lessonStore.pageSize, lessonStore.totalLessons) }}</span>
                条，共
                <span class="font-medium">{{ lessonStore.totalLessons }}</span>
                条
              </p>
            </div>
            <div>
              <nav class="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
                <button
                  @click="handlePrevPage"
                  :disabled="lessonStore.currentPage === 1"
                  class="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span class="sr-only">上一页</span>
                  <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z" clip-rule="evenodd" />
                  </svg>
                </button>
                <span class="relative inline-flex items-center px-4 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300">
                  {{ lessonStore.currentPage }} / {{ totalPages }}
                </span>
                <button
                  @click="handleNextPage"
                  :disabled="lessonStore.currentPage >= totalPages"
                  class="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span class="sr-only">下一页</span>
                  <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
                  </svg>
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 创建教案对话框 -->
    <CreateLessonModal
      v-model="showCreateModal"
      @create="handleCreate"
    />

    <!-- 删除确认对话框 -->
    <ConfirmDialog
      v-model="showDeleteConfirm"
      title="确认删除"
      message="确定要删除这个教案吗？此操作无法撤销。"
      confirm-text="删除"
      cancel-text="取消"
      danger
      @confirm="handleDeleteConfirm"
    />

    <!-- Toast 提示 -->
    <Transition name="toast">
      <div
        v-if="toast.show"
        class="fixed bottom-4 right-4 z-50 max-w-sm"
      >
        <div
          :class="[
            'rounded-lg shadow-lg p-4',
            toast.type === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200',
          ]"
        >
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <svg
                v-if="toast.type === 'success'"
                class="h-5 w-5 text-green-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <svg
                v-else
                class="h-5 w-5 text-red-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <div class="ml-3 flex-1">
              <p
                :class="[
                  'text-sm font-medium',
                  toast.type === 'success' ? 'text-green-800' : 'text-red-800',
                ]"
              >
                {{ toast.message }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDebounceFn } from '@vueuse/core'
import { useUserStore } from '../../store/user'
import { useLessonStore } from '../../store/lesson'
import { LessonStatus } from '../../types/lesson'
import type { LessonCreate } from '../../types/lesson'
import LessonCard from '../../components/Lesson/LessonCard.vue'
import CreateLessonModal from '../../components/Lesson/CreateLessonModal.vue'
import ConfirmDialog from '../../components/Common/ConfirmDialog.vue'
import CurriculumWithResources from '../../components/Curriculum/CurriculumWithResources.vue'

const router = useRouter()
const userStore = useUserStore()
const lessonStore = useLessonStore()

// 本地状态
const showCreateModal = ref(false)
const showDeleteConfirm = ref(false)
const deleteTargetId = ref<number | null>(null)
const searchQuery = ref('')
const currentStatus = ref<LessonStatus | null>(null)
const selectedGrade = ref<number | null>(null)
const selectedGradeName = ref<string>('')

// Toast 提示
const toast = ref({
  show: false,
  type: 'success' as 'success' | 'error',
  message: '',
})

// 状态筛选器
const statusFilters = [
  { label: '全部', value: null },
  { label: '草稿', value: LessonStatus.DRAFT },
  { label: '已发布', value: LessonStatus.PUBLISHED },
  { label: '已归档', value: LessonStatus.ARCHIVED },
]

// 计算总页数
const totalPages = computed(() => {
  return Math.ceil(lessonStore.totalLessons / lessonStore.pageSize)
})

// 加载教案列表
async function loadLessons() {
  try {
    await lessonStore.loadLessons({
      page: lessonStore.currentPage,
      page_size: lessonStore.pageSize,
      status: currentStatus.value || undefined,
      search: searchQuery.value || undefined,
      grade_id: selectedGrade.value || undefined,
    })
  } catch (error: any) {
    showToast('error', error.message || '加载教案列表失败')
  }
}

// 处理年级选择
function handleGradeSelected(gradeId: number | null) {
  selectedGrade.value = gradeId
  selectedGradeName.value = gradeId ? getGradeName(gradeId) : ''
  lessonStore.currentPage = 1 // 重置到第一页
  loadLessons()
}

// MVP: 处理教案创建成功
function handleLessonCreated(lessonId: number) {
  console.log('Lesson created:', lessonId)
  // 刷新教案列表
  loadLessons()
  showToast('success', '教案创建成功')
}

// 获取年级名称（这里需要根据实际数据结构调整）
function getGradeName(gradeId: number): string {
  // 这里应该根据实际的年级数据来获取名称
  // 暂时返回一个简单的映射
  const gradeNames: Record<number, string> = {
    1: '一年级', 2: '二年级', 3: '三年级', 4: '四年级', 5: '五年级', 6: '六年级',
    7: '七年级', 8: '八年级', 9: '九年级',
    10: '高一', 11: '高二', 12: '高三'
  }
  return gradeNames[gradeId] || `年级${gradeId}`
}

// 搜索防抖
const debouncedSearch = useDebounceFn(() => {
  lessonStore.currentPage = 1 // 重置到第一页
  loadLessons()
}, 300)

// 创建教案
async function handleCreate(lessonData: LessonCreate) {
  try {
    const newLesson = await lessonStore.createNewLesson(lessonData)
    showCreateModal.value = false
    showToast('success', '教案创建成功')
    
    // 跳转到编辑页面
    router.push(`/teacher/lesson/${newLesson.id}`)
  } catch (error: any) {
    showToast('error', error.message || '创建教案失败')
  }
}

// 编辑教案
function handleEdit(lessonId: number) {
  router.push(`/teacher/lesson/${lessonId}`)
}

// 查看教案
function handleView(lessonId: number) {
  router.push(`/teacher/lesson/${lessonId}`)
}

// 复制教案
async function handleDuplicate(lessonId: number) {
  try {
    await lessonStore.duplicateLessonById(lessonId)
    showToast('success', '教案复制成功')
    loadLessons() // 刷新列表
  } catch (error: any) {
    showToast('error', error.message || '复制教案失败')
  }
}

// 删除教案 - 显示确认对话框
function handleDeleteClick(lessonId: number) {
  deleteTargetId.value = lessonId
  showDeleteConfirm.value = true
}

// 确认删除
async function handleDeleteConfirm() {
  if (deleteTargetId.value === null) return
  
  try {
    await lessonStore.deleteLessonById(deleteTargetId.value)
    showToast('success', '教案删除成功')
    
    // 如果当前页没有数据了，回到上一页
    if (lessonStore.lessons.length === 0 && lessonStore.currentPage > 1) {
      lessonStore.currentPage -= 1
    }
    loadLessons()
  } catch (error: any) {
    showToast('error', error.message || '删除教案失败')
  } finally {
    deleteTargetId.value = null
  }
}

// 发布教案
async function handlePublish(lessonId: number) {
  try {
    await lessonStore.publishCurrentLesson()
    showToast('success', '教案发布成功')
    loadLessons() // 刷新列表
  } catch (error: any) {
    // 如果当前教案不是要发布的，先加载
    try {
      await lessonStore.loadLesson(lessonId)
      await lessonStore.publishCurrentLesson()
      showToast('success', '教案发布成功')
      loadLessons()
    } catch (err: any) {
      showToast('error', err.message || '发布教案失败')
    }
  }
}

// 上一页
function handlePrevPage() {
  if (lessonStore.currentPage > 1) {
    lessonStore.currentPage -= 1
    loadLessons()
  }
}

// 下一页
function handleNextPage() {
  if (lessonStore.currentPage < totalPages.value) {
    lessonStore.currentPage += 1
    loadLessons()
  }
}

// 退出登录
function handleLogout() {
  userStore.logout()
  router.push('/login')
}

// 显示 Toast
function showToast(type: 'success' | 'error', message: string) {
  toast.value = { show: true, type, message }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

// 监听搜索查询变化
watch(searchQuery, () => {
  debouncedSearch()
})

// 监听状态筛选变化
watch(currentStatus, () => {
  lessonStore.currentPage = 1 // 重置到第一页
  loadLessons()
})

// 页面加载时获取数据
onMounted(() => {
  loadLessons()
})
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(1rem);
}
</style>
