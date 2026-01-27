<template>
  <div v-if="show" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-3xl max-h-[90vh] flex flex-col">
      <!-- Header -->
      <div class="px-6 py-4 border-b flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-900">批量导入班级成员</h3>
        <button @click="close" class="text-gray-500 hover:text-gray-700">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-6 space-y-4">
        <!-- 步骤1: 说明 -->
        <div v-if="currentStep === 1" class="space-y-4">
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 class="font-medium text-blue-900 mb-2">📋 导入说明</h4>
            <ul class="text-sm text-blue-800 space-y-1 list-disc list-inside">
              <li>支持 CSV 或 Excel 文件（.csv, .xlsx, .xls）</li>
              <li><strong>用户匹配字段</strong>（至少提供一个）：</li>
              <li class="ml-4">✨ <strong>学籍号</strong>（<span class="text-red-600 font-bold">强烈推荐</span>）- 唯一标识，跟随学生整个学习经历，不会改变</li>
              <li class="ml-4">其他可选：姓名、邮箱、用户名、学号（班级内）、用户ID</li>
              <li><strong>可选字段</strong>：座号、角色、职务名称、主班级</li>
              <li>如果用户已是班级成员，将被跳过</li>
              <li>建议先导出模板，按照模板格式填写数据</li>
            </ul>
          </div>

          <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 class="font-medium text-gray-900 mb-2">文件格式要求</h4>
            <div class="text-sm text-gray-700 space-y-2">
              <div>
                <strong>表头字段（建议顺序）：</strong>
                <div class="mt-1 font-mono text-xs bg-white p-2 rounded border">
                  学籍号, 姓名, 学号, 邮箱, 用户名, 座号, 角色, 职务名称, 主班级
                </div>
              </div>
              <div class="text-xs text-red-600 bg-red-50 border border-red-200 rounded p-2 mt-2">
                ⚠️ <strong>重要提示：</strong><br/>
                1. <strong>学籍号</strong>是学生的唯一标识，跟随整个学习经历，<strong>强烈推荐使用</strong><br/>
                2. <strong>学号</strong>是班级内的学号，可能与学籍号不同<br/>
                3. 用户匹配字段至少需要填写一个，推荐填写<strong>学籍号</strong>，匹配最准确
              </div>
              <div>
                <strong>角色可选值：</strong>学生、正班主任、副班主任、任课教师、班干部
              </div>
              <div class="mt-2">
                <strong>主班级：</strong>true 或 false（可选，默认 false）
                <div class="text-xs text-gray-600 mt-1 bg-blue-50 border border-blue-200 rounded p-2">
                  💡 <strong>主班级说明：</strong><br/>
                  • 当一个学生同时属于多个班级时，标记为"主班级"的班级会作为默认班级使用<br/>
                  • 系统在查询学生统计信息、显示班级信息时会优先使用主班级的数据<br/>
                  • 如果学生只属于一个班级，建议设置为 <strong>true</strong><br/>
                  • 如果学生属于多个班级，建议将最重要的班级（如主修班）标记为主班级
                </div>
              </div>
            </div>
          </div>

          <div class="flex justify-between">
            <button
              @click="downloadTemplate"
              class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              📥 下载模板
            </button>
            <button
              @click="currentStep = 2"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
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
            <p class="text-gray-600">正在导入，请稍候...</p>
          </div>
          
          <div v-else-if="importResult" class="space-y-4">
            <div class="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 class="font-medium text-green-900 mb-2">✅ 导入完成</h4>
              <p class="text-sm text-green-800">
                {{ importResult.message }}
              </p>
              <p class="text-sm text-green-700 mt-2">
                成功: {{ importResult.successCount }} 个，失败: {{ importResult.errorCount }} 个
              </p>
            </div>
            
            <div v-if="importResult.errors && importResult.errors.length > 0" class="bg-red-50 border border-red-200 rounded-lg p-4 max-h-48 overflow-y-auto">
              <h4 class="font-medium text-red-900 mb-2">❌ 错误信息</h4>
              <ul class="text-sm text-red-800 space-y-1">
                <li v-for="(error, index) in importResult.errors" :key="index">{{ error }}</li>
              </ul>
            </div>
          </div>
          
          <div v-else class="space-y-4">
            <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h4 class="font-medium text-yellow-900 mb-2">⚠️ 确认导入</h4>
              <p class="text-sm text-yellow-800">
                即将导入文件 <strong>{{ selectedFile?.name }}</strong> 中的班级成员数据。
                请确认文件格式正确，每行至少包含一个用户标识字段（<strong>学籍号（推荐）</strong>、姓名、邮箱、用户名、学号或用户ID）。
              </p>
              <p class="text-xs text-yellow-700 mt-2">
                💡 提示：使用<strong>学籍号</strong>匹配最准确，学籍号是学生的唯一标识，跟随整个学习经历。
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
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useToast } from '@/composables/useToast'
import { classroomAssistantService } from '@/services/classroomAssistant'
import type { ClassroomMemberBatchImportRequest, ClassroomMemberBatchImportResponse, ClassroomMemberBatchItem } from '@/types/classroomAssistant'
import { RoleInClass } from '@/types/classroomAssistant'
import * as XLSX from 'xlsx'

const props = defineProps<{
  show: boolean
  classroomId: number
}>()

const emit = defineEmits<{
  close: []
  success: []
}>()

const toast = useToast()

const currentStep = ref(1)
const selectedFile = ref<File | null>(null)
const importing = ref(false)
const importResult = ref<ClassroomMemberBatchImportResponse | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

function close() {
  currentStep.value = 1
  selectedFile.value = null
  importResult.value = null
  emit('close')
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

function downloadTemplate() {
  // 创建CSV模板
  const headers = ['学籍号', '姓名', '学号', '邮箱', '用户名', '座号', '角色', '职务名称', '主班级']
  const exampleRow = ['2024001001', '张三', '2024001', 'zhangsan@example.com', 'zhangsan', '1', '学生', '', 'false']
  const csvContent = [
    headers.join(','),
    exampleRow.join(','),
    '# 说明：至少需要填写一个用户匹配字段',
    '# 学籍号（强烈推荐）：唯一标识，跟随学生整个学习经历，不会改变',
    '# 学号：班级内的学号，可能与学籍号不同',
    '# 角色可选值：学生、正班主任、副班主任、任课教师、班干部',
    '# 主班级：true 或 false（默认 false）',
    '#   主班级说明：当一个学生同时属于多个班级时，标记为"主班级"的班级会作为默认班级使用。',
    '#   如果学生只属于一个班级，建议设置为 true；如果属于多个班级，建议将最重要的班级标记为主班级。',
    '# 注意：用户ID字段已被移除，系统会根据提供的学籍号、姓名、学号、邮箱或用户名自动匹配用户'
  ].join('\n')
  
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', '班级成员导入模板.csv')
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  toast.success('模板下载成功')
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

function normalizeHeader(header: string): string | null {
  const cleaned = header.replace(/^["']|["']$/g, '').trim()
  const headerMap: Record<string, string> = {
    // 用户匹配字段
    '用户ID': 'userId',
    '用户id': 'userId',
    'user_id': 'userId',
    'userId': 'userId',
    '学籍号': 'studentIdNumber',
    '学籍编号': 'studentIdNumber',
    'student_id_number': 'studentIdNumber',
    'studentIdNumber': 'studentIdNumber',
    '姓名': 'fullName',
    'full_name': 'fullName',
    'fullName': 'fullName',
    '邮箱': 'email',
    'email': 'email',
    '用户名': 'username',
    'username': 'username',
    '学号': 'studentNo',
    'student_no': 'studentNo',
    'studentNo': 'studentNo',
    // 班级成员信息
    '座号': 'seatNo',
    'seat_no': 'seatNo',
    'seatNo': 'seatNo',
    '角色': 'roleInClass',
    'role_in_class': 'roleInClass',
    'roleInClass': 'roleInClass',
    '职务名称': 'cadreTitle',
    '职务': 'cadreTitle',
    'cadre_title': 'cadreTitle',
    'cadreTitle': 'cadreTitle',
    '主班级': 'isPrimaryClass',
    'is_primary_class': 'isPrimaryClass',
    'isPrimaryClass': 'isPrimaryClass',
  }
  return headerMap[cleaned] || null
}

function parseRole(roleStr: string): RoleInClass {
  const roleMap: Record<string, RoleInClass> = {
    '学生': RoleInClass.STUDENT,
    '正班主任': RoleInClass.HEAD_TEACHER_PRIMARY,
    '副班主任': RoleInClass.HEAD_TEACHER_DEPUTY,
    '任课教师': RoleInClass.SUBJECT_TEACHER,
    '班干部': RoleInClass.CADRE,
  }
  return roleMap[roleStr.trim()] || RoleInClass.STUDENT
}

function parseCSV(csvText: string): ClassroomMemberBatchItem[] {
  const lines = csvText.split('\n').filter(line => line.trim() && !line.trim().startsWith('#'))
  if (lines.length < 2) {
    throw new Error('CSV文件格式不正确，至少需要表头和数据行')
  }
  
  const headerLine = lines[0]
  const headers = headerLine.split(',').map(h => h.trim())
  const normalizedHeaders = headers.map(normalizeHeader)
  
  const members: ClassroomMemberBatchItem[] = []
  
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim()
    if (!line) continue
    
    const values = line.split(',').map(v => v.trim().replace(/^["']|["']$/g, ''))
    const row: any = {}
    
    normalizedHeaders.forEach((header, index) => {
      if (header) {
        row[header] = values[index] || ''
      }
    })
    
    // 检查至少提供了一个用户标识字段
    const hasUserId = row.userId && String(row.userId).trim() && !isNaN(parseInt(String(row.userId)))
    const hasStudentIdNumber = row.studentIdNumber && String(row.studentIdNumber).trim()
    const hasFullName = row.fullName && String(row.fullName).trim()
    const hasEmail = row.email && String(row.email).trim()
    const hasUsername = row.username && String(row.username).trim()
    const hasStudentNo = row.studentNo && String(row.studentNo).trim()
    
    if (!hasUserId && !hasStudentIdNumber && !hasFullName && !hasEmail && !hasUsername && !hasStudentNo) {
      throw new Error(`第${i + 1}行：至少需要提供一个用户标识字段（用户ID、学籍号、姓名、邮箱、用户名或学号）`)
    }
    
    const member: ClassroomMemberBatchItem = {
      userId: hasUserId ? parseInt(String(row.userId)) : undefined,
      studentIdNumber: hasStudentIdNumber ? String(row.studentIdNumber).trim() : undefined,
      fullName: hasFullName ? row.fullName.trim() : undefined,
      email: hasEmail ? row.email.trim() : undefined,
      username: hasUsername ? row.username.trim() : undefined,
      studentNo: hasStudentNo ? row.studentNo.trim() : undefined,
      roleInClass: row.roleInClass ? parseRole(row.roleInClass) : RoleInClass.STUDENT,
      seatNo: row.seatNo ? parseInt(row.seatNo) : undefined,
      cadreTitle: row.cadreTitle || undefined,
      isPrimaryClass: row.isPrimaryClass === 'true' || row.isPrimaryClass === true || false,
    }
    
    members.push(member)
  }
  
  return members
}

async function parseExcel(file: File): Promise<ClassroomMemberBatchItem[]> {
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
        
        const headers = jsonData[0].map(h => String(h).trim())
        const normalizedHeaders = headers.map(normalizeHeader)
        
        const members: ClassroomMemberBatchItem[] = []
        
        for (let i = 1; i < jsonData.length; i++) {
          const row = jsonData[i]
          if (!row || row.length === 0) continue
          
          const rowData: any = {}
          normalizedHeaders.forEach((header, index) => {
            if (header && row[index] !== undefined) {
              rowData[header] = String(row[index]).trim()
            }
          })
          
          // 检查至少提供了一个用户标识字段
          const hasUserId = rowData.userId && String(rowData.userId).trim() && !isNaN(parseInt(String(rowData.userId)))
          const hasStudentIdNumber = rowData.studentIdNumber && String(rowData.studentIdNumber).trim()
          const hasFullName = rowData.fullName && String(rowData.fullName).trim()
          const hasEmail = rowData.email && String(rowData.email).trim()
          const hasUsername = rowData.username && String(rowData.username).trim()
          const hasStudentNo = rowData.studentNo && String(rowData.studentNo).trim()
          
          if (!hasUserId && !hasStudentIdNumber && !hasFullName && !hasEmail && !hasUsername && !hasStudentNo) {
            throw new Error(`第${i + 1}行：至少需要提供一个用户标识字段（用户ID、学籍号、姓名、邮箱、用户名或学号）`)
          }
          
          const member: ClassroomMemberBatchItem = {
            userId: hasUserId ? parseInt(String(rowData.userId)) : undefined,
            studentIdNumber: hasStudentIdNumber ? String(rowData.studentIdNumber).trim() : undefined,
            fullName: hasFullName ? rowData.fullName.trim() : undefined,
            email: hasEmail ? rowData.email.trim() : undefined,
            username: hasUsername ? rowData.username.trim() : undefined,
            studentNo: hasStudentNo ? rowData.studentNo.trim() : undefined,
            roleInClass: rowData.roleInClass ? parseRole(rowData.roleInClass) : RoleInClass.STUDENT,
            seatNo: rowData.seatNo ? parseInt(rowData.seatNo) : undefined,
            cadreTitle: rowData.cadreTitle || undefined,
            isPrimaryClass: rowData.isPrimaryClass === 'true' || rowData.isPrimaryClass === true || false,
          }
          
          members.push(member)
        }
        
        if (members.length === 0) {
          throw new Error('没有找到有效的成员数据')
        }
        
        resolve(members)
      } catch (error: any) {
        reject(error)
      }
    }
    
    reader.onerror = () => reject(new Error('文件读取失败'))
    reader.readAsArrayBuffer(file)
  })
}

async function startImport() {
  if (!selectedFile.value) return
  
  importing.value = true
  importResult.value = null
  
  try {
    let members: ClassroomMemberBatchItem[]
    
    const fileName = selectedFile.value.name.toLowerCase()
    if (fileName.endsWith('.csv')) {
      const csvText = await readFileAsText(selectedFile.value)
      members = parseCSV(csvText)
    } else if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
      members = await parseExcel(selectedFile.value)
    } else {
      throw new Error('不支持的文件格式')
    }
    
    const request: ClassroomMemberBatchImportRequest = { members }
    const result = await classroomAssistantService.batchImportClassroomMembers(props.classroomId, request)
    importResult.value = result
    
    if (result.successCount > 0) {
      toast.success(`成功导入 ${result.successCount} 个成员`)
      emit('success')
    }
    
    if (result.errorCount > 0) {
      toast.warning(`${result.errorCount} 个成员导入失败`)
    }
    
  } catch (error: any) {
    console.error('Failed to import members:', error)
    toast.error(error.message || error.response?.data?.detail || '导入失败')
  } finally {
    importing.value = false
  }
}

function readFileAsText(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => resolve(e.target?.result as string)
    reader.onerror = () => reject(new Error('文件读取失败'))
    reader.readAsText(file, 'UTF-8')
  })
}
</script>

