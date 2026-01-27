<template>
  <div class="space-y-6">
    <!-- 操作栏 -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex justify-between items-center">
        <div class="flex gap-4">
          <button
            @click="openCreateRegionModal"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            + 创建区域
          </button>
          <button
            @click="loadRegions"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            🔄 刷新
          </button>
        </div>
        <div class="flex gap-2">
          <select v-model="regionLevelFilter" @change="loadRegions" class="px-3 py-2 border rounded-lg">
            <option value="">所有级别</option>
            <option value="1">省级</option>
            <option value="2">市级</option>
            <option value="3">区级</option>
          </select>
          <input
            v-model="regionSearchQuery"
            @input="searchRegions"
            type="text"
            placeholder="搜索区域..."
            class="px-3 py-2 border rounded-lg w-64"
          />
        </div>
      </div>
    </div>

    <!-- 区域列表 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">区域名称</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">编码</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">级别</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">创建时间</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="region in regions" :key="region.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm font-medium text-gray-900">{{ region.name }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ region.code }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="px-2 py-1 text-xs font-semibold rounded-full"
                    :class="getRegionLevelClass(region.level)">
                {{ getRegionLevelName(region.level) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="px-2 py-1 text-xs font-semibold rounded-full"
                    :class="region.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                {{ region.is_active ? '激活' : '未激活' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(region.created_at) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <div class="flex gap-2">
                <button @click="editRegion(region)" class="text-blue-600 hover:text-blue-900">
                  编辑
                </button>
                <button @click="deleteRegion(region)" class="text-red-600 hover:text-red-900">
                  删除
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="flex justify-between items-center">
      <div class="text-sm text-gray-700">
        显示 {{ (regionPage - 1) * regionPageSize + 1 }} - {{ Math.min(regionPage * regionPageSize, regionTotal) }} 条，共 {{ regionTotal }} 条
      </div>
      <div class="flex gap-2">
        <button
          @click="prevRegionPage"
          :disabled="regionPage === 1"
          class="px-3 py-2 border rounded-lg disabled:opacity-50"
        >
          上一页
        </button>
        <span class="px-3 py-2">{{ regionPage }} / {{ regionTotalPages }}</span>
        <button
          @click="nextRegionPage"
          :disabled="regionPage === regionTotalPages"
          class="px-3 py-2 border rounded-lg disabled:opacity-50"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 添加/编辑区域对话框 -->
    <el-dialog
      v-model="showRegionModal"
      :title="editingRegion ? '编辑区域' : '创建区域'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="regionForm" label-width="120px">
        <el-form-item label="区域名称*" required>
          <el-input v-model="regionForm.name" placeholder="请输入区域名称" />
        </el-form-item>
        <el-form-item label="区域编码*">
          <el-input v-model="regionForm.code" placeholder="请输入区域编码" />
        </el-form-item>
        <el-form-item label="级别*" required>
          <el-select v-model="regionForm.level" placeholder="请选择级别" class="w-full">
            <el-option label="省级" :value="1" />
            <el-option label="市级" :value="2" />
            <el-option label="区级" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="regionForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入区域描述"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="regionForm.is_active"
            active-text="激活"
            inactive-text="停用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeRegionModal">取消</el-button>
        <el-button type="primary" @click="saveRegion">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import adminService, { type Region } from '@/services/admin'

const toast = useToast()

// 状态
const regions = ref<Region[]>([])
const regionPage = ref(1)
const regionPageSize = ref(10)
const regionTotal = ref(0)
const regionLevelFilter = ref('')
const regionSearchQuery = ref('')
const showRegionModal = ref(false)
const editingRegion = ref<Region | null>(null)
const regionForm = ref({
  name: '',
  code: '',
  level: 1,
  description: '',
  is_active: true
})

// 计算属性
const regionTotalPages = computed(() => Math.ceil(regionTotal.value / regionPageSize.value))

// 方法
function getRegionLevelName(level: number): string {
  const levelMap = { 1: '省级', 2: '市级', 3: '区级' }
  return levelMap[level] || '未知'
}

function getRegionLevelClass(level: number): string {
  const classMap = {
    1: 'bg-red-100 text-red-800',
    2: 'bg-blue-100 text-blue-800',
    3: 'bg-green-100 text-green-800'
  }
  return classMap[level] || 'bg-gray-100 text-gray-800'
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

async function loadRegions() {
  try {
    const response = await adminService.getRegions({
      page: regionPage.value,
      size: regionPageSize.value,
      level: regionLevelFilter.value ? parseInt(regionLevelFilter.value) : undefined,
      search: regionSearchQuery.value || undefined
    })
    regions.value = response.regions
    regionTotal.value = response.total
  } catch (error: any) {
    console.error('Failed to load regions:', error)
    toast.error(error.response?.data?.detail || '加载区域列表失败')
  }
}

function searchRegions() {
  regionPage.value = 1
  loadRegions()
}

function openCreateRegionModal() {
  editingRegion.value = null
  regionForm.value = {
    name: '',
    code: '',
    level: 1,
    description: '',
    is_active: true
  }
  showRegionModal.value = true
}

function editRegion(region: Region) {
  editingRegion.value = region
  regionForm.value = {
    name: region.name,
    code: region.code,
    level: region.level,
    description: region.description || '',
    is_active: region.is_active
  }
  showRegionModal.value = true
}

function closeRegionModal() {
  showRegionModal.value = false
  editingRegion.value = null
}

async function saveRegion() {
  try {
    if (editingRegion.value) {
      await adminService.updateRegion(editingRegion.value.id, regionForm.value)
      toast.success('区域更新成功')
    } else {
      await adminService.createRegion(regionForm.value)
      toast.success('区域创建成功')
    }
    closeRegionModal()
    loadRegions()
  } catch (error: any) {
    console.error('Failed to save region:', error)
    toast.error(error.response?.data?.detail || '保存区域失败')
  }
}

async function deleteRegion(region: Region) {
  if (!confirm(`确定要删除区域 ${region.name} 吗？`)) {
    return
  }

  try {
    await adminService.deleteRegion(region.id)
    toast.success('区域删除成功')
    loadRegions()
  } catch (error: any) {
    console.error('Failed to delete region:', error)
    toast.error(error.response?.data?.detail || '删除区域失败')
  }
}

function prevRegionPage() {
  if (regionPage.value > 1) {
    regionPage.value--
    loadRegions()
  }
}

function nextRegionPage() {
  if (regionPage.value < regionTotalPages.value) {
    regionPage.value++
    loadRegions()
  }
}

// 生命周期
onMounted(() => {
  loadRegions()
})

// 暴露方法给父组件
defineExpose({
  loadRegions
})
</script>
