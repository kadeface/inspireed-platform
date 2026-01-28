# 发布分支策略与部署流程

## 📋 概述

本文档描述了 InspireEd 平台的生产环境发布流程，包括分支管理、数据库安全、Docker 部署等关键环节。

## 🌿 Git 分支策略

### 分支结构

```
main (生产环境)
  └── release/v1.x.x (发布分支)
      └── dev (开发分支)
          └── feature/* (功能分支)
```

### 分支说明

- **main**: 生产环境稳定版本，只接受来自 release 分支的合并
- **release/v1.x.x**: 发布分支，用于准备生产发布
- **dev**: 开发分支，日常开发工作
- **feature/***: 功能分支，从 dev 分支创建

## 🚀 创建发布分支流程

### 1. 准备工作

```bash
# 确保在 dev 分支且代码是最新的
git checkout dev
git pull origin dev

# 确保工作区干净
git status
```

### 2. 创建发布分支

```bash
# 确定版本号（遵循语义化版本：主版本.次版本.修订版本）
VERSION="v1.0.0"

# 创建发布分支
git checkout -b release/$VERSION

# 推送到远程
git push -u origin release/$VERSION
```

### 3. 发布前检查

运行发布前检查脚本：

```bash
./scripts/deployment/pre-release-checklist.sh
```

检查清单包括：
- ✅ 代码质量检查（lint、类型检查）
- ✅ 测试通过
- ✅ 数据库迁移脚本检查
- ✅ 环境变量配置检查
- ✅ 安全漏洞扫描
- ✅ 依赖版本检查

### 4. 更新版本信息

```bash
# 更新版本号（如果项目中有版本文件）
# 例如：package.json, pyproject.toml 等
```

### 5. 提交发布准备

```bash
git add .
git commit -m "chore: prepare release $VERSION"
git push origin release/$VERSION
```

## 🔒 数据库安全措施

### 1. 生产环境数据库配置

**重要安全原则：**

1. **密码强度**
   - 使用强密码（至少32位随机字符串）
   - 使用密码生成工具：`openssl rand -hex 32`

2. **网络隔离**
   - 数据库端口仅绑定到 `127.0.0.1`（本地）
   - 不暴露到公网
   - 使用 Docker 内部网络通信

3. **访问控制**
   - 创建专用数据库用户（非 postgres 超级用户）
   - 最小权限原则
   - 定期轮换密码

4. **数据备份**
   - 自动每日备份
   - 迁移前必须备份
   - 备份文件加密存储

### 2. 数据库备份策略

#### 自动备份

```bash
# 使用提供的备份脚本
./scripts/deployment/backup-database.sh
```

#### 手动备份

```bash
# 备份数据库
docker exec inspireed-postgres pg_dump -U postgres inspireed > backup_$(date +%Y%m%d_%H%M%S).sql

# 备份数据卷（完整备份）
docker run --rm -v inspireed-platform-main_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_data_$(date +%Y%m%d_%H%M%S).tar.gz /data
```

### 3. 数据库迁移安全

**迁移前必须：**

1. ✅ 备份数据库
2. ✅ 在测试环境验证迁移
3. ✅ 检查迁移脚本的幂等性
4. ✅ 准备回滚方案

**迁移执行：**

```bash
# 1. 备份
./scripts/deployment/backup-database.sh

# 2. 运行迁移
docker exec inspireed-backend alembic upgrade head

# 3. 验证迁移
docker exec inspireed-backend alembic current
```

## 🐳 Docker 部署安全

### 1. 环境变量管理

**重要：`.env.prod` 文件绝不能提交到 Git！**

```bash
# 创建生产环境变量文件
cp backend/env.example backend/.env.prod

# 使用安全的方式生成密钥
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 32)
REDIS_PASSWORD=$(openssl rand -hex 32)
MINIO_ROOT_PASSWORD=$(openssl rand -hex 32)
```

### 2. 网络安全

- 使用 Docker 内部网络（`inspireed-network`）
- 数据库、Redis、MinIO 仅内部访问
- 仅暴露必要的端口（80, 8000）
- 使用防火墙限制访问

### 3. 数据持久化

- 使用 Docker volumes 持久化数据
- 定期备份 volumes
- 监控磁盘空间

## 📦 生产环境部署流程

### 1. 服务器准备

```bash
# 在腾讯云服务器上
# 1. 安装 Docker 和 Docker Compose
# 2. 配置防火墙
# 3. 创建必要的目录
```

### 2. 部署步骤

```bash
# 1. 克隆或更新代码
git clone <repository-url>
cd inspireed-platform-main
git checkout release/v1.0.0

# 2. 配置环境变量
cp backend/env.example backend/.env.prod
# 编辑 backend/.env.prod，设置生产环境配置

# 3. 运行部署脚本
./scripts/deployment/deploy-production.sh
```

### 3. 部署后验证

```bash
# 检查服务状态
docker-compose -f docker/docker-compose.prod.yml ps

# 检查健康状态
curl http://localhost:8000/health
curl http://localhost/

# 检查日志
docker-compose -f docker/docker-compose.prod.yml logs -f
```

## 🔄 回滚流程

### 1. 代码回滚

```bash
# 切换到上一个稳定版本
git checkout <previous-release-tag>

# 重新部署
./scripts/deployment/deploy-production.sh
```

### 2. 数据库回滚

```bash
# 1. 停止服务
docker-compose -f docker/docker-compose.prod.yml down

# 2. 恢复数据库备份
docker exec -i inspireed-postgres psql -U postgres inspireed < backup_YYYYMMDD_HHMMSS.sql

# 3. 或回滚迁移
docker exec inspireed-backend alembic downgrade -1

# 4. 重启服务
docker-compose -f docker/docker-compose.prod.yml up -d
```

## ✅ 发布检查清单

### 代码层面
- [ ] 所有测试通过
- [ ] 代码审查完成
- [ ] 无已知安全漏洞
- [ ] 依赖版本已更新且安全

### 数据库层面
- [ ] 数据库备份已完成
- [ ] 迁移脚本已测试
- [ ] 回滚方案已准备
- [ ] 数据库密码已更新为强密码

### 配置层面
- [ ] `.env.prod` 已配置且未提交到 Git
- [ ] 所有密钥已更新
- [ ] CORS 配置正确
- [ ] API 地址配置正确

### 部署层面
- [ ] Docker 镜像构建成功
- [ ] 服务健康检查通过
- [ ] 日志正常
- [ ] 性能测试通过

### 安全层面
- [ ] 数据库端口未暴露到公网
- [ ] 防火墙规则已配置
- [ ] SSL/TLS 证书已配置（如需要）
- [ ] 访问日志已启用

## 📝 版本发布记录

发布时创建 Release Notes：

```markdown
## Release v1.0.0 (2025-01-XX)

### 新增功能
- 功能1
- 功能2

### 修复
- Bug修复1
- Bug修复2

### 改进
- 性能优化
- UI改进

### 安全
- 安全更新
```

## 🔗 相关文档

- [数据库安全配置指南](./DATABASE_SECURITY.md)
- [腾讯云部署指南](./TENCENT_CLOUD_DEPLOYMENT.md)
- [Docker 部署文档](../docker/README.md)
