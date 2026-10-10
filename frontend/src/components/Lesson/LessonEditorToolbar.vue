<template>
  <nav class="sticky top-0 z-30 border-b border-slate-200 bg-white">
    <div class="mx-auto px-3 sm:px-6 lg:px-8">
      <div class="flex flex-col gap-2 py-2 md:h-16 md:flex-row md:items-center md:justify-between md:py-0">
        <!-- 左侧：返回按钮 + 标题 -->
        <div class="flex w-full items-center gap-2 md:flex-1 md:gap-4">
          <button
            @click="$emit('back')"
            :class="ghostButtonClass"
            title="返回教案列表"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 19l-7-7 7-7"
              />
            </svg>
            返回
          </button>

          <input
            :value="lessonTitle"
            @input="$emit('update:lessonTitle', ($event.target as HTMLInputElement).value)"
            type="text"
            placeholder="教案标题"
            class="min-w-0 flex-1 rounded-xl border-none bg-transparent px-2 text-base font-semibold text-slate-800 outline-none focus:ring-2 focus:ring-emerald-500 md:max-w-md md:text-lg"
          />
        </div>

        <!-- 右侧：操作按钮 -->
        <div class="no-scrollbar flex w-full items-center gap-2 overflow-x-auto pb-1 md:w-auto md:gap-3 md:overflow-visible md:pb-0">
          <!-- 上课模式：仅显示导播台只读信息（结束/窗口等操作仅在下方导播台内，避免重复） -->
          <template
            v-if="
              isPreviewMode &&
              classroomPanelData?.session &&
              (classroomPanelData.session.status === 'active' ||
                classroomPanelData.session.status === 'teaching' ||
                classroomPanelData.session.status === 'TEACHING')
            "
          >
            <div class="hidden items-center gap-2.5 border-r border-gray-200 pr-3 text-xs md:mr-3 md:flex">
              <!-- 课程标题 -->
              <div class="text-gray-800 font-semibold max-w-xs truncate">
                {{ currentLesson?.title }}
              </div>
              <!-- 学生人数 -->
              <div class="flex items-center gap-1 px-2 py-0.5 bg-blue-50 rounded text-blue-700">
                <span>👥</span>
                <span class="font-medium">{{ classroomPanelData.activeStudents.length }}</span>
                <span v-if="classroomPanelData.totalStudents > 0" class="text-blue-500"
                  >/{{ classroomPanelData.totalStudents }}</span
                >
                <span class="text-blue-600">人已进入</span>
              </div>
              <!-- 模块数量 -->
              <div
                v-if="cellsCount > 0"
                class="flex items-center gap-1 px-2 py-0.5 bg-purple-50 rounded text-purple-700"
              >
                <span>📚</span>
                <span class="font-medium">{{ cellsCount }}</span>
                <span class="text-purple-600">个模块</span>
              </div>
              <!-- 时长 -->
              <div
                class="flex items-center gap-1 px-2 py-0.5 bg-emerald-50 rounded text-emerald-700"
              >
                <span>⏱️</span>
                <span class="font-medium">{{
                  classroomPanelData.formatDuration?.(classroomPanelData.displayDuration) ||
                  '0分钟'
                }}</span>
                <span v-if="classroomPanelData.remainingTime > 0" class="text-emerald-600">
                  剩余:
                  {{
                    classroomPanelData.formatRemainingTime?.(classroomPanelData.remainingTime) ||
                    ''
                  }}
                </span>
              </div>
            </div>
          </template>

          <!-- 第一组：核心操作 -->
          <div class="flex shrink-0 items-center gap-2 border-r border-gray-200 pr-2 md:pr-3">
            <!-- 保存状态指示器 -->
            <div class="hidden items-center gap-2 text-sm sm:flex">
              <span v-if="saveStatus === 'saving'" class="text-gray-500 flex items-center gap-1">
                <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle
                    class="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="4"
                  ></circle>
                  <path
                    class="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                保存中...
              </span>
              <span
                v-else-if="saveStatus === 'saved'"
                class="text-green-600 flex items-center gap-1"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                已保存
              </span>
              <span
                v-else-if="saveStatus === 'error'"
                class="text-red-600 flex items-center gap-1"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
                保存失败
              </span>
              <span v-else-if="lastSavedAt" class="text-gray-500">
                {{ formatSaveTime(lastSavedAt) }}
              </span>
            </div>

            <!-- 手动保存按钮 -->
            <button
              @click="$emit('manual-save')"
              :disabled="saveStatus === 'saving'"
              :class="isPreviewMode ? previewSaveButtonClass : saveButtonClass"
              :title="isPreviewMode ? '授课模式下无法保存，点击将提示切换到编辑模式' : '保存教案'"
            >
              {{ isPreviewMode ? '保存（需切换模式）' : '保存' }}
            </button>

            <!-- 发布按钮 -->
            <button
              v-if="currentLesson?.status === 'draft'"
              @click="$emit('publish')"
              :disabled="isSaving"
              :class="primaryButtonClass"
            >
              发布
            </button>

            <!-- 教案状态提示 -->
            <div
              v-if="isRecentlyUnpublished"
              class="hidden items-center gap-2 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-700 lg:flex"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              已从已发布状态切换为草稿
            </div>
          </div>

          <!-- 第二组：辅助工具 -->
          <div class="flex shrink-0 items-center gap-2 border-r border-gray-200 pr-2 md:pr-3">
            <!-- AI 助手 -->
            <button
              type="button"
              @click="$emit('show-ai-assistant')"
              :class="aiButtonClass"
            >
              <svg class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path
                  d="M10 2a6 6 0 00-6 6v1.586l-.707.707A1 1 0 004 12h1v1a4 4 0 004 4v1h2v-1a4 4 0 004-4v-1h1a1 1 0 00.707-1.707L16 9.586V8a6 6 0 00-6-6z"
                />
              </svg>
              AI 助手
            </button>
          </div>

          <!-- 第三组：视图控制 -->
          <div class="flex shrink-0 items-center gap-2 border-r border-gray-200 pr-2 md:pr-3">
            <!-- 紧凑模式切换 -->
            <button
              v-if="!isPreviewMode"
              @click="$emit('toggle-compact')"
              :class="compactMode ? primaryButtonClass : ghostButtonClass"
              title="紧凑模式：限制长内容的高度，便于浏览教案结构"
            >
              <svg
                class="h-4 w-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
              {{ compactMode ? '展开模式' : '紧凑模式' }}
            </button>

            <!-- 预览模式切换 -->
            <button
              @click="$emit('toggle-preview')"
              :disabled="!canEnterPreviewMode && !isPreviewMode"
              :class="
                isPreviewMode
                  ? primaryButtonClass
                  : canEnterPreviewMode
                    ? ghostButtonClass
                    : disabledButtonClass
              "
              :title="
                !canEnterPreviewMode && !isPreviewMode ? '需要先发布教案才能进入授课模式' : ''
              "
            >
              {{ isPreviewMode ? '编辑模式' : '授课模式' }}
            </button>

            <!-- 全屏预览只在编辑教案时使用 -->
            <button
              @click="$emit('fullscreen-preview')"
              :disabled="isPreviewMode"
              :class="isPreviewMode ? disabledButtonClass : ghostButtonClass"
              :title="isPreviewMode ? '全屏预览仅在编辑模式下可用' : '全屏预览'"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                />
              </svg>
              全屏预览
            </button>
          </div>

          <!-- 第四组：导出操作 -->
          <div class="flex shrink-0 items-center gap-2">
            <!-- 导出教案按钮 -->
            <button
              v-if="currentLesson"
              type="button"
              @click="$emit('export-lesson')"
              :disabled="exporting"
              :class="primaryButtonClass"
              title="导出教案为ZIP文件"
            >
              <svg v-if="exporting" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                ></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              <svg v-else class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              {{ exporting ? '导出中...' : '导出教案' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import type { Lesson } from '@/types/lesson'

interface ClassroomPanelData {
  session: any
  activeStudents: any[]
  totalStudents: number
  displayDuration: number
  remainingTime: number
  formatDuration?: (duration: number) => string
  formatRemainingTime?: (remaining: number) => string
  handleToggleDisplayMode?: () => void
  handlePause?: () => void
  handleEnd?: () => void
}

interface Props {
  lessonTitle: string
  saveStatus: 'saving' | 'saved' | 'error' | 'idle' | null
  lastSavedAt: Date | null
  isPreviewMode: boolean
  compactMode: boolean
  canEnterPreviewMode: boolean
  currentLesson: Lesson | null
  isSaving: boolean
  isRecentlyUnpublished: boolean
  exporting: boolean
  classroomPanelData: ClassroomPanelData | null
  cellsCount: number
  formatSaveTime: (date: Date) => string
}

defineProps<Props>()

const ghostButtonClass =
  'inline-flex h-9 shrink-0 items-center gap-1.5 whitespace-nowrap rounded-xl bg-white px-3 text-sm font-medium text-slate-700 shadow-sm ring-1 ring-inset ring-slate-200 transition-all hover:bg-slate-50 hover:ring-slate-300 disabled:cursor-not-allowed disabled:opacity-50'

const saveButtonClass =
  'inline-flex h-9 shrink-0 items-center gap-1.5 whitespace-nowrap rounded-xl bg-white px-3 text-sm font-medium text-emerald-700 shadow-sm ring-1 ring-inset ring-emerald-200 transition-all hover:bg-emerald-50 hover:ring-emerald-300 disabled:cursor-not-allowed disabled:opacity-50'

const previewSaveButtonClass =
  'inline-flex h-9 shrink-0 items-center gap-1.5 whitespace-nowrap rounded-xl bg-white px-3 text-sm font-medium text-amber-700 shadow-sm ring-1 ring-inset ring-amber-200 transition-all hover:bg-amber-50 hover:ring-amber-300 disabled:cursor-not-allowed disabled:opacity-50'

const disabledButtonClass =
  'inline-flex h-9 shrink-0 cursor-not-allowed items-center gap-1.5 whitespace-nowrap rounded-xl bg-gray-50 px-3 text-sm font-medium text-gray-400 shadow-sm ring-1 ring-inset ring-gray-200'

const primaryButtonClass =
  'inline-flex h-9 shrink-0 items-center gap-1.5 whitespace-nowrap rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 px-3 text-sm font-medium text-white shadow-lg shadow-emerald-500/30 transition-all hover:from-emerald-600 hover:to-teal-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'

const aiButtonClass =
  'inline-flex h-9 shrink-0 items-center gap-1.5 whitespace-nowrap rounded-xl bg-white px-3 text-sm font-medium text-violet-700 shadow-sm ring-1 ring-inset ring-violet-200 transition-all hover:bg-violet-50 hover:ring-violet-300 focus:outline-none focus:ring-2 focus:ring-violet-200 focus:ring-offset-2'

defineEmits<{
  'update:lessonTitle': [value: string]
  'back': []
  'manual-save': []
  'publish': []
  'toggle-compact': []
  'toggle-preview': []
  'fullscreen-preview': []
  'show-ai-assistant': []
  'export-lesson': []
}>()
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
