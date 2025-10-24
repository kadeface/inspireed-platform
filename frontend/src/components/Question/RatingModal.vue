<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md m-4 p-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">对回答进行评分</h3>

      <div class="flex items-center justify-center space-x-2 my-8">
        <button
          v-for="i in 5"
          :key="i"
          @click="selectedRating = i"
          class="text-4xl transition-all hover:scale-110"
        >
          {{ i <= selectedRating ? '⭐' : '☆' }}
        </button>
      </div>

      <p class="text-center text-gray-600 mb-6">
        {{ ratingText }}
      </p>

      <div class="flex items-center justify-end space-x-3">
        <button
          @click="$emit('close')"
          class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
        >
          取消
        </button>
        <button
          @click="handleSubmit"
          :disabled="selectedRating === 0"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          提交评分
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  show: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  close: []
  submit: [rating: number]
}>()

const selectedRating = ref(0)

const ratingText = computed(() => {
  if (selectedRating.value === 0) return '请选择评分'
  if (selectedRating.value === 1) return '非常不满意'
  if (selectedRating.value === 2) return '不满意'
  if (selectedRating.value === 3) return '一般'
  if (selectedRating.value === 4) return '满意'
  if (selectedRating.value === 5) return '非常满意'
  return ''
})

const handleSubmit = () => {
  if (selectedRating.value > 0) {
    emit('submit', selectedRating.value)
    selectedRating.value = 0
  }
}
</script>

