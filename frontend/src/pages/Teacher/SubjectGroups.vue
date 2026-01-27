<template>
  <div class="subject-groups-page min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50/30 to-teal-50/50">
    <!-- 统一头部 -->
    <DashboardHeader
      title="学科教研组"
      subtitle="与同事协作，共享优质教学设计"
      :user-name="userName"
      :region-name="regionName"
      :school-name="schoolName"
      :grade-name="gradeName"
      @logout="handleLogout"
    >
        <template #default>
          <div class="flex items-center gap-3 flex-wrap">
            <button
              @click="handleBackToDashboard"
              class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-xl hover:bg-white hover:shadow-md transition-all"
              title="返回教师工作台"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              返回工作台
            </button>
            <button
              @click="showCreateModal = true"
              class="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-emerald-500 to-teal-500 rounded-xl hover:from-emerald-600 hover:to-teal-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-all shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 transform hover:scale-105"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              创建教研组
            </button>
          </div>
        </template>
      </DashboardHeader>

    <!-- 主内容区 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 统计卡片 -->
      <div v-if="statistics" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-6 mb-8">
        <div class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1">
          <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-cyan-500 to-blue-600"></span>
          <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none bg-gradient-to-br from-cyan-50/80 via-transparent to-transparent"></div>
          <div class="relative">
            <p class="text-xs uppercase tracking-wide text-cyan-600 font-semibold mb-1">全部教研组</p>
            <p class="text-3xl font-bold text-gray-900 mb-2">
              {{ statistics.total_groups }}
            </p>
          </div>
        </div>
        <div class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1">
          <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-emerald-500 to-teal-600"></span>
          <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none bg-gradient-to-br from-emerald-50/80 via-transparent to-transparent"></div>
          <div class="relative">
            <p class="text-xs uppercase tracking-wide text-emerald-600 font-semibold mb-1">我的教研组</p>
            <p class="text-3xl font-bold text-gray-900 mb-2">
              {{ statistics.my_groups }}
            </p>
          </div>
        </div>
        <div class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1">
          <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-violet-500 to-purple-600"></span>
          <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none bg-gradient-to-br from-violet-50/80 via-transparent to-transparent"></div>
          <div class="relative">
            <p class="text-xs uppercase tracking-wide text-violet-600 font-semibold mb-1">总成员数</p>
            <p class="text-3xl font-bold text-gray-900 mb-2">
              {{ statistics.total_members }}
            </p>
          </div>
        </div>
        <div class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1">
          <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-amber-500 to-orange-600"></span>
          <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none bg-gradient-to-br from-amber-50/80 via-transparent to-transparent"></div>
          <div class="relative">
            <p class="text-xs uppercase tracking-wide text-amber-600 font-semibold mb-1">共享教学设计</p>
            <p class="text-3xl font-bold text-gray-900 mb-2">
              {{ statistics.total_shared_lessons }}
            </p>
          </div>
        </div>
        <div class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1">
          <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-green-500 to-emerald-600"></span>
          <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none bg-gradient-to-br from-green-50/80 via-transparent to-transparent"></div>
          <div class="relative">
            <p class="text-xs uppercase tracking-wide text-green-600 font-semibold mb-1">我的分享</p>
            <p class="text-3xl font-bold text-gray-900 mb-2">
              {{ statistics.my_shared_lessons }}
            </p>
          </div>
        </div>
      </div>

      <!-- 筛选器 -->
      <div class="bg-white/80 backdrop-blur-sm border border-gray-200 rounded-2xl shadow-lg p-6 mb-8">
        <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">学科</label>
            <select
              v-model="filters.subject_id"
              @change="loadGroups"
              class="w-full px-3 py-2 border border-gray-300 rounded-xl bg-white/80 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
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
              class="w-full px-3 py-2 border border-gray-300 rounded-xl bg-white/80 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
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
              class="w-full px-3 py-2 border border-gray-300 rounded-xl bg-white/80 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
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
              class="w-full px-3 py-2 border border-gray-300 rounded-xl bg-white/80 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
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
                class="w-4 h-4 text-emerald-600 rounded focus:ring-2 focus:ring-emerald-500"
              />
              <span class="ml-2 text-sm text-gray-700">仅显示我加入的教研组</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 教研组列表 -->
      <div v-if="loading" class="flex items-center justify-center py-16 text-gray-500 bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-lg">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-600 mr-3"></div>
        <span class="text-sm font-medium">加载中...</span>
      </div>

      <div v-else-if="groups.length === 0" class="bg-white/80 backdrop-blur-sm border border-dashed border-gray-200 rounded-2xl shadow-lg p-12 text-center">
        <svg class="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <p class="text-gray-600 text-lg font-medium mb-2">暂无教研组</p>
        <p class="text-gray-400 text-sm mb-6">创建或加入教研组，与同事协作共享优质教学设计</p>
        <button
          @click="showCreateModal = true"
          class="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-emerald-500 to-teal-500 rounded-xl hover:from-emerald-600 hover:to-teal-600 shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 transform hover:scale-105 transition-all"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          创建第一个教研组
        </button>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="group in groups"
          :key="group.id"
          @click="viewGroupDetail(group.id)"
          class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer"
        >
          <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-emerald-500 to-teal-600"></span>
          <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none bg-gradient-to-br from-emerald-50/80 via-transparent to-transparent"></div>
          
          <div
            v-if="group.cover_image_url"
            class="h-40 bg-cover bg-center"
            :style="{ backgroundImage: `url(${group.cover_image_url})` }"
          ></div>
          <div v-else class="h-40 bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500"></div>
          
          <div class="relative p-5">
            <div class="flex items-start justify-between mb-2">
              <h3 class="text-xl font-bold text-gray-900 flex-1">{{ group.name }}</h3>
              <span
                v-if="group.user_role"
                :class="getRoleBadgeClass(group.user_role)"
                class="px-3 py-1 text-xs font-semibold rounded-full ml-2 border"
              >
                {{ getRoleLabel(group.user_role) }}
              </span>
            </div>
            
            <p class="text-gray-600 text-sm mb-4 line-clamp-2">
              {{ group.description || '暂无描述' }}
            </p>
            
            <div class="flex items-center text-sm text-gray-500 space-x-4 mb-4">
              <span class="inline-flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                {{ group.subject_name }}
              </span>
              <span class="inline-flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ getScopeLabel(group.scope) }}
              </span>
            </div>
            
            <div class="flex items-center justify-between text-sm text-gray-500 pt-4 border-t border-gray-200">
              <div class="flex items-center space-x-4">
                <span class="inline-flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  {{ group.member_count }} 成员
                </span>
                <span class="inline-flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  {{ group.lesson_count }} 教案
                </span>
              </div>
              <span v-if="group.is_public" class="inline-flex items-center gap-1 text-emerald-600 font-medium">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
                </svg>
                公开
              </span>
            </div>
          </div>
      </div>
    </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="mt-8 flex justify-center">
        <nav class="flex items-center space-x-2">
          <button
            @click="currentPage > 1 && changePage(currentPage - 1)"
            :disabled="currentPage === 1"
            class="px-4 py-2 text-sm font-medium rounded-xl border border-gray-300 bg-white/80 backdrop-blur-sm text-gray-700 hover:bg-white hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            上一页
          </button>
          <button
            v-for="page in displayPages"
            :key="page"
            @click="changePage(page)"
            :class="[
              'px-4 py-2 text-sm font-medium rounded-xl border transition-all',
              page === currentPage
                ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white border-emerald-500 shadow-lg shadow-emerald-500/30'
                : 'border-gray-300 bg-white/80 backdrop-blur-sm text-gray-700 hover:bg-white hover:shadow-md',
            ]"
          >
            {{ page }}
          </button>
          <button
            @click="currentPage < totalPages && changePage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="px-4 py-2 text-sm font-medium rounded-xl border border-gray-300 bg-white/80 backdrop-blur-sm text-gray-700 hover:bg-white hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一页
          </button>
        </nav>
      </div>
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
import { useUserStore } from '@/store/user'
import { authService } from '@/services/auth'
import {
  getSubjectGroups,
  getSubjectGroupStatistics,
} from '@/services/subjectGroup'
import { curriculumService } from '@/services/curriculum'
import DashboardHeader from '@/components/Common/DashboardHeader.vue'
import type {
  SubjectGroup,
  SubjectGroupStatistics,
  GroupScope,
  MemberRole,
} from '@/types/subjectGroup'
import type { Subject } from '@/types/curriculum'
import CreateGroupModal from '@/components/SubjectGroup/CreateGroupModal.vue'

const router = useRouter()
const userStore = useUserStore()

// 用户信息
const userName = computed(() => userStore.user?.full_name || userStore.user?.username || '教师')
const regionName = computed(() => userStore.user?.region_name || null)
const schoolName = computed(() => userStore.user?.school_name || null)
const gradeName = computed(() => userStore.user?.grade_name || null)

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
    owner: 'bg-red-100 text-red-800 border-red-200',
    admin: 'bg-blue-100 text-blue-800 border-blue-200',
    member: 'bg-gray-100 text-gray-800 border-gray-200',
  }
  return classes[role] || 'bg-gray-100 text-gray-800 border-gray-200'
}

// 返回教师工作台
function handleBackToDashboard() {
  router.push('/teacher')
}

// 退出登录
function handleLogout() {
  userStore.logout()
  router.push('/login')
}

// 生命周期
onMounted(async () => {
  // 确保用户信息已加载
  if (!userStore.user) {
    try {
      const currentUser = await authService.getCurrentUser()
      userStore.setUser(currentUser)
    } catch (error) {
      console.error('Failed to load current user info:', error)
    }
  }

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

