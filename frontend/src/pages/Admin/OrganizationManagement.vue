<template>
  <div class="organization-management p-6">
    <!-- 面包屑导航 -->
    <div class="mb-4">
      <router-link 
        to="/admin" 
        class="text-blue-600 hover:text-blue-800 flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        返回管理员首页
      </router-link>
    </div>
    
    <div class="header mb-6">
      <h1 class="text-3xl font-bold text-gray-900">组织架构管理</h1>
      <p class="text-gray-600 mt-2">管理区域和学校信息</p>
    </div>

    <!-- 标签页切换 -->
    <div class="bg-white rounded-lg shadow mb-6">
      <div class="border-b border-gray-200">
        <nav class="flex -mb-px">
          <button
            @click="activeTab = 'regions'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2',
              activeTab === 'regions'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            区域管理
          </button>
          <button
            @click="activeTab = 'schools'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2',
              activeTab === 'schools'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            学校管理
          </button>
        </nav>
      </div>
    </div>

    <!-- 区域管理 -->
    <div v-if="activeTab === 'regions'" class="space-y-6">
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
    </div>

    <!-- 学校管理 -->
    <div v-if="activeTab === 'schools'" class="space-y-6">
      <!-- 操作栏 -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex justify-between items-center">
          <div class="flex gap-4">
            <button
              @click="openCreateSchoolModal"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              + 创建学校
            </button>
            <button
              @click="loadSchools"
              class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              🔄 刷新
            </button>
          </div>
          <div class="flex gap-2">
            <select v-model="schoolTypeFilter" @change="loadSchools" class="px-3 py-2 border rounded-lg">
              <option value="">所有类型</option>
              <option value="小学">小学</option>
              <option value="初中">初中</option>
              <option value="高中">高中</option>
              <option value="大学">大学</option>
            </select>
            <input
              v-model="schoolSearchQuery"
              @input="searchSchools"
              type="text"
              placeholder="搜索学校..."
              class="px-3 py-2 border rounded-lg w-64"
            />
          </div>
        </div>
      </div>

      <!-- 学校列表 -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">学校名称</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">编码</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">类型</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">校长</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="school in schools" :key="school.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ school.name }}</div>
                <div class="text-sm text-gray-500">{{ school.address }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ school.code }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800">
                  {{ school.school_type }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ school.principal || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-semibold rounded-full"
                      :class="school.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                  {{ school.is_active ? '激活' : '未激活' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex gap-2">
                  <button @click="editSchool(school)" class="text-blue-600 hover:text-blue-900">
                    编辑
                  </button>
                  <button @click="deleteSchool(school)" class="text-red-600 hover:text-red-900">
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
          显示 {{ (schoolPage - 1) * schoolPageSize + 1 }} - {{ Math.min(schoolPage * schoolPageSize, schoolTotal) }} 条，共 {{ schoolTotal }} 条
        </div>
        <div class="flex gap-2">
          <button
            @click="prevSchoolPage"
            :disabled="schoolPage === 1"
            class="px-3 py-2 border rounded-lg disabled:opacity-50"
          >
            上一页
          </button>
          <span class="px-3 py-2">{{ schoolPage }} / {{ schoolTotalPages }}</span>
          <button
            @click="nextSchoolPage"
            :disabled="schoolPage === schoolTotalPages"
            class="px-3 py-2 border rounded-lg disabled:opacity-50"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 区域编辑模态框 -->
    <div v-if="showRegionModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold mb-4">
          {{ editingRegion ? '编辑区域' : '创建区域' }}
        </h3>
        <form @submit.prevent="saveRegion">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">区域名称</label>
              <input
                v-model="regionForm.name"
                type="text"
                required
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">区域编码</label>
              <input
                v-model="regionForm.code"
                type="text"
                required
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">级别</label>
              <select v-model="regionForm.level" class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2">
                <option :value="1">省级</option>
                <option :value="2">市级</option>
                <option :value="3">区级</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">描述</label>
              <textarea
                v-model="regionForm.description"
                rows="3"
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              ></textarea>
            </div>
            <div>
              <label class="flex items-center">
                <input v-model="regionForm.is_active" type="checkbox" class="mr-2" />
                <span class="text-sm text-gray-700">激活状态</span>
              </label>
            </div>
          </div>
          <div class="mt-6 flex justify-end gap-3">
            <button
              type="button"
              @click="closeRegionModal"
              class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              取消
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              {{ editingRegion ? '更新' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 学校编辑模态框 -->
    <div v-if="showSchoolModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h3 class="text-lg font-semibold mb-4">
          {{ editingSchool ? '编辑学校' : '创建学校' }}
        </h3>
        <form @submit.prevent="saveSchool">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">学校名称</label>
              <input
                v-model="schoolForm.name"
                type="text"
                required
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">学校编码</label>
              <input
                v-model="schoolForm.code"
                type="text"
                required
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">学校类型</label>
              <select v-model="schoolForm.school_type" class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="小学">小学</option>
                <option value="初中">初中</option>
                <option value="高中">高中</option>
                <option value="大学">大学</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">所属区域</label>
              <select v-model="schoolForm.region_id" required class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="">请选择区域</option>
                <option v-for="region in allRegions" :key="region.id" :value="region.id">
                  {{ region.name }}
                </option>
              </select>
            </div>
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700">学校地址</label>
              <input
                v-model="schoolForm.address"
                type="text"
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">联系电话</label>
              <input
                v-model="schoolForm.phone"
                type="text"
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">邮箱</label>
              <input
                v-model="schoolForm.email"
                type="email"
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">校长姓名</label>
              <input
                v-model="schoolForm.principal"
                type="text"
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="flex items-center mt-6">
                <input v-model="schoolForm.is_active" type="checkbox" class="mr-2" />
                <span class="text-sm text-gray-700">激活状态</span>
              </label>
            </div>
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700">描述</label>
              <textarea
                v-model="schoolForm.description"
                rows="3"
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              ></textarea>
            </div>
          </div>
          <div class="mt-6 flex justify-end gap-3">
            <button
              type="button"
              @click="closeSchoolModal"
              class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              取消
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              {{ editingSchool ? '更新' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import adminService, { type Region, type School } from '@/services/admin'

const toast = useToast()

// 标签页状态
const activeTab = ref<'regions' | 'schools'>('regions')

// 区域管理状态
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

// 学校管理状态
const schools = ref<School[]>([])
const schoolPage = ref(1)
const schoolPageSize = ref(10)
const schoolTotal = ref(0)
const schoolTypeFilter = ref('')
const schoolSearchQuery = ref('')
const showSchoolModal = ref(false)
const editingSchool = ref<School | null>(null)
const allRegions = ref<Region[]>([])
const schoolForm = ref({
  name: '',
  code: '',
  region_id: '',
  school_type: '小学',
  address: '',
  phone: '',
  email: '',
  principal: '',
  description: '',
  is_active: true
})

// 计算属性
const regionTotalPages = computed(() => Math.ceil(regionTotal.value / regionPageSize.value))
const schoolTotalPages = computed(() => Math.ceil(schoolTotal.value / schoolPageSize.value))

// 区域管理方法
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

async function loadAllRegions() {
  try {
    const response = await adminService.getRegions({ size: 100 })
    allRegions.value = response.regions
  } catch (error: any) {
    console.error('Failed to load all regions:', error)
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

// 学校管理方法
async function loadSchools() {
  try {
    const response = await adminService.getSchools({
      page: schoolPage.value,
      size: schoolPageSize.value,
      school_type: schoolTypeFilter.value || undefined,
      search: schoolSearchQuery.value || undefined
    })
    schools.value = response.schools
    schoolTotal.value = response.total
  } catch (error: any) {
    console.error('Failed to load schools:', error)
    toast.error(error.response?.data?.detail || '加载学校列表失败')
  }
}

function searchSchools() {
  schoolPage.value = 1
  loadSchools()
}

async function openCreateSchoolModal() {
  editingSchool.value = null
  schoolForm.value = {
    name: '',
    code: '',
    region_id: '',
    school_type: '小学',
    address: '',
    phone: '',
    email: '',
    principal: '',
    description: '',
    is_active: true
  }
  // 加载所有区域供选择
  await loadAllRegions()
  showSchoolModal.value = true
}

async function editSchool(school: School) {
  editingSchool.value = school
  schoolForm.value = {
    name: school.name,
    code: school.code,
    region_id: school.region_id.toString(),
    school_type: school.school_type,
    address: school.address || '',
    phone: school.phone || '',
    email: school.email || '',
    principal: school.principal || '',
    description: school.description || '',
    is_active: school.is_active
  }
  // 加载所有区域供选择
  await loadAllRegions()
  showSchoolModal.value = true
}

function closeSchoolModal() {
  showSchoolModal.value = false
  editingSchool.value = null
}

async function saveSchool() {
  try {
    const formData = {
      ...schoolForm.value,
      region_id: parseInt(schoolForm.value.region_id)
    }
    
    if (editingSchool.value) {
      await adminService.updateSchool(editingSchool.value.id, formData)
      toast.success('学校更新成功')
    } else {
      await adminService.createSchool(formData)
      toast.success('学校创建成功')
    }
    closeSchoolModal()
    loadSchools()
  } catch (error: any) {
    console.error('Failed to save school:', error)
    toast.error(error.response?.data?.detail || '保存学校失败')
  }
}

async function deleteSchool(school: School) {
  if (!confirm(`确定要删除学校 ${school.name} 吗？`)) {
    return
  }
  
  try {
    await adminService.deleteSchool(school.id)
    toast.success('学校删除成功')
    loadSchools()
  } catch (error: any) {
    console.error('Failed to delete school:', error)
    toast.error(error.response?.data?.detail || '删除学校失败')
  }
}

function prevSchoolPage() {
  if (schoolPage.value > 1) {
    schoolPage.value--
    loadSchools()
  }
}

function nextSchoolPage() {
  if (schoolPage.value < schoolTotalPages.value) {
    schoolPage.value++
    loadSchools()
  }
}

onMounted(() => {
  loadRegions()
  loadSchools()
  loadAllRegions()
})
</script>

