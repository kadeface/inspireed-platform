#!/bin/bash
#
# 项目合并准备脚本
# 用途：创建合并所需的基础目录结构
#

set -e

echo "🚀 准备项目合并..."

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

# 1. 创建备份分支
echo "📦 创建备份分支..."
BACKUP_BRANCH="backup/before-merge-$(date +%Y%m%d)"
if git rev-parse --verify "$BACKUP_BRANCH" >/dev/null 2>&1; then
    echo "⚠️  备份分支已存在: $BACKUP_BRANCH"
else
    git branch "$BACKUP_BRANCH"
    echo "✅ 已创建备份分支: $BACKUP_BRANCH"
fi

# 2. 创建应用目录结构
echo "📁 创建目录结构..."
mkdir -p apps/inspireed
mkdir -p apps/app2
mkdir -p shared/models/shared
mkdir -p shared/schemas/shared
mkdir -p shared/api
mkdir -p infrastructure/docker
mkdir -p infrastructure/database/migrations
mkdir -p infrastructure/database/seeds
mkdir -p docs/inspireed
mkdir -p docs/app2
mkdir -p docs/shared
mkdir -p scripts/merge
mkdir -p scripts/deploy

# 创建 __init__.py 文件（Python 包）
touch shared/__init__.py
touch shared/models/__init__.py
touch shared/models/shared/__init__.py
touch shared/schemas/__init__.py

echo "✅ 目录结构已创建"

# 3. 检查当前 Git 状态
echo "🔍 检查 Git 状态..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  发现未提交的更改:"
    git status --short
    echo ""
    read -p "是否现在提交这些更改？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "chore: prepare for multi-app merge"
        echo "✅ 更改已提交"
    else
        echo "⚠️  请先提交或暂存更改后再继续"
        exit 1
    fi
else
    echo "✅ 工作区干净"
fi

# 4. 检查是否在合并分支
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "feature/multi-app-merge" ]] && [[ "$CURRENT_BRANCH" != "main" ]] && [[ "$CURRENT_BRANCH" != "dev" ]]; then
    echo "📌 当前分支: $CURRENT_BRANCH"
    read -p "是否创建合并分支 'feature/multi-app-merge'？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout -b feature/multi-app-merge
        echo "✅ 已创建并切换到合并分支"
    fi
fi

# 5. 创建备份压缩包
echo "💾 创建代码备份..."
BACKUP_FILE="backup-inspireed-$(date +%Y%m%d-%H%M%S).tar.gz"
tar -czf "$BACKUP_FILE" \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='.git' \
    --exclude='*.tar.gz' \
    --exclude='*.log' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    . 2>/dev/null || true

if [ -f "$BACKUP_FILE" ]; then
    echo "✅ 备份已创建: $BACKUP_FILE"
    # 询问是否移动备份到特定目录
    read -p "是否将备份移动到 backup/ 目录？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p backup
        mv "$BACKUP_FILE" backup/
        echo "✅ 备份已移动到 backup/$BACKUP_FILE"
    fi
fi

# 6. 显示目录结构
echo ""
echo "📂 当前项目结构:"
tree -L 2 -d -I 'node_modules|venv|__pycache__|.git' apps/ shared/ infrastructure/ 2>/dev/null || \
    find apps/ shared/ infrastructure/ -type d -maxdepth 2 | head -20

# 7. 下一步提示
echo ""
echo "✅ 准备完成！"
echo ""
echo "📋 下一步操作:"
echo "   1. 审查合并计划: docs/PROJECT_MERGE_PLAN.md"
echo "   2. 开始移动代码: scripts/merge/move-inspireed.sh"
echo "   3. 创建共享模型: 参考 docs/SCHEMA_ISOLATION_EXAMPLE.md"
echo ""
echo "💡 提示:"
echo "   - 查看合并计划: cat docs/PROJECT_MERGE_PLAN.md"
echo "   - 查看检查清单: scripts/merge/checklist.md"
echo "   - 如需回滚: git checkout $BACKUP_BRANCH"
echo ""
