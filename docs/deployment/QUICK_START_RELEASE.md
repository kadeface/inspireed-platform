# 发布分支快速开始指南

## 🚀 快速创建发布分支并部署

### 第一步：创建发布分支

```bash
# 1. 确保在 dev 分支且代码最新
git checkout dev
git pull origin dev

# 2. 创建发布分支（替换 v1.0.0 为实际版本号）
VERSION="v1.0.0"
git checkout -b release/$VERSION

# 3. 推送到远程
git push -u origin release/$VERSION
```

### 第二步：运行发布前检查

```bash
# 运行检查清单
./scripts/deployment/pre-release-checklist.sh
```

修复所有失败项和警告项。

### 第三步：配置生产环境变量

```bash
# 1. 创建生产环境变量文件
cp backend/env.example backend/.env.prod

# 2. 编辑配置文件
nano backend/.env.prod  # 或使用 vim/其他编辑器
```

**必须修改的配置项：**

```bash
# 生成强密码（每个都运行一次）
openssl rand -hex 32

# 然后更新 .env.prod 中的以下配置：
SECRET_KEY=<生成的密钥>
POSTGRES_PASSWORD=<生成的密码>
REDIS_PASSWORD=<生成的密码>
MINIO_ROOT_PASSWORD=<生成的密码>
FIRST_SUPERUSER_PASSWORD=<生成的密码>
```

**重要：确保 `.env.prod` 已添加到 `.gitignore`，不会提交到 Git！**

### 第四步：在服务器上部署

#### 在腾讯云服务器上：

```bash
# 1. 克隆或更新代码
git clone <repository-url>
cd inspireed-platform-main
git checkout release/v1.0.0  # 替换为实际版本

# 2. 配置环境变量（如果还没有）
cp backend/env.example backend/.env.prod
nano backend/.env.prod  # 编辑配置

# 3. 运行部署脚本
./scripts/deployment/deploy-production.sh
```

### 第五步：验证部署

```bash
# 检查服务状态
cd docker
docker-compose -f docker-compose.prod.yml ps

# 检查健康状态
curl http://localhost:8000/health
curl http://localhost/

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

## 📋 完整流程示例

```bash
# ===== 本地开发环境 =====

# 1. 创建发布分支
git checkout dev
git pull origin dev
git checkout -b release/v1.0.0
git push -u origin release/v1.0.0

# 2. 运行检查
./scripts/deployment/pre-release-checklist.sh

# 3. 提交发布准备
git add .
git commit -m "chore: prepare release v1.0.0"
git push origin release/v1.0.0

# ===== 服务器环境 =====

# 1. 更新代码
cd /path/to/inspireed-platform-main
git fetch origin
git checkout release/v1.0.0
git pull origin release/v1.0.0

# 2. 配置环境变量（首次部署）
if [ ! -f backend/.env.prod ]; then
    cp backend/env.example backend/.env.prod
    # 生成密码
    echo "SECRET_KEY=$(openssl rand -hex 32)"
    echo "POSTGRES_PASSWORD=$(openssl rand -hex 32)"
    echo "REDIS_PASSWORD=$(openssl rand -hex 32)"
    echo "MINIO_ROOT_PASSWORD=$(openssl rand -hex 32)"
    # 编辑 .env.prod 并填入上述密码
    nano backend/.env.prod
fi

# 3. 部署
./scripts/deployment/deploy-production.sh

# 4. 验证
curl http://localhost:8000/health
```

## 🔒 数据库安全配置

### 自动备份

```bash
# 手动备份
./scripts/deployment/backup-database.sh

# 设置定时备份（每日凌晨2点）
crontab -e
# 添加：
0 2 * * * /path/to/inspireed-platform-main/scripts/deployment/backup-database.sh
```

### 迁移前备份

```bash
# 部署前自动备份
./scripts/deployment/backup-database.sh --pre-migration
```

## 🐳 Docker 网络配置

### 检查端口绑定

确保数据库端口仅绑定到本地：

```yaml
# docker/docker-compose.prod.yml
postgres:
  ports:
    - "127.0.0.1:5432:5432"  # ✅ 仅本地访问
    # ❌ 不要使用: "5432:5432" (会暴露到公网)
```

### 防火墙配置

```bash
# 仅开放必要端口
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 8000/tcp  # API (可选，如果不需要外部访问)
sudo ufw enable
```

## 📝 发布后检查清单

- [ ] 服务健康检查通过
- [ ] 前端可以正常访问
- [ ] 后端 API 正常响应
- [ ] 数据库连接正常
- [ ] 登录功能正常
- [ ] 数据库备份已配置
- [ ] 日志正常输出
- [ ] 修改了默认管理员密码

## 🔄 回滚流程

如果部署出现问题，可以快速回滚：

```bash
# 1. 停止服务
cd docker
docker-compose -f docker-compose.prod.yml down

# 2. 恢复数据库备份（如果需要）
gunzip < backups/db_backup_YYYYMMDD_HHMMSS.sql.gz | \
  docker exec -i inspireed-postgres psql -U postgres inspireed

# 3. 切换到上一个版本
git checkout <previous-release-tag>

# 4. 重新部署
./scripts/deployment/deploy-production.sh
```

## 🔗 相关文档

- [发布分支策略](./RELEASE_BRANCH_STRATEGY.md) - 详细的分支管理策略
- [数据库安全配置](./DATABASE_SECURITY.md) - 数据库安全最佳实践
- [腾讯云部署指南](./TENCENT_CLOUD_DEPLOYMENT.md) - 腾讯云特定配置

## ❓ 常见问题

### Q: 如何生成强密码？

```bash
openssl rand -hex 32
```

### Q: .env.prod 文件应该放在哪里？

放在 `backend/.env.prod`，确保已添加到 `.gitignore`。

### Q: 如何检查服务是否正常？

```bash
# 检查容器状态
docker ps

# 检查健康状态
docker inspect inspireed-backend | grep Health -A 10

# 检查日志
docker logs inspireed-backend
```

### Q: 数据库迁移失败怎么办？

1. 检查数据库连接
2. 查看迁移日志：`docker logs inspireed-backend`
3. 手动运行迁移：`docker exec inspireed-backend alembic upgrade head`
4. 如果问题严重，恢复备份
