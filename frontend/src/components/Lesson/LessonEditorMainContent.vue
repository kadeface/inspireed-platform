<template>
  <div class="flex flex-1 overflow-hidden">
    <!-- 左侧：Cell 工具箱 -->
    <CellToolbar
      v-if="!isPreviewMode && !isFullscreenPreview"
      :collapsed="toolbarCollapsed"
      @add-cell="(cellType) => {
        console.log('LessonEditorMainContent: 收到 add-cell 事件', { cellType })
        emit('add-cell-to-end', cellType)
      }"
      @toggle-collapsed="emit('toggle-toolbar-collapsed')"
    />

    <!-- 全屏预览时整块 <main> 不渲染（见下方 v-if="!isFullscreenPreview"），导播台若仍放在 main 内会一起消失。
         因此在全屏下用 Teleport 挂到 body，并置于全屏层（z-50）之上。 -->
    <Teleport to="body">
      <div
        v-if="isFullscreenPreview && isPreviewMode && showClassroomPanel && currentLesson"
        class="fixed left-0 right-0 z-[60] max-h-[min(45vh,440px)] overflow-y-auto px-2 sm:px-4 pointer-events-auto"
        style="top: 5.5rem"
        data-testid="teacher-control-panel-fullscreen-teleport"
      >
        <TeacherClassroomControlPanel
          key="teacher-control-panel-fullscreen"
          :lesson-id="currentLesson.id"
          :lesson="currentLesson"
          @session-changed="emit('session-changed', $event)"
        />
      </div>
    </Teleport>

    <!-- 中间：编辑区 -->
    <main v-if="!isFullscreenPreview" class="flex-1 overflow-y-auto bg-gray-50">
      <div :class="[isPreviewMode ? 'w-full py-4 px-2' : 'w-full py-6 px-4 sm:px-6 lg:px-8']">
        <!-- 加载状态 -->
        <div v-if="isLoading" class="text-center py-12">
          <div
            class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
          ></div>
          <p class="mt-4 text-gray-600">加载教案中...</p>
        </div>

        <!-- 错误状态 -->
        <div
          v-else-if="loadError"
          class="bg-red-50 border border-red-200 rounded-lg p-6 text-center"
        >
          <svg
            class="mx-auto h-12 w-12 text-red-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 class="mt-4 text-lg font-medium text-gray-900">加载失败</h3>
          <p class="mt-2 text-sm text-gray-600">{{ loadError }}</p>
          <button
            @click="emit('back')"
            class="mt-6 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            返回教案列表
          </button>
        </div>

        <!-- Cell 列表 -->
        <div v-else-if="currentLesson" :class="isPreviewMode ? 'space-y-2' : 'space-y-4'">
          <!-- 封面预览区域（仅在编辑模式下显示） -->
          <div v-if="!isPreviewMode" class="mb-6">
            <div
              class="relative h-64 rounded-2xl overflow-hidden bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500 shadow-lg"
            >
              <!-- 封面图片 -->
              <img
                v-if="coverImageUrl && !coverImageLoadError"
                :src="coverImageUrl"
                :alt="currentLesson.title"
                class="h-full w-full object-cover transition-transform duration-200 hover:scale-105"
                @error="emit('cover-image-error')"
                @load="emit('cover-image-load')"
              />
              <!-- 无封面时的占位符 -->
              <div
                v-else
                class="absolute inset-0 flex flex-col items-center justify-center gap-3 text-white/90"
              >
                <div
                  class="rounded-2xl bg-white/20 backdrop-blur-md p-4 ring-2 ring-inset ring-white/30 shadow-xl"
                >
                  <svg class="h-12 w-12" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="1.6"
                      d="M4.75 5.75A2.75 2.75 0 0 1 7.5 3h9a2.75 2.75 0 0 1 2.75 2.75v14.5l-5.5-3.083L8.25 20.25V5.75"
                    />
                  </svg>
                </div>
                <span class="text-base font-semibold tracking-wide text-white/90 drop-shadow-sm"
                  >教案封面</span
                >
              </div>

              <!-- 渐变遮罩层 -->
              <div
                class="absolute inset-0 bg-gradient-to-t from-slate-900/60 via-slate-900/20 to-slate-900/0"
              ></div>

              <!-- 封面按钮 -->
              <div class="absolute bottom-4 right-4 z-10">
                <button
                  type="button"
                  @click="emit('upload-cover-image')"
                  class="inline-flex items-center gap-2 rounded-md bg-white/90 backdrop-blur-sm border border-white/30 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-white hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-white/50 transition-all shadow-md"
                  title="上传封面图片"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                  封面
                </button>
              </div>
            </div>
          </div>

          <!-- 课堂控制面板（预览模式下；非全屏 — 全屏时见上方 Teleport） -->
          <div
            v-if="!isFullscreenPreview && isPreviewMode && showClassroomPanel && currentLesson"
            :class="isPreviewMode ? 'mb-2' : 'mb-6'"
          >
            <TeacherClassroomControlPanel
              key="teacher-control-panel-inline"
              :lesson-id="currentLesson.id"
              :lesson="currentLesson"
              @session-changed="emit('session-changed', $event)"
            />
          </div>

          <!-- MVP: 参考资源面板 -->
          <ReferenceResourcePanel
            v-if="showReferencePanel && referenceResource && !isPreviewMode"
            :lesson-id="currentLesson.id"
            :resource="referenceResource"
            :notes="currentLesson.reference_notes"
            @close="emit('close-reference-panel')"
            @view-pdf="emit('show-pdf-viewer')"
            @notes-updated="emit('update-notes', $event)"
          />

          <!-- 空状态 -->
          <div
            v-if="sections.length === 0"
            class="bg-white border-2 border-dashed border-gray-300 rounded-lg p-12 text-center"
          >
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
                d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <h3 class="mt-4 text-lg font-medium text-gray-900">开始创建教案内容</h3>
            <p class="mt-2 text-sm text-gray-600">
              在下方大环节中点击「+」添加单元，或从左侧工具栏选择
            </p>
          </div>

          <!-- 大环节列表 -->
          <div ref="cellListRef" :class="isPreviewMode ? 'space-y-2' : 'space-y-4'">
            <!-- 编辑模式：标签页导航（可拖拽、可编辑） -->
            <div v-if="!isPreviewMode" class="mb-4">
              <div class="flex items-center gap-2 border-b border-gray-200 overflow-x-auto pb-1 no-scrollbar">
                <!-- 标签列表容器，用于 Sortable -->
                <div ref="tabsContainerRef" class="flex items-center gap-2">
                  <div
                    v-for="(sec, index) in sections"
                    :key="sec.id"
                    class="group relative flex items-center gap-2 px-4 py-2 rounded-t-lg border cursor-pointer select-none transition-all min-w-[140px] max-w-[200px]"
                    :class="activeSectionIndex === index ? 'bg-white border-gray-200 border-b-white text-blue-600 font-medium -mb-[1px] z-10 shadow-sm' : 'bg-gray-50 border-transparent text-gray-500 hover:bg-gray-100 hover:text-gray-700'"
                    @click="emit('set-active-section', index)"
                    :data-id="sec.id"
                  >
                    <!-- 拖拽手柄 -->
                    <span class="drag-handle cursor-move text-gray-400 hover:text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                      </svg>
                    </span>

                    <!-- 名称/编辑框 -->
                    <input
                      v-if="editingTabId === sec.id"
                      :ref="el => setEditingTabRef(el, sec.id)"
                      v-model="sec.name"
                      type="text"
                      class="w-full px-1 py-0.5 text-sm border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
                      @blur="emit('tab-edit-done')"
                      @keydown.enter="emit('tab-edit-done')"
                      @click.stop
                    />
                    <span
                      v-else
                      class="text-sm truncate flex-1"
                      @dblclick="emit('tab-dbl-click', sec)"
                      :title="sec.name"
                    >
                      {{ sec.name }}
                    </span>

                    <!-- 删除按钮 (仅自定义环节) -->
                    <button
                      v-if="sec.type === 'custom'"
                      @click.stop="emit('delete-section', index)"
                      class="p-0.5 text-gray-400 hover:text-red-500 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                      title="删除环节"
                    >
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>

                <!-- 添加按钮 -->
                <button
                  @click="emit('add-section')"
                  class="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-lg text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                  title="添加大环节"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- 授课模式：上课流程导航（只读，便于快速跳转） -->
            <div v-if="isPreviewMode && sections.length > 0" class="mb-4">
              <div class="flex items-center gap-2 border-b border-gray-200 overflow-x-auto pb-1 no-scrollbar">
                <span class="text-xs text-gray-500 flex-shrink-0 mr-2">上课流程：</span>
                <div class="flex items-center gap-2">
                  <button
                    v-for="(sec, index) in sections"
                    :key="sec.id"
                    type="button"
                    class="px-3 py-1.5 rounded-t-lg text-sm font-medium transition-colors flex-shrink-0"
                    :class="activeSectionIndex === index ? 'bg-blue-50 text-blue-600 border border-b-0 border-gray-200 -mb-[1px]' : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border border-transparent'"
                    @click="handlePreviewModeSectionClick(index)"
                  >
                    {{ sec.name }}
                  </button>
                </div>
              </div>
            </div>

            <!-- 编辑模式：当前选中大环节的内容 -->
            <template v-if="!isPreviewMode && sections[activeSectionIndex]">
              <SectionContainer
                :key="`${sections[activeSectionIndex].id}-${sections[activeSectionIndex].cells?.length || 0}`"
                :section="sections[activeSectionIndex]"
                :section-index="activeSectionIndex"
                :cell-offset="sections.slice(0, activeSectionIndex).reduce((a, s) => a + (s.cells?.length || 0), 0)"
                :editable="true"
                :compact-mode="compactMode"
                :lesson-id="currentLesson?.id"
                :show-header="false"
                @update:section="(p) => emit('update-section', { index: activeSectionIndex, payload: p })"
                @add-cell="(sectionIndex, indexInSection, cellType) => emit('add-cell-in-section', { sectionIndex, indexInSection, cellType })"
                @cell-update="emit('cell-update', $event)"
                @cell-delete="emit('cell-delete', $event)"
                @cell-move-up="emit('cell-move-up', $event)"
                @cell-move-down="emit('cell-move-down', $event)"
              />
            </template>

            <!-- 预览模式：显示所有大环节 -->
            <template v-else-if="isPreviewMode">
              <div
                v-for="(sec, si) in sections"
                :key="`${sec.id}-${sec.cells?.length || 0}`"
                :id="`section-preview-${si}`"
              >
                <SectionContainer
                  :section="sec"
                  :section-index="si"
                  :cell-offset="sections.slice(0, si).reduce((a, s) => a + (s.cells?.length || 0), 0)"
                  :editable="false"
                  :compact-mode="false"
                  :lesson-id="currentLesson?.id"
                  :show-header="true"
                  @update:section="(p) => emit('update-section', { index: si, payload: p })"
                  @add-cell="(sectionIndex, indexInSection, cellType) => emit('add-cell-in-section', { sectionIndex, indexInSection, cellType })"
                  @cell-update="emit('cell-update', $event)"
                  @cell-delete="emit('cell-delete', $event)"
                  @cell-move-up="emit('cell-move-up', $event)"
                  @cell-move-down="emit('cell-move-down', $event)"
                />
              </div>
            </template>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { nextTick } from 'vue'
import type { Lesson } from '@/types/lesson'
import type { SectionInContent } from '@/types/section'
import CellToolbar from '@/components/Lesson/CellToolbar.vue'
import SectionContainer from '@/components/Lesson/SectionContainer.vue'
import TeacherClassroomControlPanel from '@/components/Classroom/TeacherControlPanel.vue'
import ReferenceResourcePanel from '@/components/Resource/ReferenceResourcePanel.vue'

interface Props {
  isLoading: boolean
  loadError: string | null
  currentLesson: Lesson | null
  isPreviewMode: boolean
  isFullscreenPreview: boolean
  compactMode: boolean
  toolbarCollapsed: boolean
  showClassroomPanel: boolean
  showReferencePanel: boolean
  referenceResource: any
  coverImageUrl: string | null
  coverImageLoadError: boolean
  sections: SectionInContent[]
  activeSectionIndex: number
  editingTabId: string | null
  cellListRef: any
  tabsContainerRef: any
}

defineProps<Props>()

const emit = defineEmits<{
  'toggle-toolbar-collapsed': []
  'add-cell-to-end': [cellType: string]
  'back': []
  'cover-image-error': []
  'cover-image-load': []
  'upload-cover-image': []
  'session-changed': [event: any]
  'close-reference-panel': []
  'show-pdf-viewer': []
  'update-notes': [notes: string]
  'set-active-section': [index: number]
  'tab-dbl-click': [section: SectionInContent]
  'tab-edit-done': []
  'delete-section': [index: number]
  'add-section': []
  'update-section': [data: { index: number, payload: any }]
  'add-cell-in-section': [data: any]
  'cell-update': [cell: any]
  'cell-delete': [cellId: string]
  'cell-move-up': [cellId: string]
  'cell-move-down': [cellId: string]
}>()

// 授课模式下点击大环节标签：更新选中状态并滚动到对应区域
function handlePreviewModeSectionClick(index: number) {
  emit('set-active-section', index)
  nextTick(() => {
    const el = document.getElementById(`section-preview-${index}`)
    el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

// 辅助函数：设置编辑tab的ref
function setEditingTabRef(el: any, tabId: string) {
  if (el) {
    // 父组件会管理这个ref
    emit('tab-edit-done')
  }
}
</script>
