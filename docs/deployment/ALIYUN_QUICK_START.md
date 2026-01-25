# 阿里云部署快速开始

本文档提供 InspireEd 在阿里云上的快速部署指南。

## 🎯 快速决策指南

### 我应该选择哪种方案？

| 场景 | 推荐方案 | 月度成本 |
|------|---------|---------|
| 测试/演示 | 轻量应用服务器 + Docker | 100-300元 |
| 小规模生产（<100用户） | ECS 2核4GB + Docker | 300-500元 |
| 中等规模（100-1000用户） | ECS 4核8GB + RDS + Redis + OSS | 850-1600元 |
| 大规模（>1000用户） | ACK Kubernetes + 云数据库 | 2300-4200元 |

### 是否使用 Docker？

**强烈推荐使用 Docker** ✅

- ✅ 环境一致，部署简单
- ✅ 易于维护和扩展
- ✅ 项目已完全支持 Docker
- ✅ 可以平滑迁移到 Kubernetes

---

## 🚀 最快部署方式（Docker）

### 1. 购买 ECS 服务器

推荐配置：
- **CPU**: 2核（测试）或 4核（生产）
- **内存**: 4GB（测试）或 8GB（生产）
- **系统**: Ubuntu 22.04 LTS
- **带宽**: 3-5Mbps

### 2. 连接服务器

```bash
ssh root@your-ecs-ip
```

### 3. 运行部署脚本

```bash
# 克隆项目（或上传代码）
git clone https://github.com/your-org/inspireed-platform.git /opt/inspireed-platform

# 运行部署脚本
cd /opt/inspireed-platform
sudo bash scripts/deployment/deploy-aliyun-docker.sh
```

脚本会自动：
- ✅ 安装 Docker 和 Docker Compose
- ✅ 配置防火墙
- ✅ 创建环境变量文件
- ✅ 构建并启动所有服务
- ✅ 运行数据库迁移

### 4. 配置环境变量

编辑 `/opt/inspireed-platform/docker/.env` 文件，修改密码：

```bash
vim /opt/inspireed-platform/docker/.env
```

**必须修改的内容**：
- `POSTGRES_PASSWORD`: 数据库密码
- `REDIS_PASSWORD`: Redis 密码
- `MINIO_ROOT_PASSWORD`: MinIO 密码
- `SECRET_KEY`: 应用密钥（长随机字符串）

### 5. 重启服务

```bash
cd /opt/inspireed-platform/docker
docker-compose -f docker-compose.prod.yml restart
```

### 6. 访问应用

- **前端**: http://your-ecs-ip
- **后端 API**: http://your-ecs-ip:8000
- **API 文档**: http://your-ecs-ip:8000/docs

---

## 🔧 手动部署（Docker）

### 1. 安装 Docker

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh
systemctl start docker
systemctl enable docker

# 安装 Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### 2. 配置环境变量

```bash
cd /opt/inspireed-platform/docker

# 创建 .env 文件
cat > .env << 'EOF'
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=inspireed

REDIS_PASSWORD=your-redis-password

MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=your-minio-password

SECRET_KEY=your-long-random-secret-key

BACKEND_CORS_ORIGINS=["http://localhost","http://your-ecs-ip"]
ALLOW_LAN_ACCESS=false

FRONTEND_PORT=80
VITE_API_BASE_URL=http://your-ecs-ip:8000/api/v1
EOF

# 编辑配置
vim .env
```

### 3. 启动服务

```bash
# 构建并启动
docker-compose -f docker-compose.prod.yml up -d --build

# 运行数据库迁移
docker exec inspireed-backend alembic upgrade head

# 查看状态
docker-compose -f docker-compose.prod.yml ps
```

---

## 🌐 配置域名和 HTTPS

### 1. 配置域名解析

在域名服务商处添加 A 记录：
```
yourdomain.com -> your-ecs-ip
```

### 2. 安装 Nginx（如果需要反向代理）

Docker 部署中前端已包含 Nginx，如果需要外部 Nginx：

```bash
apt install -y nginx certbot python3-certbot-nginx
```

### 3. 配置 Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:80;  # 前端 Docker 容器
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000;  # 后端 Docker 容器
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. 申请 SSL 证书

```bash
# 使用 Let's Encrypt（免费）
certbot --nginx -d yourdomain.com

# 或使用阿里云免费 SSL 证书
# 在阿里云控制台申请后，下载并配置
```

---

## 📊 常用命令

### 查看服务状态

```bash
cd /opt/inspireed-platform/docker
docker-compose -f docker-compose.prod.yml ps
```

### 查看日志

```bash
# 所有服务
docker-compose -f docker-compose.prod.yml logs -f

# 特定服务
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### 重启服务

```bash
# 重启所有服务
docker-compose -f docker-compose.prod.yml restart

# 重启特定服务
docker-compose -f docker-compose.prod.yml restart backend
```

### 停止服务

```bash
docker-compose -f docker-compose.prod.yml down
```

### 更新代码

```bash
# 拉取最新代码
cd /opt/inspireed-platform
git pull

# 重新构建并启动
cd docker
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🔒 安全配置

### 1. 修改默认密码

确保 `.env` 文件中的所有密码都已修改为强密码。

### 2. 配置防火墙

```bash
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw enable
```

### 3. 限制 SSH 访问

编辑 `/etc/ssh/sshd_config`，限制特定 IP 访问：

```
AllowUsers root@your-ip
```

### 4. 定期备份

```bash
# 备份数据库
docker exec inspireed-postgres pg_dump -U postgres inspireed > backup.sql

# 备份数据卷
docker run --rm -v inspireed-platform_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

---

## 🐛 故障排查

### 服务无法启动

```bash
# 查看日志
docker-compose -f docker-compose.prod.yml logs [service_name]

# 检查端口占用
netstat -tlnp | grep [port]
```

### 数据库连接失败

```bash
# 检查数据库服务
docker-compose -f docker-compose.prod.yml ps postgres

# 检查连接
docker exec inspireed-backend ping postgres
```

### 前端无法访问后端

1. 检查 `VITE_API_BASE_URL` 配置
2. 检查 CORS 配置
3. 查看后端日志：`docker-compose logs backend`

---

## 📚 更多信息

- [完整部署指南](ALIYUN_DEPLOYMENT_GUIDE.md) - 详细的部署方案和架构说明
- [Docker 部署说明](../../docker/README.md) - Docker 配置和使用说明
- [Ubuntu 部署指南](UBUNTU_DEPLOYMENT_GUIDE.md) - Ubuntu 服务器部署指南

---

## 💡 最佳实践

1. **生产环境使用云数据库**：使用阿里云 RDS 替代 Docker 中的 PostgreSQL
2. **使用对象存储**：使用阿里云 OSS 替代 MinIO
3. **配置监控**：使用阿里云 ARMS 或自建 Prometheus
4. **定期备份**：设置自动备份策略
5. **启用 HTTPS**：使用 SSL 证书加密传输
6. **配置域名**：使用域名而非 IP 访问

