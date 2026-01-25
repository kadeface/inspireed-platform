# HTML互动课件开发指南

## 概述

本文档提供了开发HTML互动课件的指南，包括模板结构、交互组件使用和最佳实践。

## 模板位置

- **基础模板**: `/frontend/public/templates/interactive-base.html`
- **示例模板**: `/frontend/public/templates/knowledge-points/`

## 基础模板结构

### HTML结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>课件标题</title>
  <style>
    /* 样式定义 */
  </style>
</head>
<body>
  <div class="container">
    <h1>课件标题</h1>
    <div class="interactive-area">
      <!-- 互动内容 -->
    </div>
  </div>
  <script>
    // 交互逻辑
  </script>
</body>
</html>
```

### 样式系统

基础模板提供了以下样式类：

- `.container` - 主容器，白色背景，圆角卡片样式
- `.btn` - 按钮样式，渐变背景
- `.btn-secondary` - 次要按钮样式
- `.input` - 输入框样式
- `.card` - 卡片样式
- `.fade-in` - 淡入动画
- `.slide-in` - 滑入动画

### 响应式设计

模板已包含响应式设计，支持：
- 桌面端（> 768px）：完整布局
- 移动端（≤ 768px）：自适应布局，调整字体和间距

## 交互组件

### 按钮

```html
<button class="btn" onclick="handleClick()">点击按钮</button>
<button class="btn btn-secondary">次要按钮</button>
```

### 输入框

```html
<input type="text" class="input" placeholder="输入内容" />
<input type="number" class="input" placeholder="输入数字" />
```

### 卡片

```html
<div class="card">
  <p>卡片内容</p>
</div>
```

## 开发步骤

### 1. 选择模板

- 使用基础模板：适合从头开始创建
- 使用示例模板：适合快速开始，基于现有示例修改

### 2. 设计互动逻辑

确定课件的核心互动方式：
- 点击交互
- 拖拽操作
- 输入验证
- 动画演示

### 3. 实现交互

使用JavaScript实现交互逻辑：

```javascript
// 点击事件
element.addEventListener('click', function() {
  // 处理逻辑
});

// 输入事件
input.addEventListener('input', function() {
  // 处理输入
});

// 动画效果
element.classList.add('fade-in');
```

### 4. 测试和优化

- 在不同设备上测试
- 检查交互流畅性
- 优化性能和用户体验

## 示例模板

### 乘法口诀可视化

**位置**: `/templates/knowledge-points/multiplication-table.html`

**特点**:
- 9x9网格布局
- 点击单元格显示乘法结果
- 选中状态高亮

**适用知识点**: 计算类/速算技巧

### 图形认知互动

**位置**: `/templates/knowledge-points/geometry-shapes.html`

**特点**:
- 图形卡片展示
- 点击显示图形特点
- 视觉反馈

**适用知识点**: 几何类/图形认知

### 速算练习

**位置**: `/templates/knowledge-points/calculation-practice.html`

**特点**:
- 随机生成题目
- 答案验证
- 统计功能

**适用知识点**: 计算类/速算技巧

## 最佳实践

### 1. 用户体验

- **清晰的视觉反馈**：用户操作应该有明确的视觉反馈
- **友好的错误提示**：输入错误时提供清晰的提示
- **流畅的动画**：使用适度的动画增强体验

### 2. 性能优化

- **避免过度动画**：不要使用过多或过复杂的动画
- **优化DOM操作**：减少频繁的DOM操作
- **合理使用事件监听**：及时清理不需要的事件监听器

### 3. 可访问性

- **语义化HTML**：使用合适的HTML标签
- **键盘支持**：支持键盘操作（如回车提交）
- **清晰的文字**：使用易读的字体和合适的字号

### 4. 移动端适配

- **触摸友好**：按钮和交互元素要有足够的点击区域
- **响应式布局**：确保在不同屏幕尺寸下正常显示
- **性能考虑**：移动端性能有限，避免复杂计算

## 调试技巧

### 1. 使用浏览器开发者工具

- 检查控制台错误
- 调试JavaScript代码
- 检查样式问题

### 2. 测试不同设备

- 桌面浏览器
- 移动设备
- 不同屏幕尺寸

### 3. 性能分析

- 使用Performance工具分析性能
- 检查内存泄漏
- 优化渲染性能

## 常见问题

### Q: 如何添加新的交互组件？

A: 在基础模板的样式部分添加新组件的样式，然后在HTML中使用。

### Q: 如何实现数据持久化？

A: 可以使用localStorage存储用户数据，但注意数据仅在当前浏览器中有效。

### Q: 如何集成外部库？

A: 可以在HTML的`<head>`部分添加CDN链接，或下载到本地引用。

### Q: 如何优化加载速度？

A: 
- 压缩CSS和JavaScript
- 优化图片资源
- 使用CDN加速
- 减少外部依赖

## 模板选择器使用

在InteractiveCell组件中，可以使用模板选择器：

1. 点击"从模板创建"按钮
2. 浏览可用模板
3. 预览模板效果
4. 选择模板后自动加载到编辑器

## 贡献指南

如需添加新的示例模板：

1. 在 `/templates/knowledge-points/` 目录创建HTML文件
2. 遵循命名规范：`[知识点名称].html`
3. 在 `InteractiveTemplateSelector.vue` 中添加模板信息
4. 更新本文档的示例模板部分
