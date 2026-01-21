<template>
  <div class="space-y-6">
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
            @click="openSchoolImportDialog"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            📥 批量导入学校
          </button>
          <button
            @click="openDistrictClassroomImportDialog"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            📥 批量导入班级
          </button>
        </div>
        <div class="flex gap-2 items-center">
          <select v-model="schoolRegionFilter" @change="handleSchoolRegionFilterChange" class="px-3 py-2 border rounded-lg">
            <option value="">所有县区</option>
            <option v-for="region in allRegions" :key="region.id" :value="region.id">
              {{ region.name }}
            </option>
          </select>
          <select v-model="schoolTypeFilter" @change="handleSchoolTypeFilterChange" class="px-3 py-2 border rounded-lg">
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
          <button
            @click="loadSchools"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 whitespace-nowrap"
          >
            🔄 刷新
          </button>
        </div>
      </div>
    </div>

    <!-- 批量操作栏 -->
    <div v-if="hasSelection" class="bg-blue-50 border border-blue-200 rounded-lg shadow p-4">
      <div class="flex justify-between items-center">
        <div class="text-sm text-blue-800">
          <strong>已选择 {{ selectedCount }} 所学校</strong>
        </div>
        <div class="flex gap-2">
          <button
            @click="openBatchDeleteDialog"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2"
          >
            🗑️ 批量删除
          </button>
          <button
            @click="clearSelection"
            class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
          >
            取消选择
          </button>
        </div>
      </div>
    </div>

    <!-- 学校列表 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left w-12">
              <input
                type="checkbox"
                :checked="isAllCurrentPageSelected"
                :indeterminate="isIndeterminate"
                @change="toggleSelectAll($event.target.checked)"
                class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
              />
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">学校名称</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">编码</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">类型</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">校长</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="school in schools" :key="school.id"
              :class="['hover:bg-gray-50', isSelected(school.id) ? 'bg-blue-50' : '']">
            <td class="px-4 py-4 whitespace-nowrap">
              <input
                type="checkbox"
                :checked="isSelected(school.id)"
                @change="toggleSelectSchool(school.id)"
                class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
              />
            </td>
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

    <!-- 创建/编辑学校对话框 -->
    <el-dialog
      v-model="showSchoolModal"
      :title="editingSchool ? '编辑学校' : '创建学校'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="schoolForm" label-width="120px">
        <el-form-item label="学校名称" required>
          <el-input v-model="schoolForm.name" placeholder="请输入学校名称" />
        </el-form-item>
        <el-form-item label="学校编码" required>
          <el-input v-model="schoolForm.code" placeholder="请输入学校编码" />
        </el-form-item>
        <el-form-item label="学校类型">
          <el-select v-model="schoolForm.school_type" placeholder="请选择学校类型" class="w-full">
            <el-option label="小学" value="小学" />
            <el-option label="初中" value="初中" />
            <el-option label="高中" value="高中" />
            <el-option label="大学" value="大学" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属区域" required>
          <el-select v-model="schoolForm.region_id" placeholder="请选择区域" filterable class="w-full">
            <el-option
              v-for="region in allRegions"
              :key="region.id"
              :label="region.name"
              :value="region.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="学校地址">
          <el-input v-model="schoolForm.address" placeholder="请输入学校地址" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="schoolForm.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="schoolForm.email" type="email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="校长姓名">
          <el-input v-model="schoolForm.principal" placeholder="请输入校长姓名" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="schoolForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="schoolForm.is_active" active-text="激活" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeSchoolModal">取消</el-button>
        <el-button type="primary" @click="saveSchool">保存</el-button>
      </template>
    </el-dialog>

    <!-- 学校批量导入对话框 -->
    <el-dialog
      v-model="showSchoolImportDialog"
      title="批量导入学校"
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
            <li>请先下载Excel模板，按照模板格式填写学校信息</li>
            <li>必需字段：区域名称、学校名称</li>
            <li>可选字段：学校代码、学校类型、地址、联系电话、邮箱、校长</li>
            <li>支持格式：.xlsx, .xls</li>
          </ul>
        </div>
        <div class="bg-gray-50 border rounded-lg p-4">
          <h4 class="text-sm font-medium mb-2">模板字段说明</h4>
          <el-table :data="templateFields" border size="small">
            <el-table-column prop="field" label="字段名" width="120" />
            <el-table-column prop="required" label="是否必填" width="100" />
            <el-table-column prop="description" label="说明" />
            <el-table-column prop="example" label="示例" width="150" />
          </el-table>
        </div>
        <div class="flex justify-center gap-4">
          <el-button type="primary" @click="downloadSchoolTemplate" :icon="Download">
            下载Excel模板
          </el-button>
          <el-button @click="importStep = 1">
            已有模板，下一步
            <el-icon class="ml-2"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 步骤2: 上传文件 -->
      <div v-if="importStep === 1" class="space-y-4">
        <el-form :model="importForm" label-width="120px">
          <el-form-item label="自动创建区域">
            <el-switch
              v-model="importForm.autoCreateRegion"
              active-text="是"
              inactive-text="否"
            />
            <span class="ml-2 text-sm text-gray-500">如果区域不存在，是否自动创建</span>
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
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
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
            <el-icon><ArrowLeft /></el-icon>
            上一步
          </el-button>
          <el-button
            type="primary"
            @click="startSchoolImport"
            :loading="importing"
            :disabled="!selectedFile"
          >
            <el-icon><Upload /></el-icon>
            <span class="ml-2">开始导入</span>
          </el-button>
        </div>
      </div>

      <!-- 步骤3: 导入结果 -->
      <div v-if="importStep === 2" class="space-y-4">
        <el-alert
          :title="importResult.success > 0 ? '✅ 导入完成' : '❌ 导入失败'"
          :type="importResult.success > 0 ? 'success' : 'error'"
          :closable="false"
        />
        <div v-if="importResult.total > 0">
          <h4 class="text-sm font-medium mb-2">📊 导入统计</h4>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="总记录数" :value="importResult.total" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="成功" :value="importResult.success" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="失败" :value="importResult.failed" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="创建学校" :value="importResult.created_schools" />
            </el-col>
          </el-row>
          <el-row :gutter="20" class="mt-4">
            <el-col :span="6">
              <el-statistic title="创建区域" :value="importResult.created_regions" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="更新学校" :value="importResult.updated_schools" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="跳过" :value="importResult.skipped_schools" />
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
        <el-button v-if="importStep < 2" @click="showSchoolImportDialog = false">取消</el-button>
        <el-button v-if="importStep === 2" type="primary" @click="closeSchoolImportDialog">完成</el-button>
      </template>
    </el-dialog>

    <!-- 县区端批量导入班级对话框 -->
    <el-dialog
      v-model="showDistrictClassroomImportDialog"
      title="批量导入班级（支持多个学校）"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-steps :active="districtClassroomImportStep" finish-status="success" align-center class="mb-6">
        <el-step title="下载模板" />
        <el-step title="上传文件" />
        <el-step title="导入结果" />
      </el-steps>

      <!-- 步骤1: 下载模板 -->
      <div v-if="districtClassroomImportStep === 0" class="space-y-4">
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
          <el-table :data="districtClassroomTemplateFields" border size="small">
            <el-table-column prop="field" label="字段名" width="120" />
            <el-table-column prop="required" label="是否必填" width="100" />
            <el-table-column prop="description" label="说明" />
            <el-table-column prop="example" label="示例" width="150" />
          </el-table>
        </div>
        <div class="flex justify-center gap-4">
          <el-button type="primary" @click="downloadDistrictClassroomTemplate" :icon="Download">
            下载Excel模板
          </el-button>
          <el-button @click="districtClassroomImportStep = 1">
            已有模板，下一步
            <el-icon class="ml-2"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 步骤2: 上传文件 -->
      <div v-if="districtClassroomImportStep === 1" class="space-y-4">
        <el-form :model="districtClassroomImportForm" label-width="140px">
          <el-form-item label="统一设置入学年份">
            <el-input-number
              v-model="districtClassroomImportForm.enrollmentYear"
              :min="1900"
              :max="2100"
              placeholder="留空则使用Excel中的值"
              style="width: 200px;"
            />
            <span class="ml-2 text-sm text-gray-500">如果设置，将覆盖Excel中的所有入学年份</span>
          </el-form-item>
          <el-form-item label="统一设置班级容量">
            <el-input-number
              v-model="districtClassroomImportForm.capacity"
              :min="1"
              :max="200"
              placeholder="留空则使用Excel中的值"
              style="width: 200px;"
            />
            <span class="ml-2 text-sm text-gray-500">如果设置，将覆盖Excel中的所有班级容量</span>
          </el-form-item>
          <el-form-item label="更新已存在班级">
            <el-switch
              v-model="districtClassroomImportForm.updateExisting"
              active-text="是"
              inactive-text="否"
            />
            <span class="ml-2 text-sm text-gray-500">如果班级已存在，是否更新</span>
          </el-form-item>
        </el-form>
        <el-upload
          ref="districtClassroomUploadRef"
          class="upload-demo"
          drag
          :auto-upload="false"
          :limit="1"
          :on-change="handleDistrictClassroomFileChange"
          :on-exceed="handleDistrictClassroomExceed"
          accept=".xlsx,.xls"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
          <template #tip>
            <div class="el-upload__tip">只能上传 xlsx/xls 文件，且不超过 10MB</div>
          </template>
        </el-upload>
        <div v-if="selectedDistrictClassroomFile" class="mt-4 p-3 bg-gray-50 rounded-lg">
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="文件名">{{ selectedDistrictClassroomFile.name }}</el-descriptions-item>
            <el-descriptions-item label="文件大小">{{ formatFileSize(selectedDistrictClassroomFile.size) }}</el-descriptions-item>
          </el-descriptions>
        </div>
        <div class="flex justify-center gap-4">
          <el-button @click="districtClassroomImportStep = 0">
            <el-icon><ArrowLeft /></el-icon>
            上一步
          </el-button>
          <el-button
            type="primary"
            @click="startDistrictClassroomImport"
            :loading="districtClassroomImporting"
            :disabled="!selectedDistrictClassroomFile"
          >
            <el-icon><Upload /></el-icon>
            <span class="ml-2">开始导入</span>
          </el-button>
        </div>
      </div>

      <!-- 步骤3: 导入结果 -->
      <div v-if="districtClassroomImportStep === 2" class="space-y-4">
        <el-alert
          :title="districtClassroomImportResult.success > 0 ? '✅ 导入完成' : '❌ 导入失败'"
          :type="districtClassroomImportResult.success > 0 ? 'success' : 'error'"
          :closable="false"
        />
        <div v-if="districtClassroomImportResult.total > 0">
          <h4 class="text-sm font-medium mb-2">📊 导入统计</h4>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="总记录数" :value="districtClassroomImportResult.total" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="成功" :value="districtClassroomImportResult.success" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="失败" :value="districtClassroomImportResult.failed" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="创建" :value="districtClassroomImportResult.created" />
            </el-col>
          </el-row>
          <el-row :gutter="20" class="mt-4">
            <el-col :span="6">
              <el-statistic title="更新" :value="districtClassroomImportResult.updated" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="跳过" :value="districtClassroomImportResult.skipped" />
            </el-col>
          </el-row>
          <div v-if="districtClassroomImportResult.errors && districtClassroomImportResult.errors.length > 0" class="mt-4">
            <h4 class="text-sm font-medium mb-2">⚠️ 错误详情</h4>
            <el-table :data="districtClassroomImportResult.errors" max-height="300" size="small">
              <el-table-column prop="row" label="行号" width="80" />
              <el-table-column prop="field" label="字段" width="120" />
              <el-table-column prop="message" label="错误信息" />
            </el-table>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button v-if="districtClassroomImportStep < 2" @click="showDistrictClassroomImportDialog = false">取消</el-button>
        <el-button v-if="districtClassroomImportStep === 2" type="primary" @click="closeDistrictClassroomImportDialog">完成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, UploadFilled, Upload, ArrowRight, ArrowLeft } from '@element-plus/icons-vue'
import type { UploadProps } from 'element-plus'
import * as XLSX from 'xlsx'
import { useToast } from '@/composables/useToast'
import adminService, { type Region, type School, type SchoolImportResponse, type ClassroomImportResponse, type SchoolRelationCheck, type BatchDeleteSchoolsResponse } from '@/services/admin'

const toast = useToast()

// 学校管理状态
const schools = ref<School[]>([])
const schoolPage = ref(1)
const schoolPageSize = ref(10)
const schoolTotal = ref(0)
const schoolRegionFilter = ref<number | ''>('')
const schoolTypeFilter = ref('')
const schoolSearchQuery = ref('')
const showSchoolModal = ref(false)
const editingSchool = ref<School | null>(null)
const allRegions = ref<Region[]>([])
const schoolForm = ref({
  name: '',
  code: '',
  region_id: '' as number | '',
  school_type: '小学',
  address: '',
  phone: '',
  email: '',
  principal: '',
  description: '',
  is_active: true
})

const schoolTotalPages = computed(() => Math.ceil(schoolTotal.value / schoolPageSize.value))

const selectedCount = computed(() => selectedSchoolIds.value.size)

const hasSelection = computed(() => selectedSchoolIds.value.size > 0)

const canSelectAllCurrentPage = computed(() => {
  return schools.value.length > 0 && schools.value.every(school => selectedSchoolIds.value.has(school.id))
})

// 学校批量导入状态
const showSchoolImportDialog = ref(false)
const importStep = ref(0)
const selectedFile = ref<File | null>(null)
const uploadRef = ref<any>(null)
const importing = ref(false)
const importForm = ref({
  autoCreateRegion: true
})
const importResult = ref<SchoolImportResponse>({
  total: 0,
  success: 0,
  failed: 0,
  created_regions: 0,
  created_schools: 0,
  updated_schools: 0,
  skipped_schools: 0,
  errors: []
})
const templateFields = [
  { field: '区域名称', required: '✅ 必填', description: '市或区名称，如：北京市、朝阳区', example: '北京市' },
  { field: '学校名称', required: '✅ 必填', description: '学校全称', example: '北京市第一中学' },
  { field: '学校代码', required: '⭕ 选填', description: '学校代码，用于精确匹配', example: '10001' },
  { field: '学校类型', required: '⭕ 选填', description: '小学/初中/高中/大学', example: '高中' },
  { field: '地址', required: '⭕ 选填', description: '学校地址', example: '北京市XX区XX路' },
  { field: '联系电话', required: '⭕ 选填', description: '联系电话', example: '010-12345678' },
  { field: '邮箱', required: '⭕ 选填', description: '邮箱地址', example: 'school@example.com' },
  { field: '校长', required: '⭕ 选填', description: '校长姓名', example: '张校长' },
]

// 县区端班级批量导入状态
const showDistrictClassroomImportDialog = ref(false)
const districtClassroomImportStep = ref(0)
const selectedDistrictClassroomFile = ref<File | null>(null)
const districtClassroomUploadRef = ref<any>(null)
const districtClassroomImporting = ref(false)
const districtClassroomImportForm = ref({
  enrollmentYear: undefined as number | undefined,
  capacity: undefined as number | undefined,
  updateExisting: false
})
const districtClassroomImportResult = ref<ClassroomImportResponse>({
  total: 0,
  success: 0,
  failed: 0,
  created: 0,
  updated: 0,
  skipped: 0,
  errors: []
})
const districtClassroomTemplateFields = [
  { field: '学校名称', required: '✅ 必填', description: '学校全称（用于匹配学校）', example: '开平市第一中学' },
  { field: '学校代码', required: '⭕ 选填', description: '学校代码（用于精确匹配，优先于学校名称）', example: '10001' },
  { field: '年级级别', required: '✅ 必填', description: '年级级别1-12（如：7表示七年级，10表示高一）', example: '7' },
  { field: '年级名称', required: '⭕ 选填', description: '年级名称（如不填写，将根据年级级别自动获取）', example: '七年级' },
  { field: '班级编号', required: '✅ 必填', description: '班级编码（唯一标识，如：701表示7年级1班）', example: '701' },
  { field: '班级名称', required: '⭕ 选填', description: '班级名称（如不填写，将根据班级编号和年级名称自动生成）', example: '七年级1班' },
  { field: '入学年份', required: '⭕ 选填', description: '入学年份/届别（可在导入界面统一设置）', example: '2024' },
  { field: '班级容量', required: '⭕ 选填', description: '计划人数（可在导入界面统一设置）', example: '45' },
  { field: '班级描述', required: '⭕ 选填', description: '班级描述信息', example: '重点班' },
]

// 批量选择状态
const selectedSchoolIds = ref<Set<number>>(new Set())
const isAllCurrentPageSelected = ref(false)
const isIndeterminate = ref(false)
const showBatchDeleteDialog = ref(false)
const checkingRelations = ref(false)
const deletingSchools = ref(false)
const schoolRelations = ref<SchoolRelationCheck[]>([])
const batchDeleteResult = ref<BatchDeleteSchoolsResponse | null>(null)
const cascadeDelete = ref(false)

// 方法
async function loadAllRegions() {
  try {
    const response = await adminService.getRegions({ size: 1000 })
    allRegions.value = response.regions
  } catch (error: any) {
    console.error('Failed to load all regions:', error)
  }
}

async function loadSchools() {
  try {
    const response = await adminService.getSchools({
      page: schoolPage.value,
      size: schoolPageSize.value,
      region_id: schoolRegionFilter.value || undefined,
      school_type: schoolTypeFilter.value || undefined,
      search: schoolSearchQuery.value || undefined
    })
    schools.value = response.schools
    schoolTotal.value = response.total
    updateSelectAllState()
  } catch (error: any) {
    console.error('Failed to load schools:', error)
    toast.error(error.response?.data?.detail || '加载学校列表失败')
  }
}

function searchSchools() {
  schoolPage.value = 1
  loadSchools()
}

function handleSchoolRegionFilterChange() {
  schoolPage.value = 1
  loadSchools()
}

function handleSchoolTypeFilterChange() {
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
  await loadAllRegions()
  showSchoolModal.value = true
}

async function editSchool(school: School) {
  editingSchool.value = school
  schoolForm.value = {
    name: school.name,
    code: school.code,
    region_id: school.region_id,
    school_type: school.school_type,
    address: school.address || '',
    phone: school.phone || '',
    email: school.email || '',
    principal: school.principal || '',
    description: school.description || '',
    is_active: school.is_active
  }
  await loadAllRegions()
  showSchoolModal.value = true
}

function closeSchoolModal() {
  showSchoolModal.value = false
  editingSchool.value = null
}

async function saveSchool() {
  if (!schoolForm.value.name || !schoolForm.value.code || !schoolForm.value.region_id) {
    ElMessage.warning('请填写所有必填字段')
    return
  }

  try {
    const formData = {
      ...schoolForm.value,
      region_id: typeof schoolForm.value.region_id === 'string' ? parseInt(schoolForm.value.region_id) : schoolForm.value.region_id
    }
    
    if (editingSchool.value) {
      await adminService.updateSchool(editingSchool.value.id, formData)
      ElMessage.success('学校更新成功')
    } else {
      await adminService.createSchool(formData)
      ElMessage.success('学校创建成功')
    }
    closeSchoolModal()
    loadSchools()
  } catch (error: any) {
    console.error('Failed to save school:', error)
    ElMessage.error(error.response?.data?.detail || '保存学校失败')
  }
}

async function deleteSchool(school: School) {
  try {
    await ElMessageBox.confirm(
      `确定要删除学校 ${school.name} 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await adminService.deleteSchool(school.id)
    ElMessage.success('学校删除成功')
    loadSchools()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to delete school:', error)
      ElMessage.error(error.response?.data?.detail || '删除学校失败')
    }
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

// 学校批量导入方法
function openSchoolImportDialog() {
  showSchoolImportDialog.value = true
  importStep.value = 0
  selectedFile.value = null
  importForm.value = { autoCreateRegion: true }
  importResult.value = {
    total: 0,
    success: 0,
    failed: 0,
    created_regions: 0,
    created_schools: 0,
    updated_schools: 0,
    skipped_schools: 0,
    errors: []
  }
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

function closeSchoolImportDialog() {
  showSchoolImportDialog.value = false
  importStep.value = 0
  selectedFile.value = null
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
  loadSchools()
}

function downloadSchoolTemplate() {
  const template = [
    ['区域名称*', '学校名称*', '学校代码', '学校类型', '地址', '联系电话', '邮箱', '校长'],
    ['开平市', '开平市第一中学', '10001', '高中', '开平市XX区XX路', '010-12345678', 'school1@example.com', '张校长'],
    ['开平市', '开平市第二小学', '10002', '小学', '开平市XX区XX街', '010-87654321', 'school2@example.com', '李校长'],
  ]

  const ws = XLSX.utils.aoa_to_sheet(template)
  const colWidths = [
    { wch: 15 }, { wch: 20 }, { wch: 12 }, { wch: 12 },
    { wch: 25 }, { wch: 15 }, { wch: 25 }, { wch: 12 }
  ]
  ws['!cols'] = colWidths

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '学校信息')
  XLSX.writeFile(wb, '学校信息导入模板.xlsx')
  ElMessage.success('模板下载成功')
}

const handleFileChange: UploadProps['onChange'] = (uploadFile) => {
  selectedFile.value = uploadFile.raw || null
}

const handleExceed: UploadProps['onExceed'] = () => {
  ElMessage.warning('只能上传一个文件')
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

async function startSchoolImport() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  importing.value = true

  try {
    const result = await adminService.importSchools(
      selectedFile.value,
      importForm.value.autoCreateRegion
    )

    importResult.value = result
    importStep.value = 2

    if (result.success > 0) {
      ElMessage.success(`导入完成！成功 ${result.success} 条，失败 ${result.failed} 条`)
    } else {
      ElMessage.error(`导入失败：${result.errors.length > 0 ? result.errors[0].message : '未知错误'}`)
    }
  } catch (error: any) {
    console.error('导入失败:', error)
    ElMessage.error(error.response?.data?.detail || '导入失败')
    importResult.value = {
      total: 0,
      success: 0,
      failed: 1,
      created_regions: 0,
      created_schools: 0,
      updated_schools: 0,
      skipped_schools: 0,
      errors: [{
        row: 0,
        field: null,
        message: error.response?.data?.detail || '导入失败'
      }]
    }
    importStep.value = 2
  } finally {
    importing.value = false
  }
}

// 县区端班级批量导入方法
function openDistrictClassroomImportDialog() {
  showDistrictClassroomImportDialog.value = true
  districtClassroomImportStep.value = 0
  selectedDistrictClassroomFile.value = null
  districtClassroomImportForm.value = {
    enrollmentYear: undefined,
    capacity: undefined,
    updateExisting: false
  }
  districtClassroomImportResult.value = {
    total: 0,
    success: 0,
    failed: 0,
    created: 0,
    updated: 0,
    skipped: 0,
    errors: []
  }
  if (districtClassroomUploadRef.value) {
    districtClassroomUploadRef.value.clearFiles()
  }
}

function closeDistrictClassroomImportDialog() {
  showDistrictClassroomImportDialog.value = false
  districtClassroomImportStep.value = 0
  selectedDistrictClassroomFile.value = null
  if (districtClassroomUploadRef.value) {
    districtClassroomUploadRef.value.clearFiles()
  }
  loadSchools()
}

function downloadDistrictClassroomTemplate() {
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
  XLSX.writeFile(wb, '班级信息导入模板（县区端）.xlsx')
  ElMessage.success('模板下载成功')
}

const handleDistrictClassroomFileChange: UploadProps['onChange'] = (uploadFile) => {
  selectedDistrictClassroomFile.value = uploadFile.raw || null
}

const handleDistrictClassroomExceed: UploadProps['onExceed'] = () => {
  ElMessage.warning('只能上传一个文件')
}

async function startDistrictClassroomImport() {
  if (!selectedDistrictClassroomFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  districtClassroomImporting.value = true

  try {
    const result = await adminService.importClassrooms(
      selectedDistrictClassroomFile.value,
      undefined, // school_id（县区端不需要，从Excel中读取）
      undefined, // region_id（可选）
      districtClassroomImportForm.value.updateExisting,
      districtClassroomImportForm.value.enrollmentYear,
      districtClassroomImportForm.value.capacity
    )

    districtClassroomImportResult.value = result
    districtClassroomImportStep.value = 2

    if (result.success > 0) {
      ElMessage.success(`导入完成！成功 ${result.success} 条，失败 ${result.failed} 条`)
    } else {
      ElMessage.error(`导入失败：${result.errors.length > 0 ? result.errors[0].message : '未知错误'}`)
    }
  } catch (error: any) {
    console.error('导入失败:', error)
    ElMessage.error(error.response?.data?.detail || '导入失败')
    districtClassroomImportResult.value = {
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
    districtClassroomImportStep.value = 2
  } finally {
    districtClassroomImporting.value = false
  }
}

// 选择逻辑方法
function toggleSelectAll(checked: boolean) {
  if (checked) {
    // 选择当前页所有学校
    schools.value.forEach(school => {
      selectedSchoolIds.value.add(school.id)
    })
  } else {
    // 取消选择当前页所有学校
    schools.value.forEach(school => {
      selectedSchoolIds.value.delete(school.id)
    })
  }
  updateSelectAllState()
}

function toggleSelectSchool(schoolId: number) {
  if (selectedSchoolIds.value.has(schoolId)) {
    selectedSchoolIds.value.delete(schoolId)
  } else {
    selectedSchoolIds.value.add(schoolId)
  }
  updateSelectAllState()
}

function isSelected(schoolId: number): boolean {
  return selectedSchoolIds.value.has(schoolId)
}

function clearSelection() {
  selectedSchoolIds.value.clear()
  updateSelectAllState()
}

function updateSelectAllState() {
  const currentSchoolIds = schools.value.map(s => s.id)
  const selectedInCurrentPage = currentSchoolIds.filter(id => selectedSchoolIds.value.has(id))

  if (selectedInCurrentPage.length === 0) {
    isAllCurrentPageSelected.value = false
    isIndeterminate.value = false
  } else if (selectedInCurrentPage.length === schools.value.length) {
    isAllCurrentPageSelected.value = true
    isIndeterminate.value = false
  } else {
    isAllCurrentPageSelected.value = false
    isIndeterminate.value = true
  }
}

// 初始化
onMounted(async () => {
  await Promise.all([
    loadAllRegions(),
    loadSchools(),
  ])
})
</script>

<style scoped>
.space-y-6 > * + * {
  margin-top: 1.5rem;
}
</style>
