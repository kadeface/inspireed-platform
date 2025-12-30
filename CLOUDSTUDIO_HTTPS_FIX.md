# CloudStudio HTTPS 混合内容问题修复指南

## 问题描述

在 CloudStudio 环境中，前端使用 HTTPS 访问，但 API 请求仍使用 HTTP，导致浏览器阻止请求（Mixed Content 错误）。

错误信息：
```
Mixed Content: The page at 'https://...--5173.cloudstudio.club' was loaded over HTTPS, 
but requested an insecure XMLHttpRequest endpoint 'http://...--8000.cloudstudio.club/api/v1/...'
```

## 已实施的修复

### 1. 前端代码修复

**文件：`frontend/src/services/api.ts`**

- ✅ 强制在 CloudStudio 环境中使用 HTTPS
- ✅ 环境变量检查时也强制转换 HTTP 为 HTTPS
- ✅ 在 ApiService 构造函数中添加最终保护，自动转换 HTTP 为 HTTPS
- ✅ 添加详细的调试日志

**文件：`frontend/src/utils/url.ts`**

- ✅ 强制在 CloudStudio 环境中使用 HTTPS

### 2. 后端 CORS 配置

**文件：`docker/docker-compose.cloudstudio.yml`**

- ✅ 添加 `ALLOW_LAN_ACCESS: "true"` 确保使用正则表达式匹配 CloudStudio 域名

**文件：`backend/app/main.py`**

- ✅ 优化 CORS 逻辑，支持 `BACKEND_CORS_ORIGINS` 包含 `"*"` 时也使用正则表达式

## 解决方案

### 方法一：重新构建前端容器（推荐）

如果使用 Docker 容器运行前端：

```bash
cd docker
docker-compose -f docker-compose.cloudstudio.yml up -d --build frontend
```

### 方法二：如果使用 preview.yml 启动

如果使用 CloudStudio 的 preview.yml 启动前端：

1. **停止前端服务**（在 CloudStudio 的预览面板中停止）
2. **清除浏览器缓存**：
   - Chrome/Edge: `Ctrl+Shift+Delete` (Windows) 或 `Cmd+Shift+Delete` (Mac)
   - 选择"缓存的图片和文件"
   - 时间范围选择"全部时间"
3. **硬刷新页面**：
   - Windows: `Ctrl+F5` 或 `Ctrl+Shift+R`
   - Mac: `Cmd+Shift+R`
4. **重新启动前端服务**

### 方法三：检查环境变量

检查前端是否有 `.env.local` 文件设置了 HTTP 地址：

```bash
cd frontend
cat .env.local | grep VITE_API_BASE_URL
```

如果看到 `http://` 开头的地址，需要：
1. 删除或注释掉该配置
2. 让代码自动检测 CloudStudio 环境

或者修改为 HTTPS：

```bash
# 在 frontend/.env.local 中
VITE_API_BASE_URL=https://your-backend-id--8000.region.cloudstudio.club/api/v1
```

## 验证修复

### 1. 检查浏览器控制台

打开浏览器开发者工具（F12），查看控制台输出，应该看到：

```
🔍 [API] 检测环境 - hostname: 645cf02ac04c45c38ed3f5cceb49231b--5173.ap-shanghai2.cloudstudio.club ...
✅ [API] Cloud Studio 环境检测成功！
   前端地址: https://645cf02ac04c45c38ed3f5cceb49231b--5173.ap-shanghai2.cloudstudio.club
   后端地址: https://645cf02ac04c45c38ed3f5cceb49231b--8000.ap-shanghai2.cloudstudio.club/api/v1
🚀 [API] 最终使用的 API 基础地址: https://645cf02ac04c45c38ed3f5cceb49231b--8000.ap-shanghai2.cloudstudio.club/api/v1
```

**不应该看到**：
- ❌ `http://` 开头的地址
- ❌ 混合内容警告

### 2. 检查网络请求

在浏览器开发者工具的 Network 标签中：
1. 刷新页面
2. 查看 API 请求
3. 确认请求 URL 使用 `https://` 而不是 `http://`

### 3. 测试登录

1. 访问登录页面
2. 输入账号密码登录
3. 应该能正常登录，不再出现混合内容错误

## 故障排查

### 如果仍然出现混合内容错误

1. **检查代码是否已更新**：
   ```bash
   # 在 CloudStudio 中检查
   cat frontend/src/services/api.ts | grep -A 5 "强制使用 HTTPS"
   ```
   应该看到 `const apiUrl = \`https://${backendHostname}/api/v1\``

2. **检查前端容器是否使用最新代码**：
   ```bash
   # 查看前端容器日志
   docker logs inspireed-frontend --tail 50
   ```

3. **强制清除浏览器缓存**：
   - 使用无痕/隐私模式打开页面
   - 或者清除所有缓存和 Cookie

4. **检查环境变量**：
   ```bash
   # 检查是否有环境变量覆盖
   docker exec inspireed-frontend env | grep VITE_API_BASE_URL
   ```

### 如果环境变量设置了 HTTP 地址

如果 `.env.local` 或 Docker 环境变量中设置了 `VITE_API_BASE_URL=http://...`：

1. **删除或修改环境变量**（推荐）
2. **或者代码会自动转换**（已添加保护）

## 代码保护机制

代码现在有多层保护：

1. **第一层**：在 `getApiBaseUrl()` 中，CloudStudio 环境强制使用 HTTPS
2. **第二层**：环境变量检查时，如果是 CloudStudio 环境，自动转换 HTTP 为 HTTPS
3. **第三层**：在 `ApiService` 构造函数中，再次检查并转换 HTTP 为 HTTPS

即使环境变量设置了 HTTP，代码也会自动转换为 HTTPS。

## 相关文件

- `frontend/src/services/api.ts` - API 服务配置
- `frontend/src/utils/url.ts` - URL 工具函数
- `docker/docker-compose.cloudstudio.yml` - CloudStudio Docker 配置
- `backend/app/main.py` - 后端 CORS 配置

## 注意事项

1. **必须重新构建前端容器**才能使代码更改生效
2. **清除浏览器缓存**很重要，浏览器可能缓存了旧的 JavaScript 文件
3. **检查环境变量**，确保没有设置 HTTP 地址覆盖自动检测

