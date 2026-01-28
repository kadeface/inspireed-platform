# 部署文档

本目录包含 InspireEd 平台的生产环境部署相关文档和脚本。

## 📚 文档索引

### 快速开始
- **[快速开始指南](./QUICK_START_RELEASE.md)** - 快速创建发布分支并部署到生产环境

### 详细文档
- **[发布流程总结](./RELEASE_PROCESS_SUMMARY.md)** - 完整的发布流程设计说明
- **[发布分支策略](./RELEASE_BRANCH_STRATEGY.md)** - Git 分支管理和发布流程
- **[数据库安全配置](./DATABASE_SECURITY.md)** - 数据库安全最佳实践

### 其他文档
- [腾讯云部署指南](./TENCENT_CLOUD_DEPLOYMENT.md) - 腾讯云特定配置

## 🛠️ 部署脚本

所有脚本位于 `scripts/deployment/` 目录：

### 核心脚本

1. **deploy-production.sh** - 生产环境部署脚本
   ```bash
   ./scripts/deployment/deploy-production.sh
   ```
   - 自动化整个部署流程
   - 包含健康检查、数据库迁移等

2. **backup-database.sh** - 数据库备份脚本
   ```bash
   ./scripts/deployment/backup-database.sh
   ./scripts/deployment/backup-database.sh --pre-migration
   ```
   - SQL 备份（自动压缩）
   - 数据卷备份（可选）
   - 自动清理旧备份

3. **pre-release-checklist.sh** - 发布前检查清单
   ```bash
   ./scripts/deployment/pre-release-checklist.sh
   ```
   - 检查代码质量
   - 验证配置完整性
   - 安全配置检查

## 🚀 快速开始

### 1. 创建发布分支

```bash
git checkout dev
git pull origin dev
git checkout -b release/v1.0.0
git push -u origin release/v1.0.0
```

### 2. 运行发布前检查

```bash
./scripts/deployment/pre-release-checklist.sh
```

### 3. 配置生产环境

```bash
cp backend/env.example backend/.env.prod
# 编辑 backend/.env.prod，生成强密码
openssl rand -hex 32  # 运行多次生成不同服务的密码
```

### 4. 部署到服务器

```bash
./scripts/deployment/deploy-production.sh
```

## 🔒 安全要点

1. **数据库密码**：使用 `openssl rand -hex 32` 生成强密码
2. **环境变量**：确保 `.env.prod` 未提交到 Git
3. **网络隔离**：数据库端口仅绑定到本地
4. **定期备份**：设置自动备份计划

## 📋 检查清单

### 发布前
- [ ] 运行 `pre-release-checklist.sh` 通过
- [ ] 所有测试通过
- [ ] 代码审查完成
- [ ] 环境变量已配置

### 部署后
- [ ] 服务健康检查通过
- [ ] 前端可以正常访问
- [ ] 后端 API 正常响应
- [ ] 修改了默认管理员密码
- [ ] 数据库备份已配置

## 🔗 相关链接

- [项目 README](../../README.md)
- [Docker 部署文档](../docker/README.md)
- [迁移指南](../MIGRATION_GUIDE.md)
