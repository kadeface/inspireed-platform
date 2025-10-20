<template>
  <div class="chart-cell cell-container p-4">
    <h3 class="text-lg font-semibold mb-3">{{ cell.title || '数据可视化' }}</h3>
    <div ref="chartRef" class="chart-container" style="height: 300px"></div>
    <p class="text-sm text-gray-500 mt-4">
      {{ cell.content.chartType }} 图表 - ECharts/Chart.js 集成开发中...
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { ChartCell as ChartCellType } from '../../types/cell'

interface Props {
  cell: ChartCellType
  editable?: boolean
}

defineProps<Props>()

const chartRef = ref<HTMLElement>()

onMounted(() => {
  // TODO: 初始化ECharts或Chart.js
  console.log('Chart initialization pending...')
})
</script>

