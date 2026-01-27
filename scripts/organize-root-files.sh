#!/bin/bash
#
# 整理根目录零散文件脚本
# 用途：将根目录的零散文件移动到 docs 目录的相应子目录
#

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}📁 开始整理根目录零散文件...${NC}"
echo ""

# 获取脚本所在目录的根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT_DIR"

# 创建 docs 目录结构
echo -e "${GREEN}✅ 创建 docs 目录结构...${NC}"
mkdir -p docs/guides
mkdir -p docs/fixes
mkdir -p docs/deployment
mkdir -p docs/debug
mkdir -p docs/interactive-content
mkdir -p docs/tests
mkdir -p docs/misc
mkdir -p docs/examples

# 移动开发指南文档
echo -e "${BLUE}📚 移动开发指南文档...${NC}"
for file in QUICK_START*.md START_SCRIPTS_GUIDE.md; do
    if [ -f "$file" ]; then
        mv "$file" docs/guides/ && echo "  ✅ $file -> docs/guides/"
    fi
done

# 移动问题修复文档
echo -e "${BLUE}🔧 移动问题修复文档...${NC}"
for file in FIX_*.md ACTIVITY_MODULE_FIX_README.md BACKEND_RESTART_REQUIRED.md; do
    if [ -f "$file" ]; then
        mv "$file" docs/fixes/ && echo "  ✅ $file -> docs/fixes/"
    fi
done

# 移动部署相关文档
echo -e "${BLUE}🚀 移动部署相关文档...${NC}"
for file in *CLOUDSTUDIO*.md TENCENT_CLOUD*.md DOCKER_COMPOSE*.md; do
    if [ -f "$file" ]; then
        mv "$file" docs/deployment/ && echo "  ✅ $file -> docs/deployment/"
    fi
done

# 移动调试文档
echo -e "${BLUE}🐛 移动调试文档...${NC}"
for file in DEBUG_*.md CONFIG_LOADING*.md; do
    if [ -f "$file" ]; then
        mv "$file" docs/debug/ && echo "  ✅ $file -> docs/debug/"
    fi
done

# 移动 HTML 互动内容
echo -e "${BLUE}🎮 移动 HTML 互动内容...${NC}"
for file in *.html; do
    if [ -f "$file" ]; then
        mv "$file" docs/interactive-content/ && echo "  ✅ $file -> docs/interactive-content/"
    fi
done

# 移动测试文件
echo -e "${BLUE}🧪 移动测试文件...${NC}"
for file in test_*.py test-*.html DEBUG_SCRIPT.js; do
    if [ -f "$file" ]; then
        mv "$file" docs/tests/ && echo "  ✅ $file -> docs/tests/"
    fi
done

# 移动其他文档和资源
echo -e "${BLUE}💡 移动其他文档和资源...${NC}"
for file in AI_ASSISTANT*.md VIDEO_SCRIPT*.md X6_MIGRATION*.md "InspireEd"*.md assets_tmp_*.png assets_tmp_*.jpg assets_tmp_*.jpeg; do
    if [ -f "$file" ]; then
        mv "$file" docs/misc/ && echo "  ✅ $file -> docs/misc/"
    fi
done

# 移动示例代码
echo -e "${BLUE}📝 移动示例代码...${NC}"
for file in app.py main.py languages.py; do
    if [ -f "$file" ] && [ ! -f "backend/$file" ] && [ ! -f "frontend/$file" ]; then
        mv "$file" docs/examples/ && echo "  ✅ $file -> docs/examples/"
    fi
done

echo ""
echo -e "${GREEN}✅ 文件整理完成！${NC}"
echo ""
echo -e "${BLUE}📊 整理统计:${NC}"
echo "  📚 guides: $(ls -1 docs/guides/*.md 2>/dev/null | wc -l | xargs) 个文件"
echo "  🔧 fixes: $(ls -1 docs/fixes/*.md 2>/dev/null | wc -l | xargs) 个文件"
echo "  🚀 deployment: $(ls -1 docs/deployment/*.md 2>/dev/null | wc -l | xargs) 个文件"
echo "  🐛 debug: $(ls -1 docs/debug/*.md 2>/dev/null | wc -l | xargs) 个文件"
echo "  🎮 interactive-content: $(ls -1 docs/interactive-content/*.html 2>/dev/null | wc -l | xargs) 个文件"
echo "  🧪 tests: $(ls -1 docs/tests/* 2>/dev/null | wc -l | xargs) 个文件"
echo "  💡 misc: $(ls -1 docs/misc/* 2>/dev/null | wc -l | xargs) 个文件"
echo "  📝 examples: $(ls -1 docs/examples/* 2>/dev/null | wc -l | xargs) 个文件"
echo ""
echo -e "${BLUE}📋 查看详细结构:${NC}"
echo "  cat docs/README.md"
