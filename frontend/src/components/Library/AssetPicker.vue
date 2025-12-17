<template>
  <div class="asset-picker">
    <!-- 搜索与筛选 -->
    <div class="search-filters mb-4">
      <div class="flex gap-2 mb-2">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索资源标题..."
          class="flex-1 px-3 py-2 border rounded-lg bg-white text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
          @input="debouncedSearch"
        />
        <select
          v-model="filterType"
          class="px-3 py-2 border rounded-lg bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-purple-500"
          @change="loadAssets"
        >
          <option value="">全部类型</option>
          <option value="pdf">PDF 文档</option>
          <option value="video">视频</option>
          <option value="image">图片</option>
          <option value="audio">音频</option>
          <option value="document">文档</option>
          <option value="interactive">交互式课件</option>
          <option value="other">其他</option>
        </select>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-purple-500 border-t-transparent"></div>
      <p class="mt-2 text-gray-600">加载中...</p>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="text-center py-8">
      <p class="text-red-600">{{ error }}</p>
      <button
        @click="loadAssets"
        class="mt-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
      >
        重试
      </button>
    </div>

    <!-- 资产列表 -->
    <div v-else-if="assets.length > 0" class="assets-list">
      <div class="grid grid-cols-1 gap-2 max-h-96 overflow-y-auto">
        <div
          v-for="asset in assets"
          :key="asset.id"
          :class="[
            'asset-item p-3 border rounded-lg cursor-pointer transition-all',
            selectedAssetId === asset.id
              ? 'border-purple-500 bg-purple-50'
              : 'border-gray-200 hover:border-purple-300 hover:bg-gray-50'
          ]"
          @click="selectAsset(asset)"
        >
          <div class="flex items-start gap-3">
            <!-- 缩略图/图标 -->
            <div class="flex-shrink-0 w-16 h-16 bg-gray-100 rounded flex items-center justify-center">
              <img
                v-if="asset.thumbnail_url"
                :src="asset.thumbnail_url"
                :alt="asset.title"
                class="w-full h-full object-cover rounded"
              />
              <span v-else class="text-3xl">{{ getAssetIcon(asset.asset_type) }}</span>
            </div>

            <!-- 资产信息 -->
            <div class="flex-1 min-w-0">
              <h4 class="font-medium text-gray-900 truncate">{{ asset.title }}</h4>
              <div class="flex items-center gap-2 mt-1 text-sm text-gray-500">
                <span>{{ getAssetTypeName(asset.asset_type) }}</span>
                <span v-if="asset.size_bytes">• {{ formatSize(asset.size_bytes) }}</span>
                <span v-if="asset.page_count">• {{ asset.page_count }} 页</span>
              </div>
              <div class="mt-1 text-xs text-gray-400">
                更新于 {{ formatDate(asset.updated_at) }}
              </div>
            </div>

            <!-- 选中标记 -->
            <div v-if="selectedAssetId === asset.id" class="flex-shrink-0">
              <svg class="w-6 h-6 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clip-rule="evenodd"
                />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="flex items-center justify-between mt-4 pt-4 border-t">
        <button
          :disabled="currentPage === 1"
          @click="changePage(currentPage - 1)"
          class="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          上一页
        </button>
        <span class="text-sm text-gray-600">
          第 {{ currentPage }} / {{ totalPages }} 页 (共 {{ total }} 项)
        </span>
        <button
          :disabled="currentPage === totalPages"
          @click="changePage(currentPage + 1)"
          class="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="text-center py-8">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        />
      </svg>
      <p class="mt-2 text-gray-600">暂无资源</p>
      <p class="text-sm text-gray-500">请先上传资源到资源库</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { libraryService } from '@/services/library'
import type { LibraryAssetSummary } from '@/types/library'
import { getAssetTypeIcon, getAssetTypeName, formatFileSize } from '@/types/library'

interface Props {
  filterType?: string  // 可选的默认类型筛选
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'select', asset: LibraryAssetSummary | null): void
}>()

const loading = ref(false)
const error = ref<string | null>(null)
const assets = ref<LibraryAssetSummary[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const searchQuery = ref('')
const filterType = ref(props.filterType || '')
const selectedAssetId = ref<number | null>(null)

// 如果 props.filterType 存在，初始化时应用筛选
if (props.filterType) {
  filterType.value = props.filterType
}

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

// 加载资产列表
const loadAssets = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await libraryService.listAssets({
      query: searchQuery.value || undefined,
      asset_type: filterType.value || undefined,
      page: currentPage.value,
      page_size: pageSize.value,
    })

    assets.value = response.items
    total.value = response.total
  } catch (err: any) {
    console.error('Failed to load assets:', err)
    error.value = err.response?.data?.detail || '加载资源失败'
  } finally {
    loading.value = false
  }
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

// 选择资产
const selectAsset = (asset: LibraryAssetSummary) => {
  if (selectedAssetId.value === asset.id) {
    // 取消选择
    selectedAssetId.value = null
    emit('select', null)
  } else {
    // 选中
    selectedAssetId.value = asset.id
    emit('select', asset)
  }
}

// 切换页码
const changePage = (page: number) => {
  currentPage.value = page
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

// 监听 props.filterType 变化
watch(() => props.filterType, (newType) => {
  if (newType) {
    filterType.value = newType
    currentPage.value = 1
    loadAssets()
  }
}, { immediate: true })

onMounted(() => {
  loadAssets()
})

// 暴露刷新方法
defineExpose({
  refresh: loadAssets,
})
</script>

<style scoped>
.asset-picker {
  @apply w-full;
}

.asset-item {
  @apply transition-all duration-200;
}
</style>
