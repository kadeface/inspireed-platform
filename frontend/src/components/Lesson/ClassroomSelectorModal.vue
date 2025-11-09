<template>
  <Transition name="modal">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900 bg-opacity-50 px-4 py-6"
    >
      <div class="w-full max-w-xl rounded-lg bg-white shadow-xl">
        <div class="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <h3 class="text-lg font-semibold text-gray-900">
            选择发布班级
          </h3>
          <button
            type="button"
            class="text-gray-400 hover:text-gray-600"
            @click="handleClose"
          >
            <span class="sr-only">关闭</span>
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="max-h-96 overflow-y-auto px-6 py-4">
          <div v-if="loading" class="flex items-center justify-center py-8 text-gray-500">
            <svg class="h-5 w-5 animate-spin text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span class="ml-2">加载班级中...</span>
          </div>

          <div v-else-if="classrooms.length === 0" class="rounded-md bg-yellow-50 p-4 text-sm text-yellow-700">
            当前没有可选的班级，请联系管理员配置班级信息。
          </div>

          <div v-else class="space-y-3">
            <label
              v-for="classroom in classrooms"
              :key="classroom.id"
              class="flex cursor-pointer items-start gap-3 rounded-lg border border-gray-200 p-3 hover:border-blue-400"
            >
              <input
                type="checkbox"
                class="mt-1 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                :value="classroom.id"
                v-model="localSelection"
              />
              <div>
                <p class="text-sm font-medium text-gray-900">
                  {{ classroom.name }}
                </p>
                <p class="text-xs text-gray-500">
                  年级：{{ formatGradeName(classroom.grade_id) }}
                  <span v-if="classroom.code" class="ml-2">班级编码：{{ classroom.code }}</span>
                </p>
              </div>
            </label>
          </div>

          <p v-if="error" class="mt-4 text-sm text-red-600">
            {{ error }}
          </p>
        </div>

        <div class="flex items-center justify-end gap-3 border-t border-gray-200 bg-gray-50 px-6 py-4">
          <button
            type="button"
            class="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
            @click="handleClose"
          >
            取消
          </button>
          <button
            type="button"
            class="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="loading || classrooms.length === 0"
            @click="handleConfirm"
          >
            确认发布
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { LessonClassroom } from '../../types/lesson'

interface Props {
  modelValue: boolean
  classrooms: LessonClassroom[]
  initialSelectedIds: number[]
  loading?: boolean
  error?: string | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm', selectedIds: number[]): void
  (e: 'cancel'): void
}>()

const localSelection = ref<number[]>([])

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      localSelection.value = [...props.initialSelectedIds]
    }
  },
  { immediate: true }
)

watch(
  () => props.initialSelectedIds,
  (ids) => {
    if (props.modelValue) {
      localSelection.value = [...ids]
    }
  }
)

const loading = computed(() => props.loading ?? false)
const error = computed(() => props.error ?? null)

function handleClose() {
  emit('update:modelValue', false)
  emit('cancel')
}

function handleConfirm() {
  emit('confirm', [...localSelection.value])
}

function formatGradeName(gradeId: number) {
  const gradeNames: Record<number, string> = {
    1: '一年级',
    2: '二年级',
    3: '三年级',
    4: '四年级',
    5: '五年级',
    6: '六年级',
    7: '七年级',
    8: '八年级',
    9: '九年级',
    10: '高一',
    11: '高二',
    12: '高三',
  }
  return gradeNames[gradeId] ?? `年级 ${gradeId}`
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>

