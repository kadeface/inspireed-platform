# 修复登录401错误 - Admin用户初始化

## 问题描述

登录时返回 401 错误，提示"用户名或密码错误"。这通常是因为数据库中还没有初始化管理员账号。

## 快速修复

### 方法 1：在运行中的容器中执行（推荐）

如果您的服务已经在运行，直接在容器中执行初始化脚本：

```bash
# 进入docker目录
cd docker

# 执行初始化脚本
docker exec inspireed-backend python scripts/ensure_admin_user.py
```

### 方法 2：如果容器未运行，先启动服务

```bash
# 进入docker目录
cd docker

# 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 等待服务启动（约30秒）
sleep 30

# 运行数据库迁移（如果还没运行）
docker exec inspireed-backend alembic upgrade head

# 初始化admin用户
docker exec inspireed-backend python scripts/ensure_admin_user.py
```

## 默认管理员账号

初始化后，可以使用以下账号登录：

- **用户名**：`admin`
- **密码**：`admin123`
- **邮箱**：`admin@inspireed.com`

## 验证

初始化完成后，您应该看到类似以下输出：

```
🔧 检查并确保admin用户存在...

✅ 找到用户: admin (ID: 1)
   邮箱: admin@inspireed.com
   角色: admin
   激活状态: True
   密码验证: ✅ 正确

✅ Admin用户已更新
   用户名: admin
   密码: admin123
```

## 如果仍然无法登录

1. **检查用户是否激活**：
   ```bash
   docker exec inspireed-backend python -c "
   import asyncio
   from app.core.database import AsyncSessionLocal
   from app.models import User
   from sqlalchemy import select
   
   async def check():
       async with AsyncSessionLocal() as db:
           result = await db.execute(select(User).where(User.username == 'admin'))
           user = result.scalar_one_or_none()
           if user:
               print(f'用户: {user.username}')
               print(f'激活状态: {user.is_active}')
               print(f'角色: {user.role}')
           else:
               print('未找到admin用户')
   
   asyncio.run(check())
   "
   ```

2. **检查密码哈希**：
   ```bash
   docker exec inspireed-backend python scripts/ensure_admin_user.py
   ```

3. **查看后端日志**：
   ```bash
   docker logs inspireed-backend --tail 50
   ```

## 安全建议

⚠️ **重要**：首次登录后，请立即：
1. 修改管理员密码
2. 在生产环境中使用强密码
3. 考虑禁用或删除默认测试账号

## 相关文件

- 初始化脚本：`backend/scripts/ensure_admin_user.py`
- 便捷脚本：`backend/scripts/init_admin.sh`
- 部署文档：`docker/CLOUDSTUDIO_DEPLOYMENT.md`

