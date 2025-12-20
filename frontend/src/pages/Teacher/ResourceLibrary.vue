<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50/30 to-teal-50/50">
    <!-- 统一头部 -->
    <DashboardHeader
      title="资源库"
      subtitle="管理和分享学校的教学资源"
      :user-name="userName"
      :region-name="regionName"
      :school-name="schoolName"
      :grade-name="gradeName"
      @logout="handleLogout"
    >
      <template #default>
        <div class="flex items-center gap-3 flex-wrap">
          <button
            @click="handleBack"
            class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-xl hover:bg-white hover:shadow-md transition-all"
            title="返回教师工作台"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            返回工作台
          </button>
          <button
            @click="showUploadModal = true"
            class="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-emerald-500 to-teal-500 rounded-xl hover:from-emerald-600 hover:to-teal-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-all shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 transform hover:scale-105"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            上传资源
          </button>
        </div>
      </template>
    </DashboardHeader>

    <!-- 主内容区 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 操作栏 -->
      <div class="mb-6 flex items-center gap-4">
        <!-- 搜索 -->
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索资源..."
          class="w-64 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white text-gray-900 placeholder:text-gray-400 focus:border-emerald-500"
          @input="debouncedSearch"
        />
        
        <!-- 快速筛选（可选，与树形目录配合使用） -->
        <select
          v-model="filterVisibility"
          class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white text-gray-900 focus:border-emerald-500"
          @change="loadAssets"
        >
          <option value="">全部可见性</option>
          <option value="teacher_only">仅自己</option>
          <option value="school">全校可见</option>
        </select>
      </div>

      <!-- 双栏布局 -->
      <div class="flex gap-6">
        <!-- 左侧：树形目录 -->
        <div class="flex-shrink-0 w-64">
          <ResourceDirectoryTree
            :subjects="subjects"
            :grades="grades"
            :selected-filter="currentFilter"
            @select="handleTreeSelect"
          />
        </div>

        <!-- 右侧：内容列表 -->
        <div class="flex-1">

          <!-- 加载状态 -->
          <div v-if="loading" class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-emerald-500 border-t-transparent"></div>
            <p class="mt-4 text-gray-600">加载中...</p>
          </div>

          <!-- 错误提示 -->
          <div v-else-if="error" class="text-center py-12">
            <p class="text-red-600 mb-4">{{ error }}</p>
            <button
              @click="loadAssets"
              class="px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-lg hover:from-emerald-600 hover:to-teal-600 shadow-lg shadow-emerald-500/30"
            >
              重试
            </button>
          </div>

          <!-- 资产列表 -->
          <div v-else-if="assets.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            <div
              v-for="asset in assets"
              :key="asset.id"
              class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer"
              @click="viewAsset(asset)"
            >
              <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-emerald-500 to-teal-500"></span>
              <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none bg-gradient-to-br from-emerald-50/80 via-transparent to-transparent"></div>

              <!-- 缩略图 -->
              <div class="aspect-video bg-gray-100 flex items-center justify-center relative">
                <img
                  v-if="asset.thumbnail_url"
                  :src="asset.thumbnail_url"
                  :alt="asset.title"
                  class="w-full h-full object-cover"
                />
                <span v-else class="text-6xl">{{ getAssetIcon(asset.asset_type) }}</span>
              </div>

              <!-- 信息 -->
              <div class="p-4 relative">
                <h3 class="font-semibold text-gray-900 truncate mb-2">{{ asset.title }}</h3>
                <div class="flex items-center gap-2 text-sm text-gray-500 mb-2">
                  <span>{{ getAssetTypeName(asset.asset_type) }}</span>
                  <span v-if="asset.size_bytes">• {{ formatSize(asset.size_bytes) }}</span>
                </div>
                <!-- 知识点分类标签 -->
                <div v-if="asset.knowledge_point_category || asset.knowledge_point_name" class="mb-2 flex flex-wrap gap-1">
                  <span
                    v-if="asset.knowledge_point_category"
                    class="px-2 py-0.5 text-xs bg-emerald-100 text-emerald-700 rounded-full"
                  >
                    {{ asset.knowledge_point_category }}
                  </span>
                  <span
                    v-if="asset.knowledge_point_name"
                    class="px-2 py-0.5 text-xs bg-teal-100 text-teal-700 rounded-full"
                  >
                    {{ asset.knowledge_point_name }}
                  </span>
                </div>
                <div class="flex items-center justify-between text-xs text-gray-400">
                  <span>{{ formatDate(asset.updated_at) }}</span>
                  <span :class="[
                    'px-2 py-1 rounded-full',
                    asset.visibility === 'school' ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-700'
                  ]">
                    {{ getVisibilityName(asset.visibility) }}
                  </span>
                </div>
                <!-- 点击次数 -->
                <div class="mt-2 flex items-center gap-1 text-xs text-gray-500">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  <span>{{ asset.view_count || 0 }} 次点击</span>
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
              class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-white/80 backdrop-blur-sm disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              上一页
            </button>
            <span class="text-gray-600">
              第 {{ currentPage }} / {{ totalPages }} 页 (共 {{ total }} 项)
            </span>
            <button
              :disabled="currentPage === totalPages"
              @click="changePage(currentPage + 1)"
              class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-white/80 backdrop-blur-sm disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </main>

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
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { authService } from '@/services/auth'
import { libraryService } from '@/services/library'
import { curriculumService } from '@/services/curriculum'
import type { LibraryAssetSummary, ResourceFilter } from '@/types/library'
import type { Subject, Grade } from '@/types/curriculum'
import { getAssetTypeIcon, getAssetTypeName, getVisibilityName, formatFileSize } from '@/types/library'
import UploadAssetModal from '@/components/Library/UploadAssetModal.vue'
import AssetDetailModal from '@/components/Library/AssetDetailModal.vue'
import ResourceDirectoryTree from '@/components/Library/ResourceDirectoryTree.vue'
import DashboardHeader from '@/components/Common/DashboardHeader.vue'

const router = useRouter()
const userStore = useUserStore()

const userName = computed(() => userStore.user?.full_name || userStore.user?.username || '教师')
const regionName = computed(() => userStore.user?.region_name || '')
const schoolName = computed(() => userStore.user?.school_name || '')
const gradeName = computed(() => userStore.user?.grade_name || '')

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
    if (currentFilter.value.knowledge_point_category) {
      params.knowledge_point_category = currentFilter.value.knowledge_point_category
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
const viewAsset = async (asset: LibraryAssetSummary) => {
  selectedAssetId.value = asset.id
  showDetailModal.value = true
  
  // 记录点击次数（异步执行，不阻塞界面）
  try {
    await libraryService.incrementViewCount(asset.id)
    // 更新本地显示的点击次数
    const assetInList = assets.value.find(a => a.id === asset.id)
    if (assetInList) {
      assetInList.view_count = (assetInList.view_count || 0) + 1
    }
  } catch (error) {
    // 静默失败，不影响用户体验
    console.error('Failed to increment view count:', error)
  }
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

// 返回上一页
const handleBack = () => {
  router.push('/teacher')
}

// 退出登录
const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

onMounted(() => {
  const initialize = async () => {
    if (!userStore.user) {
      try {
        const currentUser = await authService.getCurrentUser()
        userStore.setUser(currentUser)
      } catch (error) {
        console.error('Failed to load current user info:', error)
      }
    }
    loadSubjects()
    loadGrades()
    loadAssets()
  }
  initialize()
})
</script>

<style scoped>
/* 样式已通过 Tailwind 类实现 */
</style>
