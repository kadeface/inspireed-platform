<template>
  <div class="space-y-6">
    <!-- 功能说明 -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <p class="text-sm text-blue-800">
        💡 <strong>功能说明：</strong>管理学生档案信息，包括基本信息、所属班级、学籍号等。支持批量导入学生。
      </p>
    </div>

    <!-- 筛选和操作栏 -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex flex-wrap items-center gap-4 mb-4">
        <!-- 筛选器 -->
        <select
          v-model="filters.region_id"
          @change="handleRegionChange"
          class="px-3 py-2 border rounded-lg"
        >
          <option :value="undefined">所有区域</option>
          <option v-for="region in allRegions" :key="region.id" :value="region.id">
            {{ region.name }}
          </option>
        </select>

        <select
          v-model="filters.school_id"
          @change="handleSchoolChange"
          class="px-3 py-2 border rounded-lg"
        >
          <option :value="undefined">所有学校</option>
          <option v-for="school in filteredSchools" :key="school.id" :value="school.id">
            {{ school.name }}
          </option>
        </select>

        <select
          v-model="filters.grade_id"
          @change="() => loadStudents()"
          class="px-3 py-2 border rounded-lg"
        >
          <option :value="undefined">所有年级</option>
          <option v-for="grade in grades" :key="grade.id" :value="grade.id">
            {{ grade.name }}
          </option>
        </select>

        <select
          v-model="filters.classroom_id"
          @change="() => loadStudents()"
          class="px-3 py-2 border rounded-lg"
        >
          <option :value="undefined">所有班级</option>
          <option v-for="classroom in filteredClassrooms" :key="classroom.id" :value="classroom.id">
            {{ classroom.name }}
          </option>
        </select>

        <input
          v-model="filters.search"
          @input="debouncedLoadStudents"
          type="text"
          placeholder="搜索姓名、学号、学籍号..."
          class="px-3 py-2 border rounded-lg w-64"
        />

        <div class="ml-auto flex gap-2">
          <button
            @click="openCreateStudentModal"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            + 添加学生
          </button>
          <button
            @click="openImportDialog"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            📥 批量导入
          </button>
          <button
            @click="openBatchDeleteByFilterDialog"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            🗑️ 批量删除（按年级/班级）
          </button>
          <button
            @click="() => loadStudents()"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 whitespace-nowrap"
          >
            🔄 刷新
          </button>
        </div>
      </div>
    </div>

    <!-- 批量选择工具栏 -->
    <div v-if="selectedStudents.length > 0" class="bg-blue-50 border-b border-blue-200 px-6 py-3 flex items-center justify-between">
      <div class="text-sm text-blue-800">
        已选择 <span class="font-bold">{{ selectedStudents.length }}</span> 位学生
      </div>
      <div class="flex gap-2">
        <button
          @click="openBatchDeleteWithSelected"
          class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
        >
          批量删除
        </button>
        <button
          @click="clearSelection"
          class="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 text-sm"
        >
          取消选择
        </button>
      </div>
    </div>

    <!-- 学生列表 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase w-12">
              <input
                type="checkbox"
                :checked="isAllSelected"
                :indeterminate="isSomeSelected"
                @change="toggleSelectAll"
                class="h-4 w-4 text-blue-600 rounded"
              />
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">姓名</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">用户名</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">学号</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">学籍号</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">邮箱</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">所属班级</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">最后登录</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-if="loading">
            <td :colspan="11" class="px-6 py-4 text-center text-gray-500">
              加载中...
            </td>
          </tr>
          <tr v-else-if="students.length === 0">
            <td :colspan="11" class="px-6 py-4 text-center text-gray-500">
              暂无学生数据
            </td>
          </tr>
          <tr v-else v-for="student in students" :key="student.id" :class="{ 'bg-blue-50': selectedStudents.includes(student.id) }">
            <td class="px-6 py-4 whitespace-nowrap">
              <input
                type="checkbox"
                :checked="selectedStudents.includes(student.id)"
                @change="toggleStudentSelection(student.id)"
                class="h-4 w-4 text-blue-600 rounded"
              />
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ student.id }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              {{ student.full_name || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ student.username }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ student.username }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ student.student_id_number || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ student.email }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ student.classroom_name || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span v-if="student.is_active" class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                激活
              </span>
              <span v-else class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                停用
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ student.last_login ? formatDate(student.last_login) : '从未登录' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
              <button
                @click="editStudent(student)"
                class="text-blue-600 hover:text-blue-900"
              >
                编辑
              </button>
              <button
                @click="toggleStudentStatus(student)"
                :class="student.is_active ? 'text-orange-600 hover:text-orange-900' : 'text-green-600 hover:text-green-900'"
              >
                {{ student.is_active ? '停用' : '激活' }}
              </button>
              <button
                @click="resetPassword(student)"
                class="text-purple-600 hover:text-purple-900"
              >
                重置密码
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <div class="bg-white px-4 py-3 border-t border-gray-200 flex items-center justify-between">
        <div class="text-sm text-gray-700">
          共 {{ total }} 位学生
        </div>
        <div class="flex gap-2">
          <button
            @click="currentPage > 1 && loadStudents(currentPage - 1)"
            :disabled="currentPage <= 1"
            class="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
          >
            上一页
          </button>
          <span class="px-3 py-1 text-gray-600">
            第 {{ currentPage }} 页
          </span>
          <button
            @click="currentPage * pageSize < total && loadStudents(currentPage + 1)"
            :disabled="currentPage * pageSize >= total"
            class="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑学生对话框 -->
    <el-dialog
      v-model="showStudentModal"
      :title="editingStudent ? '编辑学生' : '添加学生'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="studentForm" label-width="100px">
        <el-form-item label="姓名">
          <el-input v-model="studentForm.full_name" placeholder="请输入学生姓名" />
        </el-form-item>
        <el-form-item label="学号">
          <el-input v-model="studentForm.username" placeholder="请输入学号" />
        </el-form-item>
        <el-form-item label="学籍号">
          <el-input v-model="studentForm.student_id_number" placeholder="请输入学籍号（身份证号等）" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="studentForm.email" type="email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item v-if="!editingStudent" label="密码">
          <el-input v-model="studentForm.password" type="password" placeholder="请输入初始密码" />
        </el-form-item>
        <el-form-item label="所属学校">
          <el-select v-model="studentForm.school_id" @change="handleFormSchoolChange" placeholder="输入学校名称搜索或选择学校" class="w-full" filterable>
            <el-option
              v-for="school in filteredSchools"
              :key="school.id"
              :label="school.name"
              :value="school.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="年级">
          <el-select v-model="studentForm.grade_id" @change="handleFormGradeChange" placeholder="请选择年级" class="w-full" :disabled="!studentForm.school_id">
            <el-option
              v-for="grade in grades"
              :key="grade.id"
              :label="grade.name"
              :value="grade.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="班级">
          <el-select v-model="studentForm.classroom_id" placeholder="请选择班级" class="w-full" :disabled="!studentForm.school_id || !studentForm.grade_id">
            <el-option
              v-for="classroom in formClassrooms"
              :key="classroom.id"
              :label="classroom.name"
              :value="classroom.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="学生类型">
          <el-select v-model="studentForm.student_type" placeholder="请选择学生类型" class="w-full">
            <el-option label="未分科" value="none" />
            <el-option label="文科" value="arts" />
            <el-option label="理科" value="science" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="studentForm.is_active" active-text="激活" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showStudentModal = false">取消</el-button>
        <el-button type="primary" @click="saveStudent" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="批量导入学生"
      width="800px"
    >
      <div class="space-y-4">
        <el-alert
          title="导入说明"
          type="info"
          :closable="false"
          show-icon
        >
          <p>请按照模板格式填写学生信息。支持导入的字段：学号、姓名、学籍号、邮箱、学校名称、学校代码、年级级别、班级编号。</p>
          <p class="mt-2 text-sm text-gray-600">
            <strong>注意：</strong>
            <br>- 学校名称*：学生所属学校（必填）
            <br>- 学校代码：学校编码（可选，用于辅助验证）
            <br>- 年级级别使用数字（1-12），如：7表示七年级，10表示高一
            <br>- 班级编号格式：年级+班级序号，如：701表示七年级1班，1001表示高一1班
            <br>- 学生必须指定学籍号，作为唯一标识
          </p>
        </el-alert>

        <el-button type="primary" @click="downloadTemplate">
          📥 下载导入模板
        </el-button>

        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          accept=".xlsx,.xls"
          :on-change="handleFileChange"
          drag
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              只支持 .xlsx 或 .xls 格式的 Excel 文件
            </div>
          </template>
        </el-upload>

        <div v-if="importPreview.length > 0" class="border rounded p-4">
          <h4 class="font-medium mb-2">导入预览（共 {{ importPreview.length }} 条）</h4>
          <el-table :data="importPreview" max-height="300" size="small">
            <el-table-column prop="学号*" label="学号" width="120" />
            <el-table-column prop="姓名*" label="姓名" width="100" />
            <el-table-column prop="学籍号*" label="学籍号" width="150" />
            <el-table-column prop="邮箱" label="邮箱" width="150" />
            <el-table-column prop="学校名称*" label="学校名称" width="120" />
            <el-table-column prop="学校代码" label="学校代码" width="100" />
            <el-table-column prop="年级级别*" label="年级" width="80" />
            <el-table-column prop="班级编号*" label="班级编号" width="100" />
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="startImport" :loading="importing">
          开始导入
        </el-button>
      </template>
    </el-dialog>

    <!-- 批量删除对话框（支持按选中学生或按条件删除） -->
    <el-dialog
      v-model="showBatchDeleteByFilterDialog"
      :title="batchDeleteMode === 'selected' ? '批量删除选中学生' : '批量删除学生（按年级/班级）'"
      width="700px"
    >
      <div class="space-y-4">
        <el-alert
          title="危险操作"
          type="error"
          :closable="false"
          show-icon
        >
          <p>此操作将批量删除学生及其相关数据，不可撤销！</p>
          <p class="mt-2 text-sm">
            将同时删除：
            <br>- 考号映射记录
            <br>- 考场安排记录
            <br>- 活动提交、互评等学习数据
            <br>- 学生账号及其所有关联数据
          </p>
        </el-alert>

        <!-- 按选中学生删除模式 -->
        <div v-if="batchDeleteMode === 'selected'" class="border rounded p-4 bg-blue-50">
          <h4 class="font-medium mb-3 text-blue-800">已选择 {{ selectedStudents.length }} 位学生</h4>
          <div v-if="selectedStudentsPreview.length > 0">
            <el-table :data="selectedStudentsPreview" max-height="200" size="small">
              <el-table-column prop="username" label="学号" width="120" />
              <el-table-column prop="full_name" label="姓名" width="100" />
              <el-table-column prop="email" label="邮箱" />
              <el-table-column prop="classroom_name" label="班级" width="120" />
            </el-table>
            <p v-if="selectedStudents.length > selectedStudentsPreview.length" class="text-sm text-gray-600 mt-2">
              共 {{ selectedStudents.length }} 位学生，上方仅显示前 {{ selectedStudentsPreview.length }} 位
            </p>
          </div>
        </div>

        <!-- 按条件删除模式 -->
        <el-form v-else :model="batchDeleteForm" label-width="100px">
          <el-form-item label="所属区域">
            <el-select
              v-model="batchDeleteForm.region_id"
              @change="handleBatchDeleteRegionChange"
              placeholder="选择区域（不选则删除所有区域）"
              clearable
              class="w-full"
            >
              <el-option
                v-for="region in allRegions"
                :key="region.id"
                :label="region.name"
                :value="region.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="年级">
            <el-select
              v-model="batchDeleteForm.grade_id"
              @change="handleBatchDeleteGradeChange"
              placeholder="选择年级（不选则删除所有年级）"
              clearable
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

          <el-form-item label="所属学校">
            <el-select
              v-model="batchDeleteForm.school_id"
              @change="handleBatchDeleteSchoolChange"
              placeholder="输入学校名称搜索或选择学校（不选则删除所有学校）"
              clearable
              filterable
              class="w-full"
            >
              <el-option
                v-for="school in filteredSchoolsForBatchDelete"
                :key="school.id"
                :label="school.name"
                :value="school.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="班级">
            <el-select
              v-model="batchDeleteForm.classroom_id"
              placeholder="选择班级（不选则删除所有班级）"
              clearable
              class="w-full"
              :disabled="!batchDeleteForm.school_id"
            >
              <el-option
                v-for="classroom in filteredClassroomsForBatchDelete"
                :key="classroom.id"
                :label="classroom.name"
                :value="classroom.id"
              />
            </el-select>
          </el-form-item>
        </el-form>

        <!-- 预览结果（按条件删除模式） -->
        <div v-if="batchDeleteMode === 'filter' && previewResult" class="border rounded p-4 bg-gray-50">
          <h4 class="font-medium mb-2">删除预览</h4>
          <p class="text-lg font-bold text-red-600">{{ previewResult.message }}</p>
          <div v-if="previewResult.preview_users && previewResult.preview_users.length > 0" class="mt-3">
            <p class="text-sm text-gray-600 mb-2">部分学生列表（显示前{{ previewResult.showing }}个）：</p>
            <el-table :data="previewResult.preview_users" max-height="200" size="small">
              <el-table-column prop="username" label="学号" width="100" />
              <el-table-column prop="full_name" label="姓名" width="100" />
              <el-table-column prop="email" label="邮箱" />
              <el-table-column prop="classroom_name" label="班级" />
            </el-table>
          </div>
        </div>

        <div class="flex gap-2">
          <!-- 按条件删除模式：需要先预览 -->
          <template v-if="batchDeleteMode === 'filter'">
            <el-button
              type="warning"
              @click="previewBatchDelete"
              :loading="previewing"
              :disabled="deleting"
            >
              🔍 预览删除范围
            </el-button>
            <el-button
              v-if="previewResult"
              type="danger"
              @click="confirmBatchDelete"
              :loading="deleting"
              :disabled="!previewResult || previewResult.total_count === 0"
            >
              ⚠️ 确认删除
            </el-button>
          </template>
          <!-- 按选中学生删除模式：直接删除 -->
          <template v-else>
            <el-button
              type="danger"
              @click="confirmBatchDeleteSelected"
              :loading="deleting"
              :disabled="selectedStudents.length === 0"
            >
              ⚠️ 确认删除 {{ selectedStudents.length }} 位学生
            </el-button>
          </template>
        </div>
      </div>
      <template #footer>
        <el-button @click="showBatchDeleteByFilterDialog = false" :disabled="deleting">取消</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { adminService, type User, type Region, type School, type Classroom } from '@/services/admin'
import curriculumService from '@/services/curriculum'
import type { UploadFile } from 'element-plus'
import type { Grade } from '@/types/curriculum'
import * as XLSX from 'xlsx'
import { sanitizeViteApiUrlForProduction } from '@/utils/runtimeApiBase'

// 状态管理
const students = ref<User[]>([])
const allRegions = ref<Region[]>([])
const allSchools = ref<School[]>([])
const allClassrooms = ref<Classroom[]>([])
const grades = ref<Grade[]>([])
const loading = ref(false)
const saving = ref(false)
const importing = ref(false)
const selectedStudents = ref<number[]>([])

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 筛选器
const filters = ref<{
  region_id?: number
  school_id?: number
  grade_id?: number
  classroom_id?: number
  search?: string
}>({})

// 计算属性
const filteredSchools = computed(() => {
  if (filters.value.region_id) {
    return allSchools.value.filter(s => s.region_id === filters.value.region_id)
  }
  return allSchools.value
})

const filteredClassrooms = computed(() => {
  let result = allClassrooms.value
  if (filters.value.school_id) {
    result = result.filter(c => c.school_id === filters.value.school_id)
  }
  if (filters.value.grade_id) {
    result = result.filter(c => c.grade_id === filters.value.grade_id)
  }
  return result
})

const formClassrooms = computed(() => {
  let result = allClassrooms.value
  if (studentForm.value.school_id) {
    result = result.filter(c => c.school_id === studentForm.value.school_id)
  }
  if (studentForm.value.grade_id) {
    result = result.filter(c => c.grade_id === studentForm.value.grade_id)
  }
  return result
})

// 批量选择相关
const isAllSelected = computed(() => {
  return students.value.length > 0 && selectedStudents.value.length === students.value.length
})

const isSomeSelected = computed(() => {
  return selectedStudents.value.length > 0 && selectedStudents.value.length < students.value.length
})

// 批量删除对话框中使用的学校筛选（根据区域+年级过滤）
const filteredSchoolsForBatchDelete = computed(() => {
  let result = allSchools.value
  
  // 先按区域筛选
  if (batchDeleteForm.value.region_id) {
    result = result.filter(s => s.region_id === batchDeleteForm.value.region_id)
  }
  
  // 如果选择了年级，只显示该年级下有班级的学校
  if (batchDeleteForm.value.grade_id) {
    // 找出该年级下的所有班级
    const gradeClassrooms = allClassrooms.value.filter(
      c => c.grade_id === batchDeleteForm.value.grade_id
    )
    // 提取这些班级所属的学校ID
    const schoolIdsWithGrade = new Set(gradeClassrooms.map(c => c.school_id))
    
    // 如果已经按区域筛选过，则只保留该区域下且该年级有班级的学校
    // 如果没有按区域筛选，则只保留该年级有班级的学校
    result = result.filter(s => schoolIdsWithGrade.has(s.id))
  }
  
  return result
})

// 批量删除对话框中使用的班级筛选（根据学校+年级过滤）
const filteredClassroomsForBatchDelete = computed(() => {
  let result = allClassrooms.value
  // 按学校筛选
  if (batchDeleteForm.value.school_id) {
    result = result.filter(c => c.school_id === batchDeleteForm.value.school_id)
  } else if (batchDeleteForm.value.region_id) {
    // 如果没有选择学校但选择了区域，按区域筛选
    const schoolIds = allSchools.value
      .filter(s => s.region_id === batchDeleteForm.value.region_id)
      .map(s => s.id)
    result = result.filter(c => schoolIds.includes(c.school_id))
  }
  // 按年级筛选
  if (batchDeleteForm.value.grade_id) {
    result = result.filter(c => c.grade_id === batchDeleteForm.value.grade_id)
  }
  return result
})

// 对话框状态
const showStudentModal = ref(false)
const showImportDialog = ref(false)
const showBatchDeleteByFilterDialog = ref(false)
const editingStudent = ref<User | null>(null)

// 批量删除相关（统一处理按选中和按条件）
const batchDeleteMode = ref<'selected' | 'filter'>('filter') // 'selected': 按选中学生, 'filter': 按条件
const batchDeleteForm = ref<{
  region_id?: number
  school_id?: number
  grade_id?: number
  classroom_id?: number
}>({
  region_id: undefined,
  school_id: undefined,
  grade_id: undefined,
  classroom_id: undefined
})

const previewResult = ref<any>(null)
const previewing = ref(false)
const deleting = ref(false)

// 选中学生的预览列表（最多显示10个）
const selectedStudentsPreview = computed(() => {
  return students.value
    .filter(s => selectedStudents.value.includes(s.id))
    .slice(0, 10)
    .map(s => ({
      username: s.username,
      full_name: s.full_name || '-',
      email: s.email,
      classroom_name: s.classroom_name || '-'
    }))
})

// 表单数据
const studentForm = ref({
  full_name: '',
  username: '',
  student_id_number: '',
  email: '',
  password: '',
  school_id: undefined as number | undefined,
  grade_id: undefined as number | undefined,
  classroom_id: undefined as number | undefined,
  student_type: 'none',
  is_active: true
})

// 导入相关
const uploadRef = ref()
const importFile = ref<File | null>(null)
const importPreview = ref<any[]>([])

// Toast
const toast = useToast()

// 防抖加载
let debounceTimer: ReturnType<typeof setTimeout> | null = null
const debouncedLoadStudents = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => loadStudents(), 500)
}

// 加载数据
const loadStudents = async (page?: number) => {
  if (page) currentPage.value = page
  loading.value = true
  try {
    const response = await adminService.getUsers({
      page: currentPage.value,
      size: pageSize.value,
      role: 'student',
      search: filters.value.search,
    })
    // 在前端过滤（因为后端可能不支持所有筛选条件）
    let filteredUsers = response.users
    if (filters.value.school_id) {
      filteredUsers = filteredUsers.filter(u => u.school_id === filters.value.school_id)
    }
    if (filters.value.grade_id) {
      filteredUsers = filteredUsers.filter(u => u.grade_id === filters.value.grade_id)
    }
    if (filters.value.classroom_id) {
      filteredUsers = filteredUsers.filter(u => u.classroom_id === filters.value.classroom_id)
    }
    students.value = filteredUsers
    total.value = filteredUsers.length
  } catch (error) {
    toast.error('加载学生列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadRegions = async () => {
  try {
    const response = await adminService.getRegions({ size: 1000 })
    allRegions.value = response.regions
  } catch (error) {
    console.error('加载区域失败:', error)
  }
}

const loadSchools = async () => {
  try {
    const response = await adminService.getSchools({ size: 1000 })
    allSchools.value = response.schools
  } catch (error) {
    console.error('加载学校失败:', error)
  }
}

const loadClassrooms = async () => {
  try {
    const response = await adminService.getClassrooms({ size: 1000 })
    allClassrooms.value = response.classrooms
  } catch (error) {
    console.error('加载班级失败:', error)
  }
}

const loadGrades = async () => {
  try {
    grades.value = await curriculumService.getGrades(true)
  } catch (error) {
    console.error('加载年级失败:', error)
  }
}

// 事件处理
const handleRegionChange = () => {
  filters.value.school_id = undefined
  filters.value.grade_id = undefined
  filters.value.classroom_id = undefined
  loadStudents()
}

const handleSchoolChange = () => {
  filters.value.grade_id = undefined
  filters.value.classroom_id = undefined
  loadStudents()
}

const handleFormSchoolChange = () => {
  studentForm.value.grade_id = undefined
  studentForm.value.classroom_id = undefined
}

const handleFormGradeChange = () => {
  studentForm.value.classroom_id = undefined
}

// 学生操作
const openCreateStudentModal = () => {
  editingStudent.value = null
  resetForm()
  showStudentModal.value = true
}

const editStudent = (student: User) => {
  editingStudent.value = student
  studentForm.value = {
    full_name: student.full_name || '',
    username: student.username,
    student_id_number: student.student_id_number || '',
    email: student.email,
    password: '',
    school_id: student.school_id || undefined,
    grade_id: student.grade_id || undefined,
    classroom_id: student.classroom_id || undefined,
    student_type: (student as any).student_type || 'none',
    is_active: student.is_active
  }
  showStudentModal.value = true
}

const saveStudent = async () => {
  if (!studentForm.value.username) {
    ElMessage.warning('请输入学号')
    return
  }
  if (!studentForm.value.email) {
    ElMessage.warning('请输入邮箱')
    return
  }
  if (!editingStudent.value && !studentForm.value.password) {
    ElMessage.warning('请输入密码')
    return
  }

  saving.value = true
  try {
    if (editingStudent.value) {
      await adminService.updateUser(editingStudent.value.id, {
        username: studentForm.value.username,
        email: studentForm.value.email,
        full_name: studentForm.value.full_name,
        student_id_number: studentForm.value.student_id_number,
        school_id: studentForm.value.school_id,
        grade_id: studentForm.value.grade_id,
        classroom_id: studentForm.value.classroom_id,
        is_active: studentForm.value.is_active
      })
      ElMessage.success('更新成功')
    } else {
      await adminService.createUser({
        username: studentForm.value.username,
        email: studentForm.value.email,
        full_name: studentForm.value.full_name,
        student_id_number: studentForm.value.student_id_number,
        password: studentForm.value.password,
        role: 'student',
        school_id: studentForm.value.school_id,
        grade_id: studentForm.value.grade_id,
        classroom_id: studentForm.value.classroom_id,
        is_active: studentForm.value.is_active
      })
      ElMessage.success('创建成功')
    }
    showStudentModal.value = false
    loadStudents()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    saving.value = false
  }
}

const toggleStudentStatus = async (student: User) => {
  try {
    await adminService.toggleUserStatus(student.id)
    ElMessage.success(student.is_active ? '已停用' : '已激活')
    loadStudents()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const resetPassword = async (student: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要重置学生 ${student.full_name || student.username} 的密码吗？`,
      '重置密码',
      { type: 'warning' }
    )
    const result = await adminService.resetUserPassword(student.id)
    ElMessageBox.alert(`新密码：${result.new_password}`, '密码重置成功', {
      type: 'success',
      confirmButtonText: '复制',
      callback: () => {
        navigator.clipboard.writeText(result.new_password)
      }
    })
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重置密码失败')
    }
  }
}

const resetForm = () => {
  studentForm.value = {
    full_name: '',
    username: '',
    student_id_number: '',
    email: '',
    password: '',
    school_id: undefined,
    grade_id: undefined,
    classroom_id: undefined,
    student_type: 'none',
    is_active: true
  }
}

// 批量选择和删除
const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedStudents.value = []
  } else {
    selectedStudents.value = students.value.map(s => s.id)
  }
}

const toggleStudentSelection = (studentId: number) => {
  const index = selectedStudents.value.indexOf(studentId)
  if (index > -1) {
    selectedStudents.value.splice(index, 1)
  } else {
    selectedStudents.value.push(studentId)
  }
}

const clearSelection = () => {
  selectedStudents.value = []
}

// 打开批量删除对话框（按选中学生）
const openBatchDeleteWithSelected = () => {
  if (selectedStudents.value.length === 0) {
    toast.warning('请先选择要删除的学生')
    return
  }
  batchDeleteMode.value = 'selected'
  previewResult.value = null
  showBatchDeleteByFilterDialog.value = true
}

// 批量删除（按条件）相关
const openBatchDeleteByFilterDialog = () => {
  batchDeleteMode.value = 'filter'
  batchDeleteForm.value = {
    region_id: filters.value.region_id,
    school_id: filters.value.school_id,
    grade_id: filters.value.grade_id,
    classroom_id: filters.value.classroom_id
  }
  previewResult.value = null
  showBatchDeleteByFilterDialog.value = true
}

const handleBatchDeleteRegionChange = () => {
  // 区域变化时，清空学校和班级选择（年级保持不变）
  // 新的逻辑顺序：区域 → 年级 → 学校 → 班级
  batchDeleteForm.value.school_id = undefined
  batchDeleteForm.value.classroom_id = undefined
}

const handleBatchDeleteGradeChange = () => {
  // 年级变化时，清空学校和班级选择
  // 新的逻辑顺序：区域 → 年级 → 学校 → 班级
  batchDeleteForm.value.school_id = undefined
  batchDeleteForm.value.classroom_id = undefined
}

const handleBatchDeleteSchoolChange = () => {
  // 学校变化时，只清空班级选择（年级保持不变）
  // 新的逻辑顺序：区域 → 年级 → 学校 → 班级
  batchDeleteForm.value.classroom_id = undefined
}

const previewBatchDelete = async () => {
  previewing.value = true
  previewResult.value = null
  try {
    const result = await adminService.previewBatchDeleteByFilter({
      role: 'student',
      region_id: batchDeleteForm.value.region_id,
      school_id: batchDeleteForm.value.school_id,
      grade_id: batchDeleteForm.value.grade_id,
      classroom_id: batchDeleteForm.value.classroom_id
    })
    previewResult.value = result
    toast.success(`找到 ${result.total_count} 位学生`)
  } catch (error: any) {
    console.error('Failed to preview batch delete:', error)
    toast.error(error.response?.data?.detail || '预览失败')
  } finally {
    previewing.value = false
  }
}

// 确认删除（按条件删除模式）
const confirmBatchDelete = async () => {
  if (!previewResult.value || previewResult.value.total_count === 0) {
    toast.warning('没有要删除的学生')
    return
  }

  if (!confirm(`确定要删除 ${previewResult.value.total_count} 位学生吗？\n\n此操作不可撤销，将同时删除：\n- 学生账号\n- 考号映射\n- 考场安排\n- 活动提交、互评等学习数据`)) {
    return
  }

  deleting.value = true
  try {
    const result = await adminService.batchDeleteByFilter({
      role: 'student',
      region_id: batchDeleteForm.value.region_id,
      school_id: batchDeleteForm.value.school_id,
      grade_id: batchDeleteForm.value.grade_id,
      classroom_id: batchDeleteForm.value.classroom_id,
      confirm: true
    })
    toast.success(
      `成功删除 ${result.deleted_count} 位学生\n` +
      `同时删除了 ${result.exam_mappings_deleted || 0} 条考号映射\n` +
      `和 ${result.exam_room_students_deleted || 0} 条考场安排记录`
    )
    showBatchDeleteByFilterDialog.value = false
    loadStudents() // 刷新列表
  } catch (error: any) {
    console.error('Failed to batch delete by filter:', error)
    toast.error(error.response?.data?.detail || '批量删除失败')
  } finally {
    deleting.value = false
  }
}

// 确认删除（按选中学生模式）
const confirmBatchDeleteSelected = async () => {
  if (selectedStudents.value.length === 0) {
    toast.warning('没有要删除的学生')
    return
  }

  if (!confirm(`确定要删除 ${selectedStudents.value.length} 位选中学生吗？\n\n此操作不可撤销，将同时删除：\n- 学生账号\n- 考号映射\n- 考场安排\n- 活动提交、互评等学习数据`)) {
    return
  }

  deleting.value = true
  try {
    // 注意：batchDeleteUsers 使用的是旧的删除逻辑，可能没有删除所有相关表
    // 为了使用完整的删除逻辑，我们需要调用 batchDeleteByFilter
    // 但由于 batchDeleteByFilter 不支持直接传用户ID列表，我们需要通过其他方式
    
    // 方案：直接使用 batchDeleteUsers，但后续需要确保后端也使用完整的删除逻辑
    // 或者，我们可以通过查询这些学生，然后使用他们的筛选条件来调用 batchDeleteByFilter
    // 但这样比较复杂
    
    // 目前先使用 batchDeleteUsers，后续可以考虑修改后端支持按ID列表的完整删除
    const result = await adminService.batchDeleteUsers(selectedStudents.value)
    
    toast.success(
      `成功删除 ${result.deleted_count} 位学生` +
      (result.failed_count ? `，失败 ${result.failed_count} 位` : '')
    )
    
    // 从列表中移除已删除的学生
    students.value = students.value.filter(s => !selectedStudents.value.includes(s.id))
    total.value -= result.deleted_count
    
    showBatchDeleteByFilterDialog.value = false
    clearSelection()
    loadStudents() // 刷新列表以确保数据同步
  } catch (error: any) {
    console.error('Failed to batch delete selected students:', error)
    toast.error(error.response?.data?.detail || '批量删除失败')
  } finally {
    deleting.value = false
  }
}

// 导入相关
const openImportDialog = () => {
  importFile.value = null
  importPreview.value = []
  showImportDialog.value = true
}

const downloadTemplate = () => {
  const template = [
    ['学号*', '姓名*', '学籍号*', '邮箱', '学校名称*', '学校代码', '年级级别*', '班级编号*'],
    ['2024100001', '张三', '123456789012345678', 'zhang@example.com', '示例学校', '10001', 7, '701'],
    ['2024100002', '李四', '987654321098765432', 'li@example.com', '示例学校', '10001', 7, '702'],
    ['2024100003', '王五', '111111111111111111', 'wang@example.com', '示例学校', '10001', 10, '1001']
  ]

  const ws = XLSX.utils.aoa_to_sheet(template)
  // 设置列宽
  const colWidths = [
    { wch: 15 }, { wch: 12 }, { wch: 20 }, { wch: 20 }, { wch: 20 },
    { wch: 12 }, { wch: 12 }, { wch: 12 }
  ]
  ws['!cols'] = colWidths

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '学生导入模板')
  XLSX.writeFile(wb, '学生导入模板.xlsx')
  ElMessage.success('模板下载成功')
}

const handleFileChange = (file: UploadFile) => {
  console.log('📁 [学生导入] 文件变更事件触发:', file)

  // 获取文件对象（兼容不同版本的 Element Plus）
  let rawFile: File | null = null

  if (file.raw) {
    rawFile = file.raw as File
  } else if (file instanceof File) {
    rawFile = file
  } else {
    console.error('❌ [学生导入] 无法获取文件对象:', file)
    ElMessage.error('文件获取失败，请重试')
    return
  }

  console.log('✅ [学生导入] 获取到文件:', rawFile.name, rawFile.size, rawFile.type)

  importFile.value = rawFile

  // 读取文件预览
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = new Uint8Array(e.target?.result as ArrayBuffer)
      const workbook = XLSX.read(data, { type: 'array' })
      const worksheet = workbook.Sheets[workbook.SheetNames[0]]
      const json = XLSX.utils.sheet_to_json(worksheet) as any[]
      importPreview.value = json
      console.log('📊 [学生导入] 解析成功，共', json.length, '条数据')
    } catch (error) {
      console.error('❌ [学生导入] 文件解析失败:', error)
      ElMessage.error('文件解析失败，请检查文件格式')
    }
  }
  reader.readAsArrayBuffer(rawFile)
}

const startImport = async () => {
  console.log('🚀 [学生导入] 开始导入，当前文件状态:', importFile.value)

  if (!importFile.value) {
    console.error('❌ [学生导入] 文件对象为空')
    ElMessage.warning('请选择文件')
    return
  }

  console.log('✅ [学生导入] 文件已选择:', importFile.value.name, importFile.value.size)

  importing.value = true
  try {
    // 获取正确的API基础URL
    const hostname = window.location.hostname
    const protocol = window.location.protocol
    let apiBaseUrl = '/api/v1'

    // 检测 CloudStudio 环境
    if (hostname.includes('cloudstudio.club') || hostname.includes('coding.net')) {
      if (hostname.includes('--')) {
        const backendHostname = hostname.replace(/--\d+/, '--8000')
        apiBaseUrl = `https://${backendHostname}/api/v1`
      } else {
        apiBaseUrl = `${protocol}//${hostname}:8000/api/v1`
      }
    } else if (import.meta.env.VITE_API_BASE_URL) {
      apiBaseUrl = import.meta.env.VITE_API_BASE_URL
      const s = sanitizeViteApiUrlForProduction(apiBaseUrl)
      if (s) apiBaseUrl = s
    } else if (import.meta.env.DEV) {
      apiBaseUrl = `${protocol}//${hostname}:8000/api/v1`
    }

    console.log('🚀 [学生导入] API基础地址:', apiBaseUrl)

    // 调用统一导入API
    const token = localStorage.getItem('access_token')

    // 创建FormData（只包含文件）
    const formData = new FormData()
    formData.append('file', importFile.value)

    // 构建URL（strategy_type 作为查询参数）
    const url = new URL(`${apiBaseUrl}/import`)
    url.searchParams.append('strategy_type', 'student_account')
    url.searchParams.append('update_existing', 'false')

    console.log('📤 [学生导入] 请求URL:', url.toString())

    const response = await fetch(url.toString(), {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
        // 不要设置 Content-Type，让浏览器自动设置 multipart/form-data
      },
      body: formData
    })

    console.log('📥 [学生导入] 响应状态:', response.status)

    if (!response.ok) {
      let errorMessage = '导入失败'
      try {
        const error = await response.json()
        errorMessage = error.detail || error.message || errorMessage
      } catch (e) {
        errorMessage = `HTTP ${response.status}: ${response.statusText}`
      }
      throw new Error(errorMessage)
    }

    const result = await response.json()
    console.log('✅ [学生导入] 导入结果:', result)

    // 显示导入结果
    if (result.failed > 0) {
      ElMessage.warning(
        `导入完成：成功 ${result.success} 条，失败 ${result.failed} 条` +
        (result.errors?.length > 0 ? `\n错误：${result.errors[0].message}` : '')
      )
    } else {
      ElMessage.success(`成功导入 ${result.success} 位学生`)
    }

    showImportDialog.value = false
    loadStudents()
  } catch (error: any) {
    console.error('❌ [学生导入] 错误:', error)
    ElMessage.error(error.message || '导入失败')
  } finally {
    importing.value = false
  }
}

// 工具函数
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadRegions()
  loadSchools()
  loadClassrooms()
  loadGrades()
  loadStudents()
})
</script>

<style scoped>
.el-upload {
  width: 100%;
}

.el-upload :deep(.el-upload-dragger) {
  width: 100%;
}
</style>
