<template>
  <div class="subject-groups-page p-6">
    <!-- 页面标题和操作栏 -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">学科教研组</h1>
        <p class="text-gray-600 mt-2">与同事协作，共享优质教学设计</p>
      </div>
      <button
        @click="showCreateModal = true"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        <i class="fas fa-plus mr-2"></i>创建教研组
      </button>
    </div>

    <!-- 统计卡片 -->
    <div v-if="statistics" class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-gray-500 text-sm">全部教研组</div>
        <div class="text-2xl font-bold text-gray-900 mt-1">
          {{ statistics.total_groups }}
        </div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-gray-500 text-sm">我的教研组</div>
        <div class="text-2xl font-bold text-blue-600 mt-1">
          {{ statistics.my_groups }}
        </div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-gray-500 text-sm">总成员数</div>
        <div class="text-2xl font-bold text-gray-900 mt-1">
          {{ statistics.total_members }}
        </div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-gray-500 text-sm">共享教学设计</div>
        <div class="text-2xl font-bold text-gray-900 mt-1">
          {{ statistics.total_shared_lessons }}
        </div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-gray-500 text-sm">我的分享</div>
        <div class="text-2xl font-bold text-green-600 mt-1">
          {{ statistics.my_shared_lessons }}
        </div>
      </div>
    </div>

    <!-- 筛选器 -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">学科</label>
          <select
            v-model="filters.subject_id"
            @change="loadGroups"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option :value="undefined">全部学科</option>
            <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
              {{ subject.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">年级</label>
          <select
            v-model="filters.grade_id"
            @change="loadGroups"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option :value="undefined">全部年级</option>
            <option v-for="grade in grades" :key="grade.id" :value="grade.id">
              {{ grade.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">范围</label>
          <select
            v-model="filters.scope"
            @change="loadGroups"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option :value="undefined">全部范围</option>
            <option value="school">校级</option>
            <option value="region">区域级</option>
            <option value="national">全国级</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">类型</label>
          <select
            v-model="filters.is_public"
            @change="loadGroups"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option :value="undefined">全部类型</option>
            <option :value="true">公开</option>
            <option :value="false">私密</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">我的教研组</label>
          <div class="flex items-center h-10">
            <input
              type="checkbox"
              v-model="filters.my_groups"
              @change="loadGroups"
              class="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
            <span class="ml-2 text-gray-700">仅显示我加入的教研组</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 教研组列表 -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      <p class="text-gray-600 mt-4">加载中...</p>
    </div>

    <div v-else-if="groups.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <i class="fas fa-users text-gray-400 text-6xl mb-4"></i>
      <p class="text-gray-600 text-lg">暂无教研组</p>
      <button
        @click="showCreateModal = true"
        class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        创建第一个教研组
      </button>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="group in groups"
        :key="group.id"
        @click="viewGroupDetail(group.id)"
        class="bg-white rounded-lg shadow hover:shadow-lg transition cursor-pointer"
      >
        <div
          v-if="group.cover_image_url"
          class="h-40 bg-cover bg-center rounded-t-lg"
          :style="{ backgroundImage: `url(${group.cover_image_url})` }"
        ></div>
        <div v-else class="h-40 bg-gradient-to-br from-blue-500 to-purple-600 rounded-t-lg"></div>
        
        <div class="p-4">
          <div class="flex items-start justify-between mb-2">
            <h3 class="text-xl font-bold text-gray-900 flex-1">{{ group.name }}</h3>
            <span
              v-if="group.user_role"
              :class="getRoleBadgeClass(group.user_role)"
              class="px-2 py-1 text-xs rounded-full ml-2"
            >
              {{ getRoleLabel(group.user_role) }}
            </span>
          </div>
          
          <p class="text-gray-600 text-sm mb-3 line-clamp-2">
            {{ group.description || '暂无描述' }}
          </p>
          
          <div class="flex items-center text-sm text-gray-500 space-x-4 mb-3">
            <span><i class="fas fa-book mr-1"></i>{{ group.subject_name }}</span>
            <span><i class="fas fa-globe mr-1"></i>{{ getScopeLabel(group.scope) }}</span>
          </div>
          
          <div class="flex items-center justify-between text-sm text-gray-500 pt-3 border-t">
            <div class="flex items-center space-x-4">
              <span><i class="fas fa-users mr-1"></i>{{ group.member_count }} 成员</span>
              <span><i class="fas fa-file-alt mr-1"></i>{{ group.lesson_count }} 教案</span>
            </div>
            <span v-if="group.is_public" class="text-green-600">
              <i class="fas fa-lock-open mr-1"></i>公开
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="mt-6 flex justify-center">
      <nav class="flex space-x-2">
        <button
          @click="currentPage > 1 && changePage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="px-3 py-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          上一页
        </button>
        <button
          v-for="page in displayPages"
          :key="page"
          @click="changePage(page)"
          :class="[
            'px-3 py-2 rounded-lg border',
            page === currentPage
              ? 'bg-blue-600 text-white border-blue-600'
              : 'border-gray-300 hover:bg-gray-50',
          ]"
        >
          {{ page }}
        </button>
        <button
          @click="currentPage < totalPages && changePage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="px-3 py-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          下一页
        </button>
      </nav>
    </div>

    <!-- 创建教研组模态框 -->
    <CreateGroupModal
      v-if="showCreateModal"
      :subjects="subjects"
      :grades="grades"
      @close="showCreateModal = false"
      @created="handleGroupCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  getSubjectGroups,
  getSubjectGroupStatistics,
} from '@/services/subjectGroup'
import { curriculumService } from '@/services/curriculum'
import type {
  SubjectGroup,
  SubjectGroupStatistics,
  GroupScope,
  MemberRole,
} from '@/types/subjectGroup'
import type { Subject } from '@/types/curriculum'
import CreateGroupModal from '@/components/SubjectGroup/CreateGroupModal.vue'

const router = useRouter()

// 数据
const groups = ref<SubjectGroup[]>([])
const statistics = ref<SubjectGroupStatistics | null>(null)
const subjects = ref<Subject[]>([])
const grades = ref<Array<{ id: number; name: string }>>([])
const loading = ref(false)
const showCreateModal = ref(false)

// 分页
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

// 筛选
const filters = ref<{
  subject_id?: number
  grade_id?: number
  scope?: GroupScope
  is_public?: boolean
  my_groups: boolean
}>({
  my_groups: false,
})

// 计算属性
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))
const displayPages = computed(() => {
  const pages: number[] = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// 方法
async function loadGroups() {
  loading.value = true
  try {
    const response = await getSubjectGroups({
      ...filters.value,
      page: currentPage.value,
      page_size: pageSize.value,
    })
    groups.value = response.items
    total.value = response.total
  } catch (error) {
    console.error('加载教研组失败:', error)
  } finally {
    loading.value = false
  }
}

async function loadStatistics() {
  try {
    statistics.value = await getSubjectGroupStatistics()
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

async function loadSubjects() {
  try {
    subjects.value = await curriculumService.getSubjects()
  } catch (error) {
    console.error('加载学科失败:', error)
  }
}

async function loadGrades() {
  try {
    const allGrades = await curriculumService.getGrades()
    grades.value = allGrades.map(g => ({ id: g.id, name: g.name }))
  } catch (error) {
    console.error('加载年级失败:', error)
  }
}

function changePage(page: number) {
  currentPage.value = page
  loadGroups()
}

function viewGroupDetail(groupId: number) {
  router.push(`/teacher/subject-groups/${groupId}`)
}

function handleGroupCreated() {
  showCreateModal.value = false
  loadGroups()
  loadStatistics()
}

function getScopeLabel(scope: GroupScope): string {
  const labels: Record<GroupScope, string> = {
    school: '校级',
    region: '区域级',
    national: '全国级',
  }
  return labels[scope] || scope
}

function getRoleLabel(role: MemberRole): string {
  const labels: Record<MemberRole, string> = {
    owner: '组长',
    admin: '管理员',
    member: '成员',
  }
  return labels[role] || role
}

function getRoleBadgeClass(role: MemberRole): string {
  const classes: Record<MemberRole, string> = {
    owner: 'bg-red-100 text-red-800',
    admin: 'bg-blue-100 text-blue-800',
    member: 'bg-gray-100 text-gray-800',
  }
  return classes[role] || 'bg-gray-100 text-gray-800'
}

// 生命周期
onMounted(() => {
  loadGroups()
  loadStatistics()
  loadSubjects()
  loadGrades()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

