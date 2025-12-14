<template>
  <div class="resource-library-page h-full flex flex-col">
    <!-- 页头 -->
    <div class="px-6 pt-6 pb-4 border-b bg-white">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">资源库</h1>
          <p class="mt-2 text-gray-600">管理和分享学校的教学资源</p>
        </div>
        <!-- 上传按钮 -->
        <button
          @click="showUploadModal = true"
          class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          上传资源
        </button>
      </div>

      <!-- 操作栏 -->
      <div class="mt-4 flex items-center gap-4">
        <!-- 搜索 -->
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索资源..."
          class="w-64 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white text-gray-900 placeholder:text-gray-400 focus:border-purple-500"
          @input="debouncedSearch"
        />
        
        <!-- 快速筛选（可选，与树形目录配合使用） -->
        <select
          v-model="filterVisibility"
          class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white text-gray-900 focus:border-purple-500"
          @change="loadAssets"
        >
          <option value="">全部可见性</option>
          <option value="teacher_only">仅自己</option>
          <option value="school">全校可见</option>
        </select>
      </div>
    </div>

    <!-- 双栏布局 -->
    <div class="flex-1 flex overflow-hidden">
      <!-- 左侧：树形目录 -->
      <ResourceDirectoryTree
        :subjects="subjects"
        :grades="grades"
        :selected-filter="currentFilter"
        @select="handleTreeSelect"
        class="flex-shrink-0"
      />

      <!-- 右侧：内容列表 -->
      <div class="flex-1 overflow-y-auto p-6">

        <!-- 加载状态 -->
        <div v-if="loading" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent"></div>
          <p class="mt-4 text-gray-600">加载中...</p>
        </div>

        <!-- 错误提示 -->
        <div v-else-if="error" class="text-center py-12">
          <p class="text-red-600 mb-4">{{ error }}</p>
          <button
            @click="loadAssets"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            重试
          </button>
        </div>

        <!-- 资产列表 -->
        <div v-else-if="assets.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div
        v-for="asset in assets"
        :key="asset.id"
        class="bg-white rounded-lg border border-gray-200 hover:border-purple-300 transition-all cursor-pointer overflow-hidden"
        @click="viewAsset(asset)"
      >
        <!-- 缩略图 -->
        <div class="aspect-video bg-gray-100 flex items-center justify-center">
          <img
            v-if="asset.thumbnail_url"
            :src="asset.thumbnail_url"
            :alt="asset.title"
            class="w-full h-full object-cover"
          />
          <span v-else class="text-6xl">{{ getAssetIcon(asset.asset_type) }}</span>
        </div>

        <!-- 信息 -->
        <div class="p-4">
          <h3 class="font-medium text-gray-900 truncate mb-2">{{ asset.title }}</h3>
          <div class="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <span>{{ getAssetTypeName(asset.asset_type) }}</span>
            <span v-if="asset.size_bytes">• {{ formatSize(asset.size_bytes) }}</span>
          </div>
          <div class="flex items-center justify-between text-xs text-gray-400">
            <span>{{ formatDate(asset.updated_at) }}</span>
            <span :class="[
              'px-2 py-1 rounded',
              asset.visibility === 'school' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
            ]">
              {{ getVisibilityName(asset.visibility) }}
            </span>
          </div>
        </div>
      </div>
    </div>

        <!-- 空状态 -->
        <div v-else class="text-center py-12">
          <svg class="mx-auto h-24 w-24 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <p class="mt-4 text-xl text-gray-600">暂无资源</p>
          <p class="mt-2 text-gray-500">点击上方按钮上传第一个资源</p>
        </div>

        <!-- 分页 -->
        <div v-if="totalPages > 1" class="mt-6 flex items-center justify-center gap-4">
      <button
        :disabled="currentPage === 1"
        @click="changePage(currentPage - 1)"
        class="px-4 py-2 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        上一页
      </button>
      <span class="text-gray-600">
        第 {{ currentPage }} / {{ totalPages }} 页 (共 {{ total }} 项)
      </span>
      <button
        :disabled="currentPage === totalPages"
        @click="changePage(currentPage + 1)"
        class="px-4 py-2 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        下一页
        </button>
      </div>
      </div>
    </div>

    <!-- 上传模态框 -->
    <UploadAssetModal
      :is-open="showUploadModal"
      @close="showUploadModal = false"
      @success="handleUploadSuccess"
    />

    <!-- 详情模态框 -->
    <AssetDetailModal
      :is-open="showDetailModal"
      :asset-id="selectedAssetId"
      @close="showDetailModal = false"
      @updated="loadAssets"
      @deleted="handleAssetDeleted"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { libraryService } from '@/services/library'
import { curriculumService } from '@/services/curriculum'
import type { LibraryAssetSummary, ResourceFilter } from '@/types/library'
import type { Subject, Grade } from '@/types/curriculum'
import { getAssetTypeIcon, getAssetTypeName, getVisibilityName, formatFileSize } from '@/types/library'
import UploadAssetModal from '@/components/Library/UploadAssetModal.vue'
import AssetDetailModal from '@/components/Library/AssetDetailModal.vue'
import ResourceDirectoryTree from '@/components/Library/ResourceDirectoryTree.vue'

const loading = ref(false)
const error = ref<string | null>(null)
const assets = ref<LibraryAssetSummary[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const searchQuery = ref('')
const filterVisibility = ref('')
const subjects = ref<Subject[]>([])
const grades = ref<Grade[]>([])
const currentFilter = ref<ResourceFilter>({})

const showUploadModal = ref(false)
const showDetailModal = ref(false)
const selectedAssetId = ref<number | null>(null)

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

// 加载资产列表
const loadAssets = async () => {
  loading.value = true
  error.value = null

  try {
    const params: any = {
      query: searchQuery.value || undefined,
      visibility: filterVisibility.value || undefined,
      page: currentPage.value,
      page_size: pageSize.value,
    }

    // 从树形目录筛选条件中获取
    if (currentFilter.value.subject_id !== undefined) {
      params.subject_id = currentFilter.value.subject_id
    }
    // grade_id 为 null 时表示只显示通用资源，需要在前端过滤
    // grade_id 为 undefined 时表示不限制年级
    if (currentFilter.value.grade_id !== undefined && currentFilter.value.grade_id !== null) {
      params.grade_id = currentFilter.value.grade_id
    }
    if (currentFilter.value.asset_type) {
      params.asset_type = currentFilter.value.asset_type
    }
    if (currentFilter.value.visibility) {
      params.visibility = currentFilter.value.visibility
    }

    const response = await libraryService.listAssets(params)

    // 如果选择了"跨年级通用"（grade_id === null），在前端过滤
    let filteredItems = response.items
    if (currentFilter.value.grade_id === null) {
      filteredItems = response.items.filter(item => item.grade_id === null || item.grade_id === undefined)
      // 注意：total 可能不准确，因为这是前端过滤后的结果
      // 理想情况下后端应该支持 grade_id IS NULL 查询
    }

    assets.value = filteredItems
    total.value = currentFilter.value.grade_id === null ? filteredItems.length : response.total
  } catch (err: any) {
    console.error('Failed to load assets:', err)
    if (err.response?.status === 403) {
      error.value = '您没有权限访问资源库'
    } else {
      error.value = err.response?.data?.detail || '加载资源失败'
    }
  } finally {
    loading.value = false
  }
}

// 处理树形目录选择
const handleTreeSelect = (filter: ResourceFilter) => {
  currentFilter.value = filter
  currentPage.value = 1
  loadAssets()
}

// 防抖搜索
let searchTimeout: number | null = null
const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = window.setTimeout(() => {
    currentPage.value = 1
    loadAssets()
  }, 500)
}

// 切换页码
const changePage = (page: number) => {
  currentPage.value = page
  loadAssets()
}

// 查看资产
const viewAsset = (asset: LibraryAssetSummary) => {
  selectedAssetId.value = asset.id
  showDetailModal.value = true
}

// 上传成功
const handleUploadSuccess = () => {
  showUploadModal.value = false
  loadAssets()
}

// 资产删除
const handleAssetDeleted = () => {
  showDetailModal.value = false
  loadAssets()
}

// 格式化大小
const formatSize = (bytes: number) => formatFileSize(bytes)

// 获取图标
const getAssetIcon = (type: string) => getAssetTypeIcon(type as any)

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

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

onMounted(() => {
  loadSubjects()
  loadGrades()
  loadAssets()
})
</script>

<style scoped>
.resource-library-page {
  height: calc(100vh - 4rem);
}
</style>
