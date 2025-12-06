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
              class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
              title="返回"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
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
            <template v-if="isPreviewMode && classroomPanelData?.session && classroomPanelData.session.status === 'active'">
              <div class="flex items-center gap-2.5 text-xs border-r border-gray-200 pr-3 mr-3">
                <!-- 课程标题 -->
                <div class="text-gray-800 font-semibold max-w-xs truncate">
                  {{ currentLesson?.title }}
                </div>
                <!-- 学生人数 -->
                <div class="flex items-center gap-1 px-2 py-0.5 bg-blue-50 rounded text-blue-700">
                  <span>👥</span>
                  <span class="font-medium">{{ classroomPanelData.activeStudents.length }}</span>
                  <span v-if="classroomPanelData.totalStudents > 0" class="text-blue-500">/{{ classroomPanelData.totalStudents }}</span>
                  <span class="text-blue-600">人已进入</span>
                </div>
                <!-- 模块数量 -->
                <div v-if="currentLesson?.content" class="flex items-center gap-1 px-2 py-0.5 bg-purple-50 rounded text-purple-700">
                  <span>📚</span>
                  <span class="font-medium">{{ currentLesson.content.length }}</span>
                  <span class="text-purple-600">个模块</span>
                </div>
                <!-- 时长 -->
                <div class="flex items-center gap-1 px-2 py-0.5 bg-emerald-50 rounded text-emerald-700">
                  <span>⏱️</span>
                  <span class="font-medium">{{ classroomPanelData.formatDuration?.(classroomPanelData.displayDuration) || '0分钟' }}</span>
                  <span v-if="classroomPanelData.remainingTime > 0" class="text-emerald-600">
                    剩余: {{ classroomPanelData.formatRemainingTime?.(classroomPanelData.remainingTime) || '' }}
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
            
            <!-- 保存状态指示器 -->
            <div class="flex items-center gap-2 text-sm">
              <span v-if="saveStatus === 'saving'" class="text-gray-500 flex items-center gap-1">
                <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                保存中...
              </span>
              <span v-else-if="saveStatus === 'saved'" class="text-green-600 flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                已保存
              </span>
              <span v-else-if="saveStatus === 'error'" class="text-red-600 flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                保存失败
              </span>
              <span v-else-if="lastSavedAt" class="text-gray-500">
                {{ formatSaveTime(lastSavedAt) }}
              </span>
            </div>

            <!-- 教案状态提示 -->
            <div v-if="isRecentlyUnpublished" class="flex items-center gap-2 px-3 py-1.5 text-sm text-amber-600 bg-amber-50 rounded-md">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              已从已发布状态切换为草稿
            </div>

            <!-- AI 助手 -->
            <button
              type="button"
              @click="showLessonAssistant = true"
              class="inline-flex items-center gap-2 rounded-md bg-gradient-to-r from-[#4C6EF5] to-[#6C8DFF] px-3 py-1.5 text-sm font-medium text-white shadow hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-[#BFD0FF]"
            >
              <svg class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10 2a6 6 0 00-6 6v1.586l-.707.707A1 1 0 004 12h1v1a4 4 0 004 4v1h2v-1a4 4 0 004-4v-1h1a1 1 0 00.707-1.707L16 9.586V8a6 6 0 00-6-6z" />
              </svg>
              AI 助手
            </button>

            <!-- 手动保存按钮 -->
            <button
              @click="handleManualSave"
              :disabled="saveStatus === 'saving'"
              :class="[
                'px-3 py-1.5 text-sm font-medium rounded-md disabled:opacity-50',
                isPreviewMode
                  ? 'text-amber-700 bg-amber-50 border border-amber-300 hover:bg-amber-100'
                  : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
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

            <!-- 课堂模式按钮 -->
            <!-- 课堂控制按钮已隐藏，进入授课模式时自动显示课堂控制面板 -->

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
              <svg class="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
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
              :title="!canEnterPreviewMode && !isPreviewMode ? '需要先发布教案才能进入授课模式' : ''"
            >
              {{ isPreviewMode ? '编辑模式' : '授课模式' }}
            </button>

            <!-- 全屏预览按钮 -->
            <button
              @click="toggleFullscreenPreview"
              class="px-3 py-1.5 text-sm font-medium rounded-md bg-purple-600 text-white hover:bg-purple-700 flex items-center gap-2"
              title="全屏预览"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              全屏预览
            </button>
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
        <div 
          :class="[
            isPreviewMode ? 'w-full py-4 px-2' : 'w-full py-6 px-4 sm:px-6 lg:px-8'
          ]"
        >
          <!-- 加载状态 -->
          <div v-if="isLoading" class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p class="mt-4 text-gray-600">加载教案中...</p>
          </div>

          <!-- 错误状态 -->
          <div v-else-if="loadError" class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <svg class="mx-auto h-12 w-12 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
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
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 class="mt-4 text-lg font-medium text-gray-900">开始创建教案内容</h3>
              <p class="mt-2 text-sm text-gray-600">从左侧工具栏选择要添加的单元类型</p>
            </div>

            <!-- Cell 列表容器 -->
            <div ref="cellListRef" :class="isPreviewMode ? 'space-y-2' : 'space-y-4'">
              <template v-for="(cell, index) in displayCells" :key="cell.id">
                <!-- 顶部添加按钮（第一个 Cell 前） -->
                <div v-if="index === 0 && !isPreviewMode" class="add-cell-menu-container">
                  <AddCellMenu
                    :insert-index="0"
                    @add="handleAddCellAt"
                  />
                </div>

                <!-- Cell 容器 -->
                <!-- sessionId 和 lessonId 通过 provide/inject 传递，不需要 props -->
                <CellContainer
                  :cell="cell"
                  :index="index"
                  :editable="!isPreviewMode"
                  :draggable="!isPreviewMode"
                  :show-move-buttons="!isPreviewMode"
                  :compact-mode="compactMode && !isPreviewMode"
                  :lesson-id="currentLesson?.id"
                  @update="handleCellUpdate"
                  @delete="handleDeleteCell"
                  @move-up="handleMoveUp"
                  @move-down="handleMoveDown"
                />
                <!-- 调试信息 -->

                <!-- Cell 之间的添加按钮 -->
                <div v-if="!isPreviewMode" class="add-cell-menu-container">
                  <AddCellMenu
                    :insert-index="index + 1"
                    @add="handleAddCellAt"
                  />
                </div>
              </template>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Toast 提示 -->
    <Transition name="toast-slide">
      <div
        v-if="toast.show"
        class="fixed top-4 right-4 z-50 max-w-sm"
      >
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
                      : 'bg-red-100'
                ]"
              >
                <svg
                  v-if="toast.type === 'success'"
                  class="h-4 w-4 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <svg
                  v-else-if="toast.type === 'warning'"
                  class="h-4 w-4 text-amber-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <svg
                  v-else
                  class="h-4 w-4 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
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
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
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
    <PDFViewerModal
      v-model="showPDFViewer"
      :resource-id="referenceResource?.id || null"
    />

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
                    <p class="text-sm text-gray-500 mt-1">{{ slideMode ? '幻灯片模式' : '沉浸式预览' }}</p>
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
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
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
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
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
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                    </svg>
                    {{ compactMode ? '展开模式' : '紧凑模式' }}
                  </button>
                  
                  <!-- 退出全屏按钮 -->
                  <button
                    @click="toggleFullscreenPreview"
                    class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
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
                    :index="index"
                    :editable="false"
                    :draggable="false"
                    :show-move-buttons="false"
                    :compact-mode="compactMode"
                  />
                </div>

                <!-- 空状态 -->
                <div v-else class="text-center py-12">
                  <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
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
                'overflow-y-auto': !slideFullscreen
              }"
              :style="slideFullscreen ? 'overflow: hidden; position: relative;' : ''"
              @mousemove="handleSlideMouseMove"
              @touchstart="handleSlideMouseMove"
              @mouseleave="handleSlideMouseLeave"
            >
              <div class="flex justify-center relative" :class="slideFullscreen ? 'h-full p-0 overflow-y-auto' : 'p-8 items-center'">
                <Transition name="slide-fade" mode="out-in">
                  <div
                    v-if="currentCell"
                    :key="`slide-${currentCell.id}`"
                    :class="slideFullscreen ? 'w-full min-h-full flex items-start justify-center p-8' : 'w-full max-w-6xl'"
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
                  <div
                    v-else
                    key="empty-slide"
                    class="text-center py-12 w-full"
                  >
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
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
                  style="height: auto !important; width: auto !important; pointer-events: auto;"
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
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>

                <!-- 页码显示 -->
                <div class="px-4 py-1.5 bg-white bg-opacity-90 rounded-full border border-gray-300 shadow-md min-w-[80px] text-center">
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
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
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
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
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
                <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
                </svg>
              </button>

              <!-- 页码显示 -->
              <div class="px-8 py-3 bg-gray-50 rounded-full border-2 border-gray-200 min-w-[120px] text-center">
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
                <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
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
              <svg class="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
              </svg>
            </button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, watchEffect, nextTick, provide } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useLessonStore } from '../../store/lesson'
// 已删除自动保存功能，避免并发保存导致数据覆盖
// import { useAutoSave } from '../../composables/useAutoSave'
import { v4 as uuidv4 } from 'uuid'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'
import Sortable from 'sortablejs'
import type { Cell, ReferenceMaterialCell } from '../../types/cell'
import { CellType } from '../../types/cell'
import type { LessonRelatedMaterial } from '../../types/lesson'
import CellToolbar from '../../components/Lesson/CellToolbar.vue'
import CellContainer from '../../components/Cell/CellContainer.vue'
import AddCellMenu from '../../components/Lesson/AddCellMenu.vue'
import ReferenceResourcePanel from '../../components/Resource/ReferenceResourcePanel.vue'
import PDFViewerModal from '../../components/Resource/PDFViewerModal.vue'
import ClassroomSelectorModal from '../../components/Lesson/ClassroomSelectorModal.vue'
import LessonAiAssistantDrawer from '@/components/Teacher/LessonAiAssistantDrawer.vue'
import TeacherClassroomControlPanel from '@/components/Classroom/TeacherControlPanel.vue'
import { useFullscreen } from '@/composables/useFullscreen'

// 配置 dayjs
dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const router = useRouter()
const route = useRoute()
const lessonStore = useLessonStore()

// 本地状态
const isLoading = ref(true)
const loadError = ref<string | null>(null)
const toolbarCollapsed = ref(false)
const isPreviewMode = ref(false)
const compactMode = ref(true) // 紧凑模式：默认启用，限制长内容的高度
const isFullscreenPreview = ref(false)
const slideMode = ref(false) // 幻灯片模式：一页一页播放
const currentSlideIndex = ref(0) // 当前幻灯片索引
const slideFullscreen = ref(false) // 幻灯片全屏模式：隐藏顶部栏和底部栏，铺满屏幕
const showSlideControls = ref(true) // 全屏模式下控制按钮的显示状态
let slideControlsTimer: ReturnType<typeof setTimeout> | null = null
const cellListRef = ref<HTMLElement>()
const slideContainerRef = ref<HTMLElement>() // 幻灯片容器引用，用于全屏
const { isFullscreen: isSlideNativeFullscreen, toggleFullscreen: toggleSlideFullscreen } = useFullscreen(slideContainerRef)
const lessonTitle = ref('')
const isFlowInteractionActive = ref(false)
let flowInteractionResumeTimer: ReturnType<typeof setTimeout> | null = null

// MVP: 参考资源相关状态
const referenceResource = ref<any>(null)
const showReferencePanel = ref(true)
const showPDFViewer = ref(false)
const showPublishModal = ref(false)
const selectedClassroomIds = ref<number[]>([])
const publishError = ref<string | null>(null)
const showLessonAssistant = ref(false)
const showClassroomPanel = ref(false)

// 课堂会话相关
const teacherControlPanelRef = ref<InstanceType<typeof TeacherClassroomControlPanel> | null>(null)

// 从 TeacherControlPanel 获取 sessionId（使用 ref 存储，通过 watch 更新）
const currentSessionId = ref<number | undefined>(undefined)

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

// 🔧 处理 TeacherControlPanel 的 session 变化事件
function handleSessionChanged(session: any | null) {
  console.log('📨 LessonEditor: 收到 session-changed 事件', {
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
    console.log('⚠️ LessonEditor: session 已清除')
  }
}

// 监听 currentSessionId 的变化，只在真正变化时输出日志
watch(currentSessionId, (newId, oldId) => {
  if (newId !== oldId) {
    if (newId !== undefined) {
      console.log('✅ LessonEditor: sessionId 已设置:', newId)
    }
    // 从有值变为无值时不输出（这是正常情况）
  }
}, { immediate: false })

// 强制检查 sessionId 的函数（静默执行，不输出日志）
function checkSessionId() {
  if (!isPreviewMode.value || !showClassroomPanel.value || !teacherControlPanelRef.value) {
    return
  }
  
  const panel = teacherControlPanelRef.value as any
  
  // 尝试多种方式获取
  const sessionIdFromComputed = panel?.sessionId?.value
  const sessionIdFromSession = panel?.session?.value?.id
  
  const newSessionId = sessionIdFromComputed !== undefined ? sessionIdFromComputed : sessionIdFromSession
  
  if (newSessionId !== undefined && newSessionId !== currentSessionId.value) {
    currentSessionId.value = newSessionId
  }
}

// 在 onMounted 中立即检查
onMounted(() => {
  // 延迟一点，确保 TeacherControlPanel 已经挂载
  setTimeout(() => {
    checkSessionId()
    // 如果还是没有，每隔 500ms 检查一次，最多检查 10 次
    let checkCount = 0
    const intervalId = setInterval(() => {
      checkSessionId()
      checkCount++
      if (currentSessionId.value !== undefined || checkCount >= 10) {
        clearInterval(intervalId)
      }
    }, 500)
  }, 100)
})

// 监听 TeacherControlPanel 的 session 变化（使用 immediate 和 deep watch）
watch(
  () => {
    if (!isPreviewMode.value || !showClassroomPanel.value) {
      return undefined
    }
    // 尝试从 ref 获取（静默执行，不输出日志）
    if (teacherControlPanelRef.value) {
      const panel = teacherControlPanelRef.value as any
      
      // 优先从 sessionId computed 获取
      if (panel?.sessionId?.value !== undefined) {
        return panel.sessionId.value
      }
      // 从 session ref 获取
      if (panel?.session?.value?.id !== undefined) {
        return panel.session.value.id
      }
      // 尝试直接访问 session.value（如果是 ref）
      if (panel?.session && typeof panel.session === 'object' && 'value' in panel.session) {
        const sessionValue = (panel.session as any).value
        if (sessionValue?.id !== undefined) {
          return sessionValue.id
        }
      }
    }
    return undefined
  },
  (newSessionId) => {
    if (newSessionId !== undefined && newSessionId !== currentSessionId.value) {
      // 只在真正获取到 sessionId 时输出一次日志
      currentSessionId.value = newSessionId
    } else if (newSessionId === undefined && currentSessionId.value !== undefined) {
      // 从有值变为无值时，静默处理（这是正常情况）
      currentSessionId.value = undefined
    }
  },
  { immediate: true, deep: true }
)

// 也监听 teacherControlPanelRef 的变化（当组件挂载时）
// 🔧 修改：不要清除 sessionId，因为事件机制会处理
watch(teacherControlPanelRef, (panel) => {
  if (panel && isPreviewMode.value && showClassroomPanel.value) {
    const panelAny = panel as any
    
    const sessionId = panelAny?.sessionId?.value || panelAny?.session?.value?.id
    if (sessionId !== undefined && sessionId !== currentSessionId.value) {
      // 只有在能获取到 sessionId 时才更新，不要清除
      currentSessionId.value = sessionId
    }
    // 🔧 移除 else 分支，不要清除 sessionId（事件机制会处理）
  }
  // 🔧 移除 else if (!panel) 分支，不要清除 sessionId
}, { immediate: true, deep: true })

// 使用 ref 存储 session，通过 watch 监听变化并更新
const providedSessionRef = ref<any>(null)

// 也监听 session 对象本身的变化，使用 watch 确保能捕获异步加载
const panelSession = computed(() => {
  if (!teacherControlPanelRef.value) {
    return null
  }
  const panel = teacherControlPanelRef.value as any
  const sessionRef = panel?.session
  const sessionValue = sessionRef?.value || null
  
  // 添加调试日志，验证 computed 是否被触发
  if (sessionValue?.id) {
    console.log('🔍 LessonEditor: panelSession computed 被访问，sessionId =', sessionValue.id)
  }
  
  return sessionValue
})

// 用 watch 监听 panelSession 的变化，更新 providedSessionRef
// 🔧 修改：不要清除 providedSessionRef，因为事件机制会处理
watch(panelSession, (sessionValue) => {
  if (sessionValue?.id) {
    console.log('✅ LessonEditor: panelSession 变化，session 已加载:', {
      id: sessionValue.id,
      status: sessionValue.status,
    })
    providedSessionRef.value = sessionValue
  }
  // 🔧 移除 else 分支，不要清除 providedSessionRef（事件机制会处理）
}, { immediate: true, deep: true })

// 🔧 移除通过 ref 访问的 watch，只保留事件机制
// 因为通过 defineExpose 暴露的 ref 无法被 Vue 的响应式系统追踪
// 事件机制已经能正常工作，不需要这些 watch

// 额外的轮询检查（作为备用方案，确保能获取到 sessionId）
let sessionIdCheckInterval: ReturnType<typeof setInterval> | null = null
watch([isPreviewMode, showClassroomPanel, teacherControlPanelRef], ([preview, showPanel, panel]) => {
  if (preview && showPanel && panel && !sessionIdCheckInterval) {
    // 如果 currentSessionId 是 undefined，每 500ms 检查一次（最多检查 10 次）
    let checkCount = 0
    sessionIdCheckInterval = setInterval(() => {
      if (currentSessionId.value !== undefined || checkCount >= 10) {
        if (sessionIdCheckInterval) {
          clearInterval(sessionIdCheckInterval)
          sessionIdCheckInterval = null
        }
        return
      }
      
      const panelAny = panel as any
      const sessionId = panelAny?.sessionId?.value || panelAny?.session?.value?.id
      if (sessionId !== undefined) {
        console.log('✅ LessonEditor: 通过轮询检查获取到 sessionId:', sessionId)
        currentSessionId.value = sessionId
        if (sessionIdCheckInterval) {
          clearInterval(sessionIdCheckInterval)
          sessionIdCheckInterval = null
        }
      }
      checkCount++
    }, 500)
  } else if ((!preview || !showPanel || !panel) && sessionIdCheckInterval) {
    clearInterval(sessionIdCheckInterval)
    sessionIdCheckInterval = null
  }
}, { immediate: true })

// 🔧 简化传递链路：使用 ref 存储 session，通过 watch 确保响应式更新
// 提供 session 和 sessionId 给所有子组件（包括 CellContainer, ActivityCell 等）

// 创建一个更可靠的 sessionId computed，直接从 TeacherControlPanel 获取
const providedSessionId = computed(() => {
  // 优先级1: 从 providedSessionRef 获取
  if (providedSessionRef.value?.id !== undefined) {
    return providedSessionRef.value.id
  }
  
  // 优先级2: 直接从 TeacherControlPanel 获取 sessionId
  if (teacherControlPanelRef.value) {
    const panel = teacherControlPanelRef.value as any
    const sessionIdFromComputed = panel?.sessionId?.value
    if (sessionIdFromComputed !== undefined) {
      return sessionIdFromComputed
    }
    
    // 优先级3: 从 session.value.id 获取
    const sessionIdFromSession = panel?.session?.value?.id
    if (sessionIdFromSession !== undefined) {
      return sessionIdFromSession
    }
  }
  
  // 优先级4: 使用 currentSessionId（作为最后的后备）
  return currentSessionId.value
})

// 监听 providedSessionId 的变化，输出调试信息
watch(providedSessionId, (newId, oldId) => {
  if (newId !== oldId) {
    if (newId !== undefined) {
      console.log('✅ LessonEditor: providedSessionId 已更新:', newId, {
        source: providedSessionRef.value?.id !== undefined ? 'providedSessionRef' :
                teacherControlPanelRef.value ? 'teacherControlPanel' : 'currentSessionId',
        timestamp: new Date().toLocaleTimeString(),
      })
    } else {
      console.warn('⚠️ LessonEditor: providedSessionId 为 undefined', {
        providedSessionRefValue: providedSessionRef.value,
        hasTeacherPanel: !!teacherControlPanelRef.value,
        currentSessionId: currentSessionId.value,
        timestamp: new Date().toLocaleTimeString(),
      })
    }
  }
}, { immediate: true })

provide('classroomSession', providedSessionRef)
provide('classroomSessionId', providedSessionId)
provide('currentLessonId', computed(() => currentLesson.value?.id))

// 保存锁，防止并发保存
const isSavingOnUnmount = ref(false)

// Toast 提示
const toast = ref({
  show: false,
  type: 'success' as 'success' | 'error' | 'warning',
  message: '',
})

// 计算属性
const currentLesson = computed(() => lessonStore.currentLesson)
const cells = computed(() => lessonStore.cells)

// 判断是否可以进入授课模式（只有已发布的教案才能进入授课模式）
const canEnterPreviewMode = computed(() => {
  return currentLesson.value?.status === 'published'
})

// 过滤Cells：在授课模式下只显示导播台选择的Cell
const filteredCells = computed(() => {
  if (!cells.value || cells.value.length === 0) return []
  
  // 如果不在授课模式，显示所有Cell
  if (!isPreviewMode.value) {
    return cells.value
  }
  
  // 授课模式：根据导播台选择的 display_cell_orders 过滤
  const session = providedSessionRef.value
  if (session?.settings?.display_cell_orders) {
    const displayOrders = session.settings.display_cell_orders
    
    // 如果 displayOrders 是空数组，返回空数组（隐藏所有Cell）
    if (displayOrders.length === 0) {
      return []
    }
    
    // 根据 order 过滤
    const filteredByOrders = cells.value.filter((cell, index) => {
      const cellOrder = cell.order !== undefined ? cell.order : index
      return displayOrders.includes(cellOrder)
    })
    
    return filteredByOrders
  }
  
  // 如果没有 display_cell_orders，显示所有Cell（兼容旧行为）
  return cells.value
})

// 显示用的Cells：在授课模式下使用过滤后的cells，否则使用所有cells
const displayCells = computed(() => {
  return isPreviewMode.value ? filteredCells.value : cells.value
})

// 幻灯片模式：当前显示的Cell
const currentCell = computed(() => {
  const cellsToUse = isPreviewMode.value ? filteredCells.value : cells.value
  if (!slideMode.value || cellsToUse.length === 0) {
    return null
  }
  const index = Math.max(0, Math.min(currentSlideIndex.value, cellsToUse.length - 1))
  return cellsToUse[index] || null
})

// 调试：输出课堂控制按钮的显示条件
watch([isPreviewMode, () => currentLesson.value?.status], ([preview, status]) => {
  if (preview) {
    console.log('🔍 课堂控制按钮显示条件:', {
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
const publishModalError = computed(
  () => publishError.value || classroomsError.value || null
)

const lessonOutline = computed(() => {
  if (!currentLesson.value || !Array.isArray(currentLesson.value.content)) {
    return ''
  }

  const items = currentLesson.value.content
    .slice(0, 6)
    .map((cell, index) => summarizeCell(cell as Cell, index))
    .filter((item): item is string => Boolean(item))

  return items.join('\n')
})

// 标记是否最近从未发布状态切换的
const isRecentlyUnpublished = ref(false)

// 手动保存功能（已删除自动保存，避免并发保存导致数据覆盖）
const saveStatus = ref<'idle' | 'saving' | 'saved' | 'error'>('idle')
const lastSavedAt = ref<Date | null>(null)

// 手动保存函数
async function manualSave() {
  if (!currentLesson.value || isPreviewMode.value) return
  
  saveStatus.value = 'saving'
  try {
    // 更新标题
    currentLesson.value.title = lessonTitle.value
    // 确保使用最新的 cells 数据
    currentLesson.value.content = [...cells.value]
    await lessonStore.saveCurrentLesson()
    saveStatus.value = 'saved'
    lastSavedAt.value = new Date()
    // 2秒后重置为 idle
    setTimeout(() => {
      if (saveStatus.value === 'saved') {
        saveStatus.value = 'idle'
      }
    }, 2000)
  } catch (error: any) {
    saveStatus.value = 'error'
    console.error('保存失败:', error)
    throw error
  }
}

// 标记是否有未保存的更改
const hasUnsavedChanges = ref(false)

// 监听教案变化，标记为有未保存更改
// 注意：在保存过程中（saveStatus === 'saving'）不触发此标记，避免保存完成后的状态更新被误判为"未保存更改"
watch(
  [() => currentLesson.value?.content, () => lessonTitle.value],
  () => {
    // 只有在非预览模式、非保存中状态下才标记为有未保存更改
    if (currentLesson.value && !isPreviewMode.value && saveStatus.value !== 'saving') {
      hasUnsavedChanges.value = true
    }
  },
  { deep: true }
)

// 监听保存状态，清除未保存标记
watch(saveStatus, (status) => {
  if (status === 'saved') {
    hasUnsavedChanges.value = false
  }
})

// 格式化保存时间
function formatSaveTime(date: Date) {
  const now = dayjs()
  const saveTime = dayjs(date)
  const diffInMinutes = now.diff(saveTime, 'minute')
  
  if (diffInMinutes < 1) {
    return '刚刚保存'
  } else if (diffInMinutes < 60) {
    return `${diffInMinutes}分钟前保存`
  } else {
    return saveTime.format('HH:mm 保存')
  }
}

// 生成默认 Cell 内容
function getDefaultCell(cellType: CellType, order: number): Cell {
  const baseCell = {
    id: uuidv4(),
    type: cellType,
    order,
    editable: true,
  }

  switch (cellType) {
    case CellType.TEXT:
      return {
        ...baseCell,
        type: CellType.TEXT,
        content: {
          html: '<p>在此输入文本内容...</p>',
        },
      } as Cell

    case CellType.CODE:
      return {
        ...baseCell,
        type: CellType.CODE,
        content: {
          code: '# 在此编写代码\nprint("Hello, World!")',
          language: 'python' as const,
        },
        config: {
          environment: 'jupyterlite' as const,
        },
      } as Cell

    case CellType.PARAM:
      return {
        ...baseCell,
        type: CellType.PARAM,
        content: {
          schema: {},
          values: {},
        },
      } as Cell

    case CellType.SIM:
      return {
        ...baseCell,
        type: CellType.SIM,
        content: {
          type: 'phet' as const,
          config: {
            width: 800,
            height: 600,
            autoplay: false,
            locale: 'zh_CN'
          },
        },
      } as Cell

    case CellType.CHART:
      return {
        ...baseCell,
        type: CellType.CHART,
        content: {
          chartType: 'bar' as const,
          data: {},
          options: {},
        },
      } as Cell

    case CellType.CONTEST:
      return {
        ...baseCell,
        type: CellType.CONTEST,
        content: {
          title: '竞赛任务',
          description: '在此输入竞赛说明...',
          rules: {},
        },
      } as Cell

    case CellType.VIDEO:
      return {
        ...baseCell,
        type: CellType.VIDEO,
        content: {
          videoUrl: '',
          title: '',
          description: '',
        },
        config: {
          autoplay: false,
          controls: true,
          loop: false,
          muted: false,
        },
      } as Cell

    case CellType.ACTIVITY:
      return {
        ...baseCell,
        type: CellType.ACTIVITY,
        content: {
          title: '新活动',
          description: '',
          activityType: 'quiz' as const,
          timing: {
            phase: 'in-class' as const,
          },
          items: [],
          grading: {
            enabled: true,
            totalPoints: 100,
            autoGrade: false,
          },
          submission: {
            allowMultiple: false,
            showFeedback: 'immediate' as const,
          },
          display: {
            showProgress: true,
          },
        },
        config: {
          allowOffline: true,
        },
      } as Cell

    case CellType.FLOWCHART:
      return {
        ...baseCell,
        type: CellType.FLOWCHART,
        content: {
          nodes: [],
          edges: [],
          style: {
            theme: 'light' as const,
            layoutDirection: 'TB' as const,
          },
        },
        config: {
          editable: true,
          showMinimap: false,
        },
      } as Cell

    case CellType.BROWSER:
      return {
        ...baseCell,
        type: CellType.BROWSER,
        content: {
          url: '',
          title: '',
          description: '',
        },
        config: {
          allowFullscreen: true,
          allowNavigation: true,
          showToolbar: false,
          height: '600px',
        },
      } as Cell

    default:
      throw new Error(`Unknown cell type: ${cellType}`)
  }
}

function createReferenceMaterialCell(
  material: LessonRelatedMaterial,
  order: number
): ReferenceMaterialCell {
  return {
    id: uuidv4(),
    type: CellType.REFERENCE_MATERIAL,
    order,
    editable: true,
    content: {
      material_id: material.id,
      title: material.title,
      summary: material.summary,
      resource_type: material.resource_type,
      source_lesson_id: material.source_lesson_id,
      source_lesson_title: material.source_lesson_title,
      preview_url: material.preview_url,
      download_url: material.download_url,
      tags: material.tags ?? [],
      updated_at: material.updated_at,
      is_accessible: material.is_accessible,
    },
  }
}

// 添加 Cell 到末尾
function handleAddCellToEnd(cellType: CellType) {
  const newCell = getDefaultCell(cellType, cells.value.length)
  lessonStore.addCell(newCell)
  showToast('success', `已添加${getCellTypeName(cellType)}`)
}

// 在指定位置添加 Cell
function handleAddCellAt(cellType: CellType, index: number) {
  const newCell = getDefaultCell(cellType, index)
  
  // 插入 Cell
  if (currentLesson.value) {
    currentLesson.value.content.splice(index, 0, newCell)
    
    // 更新后续 Cell 的 order
    currentLesson.value.content.forEach((cell, idx) => {
      cell.order = idx
    })
  }
  
  showToast('success', `已添加${getCellTypeName(cellType)}`)
  
  // 滚动到新添加的单元
  nextTick(() => {
    scrollToNewCell(index)
  })
}

function insertReferenceMaterial(material: LessonRelatedMaterial): number | null {
  if (!currentLesson.value) return null
  const index = currentLesson.value.content.length
  const newCell = createReferenceMaterialCell(material, index)
  lessonStore.addCell(newCell)
  return index
}

// 更新 Cell
function handleCellUpdate(updatedCell: Cell) {
  lessonStore.updateCell(updatedCell.id, updatedCell)
}

// 删除 Cell
function handleDeleteCell(cellId: string) {
  if (confirm('确定要删除这个单元吗？')) {
    lessonStore.deleteCell(cellId)
    showToast('success', '单元已删除')
  }
}

// 上移 Cell
function handleMoveUp(cellId: string) {
  const index = cells.value.findIndex((c) => c.id === cellId)
  if (index > 0) {
    lessonStore.reorderCells(index, index - 1)
  }
}

// 下移 Cell
function handleMoveDown(cellId: string) {
  const index = cells.value.findIndex((c) => c.id === cellId)
  if (index < cells.value.length - 1) {
    lessonStore.reorderCells(index, index + 1)
  }
}

// 切换预览模式
function handleTogglePreviewMode() {
  // 如果已经在预览模式，直接切换回编辑模式
  if (isPreviewMode.value) {
    isPreviewMode.value = false
    return
  }

  // 如果教案是草稿状态，提示用户需要先发布
  if (!canEnterPreviewMode.value) {
    showToast('warning', '需要先发布教案才能进入授课模式')
    return
  }

  // 已发布的教案可以进入授课模式
  isPreviewMode.value = true
}

// 手动保存
async function handleManualSave() {
  // 如果在预览模式下，提示切换到编辑模式
  if (isPreviewMode.value) {
    const confirmed = confirm(
      '当前处于授课模式（预览模式），无法保存教案。\n\n' +
      '是否切换到编辑模式以保存更改？\n\n' +
      '提示：切换到编辑模式后，您可以继续编辑和保存教案。'
    )
    if (confirmed) {
      // 切换到编辑模式
      isPreviewMode.value = false
      // 等待模式切换完成后再保存
      await nextTick()
      try {
        // 更新标题
        if (currentLesson.value) {
          currentLesson.value.title = lessonTitle.value
        }
        await manualSave()
        showToast('success', '已切换到编辑模式并保存成功')
      } catch (error: any) {
        showToast('error', error.message || '保存失败')
      }
    } else {
      // 用户取消，不显示提示（避免干扰）
    }
    return
  }

  // 编辑模式下正常保存
  try {
    // 确保标题已更新
    if (currentLesson.value) {
      currentLesson.value.title = lessonTitle.value
    }
    await manualSave()
    showToast('success', '保存成功')
  } catch (error: any) {
    showToast('error', error.message || '保存失败')
  }
}

// 发布教案
async function handlePublish() {
  publishError.value = null

  try {
    await lessonStore.loadAvailableClassrooms()
    const existingIds = currentLesson.value?.classroom_ids ?? []
    selectedClassroomIds.value = [...existingIds]

    if (
      selectedClassroomIds.value.length === 0 &&
      availableClassrooms.value.length === 1
    ) {
      selectedClassroomIds.value = [availableClassrooms.value[0].id]
    }

    showPublishModal.value = true
  } catch (error: any) {
    showToast('error', error.message || '获取班级列表失败')
  }
}

async function handlePublishConfirm(classroomIds: number[]) {
  if (classroomIds.length === 0) {
    publishError.value = '请选择至少一个班级'
    return
  }

  publishError.value = null

  try {
    await lessonStore.publishCurrentLesson(classroomIds)
    selectedClassroomIds.value = [...classroomIds]
    showPublishModal.value = false
    showToast('success', '教案已发布')
  } catch (error: any) {
    publishError.value = error.message || '发布失败'
  }
}

function handlePublishCancel() {
  publishError.value = null
}

// 返回
async function handleBack() {
  // 在导航前保存未保存的更改（确保数据不丢失）
  if (currentLesson.value && !isPreviewMode.value) {
    // 检查是否有实际的未保存更改（通过对比 cells 和 currentLesson.content）
    const currentCellsCount = cells.value.length
    const lessonContentCount = currentLesson.value.content?.length || 0
    
    // 只有在以下情况下才保存：
    // 1. 明确标记了有未保存的更改（hasUnsavedChanges）
    // 2. cells 数量与教案内容数量不一致（说明有添加或删除操作）
    const hasActualChanges = currentCellsCount !== lessonContentCount || hasUnsavedChanges.value
    
    if (hasActualChanges) {
      isSavingOnUnmount.value = true
      try {
        // 先保存最新的 cells 数据到本地变量，避免在保存过程中被覆盖
        const latestCells = [...cells.value]
        const latestCellsCount = latestCells.length
        
        console.log('💾 返回前保存未保存的更改...', {
          cellsCount: latestCellsCount,
          lessonContentCount: lessonContentCount,
          hasUnsavedChanges: hasUnsavedChanges.value,
          hasActualChanges: hasActualChanges
        })
        
        // 更新标题和内容
        if (currentLesson.value) {
          currentLesson.value.title = lessonTitle.value
          // 确保使用最新的 cells 数据（使用之前保存的副本，避免在保存过程中被覆盖）
          currentLesson.value.content = latestCells
        }
        
        // 强制保存，确保使用最新的数据
        const savedLesson = await lessonStore.saveCurrentLesson()
        hasUnsavedChanges.value = false
        
        console.log('✅ 返回前已保存更改', {
          savedContentLength: savedLesson.content?.length || 0,
          expectedLength: latestCellsCount,
          match: savedLesson.content?.length === latestCellsCount
        })
        
        // 等待保存完全提交
        await new Promise(resolve => setTimeout(resolve, 200))
      } catch (error) {
        console.error('❌ 返回前保存失败:', error)
        // 即使保存失败，也允许用户返回（避免阻塞）
        // 但记录错误以便调试
      } finally {
        isSavingOnUnmount.value = false
      }
    } else {
      console.log('✅ 无未保存的更改，直接返回')
    }
  }
  
  router.push('/teacher')
}

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

// 切换全屏预览
function toggleFullscreenPreview() {
  isFullscreenPreview.value = !isFullscreenPreview.value
  
  // 进入全屏时，禁止body滚动
  if (isFullscreenPreview.value) {
    document.body.style.overflow = 'hidden'
    // 进入全屏时，如果启用幻灯片模式，重置到第一页
    if (slideMode.value) {
      currentSlideIndex.value = 0
    }
  } else {
    document.body.style.overflow = ''
  }
}

// 切换幻灯片全屏（使用浏览器原生全屏API）
async function handleSlideFullscreenToggle() {
  try {
    await toggleSlideFullscreen()
  } catch (error) {
    console.error('切换幻灯片全屏失败:', error)
  }
}

// 幻灯片模式：上一页
function goToPreviousSlide() {
  if (currentSlideIndex.value > 0) {
    currentSlideIndex.value--
  }
}

// 幻灯片模式：下一页
function goToNextSlide() {
  const cellsToUse = isPreviewMode.value ? filteredCells.value : cells.value
  if (currentSlideIndex.value < cellsToUse.length - 1) {
    currentSlideIndex.value++
  }
}

// 幻灯片模式：跳转到指定页
function goToSlide(index: number) {
  const cellsToUse = isPreviewMode.value ? filteredCells.value : cells.value
  const maxIndex = cellsToUse.length - 1
  currentSlideIndex.value = Math.max(0, Math.min(index, maxIndex))
}

// 滚动到顶部
function scrollToTop() {
  const container = document.querySelector('.fixed.inset-0 .overflow-y-auto') as HTMLElement | null
  if (container && container.scrollTo) {
    container.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
  }
}

// 显示 Toast
function showToast(type: 'success' | 'error' | 'warning', message: string) {
  toast.value = { show: true, type, message }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

// 滚动到新添加的单元
function scrollToNewCell(index: number) {
  if (!cellListRef.value) return
  
  const cellElements = cellListRef.value.querySelectorAll('[data-cell-index]')
  const targetElement = cellElements[index] as HTMLElement | null
  
  if (targetElement && targetElement.classList) {
    targetElement.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
      inline: 'nearest'
    })
    
    // 添加高亮效果
    targetElement.classList.add('ring-2', 'ring-blue-400', 'ring-opacity-75')
    setTimeout(() => {
      if (targetElement && targetElement.classList) {
        targetElement.classList.remove('ring-2', 'ring-blue-400', 'ring-opacity-75')
      }
    }, 2000)
  }
}

// 获取 Cell 类型名称
function getCellTypeName(cellType: CellType): string {
  const nameMap = {
    [CellType.TEXT]: '文本单元',
    [CellType.CODE]: '代码单元',
    [CellType.PARAM]: '参数单元',
    [CellType.SIM]: '仿真单元',
    [CellType.CHART]: '图表单元',
    [CellType.CONTEST]: '竞赛单元',
    [CellType.VIDEO]: '视频单元',
    [CellType.ACTIVITY]: '活动单元',
    [CellType.FLOWCHART]: '流程图单元',
  }
  return nameMap[cellType]
}

// 初始化拖拽排序
let sortableInstance: Sortable | null = null

function initSortable() {
  if (cellListRef.value && !isPreviewMode.value) {
    // 先销毁已存在的实例
    destroySortable()
    
    sortableInstance = Sortable.create(cellListRef.value, {
      animation: 200,
      handle: '.drag-handle, .cell-drag-area',
      filter: '.add-cell-menu-container, .cell-title-editor',
      preventOnFilter: false,
      ghostClass: 'sortable-ghost',
      chosenClass: 'sortable-chosen',
      dragClass: 'sortable-drag',
      forceFallback: true,
      fallbackOnBody: true,
      swapThreshold: 0.65,
      onStart: (evt) => {
        // 拖拽开始时添加视觉反馈
        evt.item.style.cursor = 'grabbing'
      },
      onEnd: (evt) => {
        // 恢复光标样式
        if (evt.item) {
          evt.item.style.cursor = ''
        }
        if (evt.oldIndex !== undefined && evt.newIndex !== undefined && evt.oldIndex !== evt.newIndex) {
          lessonStore.reorderCells(evt.oldIndex, evt.newIndex)
          showToast('success', '顺序已调整')
        }
      },
    })
  }
}

function destroySortable() {
  if (sortableInstance) {
    sortableInstance.destroy()
    sortableInstance = null
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
    })
  }
})

// 监听 cells 变化，重新初始化拖拽（当 cells 数量变化时）
watch(() => cells.value.length, () => {
  if (!isPreviewMode.value && cellListRef.value) {
    nextTick(() => {
      destroySortable()
      setTimeout(initSortable, 100)
    })
  }
})

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

// 处理幻灯片区域的鼠标移动
function handleSlideMouseMove() {
  if (slideFullscreen.value) {
    showSlideControls.value = true
    resetControlsTimer()
  }
}

// 处理鼠标离开幻灯片区域
function handleSlideMouseLeave() {
  if (slideFullscreen.value) {
    resetControlsTimer()
  }
}

// 处理控制按钮区域的鼠标进入
function handleControlsMouseEnter() {
  if (slideFullscreen.value) {
    clearControlsTimer()
    showSlideControls.value = true
  }
}

// 处理控制按钮区域的鼠标离开
function handleControlsMouseLeave() {
  if (slideFullscreen.value) {
    resetControlsTimer()
  }
}

// 重置控制按钮隐藏定时器
function resetControlsTimer() {
  clearControlsTimer()
  if (slideFullscreen.value) {
    slideControlsTimer = setTimeout(() => {
      if (slideFullscreen.value) {
        showSlideControls.value = false
      }
    }, 3000) // 3秒后自动隐藏
  }
}

// 清除控制按钮隐藏定时器
function clearControlsTimer() {
  if (slideControlsTimer) {
    clearTimeout(slideControlsTimer)
    slideControlsTimer = null
  }
}

// 监听cells变化，确保索引有效
watch(() => cells.value.length, (newLength) => {
  if (slideMode.value && currentSlideIndex.value >= newLength) {
    currentSlideIndex.value = Math.max(0, newLength - 1)
  }
})

// 处理全屏预览的键盘事件
function handleFullscreenKeydown(event: KeyboardEvent) {
  // ESC: 退出全屏或退出幻灯片全屏（原生全屏API会自动处理ESC键，这里主要是为了兼容）
  if (event.key === 'Escape') {
    if (slideFullscreen.value && isSlideNativeFullscreen.value) {
      handleSlideFullscreenToggle()
      return
    }
    if (isFullscreenPreview.value) {
      toggleFullscreenPreview()
      return
    }
  }

  // 仅在幻灯片模式下处理导航快捷键
  if (!slideMode.value) {
    return
  }

  // 阻止默认行为（如空格键滚动页面）
  if (['ArrowLeft', 'ArrowRight', 'Space', 'Enter', 'Home', 'End'].includes(event.key)) {
    event.preventDefault()
  }

  switch (event.key) {
    case 'ArrowLeft':
      // 左箭头：上一页
      goToPreviousSlide()
      break
    case 'ArrowRight':
    case 'Space':
    case 'Enter':
      // 右箭头/空格/回车：下一页
      goToNextSlide()
      break
    case 'Home':
      // Home: 第一页
      goToSlide(0)
      break
    case 'End':
      // End: 最后一页
      goToSlide(cells.value.length - 1)
      break
  }
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
watch(() => currentLesson.value?.title, (newTitle) => {
  if (newTitle !== undefined) {
    lessonTitle.value = newTitle
  }
})

// MVP: 处理参考笔记更新
function handleNotesUpdated(notes: string) {
  if (currentLesson.value) {
    currentLesson.value.reference_notes = notes
  }
}

function stripHtmlTags(html: string): string {
  return html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
}

function summarizeCell(cell: Cell, index: number): string | null {
  const orderLabel = `第${index + 1}单元`
  const typeMap: Record<string, string> = {
    [CellType.TEXT]: '文本',
    [CellType.CODE]: '代码',
    [CellType.PARAM]: '参数',
    [CellType.SIM]: '仿真',
    [CellType.CHART]: '图表',
    [CellType.CONTEST]: '竞赛',
    [CellType.VIDEO]: '视频',
    [CellType.ACTIVITY]: '活动',
    [CellType.FLOWCHART]: '流程图',
    [CellType.REFERENCE_MATERIAL]: '参考素材',
  }

  const typeLabel = typeMap[cell.type] || '单元'
  let detail = ''

  if (cell.type === CellType.TEXT && (cell as any).content?.html) {
    const plain = stripHtmlTags((cell as any).content.html ?? '')
    if (plain) {
      detail = plain.slice(0, 28)
      if (plain.length > 28) {
        detail += '…'
      }
    }
  } else if (cell.type === CellType.ACTIVITY && (cell as any).content?.title) {
    detail = (cell as any).content.title
  } else if (cell.type === CellType.VIDEO && (cell as any).content?.title) {
    detail = (cell as any).content.title
  } else if (cell.type === CellType.FLOWCHART) {
    detail = '流程设计'
  } else if (cell.type === CellType.SIM) {
    detail = '仿真互动'
  }

  const parts = [orderLabel, typeLabel]
  if (detail) {
    parts.push(`：${detail}`)
  }
  return parts.join('')
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function markdownToHtml(markdown: string): string {
  const trimmed = markdown.trim()
  if (!trimmed) return ''

  const blocks = trimmed.split(/\n{2,}/)
  return blocks
    .map((block) => {
      const lines = block.split('\n')
      const htmlLines = lines.map((line) => escapeHtml(line))
      return `<p>${htmlLines.join('<br />')}</p>`
    })
    .join('')
}

function handleAiInsert(content: string) {
  if (!currentLesson.value) return

  const html = markdownToHtml(content)
  if (!html) {
    showToast('error', 'AI 返回内容为空，插入失败')
    return
  }

  const newCell = getDefaultCell(CellType.TEXT, currentLesson.value.content.length)
  ;(newCell.content as any).html = html
  lessonStore.addCell(newCell)
  showToast('success', 'AI 建议已插入到教案末尾')

  nextTick(() => {
    scrollToNewCell(cells.value.length - 1)
  })
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
            const items = Array.isArray((pending as any)?.value)
              ? [...(pending as any).value]
              : []
            if ((pending as any)?.value) {
              ;(pending as any).value = []
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

      currentLesson.value.content.forEach((cell, idx) => {
        cell.order = idx
      })

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
  // 如果已经在 handleBack 中保存了，跳过
  if (isSavingOnUnmount.value) {
    console.log('⏭️ 已在返回时保存，跳过卸载时保存')
    return
  }
  
  // 在卸载前保存未保存的更改
  if (currentLesson.value && !isPreviewMode.value) {
    // 检查是否有实际的未保存更改（通过对比 cells 和 currentLesson.content）
    const currentCellsCount = cells.value.length
    const lessonContentCount = currentLesson.value.content?.length || 0
    const hasActualChanges = currentCellsCount !== lessonContentCount || hasUnsavedChanges.value
    
    if (hasActualChanges) {
      isSavingOnUnmount.value = true
      try {
        console.log('💾 组件卸载前保存未保存的更改...', {
          cellsCount: currentCellsCount,
          lessonContentCount: lessonContentCount,
          hasUnsavedChanges: hasUnsavedChanges.value,
          hasActualChanges: hasActualChanges
        })
        // 更新标题
        if (currentLesson.value) {
          currentLesson.value.title = lessonTitle.value
          // 确保使用最新的 cells 数据
          currentLesson.value.content = [...cells.value]
        }
        await lessonStore.saveCurrentLesson()
        hasUnsavedChanges.value = false
        console.log('✅ 组件卸载前已保存更改')
      } catch (error) {
        console.error('❌ 组件卸载前保存失败:', error)
        // 保存失败时记录错误，但继续卸载流程
      } finally {
        isSavingOnUnmount.value = false
      }
    }
  }
  
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
  0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
  100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
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
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.slide-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
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
  transition: opacity 0.3s ease, transform 0.3s ease;
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
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
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
</style>