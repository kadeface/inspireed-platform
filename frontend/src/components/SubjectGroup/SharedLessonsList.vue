<template>
  <div class="shared-lessons-list">
    <div v-if="loading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="lessons.length === 0" class="text-center py-12 text-gray-500">
      <i class="fas fa-folder-open text-4xl mb-2"></i>
      <p>暂无共享教学设计</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="lesson in lessons"
        :key="lesson.id"
        class="border rounded-lg p-4 hover:shadow-md transition"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3 mb-2">
              <h4 class="text-lg font-semibold text-gray-900">
                {{ lesson.lesson_title }}
              </h4>
              <span class="text-xs text-gray-500">
                由 {{ lesson.sharer_name }} 分享
              </span>
            </div>
            
            <p class="text-gray-600 text-sm mb-3">
              {{ lesson.lesson_description || '暂无描述' }}
            </p>

            <div v-if="lesson.share_note" class="mb-3 p-2 bg-blue-50 rounded text-sm text-gray-700">
              <i class="fas fa-comment mr-1"></i>
              {{ lesson.share_note }}
            </div>

            <div class="flex items-center space-x-4 text-sm text-gray-500">
              <span><i class="fas fa-cube mr-1"></i>{{ lesson.lesson_cell_count || 0 }} 单元</span>
              <span v-if="lesson.lesson_estimated_duration">
                <i class="fas fa-clock mr-1"></i>{{ lesson.lesson_estimated_duration }} 分钟
              </span>
              <span><i class="fas fa-eye mr-1"></i>{{ lesson.view_count }} 查看</span>
              <span><i class="fas fa-download mr-1"></i>{{ lesson.download_count }} 下载</span>
              <span><i class="fas fa-heart mr-1"></i>{{ lesson.like_count }} 点赞</span>
            </div>
          </div>

          <div class="flex flex-col space-y-2 ml-4">
            <button
              @click="viewLesson(lesson.lesson_id)"
              class="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition"
            >
              <i class="fas fa-eye mr-1"></i>查看
            </button>
            <button
              @click="copyLesson(lesson.lesson_id, groupId)"
              class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 transition"
            >
              <i class="fas fa-copy mr-1"></i>复制
            </button>
            <button
              v-if="canRemove(lesson)"
              @click="handleUnshare(lesson)"
              class="px-3 py-1 text-sm border border-red-300 text-red-600 rounded hover:bg-red-50 transition"
            >
              <i class="fas fa-trash mr-1"></i>移除
            </button>
          </div>
        </div>

        <div class="mt-3 pt-3 border-t text-xs text-gray-500">
          分享于 {{ formatDate(lesson.shared_at) }}
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="mt-6 flex justify-center">
      <nav class="flex space-x-2">
        <button
          @click="currentPage > 1 && changePage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="px-3 py-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          上一页
        </button>
        <button
          v-for="page in displayPages"
          :key="page"
          @click="changePage(page)"
          :class="[
            'px-3 py-2 rounded-lg border',
            page === currentPage
              ? 'bg-blue-600 text-white border-blue-600'
              : 'border-gray-300 hover:bg-gray-50',
          ]"
        >
          {{ page }}
        </button>
        <button
          @click="currentPage < totalPages && changePage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="px-3 py-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          下一页
        </button>
      </nav>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import {
  getSharedLessons,
  unshareLesson,
  incrementLessonView,
  incrementLessonDownload,
} from '@/services/subjectGroup'
import type { SharedLesson, MemberRole } from '@/types/subjectGroup'

const props = defineProps<{
  groupId: number
  userRole?: MemberRole
}>()

const router = useRouter()
const authStore = useAuthStore()

// 数据
const lessons = ref<SharedLesson[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 计算属性
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))
const displayPages = computed(() => {
  const pages: number[] = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// 方法
async function loadLessons() {
  loading.value = true
  try {
    const response = await getSharedLessons(props.groupId, {
      page: currentPage.value,
      page_size: pageSize.value,
    })
    lessons.value = response.items
    total.value = response.total
  } catch (error) {
    console.error('加载共享教学设计失败:', error)
  } finally {
    loading.value = false
  }
}

function changePage(page: number) {
  currentPage.value = page
  loadLessons()
}

async function viewLesson(lessonId: number) {
  try {
    await incrementLessonView(props.groupId, lessonId)
    router.push(`/teacher/lessons/${lessonId}`)
  } catch (error) {
    console.error('查看教案失败:', error)
  }
}

async function copyLesson(lessonId: number, groupId: number) {
  try {
    await incrementLessonDownload(groupId, lessonId)
    // TODO: 实现复制教案功能
    alert('复制功能开发中...')
  } catch (error) {
    console.error('复制教案失败:', error)
  }
}

function canRemove(lesson: SharedLesson): boolean {
  // 分享者或组长/管理员可以移除
  const currentUserId = authStore.user?.id
  if (!currentUserId) return false

  if (lesson.sharer_id === currentUserId) return true
  if (props.userRole === 'owner' || props.userRole === 'admin') return true

  return false
}

async function handleUnshare(lesson: SharedLesson) {
  if (!confirm('确定要移除此共享教学设计吗？')) {
    return
  }

  try {
    await unshareLesson(props.groupId, lesson.lesson_id)
    loadLessons()
  } catch (error) {
    console.error('移除共享教学设计失败:', error)
    alert('移除失败，请重试')
  }
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

// 生命周期
onMounted(() => {
  loadLessons()
})
</script>

