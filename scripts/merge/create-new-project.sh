#!/bin/bash
#
# 创建新项目脚本
# 用途：创建新的 inspireed-platform 项目，并设置基础结构
#

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 创建新项目 inspireed-platform...${NC}"

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_DIR="$(pwd)"

# 默认新项目路径（当前目录的兄弟目录）
if [ -z "$1" ]; then
    NEW_PROJECT_DIR="$(cd "$CURRENT_DIR/.." && pwd)/inspireed-platform"
else
    NEW_PROJECT_DIR="$(cd "$1" && pwd)"
fi

echo -e "${BLUE}新项目路径: ${NEW_PROJECT_DIR}${NC}"

# 检查目录是否已存在
if [ -d "$NEW_PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠️  目录已存在: $NEW_PROJECT_DIR${NC}"
    read -p "是否继续？（将覆盖现有文件）(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 1
    fi
fi

# 创建项目目录
mkdir -p "$NEW_PROJECT_DIR"
cd "$NEW_PROJECT_DIR"

echo -e "${GREEN}✅ 创建目录结构...${NC}"

# 创建基础目录结构
mkdir -p apps/{inspireed,app2}
mkdir -p shared/{models/shared,schemas/shared,api/v1/shared,utils,types}
mkdir -p infrastructure/{docker,database/{migrations/versions,seeds},k8s}
mkdir -p docs/{architecture,guides,inspireed,app2}
mkdir -p scripts/{setup,dev,deploy,tools}
mkdir -p .github/workflows
mkdir -p .vscode

# 创建 Python 包结构
touch shared/__init__.py
touch shared/models/__init__.py
touch shared/models/shared/__init__.py
touch shared/schemas/__init__.py
touch shared/schemas/shared/__init__.py
touch shared/api/__init__.py
touch shared/utils/__init__.py

echo -e "${GREEN}✅ 创建基础配置文件...${NC}"

# 创建 package.json
cat > package.json << 'EOF'
{
  "name": "inspireed-platform",
  "version": "1.0.0",
  "private": true,
  "description": "InspireEd Platform - Multi-Application Platform",
  "workspaces": [
    "apps/*/frontend",
    "shared"
  ],
  "scripts": {
    "dev": "pnpm -r --parallel dev",
    "build": "pnpm -r build",
    "test": "pnpm -r test",
    "lint": "pnpm -r lint",
    "format": "prettier --write \"**/*.{ts,tsx,js,jsx,json,md}\""
  },
  "devDependencies": {
    "prettier": "^3.0.0",
    "typescript": "^5.0.0"
  },
  "engines": {
    "node": ">=18.0.0",
    "pnpm": ">=8.0.0"
  }
}
EOF

# 创建 pnpm-workspace.yaml
cat > pnpm-workspace.yaml << 'EOF'
packages:
  - 'apps/*/frontend'
  - 'shared'
EOF

# 创建 pyproject.toml
cat > pyproject.toml << 'EOF'
[tool.poetry]
name = "inspireed-platform"
version = "1.0.0"
description = "InspireEd Platform - Multi-Application Platform"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.10"

[tool.poetry.group.shared.dependencies]
fastapi = "^0.100.0"
sqlalchemy = "^2.0.0"
alembic = "^1.12.0"
asyncpg = "^0.29.0"
pydantic = "^2.0.0"
pydantic-settings = "^2.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
black = "^23.0.0"
ruff = "^0.1.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF

# 创建 .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/
dist/
build/
.pytest_cache/

# Node
node_modules/
.pnpm-store/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
.env.*.local

# Database
*.db
*.sqlite

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db

# Docker
.docker/

# Coverage
.coverage
htmlcov/

# Temporary
tmp/
temp/
*.tmp

# Backup
*.tar.gz
backup/
EOF

# 创建主 README.md
cat > README.md << 'EOF'
# InspireEd Platform

多应用统一平台，支持多个应用共享基础设施和基础数据。

## 📋 应用列表

- **InspireEd**: 探究式STEM教学系统
- **App2**: [应用2描述]

## 🏗️ 项目结构

```
inspireed-platform/
├── apps/              # 应用目录
│   ├── inspireed/     # InspireEd 应用
│   └── app2/          # 应用2
├── shared/            # 共享代码
├── infrastructure/    # 基础设施
├── docs/              # 文档
└── scripts/           # 脚本
```

## 🚀 快速开始

### 前置要求

- Node.js 18+
- Python 3.10+
- Docker & Docker Compose
- pnpm 8+
- Poetry (Python 包管理)

### 安装依赖

```bash
# 安装前端依赖
pnpm install

# 安装 Python 依赖
poetry install
```

### 启动开发环境

```bash
# 启动所有服务
./scripts/dev/start-all.sh
```

详细说明请查看 [docs/guides/getting-started.md](docs/guides/getting-started.md)

## 📚 文档

- [快速开始](docs/guides/getting-started.md)
- [架构设计](docs/architecture/overview.md)
- [开发指南](docs/guides/development.md)
- [部署指南](docs/guides/deployment.md)

## 🛠️ 开发

```bash
# 安装依赖
pnpm install
poetry install

# 运行测试
pnpm test
poetry run pytest

# 代码格式化
pnpm format
poetry run black .
```

## 📝 许可证

MIT License
EOF

# 创建基础文档
cat > docs/guides/getting-started.md << 'EOF'
# 快速开始指南

## 安装

1. 克隆项目
2. 安装依赖
3. 配置环境变量
4. 启动服务

详细说明待完善...
EOF

# 初始化 Git 仓库
if [ ! -d .git ]; then
    echo -e "${GREEN}✅ 初始化 Git 仓库...${NC}"
    git init
    git branch -M main
    git add .
    git commit -m "chore: initial project structure"
    echo -e "${GREEN}✅ Git 仓库已初始化${NC}"
else
    echo -e "${YELLOW}⚠️  Git 仓库已存在${NC}"
fi

echo ""
echo -e "${GREEN}✅ 新项目创建完成！${NC}"
echo ""
echo -e "${BLUE}📂 项目路径: ${NEW_PROJECT_DIR}${NC}"
echo ""
echo -e "${BLUE}📋 下一步操作:${NC}"
echo "  1. 查看合并计划: docs/PROJECT_MERGE_PLAN_NEW.md"
echo "  2. 导入 InspireEd 代码: ./scripts/setup/import-inspireed.sh"
echo "  3. 导入应用2代码"
echo "  4. 创建共享代码"
echo ""
echo -e "${BLUE}💡 提示:${NC}"
echo "  - 进入项目目录: cd $NEW_PROJECT_DIR"
echo "  - 查看项目结构: tree -L 2"
echo "  - 添加远程仓库: git remote add origin <repository-url>"
echo ""
