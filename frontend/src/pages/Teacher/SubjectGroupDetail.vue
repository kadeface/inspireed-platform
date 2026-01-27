<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50/30 to-teal-50/50">
    <div class="subject-group-detail-page max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
        <p class="text-gray-600 mt-4">加载中...</p>
      </div>

      <div v-else-if="group">
        <!-- 返回按钮 -->
        <button
          @click="$router.back()"
          class="mb-6 text-amber-600 hover:text-amber-700 transition flex items-center group"
        >
          <i class="fas fa-arrow-left mr-2 transform group-hover:-translate-x-1 transition-transform"></i>返回
        </button>

        <!-- 教研组头部 -->
        <div class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm shadow-lg hover:shadow-2xl transition-all duration-300 mb-6">
          <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-amber-500 to-orange-600"></span>
          <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none bg-gradient-to-br from-amber-50/80 via-transparent to-transparent"></div>
          
          <div
            v-if="group.cover_image_url"
            class="h-48 bg-cover bg-center relative"
            :style="{ backgroundImage: `url(${group.cover_image_url})` }"
          ></div>
          <div v-else class="h-48 bg-gradient-to-br from-amber-500 to-orange-600 relative"></div>
        
          <div class="p-6 relative">
          <div class="flex justify-between items-start mb-4">
            <div class="flex-1">
              <div class="flex items-center space-x-3 mb-2">
                <h1 class="text-3xl font-bold text-gray-900">{{ group.name }}</h1>
                <span
                  v-if="group.user_role"
                  :class="getRoleBadgeClass(group.user_role)"
                  class="px-3 py-1 text-sm rounded-full"
                >
                  {{ getRoleLabel(group.user_role) }}
                </span>
                <span v-if="group.is_public" class="px-3 py-1 text-sm bg-green-100 text-green-800 rounded-full">
                  <i class="fas fa-lock-open mr-1"></i>公开
                </span>
              </div>
              <p class="text-gray-600">{{ group.description || '暂无描述' }}</p>
            </div>
            <div v-if="canManage" class="flex space-x-2">
              <button
                @click="showEditModal = true"
                class="px-4 py-2 border border-gray-200 rounded-xl hover:bg-gray-50 transition-all shadow-sm hover:shadow-md"
              >
                <i class="fas fa-edit mr-2"></i>编辑
              </button>
              <button
                v-if="isOwner"
                @click="handleDelete"
                class="px-4 py-2 border border-red-200 text-red-600 rounded-xl hover:bg-red-50 transition-all shadow-sm hover:shadow-md"
              >
                <i class="fas fa-trash mr-2"></i>删除
              </button>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
            <div class="flex items-center text-gray-700">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 shadow-md mr-3">
                <i class="fas fa-book text-white"></i>
              </div>
              <span class="font-medium">{{ group.subject_name }}</span>
            </div>
            <div class="flex items-center text-gray-700">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 shadow-md mr-3">
                <i class="fas fa-globe text-white"></i>
              </div>
              <span class="font-medium">{{ getScopeLabel(group.scope) }}</span>
            </div>
            <div class="flex items-center text-gray-700">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 shadow-md mr-3">
                <i class="fas fa-users text-white"></i>
              </div>
              <span class="font-medium">{{ group.member_count }} 成员</span>
            </div>
            <div class="flex items-center text-gray-700">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 shadow-md mr-3">
                <i class="fas fa-file-alt text-white"></i>
              </div>
              <span class="font-medium">{{ group.lesson_count }} 共享教案</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 标签页 -->
      <div class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm shadow-lg hover:shadow-2xl transition-all duration-300 mb-6">
        <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-amber-500 to-orange-600"></span>
        <div class="border-b border-gray-200">
          <nav class="flex space-x-8 px-6">
            <button
              @click="activeTab = 'lessons'"
              :class="[
                'py-4 border-b-2 font-medium transition-all',
                activeTab === 'lessons'
                  ? 'border-amber-600 text-amber-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700',
              ]"
            >
              <i class="fas fa-file-alt mr-2"></i>共享教学设计
            </button>
            <button
              @click="activeTab = 'members'"
              :class="[
                'py-4 border-b-2 font-medium transition-all',
                activeTab === 'members'
                  ? 'border-amber-600 text-amber-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700',
              ]"
            >
              <i class="fas fa-users mr-2"></i>成员管理
            </button>
          </nav>
        </div>

        <div class="p-6">
          <!-- 共享教学设计标签页 -->
          <div v-if="activeTab === 'lessons'">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold text-gray-900">共享教学设计</h3>
              <button
                v-if="group.user_role"
                @click="showShareLessonModal = true"
                class="px-4 py-2 bg-gradient-to-br from-amber-500 to-orange-600 text-white rounded-xl hover:shadow-lg transition-all shadow-md"
              >
                <i class="fas fa-share mr-2"></i>分享教案
              </button>
            </div>

            <SharedLessonsList
              :group-id="group.id"
              :user-role="group.user_role"
            />
          </div>

          <!-- 成员管理标签页 -->
          <div v-if="activeTab === 'members'">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold text-gray-900">成员管理</h3>
              <button
                v-if="canManage"
                @click="showAddMemberModal = true"
                class="px-4 py-2 bg-gradient-to-br from-amber-500 to-orange-600 text-white rounded-xl hover:shadow-lg transition-all shadow-md"
              >
                <i class="fas fa-user-plus mr-2"></i>添加成员
              </button>
            </div>

            <GroupMembersList
              :group-id="group.id"
              :user-role="group.user_role"
              :can-manage="canManage"
              @member-removed="loadGroup"
            />
          </div>
        </div>
      </div>
    </div>
  </div>

    <!-- 编辑模态框 -->
    <EditGroupModal
      v-if="showEditModal && group"
      :group="group"
      @close="showEditModal = false"
      @updated="handleGroupUpdated"
    />

    <!-- 分享教案模态框 -->
    <ShareLessonModal
      v-if="showShareLessonModal && group"
      :group-id="group.id"
      @close="showShareLessonModal = false"
      @shared="handleLessonShared"
    />

    <!-- 添加成员模态框 -->
    <AddMemberModal
      v-if="showAddMemberModal && group"
      :group-id="group.id"
      @close="showAddMemberModal = false"
      @added="handleMemberAdded"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSubjectGroup, deleteSubjectGroup } from '@/services/subjectGroup'
import type { SubjectGroup, GroupScope, MemberRole } from '@/types/subjectGroup'
import SharedLessonsList from '@/components/SubjectGroup/SharedLessonsList.vue'
import GroupMembersList from '@/components/SubjectGroup/GroupMembersList.vue'
import EditGroupModal from '@/components/SubjectGroup/EditGroupModal.vue'
import ShareLessonModal from '@/components/SubjectGroup/ShareLessonModal.vue'
import AddMemberModal from '@/components/SubjectGroup/AddMemberModal.vue'

const route = useRoute()
const router = useRouter()

// 数据
const group = ref<SubjectGroup | null>(null)
const loading = ref(false)
const activeTab = ref<'lessons' | 'members'>('lessons')
const showEditModal = ref(false)
const showShareLessonModal = ref(false)
const showAddMemberModal = ref(false)

// 计算属性
const groupId = computed(() => Number(route.params.id))
const isOwner = computed(() => group.value?.user_role === 'owner')
const canManage = computed(() => {
  const role = group.value?.user_role
  return role === 'owner' || role === 'admin'
})

// 方法
async function loadGroup() {
  loading.value = true
  try {
    group.value = await getSubjectGroup(groupId.value)
  } catch (error: any) {
    console.error('加载教研组失败:', error)
    if (error.response?.status === 404) {
      alert('教研组不存在')
      router.push('/teacher/subject-groups')
    } else if (error.response?.status === 403) {
      alert('无权访问此教研组')
      router.push('/teacher/subject-groups')
    }
  } finally {
    loading.value = false
  }
}

async function handleDelete() {
  if (!confirm('确定要删除此教研组吗？此操作不可恢复。')) {
    return
  }

  try {
    await deleteSubjectGroup(groupId.value)
    alert('教研组已删除')
    router.push('/teacher/subject-groups')
  } catch (error) {
    console.error('删除教研组失败:', error)
    alert('删除失败，请重试')
  }
}

function handleGroupUpdated() {
  showEditModal.value = false
  loadGroup()
}

function handleLessonShared() {
  showShareLessonModal.value = false
  loadGroup()
}

function handleMemberAdded() {
  showAddMemberModal.value = false
  loadGroup()
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
  loadGroup()
})
</script>

