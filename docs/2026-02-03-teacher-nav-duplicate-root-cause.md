# 教师导播台导航条重复按钮 — 根本原因说明

## 现象

开始上课后，`header-controls` 内出现重复的「窗口」「结束」以及已废弃的「暂停」「继续」按钮，例如：

```
结束授课  窗口  ⏸️ 暂停  ⏹️ 结束  窗口  ▶️ 继续  ⏹️ 结束
```

## 根本原因

### 1. 多套条件块并存（历史设计）

旧版 `TeacherControlPanel.vue` 在 **同一层** `header-controls` 里有多块 **互相独立的 `v-if`**（不是 `v-else-if`），按状态展示不同按钮：

| 条件 | 渲染内容 |
|------|----------|
| `session.status === 'PENDING'` | 开始上课 + 结束 |
| `session.status === 'active' \|\| 'ACTIVE'` | **窗口** + **暂停** + **结束** |
| `session.status === 'paused' \|\| 'PAUSED'` | **窗口** + **继续** + **结束** |

后来引入 **SessionControlButtons**，在 TEACHING 时再渲染「结束授课」。  
结果是：**同一区域里既有子组件按钮，又有上述多块按状态渲染的按钮**，来源不统一。

### 2. 状态语义不一致

- **后端** 会话状态只有：`PREPARING`、`TEACHING`、`ENDED`（v2.0 已移除 PAUSED）。
- **旧前端** 仍按 `active` / `ACTIVE`、`paused` / `PAUSED` 判断，和当前后端不一致。
- 若某处把 `TEACHING` 映射成 `active`，或存在「teaching 块 + active 块」同时满足的情况，就会 **多块同时渲染**，出现：
  - 重复的「窗口」「结束」
  - 已废弃的「暂停」「继续」

### 3. 单一职责被打破

- 会话操作按钮 **本应只由一处** 决定（例如只由 SessionControlButtons + 一个「上课中」块）。
- 旧实现里：SessionControlButtons 负责一部分，内联的 ACTIVE/PAUSED 块又各负责一部分，**没有用 `v-else-if` 做成互斥**，导致在部分状态下多块同时显示。

## 正确做法（当前已采用）

1. **唯一控制源**
   - 所有「结束」「开始上课」「创建课堂」等会话操作，只由 **SessionControlButtons** 根据 `sessionStatus` 渲染（内部用 `v-if` / `v-else-if` / `v-else` 互斥）。
   - 上课中（TEACHING）时，只在 **一个** `v-if="teaching"` 块里增加「窗口」切换，不再重复「结束」，也不渲染「暂停」「继续」。

2. **状态与后端一致**
   - 使用 `normalizedSessionStatus`（preparing / teaching / ended）驱动 SessionControlButtons 和「上课中」块，与后端 PREPARING / TEACHING / ENDED 一致。
   - 不再使用 `active`、`paused` 作为会话状态判断。

3. **避免再次引入多块**
   - 在 `header-controls` 内 **不要** 再为「上课中」或「已暂停」单独加新的 `v-if` 按钮块（尤其是 窗口/结束/暂停/继续）。
   - 新增会话相关按钮时，应放在 SessionControlButtons 或该唯一「上课中」块内，并保持与上述状态枚举一致。

## 若仍看到重复

1. **确认构建与缓存**
   - 执行重新构建：`pnpm build` 或 `npm run build`。
   - 浏览器强刷或清空缓存后再打开（Ctrl+Shift+R / Cmd+Shift+R）。

2. **确认未使用旧文件**
   - 确保没有引用 `TeacherControlPanel.vue.backup` 或从备份还原了旧模板。
   - 确认 `TeacherControlPanel.vue` 的 `header-controls` 内只有：SessionControlButtons + 一个「上课中」的 窗口 块。

---

文档日期：2026-02-03
