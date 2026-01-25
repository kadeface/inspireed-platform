# 课堂控制面板问题排查指南

## 常见问题

### 1. CORS 错误

**错误信息：**
```
Origin http://192.168.2.35:5173 is not allowed by Access-Control-Allow-Origin
```

**解决方法：**

1. **检查后端配置**
   - 确认 `ALLOW_LAN_ACCESS=True` 在 `.env` 文件中
   - 确认后端正在运行：`curl http://192.168.2.35:8000/health`

2. **检查后端日志**
   - 查看后端是否有500错误
   - 如果返回500，可能是数据库连接问题或其他内部错误

3. **重启后端服务**
   ```bash
   cd backend
   # 停止旧服务
   pkill -f "uvicorn app.main:app"
   # 重新启动
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### 2. cell_id=0 错误

**错误信息：**
```
Failed to load submissions: cell_id=0
```

**原因：**
- Cell ID 无法解析为数字ID
- 通常是UUID字符串无法转换为数字

**解决方法：**

1. **检查Cell ID**
   - 打开浏览器控制台
   - 查看警告信息：`⚠️ Cannot resolve cell ID to numeric ID`
   - 检查Cell对象是否有 `_dbId` 字段

2. **临时解决方法**
   - 在ActivityCell组件中已经添加了保护
   - 当cell_id=0时，会显示友好的提示而不是调用API

3. **根本解决方法**
   - 确保Cell已保存到数据库
   - 检查教案内容中Cell的数据结构

### 3. 课堂控制按钮不显示

**原因：**
- 教案状态不是 'published'
- 未切换到预览模式

**检查步骤：**

1. **检查教案状态**
   ```javascript
   // 在浏览器控制台执行
   console.log('Lesson status:', currentLesson?.status)
   // 应该是 'published'
   ```

2. **检查预览模式**
   ```javascript
   // 在浏览器控制台执行
   console.log('Preview mode:', isPreviewMode)
   // 应该是 true
   ```

3. **手动发布教案**
   - 点击"发布"按钮
   - 选择要发布的班级
   - 确认发布成功

4. **切换到预览模式**
   - 点击工具栏上的"预览模式"按钮
   - 页面应该变为只读状态

### 4. API 请求失败

**检查网络请求：**

1. **打开浏览器开发者工具**
   - F12 → Network 标签

2. **查看失败的请求**
   - 检查请求URL是否正确
   - 检查响应状态码
   - 查看响应内容

3. **检查后端日志**
   - 查看后端终端输出
   - 查找错误堆栈信息

### 5. 数据库迁移未完成

**检查迁移状态：**
```bash
cd backend
alembic current
```

**应用迁移：**
```bash
cd backend
alembic upgrade head
```

## 调试技巧

### 1. 查看组件状态

在浏览器控制台：
```javascript
// 查看Vue组件（需要Vue DevTools）
// 或者通过window对象（如果组件暴露了）
```

### 2. 手动触发功能

如果按钮不显示，可以手动在控制台执行：
```javascript
// 切换到预览模式
isPreviewMode = true

// 显示控制面板
showClassroomPanel = true
```

### 3. 检查API端点

测试后端API：
```bash
# 测试健康检查
curl http://192.168.2.35:8000/health

# 测试课堂会话API（需要token）
curl -X GET http://192.168.2.35:8000/api/v1/classroom-sessions/lessons/1/sessions \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. 查看后端日志

```bash
# 查看后端日志
tail -f logs/backend.log

# 或者直接查看终端输出
```

## 常见错误代码

### 500 Internal Server Error

**可能原因：**
- 数据库连接失败
- SQL语法错误
- 未捕获的异常

**解决方法：**
1. 检查数据库连接
2. 查看后端日志
3. 检查数据库迁移状态

### 404 Not Found

**可能原因：**
- API路由未注册
- URL路径错误
- 资源不存在

**解决方法：**
1. 检查路由配置
2. 确认API端点正确
3. 检查数据库中的数据

### 403 Forbidden

**可能原因：**
- 权限不足
- Token无效
- 角色不匹配

**解决方法：**
1. 检查用户角色
2. 重新登录获取新token
3. 检查权限配置

## 联系支持

如果以上方法都无法解决问题，请提供：

1. 浏览器控制台的完整错误信息
2. 后端日志的错误堆栈
3. 网络请求的详细信息（URL、请求头、响应）
4. 系统环境信息（操作系统、浏览器版本、Node版本等）

