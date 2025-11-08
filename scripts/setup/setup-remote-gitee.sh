#!/bin/bash
# Gitee 远程仓库设置脚本
# 使用前请将 YOUR_USERNAME 替换为你的 Gitee 用户名

echo "🚀 正在配置 Gitee 远程仓库..."
echo ""
echo "⚠️  请先确认："
echo "1. 你已经在 Gitee 上创建了仓库"
echo "2. 仓库名为：inspireed-platform"
echo ""
read -p "请输入你的 Gitee 用户名: " GITEE_USERNAME

if [ -z "$GITEE_USERNAME" ]; then
    echo "❌ 错误：用户名不能为空"
    exit 1
fi

echo ""
echo "📝 配置远程仓库..."
git remote add origin "https://gitee.com/${GITEE_USERNAME}/inspireed-platform.git"

if [ $? -eq 0 ]; then
    echo "✅ 远程仓库配置成功！"
    echo ""
    echo "📤 正在推送代码到 Gitee..."
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 完成！你的代码已推送到 Gitee"
        echo "🌐 访问地址: https://gitee.com/${GITEE_USERNAME}/inspireed-platform"
    else
        echo ""
        echo "⚠️  推送失败，可能需要配置 Gitee 认证"
        echo "请使用以下命令手动推送："
        echo "  git push -u origin main"
        echo ""
        echo "如果需要配置 Gitee 认证，请参考："
        echo "https://gitee.com/help/articles/4181"
    fi
else
    echo "❌ 配置失败，可能已经存在远程仓库配置"
    echo "查看当前配置："
    git remote -v
fi

