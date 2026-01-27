<template>
  <div class="group-members-list">
    <div v-if="loading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="members.length === 0" class="text-center py-12 text-gray-500">
      <i class="fas fa-user-friends text-4xl mb-2"></i>
      <p>暂无成员</p>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="member in members"
        :key="member.id"
        class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition"
      >
        <div class="flex items-center space-x-4">
          <div
            v-if="member.user_avatar_url"
            class="w-12 h-12 rounded-full bg-cover bg-center"
            :style="{ backgroundImage: `url(${member.user_avatar_url})` }"
          ></div>
          <div v-else class="w-12 h-12 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
            {{ member.user_name?.charAt(0).toUpperCase() || 'U' }}
          </div>

          <div>
            <div class="flex items-center space-x-2">
              <h4 class="font-semibold text-gray-900">{{ member.user_name }}</h4>
              <span
                :class="getRoleBadgeClass(member.role)"
                class="px-2 py-1 text-xs rounded-full"
              >
                {{ getRoleLabel(member.role) }}
              </span>
            </div>
            <p class="text-sm text-gray-500">{{ member.user_email }}</p>
            <p class="text-xs text-gray-400 mt-1">
              加入于 {{ formatDate(member.joined_at) }}
            </p>
          </div>
        </div>

        <div v-if="canManage && member.role !== 'owner'" class="flex space-x-2">
          <button
            @click="showEditMemberModal(member)"
            class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 transition"
          >
            <i class="fas fa-edit mr-1"></i>编辑
          </button>
          <button
            @click="handleRemoveMember(member)"
            class="px-3 py-1 text-sm border border-red-300 text-red-600 rounded hover:bg-red-50 transition"
          >
            <i class="fas fa-trash mr-1"></i>移除
          </button>
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

    <!-- 编辑成员模态框 -->
    <EditMemberModal
      v-if="editingMember"
      :member="editingMember"
      :group-id="groupId"
      @close="editingMember = null"
      @updated="handleMemberUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getGroupMembers, removeGroupMember } from '@/services/subjectGroup'
import type { GroupMembership, MemberRole } from '@/types/subjectGroup'
import EditMemberModal from '@/components/SubjectGroup/EditMemberModal.vue'

const props = defineProps<{
  groupId: number
  userRole?: MemberRole
  canManage: boolean
}>()

const emit = defineEmits<{
  memberRemoved: []
}>()

// 数据
const members = ref<GroupMembership[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const editingMember = ref<GroupMembership | null>(null)

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
async function loadMembers() {
  loading.value = true
  try {
    const response = await getGroupMembers(props.groupId, {
      page: currentPage.value,
      page_size: pageSize.value,
    })
    members.value = response.items
    total.value = response.total
  } catch (error) {
    console.error('加载成员列表失败:', error)
  } finally {
    loading.value = false
  }
}

function changePage(page: number) {
  currentPage.value = page
  loadMembers()
}

function showEditMemberModal(member: GroupMembership) {
  editingMember.value = member
}

function handleMemberUpdated() {
  editingMember.value = null
  loadMembers()
}

async function handleRemoveMember(member: GroupMembership) {
  if (!confirm(`确定要移除成员 ${member.user_name} 吗？`)) {
    return
  }

  try {
    await removeGroupMember(props.groupId, member.user_id)
    loadMembers()
    emit('memberRemoved')
  } catch (error) {
    console.error('移除成员失败:', error)
    alert('移除失败，请重试')
  }
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

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

// 生命周期
onMounted(() => {
  loadMembers()
})
</script>

