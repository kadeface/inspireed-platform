#!/bin/bash

# 创建桌面快捷方式脚本

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DESKTOP_DIR="$HOME/Desktop"
SHORTCUT_NAME="启动InspireEd.command"
SHORTCUT_PATH="$DESKTOP_DIR/$SHORTCUT_NAME"

echo "📝 创建桌面快捷方式..."

# 检查桌面目录是否存在
if [ ! -d "$DESKTOP_DIR" ]; then
    echo "❌ 找不到桌面目录: $DESKTOP_DIR"
    exit 1
fi

# 如果已存在，先删除
if [ -f "$SHORTCUT_PATH" ]; then
    echo "⚠️  发现已存在的快捷方式，将覆盖..."
    rm -f "$SHORTCUT_PATH"
fi

# 创建快捷方式（符号链接）
ln -s "$PROJECT_DIR/启动InspireEd.command" "$SHORTCUT_PATH"

# 设置执行权限
chmod +x "$SHORTCUT_PATH"

echo "✅ 桌面快捷方式已创建: $SHORTCUT_PATH"
echo ""
echo "💡 使用方法："
echo "   1. 双击桌面上的 '启动InspireEd.command' 图标"
echo "   2. 系统会自动打开终端并启动服务"
echo ""
echo "📋 其他快捷方式："
echo "   - 项目目录中的 '启动InspireEd.command' 文件"
echo "   - 项目目录中的 '启动InspireEd.sh' 文件"

