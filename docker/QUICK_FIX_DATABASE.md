# 数据库初始化问题快速修复指南

## 问题现象

后端容器启动成功，但日志中显示数据库表创建错误：
```
⚠️ Application will continue, but database operations may fail
```

## 原因分析

应用启动时尝试自动创建数据库表，但应该使用 Alembic 迁移来管理数据库结构。自动创建表可能与迁移不一致，导致错误。

## 解决方案

### 方法 1：运行数据库迁移（推荐）

```bash
cd docker
./run-migration.sh
```

或者手动运行：

```bash
docker exec inspireed-backend alembic upgrade head
```

### 方法 2：使用修复脚本（自动运行迁移）

```bash
cd docker
./fix-backend-startup.sh
```

这个脚本会自动：
1. 检查并启动依赖服务
2. 重新构建后端镜像
3. 启动后端服务
4. **自动运行数据库迁移**
5. 验证服务状态

## 验证修复

### 1. 检查数据库版本

```bash
docker exec inspireed-backend alembic current
```

应该显示类似：
```
20250122_add_student_projects (head)
```

### 2. 测试健康端点

```bash
docker exec inspireed-backend python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read())"
```

应该返回：
```
b'{"status":"healthy"}'
```

### 3. 检查服务状态

```bash
docker-compose -f docker-compose.prod.yml ps
```

所有服务应该显示为 `healthy`。

## 改进说明

已对代码进行以下改进：

1. **智能检测迁移系统**：`init_db()` 函数现在会自动检测是否使用了 Alembic 迁移
   - 如果检测到迁移系统，会跳过自动创建表
   - 提示运行 `alembic upgrade head`

2. **更好的错误处理**：
   - 表已存在的错误会被忽略
   - 提供清晰的错误提示

3. **自动化迁移**：
   - `fix-backend-startup.sh` 脚本现在会自动运行迁移
   - 新增 `run-migration.sh` 脚本用于单独运行迁移

## 常见问题

### Q: 迁移失败怎么办？

A: 查看详细错误：
```bash
docker logs inspireed-backend | tail -50
```

### Q: 如何重置数据库？

A: ⚠️ **警告**：这会删除所有数据！

```bash
# 停止服务
docker-compose -f docker-compose.prod.yml down

# 删除数据卷
docker volume rm inspireed-platform-main_postgres_data

# 重新启动
docker-compose -f docker-compose.prod.yml up -d

# 等待服务启动后运行迁移
sleep 30
docker exec inspireed-backend alembic upgrade head
```

### Q: 迁移和自动创建表的区别？

A:
- **Alembic 迁移**：推荐方式，可以版本控制、回滚、处理复杂变更
- **自动创建表**：仅用于开发环境，不支持版本控制

生产环境应该始终使用 Alembic 迁移。

