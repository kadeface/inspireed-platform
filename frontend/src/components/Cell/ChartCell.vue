<template>
  <div class="chart-cell cell-container" :class="{ 'fullscreen': isFullscreen }" ref="containerRef">
    <div v-if="!editable" class="cell-toolbar mb-2">
      <button
        class="cell-fullscreen-btn"
        :class="{ 'active': isFullscreen }"
        @click="toggleFullscreen"
        :title="isFullscreen ? '退出全屏' : '全屏查看'"
      >
        <svg v-if="!isFullscreen" class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
        </svg>
        <svg v-else class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
        <span class="text-sm font-medium ml-1">{{ isFullscreen ? '退出全屏' : '全屏' }}</span>
      </button>
    </div>

    <h3 v-if="cell.title" class="text-sm font-medium text-gray-700 mb-3">{{ cell.title }}</h3>
    <div ref="chartRef" class="chart-container" :style="{ height: chartHeight + 'px' }"></div>

    <!-- 编辑器（教师模式） -->
    <div v-if="editable" class="chart-editor mt-4 space-y-3">
      <div>
        <label class="text-xs text-gray-500">图表类型</label>
        <select v-model="localType" @change="update" class="w-full mt-1 px-3 py-2 border border-gray-200 rounded-md text-sm">
          <option value="bar">柱状图</option>
          <option value="line">折线图</option>
          <option value="pie">饼图</option>
          <option value="scatter">散点图</option>
        </select>
      </div>
      <div>
        <label class="text-xs text-gray-500">JSON 数据配置</label>
        <textarea
          v-model="localDataStr"
          @blur="update"
          rows="6"
          class="w-full mt-1 px-3 py-2 border border-gray-200 rounded-md text-xs font-mono"
          placeholder='{"categories": ["A","B","C"], "values": [10,20,15], "name": "数据"}'
        />
      </div>
      <p class="text-xs text-gray-400">ECharts 驱动 · 支持 bar / line / pie / scatter</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { ChartCell as ChartCellType } from '../../types/cell'
import { useFullscreen } from '@/composables/useFullscreen'

interface Props {
  cell: ChartCellType
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), { editable: false })
const emit = defineEmits<{ update: [cell: ChartCellType] }>()

const containerRef = ref<HTMLElement | null>(null)
const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null
const { isFullscreen, toggleFullscreen } = useFullscreen(containerRef)

const localType = ref(props.cell.content?.chartType || 'bar')
const localDataStr = ref(JSON.stringify(props.cell.content?.data || {}, null, 2))
const chartHeight = ref(props.cell.content?.options?.height || 300)

function buildOptions(): any {
  const raw = (() => { try { return JSON.parse(localDataStr.value) } catch { return {} } })()
  const categories = raw.categories || raw.labels || []
  const values = raw.values || raw.data || []
  const name = raw.name || '数据'

  switch (localType.value) {
    case 'pie':
      return {
        tooltip: { trigger: 'item' },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          data: categories.map((c: string, i: number) => ({
            name: c, value: values[i] || 0
          })),
          label: { formatter: '{b}: {c}' }
        }]
      }
    case 'line':
      return {
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: categories },
        yAxis: { type: 'value' },
        series: [{ data: values, type: 'line', smooth: true, name }]
      }
    case 'scatter':
      return {
        tooltip: { trigger: 'item' },
        xAxis: { type: 'value' },
        yAxis: { type: 'value' },
        series: [{ data: raw.points || [], type: 'scatter', name }]
      }
    default:
      return {
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: categories },
        yAxis: { type: 'value' },
        series: [{ data: values, type: 'bar', name, itemStyle: { borderRadius: [4, 4, 0, 0] } }]
      }
  }
}

function renderChart() {
  if (!chartRef.value) return
  if (!chartInstance) chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption(buildOptions(), true)
}

function update() {
  try {
    const data = JSON.parse(localDataStr.value)
    emit('update', {
      ...props.cell,
      content: {
        chartType: localType.value as any,
        data,
        options: { height: chartHeight.value }
      }
    })
  } catch {
    // JSON 不合法时不更新
  }
  renderChart()
}

onMounted(() => {
  nextTick(() => renderChart())
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})

function handleResize() {
  chartInstance?.resize()
}

watch(() => props.cell.content?.chartType, (v) => {
  if (v) localType.value = v
  nextTick(() => renderChart())
})

watch(() => props.cell.content?.data, (v) => {
  if (v) localDataStr.value = JSON.stringify(v, null, 2)
  nextTick(() => renderChart())
})
</script>

<style scoped>
.cell-toolbar { @apply flex justify-end; }
.cell-fullscreen-btn { @apply flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 rounded-md transition-colors; }
.cell-fullscreen-btn.active { @apply bg-red-50 hover:bg-red-100 text-red-700; }
.cell-fullscreen-btn .icon { @apply w-4 h-4; }
.chart-container { @apply w-full; }
.chart-editor { @apply border-t border-gray-100 pt-3; }
.chart-cell.fullscreen { @apply fixed inset-0 z-50 bg-white overflow-auto p-8; }
.chart-cell.fullscreen .chart-container { @apply h-[calc(100vh-12rem)]; }
</style>
