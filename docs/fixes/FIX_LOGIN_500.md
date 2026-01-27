# 修复登录500错误

## 问题描述

登录时返回 500 内部服务器错误，这通常表示后端在处理登录请求时发生了异常。

## 快速诊断

### 步骤 1：运行诊断脚本（推荐）

```bash
docker exec inspireed-backend python scripts/diagnose_login.py
```

这个脚本会检查：
- ✅ 数据库连接是否正常
- ✅ admin用户是否存在
- ✅ 密码验证是否正常
- ✅ 密码哈希生成是否正常
- ✅ 配置是否正确

### 步骤 2：查看后端日志

```bash
# 查看最近的错误日志
docker logs inspireed-backend --tail 100

# 实时查看日志
docker logs inspireed-backend -f
```

## 常见问题和解决方案

### 问题 1：bcrypt 版本不兼容

**症状**：日志中出现 `AttributeError: module 'bcrypt' has no attribute '__about__'` 或密码验证错误

**解决方案**：

```bash
# 方法 A：重新安装兼容版本
docker exec inspireed-backend pip install --upgrade "bcrypt==3.2.2"

# 方法 B：使用简化版初始化脚本（推荐）
docker exec inspireed-backend python scripts/ensure_admin_user_simple.py
```

### 问题 2：用户不存在

**症状**：诊断脚本显示"未找到admin用户"

**解决方案**：

```bash
# 创建admin用户
docker exec inspireed-backend python scripts/ensure_admin_user_simple.py
```

### 问题 3：密码哈希格式不匹配

**症状**：用户存在但密码验证失败

**解决方案**：

```bash
# 重新设置密码
docker exec inspireed-backend python scripts/ensure_admin_user_simple.py
```

### 问题 4：数据库连接问题

**症状**：诊断脚本显示数据库连接失败

**解决方案**：

```bash
# 检查数据库服务是否运行
docker-compose -f docker-compose.prod.yml ps

# 检查数据库连接配置
docker exec inspireed-backend env | grep POSTGRES

# 重启数据库服务
docker-compose -f docker-compose.prod.yml restart postgres
```

### 问题 5：SECRET_KEY 未设置

**症状**：创建 JWT token 时出错

**解决方案**：

```bash
# 检查 SECRET_KEY
docker exec inspireed-backend env | grep SECRET_KEY

# 如果未设置，需要在 .env 文件中配置
# 生成 SECRET_KEY：
openssl rand -hex 32
```

## 完整修复流程

如果诊断脚本发现问题，按以下步骤修复：

```bash
# 1. 进入docker目录
cd docker

# 2. 确保服务运行
docker-compose -f docker-compose.prod.yml ps

# 3. 修复 bcrypt 版本（如果需要）
docker exec inspireed-backend pip install --upgrade "bcrypt==3.2.2"

# 4. 初始化admin用户
docker exec inspireed-backend python scripts/ensure_admin_user_simple.py

# 5. 再次运行诊断
docker exec inspireed-backend python scripts/diagnose_login.py

# 6. 查看日志确认
docker logs inspireed-backend --tail 50
```

## 验证修复

修复后，尝试登录：
- 用户名：`admin`
- 密码：`admin123`

如果仍然出现 500 错误，查看后端日志获取详细错误信息：

```bash
docker logs inspireed-backend --tail 100 | grep -A 10 "ERROR\|Exception\|Traceback"
```

## 相关文件

- 诊断脚本：`backend/scripts/diagnose_login.py`
- 初始化脚本：`backend/scripts/ensure_admin_user_simple.py`
- 登录API：`backend/app/api/v1/auth.py`
- 修复401错误指南：`FIX_LOGIN_401.md`

