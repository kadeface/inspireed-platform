# 生产环境部署指南

## 问题诊断

### 错误现象
```
Router error: TypeError: Failed to fetch dynamically imported module: 
http://111.230.61.28:5173/src/pages/Teacher/Dashboard.vue
```

### 问题原因

1. **使用了开发模式配置**：服务器上使用的是 `docker-compose.yml`（开发模式），前端使用 `Dockerfile.dev` 启动了Vite开发服务器（端口5173）
2. **动态导入失败**：Vue Router的动态导入（`import()`）在生产环境中无法正常工作
3. **架构不匹配**：开发服务器适合本地开发，但不适合生产部署

## 解决方案

### 方案1：使用生产模式Docker配置（推荐）

#### 在服务器上部署

1. **停止开发模式容器**：
```bash
cd /path/to/inspireed-platform-main/docker
docker-compose down
```

2. **使用生产模式部署**：
```bash
# 使用部署脚本（推荐）
./deploy-prod.sh

# 或手动部署
docker-compose -f docker-compose.prod.yml up -d --build
```

3. **检查服务状态**：
```bash
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

#### 访问地址变化

- **开发模式**：
  - 前端：`http://111.230.61.28:5173`（Vite开发服务器）
  - 后端：`http://111.230.61.28:8000`

- **生产模式**：
  - 前端：`http://111.230.61.28`（Nginx，端口80）
  - 后端：`http://111.230.61.28:8000`

### 方案2：修改Nginx反向代理（如果使用外部Nginx）

如果服务器上有外部Nginx，可以配置反向代理：

```nginx
server {
    listen 80;
    server_name 111.230.61.28;

    # 前端静态文件
    location / {
        proxy_pass http://localhost:80;  # 容器内的Nginx
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 后端API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态资源
    location /uploads/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 生产模式 vs 开发模式

| 特性 | 开发模式 | 生产模式 |
|------|---------|---------|
| 前端端口 | 5173 | 80 |
| 前端服务器 | Vite Dev Server | Nginx |
| 构建方式 | 热更新（HMR） | 静态构建 |
| 文件大小 | 较大（包含source map） | 优化压缩 |
| 加载速度 | 较慢（动态编译） | 快速（预构建） |
| 适用场景 | 本地开发、调试 | 生产部署 |

## 生产环境优势

1. **性能优化**：
   - 静态文件预构建，加载速度快
   - Gzip压缩，减少传输大小
   - 浏览器缓存优化

2. **稳定性**：
   - Nginx提供高并发支持
   - 不依赖Node.js运行时
   - 容器资源占用更低

3. **安全性**：
   - 不暴露源代码
   - 生产环境配置独立
   - 更好的错误处理

## 配置文件说明

### `docker/docker-compose.prod.yml`
- 生产环境Docker配置
- 前端使用 `Dockerfile` 构建静态文件
- Nginx提供服务（端口80）

### `docker/docker-compose.yml`
- 开发环境Docker配置（CloudStudio专用）
- 前端使用 `Dockerfile.dev` 启动开发服务器
- 支持热更新（端口5173）

### `frontend/Dockerfile`
- 生产模式：多阶段构建
- 第一阶段：Node构建静态文件
- 第二阶段：Nginx提供服务

### `frontend/Dockerfile.dev`
- 开发模式：单阶段构建
- 直接启动Vite开发服务器
- 支持热更新和调试

## 常见问题

### Q1: 部署后前端无法访问后端API

**检查步骤**：
1. 确认后端服务正常运行：`curl http://localhost:8000/health`
2. 检查CORS配置：后端 `.env` 中 `ALLOW_LAN_ACCESS=true`
3. 查看后端日志：`docker logs inspireed-backend`

### Q2: 静态资源（图片）加载失败

**解决方法**：
- 确保后端 `/uploads/resources/` 路由配置正确
- 检查文件权限：`ls -la backend/storage/resources/`
- 查看后端CORS日志

### Q3: 如何切换回开发模式？

```bash
# 停止生产模式
docker-compose -f docker-compose.prod.yml down

# 启动开发模式
docker-compose up -d
```

## 部署检查清单

- [ ] 停止开发模式容器
- [ ] 检查 `backend/.env` 配置
- [ ] 运行 `deploy-prod.sh` 脚本
- [ ] 验证服务状态（`docker ps`）
- [ ] 测试前端访问（`http://服务器IP`）
- [ ] 测试后端API（`http://服务器IP:8000/api/v1/docs`）
- [ ] 测试静态资源加载
- [ ] 检查应用日志（`docker logs`）

## 回滚方案

如果生产部署出现问题，可以快速回滚到开发模式：

```bash
# 停止生产模式
cd /path/to/inspireed-platform-main/docker
docker-compose -f docker-compose.prod.yml down

# 恢复开发模式
docker-compose up -d

# 访问地址：http://111.230.61.28:5173
```

## 技术支持

如遇问题，请提供：
1. 部署日志：`docker-compose -f docker-compose.prod.yml logs`
2. 服务状态：`docker-compose -f docker-compose.prod.yml ps`
3. 浏览器控制台错误截图
4. 后端API错误日志
