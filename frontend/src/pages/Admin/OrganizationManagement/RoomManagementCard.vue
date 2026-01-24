<template>
  <div class="space-y-6">
    <!-- 操作栏 -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex justify-between items-center">
        <div class="flex gap-4">
          <button
            @click="openCreateRoomModal"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            + 创建课室
          </button>
          <button
            @click="openRoomImportDialog"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            📥 批量导入课室
          </button>
          <button
            @click="loadRooms"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            🔄 刷新
          </button>
        </div>
        <div class="flex gap-2">
          <select
            v-model="filters.school_id"
            @change="loadRooms"
            class="px-3 py-2 border rounded-lg"
          >
            <option value="">所有学校</option>
            <option v-for="school in schools" :key="school.id" :value="school.id">
              {{ school.name }}
            </option>
          </select>
          <select
            v-model="filters.room_type"
            @change="loadRooms"
            class="px-3 py-2 border rounded-lg"
          >
            <option value="">所有类型</option>
            <option value="普通教室">普通教室</option>
            <option value="实验室">实验室</option>
            <option value="多媒体教室">多媒体教室</option>
            <option value="计算机教室">计算机教室</option>
            <option value="音乐教室">音乐教室</option>
            <option value="美术教室">美术教室</option>
            <option value="体育馆">体育馆</option>
            <option value="报告厅">报告厅</option>
          </select>
          <input
            v-model="filters.search"
            type="text"
            placeholder="搜索课室名称或编码..."
            class="px-3 py-2 border rounded-lg"
            @keyup.enter="loadRooms"
          />
          <button
            @click="loadRooms"
            class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            搜索
          </button>
        </div>
      </div>
    </div>

    <!-- 课室列表 -->
    <div class="bg-white rounded-lg shadow">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                课室名称
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                编码
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                所属学校
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                楼栋
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                楼层
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                类型
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                容量
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                固定班级
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                状态
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                操作
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="room in rooms" :key="room.id">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ room.id }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ room.name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ room.code || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ getSchoolName(room.school_id) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ room.building || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ room.floor || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ room.room_type }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ room.capacity || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ getClassroomName(room.assigned_classroom_id) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                    room.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  ]"
                >
                  {{ room.is_active ? '激活' : '停用' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  @click="openEditRoomModal(room)"
                  class="text-blue-600 hover:text-blue-900 mr-3"
                >
                  编辑
                </button>
                <button
                  @click="deleteRoom(room.id)"
                  class="text-red-600 hover:text-red-900"
                >
                  删除
                </button>
              </td>
            </tr>
            <tr v-if="rooms.length === 0">
              <td colspan="11" class="px-6 py-4 text-center text-sm text-gray-500">
                暂无课室数据
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div class="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
        <div class="flex items-center justify-between">
          <div class="flex-1 flex justify-between sm:hidden">
            <button
              @click="prevPage"
              :disabled="pagination.page === 1"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              上一页
            </button>
            <button
              @click="nextPage"
              :disabled="pagination.page >= pagination.total_pages"
              class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              下一页
            </button>
          </div>
          <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                显示第
                <span class="font-medium">{{ (pagination.page - 1) * pagination.size + 1 }}</span>
                至
                <span class="font-medium">{{ Math.min(pagination.page * pagination.size, pagination.total) }}</span>
                条，共
                <span class="font-medium">{{ pagination.total }}</span>
                条结果
              </p>
            </div>
            <div>
              <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                <button
                  @click="prevPage"
                  :disabled="pagination.page === 1"
                  class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                >
                  上一页
                </button>
                <button
                  v-for="page in displayedPages"
                  :key="page"
                  @click="goToPage(page)"
                  :class="[
                    'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
                    page === pagination.page
                      ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                      : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                  ]"
                >
                  {{ page }}
                </button>
                <button
                  @click="nextPage"
                  :disabled="pagination.page >= pagination.total_pages"
                  class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                >
                  下一页
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建/编辑课室模态框 -->
    <div
      v-if="showRoomModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full"
      @click.self="showRoomModal = false"
    >
      <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            {{ editingRoom ? '编辑课室' : '创建课室' }}
          </h3>
          <form @submit.prevent="saveRoom" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">课室名称 *</label>
                <input
                  v-model="roomForm.name"
                  type="text"
                  required
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">课室编码</label>
                <input
                  v-model="roomForm.code"
                  type="text"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">所属学校 *</label>
                <select
                  v-model="roomForm.school_id"
                  required
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="">请选择学校</option>
                  <option v-for="school in schools" :key="school.id" :value="school.id">
                    {{ school.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">课室类型 *</label>
                <select
                  v-model="roomForm.room_type"
                  required
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="">请选择类型</option>
                  <option value="普通教室">普通教室</option>
                  <option value="实验室">实验室</option>
                  <option value="多媒体教室">多媒体教室</option>
                  <option value="计算机教室">计算机教室</option>
                  <option value="音乐教室">音乐教室</option>
                  <option value="美术教室">美术教室</option>
                  <option value="体育馆">体育馆</option>
                  <option value="报告厅">报告厅</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">楼栋</label>
                <input
                  v-model="roomForm.building"
                  type="text"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">楼层</label>
                <input
                  v-model.number="roomForm.floor"
                  type="number"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">座位容量</label>
                <input
                  v-model.number="roomForm.capacity"
                  type="number"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">固定分配班级</label>
                <select
                  v-model="roomForm.assigned_classroom_id"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option :value="null">共享课室（不固定）</option>
                  <option v-for="classroom in classrooms" :key="classroom.id" :value="classroom.id">
                    {{ classroom.name }}
                  </option>
                </select>
              </div>
              <div class="col-span-2">
                <label class="block text-sm font-medium text-gray-700">设备清单（用逗号分隔）</label>
                <input
                  v-model="equipmentString"
                  type="text"
                  placeholder="例如: 投影仪,电脑,音响"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div class="col-span-2">
                <label class="block text-sm font-medium text-gray-700">课室描述</label>
                <textarea
                  v-model="roomForm.description"
                  rows="3"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                ></textarea>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">状态</label>
                <select
                  v-model="roomForm.is_active"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option :value="true">激活</option>
                  <option :value="false">停用</option>
                </select>
              </div>
            </div>
            <div class="flex justify-end gap-3 mt-6">
              <button
                type="button"
                @click="showRoomModal = false"
                class="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
              >
                取消
              </button>
              <button
                type="submit"
                class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                {{ editingRoom ? '更新' : '创建' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 批量导入课室对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="批量导入课室"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-steps :active="importStep" finish-status="success" align-center class="mb-6">
        <el-step title="下载模板" />
        <el-step title="上传文件" />
        <el-step title="导入结果" />
      </el-steps>

      <!-- 步骤1: 下载模板 -->
      <div v-if="importStep === 0" class="space-y-4">
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p class="text-sm text-blue-800 mb-2"><strong>导入说明：</strong></p>
          <ul class="text-sm text-blue-700 list-disc list-inside space-y-1">
            <li>请先下载Excel模板，按照模板格式填写课室信息</li>
            <li>必需字段：学校名称、课室名称、课室类型</li>
            <li>可选字段：课室编码、楼栋、楼层、座位容量、设备清单、固定分配班级、课室描述、是否激活</li>
            <li>支持格式：.xlsx, .xls</li>
          </ul>
        </div>
        <div class="bg-gray-50 border rounded-lg p-4">
          <h4 class="text-sm font-medium mb-2">模板字段说明</h4>
          <el-table :data="roomTemplateFields" border size="small" max-height="400">
            <el-table-column prop="field" label="字段名" width="130" />
            <el-table-column prop="required" label="是否必填" width="100" />
            <el-table-column prop="description" label="说明" />
            <el-table-column prop="example" label="示例" width="180" />
          </el-table>
        </div>
        <div class="flex justify-center gap-4">
          <el-button type="primary" @click="downloadRoomTemplate">
            下载Excel模板
          </el-button>
          <el-button @click="importStep = 1">
            已有模板，下一步
          </el-button>
        </div>
      </div>

      <!-- 步骤2: 上传文件 -->
      <div v-if="importStep === 1" class="space-y-4">
        <el-form :model="importForm" label-width="140px">
          <el-form-item label="更新已存在的课室">
            <el-switch
              v-model="updateExisting"
              active-text="是"
              inactive-text="否"
            />
            <span class="ml-2 text-sm text-gray-500">按学校+课室名称匹配</span>
          </el-form-item>
        </el-form>
        <el-upload
          ref="uploadRef"
          class="upload-demo"
          drag
          :auto-upload="false"
          :limit="1"
          :on-change="handleFileChange"
          :on-exceed="handleExceed"
          accept=".xlsx,.xls"
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
          <template #tip>
            <div class="el-upload__tip">只能上传 xlsx/xls 文件，且不超过 10MB</div>
          </template>
        </el-upload>
        <div v-if="selectedFile" class="mt-4 p-3 bg-gray-50 rounded-lg">
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="文件名">{{ selectedFile.name }}</el-descriptions-item>
            <el-descriptions-item label="文件大小">{{ formatFileSize(selectedFile.size) }}</el-descriptions-item>
          </el-descriptions>
        </div>
        <div class="flex justify-center gap-4">
          <el-button @click="importStep = 0">
            上一步
          </el-button>
          <el-button
            type="primary"
            @click="startImport"
            :loading="importing"
            :disabled="!selectedFile"
          >
            <span class="ml-2">开始导入</span>
          </el-button>
        </div>
      </div>

      <!-- 步骤3: 导入结果 -->
      <div v-if="importStep === 2" class="space-y-4">
        <el-alert
          :title="importResult && importResult.failed === 0 ? '✅ 导入完成' : '⚠️ 导入完成'"
          :type="importResult && importResult.failed === 0 ? 'success' : 'warning'"
          :closable="false"
        />
        <div v-if="importResult && importResult.total > 0">
          <h4 class="text-sm font-medium mb-2">📊 导入统计</h4>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="总记录数" :value="importResult.total" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="成功" :value="importResult.success" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="新增" :value="importResult.created" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="更新" :value="importResult.updated" />
            </el-col>
          </el-row>
          <el-row :gutter="20" class="mt-4">
            <el-col :span="6">
              <el-statistic title="失败" :value="importResult.failed" />
            </el-col>
            <el-col :span="6" v-if="importResult.skipped > 0">
              <el-statistic title="跳过" :value="importResult.skipped" />
            </el-col>
          </el-row>
          <div v-if="importResult.errors && importResult.errors.length > 0" class="mt-4">
            <h4 class="text-sm font-medium mb-2">⚠️ 错误详情</h4>
            <el-table :data="importResult.errors" max-height="300" size="small">
              <el-table-column prop="row" label="行号" width="80" />
              <el-table-column prop="field" label="字段" width="120" />
              <el-table-column prop="message" label="错误信息" />
            </el-table>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button v-if="importStep < 2" @click="showImportDialog = false">取消</el-button>
        <el-button v-if="importStep === 2" type="primary" @click="closeImportDialog">完成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import adminService, { type Room, type RoomCreate, type RoomUpdate, type School, type Classroom, type RoomImportResponse } from '@/services/admin'

// 数据
const rooms = ref<Room[]>([])
const schools = ref<School[]>([])
const classrooms = ref<Classroom[]>([])
const editingRoom = ref<Room | null>(null)
const showRoomModal = ref(false)

// 批量导入相关
const showImportDialog = ref(false)
const importStep = ref(0)
const importFile = ref<File | null>(null)
const selectedFile = ref<File | null>(null)
const importing = ref(false)
const updateExisting = ref(false)
const importResult = ref<RoomImportResponse | null>(null)
const uploadRef = ref()
const importForm = ref({
  autoCreate: false
})

// 模板字段说明
const roomTemplateFields = [
  { field: '学校名称', required: '是', description: '必须是系统中已存在的学校', example: '示例学校' },
  { field: '课室名称', required: '是', description: '课室的名称', example: '101普通教室' },
  { field: '课室类型', required: '是', description: '普通教室/实验室/多媒体教室等', example: '普通教室' },
  { field: '课室编码', required: '否', description: '唯一标识码', example: 'R101' },
  { field: '楼栋', required: '否', description: '如：A栋、B栋', example: 'A栋' },
  { field: '楼层', required: '否', description: '数字', example: '1' },
  { field: '座位容量', required: '否', description: '数字', example: '40' },
  { field: '设备清单', required: '否', description: '逗号分隔', example: '投影仪,电脑,音响' },
  { field: '固定分配班级', required: '否', description: '班级名称，留空表示共享', example: '' },
  { field: '课室描述', required: '否', description: '文字说明', example: '标准普通教室' },
  { field: '是否激活', required: '否', description: '是/否', example: '是' },
]

// 分页
const pagination = ref({
  page: 1,
  size: 10,
  total: 0,
  total_pages: 0
})

// 筛选
const filters = ref({
  school_id: '',
  room_type: '',
  building: '',
  search: ''
})

// 表单
const roomForm = ref<RoomCreate>({
  name: '',
  code: '',
  school_id: 0,
  building: '',
  floor: null,
  room_type: '',
  capacity: null,
  equipment: [],
  assigned_classroom_id: null,
  is_active: true,
  description: ''
})

const equipmentString = computed({
  get: () => roomForm.value.equipment?.join(',') || '',
  set: (val: string) => {
    roomForm.value.equipment = val ? val.split(',').map(s => s.trim()) : []
  }
})

// 计算显示的页码
const displayedPages = computed(() => {
  const pages = []
  const current = pagination.value.page
  const total = pagination.value.total_pages
  const start = Math.max(1, current - 2)
  const end = Math.min(total, current + 2)

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// 方法
const loadRooms = async () => {
  try {
    const response = await adminService.getRooms({
      page: pagination.value.page,
      size: pagination.value.size,
      school_id: filters.value.school_id ? Number(filters.value.school_id) : undefined,
      room_type: filters.value.room_type || undefined,
      building: filters.value.building || undefined,
      search: filters.value.search || undefined
    })
    rooms.value = response.rooms
    pagination.value = {
      page: response.page,
      size: response.size,
      total: response.total,
      total_pages: response.total_pages
    }
  } catch (error) {
    console.error('加载课室失败:', error)
    ElMessage.error('加载课室失败')
  }
}

const loadSchools = async () => {
  try {
    const response = await adminService.getSchools({ page: 1, size: 1000 })
    schools.value = response.schools
  } catch (error) {
    console.error('加载学校失败:', error)
    ElMessage.error('加载学校失败')
  }
}

const loadClassrooms = async () => {
  try {
    const response = await adminService.getClassrooms({ page: 1, size: 100 })
    classrooms.value = response.classrooms
  } catch (error) {
    console.error('加载班级失败:', error)
    ElMessage.error('加载班级失败')
  }
}

const getSchoolName = (schoolId: number) => {
  const school = schools.value.find(s => s.id === schoolId)
  return school?.name || '-'
}

const getClassroomName = (classroomId?: number | null) => {
  if (!classroomId) return '共享课室'
  const classroom = classrooms.value.find(c => c.id === classroomId)
  return classroom?.name || '-'
}

const openCreateRoomModal = () => {
  editingRoom.value = null
  roomForm.value = {
    name: '',
    code: '',
    school_id: 0,
    building: '',
    floor: null,
    room_type: '',
    capacity: null,
    equipment: [],
    assigned_classroom_id: null,
    is_active: true,
    description: ''
  }
  showRoomModal.value = true
}

const openEditRoomModal = (room: Room) => {
  editingRoom.value = room
  roomForm.value = { ...room }
  showRoomModal.value = true
}

const saveRoom = async () => {
  try {
    if (editingRoom.value) {
      await adminService.updateRoom(editingRoom.value.id, roomForm.value as RoomUpdate)
      ElMessage.success('课室更新成功')
    } else {
      await adminService.createRoom(roomForm.value)
      ElMessage.success('课室创建成功')
    }
    showRoomModal.value = false
    loadRooms()
  } catch (error: any) {
    console.error('保存课室失败:', error)
    ElMessage.error(error.response?.data?.detail || '保存课室失败')
  }
}

const deleteRoom = async (roomId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个课室吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await adminService.deleteRoom(roomId)
    ElMessage.success('课室删除成功')
    loadRooms()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除课室失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除课室失败')
    }
  }
}

const prevPage = () => {
  if (pagination.value.page > 1) {
    pagination.value.page--
    loadRooms()
  }
}

const nextPage = () => {
  if (pagination.value.page < pagination.value.total_pages) {
    pagination.value.page++
    loadRooms()
  }
}

const goToPage = (page: number) => {
  pagination.value.page = page
  loadRooms()
}

// 批量导入相关方法
const openRoomImportDialog = () => {
  importStep.value = 0
  selectedFile.value = null
  importFile.value = null
  updateExisting.value = false
  importResult.value = null
  showImportDialog.value = true
}

const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
  importFile.value = file.raw
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const startImport = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请选择要导入的文件')
    return
  }

  importing.value = true
  try {
    const result = await adminService.importRooms(selectedFile.value, updateExisting.value)
    importResult.value = result
    importStep.value = 2

    if (result.failed === 0) {
      ElMessage.success(`导入成功！新增 ${result.created} 条，更新 ${result.updated} 条`)
    } else {
      ElMessage.warning(
        `导入完成！新增 ${result.created} 条，更新 ${result.updated} 条，失败 ${result.failed} 条`
      )
    }

    loadRooms()
  } catch (error: any) {
    console.error('导入失败:', error)
    ElMessage.error(error.response?.data?.detail || '导入失败')
  } finally {
    importing.value = false
  }
}

const closeImportDialog = () => {
  showImportDialog.value = false
  importStep.value = 0
  selectedFile.value = null
  importFile.value = null
  importResult.value = null
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

const downloadRoomTemplate = () => {
  // 创建Excel模板数据
  const template = [
    {
      '学校名称': '示例学校',
      '课室名称': '101普通教室',
      '课室类型': '普通教室',
      '课室编码': 'R101',
      '楼栋': 'A栋',
      '楼层': 1,
      '座位容量': 40,
      '设备清单': '投影仪,电脑,音响',
      '固定分配班级': '',
      '课室描述': '标准普通教室',
      '是否激活': '是'
    },
    {
      '学校名称': '示例学校',
      '课室名称': '化学实验室1',
      '课室类型': '实验室',
      '课室编码': 'LAB-CHEM-01',
      '楼栋': 'B栋',
      '楼层': 2,
      '座位容量': 30,
      '设备清单': '实验台,通风设备,防护用品',
      '固定分配班级': '',
      '课室描述': '化学专用实验室',
      '是否激活': '是'
    }
  ]

  // 转换为CSV格式
  const headers = Object.keys(template[0])
  const csvContent = [
    headers.join(','),
    ...template.map(row => headers.map(header => {
      const value = row[header as keyof typeof row]
      // 处理包含逗号的字段
      if (typeof value === 'string' && value.includes(',')) {
        return `"${value}"`
      }
      return value
    }).join(','))
  ].join('\n')

  // 创建Blob并下载
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', '课室导入模板.csv')
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  ElMessage.success('模板下载成功')
}

// 初始化
onMounted(() => {
  loadRooms()
  loadSchools()
  loadClassrooms()
})
</script>
