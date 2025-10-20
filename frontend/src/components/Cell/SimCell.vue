<template>
  <div class="sim-cell cell-container p-4">
    <h3 class="text-lg font-semibold mb-3">{{ cell.title || '仿真演示' }}</h3>
    <div class="sim-container bg-gray-100 rounded-lg" style="height: 400px">
      <div class="flex items-center justify-center h-full text-gray-500">
        <p>{{ cell.content.type }} 仿真引擎开发中...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SimCell as SimCellType } from '../../types/cell'

interface Props {
  cell: SimCellType
  editable?: boolean
}

defineProps<Props>()
</script>

