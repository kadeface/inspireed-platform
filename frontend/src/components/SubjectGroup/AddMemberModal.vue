<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-lg shadow-xl max-w-lg w-full">
      <div class="p-6">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-gray-900">添加成员</h2>
          <button
            @click="$emit('close')"
            class="text-gray-500 hover:text-gray-700 transition"
          >
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- 用户ID -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              用户ID <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="formData.user_id"
              type="number"
              required
              placeholder="请输入用户ID"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <p class="text-xs text-gray-500 mt-1">提示：可以通过用户管理页面查找用户ID</p>
          </div>

          <!-- 成员角色 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              成员角色 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.role"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="member">普通成员</option>
              <option value="admin">管理员</option>
            </select>
          </div>

          <!-- 错误提示 -->
          <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {{ error }}
          </div>

          <!-- 按钮组 -->
          <div class="flex justify-end space-x-3 pt-4 border-t">
            <button
              type="button"
              @click="$emit('close')"
              class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
            >
              取消
            </button>
            <button
              type="submit"
              :disabled="submitting"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="submitting">
                <i class="fas fa-spinner fa-spin mr-2"></i>添加中...
              </span>
              <span v-else>
                <i class="fas fa-user-plus mr-2"></i>添加
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { addGroupMember } from '@/services/subjectGroup'
import type { GroupMembershipCreate, MemberRole } from '@/types/subjectGroup'

const props = defineProps<{
  groupId: number
}>()

const emit = defineEmits<{
  close: []
  added: []
}>()

const formData = reactive<GroupMembershipCreate>({
  user_id: undefined as any,
  role: 'member' as MemberRole,
})

const submitting = ref(false)
const error = ref('')

async function handleSubmit() {
  if (!formData.user_id) {
    error.value = '请输入用户ID'
    return
  }

  submitting.value = true
  error.value = ''

  try {
    await addGroupMember(props.groupId, formData)
    emit('added')
  } catch (err: any) {
    error.value = err.response?.data?.detail || '添加失败，请重试'
  } finally {
    submitting.value = false
  }
}
</script>

