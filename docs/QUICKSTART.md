# InspireEd 快速启动指南

## 🚀 快速开始

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

### 2. 配置后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env.example .env
# 编辑 .env 文件，设置数据库连接等

# 运行数据库迁移
alembic upgrade head

# 启动后端服务
uvicorn app.main:app --reload
```

后端将运行在 http://localhost:8000
API文档: http://localhost:8000/docs

### 3. 配置前端

```bash
cd frontend

# 安装依赖
pnpm install

# 配置环境变量
cp env.example .env.local
# 编辑 .env.local，设置API地址

# 启动前端服务
pnpm dev
```

前端将运行在 http://localhost:5173

## 📝 默认账户

首次运行时，系统会创建超级管理员账户：

- 邮箱: admin@inspireed.com
- 密码: admin123

## ✅ 已实现功能

### 前端 (Vue3)

✅ **基础设施**
- Monorepo 项目结构
- Vue3 + TypeScript + Vite
- Pinia 状态管理
- Vue Router 路由配置
- TailwindCSS 样式系统

✅ **Cell 组件系统**
- TextCell - 富文本编辑 (TipTap集成)
- CodeCell - 代码编辑与执行 (CodeMirror 6)
- ParamCell - 参数配置表单
- SimCell - 仿真容器
- QACell - 问答交互
- ChartCell - 图表可视化
- ContestCell - 竞技排行榜

✅ **编辑器功能**
- TipTap 富文本编辑器
- 工具栏（粗体、斜体、标题、列表等）
- 图片插入
- 代码块支持

✅ **页面与路由**
- 登录/注册页面
- 教师工作台
- 学生工作台
- 教研工作台
- 角色权限路由守卫

✅ **状态管理**
- User Store (用户状态)
- Lesson Store (教案状态)
- Cell 管理 (增删改查)

### 后端 (FastAPI)

✅ **基础设施**
- FastAPI 应用框架
- SQLAlchemy 异步ORM
- Alembic 数据库迁移
- PostgreSQL + TimescaleDB
- Redis 缓存
- MinIO 对象存储

✅ **认证系统**
- JWT Token 认证
- OAuth2 密码流
- 用户注册/登录
- 角色权限 (RBAC)
- 密码加密 (bcrypt)

✅ **数据模型**
- User (用户)
- Lesson (教案)
- Cell (单元)
- ExecutionLog (执行日志)
- QARecord (问答记录)

✅ **API 服务**
- 用户认证 (/auth/login, /auth/register, /auth/me)
- 用户管理 (/users)
- 教案CRUD (/lessons)
  - 创建/更新/删除教案
  - 教案列表（分页、搜索）
  - 发布教案
  - 复制教案

✅ **配置与部署**
- Docker Compose 配置
- 环境变量管理
- CI/CD (GitHub Actions)
- 代码规范 (ESLint, Black, MyPy)

## 🔧 开发中功能

以下功能已有基础实现，待完善：

- [ ] JupyterLite/JupyterHub 集成（代码执行）
- [ ] 仿真引擎集成（Three.js/Matter.js）
- [ ] AI 问答系统（LangChain + OpenAI）
- [ ] 数据中台（Kafka + ClickHouse）
- [ ] 可视化看板
- [ ] 编辑器高级功能（拖拽排序、版本对比）

## 📚 下一步

1. 安装依赖并启动服务
2. 访问前端界面进行注册/登录
3. 探索教案编辑功能
4. 查看 API 文档了解接口

## 🐛 常见问题

**Q: 数据库连接失败？**
A: 确保 Docker 服务已启动：`docker-compose ps`

**Q: 前端无法连接API？**
A: 检查 `.env.local` 中的 `VITE_API_BASE_URL` 是否正确

**Q: 依赖安装失败？**
A: 尝试升级包管理器：
- Python: `python -m pip install --upgrade pip`
- Node: `npm install -g pnpm@latest`

## 📖 更多文档

- [开发指南](./development.md)
- [架构设计](./architecture.md)
- [API 文档](http://localhost:8000/docs)

---

**项目状态**: 🟡 MVP 开发中
**最后更新**: 2025-10-10

