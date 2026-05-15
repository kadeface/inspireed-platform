<template>
  <div v-if="show" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">统一数据导入</h3>
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
          <h4 class="font-medium text-blue-900 mb-2">📋 统一导入说明</h4>
          <ul class="text-sm text-blue-800 space-y-1">
            <li>• <strong>一次导入，完成所有操作</strong>：创建用户、更新用户信息、添加到班级</li>
            <li>• 支持 CSV 和 Excel 格式文件（.csv, .xlsx, .xls），文件大小不超过5MB</li>
            <li>• <strong>学籍号（推荐）</strong>：唯一标识，用于匹配已存在的用户</li>
            <li>• 如果用户不存在，系统会根据学号/用户名、邮箱、姓名创建新用户（需要提供密码）</li>
            <li>• 如果用户已存在，系统会更新用户信息（密码可选）</li>
            <li>• 如果提供了班级ID，系统会自动将用户添加到班级</li>
            <li>• <strong>组织架构ID获取</strong>：区域ID、学校ID、年级ID、班级ID请在"组织架构管理"页面查看（见下方说明）</li>
            <li>• 角色可选值：管理员、教研员、教师、学生</li>
            <li>• 班级角色可选值：学生、正班主任、副班主任、任课教师、班干部</li>
          </ul>
        </div>
        
        <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h4 class="font-medium text-gray-900 mb-2">模板字段说明</h4>
          <div class="text-sm text-gray-700 space-y-2">
            <div>
              <strong>必需字段（创建新用户时）：</strong>
              <div class="mt-1 font-mono text-xs bg-white p-2 rounded border">
                学号/用户名, 邮箱, 密码
              </div>
            </div>
            <div>
              <strong>用户匹配字段（至少提供一个）：</strong>
              <div class="mt-1 font-mono text-xs bg-white p-2 rounded border">
                学籍号（推荐）, 学号/用户名, 邮箱, 姓名
              </div>
            </div>
            <div>
              <strong>完整字段列表：</strong>
              <div class="mt-1 font-mono text-xs bg-white p-2 rounded border">
                学籍号, 学号/用户名, 姓名, 邮箱, 密码, 角色, 是否激活, 区域ID, 学校ID, 年级ID, 班级ID, 座号, 班级角色, 职务名称, 主班级, 班级学号
              </div>
              <p class="mt-1 text-xs text-gray-600">
                💡 <strong>提示：</strong>组织架构ID（区域ID、学校ID、年级ID、班级ID）为可选字段，详见下方的"组织架构ID获取方式"说明
              </p>
            </div>
          </div>
        </div>
        
        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h4 class="font-medium text-yellow-900 mb-2">📌 组织架构ID获取方式</h4>
          <div class="text-sm text-yellow-800 space-y-3">
            <p><strong>区域ID、学校ID、年级ID、班级ID</strong>等组织架构信息可以通过以下方式获取：</p>
            
            <div>
              <p class="font-semibold mb-1">1. 区域ID、学校ID、班级ID：</p>
              <ul class="list-disc list-inside space-y-1 ml-2 text-xs">
                <li>访问 <strong>管理员后台 → 组织架构管理</strong> 页面</li>
                <li>在组织架构管理页面中，<strong>每个组织单位的ID会显示在列表中</strong>（通常在表格的第一列或详情页面）</li>
                <li><strong>班级ID说明：</strong>
                  <div class="mt-1 ml-4 p-2 bg-white rounded border border-blue-200 text-xs">
                    • 班级ID是数据库中的数字ID，需要在组织架构管理页面的班级列表中查看<br/>
                    • 班级编码（code）格式为"入学年份+班级编号"，例如：202501（表示2025年入学的01班）<br/>
                    • <strong>导入时填写的是班级ID（数字），不是班级编码</strong><br/>
                    • 班级编码仅用于显示和识别，不能用作导入时的ID
                  </div>
                </li>
              </ul>
            </div>
            
            <div>
              <p class="font-semibold mb-1">2. 年级ID（重要）：</p>
              <ul class="list-disc list-inside space-y-1 ml-2 text-xs">
                <li>方法一：访问 <strong>管理员后台 → 课程管理</strong> 页面，在课程树结构中可以看到年级信息</li>
                <li>方法二：在 <strong>组织架构管理 → 创建/编辑班级</strong> 时，年级下拉选择框中会显示"年级名称 (ID: 年级ID)"格式，可直接看到年级ID</li>
                <li>方法三：系统标准年级ID对应关系（按顺序递增）：
                  <div class="mt-1 ml-4 p-2 bg-white rounded border border-yellow-200 text-xs">
                    <div class="font-mono space-y-0.5">
                      <div>一年级 → ID: 1 | 二年级 → ID: 2 | 三年级 → ID: 3</div>
                      <div>四年级 → ID: 4 | 五年级 → ID: 5 | 六年级 → ID: 6</div>
                      <div>七年级 → ID: 7 | 八年级 → ID: 8 | 九年级 → ID: 9</div>
                      <div>高一 → ID: 10 | 高二 → ID: 11 | 高三 → ID: 12</div>
                      <div>未分类 → ID: 13</div>
                    </div>
                    <div class="text-gray-600 mt-2 text-xs">💡 提示：年级ID从1开始按顺序递增，与年级级别（level）基本一致</div>
                  </div>
                </li>
              </ul>
            </div>
            
            <div class="mt-2 p-2 bg-white rounded border border-yellow-300">
              <p class="text-xs font-semibold mb-1"><strong>ID示例：</strong></p>
              <p class="text-xs">区域ID: 1 | 学校ID: 101 | 年级ID: 3（三年级）| 班级ID: 5（数据库数字ID）</p>
              <p class="text-xs text-gray-600 mt-1">
                💡 <strong>提示：</strong>这些字段为<strong>可选字段</strong>，如果用户不属于特定组织，可以留空<br/>
                💡 <strong>注意：</strong>班级ID是数据库中的数字ID（如：5），不是班级编码（如：202501），请在"组织架构管理"页面查看班级ID
              </p>
            </div>
          </div>
        </div>
        
        <div class="flex justify-center">
          <button
            @click="downloadTemplate"
            class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
          >
            <span class="mr-2">📥</span>
            下载统一导入模板
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
            ref="fileInputRef"
            type="file"
            accept=".csv,.xlsx,.xls"
            @change="handleFileSelect"
            class="hidden"
          />
          <div v-if="!selectedFile" @click="triggerFileSelect" class="cursor-pointer">
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
              @click="resetSelectedFile"
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
          <p class="text-gray-600">正在导入数据，请稍候...</p>
        </div>
        
        <div v-else-if="importResult" class="space-y-4">
          <div class="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 class="font-medium text-green-900 mb-2">✅ 导入完成</h4>
            <p class="text-sm text-green-800">
              {{ importResult.message }}
            </p>
            <p class="text-sm text-green-700 mt-2">
              成功: {{ importResult.success_count }} 个，失败: {{ importResult.error_count }} 个
            </p>
            <p class="text-sm text-green-700">
              创建/更新用户: {{ importResult.created_user_count }} 个，添加到班级: {{ importResult.added_member_count }} 个
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
            <h4 class="font-medium text-blue-900 mb-2">👥 创建/更新的用户</h4>
            <div class="max-h-32 overflow-y-auto">
              <ul class="text-sm text-blue-800 space-y-1">
                <li v-for="user in importResult.created_users" :key="user.id">
                  • {{ user.username }} ({{ user.email }}) - {{ getRoleDisplayName(user.role) }}
                </li>
              </ul>
            </div>
          </div>
          
          <div v-if="importResult.added_members.length > 0" class="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <h4 class="font-medium text-purple-900 mb-2">🏫 添加到班级的成员</h4>
            <div class="max-h-32 overflow-y-auto">
              <ul class="text-sm text-purple-800 space-y-1">
                <li v-for="member in importResult.added_members" :key="`${member.user_id}-${member.classroom_id}`">
                  • {{ member.username }} ({{ member.full_name || '未设置姓名' }}) → {{ member.classroom_name || `班级${member.classroom_id}` }}
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <div v-else class="space-y-4">
          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h4 class="font-medium text-yellow-900 mb-2">⚠️ 确认导入</h4>
            <p class="text-sm text-yellow-800">
              即将导入文件 <strong>{{ selectedFile?.name }}</strong> 中的数据。
            </p>
            <p class="text-sm text-yellow-800 mt-2">
              系统将自动：创建新用户、更新已存在用户、添加到班级（如果提供了班级ID）。
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
import adminService, { type UnifiedImportItem, type UnifiedImportResult } from '@/services/admin'
import * as XLSX from 'xlsx'
import GBK from 'gbk.js'

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
const importResult = ref<UnifiedImportResult | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

const HEADER_MAP: Record<string, string | null> = {
  // 用户标识字段
  student_id_number: 'student_id_number',
  学籍号: 'student_id_number',
  学籍编号: 'student_id_number',
  username: 'username',
  用户名: 'username',
  '学号/用户名': 'username',
  学号: 'username',
  email: 'email',
  邮箱: 'email',
  full_name: 'full_name',
  姓名: 'full_name',
  name: 'full_name',
  // 用户创建/更新字段
  password: 'password',
  密码: 'password',
  role: 'role',
  角色: 'role',
  is_active: 'is_active',
  '是否激活': 'is_active',
  '激活状态': 'is_active',
  // 组织信息
  region_id: 'region_id',
  '区域ID': 'region_id',
  '区域ID(可选)': 'region_id',
  school_id: 'school_id',
  '学校ID': 'school_id',
  '学校ID(可选)': 'school_id',
  grade_id: 'grade_id',
  '年级ID': 'grade_id',
  '年级ID(可选)': 'grade_id',
  classroom_id: 'classroom_id',
  '班级ID': 'classroom_id',
  '班级ID(可选)': 'classroom_id',
  // 班级成员信息
  seat_no: 'seat_no',
  座号: 'seat_no',
  role_in_class: 'role_in_class',
  班级角色: 'role_in_class',
  cadre_title: 'cadre_title',
  职务名称: 'cadre_title',
  职务: 'cadre_title',
  is_primary_class: 'is_primary_class',
  主班级: 'is_primary_class',
  student_no: 'student_no',
  班级学号: 'student_no',
  备注: null,
  说明: null,
  remark: null,
}

const ROLE_MAP: Record<string, string> = {
  admin: 'admin',
  管理员: 'admin',
  teacher: 'teacher',
  教师: 'teacher',
  student: 'student',
  学生: 'student',
  researcher: 'researcher',
  教研员: 'researcher',
}

function normalizeHeader(header: string): string | null {
  const cleaned = header.replace(/^["']|["']$/g, '').trim()
  
  if (Object.prototype.hasOwnProperty.call(HEADER_MAP, cleaned)) {
    return HEADER_MAP[cleaned]
  }
  
  const withoutBrackets = cleaned.replace(/\([^)]*\)/g, '').trim()
  if (withoutBrackets !== cleaned && Object.prototype.hasOwnProperty.call(HEADER_MAP, withoutBrackets)) {
    return HEADER_MAP[withoutBrackets]
  }
  
  return cleaned || null
}

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

function triggerFileSelect() {
  fileInputRef.value?.click()
}

function resetSelectedFile() {
  selectedFile.value = null
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
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
    const result = await adminService.getUnifiedImportTemplate()
    
    const blob = new Blob([result.template], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', result.filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
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
    
    if (file.size > 5 * 1024 * 1024) {
      toast.error('文件大小不能超过5MB')
      return
    }
    
    selectedFile.value = file
  }
}

function readFileAsText(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    
    reader.onload = async (e) => {
      try {
        const arrayBuffer = e.target?.result as ArrayBuffer
        if (!arrayBuffer) {
          reject(new Error('文件读取失败'))
          return
        }
        
        try {
          const utf8Text = new TextDecoder('utf-8', { fatal: true }).decode(arrayBuffer)
          const hasReplacementChar = utf8Text.slice(0, 200).includes('\uFFFD')
          const hasChinese = /[\u4e00-\u9fa5]/.test(utf8Text.slice(0, 200))
          const hasGarbledPattern = /[^\u0000-\u007F\u4e00-\u9fa5\s，。！？：；""''（）【】《》、]/.test(utf8Text.slice(0, 200))
          
          if (!hasReplacementChar && (!hasGarbledPattern || hasChinese)) {
            resolve(utf8Text)
            return
          }
        } catch (e) {
          // UTF-8 解码失败，继续尝试 GBK
        }
        
        try {
          const uint8Array = new Uint8Array(arrayBuffer)
          const gbkText = GBK.toString(uint8Array)
          if (/[\u4e00-\u9fa5]/.test(gbkText.slice(0, 200))) {
            resolve(gbkText)
            return
          }
        } catch (gbkError) {
          // GBK 解码失败
        }
        
        const utf8Text = new TextDecoder('utf-8', { fatal: false }).decode(arrayBuffer)
        resolve(utf8Text)
      } catch (error: any) {
        reject(new Error(`文件读取失败: ${error.message}`))
      }
    }
    
    reader.onerror = () => reject(new Error('文件读取失败'))
    reader.readAsArrayBuffer(file)
  })
}

function parseCSVLine(line: string): string[] {
  const result: string[] = []
  let current = ''
  let inQuotes = false
  
  for (let i = 0; i < line.length; i++) {
    const char = line[i]
    
    if (char === '"') {
      if (inQuotes && line[i + 1] === '"') {
        current += '"'
        i++
      } else {
        inQuotes = !inQuotes
      }
    } else if (char === ',' && !inQuotes) {
      result.push(current.trim())
      current = ''
    } else {
      current += char
    }
  }
  
  result.push(current.trim())
  return result
}

function parseCSV(csvText: string): UnifiedImportItem[] {
  let text = csvText
  if (text.charCodeAt(0) === 0xFEFF) {
    text = text.slice(1)
  }
  
  const lines = text.trim().split(/\r?\n/).filter(line => line.trim() && !line.trim().startsWith('#'))
  if (lines.length === 0) {
    throw new Error('CSV文件为空')
  }
  
  const firstLine = lines[0]
  const hasTabs = firstLine.includes('\t')
  const delimiter = hasTabs ? '\t' : ','
  
  const parseLine = delimiter === '\t' 
    ? (line: string) => line.split('\t').map(h => h.trim())
    : parseCSVLine
  
  const originalHeaders = parseLine(lines[0]).map(h => h.replace(/^"|"$/g, '').trim())
  const normalizedHeaders = originalHeaders.map(normalizeHeader)
  
  const parseBoolean = (value: string, rowNumber: number) => {
    const normalized = value.trim().toLowerCase()
    if (['true', '1', 'yes', 'y', '是', '激活'].includes(normalized)) return true
    if (['false', '0', 'no', 'n', '', '否', '未激活'].includes(normalized)) return false
    throw new Error(`第${rowNumber}行 is_active 列只能填写 true/false`)
  }
  
  const parseOptionalNumber = (value: string | undefined, column: string, rowNumber: number) => {
    if (value === undefined || value === null || value === '') {
      return undefined
    }
    const parsed = Number(value)
    if (Number.isNaN(parsed)) {
      throw new Error(`第${rowNumber}行 ${column} 列必须填写数字ID或留空`)
    }
    return parsed
  }

  const items: UnifiedImportItem[] = []
  
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim()
    if (!line) continue
    const rowNumber = i + 1
    
    const values = parseLine(line).map(v => v.replace(/^"|"$/g, '').trim())
    if (values.length !== normalizedHeaders.length) {
      throw new Error(`第${rowNumber}行数据列数不匹配，期望 ${normalizedHeaders.length} 列，实际 ${values.length} 列`)
    }
    
    const item: any = {}
    normalizedHeaders.forEach((_, index) => {
      const normalizedHeader = normalizeHeader(originalHeaders[index])
      if (!normalizedHeader) {
        return
      }
      item[normalizedHeader] = values[index]
    })
    
    const roleValue = item.role ? String(item.role).trim().toLowerCase() : undefined
    const normalizedRole = roleValue && ROLE_MAP[roleValue] ? ROLE_MAP[roleValue] : undefined

    items.push({
      student_id_number: item.student_id_number ? String(item.student_id_number).trim() : undefined,
      username: item.username ? String(item.username).trim() : undefined,
      email: item.email ? String(item.email).trim() : undefined,
      full_name: item.full_name ? String(item.full_name).trim() : undefined,
      password: item.password ? String(item.password).trim() : undefined,
      role: normalizedRole,
      is_active: item.is_active !== undefined ? parseBoolean(String(item.is_active), rowNumber) : undefined,
      region_id: parseOptionalNumber(item.region_id, 'region_id', rowNumber),
      school_id: parseOptionalNumber(item.school_id, 'school_id', rowNumber),
      grade_id: parseOptionalNumber(item.grade_id, 'grade_id', rowNumber),
      classroom_id: parseOptionalNumber(item.classroom_id, 'classroom_id', rowNumber),
      seat_no: parseOptionalNumber(item.seat_no, 'seat_no', rowNumber),
      role_in_class: item.role_in_class ? String(item.role_in_class).trim() : undefined,
      cadre_title: item.cadre_title ? String(item.cadre_title).trim() : undefined,
      is_primary_class: item.is_primary_class !== undefined ? (String(item.is_primary_class).toLowerCase() === 'true') : undefined,
      student_no: item.student_no ? String(item.student_no).trim() : undefined,
    })
  }
  
  return items
}

async function parseExcel(file: File): Promise<UnifiedImportItem[]> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target?.result as ArrayBuffer)
        const workbook = XLSX.read(data, { type: 'array' })
        
        const firstSheetName = workbook.SheetNames[0]
        const worksheet = workbook.Sheets[firstSheetName]
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 }) as any[][]
        
        if (jsonData.length < 2) {
          throw new Error('Excel文件为空或格式不正确')
        }
        
        const originalHeaders = jsonData[0].map(h => String(h).trim())
        const normalizedHeaders = originalHeaders.map(normalizeHeader)
        
        const parseBoolean = (value: string, rowNumber: number) => {
          const normalized = String(value).trim().toLowerCase()
          if (['true', '1', 'yes', 'y', '是', '激活'].includes(normalized)) return true
          if (['false', '0', 'no', 'n', '', '否', '未激活'].includes(normalized)) return false
          throw new Error(`第${rowNumber}行 is_active 列只能填写 true/false`)
        }
        
        const parseOptionalNumber = (value: string | undefined, column: string, rowNumber: number) => {
          if (value === undefined || value === null || value === '') {
            return undefined
          }
          const parsed = Number(value)
          if (Number.isNaN(parsed)) {
            throw new Error(`第${rowNumber}行 ${column} 列必须填写数字ID或留空`)
          }
          return parsed
        }

        const items: UnifiedImportItem[] = []
        
        for (let i = 1; i < jsonData.length; i++) {
          const row = jsonData[i]
          if (!row || row.length === 0) continue
          const rowNumber = i + 1
          
          const item: any = {}
          normalizedHeaders.forEach((_, index) => {
            const normalizedHeader = normalizeHeader(originalHeaders[index])
            if (!normalizedHeader) {
              return
            }
            item[normalizedHeader] = row[index] !== undefined ? String(row[index]).trim() : ''
          })
          
          const roleValue = item.role ? String(item.role).trim().toLowerCase() : undefined
          const normalizedRole = roleValue && ROLE_MAP[roleValue] ? ROLE_MAP[roleValue] : undefined

          items.push({
            student_id_number: item.student_id_number ? String(item.student_id_number).trim() : undefined,
            username: item.username ? String(item.username).trim() : undefined,
            email: item.email ? String(item.email).trim() : undefined,
            full_name: item.full_name ? String(item.full_name).trim() : undefined,
            password: item.password ? String(item.password).trim() : undefined,
            role: normalizedRole,
            is_active: item.is_active !== undefined ? parseBoolean(String(item.is_active), rowNumber) : undefined,
            region_id: parseOptionalNumber(item.region_id, 'region_id', rowNumber),
            school_id: parseOptionalNumber(item.school_id, 'school_id', rowNumber),
            grade_id: parseOptionalNumber(item.grade_id, 'grade_id', rowNumber),
            classroom_id: parseOptionalNumber(item.classroom_id, 'classroom_id', rowNumber),
            seat_no: parseOptionalNumber(item.seat_no, 'seat_no', rowNumber),
            role_in_class: item.role_in_class ? String(item.role_in_class).trim() : undefined,
            cadre_title: item.cadre_title ? String(item.cadre_title).trim() : undefined,
            is_primary_class: item.is_primary_class !== undefined ? (String(item.is_primary_class).toLowerCase() === 'true') : undefined,
            student_no: item.student_no ? String(item.student_no).trim() : undefined,
          })
        }
        
        if (items.length === 0) {
          throw new Error('没有找到有效的数据')
        }
        
        resolve(items)
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

async function startImport() {
  if (!selectedFile.value) return
  
  importing.value = true
  importResult.value = null
  
  try {
    let items: UnifiedImportItem[]
    
    const fileName = selectedFile.value.name.toLowerCase()
    if (fileName.endsWith('.csv')) {
      const csvText = await readFileAsText(selectedFile.value)
      items = parseCSV(csvText)
    } else if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
      items = await parseExcel(selectedFile.value)
    } else {
      throw new Error('不支持的文件格式')
    }
    
    const result = await adminService.unifiedImport(items)
    importResult.value = result
    
    if (result.success_count > 0) {
      toast.success(`成功导入 ${result.success_count} 条数据`)
      emit('success')
    }
    
    if (result.error_count > 0) {
      toast.warning(`${result.error_count} 条数据导入失败`)
    }
    
  } catch (error: any) {
    console.error('Failed to import:', error)
    toast.error(error.message || error.response?.data?.detail || '导入失败')
  } finally {
    importing.value = false
  }
}
</script>
