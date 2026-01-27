# 全屏预览功能界面展示

> 注：本文档包含占位符，实际使用时请添加真实截图

## 1. 编辑页面 - 全屏预览按钮

在教案编辑页面顶部工具栏右侧，可以看到"全屏预览"按钮（紫色按钮，带眼睛图标）。

```
[截图占位：编辑页面顶部工具栏，突出显示"全屏预览"按钮]
建议截图路径：docs/images/fullscreen-preview-button.png
```

**按钮位置：**
- 位于顶部工具栏右侧
- "预览模式"按钮之后
- 采用紫色背景，白色文字
- 带有眼睛图标

---

## 2. 全屏预览模式 - 整体界面

点击"全屏预览"按钮后，页面进入全屏预览模式。

```
[截图占位：全屏预览模式的整体界面]
建议截图路径：docs/images/fullscreen-preview-overview.png
```

**界面特点：**
- 全屏显示，覆盖整个浏览器窗口
- 顶部保留简洁的导航栏
- 中间区域显示教学内容
- 右下角有浮动的"返回顶部"按钮

---

## 3. 全屏预览模式 - 顶部导航栏

全屏预览模式的顶部导航栏设计简洁，只保留必要的信息和操作。

```
[截图占位：全屏预览模式的顶部导航栏]
建议截图路径：docs/images/fullscreen-preview-header.png
```

**导航栏元素：**
- 左侧：教案标题和"沉浸式预览"标签
- 右侧："退出预览"按钮

---

## 4. 内容展示区域

全屏预览模式下，教学内容以最佳的方式展示。

```
[截图占位：全屏预览模式的内容展示区域，包含多种Cell类型]
建议截图路径：docs/images/fullscreen-preview-content.png
```

**内容区域特点：**
- 最大宽度约为 1280px，居中显示
- 各个 Cell 之间有合适的间距
- 支持所有 Cell 类型的正常渲染

---

## 5. 浮动操作按钮

在全屏预览模式的右下角，有一个浮动的"返回顶部"按钮。

```
[截图占位：右下角的浮动"返回顶部"按钮]
建议截图路径：docs/images/fullscreen-preview-fab.png
```

**按钮特点：**
- 圆形设计
- 白色背景，带阴影
- 鼠标悬停时阴影加深
- 点击后平滑滚动到页面顶部

---

## 6. 不同 Cell 类型的展示

全屏预览模式支持所有 Cell 类型的展示。

### 6.1 文本单元

```
[截图占位：文本单元在全屏预览模式下的展示]
建议截图路径：docs/images/fullscreen-preview-text-cell.png
```

### 6.2 代码单元

```
[截图占位：代码单元在全屏预览模式下的展示]
建议截图路径：docs/images/fullscreen-preview-code-cell.png
```

### 6.3 视频单元

```
[截图占位：视频单元在全屏预览模式下的展示]
建议截图路径：docs/images/fullscreen-preview-video-cell.png
```

### 6.4 仿真单元

```
[截图占位：仿真单元在全屏预览模式下的展示]
建议截图路径：docs/images/fullscreen-preview-sim-cell.png
```

---

## 7. 进入/退出动画

全屏预览模式有流畅的进入和退出动画。

```
[GIF占位：进入全屏预览的动画效果]
建议GIF路径：docs/images/fullscreen-preview-enter.gif
```

```
[GIF占位：退出全屏预览的动画效果]
建议GIF路径：docs/images/fullscreen-preview-exit.gif
```

**动画特点：**
- 淡入淡出效果
- 轻微的缩放效果（0.95 → 1.0）
- 持续时间：300ms
- 缓动函数：ease

---

## 8. 空状态展示

当教案没有内容时，全屏预览模式显示友好的空状态提示。

```
[截图占位：全屏预览模式的空状态]
建议截图路径：docs/images/fullscreen-preview-empty.png
```

---

## 9. 响应式设计

全屏预览模式在不同屏幕尺寸下都有良好的展示效果。

### 9.1 桌面端（1920x1080）

```
[截图占位：桌面端大屏幕下的全屏预览]
建议截图路径：docs/images/fullscreen-preview-desktop.png
```

### 9.2 笔记本（1366x768）

```
[截图占位：笔记本屏幕下的全屏预览]
建议截图路径：docs/images/fullscreen-preview-laptop.png
```

### 9.3 平板横屏（1024x768）

```
[截图占位：平板横屏下的全屏预览]
建议截图路径：docs/images/fullscreen-preview-tablet.png
```

---

## 添加截图的步骤

1. 创建 `docs/images/` 目录（如果不存在）：
   ```bash
   mkdir -p docs/images
   ```

2. 启动应用并登录教师账号

3. 创建或打开一个包含多种 Cell 类型的教案

4. 使用截图工具捕获各个界面：
   - macOS: Cmd + Shift + 4（区域截图）或 Cmd + Shift + 3（全屏截图）
   - Windows: Win + Shift + S
   - 浏览器开发者工具：F12 → 设备模式（用于响应式截图）

5. 将截图保存到 `docs/images/` 目录，使用建议的文件名

6. 替换本文档中的占位符为实际的图片链接：
   ```markdown
   ![描述文字](../images/screenshot-name.png)
   ```

7. 对于动画效果，可以使用以下工具录制 GIF：
   - macOS: Kap (https://getkap.co/)
   - Windows: ScreenToGif (https://www.screentogif.com/)
   - 跨平台: LICEcap (https://www.cockos.com/licecap/)

---

## 注意事项

- 截图应清晰，避免模糊
- 建议使用 PNG 格式保存截图（无损压缩）
- GIF 动画应控制文件大小，建议不超过 5MB
- 截图中避免包含敏感信息
- 可以使用图片编辑工具添加箭头、标注等辅助说明


