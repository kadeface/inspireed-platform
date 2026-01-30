#!/bin/bash
# 部署脚本：从 dev 选择性部署到 production-deploy
# 用法: ./scripts/deploy-to-production.sh <commit-hash> [commit-hash2] ...

set -e

if [ $# -eq 0 ]; then
    echo "❌ 错误: 请提供至少一个提交哈希"
    echo ""
    echo "用法:"
    echo "  ./scripts/deploy-to-production.sh <commit-hash>"
    echo "  ./scripts/deploy-to-production.sh <commit-hash1> <commit-hash2> ..."
    echo ""
    echo "示例:"
    echo "  ./scripts/deploy-to-production.sh 614eb33"
    echo "  ./scripts/deploy-to-production.sh 614eb33 000a0a5"
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

echo -e "${YELLOW}📋 准备部署以下提交:${NC}"
for commit in "$@"; do
    echo "  - $commit: $(git log -1 --oneline $commit 2>/dev/null || echo '提交不存在')"
done

echo ""
read -p "确认部署这些提交到 production-deploy? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消"
    exit 1
fi

echo -e "${YELLOW}🔄 切换到 production-deploy 分支...${NC}"
git checkout production-deploy

echo -e "${YELLOW}📥 拉取最新代码...${NC}"
git pull origin production-deploy || echo "⚠️  拉取失败，继续..."

echo -e "${YELLOW}🍒 开始 Cherry-pick 提交...${NC}"
SUCCESS_COUNT=0
FAILED_COMMITS=()

for commit in "$@"; do
    echo ""
    echo -e "${YELLOW}正在处理: $commit${NC}"
    if git cherry-pick $commit; then
        echo -e "${GREEN}✅ $commit 成功${NC}"
        ((SUCCESS_COUNT++))
    else
        echo -e "${RED}❌ $commit 失败（可能有冲突）${NC}"
        FAILED_COMMITS+=($commit)
        echo "请手动解决冲突后运行: git cherry-pick --continue"
        echo "或放弃: git cherry-pick --abort"
        read -p "是否继续处理下一个提交? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            break
        fi
    fi
done

echo ""
echo -e "${GREEN}📊 部署结果:${NC}"
echo "  成功: $SUCCESS_COUNT"
echo "  失败: ${#FAILED_COMMITS[@]}"

if [ ${#FAILED_COMMITS[@]} -gt 0 ]; then
    echo -e "${RED}失败的提交:${NC}"
    for commit in "${FAILED_COMMITS[@]}"; do
        echo "  - $commit"
    done
fi

if [ $SUCCESS_COUNT -gt 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Cherry-pick 完成！${NC}"
    echo ""
    echo "📝 下一步:"
    echo "  1. 检查更改: git log --oneline -5"
    echo "  2. 推送到远程: git push origin production-deploy"
    echo ""
    read -p "是否立即推送到远程? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}📤 推送到远程...${NC}"
        git push origin production-deploy
        echo -e "${GREEN}✅ 推送成功！${NC}"
    fi
fi
