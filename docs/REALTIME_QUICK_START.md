# 活动实时互动功能 - 快速启动指南

本文档提供了活动实时互动功能的快速启动说明。

## 功能概述

✅ 已实现功能：
- 学生提交活动 → 教师实时收到通知
- 教师评分 → 学生实时收到通知
- 实时统计信息显示
- 支持课堂和课后两种模式
- 自动重连和错误恢复

## 快速开始

### 1. 启动服务

确保后端和前端服务都已启动：

```bash
# 启动后端（在 backend 目录）
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端（在 frontend 目录）
npm run dev
```

### 2. 测试流程

#### 场景 1：课堂模式（推荐先测试）

1. **教师端操作：**
   - 登录教师账号
   - 创建或进入一个课堂会话
   - 打开教师端 WebSocket 连接（自动）
   - 查看实时提交列表

2. **学生端操作：**
   - 登录学生账号
   - 加入同一课堂会话
   - 打开并完成一个活动
   - 点击提交

3. **预期结果：**
   - ✅ 教师端立即看到新提交
   - ✅ 实时统计数据自动更新
   - ✅ 教师端显示通知提示

4. **教师评分：**
   - 教师给学生评分
   - 学生端立即收到评分通知
   - 学生可以看到分数和反馈

#### 场景 2：课后模式

1. **学生端操作：**
   - 登录学生账号
   - 打开一个教案
   - 完成并提交活动

2. **教师端操作：**
   - 登录教师账号
   - 打开同一教案
   - 查看学生提交列表
   - 给学生评分

3. **预期结果：**
   - ✅ 教师端实时看到提交（如果教师在线）
   - ✅ 学生端实时收到评分通知（如果学生在线）

### 3. WebSocket 连接验证

#### 验证教师端连接

打开浏览器开发者工具（F12）-> Network -> WS，应该看到：

```
ws://localhost:8000/api/v1/classroom-sessions/sessions/{session_id}/ws/teacher?token=xxx
或
ws://localhost:8000/api/v1/classroom-sessions/lessons/{lesson_id}/ws/teacher?token=xxx
```

状态应该是 `101 Switching Protocols`。

#### 查看 WebSocket 消息

在开发者工具的 Console 中，应该看到：

```
✅ 实时通道连接成功
📨 收到实时消息: new_submission {...}
📨 收到实时消息: submission_statistics_updated {...}
```

## 常见问题

### Q1: WebSocket 连接失败

**现象：** 控制台显示 "WebSocket connection failed" 或 "401 Unauthorized"

**解决方案：**
1. 检查用户是否已登录
2. 检查 token 是否有效
3. 检查用户角色是否正确（教师/学生）
4. 检查后端服务是否正常运行

### Q2: 收不到实时通知

**现象：** 学生提交后，教师端没有反应

**解决方案：**
1. 打开浏览器开发者工具，检查 WebSocket 连接状态
2. 查看后端日志，确认消息是否发送
3. 确认教师和学生在同一个 session 或 lesson
4. 刷新页面重新建立连接

### Q3: 连接频繁断开

**现象：** WebSocket 连接不稳定，频繁重连

**解决方案：**
1. 检查网络连接是否稳定
2. 检查防火墙或代理设置
3. 如果是生产环境，确保 Nginx 配置正确支持 WebSocket
4. 增加 WebSocket 超时时间

### Q4: 多个标签页冲突

**现象：** 打开多个标签页后，某些标签页收不到消息

**这是正常的：** 每个标签页都会建立独立的连接，旧连接会被新连接替换。这是预期行为，用于防止同一用户的重复连接。

## 配置说明

### 环境变量

确保前端 `.env` 文件配置正确：

```env
VITE_API_BASE_URL=http://localhost:8000
```

WebSocket 会自动使用相同的域名，协议会根据 HTTP/HTTPS 自动选择 WS/WSS。

### 生产环境 Nginx 配置

```nginx
location /api/ {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_read_timeout 300s;  # 增加超时时间
    proxy_send_timeout 300s;
}
```

## 进一步阅读

- 📖 [完整集成指南](./REALTIME_INTEGRATION_GUIDE.md) - 详细的代码集成说明
- 📖 [实施总结](./REALTIME_IMPLEMENTATION_SUMMARY.md) - 技术架构和实施细节
- 📖 [原始设计文档](./design/ACTIVITY_REALTIME_INTERACTION.md) - 完整的设计方案

## 支持

如有问题，请：
1. 查看浏览器控制台的错误信息
2. 查看后端日志文件
3. 参考上述文档
4. 联系开发团队

---

**最后更新：** 2025-11-17  
**版本：** v1.0

