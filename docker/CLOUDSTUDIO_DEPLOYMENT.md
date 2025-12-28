# CloudStudio 部署指南

本文档说明如何在腾讯云 CloudStudio 环境中部署 InspireEd 平台。

## 🎯 重要说明

**CloudStudio 已经预装了 Docker 和 Docker Compose**，您无需手动安装！可以直接使用。

### 验证 Docker 环境

在 CloudStudio 终端中运行以下命令验证 Docker 是否可用：

```bash
# 检查 Docker 版本
docker --version

# 检查 Docker Compose 版本
docker-compose --version

# 检查 Docker 服务状态
docker info
```

如果以上命令都能正常运行，说明 Docker 环境已经准备就绪。

## 📋 前置要求

1. **CloudStudio 工作空间**：建议选择 "Python + Docker" 或 "Node.js + Docker" 预配置环境
2. **项目代码**：确保已将项目代码克隆或上传到 CloudStudio 工作空间
3. **端口访问**：CloudStudio 会自动分配公网访问地址，无需手动配置端口映射

## 🚀 快速部署步骤

### 步骤 1：进入项目目录

```bash
cd /workspace/inspireed-platform-main  # 根据实际路径调整
```

### 步骤 2：配置环境变量

进入 `docker` 目录，创建 `.env` 文件：

```bash
cd docker
```

#### 🔑 生成 SECRET_KEY（重要）

`SECRET_KEY` 用于 JWT token 的加密签名，必须是一个随机且足够长的字符串（建议至少 32 字符）。

**推荐方法：使用 OpenSSL 生成（最简单）**

```bash
# 生成一个 64 字符的随机十六进制字符串（推荐）
openssl rand -hex 32

# 或者生成一个 32 字节的 base64 编码字符串
openssl rand -base64 32
```

**其他生成方法：**

```bash
# 方法 2：使用 Python（如果已安装 Python）
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 方法 3：使用 Python 生成十六进制字符串
python3 -c "import secrets; print(secrets.token_hex(32))"

# 方法 4：使用 Node.js（如果已安装 Node.js）
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

**⚠️ 重要提示**：
- 请将生成的 SECRET_KEY 复制保存，稍后在 `.env` 文件中使用
- SECRET_KEY 一旦设置，请妥善保管，不要泄露
- 如果 SECRET_KEY 丢失或更改，所有已签发的 JWT token 将失效

#### 创建 .env 文件

使用生成的 SECRET_KEY 创建 `.env` 文件：

```bash
# 如果您已经生成了 SECRET_KEY，请将下面的 YOUR_SECRET_KEY_HERE 替换为实际生成的密钥

cat > .env << 'EOF'
# PostgreSQL 配置
POSTGRES_USER=postgres
POSTGRES_PASSWORD=inspireed2024
POSTGRES_DB=inspireed
POSTGRES_PORT=5432

# Redis 配置
REDIS_PASSWORD=inspireed_redis_2024
REDIS_PORT=6379

# MinIO 配置
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=inspireed_minio_2024
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001
MINIO_BUCKET_NAME=inspireed

# 后端配置
BACKEND_PORT=8000
SECRET_KEY=yolmbSnH4vKVDZKayXyrbIhWV3R_1ePWn8ic6jAoWjA # ⚠️ 请替换为使用 openssl rand -hex 32 生成的密钥
BACKEND_CORS_ORIGINS=["http://localhost","http://localhost:80","http://localhost:5173"]
ALLOW_LAN_ACCESS=true

# 前端配置
FRONTEND_PORT=80
VITE_API_BASE_URL=http://localhost:8000/api/v1
EOF
```

**或者，您可以直接在命令行中生成并写入文件：**

```bash
# 生成 SECRET_KEY 并写入 .env 文件
SECRET_KEY=$(openssl rand -hex 32)

cat > .env << EOF
# PostgreSQL 配置
POSTGRES_USER=postgres
POSTGRES_PASSWORD=inspireed2024
POSTGRES_DB=inspireed
POSTGRES_PORT=5432

# Redis 配置
REDIS_PASSWORD=inspireed_redis_2024
REDIS_PORT=6379

# MinIO 配置
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=inspireed_minio_2024
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001
MINIO_BUCKET_NAME=inspireed

# 后端配置
BACKEND_PORT=8000
SECRET_KEY=${SECRET_KEY}
BACKEND_CORS_ORIGINS=["http://localhost","http://localhost:80","http://localhost:5173"]
ALLOW_LAN_ACCESS=true

# 前端配置
FRONTEND_PORT=80
VITE_API_BASE_URL=http://localhost:8000/api/v1
EOF

# 显示生成的 SECRET_KEY（请妥善保存）
echo "✅ SECRET_KEY 已生成并保存到 .env 文件"
echo "🔑 请妥善保存此 SECRET_KEY: ${SECRET_KEY}"
```

**⚠️ 重要提示**：请务必修改 `.env` 文件中的所有默认密码和密钥，使用强密码保护您的服务！

### 步骤 3：启动基础服务（推荐先启动数据库等基础服务）

```bash
# 启动 PostgreSQL, Redis, MinIO 等基础服务
docker-compose up -d

# 等待服务启动（约 10-15 秒）
sleep 15

# 检查服务状态
docker-compose ps
```

### 步骤 4：启动完整服务（包含后端和前端）

```bash
# 构建并启动所有服务（包括后端和前端）
docker-compose -f docker-compose.prod.yml up -d --build

# 查看所有服务状态
docker-compose -f docker-compose.prod.yml ps
```

### 步骤 5：运行数据库迁移

**重要**：数据库迁移是必需的，用于创建和更新数据库表结构。

```bash
# 方法 1：使用迁移脚本（推荐）
cd docker
./run-migration.sh

# 方法 2：手动运行迁移
# 等待后端服务完全启动
sleep 20

# 运行数据库迁移
docker exec inspireed-backend alembic upgrade head
```

**验证迁移**：
```bash
# 查看当前数据库版本
docker exec inspireed-backend alembic current

# 查看迁移历史
docker exec inspireed-backend alembic history
```

### 步骤 6：查看服务日志

```bash
# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f postgres
```

### 步骤 7：访问服务

CloudStudio 会自动为运行的服务分配访问地址：

1. **前端访问**：在 CloudStudio 的 "端口" 面板中，找到端口 `80` 的访问地址
2. **后端 API**：找到端口 `8000` 的访问地址，访问 `/api/v1/docs` 查看 API 文档
3. **MinIO 控制台**：找到端口 `9001` 的访问地址（用户名：minioadmin，密码：您在 .env 中配置的密码）

## 🔧 CloudStudio 特定配置

### 端口访问配置

CloudStudio 的端口访问方式与本地不同：

1. **自动端口转发**：CloudStudio 会自动为容器暴露的端口创建公网访问地址
2. **查看端口**：在 CloudStudio 界面左侧的 "端口" 面板中查看所有端口及其访问地址
3. **CORS 配置**：如果前端需要访问后端 API，请确保 `BACKEND_CORS_ORIGINS` 中包含 CloudStudio 分配的前端地址

### 更新 CORS 配置

如果前端和后端不在同一域名下，需要更新后端 CORS 配置：

```bash
# 编辑 .env 文件
cd docker
vim .env

# 更新 BACKEND_CORS_ORIGINS，添加 CloudStudio 分配的前端地址
# 例如：BACKEND_CORS_ORIGINS=["http://your-frontend-url.cloudstudio.net","http://your-backend-url.cloudstudio.net"]

# 重启后端服务
docker-compose -f docker-compose.prod.yml restart backend
```

### 数据持久化

CloudStudio 的数据持久化策略：

1. **数据卷**：Docker 数据卷会保存在 CloudStudio 工作空间中
2. **数据备份**：建议定期导出数据库和数据卷，防止数据丢失
3. **数据恢复**：如需要，可以从备份恢复数据

## 📝 常用操作命令

### 启动服务

```bash
cd docker
docker-compose -f docker-compose.prod.yml up -d
```

### 停止服务

```bash
cd docker
docker-compose -f docker-compose.prod.yml down
```

### 重启服务

```bash
# 重启所有服务
docker-compose -f docker-compose.prod.yml restart

# 重启特定服务
docker-compose -f docker-compose.prod.yml restart backend
docker-compose -f docker-compose.prod.yml restart frontend
```

### 查看服务状态

```bash
docker-compose -f docker-compose.prod.yml ps
```

### 进入容器

```bash
# 进入后端容器
docker exec -it inspireed-backend bash

# 进入前端容器
docker exec -it inspireed-frontend sh

# 进入数据库容器
docker exec -it inspireed-postgres psql -U postgres -d inspireed
```

### 查看日志

```bash
# 实时查看所有日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f [service_name]

# 查看最近 100 行日志
docker-compose -f docker-compose.prod.yml logs --tail=100 [service_name]
```

### 重建镜像

```bash
# 清理并重建所有镜像
docker-compose -f docker-compose.prod.yml build --no-cache

# 重启服务以使用新镜像
docker-compose -f docker-compose.prod.yml up -d
```

## 🐛 故障排查

### 问题 1：Docker 命令不可用

**解决方案**：
- CloudStudio 应该已经预装 Docker，如果不可用，请联系 CloudStudio 技术支持
- 确认您使用的是支持 Docker 的工作空间类型

### 问题 2：端口被占用

```bash
# 检查端口占用
docker ps

# 停止占用端口的容器
docker stop [container_id]
```

### 问题 3：服务启动失败

```bash
# 查看详细错误日志
docker-compose -f docker-compose.prod.yml logs [service_name]

# 检查服务健康状态
docker-compose -f docker-compose.prod.yml ps

# 检查容器资源使用情况
docker stats
```

### 问题 4：数据库连接失败

```bash
# 检查数据库容器是否正常运行
docker-compose ps postgres

# 检查数据库日志
docker-compose logs postgres

# 测试数据库连接
docker exec -it inspireed-postgres psql -U postgres -c "SELECT version();"
```

### 问题 5：数据库迁移错误 - "relation does not exist"

如果遇到类似 `relation "users" does not exist` 的错误，说明迁移文件引用了不存在的表。

**解决方案**：

迁移文件 `001_add_curriculum_system.py` 已经修复，如果仍然遇到问题，可以尝试以下方法：

1. **检查数据库是否为空**：
   ```bash
   docker exec -it inspireed-postgres psql -U postgres -d inspireed -c "\dt"
   ```

2. **如果数据库是全新的（没有任何表）**，迁移应该能够正常执行，因为修复后的迁移文件会检查表是否存在。

3. **如果仍然失败**，可以尝试手动初始化数据库表结构：
   ```bash
   # 进入后端容器
   docker exec -it inspireed-backend bash
   
   # 运行初始化（这会创建所有基础表）
   python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
   
   # 然后运行迁移（这会跳过已存在的表）
   alembic upgrade head
   ```

4. **或者重置数据库并重新迁移**（⚠️ 会删除所有数据）：
   ```bash
   # 停止服务
   docker-compose -f docker-compose.prod.yml down
   
   # 删除数据卷
   docker volume rm inspireed-platform-main_postgres_data
   
   # 重新启动服务
   docker-compose -f docker-compose.prod.yml up -d
   
   # 等待数据库启动
   sleep 10
   
   # 运行迁移
   docker exec inspireed-backend alembic upgrade head
   ```

### 问题 6：前端无法访问后端 API

1. **检查后端服务是否运行**：
   ```bash
   docker-compose ps backend
   ```

2. **检查 CORS 配置**：
   - 确保 `BACKEND_CORS_ORIGINS` 包含前端访问地址
   - 重启后端服务使配置生效

3. **检查网络连接**：
   ```bash
   # 从前端容器测试后端连接
   docker exec inspireed-frontend wget -O- http://backend:8000/health
   ```

### 问题 7：后端容器无法启动（unhealthy）

如果后端容器状态为 `unhealthy` 或无法启动，请按以下步骤排查：

**快速诊断**：
```bash
# 运行诊断脚本
cd docker
./diagnose-backend.sh
```

**手动排查步骤**：

1. **查看后端日志**：
   ```bash
   docker logs inspireed-backend --tail 100
   ```

2. **检查依赖服务**：
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```
   确保 PostgreSQL、Redis、MinIO 都是 `Healthy` 状态

3. **检查环境变量**：
   ```bash
   docker exec inspireed-backend env | grep -E "POSTGRES|REDIS|MINIO"
   ```
   应该看到：
   - `POSTGRES_SERVER=postgres`（不是 localhost）
   - `REDIS_HOST=redis`（不是 localhost）
   - `MINIO_ENDPOINT=minio:9000`

4. **测试健康端点**：
   ```bash
   docker exec inspireed-backend python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"
   ```

5. **重启服务**：
   ```bash
   docker-compose -f docker-compose.prod.yml restart backend
   # 等待 60-90 秒让健康检查通过
   sleep 90
   docker-compose -f docker-compose.prod.yml ps
   ```

**常见原因**：
- 数据库连接失败：检查 `POSTGRES_SERVER` 环境变量
- 健康检查超时：已优化为 60s 启动等待时间
- 应用启动失败：查看日志找出具体错误

**详细修复指南**：请参考 [CLOUDSTUDIO_BACKEND_FIX.md](./CLOUDSTUDIO_BACKEND_FIX.md)

### 问题 8：磁盘空间不足

```bash
# 查看磁盘使用情况
df -h

# 清理未使用的 Docker 资源
docker system prune -a

# 清理未使用的数据卷（⚠️ 危险操作，会删除数据）
docker volume prune
```

## 🔒 安全建议

1. **修改默认密码**：确保 `.env` 文件中的所有默认密码都已修改
2. **使用强密码**：密码至少 16 位，包含大小写字母、数字和特殊字符
3. **保护 SECRET_KEY**：
   - 使用 `openssl rand -hex 32` 生成随机 SECRET_KEY
   - SECRET_KEY 应该至少 32 字符（推荐 64 字符）
   - 妥善保管 SECRET_KEY，不要泄露或提交到版本控制系统
   - 生产环境必须使用随机生成的 SECRET_KEY，不要使用示例值
   - 如果 SECRET_KEY 泄露，立即更换并重新部署
4. **限制访问**：CloudStudio 的端口访问通常需要权限验证，确保只有授权用户可访问
5. **定期更新**：定期更新 Docker 镜像和系统依赖
6. **备份数据**：定期备份数据库和重要数据
7. **环境变量安全**：确保 `.env` 文件不会被提交到 Git，已添加到 `.gitignore`

## 📚 相关文档

- [Docker 部署说明](./README.md)
- [Docker 自动启动配置](./DOCKER_AUTOSTART.md)
- [后端容器启动问题修复指南](./CLOUDSTUDIO_BACKEND_FIX.md)
- [项目 README](../README.md)

## 💡 CloudStudio 优势

使用 CloudStudio 部署的优势：

1. ✅ **无需本地环境**：直接在浏览器中开发部署
2. ✅ **预装 Docker**：开箱即用，无需安装配置
3. ✅ **自动端口转发**：自动分配公网访问地址
4. ✅ **团队协作**：支持多人协作开发
5. ✅ **环境一致性**：团队使用相同的云端环境

## 🆘 获取帮助

如遇到问题，可以：

1. 查看项目文档和日志
2. 在 CloudStudio 社区寻求帮助
3. 联系项目维护者

祝您部署顺利！🎉

