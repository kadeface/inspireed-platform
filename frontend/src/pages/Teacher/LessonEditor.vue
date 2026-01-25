<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- 顶部工具栏 -->
    <nav class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-30">
      <div class="mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- 左侧：返回按钮 + 标题 -->
          <div class="flex items-center gap-4 flex-1">
            <button
              @click="handleBack"
              class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-xl hover:bg-white hover:shadow-md transition-all"
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
              v-model="lessonTitle"
              type="text"
              placeholder="教案标题"
              class="text-lg font-semibold text-gray-900 border-none outline-none bg-transparent flex-1 max-w-md focus:ring-2 focus:ring-blue-500 rounded px-2"
            />
          </div>

          <!-- 右侧：操作按钮 -->
          <div class="flex items-center gap-3">
            <!-- 上课模式：导播台信息 -->
            <template
              v-if="
                isPreviewMode &&
                classroomPanelData?.session &&
                classroomPanelData.session.status === 'active'
              "
            >
              <div class="flex items-center gap-2.5 text-xs border-r border-gray-200 pr-3 mr-3">
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
                  v-if="cells?.length"
                  class="flex items-center gap-1 px-2 py-0.5 bg-purple-50 rounded text-purple-700"
                >
                  <span>📚</span>
                  <span class="font-medium">{{ cells.length }}</span>
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
                <!-- 操作按钮组 -->
                <div class="flex items-center gap-1.5 ml-1">
                  <button
                    @click="classroomPanelData?.handleToggleDisplayMode?.()"
                    class="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded text-gray-700 transition-colors"
                    title="全屏显示"
                  >
                    全屏
                  </button>
                  <button
                    @click="classroomPanelData?.handlePause?.()"
                    class="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded text-gray-700 transition-colors"
                    title="暂停课程"
                  >
                    ⏸️ 暂停
                  </button>
                  <button
                    @click="classroomPanelData?.handleEnd?.()"
                    class="px-2 py-1 text-xs bg-red-100 hover:bg-red-200 rounded text-red-700 transition-colors"
                    title="结束课程"
                  >
                    ⏹️ 结束
                  </button>
                </div>
              </div>
            </template>

            <!-- 第一组：核心操作（最重要，最常用） -->
            <div class="flex items-center gap-2 border-r border-gray-200 pr-3">
              <!-- 保存状态指示器 -->
              <div class="flex items-center gap-2 text-sm">
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
                @click="handleManualSave"
                :disabled="saveStatus === 'saving'"
                :class="[
                  'px-3 py-1.5 text-sm font-medium rounded-md disabled:opacity-50',
                  isPreviewMode
                    ? 'text-amber-700 bg-amber-50 border border-amber-300 hover:bg-amber-100'
                    : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50',
                ]"
                :title="isPreviewMode ? '授课模式下无法保存，点击将提示切换到编辑模式' : '保存教案'"
              >
                {{ isPreviewMode ? '保存（需切换模式）' : '保存' }}
              </button>

              <!-- 发布按钮 -->
              <button
                v-if="currentLesson?.status === 'draft'"
                @click="handlePublish"
                :disabled="isSaving"
                class="px-3 py-1.5 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50"
              >
                发布
              </button>

              <!-- 教案状态提示 -->
              <div
                v-if="isRecentlyUnpublished"
                class="flex items-center gap-2 px-3 py-1.5 text-sm text-amber-600 bg-amber-50 rounded-md"
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

            <!-- 第二组：辅助工具（编辑辅助功能） -->
            <div class="flex items-center gap-2 border-r border-gray-200 pr-3">
              <!-- AI 助手 -->
              <button
                type="button"
                @click="showLessonAssistant = true"
                class="inline-flex items-center gap-2 rounded-md bg-gradient-to-r from-[#4C6EF5] to-[#6C8DFF] px-3 py-1.5 text-sm font-medium text-white shadow hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-[#BFD0FF]"
              >
                <svg class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path
                    d="M10 2a6 6 0 00-6 6v1.586l-.707.707A1 1 0 004 12h1v1a4 4 0 004 4v1h2v-1a4 4 0 004-4v-1h1a1 1 0 00.707-1.707L16 9.586V8a6 6 0 00-6-6z"
                  />
                </svg>
                AI 助手
              </button>
            </div>

            <!-- 隐藏的文件输入（封面按钮在封面预览区域） -->
            <input
              ref="coverImageInput"
              type="file"
              accept="image/*"
              @change="handleCoverImageSelect"
              class="hidden"
            />

            <!-- 第三组：视图控制（查看和演示功能） -->
            <div class="flex items-center gap-2 border-r border-gray-200 pr-3">
              <!-- 紧凑模式切换 -->
              <button
                v-if="!isPreviewMode"
                @click="compactMode = !compactMode"
                :class="[
                  'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                  compactMode
                    ? 'bg-purple-600 text-white hover:bg-purple-700'
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50',
                ]"
                title="紧凑模式：限制长内容的高度，便于浏览教案结构"
              >
                <svg
                  class="w-4 h-4 inline-block mr-1"
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
                @click="handleTogglePreviewMode"
                :disabled="!canEnterPreviewMode && !isPreviewMode"
                :class="[
                  'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                  isPreviewMode
                    ? 'bg-blue-600 text-white'
                    : canEnterPreviewMode
                      ? 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                      : 'bg-gray-100 text-gray-400 border border-gray-200 cursor-not-allowed',
                ]"
                :title="
                  !canEnterPreviewMode && !isPreviewMode ? '需要先发布教案才能进入授课模式' : ''
                "
              >
                {{ isPreviewMode ? '编辑模式' : '授课模式' }}
              </button>

              <!-- 全屏预览按钮 -->
              <button
                @click="toggleFullscreenPreview"
                :disabled="false"
                class="px-3 py-1.5 text-sm font-medium rounded-md bg-purple-600 text-white hover:bg-purple-700 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                :title="isPreviewMode ? '全屏预览（授课模式下可用）' : '全屏预览'"
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

            <!-- 第四组：导出操作（完成后的操作） -->
            <div class="flex items-center gap-2">
              <!-- 导出教案按钮 -->
              <button
                v-if="currentLesson"
                type="button"
                @click="handleExportLesson"
                :disabled="exporting"
                class="inline-flex items-center gap-2 rounded-md bg-blue-600 text-white px-4 py-2 text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
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

            <!-- 封面图片预览和编辑模态框 -->
            <div
              v-if="showCoverImagePreview"
              class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
              @click.self="cancelCoverImageEdit"
            >
              <div
                class="bg-white rounded-2xl shadow-2xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col"
              >
                <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                  <h3 class="text-lg font-semibold text-gray-900">编辑封面图片</h3>
                  <button
                    @click="cancelCoverImageEdit"
                    class="text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>

                <div class="flex-1 overflow-auto p-6">
                  <div class="space-y-4">
                    <!-- 图片预览 -->
                    <div
                      class="relative bg-gray-100 rounded-lg overflow-hidden"
                      style="aspect-ratio: 16/9"
                    >
                      <img
                        ref="coverImagePreview"
                        :src="coverImagePreviewUrl"
                        alt="封面预览"
                        class="w-full h-full object-contain"
                        style="max-height: 500px"
                      />
                    </div>

                    <!-- 缩放控制 -->
                    <div class="space-y-2">
                      <label class="block text-sm font-medium text-gray-700">
                        图片质量: {{ imageQuality }}%
                      </label>
                      <input
                        v-model.number="imageQuality"
                        type="range"
                        min="50"
                        max="100"
                        step="5"
                        class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                      />
                      <div class="flex justify-between text-xs text-gray-500">
                        <span>较小文件</span>
                        <span>较高质量</span>
                      </div>
                    </div>

                    <!-- 尺寸控制 -->
                    <div class="grid grid-cols-2 gap-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                          最大宽度 (px)
                        </label>
                        <input
                          v-model.number="maxImageWidth"
                          type="number"
                          min="200"
                          max="4000"
                          step="100"
                          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                          最大高度 (px)
                        </label>
                        <input
                          v-model.number="maxImageHeight"
                          type="number"
                          min="200"
                          max="4000"
                          step="100"
                          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    </div>

                    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <p class="text-sm text-blue-800">
                        <strong>提示：</strong>调整图片质量可以减小文件大小，建议使用 70-90%
                        的质量以获得最佳效果。
                      </p>
                    </div>
                  </div>
                </div>

                <div class="px-6 py-4 border-t border-gray-200 flex items-center justify-end gap-3">
                  <button
                    @click="cancelCoverImageEdit"
                    class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                  >
                    取消
                  </button>
                  <button
                    @click="processAndUploadCoverImage"
                    :disabled="isUploadingCoverImage"
                    class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {{ isUploadingCoverImage ? '上传中...' : '确认上传' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容区 -->
    <div class="flex flex-1 overflow-hidden">
      <!-- 左侧：Cell 工具箱 -->
      <CellToolbar
        v-if="!isPreviewMode && !isFullscreenPreview"
        :collapsed="toolbarCollapsed"
        @add-cell="handleAddCellToEnd"
        @toggle-collapsed="toolbarCollapsed = !toolbarCollapsed"
      />

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
              @click="handleBack"
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
                  @error="coverImageLoadError = true"
                  @load="coverImageLoadError = false"
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

                <!-- 封面按钮（放在遮罩层上，右下角） -->
                <div class="absolute bottom-4 right-4 z-10">
                  <button
                    type="button"
                    @click="triggerCoverImageUpload"
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

            <!-- 课堂控制面板（预览模式下） -->
            <TeacherClassroomControlPanel
              v-if="isPreviewMode && showClassroomPanel && currentLesson"
              ref="teacherControlPanelRef"
              :lesson-id="currentLesson.id"
              :lesson="currentLesson"
              :class="isPreviewMode ? 'mb-2' : 'mb-6'"
              @session-changed="handleSessionChanged"
            />

            <!-- MVP: 参考资源面板 -->
            <ReferenceResourcePanel
              v-if="showReferencePanel && referenceResource && !isPreviewMode"
              :lesson-id="currentLesson.id"
              :resource="referenceResource"
              :notes="currentLesson.reference_notes"
              @close="showReferencePanel = false"
              @view-pdf="showPDFViewer = true"
              @notes-updated="handleNotesUpdated"
            />

            <!-- 空状态 -->
            <div
              v-if="cells.length === 0"
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
              <!-- 编辑模式：标签页导航 -->
              <div v-if="!isPreviewMode" class="mb-4">
                <div class="flex items-center gap-2 border-b border-gray-200 overflow-x-auto pb-1 no-scrollbar">
                  <!-- 标签列表容器，用于 Sortable -->
                  <div ref="tabsContainerRef" class="flex items-center gap-2">
                    <div
                      v-for="(sec, index) in sections"
                      :key="sec.id"
                      class="group relative flex items-center gap-2 px-4 py-2 rounded-t-lg border cursor-pointer select-none transition-all min-w-[140px] max-w-[200px]"
                      :class="activeSectionIndex === index ? 'bg-white border-gray-200 border-b-white text-blue-600 font-medium -mb-[1px] z-10 shadow-sm' : 'bg-gray-50 border-transparent text-gray-500 hover:bg-gray-100 hover:text-gray-700'"
                      @click="activeSectionIndex = index"
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
                        ref="editingTabNameRef"
                        v-model="sec.name"
                        type="text"
                        class="w-full px-1 py-0.5 text-sm border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
                        @blur="editingTabId = null"
                        @keydown.enter="editingTabId = null"
                        @click.stop
                      />
                      <span
                        v-else
                        class="text-sm truncate flex-1"
                        @dblclick="handleTabDblClick(sec)"
                        :title="sec.name"
                      >
                        {{ sec.name }}
                      </span>

                      <!-- 删除按钮 (仅自定义环节) -->
                      <button
                        v-if="sec.type === 'custom'"
                        @click.stop="handleSectionDelete(index)"
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
                    @click="handleAddSection"
                    class="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-lg text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                    title="添加大环节"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                  </button>
                </div>
              </div>

              <!-- 编辑模式：当前选中大环节的内容 -->
              <template v-if="!isPreviewMode && sections[activeSectionIndex]">
                <SectionContainer
                  :key="sections[activeSectionIndex].id"
                  :section="sections[activeSectionIndex]"
                  :section-index="activeSectionIndex"
                  :cell-offset="
                    sections
                      .slice(0, activeSectionIndex)
                      .reduce((a, s) => a + (s.cells?.length || 0), 0)
                  "
                  :editable="true"
                  :compact-mode="compactMode"
                  :lesson-id="currentLesson?.id"
                  :show-header="false"
                  @update:section="(p) => handleSectionUpdate(activeSectionIndex, p)"
                  @add-cell="handleAddCellInSection"
                  @cell-update="handleCellUpdate"
                  @cell-delete="handleDeleteCell"
                  @cell-move-up="handleMoveUp"
                  @cell-move-down="handleMoveDown"
                />
              </template>

              <!-- 预览模式：显示所有大环节 (保持原有线性结构) -->
              <template v-else-if="isPreviewMode">
                <SectionContainer
                  v-for="(sec, si) in sections"
                  :key="sec.id"
                  :section="sec"
                  :section-index="si"
                  :cell-offset="
                    sections.slice(0, si).reduce((a, s) => a + (s.cells?.length || 0), 0)
                  "
                  :editable="false"
                  :compact-mode="false"
                  :lesson-id="currentLesson?.id"
                  :show-header="true"
                  @update:section="(p) => handleSectionUpdate(si, p)"
                  @add-cell="handleAddCellInSection"
                  @cell-update="handleCellUpdate"
                  @cell-delete="handleDeleteCell"
                  @cell-move-up="handleMoveUp"
                  @cell-move-down="handleMoveDown"
                />
              </template>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Toast 提示 -->
    <Transition name="toast-slide">
      <div v-if="toast.show" class="fixed top-4 right-4 z-50 max-w-sm">
        <div
          :class="[
            'rounded-lg shadow-xl p-4 border-l-4 transform transition-all duration-300',
            toast.type === 'success'
              ? 'bg-green-50 border-green-400 border-l-green-500'
              : toast.type === 'warning'
                ? 'bg-amber-50 border-amber-400 border-l-amber-500'
                : 'bg-red-50 border-red-400 border-l-red-500',
          ]"
        >
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <div
                :class="[
                  'rounded-full p-1',
                  toast.type === 'success'
                    ? 'bg-green-100'
                    : toast.type === 'warning'
                      ? 'bg-amber-100'
                      : 'bg-red-100',
                ]"
              >
                <svg
                  v-if="toast.type === 'success'"
                  class="h-4 w-4 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                <svg
                  v-else-if="toast.type === 'warning'"
                  class="h-4 w-4 text-amber-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
                <svg
                  v-else
                  class="h-4 w-4 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </div>
            </div>
            <div class="ml-3 flex-1">
              <p
                :class="[
                  'text-sm font-semibold',
                  toast.type === 'success'
                    ? 'text-green-800'
                    : toast.type === 'warning'
                      ? 'text-amber-800'
                      : 'text-red-800',
                ]"
              >
                {{ toast.message }}
              </p>
            </div>
            <button
              @click="toast.show = false"
              class="ml-2 flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <LessonAiAssistantDrawer
      v-model="showLessonAssistant"
      :lesson-title="lessonTitle"
      :lesson-outline="lessonOutline"
      @insert="handleAiInsert"
    />

    <ClassroomSelectorModal
      v-model="showPublishModal"
      :classrooms="availableClassrooms"
      :initial-selected-ids="selectedClassroomIds"
      :loading="isLoadingClassrooms"
      :error="publishModalError"
      @confirm="handlePublishConfirm"
      @cancel="handlePublishCancel"
    />

    <!-- MVP: PDF 查看器 -->
    <PDFViewerModal v-model="showPDFViewer" :resource-id="referenceResource?.id || null" />

    <!-- 浮动教学助手按钮（仅在授课模式显示） -->
    <TeachingAssistantFAB
      :visible="isPreviewMode"
      :classroom-id="currentClassroomId"
      @open-drawer="handleOpenAssistantDrawer"
    />

    <!-- 教学助手抽屉 -->
    <TeachingAssistantDrawer v-model="showAssistantDrawer" :classroom-id="currentClassroomId" />

    <!-- 全屏预览模式 -->
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
                    @click="slideMode = !slideMode"
                    :class="[
                      'px-4 py-2 text-sm font-medium rounded-lg transition-colors flex items-center gap-2',
                      slideMode
                        ? 'bg-blue-600 text-white hover:bg-blue-700'
                        : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50',
                    ]"
                    title="切换幻灯片模式：一页一页播放，适合大屏授课"
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

                  <!-- 幻灯片全屏按钮（仅在幻灯片模式显示） -->
                  <button
                    v-if="slideMode"
                    @click="handleSlideFullscreenToggle"
                    :class="[
                      'px-4 py-2 text-sm font-medium rounded-lg transition-colors flex items-center gap-2',
                      slideFullscreen
                        ? 'bg-green-600 text-white hover:bg-green-700'
                        : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50',
                    ]"
                    title="全屏模式：使用浏览器原生全屏，隐藏所有UI"
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

                  <!-- 紧凑模式切换（仅在滚动模式显示） -->
                  <button
                    v-if="!slideMode"
                    @click="compactMode = !compactMode"
                    :class="[
                      'px-4 py-2 text-sm font-medium rounded-lg transition-colors flex items-center gap-2',
                      compactMode
                        ? 'bg-purple-600 text-white hover:bg-purple-700'
                        : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50',
                    ]"
                    title="紧凑模式：限制长内容的高度，便于浏览教案结构"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M4 6h16M4 12h16M4 18h16"
                      />
                    </svg>
                    {{ compactMode ? '展开模式' : '紧凑模式' }}
                  </button>

                  <!-- 退出全屏按钮 -->
                  <button
                    @click="toggleFullscreenPreview"
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
              @mousemove="handleSlideMouseMove"
              @touchstart="handleSlideMouseMove"
              @mouseleave="handleSlideMouseLeave"
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

              <!-- 全屏模式下的浮动控制按钮（自动隐藏） -->
              <Transition name="controls-fade">
                <div
                  v-if="slideFullscreen && displayCells.length > 0 && showSlideControls"
                  class="fixed bottom-8 right-8 z-[9999] flex items-center gap-4 flex-shrink-0"
                  style="height: auto !important; width: auto !important; pointer-events: auto"
                  @mouseenter="handleControlsMouseEnter"
                  @mouseleave="handleControlsMouseLeave"
                >
                  <!-- 上一页按钮 -->
                  <button
                    @click="goToPreviousSlide"
                    :disabled="currentSlideIndex === 0"
                    :class="[
                      'w-10 h-10 rounded-full flex items-center justify-center transition-all shadow-md touch-manipulation',
                      currentSlideIndex === 0
                        ? 'bg-gray-100 bg-opacity-80 text-gray-400 cursor-not-allowed'
                        : 'bg-white bg-opacity-90 hover:bg-opacity-100 text-gray-700 hover:shadow-lg border border-gray-300 active:scale-95',
                    ]"
                    title="上一页 (←)"
                  >
                    <svg
                      class="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      stroke-width="2.5"
                    >
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
                    @click="goToNextSlide"
                    :disabled="currentSlideIndex >= displayCells.length - 1"
                    :class="[
                      'w-10 h-10 rounded-full flex items-center justify-center transition-all shadow-md touch-manipulation',
                      currentSlideIndex >= displayCells.length - 1
                        ? 'bg-gray-100 bg-opacity-80 text-gray-400 cursor-not-allowed'
                        : 'bg-white bg-opacity-90 hover:bg-opacity-100 text-gray-700 hover:shadow-lg border border-gray-300 active:scale-95',
                    ]"
                    title="下一页 (→)"
                  >
                    <svg
                      class="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      stroke-width="2.5"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
                    </svg>
                  </button>

                  <!-- 退出全屏按钮 -->
                  <button
                    @click="handleSlideFullscreenToggle"
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
          </div>

          <!-- 底部导航栏（仅幻灯片模式显示，全屏模式下隐藏） -->
          <div
            v-if="slideMode && displayCells.length > 0 && !slideFullscreen"
            class="bg-white border-t border-gray-200 flex-shrink-0 py-5 px-4"
          >
            <div class="flex items-center justify-center gap-8 max-w-4xl mx-auto">
              <!-- 上一页按钮 -->
              <button
                @click="goToPreviousSlide"
                :disabled="currentSlideIndex === 0"
                :class="[
                  'w-16 h-16 rounded-full flex items-center justify-center transition-all shadow-lg touch-manipulation',
                  currentSlideIndex === 0
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-white text-gray-700 hover:bg-gray-50 hover:shadow-xl border-2 border-gray-300 active:scale-90',
                ]"
                title="上一页 (←)"
              >
                <svg
                  class="w-7 h-7"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  stroke-width="2.5"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
                </svg>
              </button>

              <!-- 页码显示 -->
              <div
                class="px-8 py-3 bg-gray-50 rounded-full border-2 border-gray-200 min-w-[120px] text-center"
              >
                <span class="text-xl font-bold text-gray-800">
                  {{ currentSlideIndex + 1 }} / {{ cells.length }}
                </span>
              </div>

              <!-- 下一页按钮 -->
              <button
                @click="goToNextSlide"
                :disabled="currentSlideIndex >= cells.length - 1"
                :class="[
                  'w-16 h-16 rounded-full flex items-center justify-center transition-all shadow-lg touch-manipulation',
                  currentSlideIndex >= cells.length - 1
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-white text-gray-700 hover:bg-gray-50 hover:shadow-xl border-2 border-gray-300 active:scale-90',
                ]"
                title="下一页 (→)"
              >
                <svg
                  class="w-7 h-7"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  stroke-width="2.5"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>

          <!-- 滚动模式的浮动操作按钮 -->
          <div v-if="!slideMode" class="fixed bottom-8 right-8 flex flex-col gap-3">
            <!-- 返回顶部 -->
            <button
              @click="scrollToTop"
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
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick, provide } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useLessonStore } from '../../store/lesson'
import { lessonService } from '../../services/lesson'
import type { Cell } from '../../types/cell'
import { CellType } from '../../types/cell'
import type { LessonRelatedMaterial } from '../../types/lesson'
import CellToolbar from '../../components/Lesson/CellToolbar.vue'
import CellContainer from '../../components/Cell/CellContainer.vue'
import AddCellMenu from '../../components/Lesson/AddCellMenu.vue'
import SectionContainer from '../../components/Lesson/SectionContainer.vue'
import { isContentWithSections } from '../../utils/lessonContent'
import ReferenceResourcePanel from '../../components/Resource/ReferenceResourcePanel.vue'
import PDFViewerModal from '../../components/Resource/PDFViewerModal.vue'
import ClassroomSelectorModal from '../../components/Lesson/ClassroomSelectorModal.vue'
import LessonAiAssistantDrawer from '@/components/Teacher/LessonAiAssistantDrawer.vue'
import TeacherClassroomControlPanel from '@/components/Classroom/TeacherControlPanel.vue'
import TeachingAssistantFAB from '@/components/Teacher/TeachingAssistantFAB.vue'
import TeachingAssistantDrawer from '@/components/Teacher/TeachingAssistantDrawer.vue'
import { useLessonEditorSections } from '@/composables/useLessonEditorSections'
import { useLessonEditorCells, getDefaultCell } from '@/composables/useLessonEditorCells'
import { useLessonEditorSave } from '@/composables/useLessonEditorSave'
import { useLessonEditorSession } from '@/composables/useLessonEditorSession'
import { useLessonEditorNav } from '@/composables/useLessonEditorNav'
import { useLessonEditorSlides } from '@/composables/useLessonEditorSlides'
import { useLessonEditorCover } from '@/composables/useLessonEditorCover'
import { useLessonEditorPublish } from '@/composables/useLessonEditorPublish'
import { useFullscreen } from '@/composables/useFullscreen'
import { summarizeCell, markdownToHtml } from '@/utils/lessonEditorHelpers'
import api from '../../services/api'
import courseExportService from '../../services/courseExport'
import { useToast } from '@/composables/useToast'
import { getServerBaseUrl } from '@/utils/url'
import { createLogger } from '../../utils/logger'

const logger = createLogger('LESSON_EDITOR')

// 配置 dayjs
dayjs.extend(relativeTime)
dayjs.locale('zh-cn')


const router = useRouter()
const route = useRoute()
const lessonStore = useLessonStore()

// 模板 refs
const cellListRef = ref<HTMLElement>()
const tabsContainerRef = ref<HTMLElement>()
const slideContainerRef = ref<HTMLElement>()
const teacherControlPanelRef = ref<InstanceType<typeof TeacherClassroomControlPanel> | null>(null)
// 本地状态
const isLoading = ref(true)
const loadError = ref<string | null>(null)
const toolbarCollapsed = ref(false)
const isPreviewMode = ref(false)
const compactMode = ref(true)
const lessonTitle = ref('')
const isFlowInteractionActive = ref(false)
let flowInteractionResumeTimer: ReturnType<typeof setTimeout> | null = null
const referenceResource = ref<any>(null)
const showReferencePanel = ref(true)
const showPDFViewer = ref(false)
const showLessonAssistant = ref(false)
const showClassroomPanel = ref(false)
const showAssistantDrawer = ref(false)
// Toast
const toast = ref({ show: false, type: 'success' as 'success' | 'error' | 'warning', message: '' })
function showToast(type: 'success' | 'error' | 'warning', message: string) {
  toast.value = { show: true, type, message }
  setTimeout(() => { toast.value.show = false }, 3000)
}
// Composables: Sections, Cells, Save, Session, Nav
const { sections, activeSectionIndex, editingTabId, editingTabNameRef, handleSectionUpdate, handleSectionDelete, handleAddSection: _handleAddSection, handleTabDblClick, initTabsSortable, destroySortable } = useLessonEditorSections(tabsContainerRef)
const handleAddSection = () => _handleAddSection(showToast)
function initSortable() { /* 大环节模式下由 SectionContainer 负责，cell 级 Sortable 已禁用 */ }
const { createReferenceMaterialCell, scrollToNewCell, handleAddCellToEnd, handleAddCellInSection, handleAddCellAt, insertReferenceMaterial, handleCellUpdate, handleDeleteCell, handleMoveUp, handleMoveDown } = useLessonEditorCells(sections, activeSectionIndex, cellListRef, showToast)
const { saveStatus, lastSavedAt, hasUnsavedChanges, isSavingOnUnmount, handleManualSave, handleBack, formatSaveTime, saveOnUnmount } = useLessonEditorSave(sections, lessonTitle, isPreviewMode, showToast)
const { currentSessionId, providedSessionRef, providedSessionId, handleSessionChanged } = useLessonEditorSession(teacherControlPanelRef, isPreviewMode, showClassroomPanel)
const { isFullscreenPreview, toggleFullscreenPreview, handleTogglePreviewMode, handleExportLesson, exporting } = useLessonEditorNav(isPreviewMode, showToast)

// 从 TeacherControlPanel 获取导播台数据
const classroomPanelData = computed(() => {
  if (!isPreviewMode.value || !teacherControlPanelRef.value) {
    return null
  }
  const panel = teacherControlPanelRef.value as any
  return {
    session: panel.session?.value,
    activeStudents: panel.activeStudents?.value || [],
    totalStudents: panel.totalStudents?.value || 0,
    displayDuration: panel.displayDuration?.value || 0,
    remainingTime: panel.remainingTime?.value || 0,
    formatDuration: panel.formatDuration,
    formatRemainingTime: panel.formatRemainingTime,
    handleToggleDisplayMode: panel.handleToggleDisplayMode,
    handlePause: panel.handlePause,
    handleEnd: panel.handleEnd,
  }
})

// cells, displayCells, Slides, Cover, Publish, currentLesson
const cells = computed(() => lessonStore.cells)

// 🔧 处理 TeacherControlPanel 的 session 变化事件
function handleSessionChanged(session: any | null) {
  logger.debug("LessonEditor: 收到 session-changed 事件", {
    sessionId: session?.id,
    status: session?.status,
    timestamp: new Date().toLocaleTimeString(),
  })

  if (session?.id) {
    currentSessionId.value = session.id
    providedSessionRef.value = session
    console.log('✅ LessonEditor: 已更新 currentSessionId 和 providedSessionRef', {
      sessionId: session.id,
      timestamp: new Date().toLocaleTimeString(),
    })
  } else {
    currentSessionId.value = undefined
    providedSessionRef.value = null
    logger.debug("LessonEditor: session 已清除")
  }
}

const filteredCells = computed(() => {
  if (!cells.value?.length) return []
  if (!isPreviewMode.value) return cells.value
  const session = providedSessionRef.value
  if (session?.settings?.display_cell_orders) {
    const orders = session.settings.display_cell_orders
    if (orders.length === 0) return []
    return cells.value.filter((c, i) => orders.includes(c.order !== undefined ? c.order : i))
  }
  return cells.value
})
const displayCells = computed(() => (isPreviewMode.value ? filteredCells.value : cells.value))
const { slideMode, currentSlideIndex, slideFullscreen, showSlideControls, currentCell, isSlideNativeFullscreen, toggleSlideFullscreen, goToPreviousSlide, goToNextSlide, goToSlide, scrollToTop, handleSlideMouseMove, handleSlideMouseLeave, handleControlsMouseEnter, handleControlsMouseLeave, resetControlsTimer, clearControlsTimer, handleSlideKeydown } = useLessonEditorSlides(slideContainerRef, displayCells, isFullscreenPreview)
const { coverImageInput, isUploadingCoverImage, showCoverImagePreview, coverImagePreviewUrl, coverImagePreviewFile, coverImagePreview, imageQuality, maxImageWidth, maxImageHeight, coverImageLoadError, coverImageUrl, triggerCoverImageUpload, handleCoverImageSelect, cancelCoverImageEdit, processAndUploadCoverImage } = useLessonEditorCover(showToast)
const { showPublishModal, selectedClassroomIds, publishError, publishModalError, handlePublish, handlePublishConfirm, handlePublishCancel } = useLessonEditorPublish(showToast)
const currentLesson = computed(() => lessonStore.currentLesson)

provide('classroomSession', providedSessionRef)
provide('classroomSessionId', providedSessionId)
provide(
  'currentLessonId',
  computed(() => currentLesson.value?.id)
)

// 判断是否可以进入授课模式（只有已发布的教案才能进入授课模式）
const canEnterPreviewMode = computed(() => {
  return currentLesson.value?.status === 'published'
})

// 获取当前班级ID（用于教学助手）
const currentClassroomId = computed(() => {
  // 优先从 lesson 的 classroom_ids 中获取第一个
  if (currentLesson.value?.classroom_ids && currentLesson.value.classroom_ids.length > 0) {
    return currentLesson.value.classroom_ids[0]
  }
  // 如果 session 中有 classroom_id，也可以使用
  // 这里暂时返回 null，后续可以根据实际需求扩展
  return null
})

// 处理打开教学助手抽屉
function handleOpenAssistantDrawer(type: 'attendance' | 'behavior' | 'discipline' | 'duty') {
  showAssistantDrawer.value = true
}

// 调试：输出课堂控制按钮的显示条件
watch([isPreviewMode, () => currentLesson.value?.status], ([preview, status]) => {
  if (preview) {
    logger.debug("课堂控制按钮显示条件:", {
      isPreviewMode: preview,
      lessonStatus: status,
      shouldShow: preview && status === 'published'
    })
  }
}, { immediate: true })

const isSaving = computed(() => lessonStore.isSaving)
const availableClassrooms = computed(() => lessonStore.availableClassrooms)
const isLoadingClassrooms = computed(() => lessonStore.isLoadingClassrooms)
const classroomsError = computed(() => lessonStore.classroomsError)

const lessonOutline = computed(() => {
  const list = cells.value || []
  if (list.length === 0) return ''
  const items = list
    .slice(0, 6)
    .map((cell, index) => summarizeCell(cell as Cell, index))
    .filter((item): item is string => Boolean(item))
  return items.join('\n')
})

// 标记是否最近从未发布状态切换的
const isRecentlyUnpublished = ref(false)


// 处理课堂控制按钮点击
function handleClassroomButtonClick() {
  if (!isPreviewMode.value) {
    // 如果不在预览模式，自动切换到预览模式并打开课堂控制面板
    isPreviewMode.value = true
    showClassroomPanel.value = true
    showToast('success', '已进入预览模式，课堂控制面板已打开')
    return
  }
  showClassroomPanel.value = !showClassroomPanel.value
}

// 切换幻灯片全屏（使用浏览器原生全屏API）
async function handleSlideFullscreenToggle() {
  try {
    await toggleSlideFullscreen()
  } catch (error) {
    console.error('切换幻灯片全屏失败:', error)
  }
}

// 监听预览模式变化
watch(isPreviewMode, (newValue) => {
  if (newValue) {
    destroySortable()
    // 进入授课模式时，自动打开课堂控制面板
    if (currentLesson.value?.status === 'published') {
      showClassroomPanel.value = true
    }
  } else {
    nextTick(() => {
      setTimeout(initSortable, 100)
      setTimeout(initTabsSortable, 100)
    })
  }
})

// 监听 cells 变化，重新初始化拖拽（当 cells 数量变化时）
watch(
  () => cells.value.length,
  () => {
    if (!isPreviewMode.value && cellListRef.value) {
      nextTick(() => {
        destroySortable()
        setTimeout(initSortable, 100)
        setTimeout(initTabsSortable, 100)
      })
    }
  }
)

// 监听全屏预览模式，添加键盘快捷键
watch(isFullscreenPreview, (newValue) => {
  if (newValue) {
    // 添加键盘事件监听
    document.addEventListener('keydown', handleFullscreenKeydown)
  } else {
    // 移除键盘事件监听
    document.removeEventListener('keydown', handleFullscreenKeydown)
  }
})

// 监听幻灯片模式切换，重置索引
watch(slideMode, (newValue) => {
  if (newValue && isFullscreenPreview.value) {
    // 切换到幻灯片模式时，重置到第一页
    currentSlideIndex.value = 0
    // 退出全屏模式
    slideFullscreen.value = false
  }
})

// 监听原生全屏状态变化，同步到slideFullscreen
watch(isSlideNativeFullscreen, (newValue) => {
  slideFullscreen.value = newValue
  if (newValue) {
    // 进入全屏时，显示控制按钮
    showSlideControls.value = true
    resetControlsTimer()
  } else {
    // 退出全屏时，清除定时器
    clearControlsTimer()
  }
})

// 监听全屏模式切换，重置控制按钮显示状态
watch(slideFullscreen, (newValue) => {
  if (newValue) {
    // 进入全屏时，显示控制按钮
    showSlideControls.value = true
    resetControlsTimer()
  } else {
    // 退出全屏时，清除定时器
    clearControlsTimer()
  }
})

// 监听cells变化，确保索引有效（useLessonEditorSlides 内部也有类似逻辑）
watch(
  () => cells.value.length,
  (newLength) => {
    if (slideMode.value && currentSlideIndex.value >= newLength) {
      currentSlideIndex.value = Math.max(0, newLength - 1)
    }
  }
)

// 处理全屏预览的键盘事件
function handleFullscreenKeydown(event: KeyboardEvent) {
  if (handleSlideKeydown(event)) return
  if (event.key === 'Escape' && isFullscreenPreview.value) toggleFullscreenPreview()
}

function handleFlowInteractionStartEvent() {
  if (flowInteractionResumeTimer) {
    clearTimeout(flowInteractionResumeTimer)
    flowInteractionResumeTimer = null
  }
  isFlowInteractionActive.value = true
}

function handleFlowInteractionEndEvent() {
  if (flowInteractionResumeTimer) {
    clearTimeout(flowInteractionResumeTimer)
  }
  flowInteractionResumeTimer = setTimeout(() => {
    isFlowInteractionActive.value = false
    flowInteractionResumeTimer = null
  }, 500)
}

// 监听标题变化
watch(
  () => currentLesson.value?.title,
  (newTitle) => {
    if (newTitle !== undefined) {
      lessonTitle.value = newTitle
    }
  }
)

// MVP: 处理参考笔记更新
function handleNotesUpdated(notes: string) {
  if (currentLesson.value) {
    currentLesson.value.reference_notes = notes
  }
}

function handleAiInsert(content: string) {
  if (!currentLesson.value) return
  const html = markdownToHtml(content)
  if (!html) {
    showToast('error', 'AI 返回内容为空，插入失败')
    return
  }
  const teaching = sections.value.find((s) => s.order === 1)
  if (!teaching) return
  if (!teaching.cells) teaching.cells = []
  const idx = teaching.cells.length
  const newCell = getDefaultCell(CellType.TEXT, idx)
  ;(newCell.content as any).html = html
  teaching.cells.push(newCell)
  showToast('success', 'AI 建议已插入到教案末尾')
  const globalIndex = sections.value.reduce((a, s) => a + (s.cells?.length || 0), 0) - 1
  nextTick(() => scrollToNewCell(globalIndex))
}

// 页面加载
onMounted(async () => {
  // 添加页面卸载和可见性变化监听
  window.addEventListener('beforeunload', handleBeforeUnload)
  document.addEventListener('visibilitychange', handleVisibilityChange)

  window.addEventListener('flowchart-interaction-start', handleFlowInteractionStartEvent)
  window.addEventListener('flowchart-interaction-end', handleFlowInteractionEndEvent)

  const lessonId = Number(route.params.id)

  if (!lessonId || isNaN(lessonId)) {
    loadError.value = '无效的教案 ID'
    isLoading.value = false
    return
  }

  try {
    // 检查是否存在已发布教案的状态标记
    const wasPublished = sessionStorage.getItem(`lesson_${lessonId}_was_published`)

    await lessonStore.loadLesson(lessonId)
    lessonTitle.value = currentLesson.value?.title || ''

    const consumeQueue =
      typeof lessonStore.consumeReferenceQueue === 'function'
        ? lessonStore.consumeReferenceQueue
        : () => {
            const pending = lessonStore.pendingReferenceMaterials
            const items = Array.isArray((pending as any)?.value) ? [...(pending as any).value] : []
            if ((pending as any)?.value) {
              (pending as any).value = []
            }
            return items as LessonRelatedMaterial[]
          }

    const pendingMaterials = consumeQueue()
    if (pendingMaterials.length > 0 && currentLesson.value) {
      const insertedIndices: number[] = []
      let skippedCount = 0

      pendingMaterials.forEach((material) => {
        if (!material.is_accessible) {
          skippedCount += 1
          return
        }
        const index = insertReferenceMaterial(material)
        if (index !== null) {
          insertedIndices.push(index)
        }
      })

      const c = currentLesson.value.content
      if (Array.isArray(c)) {
        c.forEach((cell, idx) => {
          cell.order = idx
        })
      } else if (isContentWithSections(c)) {
        let i = 0
        for (const sec of c.sections || []) {
          for (const cell of sec.cells || []) {
            cell.order = i++
          }
        }
      }

      if (insertedIndices.length > 0) {
        await nextTick()
        scrollToNewCell(insertedIndices[0])
      }

      if (insertedIndices.length > 0 || skippedCount > 0) {
        const parts: string[] = []
        if (insertedIndices.length > 0) {
          parts.push(`已插入 ${insertedIndices.length} 个参考素材`)
        }
        if (skippedCount > 0) {
          parts.push(`${skippedCount} 个素材因权限限制未能插入`)
        }
        showToast(insertedIndices.length > 0 ? 'success' : 'error', parts.join('，'))
      }
    }

    // 如果这个教案刚刚从未发布状态切换，显示提示
    if (wasPublished && currentLesson.value?.status === 'draft') {
      isRecentlyUnpublished.value = true
      sessionStorage.removeItem(`lesson_${lessonId}_was_published`)
      // 5秒后隐藏提示
      setTimeout(() => {
        isRecentlyUnpublished.value = false
      }, 5000)
    }

    // MVP: 加载参考资源
    if (currentLesson.value?.reference_resource_id) {
      try {
        const { lessonService } = await import('../../services/lesson')
        referenceResource.value = await lessonService.getReferenceResource(lessonId)
      } catch (error) {
        console.error('Failed to load reference resource:', error)
      }
    }

    // 初始化拖拽
    setTimeout(initSortable, 100)
    setTimeout(initTabsSortable, 100)
  } catch (error: any) {
    loadError.value = error.message || '加载教案失败'
  } finally {
    isLoading.value = false
  }
})

// 页面卸载前提示用户
const handleBeforeUnload = (event: BeforeUnloadEvent) => {
  if (hasUnsavedChanges.value && currentLesson.value && !isPreviewMode.value) {
    // 提示用户有未保存的更改
    // 注意：现代浏览器会忽略自定义消息，只显示默认提示
    event.preventDefault()
    event.returnValue = ''
    return event.returnValue
  }
}

// 页面可见性变化时（切换标签页、最小化窗口等）
// 已删除自动保存，避免并发保存导致数据覆盖
// 用户需要手动点击保存按钮
const handleVisibilityChange = async () => {
  // 不再自动保存，避免并发保存导致数据覆盖
  // 用户需要手动点击保存按钮
}

// 组件卸载
onUnmounted(async () => {
  await saveOnUnmount()

  // 移除事件监听
  window.removeEventListener('beforeunload', handleBeforeUnload)
  document.removeEventListener('visibilitychange', handleVisibilityChange)

  destroySortable()
  // 确保恢复body滚动
  document.body.style.overflow = ''
  // 移除键盘事件监听
  document.removeEventListener('keydown', handleFullscreenKeydown)
  window.removeEventListener('flowchart-interaction-start', handleFlowInteractionStartEvent)
  window.removeEventListener('flowchart-interaction-end', handleFlowInteractionEndEvent)
  if (flowInteractionResumeTimer) {
    clearTimeout(flowInteractionResumeTimer)
    flowInteractionResumeTimer = null
  }
  // 清除控制按钮定时器
  clearControlsTimer()
})
</script>

<style scoped>
.toast-slide-enter-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.toast-slide-leave-active {
  transition: all 0.3s ease-in;
}

.toast-slide-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

.toast-slide-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

/* 添加脉冲动画效果 */
@keyframes pulse-success {
  0% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(34, 197, 94, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
  }
}

.toast-slide-enter-active .rounded-lg {
  animation: pulse-success 0.6s ease-out;
}

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

/* 拖拽相关样式 */
.sortable-ghost {
  opacity: 0.5;
  background: #eff6ff;
  border: 2px dashed #3b82f6;
}

.sortable-chosen {
  transform: scale(1.02);
  box-shadow:
    0 10px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.sortable-drag {
  opacity: 0.75;
}

/* 拖拽手柄悬停效果 */
.drag-handle:hover {
  transform: scale(1.1);
}

/* 可拖拽区域样式 */
.cell-drag-area {
  user-select: none;
  -webkit-user-select: none;
}

.cell-drag-area:hover {
  background-color: rgba(59, 130, 246, 0.05);
  border-radius: 0.375rem;
  transition: background-color 0.2s;
}

/* 隐藏滚动条 */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
