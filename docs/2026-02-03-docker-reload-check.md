# Docker 与前端加载时间核对（2026-02-03）

## 一、当前状态

### 1. 文件最后修改时间

| 文件 | 最后修改时间 | 说明 |
|------|--------------|------|
| `frontend/src/services/api.ts` | **Feb 3 12:11** | 今日修改（方案 C + 运行时兜底） |
| `frontend/vite.config.ts` | Feb 2 22:12 | 代理已启用 |
| `docker/docker-compose.yml` | Feb 2 19:52 | - |
| `docker/.env` | Jan 29 19:36 | - |

### 2. Docker 镜像构建时间

| 镜像 | 创建时间 | 说明 |
|------|----------|------|
| **docker-frontend:latest** | **2026-02-02 16:52:25** | 早于 api.ts 修改，不包含今日修复 |
| docker-backend:latest | 2026-02-02 19:53:44 | - |

### 3. 当前运行的容器

- **inspireed-postgres**：Up About a minute（健康）
- **inspireed-redis**：Up About a minute（健康）
- **inspireed-minio**：Up About a minute（健康）
- **inspireed-backend**：**未在运行**
- **inspireed-frontend**：**未在运行**

---

## 二、结论

1. **前端镜像比 api.ts 旧**  
   - 前端镜像构建于 **2 月 2 日 16:52**，`api.ts` 修改于 **2 月 3 日 12:11**。  
   - 若通过 **Docker 前端容器**（如 `http://localhost:80`）访问，当前镜像**没有**今日的 api.ts 修复，仍会直连 `localhost:8000`，导致教案 401。

2. **若用 Docker 跑前端，必须重新构建并重启**  
   - 需要：`docker compose build frontend --no-cache`（或 `docker build` 前端）  
   - 然后：`docker compose up -d frontend`（或你的启动方式）

3. **若用本机 `pnpm dev` 跑前端**  
   - 访问 `http://localhost:5173` 时，Vite 直接读源码，会用到最新的 api.ts。  
   - 此时 401 更可能是：未重启 dev 服务器、浏览器缓存、或访问的不是 5173（例如访问的是 80 端口的旧前端）。

---

## 三、推荐操作（按你实际用法选一种）

### 方式 A：本机跑前端（推荐，便于调试）

```bash
# 1. 确保后端在运行（本机或 Docker 的 8000 端口）
# 2. 前端用最新源码
cd /Users/382241106qq.com/inspireed-platform-main/frontend
pnpm dev
# 3. 浏览器只访问 http://localhost:5173（不要用 80 端口）
```

### 方式 B：用 Docker 跑前端（需重新构建）

```bash
cd /Users/382241106qq.com/inspireed-platform-main/docker
# 重新构建前端镜像（会包含最新 api.ts）
docker compose build frontend --no-cache
# 启动前端容器
docker compose up -d frontend
# 访问 http://localhost:80
```

### 方式 C：全栈 Docker 并全部用最新代码

```bash
cd /Users/382241106qq.com/inspireed-platform-main/docker
docker compose build --no-cache frontend backend
docker compose up -d
```

---

## 四、如何确认“已重新加载”

- **本机 pnpm dev**：改完 api.ts 后重启一次 `pnpm dev`，浏览器硬刷新（Ctrl+Shift+R）。控制台应出现 `[API] 本地开发强制使用代理 /api/v1` 或 `[API] 运行时兜底：强制使用代理 /api/v1`。
- **Docker 前端**：执行上述 build + up 后，访问 http://localhost:80，同样看控制台是否有上述日志；Network 里教案请求应为 `http://localhost/api/v1/lessons/...`（同源），而不是 `http://localhost:8000/...`。
