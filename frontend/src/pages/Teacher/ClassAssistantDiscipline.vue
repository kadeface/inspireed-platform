<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50/30 to-teal-50/50">
    <DashboardHeader
      title="纪律记录"
      subtitle="记录课堂纪律事件，形成可回顾的数据"
      :user-name="userName"
      :region-name="regionName"
      :school-name="schoolName"
      :grade-name="gradeName"
      @logout="handleLogout"
    >
      <template #default>
        <div class="flex items-center gap-3 flex-wrap">
          <button
            @click="showRecordModal = true"
            class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-amber-500 to-orange-600 rounded-xl shadow-lg hover:shadow-xl transition-all"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            记录纪律
          </button>
          <button
            @click="handleBack"
            class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-xl hover:bg-white hover:shadow-md transition-all"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            返回
          </button>
        </div>
      </template>
    </DashboardHeader>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 记录列表 -->
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-lg overflow-hidden">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h2 class="text-lg font-bold text-gray-900">纪律记录列表</h2>
          <div class="flex gap-2">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索学生..."
              class="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
            />
          </div>
        </div>
        <div class="p-6">
          <div v-if="loading" class="text-center py-8 text-gray-500">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-600 mx-auto mb-2"></div>
            加载中...
          </div>
          <div v-else-if="filteredRecords.length === 0" class="text-center py-8 text-gray-500">
            暂无记录
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="record in filteredRecords"
              :key="record.id"
              class="flex items-center justify-between p-4 border border-gray-200 rounded-xl hover:shadow-md transition-all"
            >
              <div class="flex items-center gap-4 flex-1">
                <div class="w-12 h-12 rounded-full bg-amber-100 flex items-center justify-center">
                  <svg class="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div class="flex-1">
                  <p class="font-medium text-gray-900">{{ getStudentName(record.studentId) }}</p>
                  <p class="text-sm text-gray-600">{{ getEventTypeName(record.eventType) }}</p>
                  <p v-if="record.note" class="text-xs text-gray-500 mt-1">{{ record.note }}</p>
                </div>
                <div class="text-right">
                  <p class="text-xs text-gray-500">{{ formatDate(record.recordedAt) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 记录模态框 -->
    <div
      v-if="showRecordModal"
      class="fixed inset-0 z-50 overflow-y-auto"
      @click.self="showRecordModal = false"
    >
      <div class="flex min-h-screen items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50"></div>
        <div class="relative w-full max-w-md bg-white rounded-2xl shadow-2xl p-6">
          <h3 class="text-xl font-bold text-gray-900 mb-4">记录纪律事件</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">选择学生</label>
              <select
                v-model="newRecord.studentId"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
              >
                <option value="">请选择学生</option>
                <option v-for="student in students" :key="student.id" :value="student.id">
                  {{ student.fullName || student.username }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">事件类型</label>
              <select
                v-model="selectedCategory"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500 mb-2"
              >
                <option value="">选择分类</option>
                <option v-for="category in categories" :key="category" :value="category">
                  {{ category }}
                </option>
              </select>
              <select
                v-model="newRecord.eventType"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
              >
                <option value="">请选择类型</option>
                <option
                  v-for="type in filteredEventTypes"
                  :key="type.type"
                  :value="type.type"
                >
                  {{ type.name }}
                </option>
              </select>
            </div>
            <div v-if="newRecord.eventType === 'other'">
              <label class="block text-sm font-medium text-gray-700 mb-2">自定义描述</label>
              <input
                v-model="newRecord.customEventText"
                type="text"
                placeholder="请输入事件描述"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">备注（可选，0-50字）</label>
              <textarea
                v-model="newRecord.note"
                rows="3"
                placeholder="补充说明..."
                maxlength="50"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
              ></textarea>
              <p class="text-xs text-gray-500 mt-1">{{ (newRecord.note || '').length }}/50</p>
            </div>
            <div class="flex gap-3 pt-4">
              <button
                @click="showRecordModal = false"
                class="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-all"
              >
                取消
              </button>
              <button
                @click="submitRecord"
                :disabled="!newRecord.studentId || !newRecord.eventType || saving"
                class="flex-1 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-amber-500 to-orange-600 rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
              >
                {{ saving ? '提交中...' : '提交' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import DashboardHeader from '@/components/Common/DashboardHeader.vue'
import { classroomAssistantService } from '@/services/classroomAssistant'
import type {
  DisciplineRecord,
  DisciplineEventTypeInfo,
  StudentInfo,
  DisciplineEventType,
} from '@/types/classroomAssistant'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const classroomId = computed(() => Number(route.params.classroomId))

const userName = computed(() => userStore.user?.full_name || userStore.user?.username || '')
const regionName = computed(() => userStore.user?.region_name || null)
const schoolName = computed(() => userStore.user?.school_name || null)
const gradeName = computed(() => userStore.user?.grade_name || null)

const loading = ref(false)
const saving = ref(false)
const showRecordModal = ref(false)
const searchQuery = ref('')
const selectedCategory = ref('')
const eventTypes = ref<DisciplineEventTypeInfo[]>([])
const students = ref<StudentInfo[]>([])
const records = ref<DisciplineRecord[]>([])
const newRecord = ref({
  studentId: null as number | null,
  eventType: '' as DisciplineEventType | '',
  customEventText: '',
  note: '',
})

const categories = computed(() => {
  const cats = new Set<string>()
  eventTypes.value.forEach((type) => {
    if (type.category) cats.add(type.category)
  })
  return Array.from(cats).sort()
})

const filteredEventTypes = computed(() => {
  if (!selectedCategory.value) return eventTypes.value
  return eventTypes.value.filter((type) => type.category === selectedCategory.value)
})

const filteredRecords = computed(() => {
  if (!searchQuery.value) return records.value
  return records.value.filter((r) => {
    const name = getStudentName(r.studentId).toLowerCase()
    return name.includes(searchQuery.value.toLowerCase())
  })
})

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const handleBack = () => {
  router.push('/teacher/class-assistant')
}

const loadData = async () => {
  await Promise.all([loadEventTypes(), loadStudents(), loadRecords()])
}

const loadEventTypes = async () => {
  try {
    const data = await classroomAssistantService.getDisciplineEventTypes()
    eventTypes.value = data
  } catch (error) {
    console.error('加载事件类型失败:', error)
  }
}

const loadStudents = async () => {
  try {
    const data = await classroomAssistantService.getClassroomStudents(classroomId.value)
    students.value = data
  } catch (error) {
    console.error('加载学生列表失败:', error)
  }
}

const loadRecords = async () => {
  try {
    loading.value = true
    const data = await classroomAssistantService.getDisciplineRecords(classroomId.value)
    records.value = data
  } catch (error) {
    console.error('加载记录失败:', error)
  } finally {
    loading.value = false
  }
}

const getStudentName = (studentId: number): string => {
  const student = students.value.find((s) => s.id === studentId)
  return student?.fullName || student?.username || `学生${studentId}`
}

const getEventTypeName = (type: DisciplineEventType): string => {
  const eventType = eventTypes.value.find((t) => t.type === type)
  return eventType?.name || type
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const submitRecord = async () => {
  if (!newRecord.value.studentId || !newRecord.value.eventType) return

  try {
    saving.value = true
    await classroomAssistantService.createDisciplineRecord(classroomId.value, {
      studentId: newRecord.value.studentId,
      eventType: newRecord.value.eventType as DisciplineEventType,
      customEventText: newRecord.value.customEventText || undefined,
      note: newRecord.value.note || undefined,
    })
    showRecordModal.value = false
    newRecord.value = {
      studentId: null,
      eventType: '' as DisciplineEventType | '',
      customEventText: '',
      note: '',
    }
    selectedCategory.value = ''
    await loadRecords()
  } catch (error) {
    console.error('提交记录失败:', error)
    alert('提交失败，请重试')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>
