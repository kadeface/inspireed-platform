#!/bin/bash
#
# 导入 InspireEd 代码脚本
# 用途：从现有项目导入 InspireEd 代码到新项目
#

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}📥 导入 InspireEd 代码...${NC}"

# 获取脚本参数
SOURCE_DIR="${1:-../inspireed-platform-main}"  # 源项目路径
TARGET_DIR="${2:-apps/inspireed}"  # 目标目录

# 转换为绝对路径
SOURCE_DIR="$(cd "$SOURCE_DIR" 2>/dev/null && pwd || echo "$SOURCE_DIR")"
TARGET_DIR="$(cd "$(dirname "$TARGET_DIR")" 2>/dev/null && pwd)/$(basename "$TARGET_DIR")" || TARGET_DIR="$(pwd)/$TARGET_DIR"

echo -e "${BLUE}源目录: ${SOURCE_DIR}${NC}"
echo -e "${BLUE}目标目录: ${TARGET_DIR}${NC}"

# 检查源目录是否存在
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}❌ 源目录不存在: $SOURCE_DIR${NC}"
    echo "用法: $0 <源项目路径> [目标目录]"
    exit 1
fi

# 检查源目录是否有必要的文件
if [ ! -d "$SOURCE_DIR/backend" ] || [ ! -d "$SOURCE_DIR/frontend" ]; then
    echo -e "${RED}❌ 源目录中找不到 backend 或 frontend 目录${NC}"
    exit 1
fi

# 创建目标目录
mkdir -p "$TARGET_DIR"

# 复制后端代码
echo -e "${GREEN}📦 复制后端代码...${NC}"
if [ -d "$SOURCE_DIR/backend" ]; then
    cp -r "$SOURCE_DIR/backend" "$TARGET_DIR/backend"
    echo -e "${GREEN}✅ 后端代码已复制${NC}"
else
    echo -e "${YELLOW}⚠️  后端目录不存在${NC}"
fi

# 复制前端代码
echo -e "${GREEN}📦 复制前端代码...${NC}"
if [ -d "$SOURCE_DIR/frontend" ]; then
    cp -r "$SOURCE_DIR/frontend" "$TARGET_DIR/frontend"
    echo -e "${GREEN}✅ 前端代码已复制${NC}"
else
    echo -e "${YELLOW}⚠️  前端目录不存在${NC}"
fi

# 复制文档（可选）
if [ -d "$SOURCE_DIR/docs" ]; then
    echo -e "${GREEN}📄 复制文档...${NC}"
    mkdir -p docs/inspireed
    cp -r "$SOURCE_DIR/docs"/* docs/inspireed/ 2>/dev/null || true
    echo -e "${GREEN}✅ 文档已复制${NC}"
fi

# 创建 InspireEd 的 README
if [ ! -f "$TARGET_DIR/README.md" ]; then
    echo -e "${GREEN}📝 创建 README.md...${NC}"
    cat > "$TARGET_DIR/README.md" << 'EOF'
# InspireEd

探究式STEM教学系统

## 功能

- 课程设计
- 教学活动
- 学习分析
- AI 助手

## 技术栈

- 后端: FastAPI + PostgreSQL
- 前端: Vue3 + TypeScript

## 开发

```bash
# 后端
cd backend
poetry install
poetry run uvicorn app.main:app --reload

# 前端
cd frontend
pnpm install
pnpm dev
```
EOF
    echo -e "${GREEN}✅ README.md 已创建${NC}"
fi

# 清理不需要的文件
echo -e "${GREEN}🧹 清理不需要的文件...${NC}"
find "$TARGET_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$TARGET_DIR" -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
find "$TARGET_DIR" -type d -name ".git" -exec rm -rf {} + 2>/dev/null || true
find "$TARGET_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$TARGET_DIR" -type f -name "*.log" -delete 2>/dev/null || true
echo -e "${GREEN}✅ 清理完成${NC}"

echo ""
echo -e "${GREEN}✅ InspireEd 代码已导入到: $TARGET_DIR${NC}"
echo ""
echo -e "${BLUE}📋 下一步操作:${NC}"
echo "  1. 检查导入的代码: ls -la $TARGET_DIR"
echo "  2. 更新导入路径（如果需要）"
echo "  3. 安装依赖: cd $TARGET_DIR/backend && poetry install"
echo "  4. 测试运行: cd $TARGET_DIR/backend && poetry run uvicorn app.main:app --reload"
echo ""
