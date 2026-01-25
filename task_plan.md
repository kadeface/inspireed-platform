# Task Plan: LessonEditor.vue 模块化重构

## Goal

将 `LessonEditor.vue`（约 3555 行）通过组合式函数、子组件和逻辑抽离进行模块化，在保持功能不变的前提下显著缩短主文件并提升可维护性。

## Current Phase

Phase 3（已完成）；Phase 4（子组件）与 Phase 5（主文件收口）部分完成；Phase 6（测试）待进行

## Phases

### Phase 1: 需求与结构分析
- [x] 完整阅读 LessonEditor.vue 的 template / script / style
- [x] 识别可抽离的 composables、子组件与工具函数
- [x] 梳理与 store、子组件、router 的依赖关系
- [x] 将结论写入 findings.md
- **Status:** complete

### Phase 2: 设计方案与目录规划
- [x] 确定 composables 列表及职责（见 findings「逻辑分组」）
- [x] 确定新子组件（LessonEditorNavBar, LessonEditorCoverBlock, LessonEditorFullscreenPreview）及职责
- [x] 确定工具函数归属（utils/lessonEditorHelpers：stripHtmlTags、escapeHtml、markdownToHtml、getCellTypeName）
- [x] 更新 findings.md 中的技术方案与目录结构（见「建议目录」「数据流要点」）
- **Status:** complete

### Phase 3: 实现 - Composables
- [x] 实现 useLessonEditorNav（返回、标题、紧凑/预览/全屏切换、导出等）
- [x] 实现 useLessonEditorSession（sessionId、classroom、provide、watch）
- [x] 实现 useLessonEditorSave（manualSave、handleManualSave、handleBack、saveStatus、hasUnsavedChanges、formatSaveTime）
- [x] 实现 useLessonEditorSlides（slideMode、currentSlideIndex、goTo*、slideControls 显隐、handleFullscreenKeydown 中幻灯片部分）
- [x] 实现 useLessonEditorCells（getDefaultCell、createReferenceMaterialCell、handleAdd*、handleCellUpdate、handleDeleteCell、handleMove*、summarizeCell 等）
- [x] 实现 useLessonEditorSections（handleSectionUpdate/Delete/Add、handleTabDblClick、initTabsSortable、sections↔content 的 watch）
- [x] 实现 useLessonEditorCover（triggerUpload、handleSelect、cancelEdit、processAndUpload、processImage、相关 refs）
- [x] 实现 useLessonEditorPublish（handlePublish、handlePublishConfirm/Cancel、publishModal 状态）
- **Status:** complete

### Phase 4: 实现 - 子组件
- [ ] LessonEditorNavBar：顶部导航（返回、标题、保存状态、保存/发布/导出、AI 助手、紧凑/预览/全屏、封面模态入口）
- [ ] LessonEditorCoverBlock：封面预览+上传按钮（编辑模式）
- [ ] LessonEditorFullscreenPreview：Teleport 全屏预览（滚动/幻灯片模式、幻灯片全屏、控制条、底部导航）
- **Status:** pending

### Phase 5: 实现 - 工具函数与主文件收口
- [ ] 将 stripHtmlTags、escapeHtml、markdownToHtml、getCellTypeName、scrollToNewCell 等迁到 `utils/lessonEditorHelpers.ts` 或 composable 内
- [ ] 主文件：只做 import、provide、layout 拼接、onMounted/onUnmounted
- [ ] 修正 handleBack / onUnmounted 的 content：统一为 `sectionsToContent(sections.value)`
- **Status:** pending

### Phase 6: 测试与收尾
- [ ] 本地验证：加载、编辑、保存、返回前保存、发布、导出、授课模式、全屏、幻灯片、封面、AI 插入
- [ ] 确认无回归
- **Status:** pending

## Key Questions

1. Composables 入参：内部 `useRoute/useRouter/useLessonStore`，减少主组件传参。
2. 子组件：以 `emit` 为主，由 LessonEditor 调用 composable 方法。
3. handleBack / onUnmounted：必须用 `sectionsToContent(sections.value)`，避免 sections 格式下丢 cell。

## Decisions Made

| 决策 | 理由 |
|------|------|
| Composables 放在 `composables/`，命名 `useLessonEditorXxx` | 与现有 useFullscreen、useToast 一致 |
| 子组件放 `components/Lesson/` 或 `components/Lesson/LessonEditor/` | 数量多则建子目录 |
| 工具函数放 `utils/lessonEditorHelpers.ts` | 纯函数、无 Vue 依赖 |
| 不拆 SectionContainer、CellContainer、CellToolbar | 已是独立组件 |

---

## Task: LessonEditorToast.vue 修复

### Goal

修正 `LessonEditorToast.vue` 中模板使用未定义变量 `show`、`type`、`message` 的问题，使其正确从 prop `toast` 读取 `toast.show`、`toast.type`、`toast.message`。

### Current Phase

Phase 1（分析）与 Phase 2（修复与验证）均已完成

### Phases

#### Phase 1: 分析
- [x] 确认 Props 仅包含 `toast: ToastData`，而模板使用了 `show`、`type`、`message`
- [x] 确认父组件 `LessonEditor.vue` 传入 `:toast="toast"`，且 `toast` 含 `{ show, type, message }`
- **Status:** complete

#### Phase 2: 修复与验证
- [x] 将模板中 `show` → `toast.show`，`type` → `toast.type`，`message` → `toast.message`
- [x] 运行 type-check / lint，确认无报错
- **Status:** complete

### Errors Encountered (Toast 任务)

| Error | Attempt | Resolution |
|-------|---------|------------|
| （暂无） | | |

---

## Errors Encountered

| Error | Attempt | Resolution |
|-------|---------|------------|
| （待填写） | 1 | |
