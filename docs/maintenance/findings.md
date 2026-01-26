# Findings: LessonEditor.vue 模块化

## Requirements

- 将 LessonEditor.vue（~3555 行）做模块化与复用，降低单文件长度
- 通过 composables、子组件、工具函数方式重构，不改变现有功能
- 采用 planning-with-files 做分阶段实施

## LessonEditor.vue 结构概览

### Template 区块（约 1258 行）

| 行号（约） | 区块 | 职责 | 抽离建议 |
|------------|------|------|----------|
| 1–465 | 顶部 nav | 返回、标题、导播台信息、保存状态、保存/发布、AI 助手、封面 modal、紧凑/预览/全屏、导出 | → LessonEditorNavBar + 封面编辑 Modal 可保留或单独 CoverImageModal |
| 467–744 | 主内容 | CellToolbar、加载/错误、封面预览、ReferenceResourcePanel、Section 标签+SectionContainer、空状态 | 封面块 → LessonEditorCoverBlock；其余保留或微调 |
| 746–846 | Toast | 全局 Toast | 已用 ref+函数，可保留 |
| 848–876 | 抽屉/模态 | LessonAiAssistantDrawer、ClassroomSelectorModal、PDFViewerModal、TeachingAssistantFAB、TeachingAssistantDrawer | 保留，仅由主文件组装 |
| 878–1256 | 全屏预览 Teleport | 头部、滚动/幻灯片、幻灯片全屏、浮动控制、底部导航、返回顶部 | → LessonEditorFullscreenPreview |

### Script 区块（约 2045 行）

#### 1. Refs / 状态（约 80+ 个）

- **大环节与 UI**：sections, activeSectionIndex, editingTabId, editingTabNameRef
- **加载与模式**：isLoading, loadError, toolbarCollapsed, isPreviewMode, compactMode, isFullscreenPreview, slideMode, currentSlideIndex, slideFullscreen, showSlideControls, slideControlsTimer, cellListRef, tabsContainerRef, slideContainerRef
- **封面**：coverImageInput, isUploadingCoverImage, showCoverImagePreview, coverImagePreviewUrl, coverImagePreviewFile, coverImagePreview, imageQuality, maxImageWidth, maxImageHeight, coverImageLoadError
- **发布与导出**：showPublishModal, selectedClassroomIds, publishError, exporting, exportToast
- **Session / 课堂**：teacherControlPanelRef, currentSessionId, providedSessionRef, showClassroomPanel, showAssistantDrawer
- **保存**：saveStatus, lastSavedAt, hasUnsavedChanges, isSavingOnUnmount
- **其它**：toast, lessonTitle, showLessonAssistant, referenceResource, showReferencePanel, showPDFViewer, isFlowInteractionActive, flowInteractionResumeTimer

#### 2. 逻辑分组（可对应 composables）

| 分组 | 主要函数/逻辑 | Composable 建议 |
|------|---------------|-----------------|
| **Session/课堂** | handleSessionChanged, checkSessionId, panelSession(watch), providedSessionId(computed), provide('classroomSession','classroomSessionId','currentLessonId'), 多个 watch(session 相关) | useLessonEditorSession |
| **Sections↔content** | watch(route+lessonId→normalizeContentToSections), watch(sections→sectionsToContent), handleSectionUpdate/Delete/Add, handleTabDblClick, initTabsSortable, onEnd(tabs Sortable) | useLessonEditorSections（部分与 Nav 的 fullscreen 协同） |
| **保存** | manualSave, handleManualSave, hasUnsavedChanges(watch), saveStatus(watch), formatSaveTime, handleBack 内保存, onUnmounted 内保存 | useLessonEditorSave |
| **Cells** | getDefaultCell, createReferenceMaterialCell, handleAddCellToEnd, handleAddCellInSection, handleAddCellAt, insertReferenceMaterial, handleCellUpdate, handleDeleteCell, handleMoveUp, handleMoveDown | useLessonEditorCells |
| **封面** | triggerCoverImageUpload, handleCoverImageSelect, cancelCoverImageEdit, processAndUploadCoverImage, processImage, coverImageUrl(computed), watch(cover_image_url) | useLessonEditorCover |
| **发布** | handlePublish, handlePublishConfirm, handlePublishCancel | useLessonEditorPublish |
| **导航/全屏/导出** | handleBack, handleExportLesson, toggleFullscreenPreview, handleTogglePreviewMode, handleSlideFullscreenToggle, initSortable(空), destroySortable | useLessonEditorNav（部分） |
| **幻灯片** | goToPreviousSlide, goToNextSlide, goToSlide, scrollToTop, handleSlideMouseMove, handleSlideMouseLeave, handleControlsMouseEnter/Leave, resetControlsTimer, clearControlsTimer, handleFullscreenKeydown 中幻灯片分支, watch(slideMode, isSlideNativeFullscreen, slideFullscreen, cells.length→currentSlideIndex) | useLessonEditorSlides |
| **杂项** | showToast, scrollToNewCell, getCellTypeName, handleClassroomButtonClick, handleAiInsert, handleNotesUpdated, stripHtmlTags, summarizeCell, escapeHtml, markdownToHtml, handleFlowInteractionStart/End | getCellTypeName/summarizeCell/scrollToNewCell→useLessonEditorCells 或 lessonEditorHelpers；showToast→保留或 useToast；AI/Notes/Flow→保留主文件或小 composable |

#### 3. 生命周期

- **onMounted**：loadLesson、consumeReferenceQueue、插入 reference、initSortable/initTabsSortable、beforeunload/visibilitychange、flowchart 事件、checkSessionId 轮询
- **onUnmounted**：保存逻辑、removeEventListener、destroySortable、clearControlsTimer 等

#### 4. 已有依赖

- **Store**：useLessonStore（currentLesson, cells, isSaving, loadLesson, saveCurrentLesson, publishCurrentLesson, loadAvailableClassrooms, ...）
- **子组件**：CellToolbar, CellContainer, SectionContainer, ReferenceResourcePanel, PDFViewerModal, ClassroomSelectorModal, LessonAiAssistantDrawer, TeacherClassroomControlPanel, TeachingAssistantFAB, TeachingAssistantDrawer
- **工具**：lessonContent（normalizeContentToSections, sectionsToContent, isContentWithSections）, useFullscreen(slideContainerRef)

## Technical Decisions

| 决策 | 理由 |
|------|------|
| 先做 composables，再做子组件 | 逻辑集中到 composable，template 仅做布局和绑定，子组件从「大块 template」拆即可 |
| useLessonEditorSession 负责 provide + 所有 session 相关 watch | 避免主文件堆积大量 session 相关代码 |
| useLessonEditorSlides 包含幻灯片索引、控制显隐、键盘事件中的幻灯片分支 | 全屏预览子组件只负责 DOM 和点击/触摸，业务逻辑在 composable |
| 工具函数 stripHtmlTags、escapeHtml、markdownToHtml、getCellTypeName 放 `utils/lessonEditorHelpers.ts` | 纯函数、可能被 AI/导出等复用 |
| scrollToNewCell、summarizeCell 留在 useLessonEditorCells 或 helpers | summarizeCell 依赖 Cell 类型与 summarize 规则，与 cells 强相关；scrollToNewCell 依赖 cellListRef，可放在 Nav 或主文件，或通过 composable 返回 ref 注入 |

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| handleBack 中 `currentLesson.value.content = latestCells`（扁平数组） | 应改为 `sectionsToContent(sections.value)`，与 manualSave 一致，避免 sections 格式下丢 cell |
| onUnmounted 中 `currentLesson.value.content = [...cells.value]` | 同上，改为 `sectionsToContent(sections.value)` |

## 建议目录

```
frontend/src/
├── composables/
│   ├── useLessonEditorNav.ts      # 返回、导出、fullscreen 切换、destroySortable
│   ├── useLessonEditorSession.ts  # session、provide、watch
│   ├── useLessonEditorSave.ts     # manualSave、handleBack 保存、hasUnsavedChanges、formatSaveTime
│   ├── useLessonEditorSlides.ts   # slide 索引、goTo*、controls 显隐、键盘
│   ├── useLessonEditorCells.ts    # getDefaultCell、handleAdd*、handleCellUpdate、handleDelete、handleMove*、summarizeCell、scrollToNewCell
│   ├── useLessonEditorSections.ts # sections 同步、handleSection*、handleTabDblClick、initTabsSortable
│   ├── useLessonEditorCover.ts    # 封面上传、预览、裁剪
│   └── useLessonEditorPublish.ts  # 发布弹窗、confirm/cancel
├── components/
│   └── Lesson/
│       ├── LessonEditorNavBar.vue
│       ├── LessonEditorCoverBlock.vue
│       └── LessonEditorFullscreenPreview.vue
├── utils/
│   └── lessonEditorHelpers.ts     # stripHtmlTags、escapeHtml、markdownToHtml、getCellTypeName
└── pages/
    └── Teacher/
        └── LessonEditor.vue       # 目标约 800–1200 行
```

## LessonEditorToast.vue 分析

### 问题

- **Props：** 仅有 `toast: ToastData`（`{ show, type, message }`）。
- **模板：** 使用了 `show`、`type`、`message`，这三个名字在 script 中未定义，应从 `toast` 上读取。
- **父组件：** `LessonEditor.vue` 使用 `<LessonEditorToast :toast="toast" @close="toast.show = false" />`，`toast` 符合 `ToastData`。

### 修复

在模板中统一改为：`toast.show`、`toast.type`、`toast.message`。

---

## 数据流要点

- **sections**：由 `useLessonEditorSections` 提供 ref，与 `currentLesson.content` 双向同步（normalizeContentToSections / sectionsToContent）。
- **保存**：`manualSave`、`handleBack`、`onUnmounted` 一律用 `sectionsToContent(sections.value)` 写回 `currentLesson.content`，再 `lessonStore.saveCurrentLesson()`。
- **provide**：`classroomSession`、`classroomSessionId`、`currentLessonId` 在 `useLessonEditorSession` 或主文件 provide，子组件 inject。
- **Fullscreen 与 Slide**：`isFullscreenPreview`、`slideMode`、`slideFullscreen` 等由 composable 提供，LessonEditorFullscreenPreview 通过 props 与事件与 composable 通信。
