<template>
  <div
    v-if="isOpen && asset"
    class="fixed inset-0 z-50 overflow-y-auto"
    @click.self="handleClose"
  >
    <div class="fixed inset-0 bg-gray-500 bg-opacity-75" @click="handleClose"></div>

    <div class="flex min-h-full items-center justify-center p-4">
      <div class="relative bg-white rounded-lg shadow-xl max-w-2xl w-full">
        <!-- 头部 -->
        <div class="px-6 pt-6 pb-4 border-b">
          <div class="flex items-center justify-between">
            <h3 class="text-xl font-semibold text-gray-900">资源详情</h3>
            <button @click="handleClose" class="text-gray-400 hover:text-gray-500">
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 内容 -->
        <div class="px-6 py-4 space-y-4">
          <!-- 预览 -->
          <div v-if="asset.thumbnail_url" class="aspect-video bg-gray-100 rounded-lg overflow-hidden">
            <img :src="asset.thumbnail_url" :alt="asset.title" class="w-full h-full object-cover" />
          </div>

          <!-- 基本信息 -->
          <div>
            <h4 class="text-lg font-medium text-gray-900">{{ asset.title }}</h4>
            <p v-if="asset.description" class="mt-2 text-gray-600">{{ asset.description }}</p>
          </div>

          <!-- 元数据 -->
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="text-gray-500">类型：</span>
              <span class="text-gray-900">{{ getAssetTypeName(asset.asset_type) }}</span>
            </div>
            <div v-if="asset.size_bytes">
              <span class="text-gray-500">大小：</span>
              <span class="text-gray-900">{{ formatSize(asset.size_bytes) }}</span>
            </div>
            <div v-if="asset.subject_id && subjectName">
              <span class="text-gray-500">学科：</span>
              <span class="text-gray-900">{{ subjectName }}</span>
            </div>
            <div v-if="asset.grade_id !== undefined && asset.grade_id !== null && gradeName">
              <span class="text-gray-500">年级：</span>
              <span class="text-gray-900">{{ gradeName }}</span>
            </div>
            <div v-else-if="asset.grade_id === null || asset.grade_id === undefined">
              <span class="text-gray-500">年级：</span>
              <span class="text-gray-900">跨年级通用</span>
            </div>
            <div v-if="asset.page_count">
              <span class="text-gray-500">页数：</span>
              <span class="text-gray-900">{{ asset.page_count }} 页</span>
            </div>
            <div>
              <span class="text-gray-500">可见性：</span>
              <span class="text-gray-900">{{ getVisibilityName(asset.visibility) }}</span>
            </div>
            <div>
              <span class="text-gray-500">创建时间：</span>
              <span class="text-gray-900">{{ formatDateTime(asset.created_at) }}</span>
            </div>
            <div>
              <span class="text-gray-500">更新时间：</span>
              <span class="text-gray-900">{{ formatDateTime(asset.updated_at) }}</span>
            </div>
          </div>

          <!-- 操作 -->
          <div class="flex gap-3 pt-4 border-t">
            <button
              @click="handleEdit"
              class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              编辑
            </button>
            <button
              @click="handleDelete"
              class="px-4 py-2 border border-red-600 text-red-600 rounded-lg hover:bg-red-50"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { libraryService } from '@/services/library'
import { curriculumService } from '@/services/curriculum'
import type { LibraryAssetDetail } from '@/types/library'
import type { Subject, Grade } from '@/types/curriculum'
import { getAssetTypeName, getVisibilityName, formatFileSize } from '@/types/library'

interface Props {
  isOpen: boolean
  assetId: number | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  updated: []
  deleted: []
}>()

const asset = ref<LibraryAssetDetail | null>(null)
const loading = ref(false)
const subjects = ref<Subject[]>([])
const grades = ref<Grade[]>([])

// 获取学科名称
const subjectName = computed(() => {
  if (!asset.value?.subject_id) return null
  const subject = subjects.value.find(s => s.id === asset.value?.subject_id)
  return subject?.name || null
})

// 获取年级名称
const gradeName = computed(() => {
  if (asset.value?.grade_id === undefined || asset.value?.grade_id === null) return null
  const grade = grades.value.find(g => g.id === asset.value?.grade_id)
  return grade?.name || null
})

// 加载学科列表
const loadSubjects = async () => {
  try {
    subjects.value = await curriculumService.getSubjects()
  } catch (error) {
    console.error('Failed to load subjects:', error)
  }
}

// 加载年级列表
const loadGrades = async () => {
  try {
    grades.value = await curriculumService.getGrades()
  } catch (error) {
    console.error('Failed to load grades:', error)
  }
}

watch(() => props.assetId, async (newId) => {
  if (newId && props.isOpen) {
    loading.value = true
    try {
      asset.value = await libraryService.getAsset(newId)
    } catch (error) {
      console.error('Failed to load asset:', error)
    } finally {
      loading.value = false
    }
  }
}, { immediate: true })

watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    if (subjects.value.length === 0) {
      loadSubjects()
    }
    if (grades.value.length === 0) {
      loadGrades()
    }
  }
}, { immediate: true })

const handleClose = () => {
  emit('close')
}

const formatSize = (bytes: number) => formatFileSize(bytes)

const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const handleEdit = () => {
  // TODO: 实现编辑功能
  alert('编辑功能待实现')
}

const handleDelete = async () => {
  if (!asset.value) return
  
  if (!confirm(`确定要删除资源"${asset.value.title}"吗？`)) {
    return
  }

  try {
    await libraryService.deleteAsset(asset.value.id)
    emit('deleted')
  } catch (error: any) {
    console.error('Delete failed:', error)
    alert(error.response?.data?.detail || '删除失败')
  }
}
</script>
