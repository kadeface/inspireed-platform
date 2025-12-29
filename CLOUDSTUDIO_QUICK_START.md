# CloudStudio 快速启动指南

## 问题说明

在 CloudStudio 环境中，如果使用 `docker-compose.prod.yml`（生产环境配置），会遇到以下问题：

1. **前端端口不匹配**：生产环境使用端口 80，但 CloudStudio 需要端口 5173
2. **前端容器 unhealthy**：健康检查可能失败
3. **访问地址错误**：CloudStudio 的端口转发需要特定的端口号

## 解决方案

### 方法一：使用 CloudStudio 专用配置（推荐）

我们提供了专门为 CloudStudio 环境优化的配置：

```bash
# 使用 CloudStudio 专用启动脚本
./start-cloudstudio.sh
```

这个脚本会：
- 使用 `docker-compose.cloudstudio.yml` 配置
- 前端使用开发模式（端口 5173，支持热重载）
- 自动配置 CORS 以支持 CloudStudio 的域名
- 优化健康检查配置

### 方法二：手动使用 CloudStudio 配置

```bash
cd docker
docker-compose -f docker-compose.cloudstudio.yml up -d --build
```

## 配置说明

### docker-compose.cloudstudio.yml 的特点

1. **前端使用开发模式**：
   - 使用 `Dockerfile.dev`（Vite 开发服务器）
   - 端口映射：`5173:5173`
   - 支持热重载和实时更新

2. **后端 CORS 配置**：
   - 允许所有来源：`BACKEND_CORS_ORIGINS: '["*"]'`
   - 适配 CloudStudio 的动态域名

3. **健康检查优化**：
   - 增加启动等待时间
   - 优化重试次数

## 访问地址

启动后，在 CloudStudio 的 "端口" 面板中查看：

- **前端**：端口 5173 的访问地址
  - 格式：`https://{id}--5173.{region}.cloudstudio.club`
- **后端**：端口 8000 的访问地址
  - 格式：`https://{id}--8000.{region}.cloudstudio.club`
  - API 文档：`https://{id}--8000.{region}.cloudstudio.club/docs`

## 前端自动配置

前端代码已经自动支持 CloudStudio 环境：

- 自动检测 CloudStudio 域名（包含 `cloudstudio.club`）
- 自动将前端 URL 的端口号从 5173 替换为 8000 来访问后端
- 例如：前端 `--5173` → 后端 `--8000`

## 常见问题

### 1. 前端无法访问

**检查步骤**：
```bash
# 查看前端容器状态
cd docker
docker-compose -f docker-compose.cloudstudio.yml ps frontend

# 查看前端日志
docker-compose -f docker-compose.cloudstudio.yml logs frontend

# 检查端口是否正确映射
docker-compose -f docker-compose.cloudstudio.yml ps | grep 5173
```

**解决方案**：
- 确保使用 `docker-compose.cloudstudio.yml` 而不是 `docker-compose.prod.yml`
- 检查 CloudStudio 端口面板中是否有端口 5173 的访问地址
- 等待前端容器完全启动（可能需要 1-2 分钟）

### 2. 前端无法连接后端

**检查步骤**：
```bash
# 检查后端是否正常运行
curl http://localhost:8000/health

# 检查前端日志中的 API 地址
docker-compose -f docker-compose.cloudstudio.yml logs frontend | grep API
```

**解决方案**：
- 前端会自动检测 CloudStudio 环境并配置正确的 API 地址
- 如果仍有问题，可以手动设置环境变量：
  ```bash
  export VITE_API_BASE_URL=https://your-backend-id--8000.region.cloudstudio.club/api/v1
  cd docker
  docker-compose -f docker-compose.cloudstudio.yml up -d --build frontend
  ```

### 3. 容器状态为 unhealthy

**检查步骤**：
```bash
# 查看容器详细状态
docker inspect inspireed-frontend | grep -A 10 Health

# 手动测试健康检查
docker exec inspireed-frontend wget --quiet --spider http://localhost:5173
```

**解决方案**：
- 等待更长时间（健康检查有启动等待期）
- 检查容器日志查看具体错误
- 如果持续失败，可以临时禁用健康检查进行调试

## 停止服务

```bash
cd docker
docker-compose -f docker-compose.cloudstudio.yml down
```

## 重启服务

```bash
cd docker
docker-compose -f docker-compose.cloudstudio.yml restart
```

## 查看日志

```bash
# 查看所有服务日志
cd docker
docker-compose -f docker-compose.cloudstudio.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.cloudstudio.yml logs -f frontend
docker-compose -f docker-compose.cloudstudio.yml logs -f backend
```

## 与生产环境的区别

| 项目 | 生产环境 (docker-compose.prod.yml) | CloudStudio (docker-compose.cloudstudio.yml) |
|------|-----------------------------------|---------------------------------------------|
| 前端端口 | 80 | 5173 |
| 前端模式 | 生产构建（Nginx） | 开发模式（Vite） |
| 热重载 | 不支持 | 支持 |
| CORS | 需要配置具体域名 | 允许所有来源 |
| 适用场景 | 正式生产部署 | CloudStudio 开发/演示 |

## 推荐工作流程

1. **开发阶段**：使用 `start-cloudstudio.sh` 启动，支持热重载
2. **生产部署**：使用 `start-prod.sh` 启动，使用生产构建

## 获取帮助

如果遇到问题：
1. 查看容器日志：`docker-compose -f docker-compose.cloudstudio.yml logs`
2. 检查服务状态：`docker-compose -f docker-compose.cloudstudio.yml ps`
3. 参考 [CLOUDSTUDIO_DEPLOYMENT.md](./docker/CLOUDSTUDIO_DEPLOYMENT.md) 获取更多信息

