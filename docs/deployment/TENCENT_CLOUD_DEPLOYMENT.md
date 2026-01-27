# 腾讯云端部署指南

## 概述

在腾讯云端部署 InspireEd 平台时，需要使用生产环境配置 `docker-compose.prod.yml`，该配置包含了所有服务（PostgreSQL、Redis、MinIO、Backend、Frontend）的 Docker 容器化部署。

## 快速启动

### 方法一：使用启动脚本（推荐）

```bash
# 启动所有服务
./start-prod.sh

# 停止所有服务
./stop-prod.sh
```

### 方法二：直接使用 Docker Compose 命令

#### 如果使用旧版 Docker Compose（docker-compose）

```bash
cd docker
docker-compose -f docker-compose.prod.yml up -d
```

#### 如果使用新版 Docker Compose（docker compose）

```bash
cd docker
docker compose -f docker-compose.prod.yml up -d
```

## 常用管理命令

### 查看服务状态

```bash
# 旧版
docker-compose -f docker/docker-compose.prod.yml ps

# 新版
docker compose -f docker/docker-compose.prod.yml ps
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose -f docker/docker-compose.prod.yml logs -f

# 查看特定服务日志（如 backend）
docker-compose -f docker/docker-compose.prod.yml logs -f backend

# 查看前端日志
docker-compose -f docker/docker-compose.prod.yml logs -f frontend
```

### 重启服务

```bash
# 重启所有服务
docker-compose -f docker/docker-compose.prod.yml restart

# 重启特定服务
docker-compose -f docker/docker-compose.prod.yml restart backend
```

### 停止服务

```bash
# 停止并删除容器
docker-compose -f docker/docker-compose.prod.yml down

# 停止并删除容器和卷（⚠️ 会删除数据）
docker-compose -f docker/docker-compose.prod.yml down -v
```

### 重新构建镜像

```bash
# 重新构建并启动
docker-compose -f docker/docker-compose.prod.yml up -d --build
```

## 环境变量配置

### 前端端口配置

默认前端端口为 80，如需修改：

```bash
export FRONTEND_PORT=8080
docker-compose -f docker/docker-compose.prod.yml up -d
```

### API 地址配置

如果后端 API 地址需要修改（例如使用域名），在构建前端时设置：

```bash
export VITE_API_BASE_URL=http://your-domain.com:8000/api/v1
docker-compose -f docker/docker-compose.prod.yml up -d --build frontend
```

## 服务说明

### 服务列表

- **postgres**: PostgreSQL 数据库（端口 5432）
- **redis**: Redis 缓存（端口 6379）
- **minio**: MinIO 对象存储（端口 9000/9001）
- **backend**: FastAPI 后端服务（端口 8000）
- **frontend**: Vue 前端应用（端口 80）

### 访问地址

- **前端应用**: http://your-server-ip 或 http://your-domain
- **后端API**: http://your-server-ip:8000
- **API文档**: http://your-server-ip:8000/docs
- **MinIO控制台**: http://your-server-ip:9001 (用户名: minioadmin, 密码: minioadmin)

## 防火墙配置

确保腾讯云安全组已开放以下端口：

- **80**: 前端 HTTP 访问
- **8000**: 后端 API 访问
- **5432**: PostgreSQL（如需要外部访问）
- **6379**: Redis（如需要外部访问）
- **9000/9001**: MinIO（如需要外部访问）

## 数据持久化

所有数据都存储在 Docker volumes 中：

- `postgres_data`: PostgreSQL 数据库数据
- `redis_data`: Redis 数据
- `minio_data`: MinIO 对象存储数据
- `backend_storage`: 后端应用存储

查看 volumes：

```bash
docker volume ls | grep inspireed
```

## 故障排查

### 检查服务健康状态

```bash
# 检查所有服务
docker-compose -f docker/docker-compose.prod.yml ps

# 检查后端健康
curl http://localhost:8000/health

# 检查前端健康
curl http://localhost/health
```

### 查看详细日志

```bash
# 查看后端日志
docker-compose -f docker/docker-compose.prod.yml logs backend

# 查看前端日志
docker-compose -f docker/docker-compose.prod.yml logs frontend

# 查看数据库日志
docker-compose -f docker/docker-compose.prod.yml logs postgres
```

### 进入容器调试

```bash
# 进入后端容器
docker exec -it inspireed-backend bash

# 进入数据库容器
docker exec -it inspireed-postgres psql -U postgres -d inspireed
```

## 数据库迁移

如果需要运行数据库迁移：

```bash
# 进入后端容器
docker exec -it inspireed-backend bash

# 运行迁移
alembic upgrade head
```

## 注意事项

1. **首次启动**：首次启动时，后端和前端镜像需要构建，可能需要较长时间
2. **资源要求**：建议至少 2GB 内存，4GB 更佳
3. **网络配置**：确保 Docker 网络 `docker_inspireed-network` 正常创建
4. **数据备份**：定期备份 Docker volumes 中的数据
5. **生产环境**：建议修改默认密码（PostgreSQL、Redis、MinIO）

## 与开发环境的区别

| 项目 | 开发环境 (docker-compose.yml) | 生产环境 (docker-compose.prod.yml) |
|------|------------------------------|-----------------------------------|
| 服务 | 仅基础服务（DB、Redis、MinIO） | 包含所有服务（DB、Redis、MinIO、Backend、Frontend） |
| 启动方式 | 本地运行后端和前端 | 全部容器化 |
| 端口 | 前端 5173，后端 8000 | 前端 80，后端 8000 |
| 用途 | 本地开发调试 | 生产部署 |

