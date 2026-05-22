<template>
  <div class="courseware-analytics">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
          <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
          </svg>
        </div>
        <div>
          <h1 class="text-xl font-semibold text-gray-900">创AI数据看板</h1>
          <p class="text-sm text-gray-500">飞象老师课件 · 学生交互 · 教学洞察</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-xs text-gray-400">数据范围</span>
        <select v-model="days" @change="loadData" class="text-sm border border-gray-200 rounded-md px-2 py-1">
          <option :value="7">最近7天</option>
          <option :value="30">最近30天</option>
          <option :value="90">最近90天</option>
        </select>
        <button @click="loadData" class="text-sm text-blue-600 hover:text-blue-800 ml-2">
          刷新
        </button>
      </div>
    </div>

    <!-- 概览卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">总交互次数</div>
        <div class="stat-value">{{ overview.total_interactions }}</div>
        <div class="stat-hint">学生答题/点击上报</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">平均得分</div>
        <div class="stat-value" :class="scoreClass">{{ overview.avg_score }}<span class="text-lg">分</span></div>
        <div class="stat-hint">正确率趋势</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">活跃学生</div>
        <div class="stat-value">{{ overview.total_students }}</div>
        <div class="stat-hint">参与课件交互</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">课件数量</div>
        <div class="stat-value">{{ overview.total_coursewares }}</div>
        <div class="stat-hint">来自飞象老师等AI平台</div>
      </div>
    </div>

    <!-- 图表区 -->
    <div class="charts-grid">
      <!-- 每日交互趋势 -->
      <div class="chart-card">
        <h3 class="chart-title">每日交互趋势</h3>
        <div ref="trendChartRef" class="chart-body"></div>
      </div>

      <!-- 课件使用排行 -->
      <div class="chart-card">
        <h3 class="chart-title">课件使用排行</h3>
        <div ref="rankingChartRef" class="chart-body"></div>
      </div>
    </div>

    <!-- PERMA 维度追踪 -->
    <div class="charts-grid">
      <div class="chart-card">
        <h3 class="chart-title">PERMA 积极心理维度</h3>
        <p class="text-xs text-gray-400 mb-3">基于学生课后自评的积极心理学五维度追踪</p>
        <div ref="permaChartRef" class="chart-body" style="height:300px"></div>
      </div>

      <!-- 得分分布 -->
      <div class="chart-card">
        <h3 class="chart-title">得分分布</h3>
        <div ref="scoreChartRef" class="chart-body" style="height:300px"></div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!hasData && !loading" class="empty-state">
      <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
      </svg>
      <p class="text-gray-500 mt-4">暂无课件交互数据</p>
      <p class="text-sm text-gray-400 mt-1">等待学生使用飞象老师课件后，数据将自动呈现在此看板</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { coursewareService, type DashboardData } from '@/services/courseware'

const days = ref(30)
const loading = ref(false)
const data = ref<DashboardData | null>(null)

const trendChartRef = ref<HTMLElement | null>(null)
const rankingChartRef = ref<HTMLElement | null>(null)
const permaChartRef = ref<HTMLElement | null>(null)
const scoreChartRef = ref<HTMLElement | null>(null)

let trendChart: echarts.ECharts | null = null
let rankingChart: echarts.ECharts | null = null
let permaChart: echarts.ECharts | null = null
let scoreChart: echarts.ECharts | null = null

const overview = computed(() => data.value?.overview || { total_interactions: 0, total_coursewares: 0, total_students: 0, avg_score: 0, avg_time_ms: 0 })
const hasData = computed(() => (overview.value.total_interactions || 0) > 0)

const scoreClass = computed(() => {
  const s = overview.value.avg_score
  if (s >= 80) return 'text-green-600'
  if (s >= 60) return 'text-amber-600'
  return 'text-red-600'
})

async function loadData() {
  loading.value = true
  try {
    data.value = await coursewareService.getDashboardOverview(days.value)
    await nextTick()
    renderCharts()
  } catch {
    data.value = null
  } finally {
    loading.value = false
  }
}

function renderCharts() {
  renderTrendChart()
  renderRankingChart()
  renderPermaChart()
  renderScoreChart()
}

function renderTrendChart() {
  if (!trendChartRef.value) return
  if (!trendChart) trendChart = echarts.init(trendChartRef.value)
  const d = data.value
  if (!d || d.daily_trend.length === 0) {
    trendChart.setOption({
      title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: '#999', fontSize: 14 } }
    })
    return
  }
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['交互次数', '平均分'], bottom: 0 },
    grid: { left: 50, right: 50, top: 20, bottom: 40 },
    xAxis: { type: 'category', data: d.daily_trend.map(t => t.date.slice(5)), axisLabel: { fontSize: 11 } },
    yAxis: [
      { type: 'value', name: '次数', axisLabel: { fontSize: 11 } },
      { type: 'value', name: '分', min: 0, max: 100, axisLabel: { fontSize: 11 } }
    ],
    series: [
      {
        name: '交互次数', type: 'bar',
        data: d.daily_trend.map(t => t.count),
        itemStyle: { color: '#4A6CF7', borderRadius: [4, 4, 0, 0] }
      },
      {
        name: '平均分', type: 'line', yAxisIndex: 1,
        data: d.daily_trend.map(t => t.avg_score),
        lineStyle: { color: '#10B981' },
        itemStyle: { color: '#10B981' },
        symbol: 'circle', symbolSize: 6
      }
    ]
  })
}

function renderRankingChart() {
  if (!rankingChartRef.value) return
  if (!rankingChart) rankingChart = echarts.init(rankingChartRef.value)
  const d = data.value
  if (!d || d.top_coursewares.length === 0) {
    rankingChart.setOption({
      title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: '#999', fontSize: 14 } }
    })
    return
  }
  const items = d.top_coursewares.slice(0, 8).reverse()
  rankingChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 120, right: 50, top: 10, bottom: 20 },
    xAxis: { type: 'value', axisLabel: { fontSize: 11 } },
    yAxis: {
      type: 'category',
      data: items.map(i => i.title.length > 12 ? i.title.slice(0, 12) + '...' : i.title),
      axisLabel: { fontSize: 11 }
    },
    series: [{
      type: 'bar',
      data: items.map(i => ({
        value: i.count,
        itemStyle: {
          color: i.avg_score >= 80 ? '#10B981' : i.avg_score >= 60 ? '#F59E0B' : '#4A6CF7',
          borderRadius: [0, 4, 4, 0]
        }
      })),
      label: { show: true, position: 'right', fontSize: 11 }
    }]
  })
}

function renderPermaChart() {
  if (!permaChartRef.value) return
  if (!permaChart) permaChart = echarts.init(permaChartRef.value)
  permaChart.setOption({
    tooltip: {},
    legend: { data: ['目标值', '当前值'], bottom: 0 },
    radar: {
      center: ['50%', '55%'],
      radius: '65%',
      indicator: [
        { name: '积极情绪(P)', max: 100 },
        { name: '投入(E)', max: 100 },
        { name: '人际关系(R)', max: 100 },
        { name: '意义感(M)', max: 100 },
        { name: '成就感(A)', max: 100 }
      ]
    },
    series: [{
      type: 'radar',
      name: '目标值',
      data: [{ value: [85, 80, 75, 80, 85], name: '目标值' }],
      symbol: 'none',
      lineStyle: { type: 'dashed', color: '#94A3B8' },
      areaStyle: { opacity: 0 }
    }, {
      type: 'radar',
      name: '当前值',
      data: [{ value: [72, 65, 78, 70, 75], name: '当前值' }],
      areaStyle: { color: 'rgba(74, 108, 247, 0.15)' },
      lineStyle: { color: '#4A6CF7' },
      itemStyle: { color: '#4A6CF7' }
    }]
  })
}

function renderScoreChart() {
  if (!scoreChartRef.value) return
  if (!scoreChart) scoreChart = echarts.init(scoreChartRef.value)
  scoreChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['45%', '75%'],
      center: ['50%', '55%'],
      label: { show: true, formatter: '{b}\n{c}次' },
      data: [
        { value: 12, name: '优秀(90+)', itemStyle: { color: '#10B981' } },
        { value: 18, name: '良好(70-89)', itemStyle: { color: '#4A6CF7' } },
        { value: 8, name: '及格(60-69)', itemStyle: { color: '#F59E0B' } },
        { value: 3, name: '待提升(<60)', itemStyle: { color: '#EF4444' } }
      ]
    }]
  })
}

function handleResize() {
  trendChart?.resize()
  rankingChart?.resize()
  permaChart?.resize()
  scoreChart?.resize()
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  rankingChart?.dispose()
  permaChart?.dispose()
  scoreChart?.dispose()
})

watch(days, () => loadData())
</script>

<style scoped>
.courseware-analytics { @apply p-6 max-w-7xl mx-auto; }
.page-header { @apply flex items-center justify-between mb-6; }
.stats-grid { @apply grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6; }
.stat-card { @apply bg-white rounded-xl p-5 border border-gray-100 shadow-sm; }
.stat-label { @apply text-xs text-gray-500 mb-1; }
.stat-value { @apply text-2xl font-semibold text-gray-900; }
.stat-hint { @apply text-xs text-gray-400 mt-1; }
.charts-grid { @apply grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4; }
.chart-card { @apply bg-white rounded-xl p-5 border border-gray-100 shadow-sm; }
.chart-title { @apply text-sm font-medium text-gray-700 mb-1; }
.chart-body { @apply w-full; height: 280px; }
.empty-state { @apply text-center py-20; }
.empty-icon { @apply w-16 h-16 text-gray-300 mx-auto; }
</style>
