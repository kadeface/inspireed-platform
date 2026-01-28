# 数据库安全配置指南

## 🔒 安全原则

### 1. 最小权限原则

数据库用户应该只拥有必要的权限，避免使用超级用户。

### 2. 网络隔离

- 数据库服务仅监听本地接口（127.0.0.1）
- 使用 Docker 内部网络进行服务间通信
- 不暴露数据库端口到公网

### 3. 密码安全

- 使用强密码（至少32位随机字符串）
- 定期轮换密码
- 密码存储在环境变量中，不提交到代码仓库

### 4. 数据加密

- 敏感数据加密存储
- 传输加密（TLS/SSL）
- 备份文件加密

## 🛡️ 生产环境配置

### 1. 生成安全密码

```bash
# 生成数据库密码
POSTGRES_PASSWORD=$(openssl rand -hex 32)
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"

# 生成 Redis 密码
REDIS_PASSWORD=$(openssl rand -hex 32)
echo "REDIS_PASSWORD=$REDIS_PASSWORD"

# 生成 MinIO 密码
MINIO_PASSWORD=$(openssl rand -hex 32)
echo "MINIO_ROOT_PASSWORD=$MINIO_PASSWORD"
```

### 2. 配置 Docker Compose

在 `docker/docker-compose.prod.yml` 中：

```yaml
postgres:
  environment:
    POSTGRES_USER: inspireed_user  # 非 postgres 用户
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}  # 从环境变量读取
    POSTGRES_DB: inspireed
  ports:
    - "127.0.0.1:5432:5432"  # 仅本地访问
  networks:
    - inspireed-network  # 内部网络
```

### 3. 创建专用数据库用户

```sql
-- 连接到数据库
docker exec -it inspireed-postgres psql -U postgres

-- 创建专用用户（非超级用户）
CREATE USER inspireed_user WITH PASSWORD 'strong_password_here';

-- 授予必要权限
GRANT CONNECT ON DATABASE inspireed TO inspireed_user;
GRANT USAGE ON SCHEMA public TO inspireed_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO inspireed_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO inspireed_user;

-- 设置默认权限（新表自动授权）
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO inspireed_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO inspireed_user;
```

### 4. 配置应用连接

在 `backend/.env.prod` 中：

```bash
# 使用专用用户
POSTGRES_USER=inspireed_user
POSTGRES_PASSWORD=strong_password_here
POSTGRES_SERVER=postgres  # Docker 内部网络名称
POSTGRES_DB=inspireed
POSTGRES_PORT=5432
```

## 💾 备份策略

### 1. 自动备份脚本

使用提供的备份脚本：

```bash
./scripts/deployment/backup-database.sh
```

### 2. 备份计划

**每日备份：**

```bash
# 添加到 crontab
0 2 * * * /path/to/inspireed-platform-main/scripts/deployment/backup-database.sh
```

**迁移前备份：**

```bash
# 部署前必须备份
./scripts/deployment/backup-database.sh --pre-migration
```

### 3. 备份存储

- 本地备份：保留最近7天
- 远程备份：上传到云存储（加密）
- 备份验证：定期测试恢复

### 4. 备份加密

```bash
# 加密备份文件
gpg --symmetric --cipher-algo AES256 backup_20250126.sql

# 解密
gpg --decrypt backup_20250126.sql.gpg > backup_20250126.sql
```

## 🔄 迁移安全

### 1. 迁移前检查

```bash
# 1. 检查当前数据库版本
docker exec inspireed-backend alembic current

# 2. 检查待执行的迁移
docker exec inspireed-backend alembic heads

# 3. 检查迁移脚本
docker exec inspireed-backend alembic history
```

### 2. 迁移执行流程

```bash
# 1. 备份数据库
./scripts/deployment/backup-database.sh --pre-migration

# 2. 在测试环境验证迁移
# （如果有测试环境）

# 3. 执行迁移
docker exec inspireed-backend alembic upgrade head

# 4. 验证迁移结果
docker exec inspireed-backend alembic current

# 5. 检查数据完整性
docker exec inspireed-postgres psql -U postgres -d inspireed -c "SELECT COUNT(*) FROM users;"
```

### 3. 迁移回滚

```bash
# 回滚到上一个版本
docker exec inspireed-backend alembic downgrade -1

# 回滚到指定版本
docker exec inspireed-backend alembic downgrade <revision_id>
```

## 🔍 安全监控

### 1. 连接监控

```sql
-- 查看当前连接
SELECT pid, usename, application_name, client_addr, state 
FROM pg_stat_activity 
WHERE datname = 'inspireed';

-- 查看连接数
SELECT count(*) FROM pg_stat_activity WHERE datname = 'inspireed';
```

### 2. 访问日志

启用 PostgreSQL 日志：

```yaml
# docker-compose.prod.yml
postgres:
  command: postgres -c log_connections=on -c log_disconnections=on -c log_statement=all
```

### 3. 异常检测

监控以下指标：
- 异常连接尝试
- 大量查询
- 长时间运行的查询
- 失败的认证尝试

## 🚨 应急响应

### 1. 数据泄露

1. 立即更改所有密码
2. 检查访问日志
3. 评估影响范围
4. 通知相关人员

### 2. 数据库损坏

```bash
# 1. 停止服务
docker-compose -f docker/docker-compose.prod.yml down

# 2. 恢复备份
docker exec -i inspireed-postgres psql -U postgres inspireed < backup_YYYYMMDD_HHMMSS.sql

# 3. 验证数据
docker exec inspireed-postgres psql -U postgres -d inspireed -c "\dt"

# 4. 重启服务
docker-compose -f docker/docker-compose.prod.yml up -d
```

### 3. 性能问题

```sql
-- 查看慢查询
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';

-- 终止慢查询
SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
```

## 📋 安全检查清单

### 部署前
- [ ] 数据库密码已更新为强密码
- [ ] 使用专用数据库用户（非 postgres）
- [ ] 数据库端口仅绑定到 127.0.0.1
- [ ] 备份脚本已配置
- [ ] 迁移脚本已测试

### 部署后
- [ ] 数据库连接正常
- [ ] 迁移已成功执行
- [ ] 备份已创建
- [ ] 访问日志已启用
- [ ] 监控已配置

### 定期检查
- [ ] 备份文件完整性
- [ ] 备份恢复测试
- [ ] 密码轮换
- [ ] 安全审计
- [ ] 性能监控

## 🔗 相关文档

- [发布分支策略](./RELEASE_BRANCH_STRATEGY.md)
- [Docker 部署文档](../docker/README.md)
- [迁移指南](../MIGRATION_GUIDE.md)
