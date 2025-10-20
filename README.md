# InspireEd 教师教研系统

基于 Jupyter 式架构的教学评研一体化平台

## 项目概述

InspireEd 是一个融合富文本、可执行代码单元（Cell）、仿真预览、AI 辅助答疑与数据采集的教学与教研闭环系统。

### 核心特性

- 🎨 **可执行教案**：支持7种Cell类型（Text/Code/Param/Sim/QA/Chart/Contest）
- 🔬 **浏览器端执行**：JupyterLite + Pyodide 零后端执行
- 🤖 **AI 辅助**：教师助手、学生答疑、教研分析
- 📊 **数据驱动**：完整的教学行为数据采集与可视化
- 🏫 **多角色支持**：教师、学生、教研员统一平台

## 技术栈

### 前端
- Vue3 + TypeScript + Vite
- TipTap（富文本编辑器）
- CodeMirror 6（代码编辑）
- JupyterLite（浏览器端Python执行）
- TailwindCSS + Shadcn/UI
- Pinia（状态管理）

### 后端
- FastAPI + Python 3.10+
- PostgreSQL + TimescaleDB（主数据库）
- Redis（缓存）
- MinIO（对象存储）
- Kafka + ClickHouse（日志分析）
- JupyterHub（服务端执行引擎）

### AI 集成
- LangChain
- OpenAI GPT-4
- FAISS（向量检索）

## 项目结构

```
inspireed-platform/
├── frontend/          # Vue3 前端应用
├── backend/           # FastAPI 后端服务
├── shared/            # 共享类型定义与工具
├── docker/            # Docker 配置文件
├── docs/              # 项目文档
└── .github/           # CI/CD 配置
```

## 快速启动

### 前置要求

- Node.js 18+
- Python 3.10+
- Docker 和 Docker Compose
- pnpm 8+

### 1. 启动基础服务

```bash
cd docker
docker-compose up -d
```

这将启动：
- PostgreSQL (端口 5432)
- Redis (端口 6379)
- MinIO (端口 9000/9001)
- Kafka + Zookeeper (端口 9092)

### 2. 启动后端服务

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（如果不存在）
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 创建环境配置文件
cp env.example .env

# 运行数据库迁移
alembic upgrade head

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端将运行在 http://localhost:8000
API文档: http://localhost:8000/docs

### 3. 启动前端服务

```bash
# 进入前端目录
cd frontend

# 安装依赖
pnpm install

# 创建环境配置文件
cp env.example .env.local

# 启动前端开发服务器
pnpm dev
```

前端将运行在 http://localhost:5173

### 4. 验证服务状态

```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 检查前端服务
curl http://localhost:5173
```

## 开发模式启动

### 后端开发

```bash
# 进入后端目录
cd backend
source venv/bin/activate

# 开发模式启动（自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或者使用更详细的日志
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

### 前端开发

```bash
# 进入前端目录
cd frontend

# 开发模式启动
pnpm dev

# 或者指定端口
pnpm dev --port 3000

# 或者监听所有网络接口
pnpm dev --host
```

### 一键启动脚本

项目提供了便捷的启动脚本：

```bash
# 启动所有服务
./start.sh

# 停止所有服务
./stop.sh

# 重启所有服务
./restart.sh
```

这些脚本会自动：
- 启动 Docker 基础服务
- 创建虚拟环境和安装依赖
- 运行数据库迁移
- 启动后端和前端服务
- 显示访问地址和测试账号信息

## 常见问题

### 后端启动问题

**问题：bcrypt 版本兼容性错误**
```bash
# 解决方案：降级 bcrypt 版本
pip install "bcrypt<4.0.0" --force-reinstall
```

**问题：数据库连接失败**
```bash
# 检查 Docker 服务状态
docker-compose ps

# 重启数据库服务
docker-compose restart postgres
```

**问题：CORS 配置错误**
```bash
# 检查 .env 文件中的 BACKEND_CORS_ORIGINS 配置
# 应该是 JSON 格式：["http://localhost:5173","http://localhost:3000"]
```

### 前端启动问题

**问题：依赖安装失败**
```bash
# 清理缓存重新安装
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

**问题：端口被占用**
```bash
# 查找占用端口的进程
lsof -i :5173

# 杀死进程
kill -9 <PID>

# 或使用其他端口
pnpm dev --port 3000
```

### 服务停止

```bash
# 停止所有 Docker 服务
cd docker && docker-compose down

# 停止后端服务
pkill -f "uvicorn app.main:app"

# 停止前端服务
pkill -f "pnpm dev"
```

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.10+
- Docker & Docker Compose
- pnpm 8+

### 安装依赖

```bash
# 前端
cd frontend
pnpm install

# 后端
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 启动开发环境

```bash
# 启动数据库等基础服务
docker-compose up -d

# 启动后端
cd backend
uvicorn app.main:app --reload

# 启动前端
cd frontend
pnpm dev
```

## 开发指南

详见 [docs/development.md](docs/development.md)

## 架构设计

详见 [docs/architecture.md](docs/architecture.md)

## 许可证

MIT License

## 联系方式

- 项目主页：[GitHub](https://github.com/your-org/inspireed)
- 问题反馈：[Issues](https://github.com/your-org/inspireed/issues)

前端地址：http://localhost:5173
后端API：http://localhost:8000
API文档：http://localhost:8000/docs

## 测试账号

### 管理员账号
- 邮箱：admin@inspireed.com
- 密码：admin123
- 角色：管理员（跳转到教师工作台）

### 教师账号
- 邮箱：teacher@inspireed.com
- 密码：teacher123
- 角色：教师

### 学生账号
- 邮箱：student@inspireed.com
- 密码：student123
- 角色：学生

### 研究员账号
- 邮箱：researcher@inspireed.com
- 密码：researcher123
- 角色：研究员