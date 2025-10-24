<template>
  <div v-if="show" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">批量导入用户</h3>
        <button @click="close" class="text-gray-400 hover:text-gray-600">
          <span class="text-2xl">&times;</span>
        </button>
      </div>

      <!-- 步骤指示器 -->
      <div class="mb-6">
        <div class="flex items-center justify-center space-x-4">
          <div class="flex items-center">
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium"
                 :class="currentStep >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'">
              1
            </div>
            <span class="ml-2 text-sm font-medium">下载模板</span>
          </div>
          <div class="w-8 h-0.5 bg-gray-300"></div>
          <div class="flex items-center">
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium"
                 :class="currentStep >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'">
              2
            </div>
            <span class="ml-2 text-sm font-medium">上传文件</span>
          </div>
          <div class="w-8 h-0.5 bg-gray-300"></div>
          <div class="flex items-center">
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium"
                 :class="currentStep >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'">
              3
            </div>
            <span class="ml-2 text-sm font-medium">确认导入</span>
          </div>
        </div>
      </div>

      <!-- 步骤1: 下载模板 -->
      <div v-if="currentStep === 1" class="space-y-4">
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 class="font-medium text-blue-900 mb-2">📋 导入说明</h4>
          <ul class="text-sm text-blue-800 space-y-1">
            <li>• 请先下载模板文件，按照模板格式填写用户信息</li>
            <li>• 支持 CSV 和 Excel 格式文件（.csv, .xlsx, .xls），文件大小不超过5MB</li>
            <li>• 用户名和邮箱必须唯一，不能与现有用户重复</li>
            <li>• 角色可选值：admin, researcher, teacher, student</li>
            <li>• is_active字段：true表示激活，false表示未激活</li>
          </ul>
        </div>
        
        <div class="flex justify-center">
          <button
            @click="downloadTemplate"
            class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
          >
            <span class="mr-2">📥</span>
            下载模板文件
          </button>
        </div>
        
        <div class="text-center">
          <button
            @click="currentStep = 2"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            下一步
          </button>
        </div>
      </div>

      <!-- 步骤2: 上传文件 -->
      <div v-if="currentStep === 2" class="space-y-4">
        <div class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <input
            ref="fileInput"
            type="file"
            accept=".csv,.xlsx,.xls"
            @change="handleFileSelect"
            class="hidden"
          />
          <div v-if="!selectedFile" @click="$refs.fileInput.click()" class="cursor-pointer">
            <div class="text-4xl mb-4">📁</div>
            <p class="text-lg font-medium text-gray-700">点击选择文件</p>
            <p class="text-sm text-gray-500 mt-2">支持 CSV 或 Excel 文件（.csv, .xlsx, .xls）</p>
            <p class="text-sm text-gray-500">或拖拽文件到此区域</p>
          </div>
          <div v-else class="text-center">
            <div class="text-4xl mb-4">✅</div>
            <p class="text-lg font-medium text-green-700">{{ selectedFile.name }}</p>
            <p class="text-sm text-gray-500 mt-2">文件大小: {{ formatFileSize(selectedFile.size) }}</p>
            <button
              @click="selectedFile = null; $refs.fileInput.value = ''"
              class="mt-2 text-sm text-red-600 hover:text-red-800"
            >
              重新选择
            </button>
          </div>
        </div>
        
        <div class="flex justify-between">
          <button
            @click="currentStep = 1"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            上一步
          </button>
          <button
            @click="currentStep = 3"
            :disabled="!selectedFile"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一步
          </button>
        </div>
      </div>

      <!-- 步骤3: 确认导入 -->
      <div v-if="currentStep === 3" class="space-y-4">
        <div v-if="importing" class="text-center py-8">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p class="text-gray-600">正在导入用户，请稍候...</p>
        </div>
        
        <div v-else-if="importResult" class="space-y-4">
          <div class="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 class="font-medium text-green-900 mb-2">✅ 导入完成</h4>
            <p class="text-sm text-green-800">
              成功导入 {{ importResult.success_count }} 个用户，
              {{ importResult.error_count }} 个失败
            </p>
          </div>
          
          <div v-if="importResult.errors.length > 0" class="bg-red-50 border border-red-200 rounded-lg p-4">
            <h4 class="font-medium text-red-900 mb-2">❌ 导入错误</h4>
            <div class="max-h-32 overflow-y-auto">
              <ul class="text-sm text-red-800 space-y-1">
                <li v-for="error in importResult.errors" :key="error">• {{ error }}</li>
              </ul>
            </div>
          </div>
          
          <div v-if="importResult.created_users.length > 0" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 class="font-medium text-blue-900 mb-2">👥 成功创建的用户</h4>
            <div class="max-h-32 overflow-y-auto">
              <ul class="text-sm text-blue-800 space-y-1">
                <li v-for="user in importResult.created_users" :key="user.id">
                  • {{ user.username }} ({{ user.email }}) - {{ getRoleDisplayName(user.role) }}
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <div v-else class="space-y-4">
          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h4 class="font-medium text-yellow-900 mb-2">⚠️ 确认导入</h4>
            <p class="text-sm text-yellow-800">
              即将导入文件 <strong>{{ selectedFile?.name }}</strong> 中的用户数据。
              请确认文件格式正确，用户名和邮箱不重复。
            </p>
          </div>
          
          <div class="flex justify-between">
            <button
              @click="currentStep = 2"
              class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              上一步
            </button>
            <button
              @click="startImport"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              开始导入
            </button>
          </div>
        </div>
        
        <div v-if="importResult" class="text-center">
          <button
            @click="close"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            完成
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useToast } from '@/composables/useToast'
import adminService, { type UserCreate, type BatchImportResult } from '@/services/admin'
import * as XLSX from 'xlsx'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  close: []
  success: []
}>()

const toast = useToast()

// 响应式数据
const currentStep = ref(1)
const selectedFile = ref<File | null>(null)
const importing = ref(false)
const importResult = ref<BatchImportResult | null>(null)

// 方法
function close() {
  currentStep.value = 1
  selectedFile.value = null
  importResult.value = null
  emit('close')
}

function getRoleDisplayName(role: string): string {
  const roleMap = {
    admin: '管理员',
    researcher: '教研员',
    teacher: '教师',
    student: '学生'
  }
  return roleMap[role] || role
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

async function downloadTemplate() {
  try {
    const result = await adminService.getImportTemplate()
    
    // 创建下载链接
    const blob = new Blob([result.template], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', result.filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    toast.success('模板下载成功')
  } catch (error: any) {
    console.error('Failed to download template:', error)
    toast.error('下载模板失败')
  }
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    const fileName = file.name.toLowerCase()
    const validExtensions = ['.csv', '.xlsx', '.xls']
    const isValidFile = validExtensions.some(ext => fileName.endsWith(ext))
    
    if (!isValidFile) {
      toast.error('请选择 CSV 或 Excel 格式的文件（.csv, .xlsx, .xls）')
      return
    }
    
    if (file.size > 5 * 1024 * 1024) { // 5MB
      toast.error('文件大小不能超过5MB')
      return
    }
    
    selectedFile.value = file
  }
}

async function startImport() {
  if (!selectedFile.value) return
  
  importing.value = true
  importResult.value = null
  
  try {
    let users: UserCreate[]
    
    // 根据文件类型选择解析方式
    const fileName = selectedFile.value.name.toLowerCase()
    if (fileName.endsWith('.csv')) {
      // 解析CSV文件
      const csvText = await readFileAsText(selectedFile.value)
      users = parseCSV(csvText)
    } else if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
      // 解析Excel文件
      users = await parseExcel(selectedFile.value)
    } else {
      throw new Error('不支持的文件格式')
    }
    
    // 调用导入API
    const result = await adminService.batchImportUsers(users)
    importResult.value = result
    
    if (result.success_count > 0) {
      toast.success(`成功导入 ${result.success_count} 个用户`)
      emit('success')
    }
    
    if (result.error_count > 0) {
      toast.warning(`${result.error_count} 个用户导入失败`)
    }
    
  } catch (error: any) {
    console.error('Failed to import users:', error)
    toast.error(error.message || error.response?.data?.detail || '导入失败')
  } finally {
    importing.value = false
  }
}

function readFileAsText(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => resolve(e.target?.result as string)
    reader.onerror = (e) => reject(e)
    reader.readAsText(file, 'utf-8')
  })
}

function parseCSV(csvText: string): UserCreate[] {
  const lines = csvText.trim().split('\n')
  const headers = lines[0].split(',').map(h => h.trim())
  
  // 验证必需的列
  const requiredColumns = ['username', 'email', 'password', 'role', 'is_active']
  const missingColumns = requiredColumns.filter(col => !headers.includes(col))
  
  if (missingColumns.length > 0) {
    throw new Error(`缺少必需的列: ${missingColumns.join(', ')}`)
  }
  
  const users: UserCreate[] = []
  
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim()
    if (!line) continue
    
    const values = line.split(',').map(v => v.trim())
    if (values.length !== headers.length) {
      throw new Error(`第${i+1}行数据列数不匹配`)
    }
    
    const user: any = {}
    headers.forEach((header, index) => {
      user[header] = values[index]
    })
    
    // 转换数据类型
    users.push({
      username: user.username,
      email: user.email,
      password: user.password,
      role: user.role,
      is_active: user.is_active.toLowerCase() === 'true'
    })
  }
  
  return users
}

async function parseExcel(file: File): Promise<UserCreate[]> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target?.result as ArrayBuffer)
        const workbook = XLSX.read(data, { type: 'array' })
        
        // 读取第一个工作表
        const firstSheetName = workbook.SheetNames[0]
        const worksheet = workbook.Sheets[firstSheetName]
        
        // 转换为JSON
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 }) as any[][]
        
        if (jsonData.length < 2) {
          throw new Error('Excel文件为空或格式不正确')
        }
        
        // 第一行是表头
        const headers = jsonData[0].map(h => String(h).trim())
        
        // 验证必需的列
        const requiredColumns = ['username', 'email', 'password', 'role', 'is_active']
        const missingColumns = requiredColumns.filter(col => !headers.includes(col))
        
        if (missingColumns.length > 0) {
          throw new Error(`缺少必需的列: ${missingColumns.join(', ')}`)
        }
        
        const users: UserCreate[] = []
        
        // 从第二行开始解析数据
        for (let i = 1; i < jsonData.length; i++) {
          const row = jsonData[i]
          if (!row || row.length === 0) continue
          
          const user: any = {}
          headers.forEach((header, index) => {
            user[header] = row[index] !== undefined ? String(row[index]).trim() : ''
          })
          
          // 验证必需字段
          if (!user.username || !user.email || !user.password || !user.role) {
            throw new Error(`第${i+1}行数据不完整`)
          }
          
          // 转换数据类型
          users.push({
            username: user.username,
            email: user.email,
            password: user.password,
            role: user.role,
            is_active: String(user.is_active).toLowerCase() === 'true'
          })
        }
        
        if (users.length === 0) {
          throw new Error('没有找到有效的用户数据')
        }
        
        resolve(users)
      } catch (error: any) {
        reject(new Error(`解析Excel文件失败: ${error.message}`))
      }
    }
    
    reader.onerror = () => {
      reject(new Error('读取文件失败'))
    }
    
    reader.readAsArrayBuffer(file)
  })
}
</script>
