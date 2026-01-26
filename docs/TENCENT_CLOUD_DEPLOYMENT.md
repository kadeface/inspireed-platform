# 腾讯云服务器部署指南

本文档说明如何将 InspireEd 平台部署到腾讯轻量云服务器。

## 📋 前置要求

### 服务器配置建议
- **CPU**: 2核及以上
- **内存**: 4GB 及以上
- **硬盘**: 40GB 及以上（SSD推荐）
- **操作系统**: Ubuntu 20.04/22.04 或 CentOS 7/8

### 需要安装的软件
```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

## 🚀 部署步骤

### 1. 准备服务器环境

```bash
# SSH 登录到服务器
ssh root@your-server-ip

# 安装 Git（如果没有）
sudo apt update && sudo apt install -y git  # Ubuntu/Debian
# 或
sudo yum install -y git  # CentOS

# 克隆代码（首次部署）
git clone <your-repository-url> inspireed-platform
cd inspireed-platform

# 或者如果是已有代码，拉取最新版本
cd inspireed-platform
git checkout dev
git pull origin dev
```

### 2. 配置生产环境变量

```bash
# 复制示例配置文件
cp backend/.env backend/.env.prod

# 编辑生产环境配置
nano backend/.env.prod  # 或使用 vim
```

**重要配置项**：
- ✅ `SECRET_KEY`: 已自动生成（不要修改）
- ✅ `POSTGRES_PASSWORD`: 已自动生成（不要修改）
- ✅ `MINIO_SECRET_KEY`: 已自动生成（不要修改）
- ⚠️ `OPENAI_API_KEY`: 替换为你自己的 API Key
- ⚠️ `FIRST_SUPERUSER_PASSWORD`: 首次登录后立即修改

### 3. 运行部署脚本

```bash
# 确保脚本有执行权限
chmod +x deploy-to-tencent-cloud.sh

# 运行部署
./deploy-to-tencent-cloud.sh
```

部署脚本会自动执行以下操作：
1. ✓ 检查系统依赖（Docker, Docker Compose）
2. ✓ 拉取最新代码
3. ✓ 停止旧容器
4. ✓ 构建 Docker 镜像
5. ✓ 启动所有服务
6. ✓ 等待健康检查
7. ✓ 初始化数据库（首次部署）

### 4. 访问应用

部署完成后，可以通过以下地址访问：

- **前端**: http://your-server-ip
- **后端 API**: http://your-server-ip:8000
- **API 文档**: http://your-server-ip:8000/docs

**默认管理员账号**：
- Email: admin@inspireed.com
- Password: admin123

⚠️ **首次登录后请立即修改密码！**

## 🔄 更新部署

当代码有更新时，只需重新运行部署脚本：

```bash
cd ~/inspireed-platform
git pull origin dev
./deploy-to-tencent-cloud.sh
```

## 📊 服务管理

### 查看服务状态
```bash
cd docker
docker-compose -f docker-compose.prod.yml ps
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f postgres
```

### 重启服务
```bash
cd docker
docker-compose -f docker-compose.prod.yml restart
```

### 停止服务
```bash
cd docker
docker-compose -f docker-compose.prod.yml down
```

### 完全清理（包括数据卷）
```bash
cd docker
docker-compose -f docker-compose.prod.yml down -v
```

⚠️ **警告**: `-v` 会删除所有数据，仅用于完全重置！

## 🔧 故障排查

### 服务无法启动
```bash
# 查看容器日志
docker logs inspireed-backend
docker logs inspireed-frontend
docker logs inspireed-postgres
```

### 数据库连接失败
```bash
# 检查数据库是否健康
docker exec inspireed-postgres pg_isready -U postgres

# 查看数据库日志
docker logs inspireed-postgres
```

### 端口被占用
```bash
# 查看端口占用
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :80

# 如果被占用，停止占用进程或修改 docker-compose.prod.yml 中的端口映射
```

### 数据库迁移失败
```bash
# 手动运行迁移
docker exec inspireed-backend alembic upgrade head

# 查看迁移状态
docker exec inspireed-backend alembic current

# 查看迁移历史
docker exec inspireed-backend alembic history
```

## 🔒 安全建议

1. **修改默认密码**
   - 登录后立即修改管理员密码
   - 修改数据库密码（需同步更新 .env.prod）

2. **配置防火墙**
   ```bash
   # 只开放必要端口
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```

3. **使用 HTTPS**（推荐）
   - 配置 Nginx 反向代理
   - 使用 Let's Encrypt 免费证书

4. **定期备份**
   ```bash
   # 备份数据库
   docker exec inspireed-postgres pg_dump -U postgres inspireed > backup_$(date +%Y%m%d).sql

   # 备份 MinIO 数据
   docker exec inspireed-minio mc mirror /data /backup/minio
   ```

## 📈 性能优化

### 增加上传文件大小限制
编辑 `frontend/nginx.conf`:
```nginx
client_max_body_size 100M;
```

### 配置 Redis 持久化
编辑 `docker/docker-compose.prod.yml`，在 Redis 服务中添加：
```yaml
command: redis-server --appendonly yes
volumes:
  - redis_data:/data
```

### 数据库优化
编辑 `docker/docker-compose.prod.yml`，在 PostgreSQL 服务中添加：
```yaml
command: postgres -c shared_buffers=256MB -c max_connections=200
```

## 📞 获取帮助

如果遇到问题：
1. 查看日志: `docker-compose logs`
2. 检查文档: `docs/` 目录
3. 提交 Issue: GitHub Issues

---

**部署完成后，建议保存本文档链接，方便后续维护和更新。**
