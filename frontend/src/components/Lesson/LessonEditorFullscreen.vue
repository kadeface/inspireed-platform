<template>
  <Teleport to="body">
    <Transition name="fullscreen-fade">
      <div
        v-if="isFullscreenPreview"
        class="fixed inset-0 z-50 bg-gray-50 overflow-hidden flex flex-col"
      >
        <!-- 全屏预览顶部栏 -->
        <header v-if="!slideFullscreen" class="bg-white shadow-sm z-10 flex-shrink-0">
          <div class="px-6 py-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-4">
                <div>
                  <h1 class="text-xl font-bold text-gray-900">{{ lessonTitle }}</h1>
                  <p class="text-sm text-gray-500 mt-1">
                    {{ slideMode ? '幻灯片模式' : '沉浸式预览' }}
                  </p>
                </div>
              </div>
              <div class="flex items-center gap-4">
                <!-- 幻灯片模式切换 -->
                <button
                  @click="emit('toggle-slide-mode')"
                  :class="[
                    'px-4 py-2 text-sm font-medium rounded-lg transition-colors flex items-center gap-2',
                    slideMode
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50',
                  ]"
                  title="切换幻灯片模式"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                    />
                  </svg>
                  {{ slideMode ? '滚动模式' : '幻灯片模式' }}
                </button>

                <!-- 幻灯片全屏按钮 -->
                <button
                  v-if="slideMode"
                  @click="emit('toggle-slide-fullscreen')"
                  :class="[
                    'px-4 py-2 text-sm font-medium rounded-lg transition-colors flex items-center gap-2',
                    slideFullscreen
                      ? 'bg-green-600 text-white hover:bg-green-700'
                      : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50',
                  ]"
                  title="全屏模式"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
                    />
                  </svg>
                  {{ slideFullscreen ? '退出全屏' : '全屏' }}
                </button>

                <!-- 退出全屏按钮 -->
                <button
                  @click="emit('exit-fullscreen')"
                  class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                  退出预览
                </button>
              </div>
            </div>
          </div>
        </header>

        <!-- 全屏预览内容区域 -->
        <div class="flex-1 overflow-hidden relative">
          <!-- 滚动模式 -->
          <div v-if="!slideMode" class="h-full overflow-y-auto bg-gray-50">
            <div class="w-full px-4 sm:px-6 lg:px-8 py-6">
              <!-- Cell 列表 -->
              <div v-if="displayCells.length > 0" class="space-y-4 max-w-none">
                <CellContainer
                  v-for="(cell, index) in displayCells"
                  :key="cell.id"
                  :cell="cell"
                  :index="Number(index)"
                  :editable="false"
                  :draggable="false"
                  :show-move-buttons="false"
                  :compact-mode="compactMode"
                />
              </div>

              <!-- 空状态 -->
              <div v-else class="text-center py-12">
                <svg
                  class="mx-auto h-12 w-12 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <p class="mt-4 text-lg text-gray-600">该教案暂无内容</p>
              </div>
            </div>
          </div>

          <!-- 幻灯片模式 -->
          <div
            v-else
            ref="slideContainerRef"
            class="h-full bg-gray-50"
            :class="{
              'slide-fullscreen-mode': slideFullscreen,
              'overflow-y-auto': !slideFullscreen,
            }"
            :style="slideFullscreen ? 'overflow: hidden; position: relative;' : ''"
            @mousemove="emit('slide-mouse-move', $event)"
            @touchstart="emit('slide-mouse-move', $event)"
            @mouseleave="emit('slide-mouse-leave')"
          >
            <div
              class="flex justify-center relative"
              :class="slideFullscreen ? 'h-full p-0 overflow-y-auto' : 'p-8 items-center'"
            >
              <Transition name="slide-fade" mode="out-in">
                <div
                  v-if="currentCell"
                  :key="`slide-${currentCell.id}`"
                  :class="
                    slideFullscreen
                      ? 'w-full min-h-full flex items-start justify-center p-8'
                      : 'w-full max-w-6xl'
                  "
                >
                  <div :class="slideFullscreen ? 'w-full max-w-7xl mx-auto my-auto' : 'w-full'">
                    <CellContainer
                      :cell="currentCell"
                      :index="currentSlideIndex"
                      :editable="false"
                      :draggable="false"
                      :show-move-buttons="false"
                      :compact-mode="false"
                    />
                  </div>
                </div>
                <div v-else key="empty-slide" class="text-center py-12 w-full">
                  <svg
                    class="mx-auto h-12 w-12 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  <p class="mt-4 text-lg text-gray-600">该教案暂无内容</p>
                </div>
              </Transition>
            </div>

            <!-- 全屏模式下的浮动控制按钮 -->
            <Transition name="controls-fade">
              <div
                v-if="slideFullscreen && displayCells.length > 0 && showSlideControls"
                class="fixed bottom-8 right-8 z-[9999] flex items-center gap-4 flex-shrink-0"
                style="height: auto !important; width: auto !important; pointer-events: auto"
                @mouseenter="emit('controls-mouse-enter')"
                @mouseleave="emit('controls-mouse-leave')"
              >
                <!-- 上一页按钮 -->
                <button
                  @click="emit('previous-slide')"
                  :disabled="currentSlideIndex === 0"
                  :class="[
                    'w-10 h-10 rounded-full flex items-center justify-center transition-all shadow-md touch-manipulation',
                    currentSlideIndex === 0
                      ? 'bg-gray-100 bg-opacity-80 text-gray-400 cursor-not-allowed'
                      : 'bg-white bg-opacity-90 hover:bg-opacity-100 text-gray-700 hover:shadow-lg border border-gray-300 active:scale-95',
                  ]"
                  title="上一页"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>

                <!-- 页码显示 -->
                <div
                  class="px-4 py-1.5 bg-white bg-opacity-90 rounded-full border border-gray-300 shadow-md min-w-[80px] text-center"
                >
                  <span class="text-sm font-semibold text-gray-800">
                    {{ currentSlideIndex + 1 }} / {{ displayCells.length }}
                  </span>
                </div>

                <!-- 下一页按钮 -->
                <button
                  @click="emit('next-slide')"
                  :disabled="currentSlideIndex >= displayCells.length - 1"
                  :class="[
                    'w-10 h-10 rounded-full flex items-center justify-center transition-all shadow-md touch-manipulation',
                    currentSlideIndex >= displayCells.length - 1
                      ? 'bg-gray-100 bg-opacity-80 text-gray-400 cursor-not-allowed'
                      : 'bg-white bg-opacity-90 hover:bg-opacity-100 text-gray-700 hover:shadow-lg border border-gray-300 active:scale-95',
                  ]"
                  title="下一页"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
                  </svg>
                </button>

                <!-- 退出全屏按钮 -->
                <button
                  @click="emit('toggle-slide-fullscreen')"
                  class="px-3 py-1.5 bg-white bg-opacity-90 hover:bg-opacity-100 border border-gray-300 rounded-lg shadow-md flex items-center gap-1.5 text-xs font-medium text-gray-700 transition-all ml-2"
                  title="退出全屏 (ESC)"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                  <span>退出</span>
                </button>
              </div>
            </Transition>
          </div>

          <!-- 滚动模式的浮动操作按钮 -->
          <div v-if="!slideMode" class="fixed bottom-8 right-8 flex flex-col gap-3">
            <!-- 返回顶部 -->
            <button
              @click="emit('scroll-to-top')"
              class="p-3 bg-white rounded-full shadow-lg hover:shadow-xl transition-shadow border border-gray-200"
              title="返回顶部"
            >
              <svg
                class="w-6 h-6 text-gray-700"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M5 10l7-7m0 0l7 7m-7-7v18"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Cell } from '@/types/cell'
import CellContainer from '@/components/Cell/CellContainer.vue'

interface Props {
  isFullscreenPreview: boolean
  lessonTitle: string
  slideMode: boolean
  slideFullscreen: boolean
  compactMode: boolean
  displayCells: Cell[]
  currentCell: Cell | null
  currentSlideIndex: number
  showSlideControls: boolean
  slideContainerRef: any
}

defineProps<Props>()

const emit = defineEmits<{
  'exit-fullscreen': []
  'toggle-slide-mode': []
  'toggle-slide-fullscreen': []
  'previous-slide': []
  'next-slide': []
  'slide-mouse-move': [event: any]
  'slide-mouse-leave': []
  'controls-mouse-enter': []
  'controls-mouse-leave': []
  'scroll-to-top': []
}>()
</script>

<style scoped>
/* 全屏预览动画 */
.fullscreen-fade-enter-active,
.fullscreen-fade-leave-active {
  transition: all 0.3s ease;
}

.fullscreen-fade-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.fullscreen-fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

/* 幻灯片切换动画 */
.slide-fade-enter-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}

.slide-fade-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
  position: absolute;
  width: 100%;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.slide-fade-enter-to,
.slide-fade-leave-from {
  opacity: 1;
  transform: translateX(0);
}

/* 触摸优化 */
.touch-manipulation {
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}

/* 幻灯片全屏模式 */
.slide-fullscreen-mode {
  @apply bg-gray-900;
}

.slide-fullscreen-mode .flex {
  height: 100%;
}

/* 全屏模式下隐藏 CellContainer 的边框和背景，添加白色背景 */
.slide-fullscreen-mode :deep(.cell-container) {
  @apply border-0 shadow-lg bg-white rounded-lg;
  max-height: none;
  max-width: 95vw;
  margin: auto;
  overflow: visible;
}

.slide-fullscreen-mode :deep(.cell-container > div) {
  @apply bg-white;
}

/* 确保文本内容可以滚动 */
.slide-fullscreen-mode :deep(.cell-container .text-cell-view),
.slide-fullscreen-mode :deep(.cell-container .text-cell-editor),
.slide-fullscreen-mode :deep(.cell-container .prose) {
  max-height: none;
  overflow: visible;
}

/* 全屏模式下优化内容显示 */
.slide-fullscreen-mode :deep(.cell-container .prose) {
  @apply max-w-none;
}

.slide-fullscreen-mode :deep(.cell-container img) {
  @apply max-h-[70vh] mx-auto;
}

/* 浏览器原生全屏模式下的样式 */
:fullscreen .slide-fullscreen-mode,
:-webkit-full-screen .slide-fullscreen-mode,
:-moz-full-screen .slide-fullscreen-mode,
:-ms-fullscreen .slide-fullscreen-mode {
  @apply bg-gray-900;
}

/* 只对幻灯片内容区域应用全屏样式，不影响按钮容器 */
:fullscreen .slide-fullscreen-mode > .flex.justify-center,
:-webkit-full-screen .slide-fullscreen-mode > .flex.justify-center,
:-moz-full-screen .slide-fullscreen-mode > .flex.justify-center,
:-ms-fullscreen .slide-fullscreen-mode > .flex.justify-center {
  min-height: 100vh;
  width: 100vw;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 确保按钮容器不受全屏样式影响，并确保在最上层 */
:fullscreen .slide-fullscreen-mode .fixed.bottom-8.right-8,
:-webkit-full-screen .slide-fullscreen-mode .fixed.bottom-8.right-8,
:-moz-full-screen .slide-fullscreen-mode .fixed.bottom-8.right-8,
:-ms-fullscreen .slide-fullscreen-mode .fixed.bottom-8.right-8 {
  height: auto !important;
  width: auto !important;
  flex-shrink: 0;
  z-index: 9999 !important;
  pointer-events: auto !important;
}

/* 确保按钮本身可以点击 */
:fullscreen .slide-fullscreen-mode .fixed.bottom-8.right-8 button,
:-webkit-full-screen .slide-fullscreen-mode .fixed.bottom-8.right-8 button,
:-moz-full-screen .slide-fullscreen-mode .fixed.bottom-8.right-8 button,
:-ms-fullscreen .slide-fullscreen-mode .fixed.bottom-8.right-8 button {
  pointer-events: auto !important;
  position: relative;
  z-index: 10000;
}

/* 控制按钮淡入淡出动画 */
.controls-fade-enter-active,
.controls-fade-leave-active {
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
}

.controls-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.controls-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* 滚动条样式优化 */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
