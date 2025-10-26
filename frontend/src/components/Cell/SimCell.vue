<template>
  <div class="sim-cell cell-container">
    <!-- Edit Mode - PhET Sim Selector -->
    <div v-if="editable && !cell.content.phetSim && !cell.content.url && !showCustomUrlMode" class="phet-selector p-4">
      <div class="selector-header mb-4 flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold">{{ cell.title || '仿真演示' }}</h3>
          <p class="text-sm text-gray-600 mt-1">选择一个PhET仿真实验</p>
        </div>
        <div class="flex gap-2">
          <button
            @click="openPhETWebsite"
            class="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            浏览更多仿真 →
          </button>
          <button
            @click="showCustomUrlMode = true"
            class="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            自定义URL
          </button>
        </div>
      </div>

      <!-- Category Filter -->
      <div class="category-filter mb-4">
        <div class="flex flex-wrap gap-2">
          <button
            v-for="category in categories"
            :key="category.id"
            @click="selectedCategory = category.id"
            :class="[
              'px-3 py-1 rounded-full text-sm font-medium transition-colors',
              selectedCategory === category.id
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            ]"
          >
            {{ category.name }}
          </button>
        </div>
      </div>

      <!-- Simulation Grid -->
      <div class="simulation-grid">
        <div
          v-for="sim in filteredSimulations"
          :key="sim.id"
          @click="selectSimulation(sim)"
          class="sim-card group cursor-pointer"
        >
          <div class="card-content">
            <div class="flex items-center gap-2 mb-1">
              <h4 class="font-semibold text-base">{{ sim.nameCn }}</h4>
              <span class="text-xs text-gray-500">({{ sim.name }})</span>
            </div>
            <p class="text-sm text-gray-600 line-clamp-2">{{ sim.descriptionCn }}</p>
            <div class="tags mt-2">
              <span
                v-for="topic in sim.topics.slice(0, 3)"
                :key="topic"
                class="tag"
              >
                {{ topic }}
              </span>
            </div>
          </div>
          <div class="card-overlay group-hover:opacity-100">
            <span class="text-white font-medium">点击选择</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Custom URL Mode -->
    <div v-else-if="editable && !cell.content.phetSim && !cell.content.url && showCustomUrlMode" class="p-4">
      <div class="custom-url-editor">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-lg font-semibold">自定义仿真URL</h3>
            <p class="text-sm text-gray-600 mt-1">输入PhET或其他仿真网址</p>
          </div>
          <button
            @click="showCustomUrlMode = false"
            class="text-gray-500 hover:text-gray-700"
          >
            ← 返回
          </button>
        </div>

        <div class="form-section mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            PhET仿真URL
          </label>
          <input
            v-model="customUrl"
            type="url"
            placeholder="https://phet.colorado.edu/sims/html/..."
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p class="text-xs text-gray-500 mt-1">
            提示：在 <a href="https://phet.colorado.edu" target="_blank" class="text-blue-600 hover:underline">phet.colorado.edu</a> 找到仿真后，复制其URL
          </p>
        </div>

        <div class="quick-links mb-4 p-3 bg-blue-50 rounded-lg">
          <p class="text-sm font-medium text-blue-900 mb-2">快速链接：</p>
          <div class="grid grid-cols-2 gap-2">
            <a
              href="https://phet.colorado.edu/sims/html/ph-scale/latest/ph-scale_zh_CN.html"
              target="_blank"
              class="text-xs text-blue-600 hover:underline"
            >
              • pH值
            </a>
            <a
              href="https://phet.colorado.edu/sims/html/build-an-atom/latest/build-an-atom_zh_CN.html"
              target="_blank"
              class="text-xs text-blue-600 hover:underline"
            >
              • 构建原子
            </a>
            <a
              href="https://phet.colorado.edu/sims/html/gene-expression-basics/latest/gene-expression-basics_zh_CN.html"
              target="_blank"
              class="text-xs text-blue-600 hover:underline"
            >
              • 基因表达
            </a>
            <a
              href="https://phet.colorado.edu/sims/html/graphing-lines/latest/graphing-lines_zh_CN.html"
              target="_blank"
              class="text-xs text-blue-600 hover:underline"
            >
              • 直线图形
            </a>
          </div>
        </div>

        <div class="flex justify-end gap-2">
          <button
            @click="showCustomUrlMode = false"
            class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            取消
          </button>
          <button
            @click="useCustomUrl"
            :disabled="!customUrl"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            确认使用
          </button>
        </div>
      </div>
    </div>

    <!-- Editor Mode - Selected PhET Sim -->
    <div v-else-if="editable && (cell.content.phetSim || cell.content.url)" class="p-4">
      <div class="editor-header mb-4 flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold">{{ cell.title || selectedSimInfo?.nameCn || '仿真演示' }}</h3>
          <p class="text-sm text-gray-600">
            {{ cell.content.phetSim ? selectedSimInfo?.descriptionCn : '自定义仿真URL' }}
          </p>
        </div>
        <button
          @click="changeSimulation"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          更换仿真
        </button>
      </div>

      <!-- Config Panel -->
      <div class="config-panel mb-4 p-4 bg-gray-50 rounded-lg">
        <h4 class="font-medium mb-3">配置选项</h4>
        <div class="config-grid">
          <div class="config-item">
            <label>宽度:</label>
            <input
              v-model.number="localConfig.width"
              type="number"
              min="400"
              max="1400"
              @blur="updateCell"
            />
          </div>
          <div class="config-item">
            <label>高度:</label>
            <input
              v-model.number="localConfig.height"
              type="number"
              min="300"
              max="900"
              @blur="updateCell"
            />
          </div>
          <div class="config-item">
            <label>
              <input
                v-model="localConfig.autoplay"
                type="checkbox"
                @change="updateCell"
              />
              自动播放
            </label>
          </div>
        </div>
      </div>

      <!-- Simulation Preview -->
      <div class="sim-preview">
        <iframe
          :src="editorSimulationUrl"
          :width="localConfig.width || 800"
          :height="localConfig.height || 600"
          frameborder="0"
          allowfullscreen
          class="rounded-lg shadow-lg"
        ></iframe>
      </div>
    </div>

    <!-- View Mode - Display Simulation -->
    <div v-else class="p-4">
      <div v-if="cell.title" class="sim-header mb-3">
        <h3 class="text-lg font-semibold">{{ cell.title }}</h3>
        <p v-if="selectedSimInfo?.descriptionCn" class="text-sm text-gray-600 mt-1">
          {{ selectedSimInfo.descriptionCn }}
        </p>
      </div>

      <!-- PhET Simulation -->
      <div v-if="cell.content.type === 'phet' && simulationUrl" class="sim-display">
        <iframe
          :src="simulationUrl"
          :width="cell.content.config.width || 800"
          :height="cell.content.config.height || 600"
          frameborder="0"
          allowfullscreen
          class="rounded-lg shadow-lg w-full"
        ></iframe>
      </div>

      <!-- Generic Iframe -->
      <div v-else-if="cell.content.url" class="sim-display">
        <iframe
          :src="cell.content.url"
          :width="cell.content.config.width || 800"
          :height="cell.content.config.height || 600"
          frameborder="0"
          allowfullscreen
          class="rounded-lg shadow-lg w-full"
        ></iframe>
      </div>

      <!-- Placeholder -->
      <div v-else class="sim-placeholder bg-gray-100 rounded-lg" style="height: 400px">
        <div class="flex items-center justify-center h-full text-gray-500">
          <p>未配置仿真内容</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { SimCell as SimCellType, SimCellContent } from '../../types/cell'
import {
  PHET_SIMULATIONS,
  PHET_CATEGORIES,
  getPHETSimulation,
  getPHETSimulationsByCategory,
  type PhETSimulation
} from '../../data/phet-simulations'

interface Props {
  cell: SimCellType
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false
})

const emit = defineEmits<{
  update: [cell: SimCellType]
}>()

// Category filter
const selectedCategory = ref<string>('all')
const showCustomUrlMode = ref(false)
const customUrl = ref('')

const categories = computed(() => {
  return [
    { id: 'all', name: '全部' },
    ...PHET_CATEGORIES
  ]
})

const filteredSimulations = computed(() => {
  return getPHETSimulationsByCategory(
    selectedCategory.value === 'all' ? undefined : selectedCategory.value
  )
})

const selectedSimInfo = computed(() => {
  if (props.cell.content.phetSim) {
    return getPHETSimulation(props.cell.content.phetSim)
  }
  return null
})

const localConfig = ref({ ...props.cell.content.config })

// Watch for config changes
watch(localConfig, () => {
  updateCell()
}, { deep: true })

// Construct PhET simulation URL for view mode
const simulationUrl = computed(() => {
  if (props.cell.content.type === 'phet' && props.cell.content.phetSim) {
    const sim = getPHETSimulation(props.cell.content.phetSim)
    if (sim) {
      // Construct URL with locale and any additional params
      let url = sim.url
      const params = new URLSearchParams()
      
      if (props.cell.content.config.locale) {
        params.append('locale', props.cell.content.config.locale)
      }
      
      if (props.cell.content.config.autoplay) {
        params.append('autoplay', 'true')
      }

      if (params.toString()) {
        url += '?' + params.toString()
      }
      
      return url
    }
  }
  
  return props.cell.content.url
})

// Editor mode simulation URL (handles both PhET and custom URLs)
const editorSimulationUrl = computed(() => {
  // If it's a custom URL (iframe type or has url but no phetSim)
  if (props.cell.content.url && !props.cell.content.phetSim) {
    return props.cell.content.url
  }
  
  // Otherwise use the PhET simulation URL
  return simulationUrl.value
})

function selectSimulation(sim: PhETSimulation) {
  const updatedCell: SimCellType = {
    ...props.cell,
    content: {
      type: 'phet',
      phetSim: sim.id,
      phetCategory: sim.category,
      config: {
        width: 800,
        height: 600,
        autoplay: false,
        locale: 'zh_CN'
      }
    }
  }
  
  emit('update', updatedCell)
}

function changeSimulation() {
  // Reset to selection mode by clearing the simulation data
  const updatedCell: SimCellType = {
    ...props.cell,
    content: {
      type: 'phet',
      config: {
        width: 800,
        height: 600,
        autoplay: false,
        locale: 'zh_CN'
      }
    }
  }
  // Reset custom URL state
  customUrl.value = ''
  showCustomUrlMode.value = false
  emit('update', updatedCell)
}

function updateCell() {
  const updatedCell: SimCellType = {
    ...props.cell,
    content: {
      ...props.cell.content,
      config: { ...localConfig.value }
    }
  }
  emit('update', updatedCell)
}

function openPhETWebsite() {
  window.open('https://phet.colorado.edu', '_blank')
}

function useCustomUrl() {
  if (!customUrl.value) return
  
  // 创建一个全新的 content 对象，确保旧字段被清除
  const newContent: SimCellContent = {
    type: 'iframe',
    url: customUrl.value,
    config: {
      width: 800,
      height: 600,
      autoplay: false
    }
  }
  
  const updatedCell: SimCellType = {
    ...props.cell,
    content: newContent
  }
  
  emit('update', updatedCell)
  showCustomUrlMode.value = false
  customUrl.value = '' // 清空输入框
}
</script>

<style scoped>
.sim-cell {
  @apply w-full;
}

.phet-selector {
  @apply w-full;
}

.selector-header {
  @apply border-b border-gray-200 pb-4;
}

.category-filter {
  @apply pb-3 border-b border-gray-200;
}

.simulation-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4 max-h-96 overflow-y-auto;
}

.sim-card {
  @apply relative bg-white border border-gray-300 rounded-lg p-4 transition-all hover:shadow-lg hover:border-blue-500;
}

.sim-card h4 {
  @apply text-gray-900;
}

.card-overlay {
  @apply absolute inset-0 bg-blue-600 bg-opacity-90 rounded-lg flex items-center justify-center opacity-0 transition-opacity;
}

.tags {
  @apply flex flex-wrap gap-1;
}

.tag {
  @apply px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded;
}

.editor-header {
  @apply border-b border-gray-200 pb-3;
}

.config-panel {
  @apply border border-gray-200;
}

.config-grid {
  @apply grid grid-cols-3 gap-4;
}

.config-item {
  @apply flex flex-col;
}

.config-item label {
  @apply text-sm font-medium text-gray-700 mb-1;
}

.config-item input[type="number"] {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.config-item label > input[type="checkbox"] {
  @apply mr-2;
}

.sim-preview {
  @apply flex justify-center;
}

.sim-display {
  @apply flex justify-center;
}

.sim-placeholder {
  @apply border-2 border-dashed border-gray-300;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.custom-url-editor {
  @apply w-full;
}

.form-section label {
  @apply block text-sm font-medium text-gray-700 mb-2;
}

.quick-links {
  @apply border border-blue-200;
}
</style>

