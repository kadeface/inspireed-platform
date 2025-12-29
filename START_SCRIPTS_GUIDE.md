# 启动脚本使用指南

## 📋 三个启动脚本对比

| 脚本 | 使用场景 | 运行方式 | 前端端口 | 前端模式 | 后端端口 | 后端模式 | Docker Compose 文件 |
|------|---------|---------|---------|---------|---------|---------|-------------------|
| `start.sh` | **本地开发** | 混合模式 | 5173 | 本地 Vite 开发服务器 | 8000 | 本地 uvicorn | `docker-compose.yml` (仅基础服务) |
| `start-prod.sh` | **生产环境部署** | 全容器化 | 80 | Docker + Nginx 生产构建 | 8000 | Docker 容器 | `docker-compose.prod.yml` |
| `start-cloudstudio.sh` | **CloudStudio 云端** | 全容器化 | 5173 | Docker + Vite 开发模式 | 8000 | Docker 容器 | `docker-compose.cloudstudio.yml` |

## 🎯 如何选择？

### 1. `start.sh` - 本地开发环境

**适用场景：**
- ✅ 本地开发调试
- ✅ 需要热重载和实时更新
- ✅ 需要频繁修改代码
- ✅ 本地机器（macOS/Linux）

**特点：**
- 基础服务（PostgreSQL、Redis、MinIO）在 Docker 中运行
- 前后端在本地运行，便于调试
- 前端使用 Vite 开发服务器（端口 5173）
- 后端使用 uvicorn 开发模式（端口 8000）

**启动命令：**
```bash
./start.sh
```

**访问地址：**
- 前端：http://localhost:5173
- 后端：http://localhost:8000
- API 文档：http://localhost:8000/docs

---

### 2. `start-prod.sh` - 生产环境部署

**适用场景：**
- ✅ 正式生产服务器
- ✅ 腾讯云/阿里云等云服务器
- ✅ 需要生产级性能
- ✅ 不需要热重载

**特点：**
- 所有服务都在 Docker 容器中运行
- 前端使用 Nginx 提供静态文件（端口 80）
- 前端是生产构建（已编译优化）
- 后端在 Docker 容器中运行（端口 8000）

**启动命令：**
```bash
./start-prod.sh
```

**访问地址：**
- 前端：http://your-server-ip 或 http://your-domain
- 后端：http://your-server-ip:8000
- API 文档：http://your-server-ip:8000/docs

---

### 3. `start-cloudstudio.sh` - CloudStudio 云端环境

**适用场景：**
- ✅ 腾讯云 CloudStudio 环境
- ✅ 云端开发/演示
- ✅ 需要 CloudStudio 的端口转发功能
- ✅ 需要热重载但使用 Docker

**特点：**
- 所有服务都在 Docker 容器中运行
- 前端使用 Vite 开发模式（端口 5173）
- 自动清理端口冲突
- 自动配置 CORS 支持 CloudStudio 域名
- 前端自动检测 CloudStudio 环境并配置 API 地址

**启动命令：**
```bash
./start-cloudstudio.sh
```

**访问地址：**
- 在 CloudStudio 的 "端口" 面板中查看：
  - 前端：`https://{id}--5173.{region}.cloudstudio.club`
  - 后端：`https://{id}--8000.{region}.cloudstudio.club`

---

## ⚠️ 常见混淆点

### 1. 端口号不同

- **开发环境** (`start.sh`): 前端 5173，后端 8000
- **生产环境** (`start-prod.sh`): 前端 80，后端 8000
- **CloudStudio** (`start-cloudstudio.sh`): 前端 5173，后端 8000

**为什么生产环境用 80？**
- 80 是 HTTP 标准端口，用户访问时不需要输入端口号
- 生产环境通常使用 Nginx 反向代理，端口 80 更专业

**为什么 CloudStudio 用 5173？**
- CloudStudio 需要特定的端口号进行端口转发
- 5173 是 Vite 开发服务器的默认端口
- CloudStudio 会自动为端口 5173 创建公网访问地址

### 2. 前端模式不同

- **开发环境**: 本地 Vite 开发服务器（热重载，未编译）
- **生产环境**: Docker + Nginx（生产构建，已编译优化）
- **CloudStudio**: Docker + Vite 开发服务器（热重载，但容器化）

### 3. 运行方式不同

- **开发环境**: 混合模式（基础服务 Docker，前后端本地）
- **生产/CloudStudio**: 全容器化（所有服务都在 Docker 中）

---

## 🔄 切换环境

### 从开发环境切换到生产环境

```bash
# 1. 停止开发环境
./stop.sh

# 2. 启动生产环境
./start-prod.sh
```

### 从生产环境切换到 CloudStudio

```bash
# 1. 停止生产环境
cd docker
docker-compose -f docker-compose.prod.yml down

# 2. 启动 CloudStudio 环境
cd ..
./start-cloudstudio.sh
```

---

## 📝 快速决策树

```
需要启动服务？
│
├─ 在本地开发？
│  └─ 使用 start.sh
│
├─ 在 CloudStudio？
│  └─ 使用 start-cloudstudio.sh
│
└─ 在生产服务器？
   └─ 使用 start-prod.sh
```

---

## 🛠️ 故障排查

### 端口冲突

如果遇到端口被占用：

**开发环境 (start.sh):**
```bash
# 检查端口占用
lsof -i:5173
lsof -i:8000

# 停止占用进程
kill -9 $(lsof -ti:5173)
kill -9 $(lsof -ti:8000)
```

**CloudStudio (start-cloudstudio.sh):**
- 脚本会自动清理端口 5173
- 如果仍然失败，手动执行：
```bash
./scripts/fix-port-5173.sh
```

**生产环境 (start-prod.sh):**
```bash
# 检查 Docker 容器
docker ps | grep 80
docker ps | grep 8000

# 停止容器
docker stop <container_id>
```

### 选择错误的脚本

如果使用了错误的脚本：

1. **停止当前服务**
2. **查看本文档选择正确的脚本**
3. **使用正确的脚本重新启动**

---

## 💡 最佳实践

1. **开发阶段**: 使用 `start.sh` 进行本地开发
2. **测试阶段**: 使用 `start-cloudstudio.sh` 在 CloudStudio 中测试
3. **生产部署**: 使用 `start-prod.sh` 部署到生产服务器

---

## 📚 相关文档

- [CloudStudio 快速启动指南](./CLOUDSTUDIO_QUICK_START.md)
- [腾讯云端部署指南](./TENCENT_CLOUD_DEPLOYMENT.md)
- [Docker 部署说明](./docker/README.md)

