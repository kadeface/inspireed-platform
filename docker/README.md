# Docker 部署说明

本文档说明如何使用 Docker 部署 InspireEd 平台。

## 📋 文件说明

- `docker-compose.yml`: 开发环境配置（仅包含基础服务：PostgreSQL, Redis, MinIO, Kafka）
- `docker-compose.prod.yml`: 生产环境配置（包含所有服务，包括后端和前端）
- `DOCKER_AUTOSTART.md`: Docker 自动启动配置指南
- `CLOUDSTUDIO_DEPLOYMENT.md`: CloudStudio 云端 IDE 部署指南

## 🔄 自动启动配置

所有 Docker 服务已配置为 `restart: unless-stopped`，这意味着：

- ✅ 容器会在 Docker 守护进程启动时自动启动
- ✅ 容器异常退出时会自动重启
- ✅ 手动停止的容器不会自动启动

**设置系统级自动启动：**

1. **macOS 用户**：运行自动启动设置脚本
   ```bash
   ./scripts/setup-docker-autostart.sh
   ```

2. **详细说明**：查看 [DOCKER_AUTOSTART.md](./DOCKER_AUTOSTART.md) 了解完整的自动启动配置方法

## 🚀 快速开始

> 💡 **在 CloudStudio 上部署？** 请查看 [CLOUDSTUDIO_DEPLOYMENT.md](./CLOUDSTUDIO_DEPLOYMENT.md) 获取详细的 CloudStudio 部署指南。CloudStudio 已预装 Docker，无需手动安装！

### 开发环境（仅基础服务）

```bash
cd docker
docker-compose up -d
```

这将启动：
- PostgreSQL (端口 5432)
- Redis (端口 6379)
- MinIO (端口 9000/9001)
- Kafka + Zookeeper (端口 9092)

### 生产环境（完整部署）

#### 1. 配置环境变量

在 `docker/` 目录下创建 `.env` 文件：

```bash
cd docker
cat > .env << 'EOF'
# PostgreSQL 配置
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password-here
POSTGRES_DB=inspireed
POSTGRES_PORT=5432

# Redis 配置
REDIS_PASSWORD=your-redis-password-here
REDIS_PORT=6379

# MinIO 配置
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=your-minio-password-here
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001
MINIO_BUCKET_NAME=inspireed

# 后端配置
BACKEND_PORT=8000
SECRET_KEY=your-secret-key-change-in-production-make-it-long-and-random
BACKEND_CORS_ORIGINS=["http://localhost","http://localhost:80","https://yourdomain.com"]
ALLOW_LAN_ACCESS=false

# 前端配置
FRONTEND_PORT=80
VITE_API_BASE_URL=http://localhost:8000/api/v1
EOF
```

#### 2. 构建并启动所有服务

```bash
cd docker
docker-compose -f docker-compose.prod.yml up -d --build
```

#### 3. 运行数据库迁移

```bash
# 进入后端容器
docker exec -it inspireed-backend bash

# 运行迁移
alembic upgrade head

# 退出容器
exit
```

#### 4. 查看服务状态

```bash
docker-compose -f docker-compose.prod.yml ps
```

#### 5. 查看日志

```bash
# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

## 🔧 使用外部服务（阿里云 RDS/Redis/OSS）

如果你使用阿里云 RDS、Redis 或 OSS，可以修改配置：

### 1. 修改 `.env` 文件

```bash
# 使用外部 RDS
POSTGRES_SERVER=your-rds-endpoint.rds.aliyuncs.com
POSTGRES_USER=your-rds-user
POSTGRES_PASSWORD=your-rds-password
POSTGRES_DB=inspireed

# 使用外部 Redis（需要在 docker-compose.prod.yml 中注释掉 redis 服务）
# REDIS_URL=redis://:password@your-redis-endpoint:6379/0

# 使用阿里云 OSS（需要在后端代码中配置 OSS SDK，并注释掉 minio 服务）
# OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
# OSS_ACCESS_KEY_ID=your-access-key
# OSS_ACCESS_KEY_SECRET=your-secret-key
# OSS_BUCKET_NAME=inspireed-storage
```

### 2. 修改 `docker-compose.prod.yml`

注释掉不需要的服务（如 `postgres`, `redis`, `minio`），并更新后端环境变量中的连接地址。

## 📝 常用命令

### 启动服务
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 停止服务
```bash
docker-compose -f docker-compose.prod.yml down
```

### 停止并删除数据卷（⚠️ 危险操作，会删除所有数据）
```bash
docker-compose -f docker-compose.prod.yml down -v
```

### 重启服务
```bash
docker-compose -f docker-compose.prod.yml restart backend
```

### 查看服务日志
```bash
docker-compose -f docker-compose.prod.yml logs -f [service_name]
```

### 进入容器
```bash
docker exec -it inspireed-backend bash
docker exec -it inspireed-frontend sh
```

### 重建镜像
```bash
docker-compose -f docker-compose.prod.yml build --no-cache
```

## 🔒 安全建议

1. **修改默认密码**：确保所有服务的默认密码都已修改
2. **使用强密码**：密码至少 16 位，包含大小写字母、数字和特殊字符
3. **限制网络访问**：使用 Docker 网络隔离，只暴露必要的端口
4. **使用 HTTPS**：在生产环境中使用 Nginx 反向代理并配置 SSL 证书
5. **定期备份**：备份数据库和数据卷

## 🐛 故障排查

### 后端无法连接数据库

1. 检查数据库服务是否运行：`docker-compose ps`
2. 检查环境变量配置是否正确
3. 检查网络连接：`docker exec -it inspireed-backend ping postgres`

### 前端无法访问后端 API

1. 检查后端服务是否运行：`docker-compose ps`
2. 检查 `VITE_API_BASE_URL` 配置是否正确
3. 检查 CORS 配置：确保 `BACKEND_CORS_ORIGINS` 包含前端地址

### 服务启动失败

1. 查看日志：`docker-compose logs [service_name]`
2. 检查端口是否被占用：`netstat -tlnp | grep [port]`
3. 检查磁盘空间：`df -h`
4. 检查 Docker 资源限制

## 📚 参考文档

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 官方文档](https://docs.docker.com/compose/)
- [阿里云部署指南](../docs/deployment/ALIYUN_DEPLOYMENT_GUIDE.md)

