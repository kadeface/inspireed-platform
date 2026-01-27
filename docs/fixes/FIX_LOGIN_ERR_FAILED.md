# 修复 CloudStudio 登录 ERR_FAILED 错误

## 错误信息

```
POST https://645cf02ac04c45c38ed3f5cceb49231b--8000.ap-shanghai2.cloudstudio.club/api/v1/auth/login net::ERR_FAILED
```

## 可能的原因

1. **后端服务未运行**
   - 后端服务没有启动
   - 后端服务崩溃或停止

2. **网络连接问题**
   - 端口 8000 被其他进程占用
   - 防火墙阻止了连接
   - CloudStudio 网络配置问题

3. **CORS 配置问题**
   - CORS 预检请求失败
   - 后端没有正确响应 OPTIONS 请求

4. **后端服务配置问题**
   - 环境变量配置错误
   - 数据库连接失败
   - 服务启动失败

## 快速诊断

运行诊断脚本：

```bash
bash scripts/diagnose-login-issue.sh
```

## 解决方案

### 方案一：检查后端服务是否运行

```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 如果返回错误，后端服务未运行
```

**解决方法**：
1. 使用 CloudStudio 预览功能启动后端服务
2. 或手动运行：`bash .vscode/start-backend-cloudstudio.sh`

### 方案二：检查端口占用

```bash
# 检查端口 8000 是否被占用
lsof -i :8000

# 如果被占用，停止占用进程
kill $(lsof -ti:8000)
```

### 方案三：检查 Docker 容器

如果使用 Docker 运行后端：

```bash
# 检查容器状态
docker ps | grep inspireed-backend

# 如果容器未运行，启动容器
cd docker
docker-compose -f docker-compose.cloudstudio.yml up -d backend

# 查看容器日志
docker logs inspireed-backend -f
```

### 方案四：检查 CORS 配置

```bash
# 测试 CORS 预检请求
curl -X OPTIONS \
  -H "Origin: https://645cf02ac04c45c38ed3f5cceb49231b--5173.ap-shanghai2.cloudstudio.club" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  -v http://localhost:8000/api/v1/auth/login
```

**如果 CORS 配置有问题**：
1. 检查 `backend/.env` 文件：
   ```bash
   ALLOW_LAN_ACCESS=true
   ```
2. 重启后端服务使配置生效

### 方案五：查看后端日志

```bash
# 如果使用 Docker
docker logs inspireed-backend -f

# 如果直接运行 Python
# 查看启动脚本的输出或终端日志
```

查找以下错误：
- `❌` 或 `ERROR` - 错误信息
- `CORS` - CORS 相关日志
- `Exception` - 异常信息

## 常见问题

### Q: 后端服务启动后立即停止

**可能原因**：
- 数据库连接失败
- 环境变量配置错误
- 端口被占用

**解决方法**：
1. 检查 `backend/.env` 配置
2. 确保数据库服务运行
3. 检查端口占用情况

### Q: CORS 预检请求失败

**可能原因**：
- `ALLOW_LAN_ACCESS` 未设置为 `true`
- 正则表达式不匹配 CloudStudio 域名

**解决方法**：
1. 确保 `backend/.env` 中 `ALLOW_LAN_ACCESS=true`
2. 重启后端服务

### Q: 网络连接超时

**可能原因**：
- CloudStudio 网络配置问题
- 后端服务监听地址不正确

**解决方法**：
1. 确保后端服务监听 `0.0.0.0:8000`（不是 `127.0.0.1:8000`）
2. 检查 CloudStudio 网络设置

## 验证修复

修复后，验证以下内容：

1. **后端健康检查**：
   ```bash
   curl http://localhost:8000/health
   ```
   应该返回 `{"status":"ok"}`

2. **CORS 预检请求**：
   ```bash
   curl -X OPTIONS \
     -H "Origin: https://your-frontend-url.cloudstudio.club" \
     -H "Access-Control-Request-Method: POST" \
     -v http://localhost:8000/api/v1/auth/login
   ```
   应该返回 `Access-Control-Allow-Origin` 头

3. **登录请求**：
   在浏览器中尝试登录，应该不再出现 `ERR_FAILED` 错误

## 相关文件

- `scripts/diagnose-login-issue.sh` - 诊断脚本
- `.vscode/start-backend-cloudstudio.sh` - 后端启动脚本
- `backend/app/main.py` - 后端主应用（CORS 配置）
- `backend/.env` - 后端环境配置

## 获取帮助

如果问题仍然存在：

1. 运行诊断脚本并查看输出
2. 检查后端日志中的错误信息
3. 确认所有服务都已正确启动
4. 检查 CloudStudio 的网络配置

