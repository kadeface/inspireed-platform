<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <div class="p-6">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-gray-900">创建教研组</h2>
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
              教研组名称 <span class="text-red-500">*</span>
            </label>
            <input
              v-model="formData.name"
              type="text"
              required
              placeholder="例如：智能农业教研组"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <!-- 学科选择 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              所属学科 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.subject_id"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option :value="undefined">请选择学科</option>
              <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                {{ subject.name }}
              </option>
            </select>
          </div>

          <!-- 年级选择（可选） -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              所属年级
            </label>
            <select
              v-model="formData.grade_id"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option :value="undefined">不指定年级</option>
              <option v-for="grade in props.grades" :key="grade.id" :value="grade.id">
                {{ grade.name }}
              </option>
            </select>
          </div>

          <!-- 教研组范围 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              教研组范围 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.scope"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="school">校级</option>
              <option value="region">区域级</option>
              <option value="national">全国级</option>
            </select>
          </div>

          <!-- 学校选择（校级） -->
          <div v-if="formData.scope === 'school'">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              所属学校 <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="formData.school_id"
              type="number"
              required
              placeholder="请输入学校ID"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <p class="text-xs text-gray-500 mt-1">提示：请联系管理员获取学校ID</p>
          </div>

          <!-- 区域选择（区域级） -->
          <div v-if="formData.scope === 'region'">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              所属区域 <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="formData.region_id"
              type="number"
              required
              placeholder="请输入区域ID"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <p class="text-xs text-gray-500 mt-1">提示：请联系管理员获取区域ID</p>
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
                <i class="fas fa-spinner fa-spin mr-2"></i>创建中...
              </span>
              <span v-else>
                <i class="fas fa-check mr-2"></i>创建
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
import { createSubjectGroup } from '@/services/subjectGroup'
import type { SubjectGroupCreate } from '@/types/subjectGroup'
import type { Subject } from '@/types/curriculum'

const props = defineProps<{
  subjects: Subject[]
  grades?: Array<{ id: number; name: string }>
}>()

const emit = defineEmits<{
  close: []
  created: []
}>()

const formData = reactive<SubjectGroupCreate>({
  name: '',
  subject_id: undefined as any,
  grade_id: undefined,
  scope: 'school' as any,
  is_public: false,
})

const submitting = ref(false)
const error = ref('')

async function handleSubmit() {
  if (!formData.name || !formData.subject_id) {
    error.value = '请填写必填项'
    return
  }

  if (formData.scope === 'school' && !formData.school_id) {
    error.value = '校级教研组必须选择学校'
    return
  }

  if (formData.scope === 'region' && !formData.region_id) {
    error.value = '区域级教研组必须选择区域'
    return
  }

  submitting.value = true
  error.value = ''

  try {
    await createSubjectGroup(formData)
    emit('created')
  } catch (err: any) {
    error.value = err.response?.data?.detail || '创建失败，请重试'
  } finally {
    submitting.value = false
  }
}
</script>

