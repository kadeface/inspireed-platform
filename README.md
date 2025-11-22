# InspireEd 探究式STEM教学系统

基于建构主义与循证教育的PDCA教学质量管理平台

## 项目概述

InspireEd 是一个面向STEM教育的探究式学习与教学平台，基于建构主义学习理论、5E教学模型和循证教育(Evidence-based Education)理念，构建完整的PDCA教学质量管理循环。

平台整合多模态教学资源（富文本、可执行代码、PhET交互仿真、评估工具等），支持系统化课程设计、结构化活动实施、过程性评估与数据驱动的持续改进，为教育工作者提供科学化、专业化的教学支持工具。

### 核心特性

#### 双循环理论框架

平台构建**教学管理循环**与**学习活动循环**的双循环协同体系：

##### 🔄 PDCA教学质量管理循环（教师视角）

- 📋 **Plan（系统化设计）**  
  基于布鲁姆分类法(Bloom's Taxonomy)和能力本位框架，构建层次化知识图谱与学习目标体系

- 🚀 **Do（结构化实施）**  
  整合多模态教学资源，支持5E教学模型(Engage-Explore-Explain-Elaborate-Evaluate)，创建符合学习科学的活动序列

- ✅ **Check（过程性评估）**  
  基于建构主义理论的探究式学习，多维度采集认知过程数据与学习行为轨迹

- 🔄 **Act（循证改进）**  
  运用学习分析(Learning Analytics)技术，生成可操作的教学洞察，支持循证决策与持续改进

##### 🌟 5E科学学习活动循环（学生视角）

- 🎯 **Engage（参与投入）**  
  激发好奇心，引发认知冲突，建立学习动机与问题意识

- 🔍 **Explore（探索发现）**  
  动手实验操作，收集观察数据，形成初步概念理解

- 💡 **Explain（解释建构）**  
  表达个人理解，建构科学概念，形成系统化解释

- 🚀 **Elaborate（深化拓展）**  
  应用新学知识，实现概念迁移，解决实际问题

- ✨ **Evaluate（评价反思）**  
  评估学习成果，反思认知过程，发展元认知能力

> **双循环协同**：教学管理循环指导和优化学习活动循环，学习活动循环为教学管理循环提供数据反馈

#### 技术特性

- 🎓 **教育理论支撑**：建构主义、探究式学习、计算思维、学习科学
- 🧩 **多模态资源**：交互式Notebook、PhET仿真、代码执行环境、评估工具
- 📊 **学习分析**：过程性数据采集、可视化分析、教学洞察生成
- 🤖 **AI增强**：智能问答、自动评分、个性化推荐、教学建议

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
- DeepSeek
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

## 开发规范

- 在提交 Python 代码前，必须运行 `poetry run black .`（或本地安装的 `black .`）进行格式化，并确保 `poetry run black --check .` 通过。

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
- **自动检测并显示局域网访问地址** ✨
- 显示本机和局域网访问地址
- 显示测试账号信息

## 🌐 局域网访问配置

### ⚡ 自动适配（零配置）

**系统已实现IP地址自动适配，无需手动修改配置！**

- ✅ **前端自动检测**: 根据访问地址自动匹配后端API
- ✅ **后端智能CORS**: 自动允许所有局域网IP段访问
- ✅ **即开即用**: 启动服务后直接使用任意局域网IP访问

**使用方法**:
```bash
# 1. 启动服务
./start.sh

# 2. 查看访问地址（会自动显示）
# 本机: http://localhost:5173
# 局域网: http://你的IP:5173

# 3. 从任意设备访问（无需配置）
# 手机/平板/其他电脑直接访问局域网地址即可
```

**技术原理**:
- 前端使用 `window.location.hostname` 动态检测访问IP
- 后端使用正则表达式匹配 `192.168.x.x` 和 `10.x.x.x` IP段
- 详细说明: [自动适配指南](docs/AUTO_ADAPT_GUIDE.md)

---

### 快速配置（可选）

运行自动配置脚本：

```bash
./get-network-info.sh
```

脚本会：
- 自动检测服务器 IP 地址
- 显示所有访问地址
- 提供配置建议
- 可选自动更新配置文件

### 手动配置

1. **获取服务器 IP 地址**
   ```bash
   # macOS/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # Windows
   ipconfig
   ```

2. **配置后端 CORS** (`backend/.env`)
   ```bash
   BACKEND_CORS_ORIGINS=http://localhost:5173,http://192.168.1.100:5173
   ```
   （将 `192.168.1.100` 替换为你的实际 IP）

3. **配置前端 API 地址** (`frontend/.env.local`)
   ```bash
   VITE_API_BASE_URL=http://192.168.1.100:8000/api/v1
   ```

4. **重启服务**
   ```bash
   ./restart.sh
   ```

5. **从其他设备访问**
   ```
   http://192.168.1.100:5173
   ```

### 移动设备访问

确保移动设备连接到同一 WiFi 网络，然后使用服务器 IP 地址访问。

**详细配置指南**: 查看 [网络访问指南](docs/network/NETWORK_ACCESS_GUIDE.md)

## 常见问题

### 🔥 教师端无法在其他电脑上保存教学设计

**快速修复**:
```bash
# 运行一键修复脚本
./fix-network-issue.sh

# 或运行诊断
./diagnose-network.sh
```

**详细文档**: 
- 快速指南: [README_NETWORK_FIX.md](README_NETWORK_FIX.md)
- 完整排查: [docs/network/TEACHER_STORAGE_ISSUE.md](docs/network/TEACHER_STORAGE_ISSUE.md)
- 远程测试工具: [test-from-remote.html](test-from-remote.html)

---

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

## 最新功能

### 🎬 教师端全屏预览功能（2025-11-05）

教师在设计教学案例后，现在可以使用全屏预览功能，以沉浸式的方式查看教学内容。

**主要特性：**
- 一键进入全屏预览模式
- 以学生视角完整查看教学内容
- 支持键盘快捷键（Esc）快速退出
- 流畅的过渡动画和优化的滚动体验
- 浮动"返回顶部"按钮，方便长内容导航

**使用方法：**
1. 在教案编辑页面，点击顶部工具栏的"全屏预览"按钮（紫色按钮）
2. 查看教学内容的完整展示效果
3. 点击"退出预览"按钮或按 `Esc` 键退出

**详细文档：**
- [全屏预览功能使用指南](docs/features/FULLSCREEN_PREVIEW_GUIDE.md)
- [全屏预览快速开始](docs/guides/QUICK_START_FULLSCREEN_PREVIEW.md)
- [全屏预览功能测试指南](docs/testing/TEST_FULLSCREEN_PREVIEW.md)

## 📚 完整文档

查看 [docs/README.md](docs/README.md) 获取完整的文档目录和分类索引。

### 快速链接

- **[快速开始指南](docs/guides/)** - 各项功能快速上手
- **[网络配置文档](docs/network/)** - 网络访问和配置
- **[设计文档](docs/design/)** - 系统架构和设计理念
- **[学习科学文档](docs/learning-science/)** - 学习科学理论与实践
- **[功能文档](docs/features/)** - 各项功能详细说明
- **[测试文档](docs/testing/)** - 功能测试指南
- **[变更日志](docs/CHANGELOG.md)** - 版本变更历史

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