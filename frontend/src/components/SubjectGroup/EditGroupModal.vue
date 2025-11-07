<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <div class="p-6">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-gray-900">编辑教研组</h2>
          <button
            @click="$emit('close')"
            class="text-gray-500 hover:text-gray-700 transition"
          >
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- 教研组名称 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              教研组名称
            </label>
            <input
              v-model="formData.name"
              type="text"
              placeholder="例如：智能农业教研组"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <!-- 教研组描述 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              教研组描述
            </label>
            <textarea
              v-model="formData.description"
              rows="4"
              placeholder="介绍一下这个教研组的目标和特色..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            ></textarea>
          </div>

          <!-- 是否公开 -->
          <div>
            <label class="flex items-center cursor-pointer">
              <input
                v-model="formData.is_public"
                type="checkbox"
                class="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-gray-700">公开教研组（其他教师可以申请加入）</span>
            </label>
          </div>

          <!-- 封面图URL -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              封面图URL
            </label>
            <input
              v-model="formData.cover_image_url"
              type="url"
              placeholder="https://example.com/cover.jpg"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
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
                <i class="fas fa-spinner fa-spin mr-2"></i>保存中...
              </span>
              <span v-else>
                <i class="fas fa-save mr-2"></i>保存
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
import { updateSubjectGroup } from '@/services/subjectGroup'
import type { SubjectGroup, SubjectGroupUpdate } from '@/types/subjectGroup'

const props = defineProps<{
  group: SubjectGroup
}>()

const emit = defineEmits<{
  close: []
  updated: []
}>()

const formData = reactive<SubjectGroupUpdate>({
  name: props.group.name,
  description: props.group.description,
  is_public: props.group.is_public,
  cover_image_url: props.group.cover_image_url,
})

const submitting = ref(false)
const error = ref('')

async function handleSubmit() {
  submitting.value = true
  error.value = ''

  try {
    await updateSubjectGroup(props.group.id, formData)
    emit('updated')
  } catch (err: any) {
    error.value = err.response?.data?.detail || '更新失败，请重试'
  } finally {
    submitting.value = false
  }
}
</script>

