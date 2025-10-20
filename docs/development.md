# InspireEd 开发指南

## 快速开始

### 环境准备

确保已安装以下工具：

- **Node.js** 18+ 和 pnpm 8+
- **Python** 3.10+
- **Docker** 和 Docker Compose
- **Git**

### 克隆项目

```bash
git clone <repository-url>
cd inspireed-platform
```

### 后端开发

1. **创建虚拟环境并安装依赖**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **配置环境变量**

```bash
cp env.example .env
# 编辑 .env 文件，配置数据库连接等参数
```

3. **启动基础服务**

```bash
cd ../docker
docker-compose up -d
```

4. **运行数据库迁移**

```bash
cd ../backend
alembic upgrade head
```

5. **启动开发服务器**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档。

### 前端开发

1. **安装依赖**

```bash
cd frontend
pnpm install
```

2. **配置环境变量**

创建 `.env.local` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

3. **启动开发服务器**

```bash
pnpm dev
```

访问 http://localhost:5173

## 项目结构

```
inspireed-platform/
├── frontend/           # Vue3 前端应用
│   ├── src/
│   │   ├── components/ # 组件
│   │   ├── pages/      # 页面
│   │   ├── store/      # Pinia 状态管理
│   │   ├── services/   # API 服务
│   │   ├── router/     # 路由配置
│   │   └── types/      # TypeScript 类型定义
│   └── package.json
├── backend/            # FastAPI 后端
│   ├── app/
│   │   ├── api/        # API 路由
│   │   ├── models/     # 数据库模型
│   │   ├── schemas/    # Pydantic schemas
│   │   ├── services/   # 业务逻辑
│   │   └── core/       # 核心配置
│   ├── alembic/        # 数据库迁移
│   └── tests/          # 测试
├── docker/             # Docker 配置
└── docs/               # 文档
```

## 开发规范

### 前端代码规范

- 使用 TypeScript 进行类型检查
- 遵循 ESLint 规则
- 使用 Prettier 格式化代码
- 组件使用 Composition API
- 遵循 Vue3 官方风格指南

### 后端代码规范

- 使用 Python 类型提示
- 遵循 PEP 8 代码风格
- 使用 Black 格式化代码
- 使用 MyPy 进行类型检查
- API 使用 RESTful 设计原则

### Git 提交规范

使用约定式提交（Conventional Commits）：

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建工具或辅助工具的变动
```

示例：
```bash
git commit -m "feat: 添加教案编辑器核心功能"
git commit -m "fix: 修复用户登录token过期问题"
```

## 数据库迁移

### 创建新迁移

```bash
cd backend
alembic revision --autogenerate -m "描述变更内容"
```

### 应用迁移

```bash
alembic upgrade head
```

### 回滚迁移

```bash
alembic downgrade -1  # 回滚一个版本
```

## 测试

### 前端测试

```bash
cd frontend
pnpm test
```

### 后端测试

```bash
cd backend
pytest
pytest --cov=app tests/  # 带覆盖率
```

## 常见问题

### 数据库连接失败

确保 Docker 服务正在运行：
```bash
docker-compose ps
```

### 前端无法连接后端API

检查 `.env.local` 中的 `VITE_API_BASE_URL` 配置是否正确。

### Python依赖安装失败

尝试升级 pip：
```bash
python -m pip install --upgrade pip
```

## 更多资源

- [Vue3 文档](https://vuejs.org/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [TipTap 文档](https://tiptap.dev/)
- [Pinia 文档](https://pinia.vuejs.org/)

