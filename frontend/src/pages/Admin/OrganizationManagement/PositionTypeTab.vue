<template>
  <div class="space-y-6">
    <!-- 功能说明 -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <p class="text-sm text-blue-800">
        管理教师职务类型，支持自定义职务（如：校长、教研室主任等）。系统预设的职务类型（班主任、学科教师）不能删除，只能停用。
      </p>
    </div>

    <!-- 操作栏 -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex justify-between items-center">
        <div class="flex gap-4">
          <button
            @click="openCreatePositionTypeDialog"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            + 创建职务类型
          </button>
          <button
            @click="loadPositionTypes"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            刷新
          </button>
        </div>
        <div class="flex gap-2">
          <select
            v-model="positionTypeCategoryFilter"
            @change="loadPositionTypes"
            class="px-3 py-2 border rounded-lg"
          >
            <option value="">所有分类</option>
            <option value="教学类">教学类</option>
            <option value="管理类">管理类</option>
            <option value="行政类">行政类</option>
          </select>
          <select
            v-model="positionTypeActiveFilter"
            @change="loadPositionTypes"
            class="px-3 py-2 border rounded-lg"
          >
            <option value="">全部状态</option>
            <option value="true">激活</option>
            <option value="false">停用</option>
          </select>
          <input
            v-model="positionTypeSearch"
            @input="loadPositionTypes"
            type="text"
            placeholder="搜索职务名称、代码..."
            class="px-3 py-2 border rounded-lg w-64"
          />
        </div>
      </div>
    </div>

    <!-- 职务类型列表 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">职务名称</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">代码</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">分类</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">排序</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">类型</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">描述</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="positionType in positionTypes" :key="positionType.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ positionType.id }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ positionType.name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ positionType.code || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ positionType.category || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ positionType.sort_order }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span v-if="positionType.is_system" class="px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800">系统</span>
              <span v-else class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">自定义</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span v-if="positionType.is_active" class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">激活</span>
              <span v-else class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">停用</span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-500">{{ positionType.description || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <button
                @click="openEditPositionTypeDialog(positionType)"
                class="text-blue-600 hover:text-blue-900 mr-3"
              >
                编辑
              </button>
              <button
                v-if="!positionType.is_system"
                @click="handleDeletePositionType(positionType)"
                class="text-red-600 hover:text-red-900"
              >
                删除
              </button>
              <span v-else class="text-gray-400 text-xs">系统预设不可删除</span>
            </td>
          </tr>
          <tr v-if="positionTypes.length === 0">
            <td colspan="9" class="px-6 py-4 text-center text-sm text-gray-500">
              暂无职务类型数据
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 职务类型创建/编辑对话框 -->
    <el-dialog
      v-model="showPositionTypeDialog"
      :title="editingPositionType ? '编辑职务类型' : '创建职务类型'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="positionTypeForm" label-width="120px">
        <el-form-item label="职务名称*" required>
          <el-input
            v-model="positionTypeForm.name"
            placeholder="如：校长、教研室主任"
            :disabled="editingPositionType?.is_system"
          />
        </el-form-item>
        <el-form-item label="职务代码">
          <el-input
            v-model="positionTypeForm.code"
            placeholder="如：principal、research_director（可选）"
            :disabled="editingPositionType?.is_system"
          />
        </el-form-item>
        <el-form-item label="职务分类">
          <el-select v-model="positionTypeForm.category" placeholder="选择分类" clearable>
            <el-option label="教学类" value="教学类" />
            <el-option label="管理类" value="管理类" />
            <el-option label="行政类" value="行政类" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序权重">
          <el-input-number
            v-model="positionTypeForm.sort_order"
            :min="0"
            :max="999"
            placeholder="数字越小越靠前"
          />
        </el-form-item>
        <el-form-item label="职务描述">
          <el-input
            v-model="positionTypeForm.description"
            type="textarea"
            :rows="3"
            placeholder="描述该职务的职责和特点"
          />
        </el-form-item>
        <el-form-item label="是否激活">
          <el-switch v-model="positionTypeForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="flex justify-end gap-2">
          <el-button @click="showPositionTypeDialog = false">取消</el-button>
          <el-button
            type="primary"
            @click="savePositionType"
            :loading="positionTypeSaving"
            :disabled="!positionTypeForm.name"
          >
            {{ editingPositionType ? '更新' : '创建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { teacherPositionApi } from '@/services/teacher_position'
import type {
  TeacherPositionTypeResponse as TeacherPositionType,
  TeacherPositionTypeCreate,
  TeacherPositionTypeUpdate,
} from '@/types/teacher_position'

// 状态
const positionTypes = ref<TeacherPositionType[]>([])
const positionTypeCategoryFilter = ref('')
const positionTypeActiveFilter = ref('')
const positionTypeSearch = ref('')
const showPositionTypeDialog = ref(false)
const editingPositionType = ref<TeacherPositionType | null>(null)
const positionTypeForm = ref<TeacherPositionTypeCreate>({
  name: '',
  code: '',
  description: '',
  category: '',
  sort_order: 0,
  is_active: true,
})
const positionTypeSaving = ref(false)

// 加载职务类型列表
async function loadPositionTypes() {
  try {
    const params: any = {}
    if (positionTypeCategoryFilter.value) {
      params.category = positionTypeCategoryFilter.value
    }
    if (positionTypeActiveFilter.value !== '') {
      params.is_active = positionTypeActiveFilter.value === 'true'
    }
    if (positionTypeSearch.value) {
      params.search = positionTypeSearch.value
    }
    const response = await teacherPositionApi.getPositionTypes(params)
    positionTypes.value = response.position_types
  } catch (error: any) {
    console.error('Failed to load position types:', error)
    ElMessage.error('加载职务类型列表失败')
  }
}

// 打开创建职务类型对话框
function openCreatePositionTypeDialog() {
  editingPositionType.value = null
  positionTypeForm.value = {
    name: '',
    code: '',
    description: '',
    category: '',
    sort_order: 0,
    is_active: true,
  }
  showPositionTypeDialog.value = true
}

// 打开编辑职务类型对话框
function openEditPositionTypeDialog(positionType: TeacherPositionType) {
  editingPositionType.value = positionType
  positionTypeForm.value = {
    name: positionType.name,
    code: positionType.code || '',
    description: positionType.description || '',
    category: positionType.category || '',
    sort_order: positionType.sort_order,
    is_active: positionType.is_active,
  }
  showPositionTypeDialog.value = true
}

// 保存职务类型
async function savePositionType() {
  try {
    positionTypeSaving.value = true
    if (editingPositionType.value) {
      // 更新
      await teacherPositionApi.updatePositionType(
        editingPositionType.value.id,
        positionTypeForm.value as TeacherPositionTypeUpdate
      )
      ElMessage.success('更新成功')
    } else {
      // 创建
      await teacherPositionApi.createPositionType(positionTypeForm.value)
      ElMessage.success('创建成功')
    }
    showPositionTypeDialog.value = false
    loadPositionTypes()
  } catch (error: any) {
    console.error('Failed to save position type:', error)
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    positionTypeSaving.value = false
  }
}

// 删除职务类型
async function handleDeletePositionType(positionType: TeacherPositionType) {
  try {
    await ElMessageBox.confirm(
      `确定要删除职务类型"${positionType.name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await teacherPositionApi.deletePositionType(positionType.id)
    ElMessage.success('删除成功')
    loadPositionTypes()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to delete position type:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 生命周期
onMounted(() => {
  loadPositionTypes()
})

// 暴露方法给父组件
defineExpose({
  loadPositionTypes
})
</script>
