<template>
  <div class="param-cell cell-container p-4">
    <h3 class="text-lg font-semibold mb-3">{{ cell.title || '参数配置' }}</h3>
    <div class="param-form">
      <div v-for="(value, key) in cell.content.values" :key="key" class="param-item mb-3">
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ key }}</label>
        <input
          v-model="cell.content.values[key]"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          :disabled="!editable"
          @change="handleUpdate"
        />
      </div>
    </div>
    <p class="text-sm text-gray-500 mt-4">JSON Schema驱动的表单功能开发中...</p>
  </div>
</template>

<script setup lang="ts">
import type { ParamCell as ParamCellType } from '../../types/cell'

interface Props {
  cell: ParamCellType
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
})

const emit = defineEmits<{
  update: [cell: ParamCellType]
}>()

function handleUpdate() {
  emit('update', props.cell)
}
</script>

