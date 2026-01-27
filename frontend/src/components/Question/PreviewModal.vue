<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
      <!-- 头部 -->
      <div class="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
        <h2 class="text-xl font-semibold text-gray-800">👁️ 预览回答</h2>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 transition-colors">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 问题内容 -->
      <div class="p-6 border-b bg-gray-50">
        <h3 class="text-lg font-semibold text-gray-900 mb-2">
          ❓ {{ question.title }}
        </h3>
        <p class="text-gray-700 text-sm whitespace-pre-wrap">
          {{ question.content }}
        </p>
      </div>

      <!-- 回答内容 -->
      <div class="p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">
          👨‍🏫 您的回答
        </h3>

        <div v-if="answerCells && answerCells.length > 0" class="space-y-4">
          <!-- 复用CellContainer展示 -->
          <CellContainer
            v-for="(cell, index) in answerCells"
            :key="`preview-cell-${index}`"
            :cell="cell"
            :editable="false"
          />
        </div>

        <div v-else class="text-center py-8 text-gray-500">
          还没有添加任何内容
        </div>
      </div>

      <!-- 底部 -->
      <div class="sticky bottom-0 bg-white border-t px-6 py-4 flex items-center justify-end">
        <button
          @click="$emit('close')"
          class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          关闭预览
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import CellContainer from '@/components/Cell/CellContainer.vue'
import type { QuestionDetail } from '@/types/question'

interface Props {
  question: QuestionDetail
  answerCells: any[]
}

defineProps<Props>()

defineEmits<{
  close: []
}>()
</script>

