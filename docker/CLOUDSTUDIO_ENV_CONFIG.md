# CloudStudio 环境变量配置说明

## 📋 重要说明

在 CloudStudio 环境中，`docker-compose.cloudstudio.yml` 已经在 `environment:` 部分硬编码了大部分配置，这些配置会**覆盖** `.env` 文件中的值。

## 🔧 实际生效的配置

查看 `docker-compose.cloudstudio.yml` 中的 `environment:` 部分，实际生效的配置如下：

### 后端服务配置（backend）

```yaml
environment:
  # 数据库配置（Docker 网络中使用服务名）
  POSTGRES_SERVER: postgres  # ⚠️ 使用服务名，不是 localhost
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres
  POSTGRES_DB: inspireed
  POSTGRES_PORT: 5432
  
  # Redis 配置（Docker 网络中使用服务名）
  REDIS_HOST: redis  # ⚠️ 使用服务名，不是 localhost
  REDIS_PORT: 6379
  
  # MinIO 配置（Docker 网络中使用服务名）
  MINIO_ENDPOINT: minio:9000  # ⚠️ 使用服务名，不是 localhost:9000
  MINIO_SECURE: "false"
  
  # CORS 配置
  ALLOW_LAN_ACCESS: "true"
  BACKEND_CORS_ORIGINS: '["*"]'  # CloudStudio 需要允许所有来源
```

### 前端服务配置（frontend）

```yaml
environment:
  - VITE_API_BASE_URL=${VITE_API_BASE_URL:-http://localhost:8000/api/v1}
```

**⚠️ 注意**：虽然设置了 `VITE_API_BASE_URL`，但前端代码会自动检测 CloudStudio 环境并忽略 `localhost`，使用正确的 CloudStudio URL。

## 📝 推荐的 .env 配置

如果你需要创建 `docker/.env` 文件（主要用于文档和备用），可以使用以下配置：

```bash
# PostgreSQL 配置
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=inspireed
POSTGRES_PORT=5432
POSTGRES_SERVER=postgres  # ⚠️ 使用服务名

# Redis 配置
REDIS_HOST=redis  # ⚠️ 使用服务名
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# MinIO 配置
MINIO_ENDPOINT=minio:9000  # ⚠️ 使用服务名
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=inspireed
MINIO_SECURE=false

# 后端配置
BACKEND_PORT=8000
SECRET_KEY=your-secret-key-here  # ⚠️ 使用 openssl rand -hex 32 生成
ALLOW_LAN_ACCESS=true
BACKEND_CORS_ORIGINS=["*"]

# 前端配置
FRONTEND_PORT=5173  # CloudStudio 使用 5173
# VITE_API_BASE_URL=  # 不设置，让代码自动检测
```

## ⚠️ 关键点

1. **Docker 网络中的服务名**：
   - ✅ 正确：`postgres`, `redis`, `minio:9000`
   - ❌ 错误：`localhost`, `127.0.0.1`

2. **VITE_API_BASE_URL**：
   - 建议不设置或留空，让前端代码自动检测 CloudStudio 环境
   - 即使设置了 `localhost`，代码也会自动忽略并使用正确的 URL

3. **CORS 配置**：
   - CloudStudio 环境必须设置为 `["*"]`，因为域名是动态分配的

4. **端口配置**：
   - 前端：`5173`（开发模式）
   - 后端：`8000`

## 🔍 如何验证配置

启动服务后，检查后端日志：

```bash
docker logs inspireed-backend
```

应该看到成功连接到：
- PostgreSQL: `postgres:5432`
- Redis: `redis:6379`
- MinIO: `minio:9000`

如果看到 `localhost` 或连接错误，说明配置有问题。

## 📚 相关文件

- `docker-compose.cloudstudio.yml` - CloudStudio 专用配置
- `.env.cloudstudio.example` - 配置示例文件
- `CLOUDSTUDIO_DEPLOYMENT.md` - 完整部署指南

