<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <div class="p-6">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-gray-900">分享教学设计</h2>
          <button
            @click="$emit('close')"
            class="text-gray-500 hover:text-gray-700 transition"
          >
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- 选择教案 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              选择教学设计 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.lesson_id"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option :value="undefined">请选择教学设计</option>
              <option v-for="lesson in myLessons" :key="lesson.id" :value="lesson.id">
                {{ lesson.title }}
              </option>
            </select>
            <p class="text-xs text-gray-500 mt-1">只能分享自己创建的教学设计</p>
          </div>

          <!-- 分享说明 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              分享说明
            </label>
            <textarea
              v-model="formData.share_note"
              rows="4"
              placeholder="介绍一下这个教学设计的特点和使用场景..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            ></textarea>
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
                <i class="fas fa-spinner fa-spin mr-2"></i>分享中...
              </span>
              <span v-else>
                <i class="fas fa-share mr-2"></i>分享
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { shareLessonToGroup } from '@/services/subjectGroup'
import { lessonService } from '@/services/lesson'
import type { SharedLessonCreate } from '@/types/subjectGroup'
import type { Lesson } from '@/types/lesson'

const props = defineProps<{
  groupId: number
}>()

const emit = defineEmits<{
  close: []
  shared: []
}>()

const myLessons = ref<Lesson[]>([])
const formData = reactive<SharedLessonCreate>({
  lesson_id: undefined as any,
})

const submitting = ref(false)
const error = ref('')

async function loadMyLessons() {
  try {
    const response = await lessonService.fetchLessons({ page: 1, page_size: 100 })
    myLessons.value = response.items || []
  } catch (err) {
    console.error('加载我的教学设计失败:', err)
  }
}

async function handleSubmit() {
  if (!formData.lesson_id) {
    error.value = '请选择教学设计'
    return
  }

  submitting.value = true
  error.value = ''

  try {
    await shareLessonToGroup(props.groupId, formData)
    emit('shared')
  } catch (err: any) {
    error.value = err.response?.data?.detail || '分享失败，请重试'
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadMyLessons()
})
</script>

