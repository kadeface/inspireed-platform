<template>
  <div class="diagram-toolbar">
    <div class="toolbar-left">
      <!-- 模式切换 -->
      <div class="mode-switcher">
        <button
          v-for="m in modes"
          :key="m.value"
          :class="['mode-btn', { active: mode === m.value }]"
          @click="$emit('change-mode', m.value)"
        >
          <span class="icon">{{ m.icon }}</span>
          <span>{{ m.label }}</span>
        </button>
      </div>

      <div class="divider"></div>

      <!-- 编辑操作 -->
      <div class="toolbar-group">
        <button
          class="toolbar-btn"
          :disabled="!canUndo"
          @click="$emit('undo')"
          title="撤销 (Ctrl+Z)"
        >
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
          </svg>
        </button>
        <button
          class="toolbar-btn"
          :disabled="!canRedo"
          @click="$emit('redo')"
          title="重做 (Ctrl+Y)"
        >
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 10H11a8 8 0 00-8 8v2m18-10l-6 6m6-6l-6-6" />
          </svg>
        </button>
      </div>

      <div class="divider"></div>

      <!-- 视图操作 -->
      <div class="toolbar-group">
        <button
          class="toolbar-btn"
          @click="$emit('zoom-in')"
          title="放大"
        >
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
          </svg>
        </button>
        <button
          class="toolbar-btn"
          @click="$emit('zoom-out')"
          title="缩小"
        >
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
          </svg>
        </button>
        <button
          class="toolbar-btn"
          @click="$emit('fit-view')"
          title="适应画布"
        >
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
          </svg>
        </button>
      </div>

      <div class="divider"></div>

      <!-- 全屏按钮 -->
      <div class="toolbar-group">
        <button
          class="toolbar-btn-fullscreen"
          :class="{ 'active': isFullscreen }"
          @click="$emit('toggle-fullscreen')"
          :title="isFullscreen ? '退出全屏 (Esc)' : '全屏编辑'"
        >
          <svg v-if="!isFullscreen" class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
          </svg>
          <svg v-else class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
          <span class="text-sm font-medium">{{ isFullscreen ? '退出全屏' : '全屏' }}</span>
        </button>
      </div>
    </div>

    <div class="toolbar-right">
      <!-- 导出 -->
      <div class="toolbar-group">
        <button
          class="toolbar-btn-text"
          @click="showExportMenu = !showExportMenu"
        >
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          <span>导出</span>
        </button>

        <!-- 导出菜单 -->
        <div v-if="showExportMenu" class="export-menu" v-click-outside="() => showExportMenu = false">
          <button
            v-for="format in exportFormats"
            :key="format.value"
            class="export-item"
            @click="handleExport(format.value)"
          >
            <span class="icon">{{ format.icon }}</span>
            <span>{{ format.label }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { DiagramMode, DiagramExportFormat } from '@/types/diagram'

interface Props {
  mode: DiagramMode
  canUndo: boolean
  canRedo: boolean
  isFullscreen?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isFullscreen: false,
})

const emit = defineEmits<{
  'change-mode': [mode: DiagramMode]
  undo: []
  redo: []
  'zoom-in': []
  'zoom-out': []
  'fit-view': []
  'toggle-fullscreen': []
  export: [format: DiagramExportFormat]
}>()

const showExportMenu = ref(false)

const modes = [
  { value: 'flowchart', label: '流程图', icon: '📊' },
  { value: 'mindmap', label: '思维导图', icon: '🧠' },
]

const exportFormats = [
  { value: 'png', label: 'PNG 图片', icon: '🖼️' },
  { value: 'svg', label: 'SVG 矢量图', icon: '📐' },
  { value: 'json', label: 'JSON 数据', icon: '📄' },
]

function handleExport(format: DiagramExportFormat) {
  emit('export', format)
  showExportMenu.value = false
}

// 点击外部关闭菜单的指令
const vClickOutside = {
  mounted(el: HTMLElement, binding: any) {
    el._clickOutside = (event: MouseEvent) => {
      if (!(el === event.target || el.contains(event.target as Node))) {
        binding.value()
      }
    }
    document.addEventListener('click', el._clickOutside)
  },
  unmounted(el: any) {
    document.removeEventListener('click', el._clickOutside)
    delete el._clickOutside
  },
}
</script>

<style scoped>
.diagram-toolbar {
  @apply flex items-center justify-between px-4 py-2 bg-white border-b border-gray-200;
  height: 56px;
}

.toolbar-left,
.toolbar-right {
  @apply flex items-center gap-2;
}

.divider {
  @apply w-px h-6 bg-gray-300;
}

.mode-switcher {
  @apply flex items-center gap-1 bg-gray-100 rounded-lg p-1;
}

.mode-btn {
  @apply flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-600 rounded-md transition-colors;
}

.mode-btn:hover {
  @apply bg-gray-200;
}

.mode-btn.active {
  @apply bg-white text-blue-600 shadow-sm;
}

.toolbar-group {
  @apply flex items-center gap-1 relative;
}

.toolbar-btn {
  @apply p-2 text-gray-600 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.toolbar-btn-text {
  @apply flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md transition-colors;
}

.icon {
  @apply w-5 h-5;
}

.export-menu {
  @apply absolute top-full right-0 mt-2 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50;
  min-width: 160px;
}

.export-item {
  @apply w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors;
}

.export-item .icon {
  @apply text-base;
}

.toolbar-btn-fullscreen {
  @apply flex items-center gap-2 px-3 py-2 text-gray-700 bg-blue-50 hover:bg-blue-100 rounded-md transition-colors font-medium;
}

.toolbar-btn-fullscreen.active {
  @apply bg-red-50 hover:bg-red-100 text-red-700;
}
</style>

