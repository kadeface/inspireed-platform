# 活动提交面板显示问题排查指南

## 问题描述
教师端在课堂模式下，点击"开始活动"后，活动提交面板没有显示。

## 显示条件

活动提交面板需要同时满足以下三个条件才会显示：

1. ✅ **会话已创建**：`session` 存在
2. ✅ **活动已启动**：`session.current_activity_id` 存在
3. ✅ **能找到活动Cell**：`currentActivityCell` 存在

## 排查步骤

### 步骤 1: 检查会话状态

1. 打开课堂控制面板
2. 确认已点击 **"开始上课"** 按钮
3. 状态栏应该显示 "上课中"

### 步骤 2: 导航到活动模块

1. 在导播台中找到类型为 **"活动"** 的模块（紫色图标 📋）
2. 点击该模块节点
3. 确认该模块被高亮选中（蓝色背景）

### 步骤 3: 启动活动

1. 在导播台下方的"当前模块详情"区域
2. 应该显示 **"🎯 开始活动"** 按钮
3. 点击该按钮启动活动

### 步骤 4: 查看调试信息

打开浏览器开发者工具（F12），查看控制台输出：

#### 正常情况应该看到：

```
🎬 ClassroomControlBoard.handleStartActivity 被调用
📋 当前 Cell 信息: { cellId: 123, cellType: "activity", ... }
✅ 发送 startActivity 事件, cellId: 123
🎯 handleStartActivity 被调用 { ... }
📤 准备启动活动，Cell ID: 123
✅ 活动启动成功 { currentActivityId: 123, ... }
📊 活动提交面板应该显示了，检查条件: { ... }
🔍 计算 currentActivityCell { ... }
✅ 找到活动 Cell
```

#### 如果看到错误：

##### 错误 1: "❌ Cell ID 无效"
```
❌ Cell ID 无效，无法启动活动
```

**原因**：活动 Cell 的 ID 不是数字（可能是 UUID），或者该 Cell 还未保存到数据库。

**解决方法**：
1. 在教案编辑器中点击 **"保存"** 按钮
2. 等待保存成功提示
3. 刷新页面
4. 重新进入课堂模式

##### 错误 2: "❌ 未找到匹配的活动 Cell"
```
❌ 未找到匹配的活动 Cell
```

**原因**：`session.current_activity_id` 与教案中的活动 Cell ID 不匹配。

**解决方法**：
1. 查看控制台中打印的所有 Cell 信息
2. 对比 `activityId` 和每个 Cell 的 `id`
3. 如果 ID 不匹配，可能是教案内容与数据库不同步
4. 尝试重新保存教案

##### 错误 3: "❌ 无法确定要启动的活动 Cell ID"
```
❌ 无法确定要启动的活动 Cell ID
```

**原因**：当前没有选中任何 Cell，或者 `session.current_cell_id` 为空。

**解决方法**：
1. 在导播台中点击活动模块
2. 确保该模块被选中（蓝色背景）
3. 然后点击"开始活动"按钮

## 检查网络请求

### 使用浏览器开发者工具

1. 打开 **Network（网络）** 标签
2. 点击"开始活动"按钮
3. 查找以下请求：

#### POST `/api/v1/classroom-sessions/{session_id}/start-activity`

**请求体**：
```json
{
  "cellId": 123
}
```

**成功响应** (200 OK)：
```json
{
  "id": 1,
  "status": "active",
  "current_cell_id": 123,
  "current_activity_id": 123,  // ← 这个字段必须存在且与 cellId 相同
  ...
}
```

**失败响应**：
- 404: Cell 不存在
- 400: Cell 类型不是 activity
- 403: 权限不足

### 检查提交列表请求

活动启动后，会自动请求提交列表：

#### GET `/api/v1/activities/cells/{cell_id}/submissions`

**成功响应** (200 OK)：
```json
[
  {
    "id": 1,
    "student_name": "张三",
    "status": "submitted",
    "score": 85,
    ...
  }
]
```

如果这个请求失败或返回 403，说明权限配置有问题。

## 常见问题

### Q: 我点击了"开始活动"，但是没有任何反应

**A**: 检查以下几点：

1. 浏览器控制台是否有错误信息？
2. Network 标签中请求是否成功？
3. 是否先选中了活动模块？

### Q: 活动按钮是灰色的，无法点击

**A**: 这通常意味着：

1. 正在加载中 (`loading` 状态)
2. 当前选中的不是活动类型的 Cell
3. 会话状态异常

### Q: 显示了面板，但是提交列表为空

**A**: 这是正常的，说明：

1. 活动已成功启动
2. 还没有学生提交答案
3. 面板会每 10 秒自动刷新

### Q: Cell ID 是 UUID 怎么办？

**A**: 如果教案中的 Cell ID 是 UUID 格式（例如 `"550e8400-e29b-41d4-a716-446655440000"`），需要：

1. 先保存教案到数据库
2. 保存时会自动创建数字 ID
3. 刷新页面重新加载

## 临时解决方案

如果问题仍然存在，可以尝试：

### 方案 1: 强制刷新

1. 关闭课堂会话（点击"结束课程"）
2. 刷新浏览器页面
3. 重新"开始上课"
4. 再次尝试启动活动

### 方案 2: 清除缓存

1. 清除浏览器缓存
2. 退出登录并重新登录
3. 重新进入课堂模式

### 方案 3: 检查教案

1. 进入教案编辑器
2. 确认活动 Cell 存在且配置正确
3. 点击"保存"
4. 返回课堂模式

## 获取技术支持

如果以上方法都无法解决问题，请提供以下信息：

1. 浏览器控制台的完整错误日志（截图或复制文本）
2. Network 标签中相关请求的详细信息（Request/Response）
3. 教案 ID 和会话 ID
4. 活动 Cell 的配置信息

可以在浏览器控制台运行以下命令导出调试信息：

```javascript
// 复制这段代码到浏览器控制台执行
const debugInfo = {
  userAgent: navigator.userAgent,
  timestamp: new Date().toISOString(),
  url: window.location.href,
  // 从 localStorage 获取可能有用的信息
  localStorage: Object.keys(localStorage).reduce((acc, key) => {
    if (key.includes('session') || key.includes('user')) {
      acc[key] = localStorage.getItem(key)
    }
    return acc
  }, {})
}
console.log('调试信息:', JSON.stringify(debugInfo, null, 2))
```

然后将输出的 JSON 信息提供给技术支持人员。

