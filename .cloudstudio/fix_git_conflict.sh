#!/bin/bash
# Cloud Studio Git 冲突解决脚本

echo "🔍 检查本地修改状态..."
git status

echo ""
echo "📋 查看本地 preview.yaml 的修改内容..."
git diff .cloudstudio/preview.yaml

echo ""
echo "💡 解决方案选项："
echo ""
echo "选项1: 如果本地修改不重要，可以丢弃本地修改并拉取远程更新"
echo "  执行: git checkout -- .cloudstudio/preview.yaml"
echo "  然后: git pull origin dev"
echo ""
echo "选项2: 如果想保留本地修改，先暂存后拉取再合并"
echo "  执行: git stash"
echo "  然后: git pull origin dev"
echo "  最后: git stash pop (如果需要应用本地修改)"
echo ""
echo "选项3: 如果想保留本地修改并提交"
echo "  执行: git add .cloudstudio/preview.yaml"
echo "  然后: git commit -m '你的提交信息'"
echo "  最后: git pull origin dev (可能会有冲突需要解决)"
echo ""

