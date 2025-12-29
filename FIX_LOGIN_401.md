# 修复登录401错误 - Admin用户初始化

## 问题描述

登录时返回 401 错误，提示"用户名或密码错误"。这通常是因为数据库中还没有初始化管理员账号。

## 快速修复

### 方法 1：在运行中的容器中执行（推荐）

如果您的服务已经在运行，需要先修复 bcrypt 版本兼容性问题，然后执行初始化脚本：

```bash
# 进入docker目录
cd docker

# 步骤 1：修复 bcrypt 版本兼容性问题
docker exec inspireed-backend pip install --upgrade "bcrypt==3.2.2"

# 步骤 2：执行初始化脚本
docker exec inspireed-backend python scripts/ensure_admin_user.py
```

**如果遇到 bcrypt 版本错误**，可以使用简化版本（直接使用 bcrypt，不依赖 passlib）：

```bash
# 使用简化版本脚本（推荐，避免版本兼容性问题）
docker exec inspireed-backend python scripts/ensure_admin_user_simple.py
```

或者尝试：

```bash
# 方法 A：重新安装兼容版本
docker exec inspireed-backend pip uninstall -y bcrypt && \
docker exec inspireed-backend pip install "bcrypt==3.2.2"

# 方法 B：使用 setup_test_accounts.py（它会创建所有测试账号，包括admin）
docker exec inspireed-backend python scripts/setup_test_accounts.py
```

### 方法 2：如果容器未运行，先启动服务

```bash
# 进入docker目录
cd docker

# 启动服务
docker-compose -f docker-compose.prod.yml up -d --build

# 等待服务启动（约30秒）
sleep 30

# 运行数据库迁移（如果还没运行）
docker exec inspireed-backend alembic upgrade head

# 修复 bcrypt 版本（如果需要）
docker exec inspireed-backend pip install --upgrade "bcrypt==3.2.2"

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

