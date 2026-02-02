# 课堂会话子组件重构 — 结构说明与学习指南

> 基于你整理的重构清单（7 个 Composables、10 个子组件、3 个工具文件），说明目标架构与当前代码的对应关系，并给出学习路径。

---

## 一、当前状态 vs 目标设计

| 层级 | 目标设计（你的清单） | 当前代码中的位置 |
|------|----------------------|------------------|
| **Composables** | 7 个独立文件 | 逻辑大多在 `TeacherControlPanel.vue` 和 `useClassroomSession.ts` 内联 |
| **子组件** | 10 个独立 .vue | UI 都在 `TeacherControlPanel.vue` 的 template 里，仅 `CellTypeIcon` 为内联组件 |
| **工具** | 3 个 utils 文件 | 部分在 `utils/cellId.ts`，时长/学生等格式化散落在组件内 |

**结论**：设计已明确（清单即「要做成什么样」），实现上仍是「一个大组件 + 少量 composable」，适合按下面结构分步学习和落地。

---

## 二、目标架构总览（按依赖关系）

```
                    TeacherControlPanel.vue（容器）
                                    │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
   [Composables]              [子组件]                    [工具函数]
   提供状态与方法              纯展示/轻逻辑                纯函数、无状态
        │                          │                          │
        └──────────────────────────┴──────────────────────────┘
                                    │
                            props / inject / 事件
```

- **Composables**：会话状态、轮询、计时、导航、数据加载、全屏、选择模式。
- **子组件**：只负责展示和发事件，数据来自父组件或 composables 暴露的 ref/computed。
- **工具**：格式化、Cell 处理、学生监控等，被 composables 或组件调用。

---

## 三、7 个 Composables — 职责与学习顺序

建议按「数据从哪来 → 谁用」的顺序学：先会话与数据，再轮询/计时，最后交互（导航、全屏、选择模式）。

| 顺序 | 名称 | 职责（目标） | 当前大致对应代码位置 |
|------|------|--------------|----------------------|
| 1 | **useSessionManager** | 会话 CRUD、状态变更（创建/开始/暂停/继续/结束） | `TeacherControlPanel` 里的 `handleCreateSession`、`handleBeginClass`、`handleEnd`、`handlePause`、`handleResume` 及 `session` 状态 |
| 2 | **useDataLoader** | 加载 lesson、cells、统计等，统一 loading/error | 组件内的 `loadLesson`、`loadStatistics`、`loading`、与 lesson/session 相关的请求 |
| 3 | **usePolling** | 定时拉取会话/学生列表，可启停、间隔可配 | 组件内轮询 activeStudents、或 `useClassroomSession` 里的 polling 逻辑 |
| 4 | **useDurationTimer** | 课程时长计时（开始/暂停/剩余时间） | `startDurationTimer`、`stopDurationTimer`、`sessionDuration`、`remainingTime`、`LESSON_DURATION` |
| 5 | **useNavigation** | 上一/下一模块、当前 cell、切换请求 | `handlePrevModule`、`handleNextModule`、`selectedCellIndex`、与 `buildNavigateRequest` 相关的逻辑 |
| 6 | **useFullscreen** | 导播台/模块列表全屏切换 | 已有 `useFullscreen.ts`，教师端全屏状态在 `TeacherControlPanel` 的 `isPanelFullscreen`、`modulePanelFullscreen` |
| 7 | **useSelectionMode** | 单选/多选模式、与模块勾选联动 | `isMultiSelectMode`、`toggleSelectionMode`、勾选/广播逻辑 |

**学习建议**：

1. 打开 `TeacherControlPanel.vue`，用「函数名 / 变量名」搜索上表里的关键词，看同一职责的代码如何集中在一起。
2. 想象「如果把这整块抽成 `useXxx()`，入参和返回值应该是什么」—— 这能帮你定 composable 的接口。
3. 先读 `useClassroomSession.ts`（学生端）和 `useFullscreen.ts`，感受「composable 只暴露 ref + 方法、组件只消费」的写法。

---

## 四、10 个子组件 — 职责与对应模板块

每个子组件对应「一块可独立命名的 UI」，便于单测和复用。当前都在 `TeacherControlPanel.vue` 的 template 里。

| 序号 | 组件名 | 职责（目标） | 当前在 TeacherControlPanel 中的大致位置（行号供参考） |
|------|--------|--------------|--------------------------------------------------------|
| 1 | **SessionDurationDisplay** | 显示课程已进行时长、剩余时间、颜色告警 | 约 48–66 行：`.duration-info`、`formatDuration`、`formatRemainingTime` |
| 2 | **StudentCountDisplay** | 显示「已进入人数 / 总人数」 | 约 31–38 行：`.student-count-info` |
| 3 | **SessionControlButtons** | 创建课堂、开始/结束、暂停/继续、全屏切换等按钮 | 约 68–174 行：`.header-controls` 内所有按钮 |
| 4 | **ModuleCountDisplay** | 显示「共 N 个模块」 | 约 40–46 行：`.module-count-info` |
| 5 | **WaitingForStudentsBanner** | pending 时「等待学生加入」横幅 | 若有，在控制栏下方或主内容区；可能与其他 banner 合并 |
| 6 | **JoinedStudentsList** | 已加入学生列表（头像/名字等） | 若在导播台中有单独列表区域，即对应这块 |
| 7 | **ModuleList** | 模块列表（序号、图标、标题、勾选、当前高亮） | 约 213–258 行：`.module-list`、`.module-item`、`CellTypeIcon` |
| 8 | **ClassroomSelectModal** | 创建课堂时选择班级的弹窗 | `ClassroomSwitcher` 或创建会话时的 modal |
| 9 | **ActivityStatisticsPanel** | 活动统计面板 | 与 `sessionStatistics`、`loadStatistics` 相关的 UI |
| 10 | **CellTypeIcon** | 按 cell 类型显示图标 | 约 242、278 行：已为内联组件，可单独提到 `CellTypeIcon.vue` |

**学习建议**：

1. 在 `TeacherControlPanel.vue` 的 template 里，按上表逐个找到对应 HTML 块，用注释临时标成 `<!-- SessionDurationDisplay -->` 等，建立「设计名称 ↔ 现有 DOM」的对应。2025-2026
2. 对每个块问三件事：**props 需要什么**、**需要 emit 哪些事件**、**样式是否要一起迁到子组件**（scoped 或单独文件）。
3. 先拆「纯展示、无复杂交互」的（如 SessionDurationDisplay、StudentCountDisplay、ModuleCountDisplay、CellTypeIcon），再拆带交互的（SessionControlButtons、ModuleList）。

---

## 五、3 个工具文件 — 职责与当前位置

| 工具文件 | 职责（目标） | 当前代码位置 |
|----------|--------------|--------------|
| **studentMonitoring** | 学生列表过滤、排序、状态判断（如是否已提交） | 分散在 `TeacherControlPanel` 的 `activeStudents`、`getStudentStatusClass`、统计相关逻辑 |
| **cellUtils** | Cell 类型标签、tooltip、与 ID/顺序相关的纯函数 | 部分在 `utils/cellId.ts`（`getCellId`, `buildNavigateRequest` 等），`getCellTypeLabel`、`getModuleTooltip` 等在组件内 |
| **formatUtils** | 时长显示、剩余时间、数字/日期等格式化 | 组件内的 `formatDuration`、`formatRemainingTime` 等 |

**学习建议**：

1. 在组件里搜 `format*`、`getCell*`、`getModule*`、`getStudent*`，把「不依赖 Vue/组件实例」的函数列出来，归到上面三类。
2. 先抽 `formatUtils`（最独立），再 `cellUtils`（依赖类型/常量可一起移入），最后 `studentMonitoring`（可能依赖类型定义）。

---

## 六、推荐学习路径（3 步）

### 第 1 步：建立「设计 ↔ 现状」地图（约 1 小时）

- 打开 `docs/plans/2026-02-01-classroom-session-implementation.md` 中「第 3 阶段：前端重构」相关小节。
- 打开 `TeacherControlPanel.vue`，用本指南第三节、第四节、第五节的三张表，在代码里标出每一块对应的位置。
- 输出：一份简短笔记（或注释），例如「SessionDurationDisplay ≈ 第 48–66 行 + `displayDuration` / `remainingTime`」。

### 第 2 步：按「工具 → Composable → 子组件」理解数据流

1. **工具**：想象 `formatUtils.formatDuration(seconds)`、`cellUtils.getCellTypeLabel(type)` 被谁调——应是 composables 或组件，不直接依赖 DOM。
2. **Composables**：想象 `useSessionManager()` 返回 `{ session, createSession, startSession, endSession }`，`TeacherControlPanel` 只负责把这些绑定到模板和子组件。
3. **子组件**：想象 `SessionDurationDisplay` 只接收 `duration`、`remainingTime`、`status` 等 props，不自己拉接口、不自己管定时器。

这样能避免「拆完子组件又塞回一堆逻辑」的情况。

### 第 3 步：选一小块做「最小闭环」实践

建议选 **SessionDurationDisplay + useDurationTimer**：

1. 新建 `useDurationTimer.ts`：把 `sessionDuration`、`remainingTime`、`startDurationTimer`、`stopDurationTimer`、对 `session.status` 的 watch 从 `TeacherControlPanel` 移入，暴露 `duration`、`remainingTime`、`formattedDuration`、`formattedRemaining`（内部用 `formatUtils`）。
2. 新建 `formatUtils.ts`：把 `formatDuration`、`formatRemainingTime` 移入并导出。
3. 新建 `SessionDurationDisplay.vue`：只接收 props（如 `duration`、`remainingTime`、`status`），内部用 `formatUtils` 做展示；样式从原组件剪过去。
4. 在 `TeacherControlPanel` 中：`const duration = useDurationTimer(session)`，在 template 里用 `<SessionDurationDisplay :duration="duration.duration" ... />` 替换原来的 duration 块。

做完这一条线，你就同时练到了「工具 → Composable → 子组件」的拆分与使用方式，其它块可以按同一模式复制。

---

## 七、和现有文档的关系

- **实施计划**：`docs/plans/2026-02-01-classroom-session-implementation.md` 里的 Task 3.x 是「按阶段实现」的步骤，本指南是「先理解结构再动手」的学习顺序，两者可并行：理解用本指南，实施跟计划里的 Task。
- **命名差异**：计划里部分组件名（如 SessionHeader、SessionTimer、ActionButtons）与你的清单（SessionDurationDisplay、SessionControlButtons）略有不同，以你当前清单为准即可，对应关系按「职责」对上即可。

---

## 八、自测清单（学完可自检）

- [ ] 能说出 7 个 composables 各自管什么、谁可能依赖谁。
- [ ] 能在 `TeacherControlPanel.vue` 里快速找到 10 个子组件对应的模板块。
- [ ] 能说出 3 个工具文件各放哪类函数、被谁调。
- [ ] 能独立完成「SessionDurationDisplay + useDurationTimer + formatUtils」这一条最小闭环拆分。

如果你愿意，下一步可以指定「先实现哪一个 composable 或哪一个子组件」，我可以按当前仓库的代码结构给出更具体的抽取步骤和示例补丁（或直接改对应文件）。  
你更想先动手 **Composable**、**子组件** 还是 **工具**？
