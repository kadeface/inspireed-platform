<template>
  <div class="space-y-6">
    <!-- 操作栏 -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex items-center gap-3 flex-nowrap overflow-x-auto">
        <button
          @click="openCreateClassroomModal"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 whitespace-nowrap flex-shrink-0"
        >
          + 创建班级
        </button>
        <button
          @click="openClassroomImportDialog"
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 whitespace-nowrap flex-shrink-0"
        >
          📥 批量导入班级
        </button>
        <FilterBar
          :filters="classroomFilterConfigs"
          :search-config="classroomSearchConfig"
          v-model="classroomFilters"
          v-model:search-model-value="classroomSearchQuery"
          @filter-change="handleClassroomFilterChange"
          @search-enter="handleClassroomSearchEnter"
        >
          <template #extra>
            <button
              @click="loadAllClassrooms"
              class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 whitespace-nowrap flex-shrink-0"
            >
              🔄 刷新
            </button>
          </template>
        </FilterBar>
      </div>
    </div>

    <!-- 班级列表 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div v-if="allClassroomsLoading" class="p-6 text-center text-gray-500">
        加载中...
      </div>
      <div v-else-if="allClassrooms.length === 0" class="p-6 text-center text-gray-500">
        暂无班级
      </div>
      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">班级名称</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">学校</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">年级</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">入学年份</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="classroom in allClassrooms" :key="classroom.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm font-medium text-gray-900">{{ classroom.name }}</div>
              <div class="text-xs text-gray-500">编码：{{ classroom.code || '—' }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ getSchoolNameById(classroom.school_id) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ getGradeName(classroom.grade_id) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ classroom.enrollment_year || '—' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                :class="classroom.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
              >
                {{ classroom.is_active ? '激活' : '未激活' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <div class="flex gap-2">
                <button @click="editClassroom(classroom)" class="text-blue-600 hover:text-blue-900">
                  编辑
                </button>
                <button @click="deleteClassroom(classroom)" class="text-red-600 hover:text-red-900">
                  删除
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <div class="flex justify-center mt-4 pb-4" v-if="classroomPagination.total > 0">
        <el-pagination
          v-model:current-page="classroomPagination.page"
          v-model:page-size="classroomPagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="classroomPagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleClassroomPageSizeChange"
          @current-change="handleClassroomPageChange"
        />
      </div>
    </div>

    <!-- 创建/编辑班级对话框 -->
    <el-dialog
      v-model="showClassroomModal"
      :title="editingClassroom ? '编辑班级' : '创建班级'"
      width="600px"
      :close-on-click-modal="false"
    >
      <!-- 编码格式说明 -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
        <div class="text-sm text-blue-800">
          <div class="font-semibold mb-1">📝 班级编码格式说明：</div>
          <ul class="list-disc list-inside space-y-1 text-xs">
            <li>格式：<code class="bg-blue-100 px-1 rounded">前1-2位（年级级别）+ 后2位（班级序号）</code></li>
            <li>示例：<code class="bg-blue-100 px-1 rounded">701</code> = 7年级1班，<code class="bg-blue-100 px-1 rounded">1001</code> = 10年级1班</li>
            <li>年级级别范围：1-12（1-6小学，7-9初中，10-12高中）</li>
            <li>班级序号范围：01-99</li>
          </ul>
        </div>
      </div>

      <el-form :model="classroomForm" label-width="120px">
        <el-form-item label="班级编码*" required>
          <el-input 
            v-model="classroomForm.code" 
            @input="handleClassroomCodeChange"
            @keypress="handleCodeKeypress"
            placeholder="如：701、1001" 
            maxlength="4"
          />
          <div v-if="classroomCodeError" class="text-red-500 text-xs mt-1 flex items-start gap-1">
            <span class="mt-0.5">❌</span>
            <span class="flex-1">{{ classroomCodeError }}</span>
          </div>
          <div v-else-if="classroomForm.code && !classroomForm.grade_id" class="text-amber-600 text-xs mt-1 flex items-start gap-1">
            <span class="mt-0.5">💡</span>
            <span class="flex-1">系统将根据编码自动匹配年级，或请手动选择年级</span>
          </div>
          <div v-else-if="classroomForm.code && classroomForm.grade_id && classroomForm.name" class="text-green-600 text-xs mt-1 flex items-center gap-1">
            <span>✅</span>
            <span>班级名称已自动生成：<strong>{{ classroomForm.name }}</strong></span>
          </div>
          <div v-else-if="classroomForm.code && classroomForm.code.length >= 3 && !classroomForm.grade_id" class="text-blue-600 text-xs mt-1 flex items-start gap-1">
            <span class="mt-0.5">ℹ️</span>
            <span class="flex-1">正在尝试自动匹配年级...</span>
          </div>
        </el-form-item>
        <el-form-item label="班级名称*" required>
          <el-input 
            v-model="classroomForm.name" 
            :readonly="true"
            placeholder="将根据班级编码和年级自动生成" 
            :class="classroomForm.name ? 'bg-green-50 border-green-200' : 'bg-gray-50'"
          />
          <div v-if="!classroomForm.name && classroomForm.code && classroomForm.grade_id" class="text-gray-500 text-xs mt-1">
            请检查班级编码格式是否正确
          </div>
        </el-form-item>
        <el-form-item label="所属学校" required>
          <el-select v-model="classroomForm.school_id" placeholder="请选择学校" filterable class="w-full">
            <el-option
              v-for="school in schools"
              :key="school.id"
              :label="school.name"
              :value="school.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所属年级" required>
          <el-select 
            v-model="classroomForm.grade_id" 
            @change="handleGradeChange"
            placeholder="请选择年级" 
            class="w-full"
          >
            <el-option
              v-for="grade in grades"
              :key="grade.id"
              :label="grade.name"
              :value="grade.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="入学年份">
          <el-input-number
            v-model="classroomForm.enrollment_year"
            :min="1990"
            :max="2100"
            placeholder="如：2024"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="班级容量">
          <el-input-number
            v-model="classroomForm.capacity"
            :min="1"
            :max="200"
            placeholder="物理教室容量"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="班级描述">
          <el-input
            v-model="classroomForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入班级描述"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="classroomForm.is_active" active-text="激活" inactive-text="停用" />
        </el-form-item>
        <div v-if="classroomNameError" class="text-red-600 text-sm mb-4">{{ classroomNameError }}</div>
      </el-form>
      <template #footer>
        <el-button @click="closeClassroomModal">取消</el-button>
        <el-button type="primary" @click="saveClassroom" :loading="classroomSaving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入班级对话框 -->
    <el-dialog
      v-model="showClassroomImportDialog"
      title="批量导入班级（支持多个学校）"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-steps :active="classroomImportStep" finish-status="success" align-center class="mb-6">
        <el-step title="下载模板" />
        <el-step title="上传文件" />
        <el-step title="导入结果" />
      </el-steps>

      <!-- 步骤1: 下载模板 -->
      <div v-if="classroomImportStep === 0" class="space-y-4">
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p class="text-sm text-blue-800 mb-2"><strong>导入说明：</strong></p>
          <ul class="text-sm text-blue-700 list-disc list-inside space-y-1">
            <li>请先下载Excel模板，按照模板格式填写班级信息</li>
            <li>必需字段：学校名称、年级级别、班级编号</li>
            <li>可选字段：学校代码、年级名称、班级名称、入学年份、班级容量、班级描述</li>
            <li>支持格式：.xlsx, .xls</li>
            <li><strong>注意：</strong>可以一次导入多个学校的班级，Excel中需要包含学校信息</li>
          </ul>
        </div>
        <div class="bg-gray-50 border rounded-lg p-4">
          <h4 class="text-sm font-medium mb-2">模板字段说明</h4>
          <el-table :data="classroomTemplateFields" border size="small">
            <el-table-column prop="field" label="字段名" width="120" />
            <el-table-column prop="required" label="是否必填" width="100" />
            <el-table-column prop="description" label="说明" />
            <el-table-column prop="example" label="示例" width="150" />
          </el-table>
        </div>
        <div class="flex justify-center gap-4">
          <el-button type="primary" @click="downloadClassroomTemplate" :icon="Download">
            下载Excel模板
          </el-button>
          <el-button @click="classroomImportStep = 1">
            已有模板，下一步
            <el-icon class="ml-2"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 步骤2: 上传文件 -->
      <div v-if="classroomImportStep === 1" class="space-y-4">
        <el-form :model="classroomImportForm" label-width="140px">
          <el-form-item label="统一设置入学年份">
            <el-input-number
              v-model="classroomImportForm.enrollmentYear"
              :min="1900"
              :max="2100"
              placeholder="留空则使用Excel中的值"
              style="width: 200px;"
            />
            <span class="ml-2 text-sm text-gray-500">如果设置，将覆盖Excel中的所有入学年份</span>
          </el-form-item>
          <el-form-item label="统一设置班级容量">
            <el-input-number
              v-model="classroomImportForm.capacity"
              :min="1"
              :max="200"
              placeholder="留空则使用Excel中的值"
              style="width: 200px;"
            />
            <span class="ml-2 text-sm text-gray-500">如果设置，将覆盖Excel中的所有班级容量</span>
          </el-form-item>
          <el-form-item label="更新已存在班级">
            <el-switch
              v-model="classroomImportForm.updateExisting"
              active-text="是"
              inactive-text="否"
            />
            <span class="ml-2 text-sm text-gray-500">如果班级已存在，是否更新</span>
          </el-form-item>
        </el-form>
        <el-upload
          ref="classroomUploadRef"
          class="upload-demo"
          drag
          :auto-upload="false"
          :limit="1"
          :on-change="handleClassroomFileChange"
          :on-exceed="handleClassroomExceed"
          accept=".xlsx,.xls"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
          <template #tip>
            <div class="el-upload__tip">只能上传 xlsx/xls 文件，且不超过 10MB</div>
          </template>
        </el-upload>
        <div v-if="selectedClassroomFile" class="mt-4 p-3 bg-gray-50 rounded-lg">
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="文件名">{{ selectedClassroomFile.name }}</el-descriptions-item>
            <el-descriptions-item label="文件大小">{{ formatFileSize(selectedClassroomFile.size) }}</el-descriptions-item>
          </el-descriptions>
        </div>
        <div class="flex justify-center gap-4">
          <el-button @click="classroomImportStep = 0">
            <el-icon><ArrowLeft /></el-icon>
            上一步
          </el-button>
          <el-button
            type="primary"
            @click="startClassroomImport"
            :loading="classroomImporting"
            :disabled="!selectedClassroomFile"
          >
            <el-icon><Upload /></el-icon>
            <span class="ml-2">开始导入</span>
          </el-button>
        </div>
      </div>

      <!-- 步骤3: 导入结果 -->
      <div v-if="classroomImportStep === 2" class="space-y-4">
        <el-alert
          :title="classroomImportResult.success > 0 ? '✅ 导入完成' : '❌ 导入失败'"
          :type="classroomImportResult.success > 0 ? 'success' : 'error'"
          :closable="false"
        />
        <div v-if="classroomImportResult.total > 0">
          <h4 class="text-sm font-medium mb-2">📊 导入统计</h4>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="总记录数" :value="classroomImportResult.total" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="成功" :value="classroomImportResult.success" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="失败" :value="classroomImportResult.failed" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="创建" :value="classroomImportResult.created" />
            </el-col>
          </el-row>
          <el-row :gutter="20" class="mt-4">
            <el-col :span="6">
              <el-statistic title="更新" :value="classroomImportResult.updated" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="跳过" :value="classroomImportResult.skipped" />
            </el-col>
          </el-row>
          <div v-if="classroomImportResult.errors && classroomImportResult.errors.length > 0" class="mt-4">
            <h4 class="text-sm font-medium mb-2">⚠️ 错误详情</h4>
            <el-table :data="classroomImportResult.errors" max-height="300" size="small">
              <el-table-column prop="row" label="行号" width="80" />
              <el-table-column prop="field" label="字段" width="120" />
              <el-table-column prop="message" label="错误信息" />
            </el-table>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button v-if="classroomImportStep < 2" @click="showClassroomImportDialog = false">取消</el-button>
        <el-button v-if="classroomImportStep === 2" type="primary" @click="closeClassroomImportDialog">完成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Upload, ArrowRight, UploadFilled } from '@element-plus/icons-vue'
import { useToast } from '@/composables/useToast'
import adminService, { type Region, type School, type Classroom, type User, type SchoolType } from '@/services/admin'
import curriculumService from '@/services/curriculum'
import { classroomAssistantService } from '@/services/classroomAssistant'
import type { Grade } from '@/types/curriculum'
import FilterBar, { type FilterConfig, type SearchConfig } from '@/components/Common/FilterBar.vue'
import type {
  ClassroomMembership,
  ClassroomMembershipCreate,
  ClassroomMembershipUpdate,
} from '@/types/classroomAssistant'
import { RoleInClass } from '@/types/classroomAssistant'
import type { UploadProps } from 'element-plus'
import * as XLSX from 'xlsx'

const toast = useToast()

// ==================== 班级管理状态 ====================
const allClassrooms = ref<Classroom[]>([])
const allClassroomsLoading = ref(false)
const allRegions = ref<Region[]>([])
const schools = ref<School[]>([])
const grades = ref<Grade[]>([])
const schoolTypes = ref<SchoolType[]>([])
const classroomPagination = ref({
  page: 1,
  size: 10,
  total: 0,
  totalPages: 0,
})

// 筛选状态（使用统一的 filters 对象）
const classroomFilters = ref({
  region_id: undefined as number | undefined,
  school_type: undefined as string | undefined,
  school_id: undefined as number | undefined,
  grade_id: undefined as number | undefined,
})
const classroomSearchQuery = ref('')

// 班级CRUD状态
const showClassroomModal = ref(false)
const editingClassroom = ref<Classroom | null>(null)
const classroomSaving = ref(false)
const classroomNameError = ref('')
const classroomCodeError = ref('')
const classroomForm = ref<Partial<Classroom>>({
  name: '',
  code: '',
  school_id: undefined,
  grade_id: undefined,
  enrollment_year: undefined,
  capacity: undefined,
  description: '',
  is_active: true,
})

// 批量导入班级状态
const showClassroomImportDialog = ref(false)
const classroomImportStep = ref(0)
const selectedClassroomFile = ref<File | null>(null)
const classroomImporting = ref(false)
const classroomImportForm = ref({
  enrollmentYear: undefined as number | undefined,
  capacity: undefined as number | undefined,
  updateExisting: false
})
const classroomImportResult = ref({
  total: 0,
  success: 0,
  failed: 0,
  created: 0,
  updated: 0,
  skipped: 0,
  errors: [] as any[]
})
const classroomUploadRef = ref()

// 模板字段说明
const classroomTemplateFields = [
  { field: '学校名称*', required: '是', description: '学校全称', example: '开平市第一中学' },
  { field: '学校代码', required: '否', description: '学校编码（可选，用于匹配）', example: '10001' },
  { field: '年级级别*', required: '是', description: '年级级别（1-12）', example: '7' },
  { field: '年级名称', required: '否', description: '年级名称（可选）', example: '七年级' },
  { field: '班级编号*', required: '是', description: '班级编号', example: '701' },
  { field: '班级名称', required: '否', description: '班级名称（可选）', example: '七年级1班' },
  { field: '入学年份', required: '否', description: '入学年份', example: '2024' },
  { field: '班级容量', required: '否', description: '物理教室容量', example: '45' },
  { field: '班级描述', required: '否', description: '班级描述', example: '重点班' },
]

// ==================== 成员管理状态 ====================
const showMemberManager = ref(false)
const selectedClassroom = ref<Classroom | null>(null)
const members = ref<ClassroomMembership[]>([])
const membersLoading = ref(false)
const memberPagination = ref({
  page: 1,
  size: 10,
  total: 0,
  totalPages: 0,
})
const showMemberModal = ref(false)
const editingMember = ref<ClassroomMembership | null>(null)
const memberSaving = ref(false)
const memberError = ref('')
const memberForm = ref<ClassroomMembershipCreate & { userId: number }>({
  classroomId: 0,
  userId: 0,
  roleInClass: RoleInClass.STUDENT,
  studentNo: null,
  seatNo: null,
  cadreTitle: null,
  isPrimaryClass: false,
})

// 用户搜索状态
const userSearchQuery = ref('')
const userRoleFilter = ref<string>('')
const searchedUsers = ref<User[]>([])
const userSearchLoading = ref(false)
const selectedUserInfo = ref<User | null>(null)

// 批量添加成员状态
const batchAddMode = ref(false)
const sourceClassroomFilter = ref<number | ''>('')
const sourceClassroomStudents = ref<ClassroomMembership[]>([])
const sourceStudentsLoading = ref(false)
const selectedStudentIds = ref<Set<number>>(new Set())

// ==================== 计算属性 ====================
// 学校筛选：根据区域、学段和年级筛选
// 如果选择了年级，只显示有该年级班级的学校
const filteredSchoolsForClassroom = computed(() => {
  let result = schools.value

  // 先根据区域筛选
  if (classroomFilters.value.region_id) {
    result = result.filter(school => school.region_id === classroomFilters.value.region_id)
  }

  // 根据学段筛选（通过 school_type 匹配）
  if (classroomFilters.value.school_type) {
    result = result.filter(school => school.school_type === classroomFilters.value.school_type)
  }

  // 如果选择了年级，只显示有该年级班级的学校
  if (classroomFilters.value.grade_id) {
    const schoolIdsWithGrade = new Set(
      allClassrooms.value
        .filter(c => c.grade_id === classroomFilters.value.grade_id)
        .map(c => c.school_id)
    )
    result = result.filter(school => schoolIdsWithGrade.has(school.id))
  }

  return result
})

// 筛选配置
const classroomFilterConfigs = computed<FilterConfig[]>(() => [
  {
    key: 'region_id',
    label: '县区',
    placeholder: '所有县区',
    options: allRegions.value,
    type: 'number',
    style: { width: '120px', minWidth: '110px', maxWidth: '150px' },
  },
  {
    key: 'school_type',
    label: '学段',
    placeholder: '所有学段',
    computedOptions: () => {
      if (!schoolTypes.value || schoolTypes.value.length === 0) {
        return []
      }
      return schoolTypes.value.map(st => ({
        id: st.name || '',
        name: st.name || ''
      })).filter(opt => opt.name)
    },
    valueKey: 'id',
    labelKey: 'name',
    type: 'string',
    style: { width: '110px', minWidth: '100px', maxWidth: '130px' },
  },
  {
    key: 'grade_id',
    label: '年级',
    placeholder: '所有年级',
    options: grades.value,
    type: 'number',
    style: { width: '110px', minWidth: '100px', maxWidth: '130px' },
  },
  {
    key: 'school_id',
    label: '学校',
    placeholder: '所有学校',
    computedOptions: () => filteredSchoolsForClassroom.value,
    dependsOn: 'region_id',
    type: 'number',
    style: { width: '160px', minWidth: '140px', maxWidth: '220px' },
  },
])

// 搜索建议函数
function fetchSearchSuggestions(queryString: string, callback: (suggestions: any[]) => void) {
  if (!queryString || queryString.trim().length === 0) {
    callback([])
    return
  }

  const query = queryString.trim().toLowerCase()
  const suggestions: any[] = []

  // 搜索学校（优先匹配）
  schools.value.forEach((school) => {
    const schoolName = school.name.toLowerCase()
    if (schoolName.includes(query)) {
      // 计算匹配度（开头匹配优先）
      const startsWith = schoolName.startsWith(query)
      suggestions.push({
        value: school.name,
        type: 'school',
        subtitle: '学校',
        data: school,
        _priority: startsWith ? 1 : 2, // 开头匹配优先级更高
      })
    }
  })

  // 搜索班级
  allClassrooms.value.forEach((classroom) => {
    const nameMatch = classroom.name.toLowerCase().includes(query)
    const codeMatch = classroom.code && classroom.code.toLowerCase().includes(query)
    const schoolName = getSchoolNameById(classroom.school_id).toLowerCase()
    const schoolMatch = schoolName.includes(query)

    if (nameMatch || codeMatch || schoolMatch) {
      const schoolName = getSchoolNameById(classroom.school_id)
      const gradeName = getGradeName(classroom.grade_id)
      const subtitle = `${schoolName} · ${gradeName}${classroom.code ? ` · ${classroom.code}` : ''}`
      
      // 计算匹配度
      let priority = 3
      if (classroom.name.toLowerCase().startsWith(query)) priority = 1
      else if (nameMatch) priority = 2
      else if (codeMatch) priority = 2.5

      suggestions.push({
        value: classroom.name,
        type: 'classroom',
        subtitle: subtitle,
        data: classroom,
        _priority: priority,
      })
    }
  })

  // 按优先级排序，然后限制数量（最多显示 10 条）
  suggestions.sort((a, b) => (a._priority || 999) - (b._priority || 999))
  callback(suggestions.slice(0, 10).map(({ _priority, ...rest }) => rest))
}

// 搜索配置
const classroomSearchConfig: SearchConfig = {
  placeholder: '搜索学校或班级名称...',
  debounce: false,
  enterToSearch: true,
  fetchSuggestions: fetchSearchSuggestions,
  triggerOnFocus: true,
  clearable: true,
  style: { width: '260px', minWidth: '220px', maxWidth: '300px' },
}

// ==================== 班级管理方法 ====================
async function loadAllRegions() {
  try {
    const response = await adminService.getRegions({ size: 1000 })
    allRegions.value = response.regions
  } catch (error: any) {
    console.error('Failed to load all regions:', error)
  }
}

async function loadAllSchools() {
  try {
    // 根据区域筛选加载学校列表
    const params: any = { page: 1, size: 1000 }
    if (classroomFilters.value.region_id) {
      params.region_id = classroomFilters.value.region_id
    }
    const response = await adminService.getSchools(params)
    schools.value = response.schools
  } catch (error: any) {
    console.error('Failed to load schools:', error)
    toast.error(error.response?.data?.detail || '加载学校列表失败')
  }
}

async function loadGradesList() {
  try {
    grades.value = await curriculumService.getGrades(true)
  } catch (error: any) {
    console.error('Failed to load grades:', error)
  }
}

async function loadSchoolTypes() {
  try {
    const response = await adminService.getSchoolTypes()
    schoolTypes.value = response.school_types
  } catch (error: any) {
    console.error('Failed to load school types:', error)
    toast.error(error.response?.data?.detail || '加载学段列表失败')
  }
}

async function loadAllClassrooms() {
  try {
    allClassroomsLoading.value = true

    // 确保基础数据已加载
    if (allRegions.value.length === 0) {
      await loadAllRegions()
    }
    if (schoolTypes.value.length === 0) {
      await loadSchoolTypes()
    }
    if (grades.value.length === 0) {
      await loadGradesList()
    }

    // 根据区域筛选加载学校列表
    await loadAllSchools()
    
    // 加载班级列表
    const response = await adminService.getClassrooms({
      page: classroomPagination.value.page,
      size: classroomPagination.value.size,
      region_id: classroomFilters.value.region_id,
      school_type: classroomFilters.value.school_type || undefined,
      school_id: classroomFilters.value.school_id,
      grade_id: classroomFilters.value.grade_id,
      search: classroomSearchQuery.value || undefined,
    })
    allClassrooms.value = response.classrooms
    classroomPagination.value.total = response.total || 0
    classroomPagination.value.totalPages = response.total_pages || 0
    
    // 确保返回结果中的学校都在列表中（处理边缘情况）
    const schoolIds = [...new Set(response.classrooms.map(c => c.school_id))]
    const missingSchoolIds = schoolIds.filter(id => !schools.value.find(s => s.id === id))
    if (missingSchoolIds.length > 0) {
      // 补充缺失的学校信息
      for (const schoolId of missingSchoolIds) {
        try {
          const school = await adminService.getSchool(schoolId)
          schools.value.push(school)
        } catch (error) {
          console.warn(`Failed to load school ${schoolId}:`, error)
        }
      }
    }
  } catch (error: any) {
    console.error('Failed to load all classrooms:', error)
    toast.error(error.response?.data?.detail || '加载班级列表失败')
  } finally {
    allClassroomsLoading.value = false
  }
}

function handleClassroomPageChange(page: number) {
  classroomPagination.value.page = page
  loadAllClassrooms()
}

function handleClassroomPageSizeChange(size: number) {
  classroomPagination.value.size = size
  classroomPagination.value.page = 1
  loadAllClassrooms()
}

// 处理筛选变化
async function handleClassroomFilterChange(key: string, value: any) {
  if (key === 'region_id') {
    // 区域改变时，重新加载学校列表（FilterBar 会自动清空 school_id）
    classroomPagination.value.page = 1
    await loadAllSchools()
    await loadAllClassrooms()
  } else if (key === 'stage_id') {
    // 学段改变时，重置页码并加载班级列表
    classroomPagination.value.page = 1
    loadAllClassrooms()
  } else if (key === 'grade_id') {
    // 年级改变时，需要先加载班级列表以获取有该年级的学校，然后更新学校筛选列表
    classroomPagination.value.page = 1
    await loadAllClassrooms()
    // 加载完成后，filteredSchoolsForClassroom 会自动根据新的班级列表更新
  } else {
    // 学校筛选改变时，重置页码并加载班级列表
    classroomPagination.value.page = 1
    loadAllClassrooms()
  }
}

// 处理搜索 Enter 键
function handleClassroomSearchEnter(value: string) {
  classroomPagination.value.page = 1
  loadAllClassrooms()
}

function getGradeName(gradeId?: number | null): string {
  if (!gradeId) return '—'
  const grade = grades.value.find(g => g.id === gradeId)
  return grade ? grade.name : `年级 #${gradeId}`
}

function getSchoolNameById(schoolId: number): string {
  const school = schools.value.find((s) => s.id === schoolId)
  return school?.name || `学校${schoolId}`
}

/**
 * 解析班级编号，提取年级级别和班级序号
 * 规则：后2位是班级序号，前面是年级级别
 * 例如：701 -> (7, 1), 1001 -> (10, 1), 1203 -> (12, 3)
 */
function parseClassroomCode(code: string): { gradeLevel: number | null; classSeq: number | null } {
  if (!code || !code.trim()) {
    return { gradeLevel: null, classSeq: null }
  }

  const trimmedCode = code.trim()
  
  // 至少需要3位数字（如701）
  if (trimmedCode.length < 3) {
    return { gradeLevel: null, classSeq: null }
  }

  // 提取后2位作为班级序号
  const classPart = trimmedCode.slice(-2)
  const gradePart = trimmedCode.slice(0, -2)

  try {
    const gradeLevel = parseInt(gradePart, 10)
    const classSeq = parseInt(classPart, 10)

    // 验证范围：年级1-12，班级序号1-99
    if (gradeLevel >= 1 && gradeLevel <= 12 && classSeq >= 1 && classSeq <= 99) {
      return { gradeLevel, classSeq }
    }
  } catch (e) {
    // 解析失败
  }

  return { gradeLevel: null, classSeq: null }
}

/**
 * 根据班级编号和年级生成班级名称
 */
function generateClassroomName(): void {
  classroomCodeError.value = ''
  
  if (!classroomForm.value.code || !classroomForm.value.grade_id) {
    classroomForm.value.name = ''
    return
  }

  const { gradeLevel, classSeq } = parseClassroomCode(classroomForm.value.code)

  if (!gradeLevel || !classSeq) {
    classroomCodeError.value = '班级编码格式不正确。格式：前1-2位表示年级（1-12），后2位表示班级序号（01-99）。示例：701（7年级1班）、1001（10年级1班）'
    classroomForm.value.name = ''
    return
  }

  // 获取选中的年级对象
  const selectedGrade = grades.value.find(g => g.id === classroomForm.value.grade_id)
  if (!selectedGrade) {
    classroomCodeError.value = '请先选择年级'
    classroomForm.value.name = ''
    return
  }

  // 验证年级级别是否匹配
  if (selectedGrade.level !== gradeLevel) {
    classroomCodeError.value = `班级编码中的年级级别（${gradeLevel}）与所选年级（${selectedGrade.name}，级别${selectedGrade.level}）不匹配。请检查编码或重新选择年级。`
    classroomForm.value.name = ''
    return
  }

  // 生成班级名称：年级名称 + 班级序号 + "班"
  // 班级序号直接使用，不需要特殊处理（01会显示为1，10会显示为10）
  classroomForm.value.name = `${selectedGrade.name}${classSeq}班`
}

/**
 * 处理班级编码变化
 */
function handleClassroomCodeChange(): void {
  // 自动过滤非数字字符
  if (classroomForm.value.code) {
    const numericOnly = classroomForm.value.code.replace(/\D/g, '')
    if (numericOnly !== classroomForm.value.code) {
      classroomForm.value.code = numericOnly
      return // 会在下次输入时触发
    }
  }
  
  // 先尝试根据编码自动填充年级
  autoFillGradeFromCode()
  // 然后生成班级名称
  generateClassroomName()
}

/**
 * 限制编码输入只能输入数字
 */
function handleCodeKeypress(event: KeyboardEvent): void {
  // 只允许数字键
  const char = String.fromCharCode(event.which || event.keyCode)
  if (!/[0-9]/.test(char)) {
    event.preventDefault()
  }
}

/**
 * 根据班级编码自动填充年级（如果可能）
 */
function autoFillGradeFromCode(): void {
  if (!classroomForm.value.code) {
    return
  }

  // 只处理纯数字的编码
  if (!/^\d+$/.test(classroomForm.value.code.trim())) {
    return
  }

  const { gradeLevel } = parseClassroomCode(classroomForm.value.code)
  
  if (!gradeLevel) {
    return
  }

  // 如果已经选择了年级，且年级级别匹配，不需要修改
  if (classroomForm.value.grade_id) {
    const selectedGrade = grades.value.find(g => g.id === classroomForm.value.grade_id)
    if (selectedGrade && selectedGrade.level === gradeLevel) {
      return
    }
  }

  // 尝试找到匹配的年级
  const matchingGrade = grades.value.find(g => g.level === gradeLevel)
  if (matchingGrade) {
    classroomForm.value.grade_id = matchingGrade.id
  }
}

/**
 * 处理年级变化
 */
function handleGradeChange(): void {
  generateClassroomName()
}

function openCreateClassroomModal() {
  editingClassroom.value = null
  classroomNameError.value = ''
  classroomCodeError.value = ''
  classroomForm.value = {
    name: '',
    code: '',
    school_id: undefined,
    grade_id: undefined,
    enrollment_year: undefined,
    capacity: undefined,
    description: '',
    is_active: true,
  }
  showClassroomModal.value = true
}

function editClassroom(classroom: Classroom) {
  editingClassroom.value = classroom
  classroomNameError.value = ''
  classroomCodeError.value = ''
  classroomForm.value = {
    name: classroom.name,
    code: classroom.code || '',
    school_id: classroom.school_id,
    grade_id: classroom.grade_id,
    enrollment_year: classroom.enrollment_year || undefined,
    capacity: (classroom as any).capacity || undefined,
    description: classroom.description || '',
    is_active: classroom.is_active,
  }
  // 编辑时，如果编码和年级都存在，验证并重新生成名称（确保格式统一）
  if (classroomForm.value.code && classroomForm.value.grade_id) {
    // 先尝试自动填充年级（如果编码格式正确）
    autoFillGradeFromCode()
    // 然后生成名称
    generateClassroomName()
  }
  showClassroomModal.value = true
}

async function saveClassroom() {
  if (!classroomForm.value.code || !classroomForm.value.name || !classroomForm.value.school_id || !classroomForm.value.grade_id) {
    classroomNameError.value = '请填写所有必填字段（班级编码、班级名称、学校、年级）'
    return
  }

  // 验证班级编码格式
  if (classroomCodeError.value) {
    classroomNameError.value = '请先修正班级编码格式错误'
    return
  }

  try {
    classroomSaving.value = true
    classroomNameError.value = ''

    if (editingClassroom.value) {
      await adminService.updateClassroom(editingClassroom.value.id, classroomForm.value)
      ElMessage.success('班级更新成功')
    } else {
      await adminService.createClassroom(classroomForm.value)
      ElMessage.success('班级创建成功')
    }

    closeClassroomModal()
    await loadAllClassrooms()
  } catch (error: any) {
    console.error('保存班级失败:', error)
    classroomNameError.value = error.response?.data?.detail || '保存失败，请重试'
  } finally {
    classroomSaving.value = false
  }
}

async function deleteClassroom(classroom: Classroom) {
  try {
    await ElMessageBox.confirm(
      `确定要删除班级 "${classroom.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await adminService.deleteClassroom(classroom.id)
    ElMessage.success('班级删除成功')
    await loadAllClassrooms()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除班级失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败，请重试')
    }
  }
}

function closeClassroomModal() {
  showClassroomModal.value = false
  editingClassroom.value = null
  classroomNameError.value = ''
}

// ==================== 批量导入班级方法 ====================
function openClassroomImportDialog() {
  showClassroomImportDialog.value = true
  classroomImportStep.value = 0
  selectedClassroomFile.value = null
  classroomImportForm.value = {
    enrollmentYear: undefined,
    capacity: undefined,
    updateExisting: false
  }
  classroomImportResult.value = {
    total: 0,
    success: 0,
    failed: 0,
    created: 0,
    updated: 0,
    skipped: 0,
    errors: []
  }
  if (classroomUploadRef.value) {
    classroomUploadRef.value.clearFiles()
  }
}

function closeClassroomImportDialog() {
  showClassroomImportDialog.value = false
  classroomImportStep.value = 0
  selectedClassroomFile.value = null
  if (classroomUploadRef.value) {
    classroomUploadRef.value.clearFiles()
  }
  loadAllClassrooms()
}

function downloadClassroomTemplate() {
  const template = [
    ['学校名称*', '学校代码', '年级级别*', '年级名称', '班级编号*', '班级名称', '入学年份', '班级容量', '班级描述'],
    ['开平市第一中学', '10001', 7, '七年级', '701', '七年级1班', 2024, 45, '重点班'],
    ['开平市第一中学', '10001', 7, '七年级', '702', '七年级2班', 2024, 45, '普通班'],
    ['开平市第二中学', '10002', 7, '七年级', '701', '七年级1班', 2024, 50, ''],
  ]

  const ws = XLSX.utils.aoa_to_sheet(template)
  const colWidths = [
    { wch: 20 }, { wch: 12 }, { wch: 12 }, { wch: 12 },
    { wch: 12 }, { wch: 15 }, { wch: 12 }, { wch: 12 }, { wch: 15 }
  ]
  ws['!cols'] = colWidths

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '班级信息')
  XLSX.writeFile(wb, '班级信息导入模板.xlsx')
  ElMessage.success('模板下载成功')
}

const handleClassroomFileChange: UploadProps['onChange'] = (uploadFile) => {
  selectedClassroomFile.value = uploadFile.raw || null
}

const handleClassroomExceed: UploadProps['onExceed'] = () => {
  ElMessage.warning('只能上传一个文件')
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

async function startClassroomImport() {
  if (!selectedClassroomFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  classroomImporting.value = true

  try {
    const result = await adminService.importClassrooms(
      selectedClassroomFile.value,
      undefined, // school_id（县区端不需要，从Excel中读取）
      undefined, // region_id（可选）
      classroomImportForm.value.updateExisting,
      classroomImportForm.value.enrollmentYear,
      classroomImportForm.value.capacity
    )

    classroomImportResult.value = result
    classroomImportStep.value = 2

    if (result.success > 0) {
      ElMessage.success(`导入完成！成功 ${result.success} 条，失败 ${result.failed} 条`)
    } else {
      ElMessage.error(`导入失败：${result.errors.length > 0 ? result.errors[0].message : '未知错误'}`)
    }
  } catch (error: any) {
    console.error('导入失败:', error)
    ElMessage.error(error.response?.data?.detail || '导入失败')
    classroomImportResult.value = {
      total: 0,
      success: 0,
      failed: 1,
      created: 0,
      updated: 0,
      skipped: 0,
      errors: [{
        row: 0,
        field: null,
        message: error.response?.data?.detail || '导入失败'
      }]
    }
    classroomImportStep.value = 2
  } finally {
    classroomImporting.value = false
  }
}

// ==================== 成员管理方法 ====================
async function openMemberManager(classroom: Classroom) {
  selectedClassroom.value = classroom
  showMemberManager.value = true
  await loadMembers()
}

function closeMemberManager() {
  showMemberManager.value = false
  selectedClassroom.value = null
  members.value = []
  memberPagination.value = {
    page: 1,
    size: 10,
    total: 0,
    totalPages: 0,
  }
}

async function loadMembers() {
  if (!selectedClassroom.value) return

  try {
    membersLoading.value = true
    const response = await classroomAssistantService.getClassroomMembers(
      selectedClassroom.value.id,
      memberPagination.value.page,
      memberPagination.value.size
    )
    members.value = response.members
    memberPagination.value.total = response.total
    memberPagination.value.totalPages = response.totalPages
  } catch (error: any) {
    console.error('加载成员列表失败:', error)
    toast.error(error.response?.data?.detail || '加载成员列表失败')
  } finally {
    membersLoading.value = false
  }
}

function handleMemberPageChange(page: number) {
  memberPagination.value.page = page
  loadMembers()
}

function handleMemberPageSizeChange(size: number) {
  memberPagination.value.size = size
  memberPagination.value.page = 1
  loadMembers()
}

function getRoleName(role: RoleInClass): string {
  const roleMap: Record<RoleInClass, string> = {
    [RoleInClass.HEAD_TEACHER_PRIMARY]: '正班主任',
    [RoleInClass.HEAD_TEACHER_DEPUTY]: '副班主任',
    [RoleInClass.SUBJECT_TEACHER]: '任课教师',
    [RoleInClass.CADRE]: '班干部',
    [RoleInClass.STUDENT]: '学生',
  }
  return roleMap[role] || role
}

function getRoleTagType(role: RoleInClass): string {
  const typeMap: Record<RoleInClass, string> = {
    [RoleInClass.HEAD_TEACHER_PRIMARY]: 'danger',
    [RoleInClass.HEAD_TEACHER_DEPUTY]: 'warning',
    [RoleInClass.SUBJECT_TEACHER]: 'primary',
    [RoleInClass.CADRE]: 'success',
    [RoleInClass.STUDENT]: 'info',
  }
  return typeMap[role] || ''
}

function openAddMemberModal() {
  if (!selectedClassroom.value) return
  editingMember.value = null
  memberError.value = ''
  userSearchQuery.value = ''
  userRoleFilter.value = ''
  searchedUsers.value = []
  selectedUserInfo.value = null
  batchAddMode.value = false
  sourceClassroomFilter.value = ''
  sourceClassroomStudents.value = []
  selectedStudentIds.value = new Set()
  memberForm.value = {
    classroomId: selectedClassroom.value.id,
    userId: 0,
    roleInClass: RoleInClass.STUDENT,
    studentNo: null,
    seatNo: null,
    cadreTitle: null,
    isPrimaryClass: false,
  }
  showMemberModal.value = true
}

async function searchUsersForMember() {
  if (!userSearchQuery.value && !userRoleFilter.value) {
    searchedUsers.value = []
    return
  }

  try {
    userSearchLoading.value = true
    const response = await adminService.getUsers({
      page: 1,
      size: 20,
      role: userRoleFilter.value || undefined,
      search: userSearchQuery.value || undefined,
    })
    searchedUsers.value = response.users
  } catch (error: any) {
    console.error('搜索用户失败:', error)
    toast.error(error.response?.data?.detail || '搜索用户失败')
  } finally {
    userSearchLoading.value = false
  }
}

function onUserRoleFilterChange() {
  if (userRoleFilter.value === 'student') {
    memberForm.value.roleInClass = RoleInClass.STUDENT
  } else if (userRoleFilter.value === 'teacher') {
    memberForm.value.roleInClass = RoleInClass.SUBJECT_TEACHER
  }
  searchUsersForMember()
}

function selectUserForMember(user: User) {
  memberForm.value.userId = user.id
  selectedUserInfo.value = user
  autoSetRoleFromUser(user)
}

function autoSetRoleFromUser(user: User) {
  if (user.role === 'student') {
    memberForm.value.roleInClass = RoleInClass.STUDENT
  } else if (user.role === 'teacher' || user.role === 'admin' || user.role === 'researcher') {
    memberForm.value.roleInClass = RoleInClass.SUBJECT_TEACHER
  }
}

async function onUserIdInput() {
  const userId = memberForm.value.userId

  if (selectedUserInfo.value && selectedUserInfo.value.id !== userId) {
    selectedUserInfo.value = null
  }

  if (userId && userId > 0 && !selectedUserInfo.value) {
    try {
      const user = await adminService.getUser(userId)
      selectedUserInfo.value = user
      autoSetRoleFromUser(user)
    } catch (error: any) {
      console.debug('获取用户信息失败:', error)
    }
  }
}

function editMember(member: ClassroomMembership) {
  editingMember.value = member
  memberError.value = ''
  memberForm.value = {
    classroomId: member.classroomId,
    userId: member.userId,
    roleInClass: member.roleInClass,
    studentNo: member.studentNo || null,
    seatNo: member.seatNo || null,
    cadreTitle: member.cadreTitle || null,
    isPrimaryClass: member.isPrimaryClass,
  }
  batchAddMode.value = false
  showMemberModal.value = true
}

function closeMemberModal() {
  showMemberModal.value = false
  editingMember.value = null
  memberError.value = ''
  userSearchQuery.value = ''
  userRoleFilter.value = ''
  searchedUsers.value = []
  selectedUserInfo.value = null
  batchAddMode.value = false
  sourceClassroomFilter.value = ''
  sourceClassroomStudents.value = []
  selectedStudentIds.value = new Set()
}

async function saveMember() {
  if (!selectedClassroom.value) return

  try {
    memberSaving.value = true
    memberError.value = ''

    if (editingMember.value) {
      const updateData: ClassroomMembershipUpdate = {
        roleInClass: memberForm.value.roleInClass,
        studentNo: memberForm.value.studentNo || null,
        seatNo: memberForm.value.seatNo || null,
        cadreTitle: memberForm.value.cadreTitle || null,
        isPrimaryClass: memberForm.value.isPrimaryClass,
      }
      await classroomAssistantService.updateClassroomMember(
        selectedClassroom.value.id,
        editingMember.value.userId,
        updateData
      )
      ElMessage.success('成员信息更新成功')
    } else {
      const createData: ClassroomMembershipCreate = {
        classroomId: selectedClassroom.value.id,
        userId: memberForm.value.userId,
        roleInClass: memberForm.value.roleInClass,
        studentNo: memberForm.value.studentNo || null,
        seatNo: memberForm.value.seatNo || null,
        cadreTitle: memberForm.value.cadreTitle || null,
        isPrimaryClass: memberForm.value.isPrimaryClass,
      }
      await classroomAssistantService.addClassroomMember(selectedClassroom.value.id, createData)
      ElMessage.success('成员添加成功')
    }

    closeMemberModal()
    await loadMembers()
  } catch (error: any) {
    console.error('保存成员失败:', error)
    memberError.value = error.response?.data?.detail || error.message || '保存失败，请重试'
  } finally {
    memberSaving.value = false
  }
}

async function loadSourceClassroomStudents() {
  if (!sourceClassroomFilter.value) {
    sourceClassroomStudents.value = []
    selectedStudentIds.value = new Set()
    return
  }

  try {
    sourceStudentsLoading.value = true
    // 获取所有学生（使用大页面大小）
    const sourceMembersResponse = await classroomAssistantService.getClassroomMembers(
      Number(sourceClassroomFilter.value),
      1,
      1000
    )
    let students = sourceMembersResponse.members.filter(m => m.roleInClass === RoleInClass.STUDENT)

    if (selectedClassroom.value) {
      try {
        const currentMembersResponse = await classroomAssistantService.getClassroomMembers(
          selectedClassroom.value.id,
          1,
          1000
        )
        const currentMemberUserIds = new Set(currentMembersResponse.members.filter(m => m.isActive).map(m => m.userId))
        students = students.filter(s => !currentMemberUserIds.has(s.userId))
      } catch (error) {
        console.warn('获取当前班级成员失败:', error)
      }
    }

    sourceClassroomStudents.value = students
    selectedStudentIds.value = new Set()
  } catch (error: any) {
    console.error('加载班级学生失败:', error)
    toast.error(error.response?.data?.detail || '加载班级学生失败')
    sourceClassroomStudents.value = []
  } finally {
    sourceStudentsLoading.value = false
  }
}

function toggleStudentSelection(userId: number) {
  if (selectedStudentIds.value.has(userId)) {
    selectedStudentIds.value.delete(userId)
  } else {
    selectedStudentIds.value.add(userId)
  }
}

function toggleSelectAllStudents() {
  if (selectedStudentIds.value.size === sourceClassroomStudents.value.length) {
    selectedStudentIds.value = new Set()
  } else {
    selectedStudentIds.value = new Set(sourceClassroomStudents.value.map(s => s.userId))
  }
}

async function batchAddMembers() {
  if (!selectedClassroom.value || selectedStudentIds.value.size === 0) return

  try {
    memberSaving.value = true
    memberError.value = ''

    const errors: string[] = []
    let successCount = 0

    for (const userId of selectedStudentIds.value) {
      try {
        const student = sourceClassroomStudents.value.find(s => s.userId === userId)
        if (!student) continue

        const createData: ClassroomMembershipCreate = {
          classroomId: selectedClassroom.value.id,
          userId: userId,
          roleInClass: RoleInClass.STUDENT,
          studentNo: student.studentNo || null,
          seatNo: student.seatNo || null,
          cadreTitle: null,
          isPrimaryClass: false,
        }

        await classroomAssistantService.addClassroomMember(selectedClassroom.value.id, createData)
        successCount++
      } catch (error: any) {
        const studentName = sourceClassroomStudents.value.find(s => s.userId === userId)?.userFullName || `ID: ${userId}`
        const errorMsg = error.response?.data?.detail || '添加失败'
        errors.push(`${studentName}: ${errorMsg}`)
        console.error(`添加成员失败 (userId: ${userId}):`, error)
      }
    }

    if (successCount > 0) {
      ElMessage.success(`成功添加 ${successCount} 个成员${errors.length > 0 ? `，${errors.length} 个失败` : ''}`)
    }

    if (errors.length > 0 && successCount === 0) {
      memberError.value = errors.join('\n')
      ElMessage.error('批量添加失败')
    }

    if (successCount > 0) {
      closeMemberModal()
      await loadMembers()
    }
  } catch (error: any) {
    console.error('批量添加成员失败:', error)
    memberError.value = error.response?.data?.detail || '批量添加失败'
    ElMessage.error(error.response?.data?.detail || '批量添加失败')
  } finally {
    memberSaving.value = false
  }
}

async function removeMember(member: ClassroomMembership) {
  if (!selectedClassroom.value) return

  try {
    await ElMessageBox.confirm(
      `确定要移除用户 ${member.userFullName || member.userName || `ID: ${member.userId}`} 吗？`,
      '确认移除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await classroomAssistantService.removeClassroomMember(selectedClassroom.value.id, member.userId)
    ElMessage.success('成员移除成功')
    await loadMembers()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('移除成员失败:', error)
      ElMessage.error(error.response?.data?.detail || error.message || '移除失败，请重试')
    }
  }
}

// ==================== 初始化 ====================
onMounted(async () => {
  await Promise.all([
    loadAllRegions(),
    loadSchoolTypes(),
    loadGradesList(),
    loadAllClassrooms(),
  ])
})

// 监听成员管理对话框关闭
watch(showMemberManager, (newValue) => {
  if (!newValue) {
    closeMemberManager()
  }
})
</script>

<style scoped>
.space-y-6 > * + * {
  margin-top: 1.5rem;
}
</style>
