# 快速启动后端服务指南

## 问题诊断结果

根据诊断脚本的输出，后端服务未运行。需要启动后端服务。

## 启动方法

### 方法一：使用 CloudStudio 预览功能（推荐）

1. **打开 CloudStudio 预览面板**：
   - 点击 CloudStudio 右侧的"预览"按钮
   - 或使用快捷键：`Ctrl+Shift+P` 然后输入 "Preview"

2. **启动后端服务**：
   - 在预览面板中找到 `backend-api` 应用
   - 点击"启动"或"运行"按钮
   - 等待服务启动完成

3. **验证服务启动**：
   ```bash
   curl http://localhost:8000/health
   ```
   应该返回：`{"status":"ok"}`

### 方法二：手动运行启动脚本

在 CloudStudio 终端中运行：

```bash
bash .vscode/start-backend-cloudstudio.sh
```

这个脚本会：
- 检查并启动 Docker 服务（如果需要）
- 创建 Python 虚拟环境
- 安装依赖
- 运行数据库迁移
- 启动后端服务（端口 8000）

### 方法三：使用 Docker Compose（如果使用 Docker）

```bash
cd docker
docker-compose -f docker-compose.cloudstudio.yml up -d backend
```

查看日志：
```bash
docker logs inspireed-backend -f
```

## 验证服务启动

启动后，运行以下命令验证：

```bash
# 1. 检查健康状态
curl http://localhost:8000/health

# 2. 检查 API 文档
curl http://localhost:8000/docs

# 3. 重新运行诊断脚本
bash scripts/diagnose-login-issue.sh
```

## 常见问题

### Q: 启动脚本执行失败

**可能原因**：
- Docker 未运行
- Python 环境问题
- 依赖安装失败
- 数据库连接失败

**解决方法**：
1. 检查 Docker 是否运行：`docker info`
2. 检查 Python 版本：`python3 --version`（需要 Python 3.8+）
3. 检查数据库服务是否运行
4. 查看启动脚本的详细错误信息

### Q: 端口 8000 被占用

**解决方法**：
```bash
# 查找占用端口的进程
lsof -i :8000

# 停止占用端口的进程
kill $(lsof -ti:8000)

# 然后重新启动后端服务
```

### Q: 数据库连接失败

**解决方法**：
1. 确保数据库服务运行：
   ```bash
   # 如果使用 Docker
   docker ps | grep postgres
   
   # 如果未运行，启动数据库
   cd docker
   docker-compose -f docker-compose.cloudstudio.yml up -d postgres
   ```

2. 检查 `backend/.env` 配置：
   ```bash
   cat backend/.env | grep POSTGRES
   ```

### Q: 启动后立即停止

**解决方法**：
1. 查看启动日志中的错误信息
2. 检查环境变量配置
3. 确保所有依赖服务（数据库、Redis 等）都已启动

## 启动脚本位置

- 后端启动脚本：`.vscode/start-backend-cloudstudio.sh`
- 前端启动脚本：`.vscode/start-frontend-cloudstudio.sh`
- Docker Compose 配置：`docker/docker-compose.cloudstudio.yml`

## 下一步

后端服务启动成功后：

1. **验证服务**：
   ```bash
   curl http://localhost:8000/health
   ```

2. **重新运行诊断**：
   ```bash
   bash scripts/diagnose-login-issue.sh
   ```

3. **测试登录**：
   - 在浏览器中访问前端应用
   - 尝试登录
   - 应该不再出现 `ERR_FAILED` 错误

## 相关文档

- `FIX_LOGIN_ERR_FAILED.md` - 登录错误故障排查指南
- `CLOUDSTUDIO_PREVIEW_OUTPUT.md` - 预览输出查看指南
- `scripts/diagnose-login-issue.sh` - 诊断脚本


