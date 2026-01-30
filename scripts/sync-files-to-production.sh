#!/bin/bash
# 文件同步脚本：从 dev 同步特定文件到 production-deploy
# 用法: ./scripts/sync-files-to-production.sh <file1> <file2> ...

set -e

if [ $# -eq 0 ]; then
    echo "❌ 错误: 请提供至少一个文件路径"
    echo ""
    echo "用法:"
    echo "  ./scripts/sync-files-to-production.sh <file1> <file2> ..."
    echo ""
    echo "示例:"
    echo "  ./scripts/sync-files-to-production.sh backend/app/api/v1/classroom_sessions.py"
    echo "  ./scripts/sync-files-to-production.sh backend/app/api/v1/classroom_sessions.py frontend/src/pages/Student/LessonView.vue"
    exit 1
fi

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔄 检查当前分支状态...${NC}"
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "dev" ] && [ "$CURRENT_BRANCH" != "production-deploy" ]; then
    echo -e "${RED}⚠️  警告: 当前不在 dev 或 production-deploy 分支${NC}"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${YELLOW}📋 准备同步以下文件:${NC}"
for file in "$@"; do
    if [ -f "$file" ] || git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
        echo "  ✅ $file"
    else
        echo -e "  ${RED}❌ $file (文件不存在)${NC}"
        exit 1
    fi
done

echo ""
read -p "确认从 dev 分支同步这些文件到 production-deploy? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消"
    exit 1
fi

echo -e "${YELLOW}🔄 切换到 production-deploy 分支...${NC}"
git checkout production-deploy

echo -e "${YELLOW}📥 拉取最新代码...${NC}"
git pull origin production-deploy || echo "⚠️  拉取失败，继续..."

echo -e "${YELLOW}📁 从 dev 分支检出文件...${NC}"
git checkout dev -- "$@"

echo ""
echo -e "${GREEN}✅ 文件已同步！${NC}"
echo ""
echo "📝 下一步:"
echo "  1. 检查更改: git status"
echo "  2. 查看差异: git diff --cached"
echo "  3. 提交更改:"
echo "     git add $@"
echo "     git commit -m 'fix: 同步文件到生产环境'"
echo "  4. 推送到远程: git push origin production-deploy"
echo ""
read -p "是否立即提交并推送? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}📝 提交更改...${NC}"
    git add "$@"
    
    # 生成提交信息
    FILES_LIST=$(echo "$@" | tr ' ' '\n' | sed 's|.*/||' | tr '\n' ',' | sed 's/,$//')
    COMMIT_MSG="fix: 从 dev 同步文件到生产环境
    
同步的文件:
$(for file in "$@"; do echo "  - $file"; done)"
    
    git commit -m "$COMMIT_MSG"
    
    echo -e "${YELLOW}📤 推送到远程...${NC}"
    git push origin production-deploy
    
    echo -e "${GREEN}✅ 完成！${NC}"
fi
