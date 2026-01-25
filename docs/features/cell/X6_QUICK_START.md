# AntV X6 快速开始 🚀

## 5 分钟上手指南

### 第 1 步: 安装依赖

```bash
cd frontend
pnpm install
```

### 第 2 步: 启用 X6 编辑器

**方式 A: 浏览器控制台（推荐，无需重启）**

1. 打开浏览器开发者工具 (F12)
2. 在控制台执行：

```javascript
localStorage.setItem('feature-flags', JSON.stringify({ 
  'use-x6-editor': true,
  'use-mindmap': true 
}))
location.reload()
```

**方式 B: 环境变量（需要重启）**

在 `frontend/.env.local` (如果不存在则创建) 中添加：

```env
VITE_USE_X6_EDITOR=true
VITE_USE_MINDMAP=true
```

然后重启开发服务器：

```bash
npm run dev
```

### 第 3 步: 验证启用

1. 打开一个课程编辑页面
2. 添加一个"流程图" Cell
3. 查看是否有新的工具栏和侧边栏

如果看到类似这样的界面，说明启用成功：

```
┌──────────────────────────────────────┐
│ [流程图] [思维导图] [撤销] [重做] ... │  ← 新工具栏
├──────┬───────────────────────────────┤
│      │                               │
│ 节点 │      画布区域                 │  ← 新侧边栏
│ 库   │                               │
│      │                               │
└──────┴───────────────────────────────┘
```

### 第 4 步: 测试功能

#### 流程图

1. 从左侧侧边栏**拖拽节点**到画布
2. **双击节点**编辑文本
3. **拖拽连接**节点之间的连线
4. 按 `Ctrl+Z` **撤销**操作

#### 思维导图

1. 点击工具栏的 **"思维导图"** 按钮
2. 拖拽一个 **"中心主题"** 到画布
3. 选中中心主题，按 **Tab** 添加子节点
4. 按 **Enter** 添加兄弟节点

#### 导出

1. 点击工具栏的 **"导出"** 按钮
2. 选择格式（PNG / SVG / JSON）
3. 下载文件

---

## 🎯 常用快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Z` | 撤销 |
| `Ctrl+Y` | 重做 |
| `Ctrl+C` | 复制 |
| `Ctrl+V` | 粘贴 |
| `Ctrl+X` | 剪切 |
| `Ctrl+A` | 全选 |
| `Delete` | 删除选中 |
| `Tab` | 添加子节点（思维导图） |
| `Enter` | 添加兄弟节点（思维导图） |

---

## 🔄 如何回退到旧版本

如果遇到问题，可以随时切换回旧版：

```javascript
// 浏览器控制台
localStorage.setItem('feature-flags', JSON.stringify({ 
  'use-x6-editor': false 
}))
location.reload()
```

---

## 🆘 遇到问题？

### 问题 1: 看不到新界面

**解决**: 清除缓存并刷新

```javascript
localStorage.clear()
location.reload(true)
```

### 问题 2: 节点拖拽不工作

**解决**: 检查浏览器兼容性，推荐使用 Chrome / Edge / Firefox 最新版

### 问题 3: 旧数据显示异常

**解决**: 数据会自动迁移，如有问题请查看控制台错误信息

---

## 📚 更多资源

- [完整迁移指南](./X6_MIGRATION_GUIDE.md)
- [配置文档](./X6_CONFIGURATION.md)
- [实施总结](./X6_IMPLEMENTATION_SUMMARY.md)

---

**准备好了吗？开始体验吧！** 🎉

