#!/bin/bash
# CloudStudio 预览配置链接设置脚本
# 此脚本用于让 CloudStudio 使用 .cloudstudio/preview.yaml 而不是 .vscode/preview.yml

echo "🔗 设置 CloudStudio 预览配置链接..."

# 进入 .vscode 目录
cd .vscode || {
    echo "❌ .vscode 目录不存在，正在创建..."
    mkdir -p .vscode
    cd .vscode
}

# 备份现有的 preview.yml（如果存在）
if [ -f "preview.yml" ] && [ ! -L "preview.yml" ]; then
    echo "📦 备份现有的 preview.yml..."
    cp preview.yml preview.yml.backup
    echo "✅ 已备份到 preview.yml.backup"
fi

# 创建符号链接指向 .cloudstudio/preview.yaml
echo "🔗 创建符号链接..."
ln -sf ../.cloudstudio/preview.yaml preview.yml

if [ -L "preview.yml" ]; then
    echo "✅ 符号链接创建成功！"
    echo ""
    echo "📋 当前配置："
    ls -la preview.yml
    echo ""
    echo "💡 现在 CloudStudio 将使用 .cloudstudio/preview.yaml 的配置"
    echo "💡 如果需要恢复，删除符号链接并恢复备份："
    echo "   rm preview.yml"
    echo "   mv preview.yml.backup preview.yml"
else
    echo "❌ 符号链接创建失败"
    exit 1
fi

