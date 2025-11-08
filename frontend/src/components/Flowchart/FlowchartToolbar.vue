<template>
  <div class="flowchart-toolbar">
    <div class="toolbar-section">
      <span class="toolbar-label">添加节点：</span>
      <button
        v-for="nodeType in nodeTypes"
        :key="nodeType.type"
        :title="nodeType.label"
        class="toolbar-button"
        @click="$emit('add-node', nodeType.type)"
      >
        <span class="text-xl">{{ nodeType.icon }}</span>
        <span class="text-xs">{{ nodeType.label }}</span>
      </button>
    </div>

    <div class="toolbar-divider" />

    <div class="toolbar-section">
      <button
        class="toolbar-button"
        title="自动布局"
        @click="$emit('auto-layout')"
      >
        <span class="text-lg">🎯</span>
        <span class="text-xs">自动布局</span>
      </button>

      <div class="relative">
        <button
          class="toolbar-button"
          title="布局方向"
          @click="showLayoutMenu = !showLayoutMenu"
        >
          <span class="text-lg">📐</span>
          <span class="text-xs">布局</span>
        </button>
        
        <!-- 布局方向下拉菜单 -->
        <div
          v-if="showLayoutMenu"
          class="layout-menu"
          @click="showLayoutMenu = false"
        >
          <button
            v-for="layout in layouts"
            :key="layout.value"
            :class="{ 'active': layout.value === layoutDirection }"
            class="layout-item"
            @click="$emit('change-layout', layout.value)"
          >
            <span>{{ layout.icon }}</span>
            <span>{{ layout.label }}</span>
          </button>
        </div>
      </div>

      <button
        class="toolbar-button"
        :title="theme === 'dark' ? '切换到亮色' : '切换到暗色'"
        @click="$emit('toggle-theme')"
      >
        <span class="text-lg">{{ theme === 'dark' ? '☀️' : '🌙' }}</span>
        <span class="text-xs">{{ theme === 'dark' ? '亮色' : '暗色' }}</span>
      </button>
    </div>

    <div class="toolbar-divider" />

    <div class="toolbar-section">
      <button
        class="toolbar-button"
        title="导出为图片"
        @click="$emit('export-image')"
      >
        <span class="text-lg">📷</span>
        <span class="text-xs">导出</span>
      </button>

      <button
        class="toolbar-button text-red-600 hover:bg-red-50"
        title="清空画布"
        @click="$emit('clear')"
      >
        <span class="text-lg">🗑️</span>
        <span class="text-xs">清空</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  theme?: 'light' | 'dark'
  layoutDirection?: 'TB' | 'LR' | 'BT' | 'RL'
}

const props = withDefaults(defineProps<Props>(), {
  theme: 'light',
  layoutDirection: 'TB',
})

defineEmits<{
  'add-node': [type: 'start' | 'process' | 'decision' | 'loop' | 'end']
  'auto-layout': []
  'toggle-theme': []
  'change-layout': [direction: 'TB' | 'LR' | 'BT' | 'RL']
  'export-image': []
  'clear': []
}>()

const showLayoutMenu = ref(false)

const nodeTypes = [
  { type: 'start', label: '开始', icon: '🟢' },
  { type: 'process', label: '过程', icon: '📦' },
  { type: 'decision', label: '判断', icon: '💎' },
  { type: 'loop', label: '循环', icon: '🔁' },
  { type: 'end', label: '结束', icon: '🔴' },
]

const layouts = [
  { value: 'TB', label: '从上到下', icon: '⬇️' },
  { value: 'LR', label: '从左到右', icon: '➡️' },
  { value: 'BT', label: '从下到上', icon: '⬆️' },
  { value: 'RL', label: '从右到左', icon: '⬅️' },
]
</script>

<style scoped>
.flowchart-toolbar {
  @apply flex items-center gap-2 px-4 py-3 bg-white border-b border-gray-200;
}

.toolbar-section {
  @apply flex items-center gap-1.5;
}

.toolbar-label {
  @apply text-sm font-medium text-gray-700 mr-1;
}

.toolbar-button {
  @apply flex flex-col items-center justify-center gap-0.5 px-3 py-2 
         rounded-md border border-gray-300 bg-white hover:bg-gray-50
         transition-colors duration-150 min-w-[60px];
}

.toolbar-button:hover {
  @apply border-indigo-400 shadow-sm;
}

.toolbar-divider {
  @apply w-px h-8 bg-gray-300 mx-2;
}

.layout-menu {
  @apply absolute top-full left-0 mt-1 py-1 bg-white rounded-lg shadow-lg 
         border border-gray-200 z-50 min-w-[140px];
}

.layout-item {
  @apply w-full flex items-center gap-2 px-4 py-2 text-sm 
         hover:bg-gray-50 transition-colors;
}

.layout-item.active {
  @apply bg-indigo-50 text-indigo-700 font-medium;
}
</style>

