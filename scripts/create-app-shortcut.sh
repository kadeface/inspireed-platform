#!/bin/bash

# 创建 macOS 应用快捷方式（.app）

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_NAME="启动InspireEd.app"
APP_PATH="$HOME/Desktop/$APP_NAME"
APP_CONTENTS="$APP_PATH/Contents"
APP_MACOS="$APP_CONTENTS/MacOS"
APP_RESOURCES="$APP_CONTENTS/Resources"

echo "📱 创建 macOS 应用快捷方式..."

# 检查桌面目录
if [ ! -d "$HOME/Desktop" ]; then
    echo "❌ 找不到桌面目录"
    exit 1
fi

# 如果已存在，先删除
if [ -d "$APP_PATH" ]; then
    echo "⚠️  发现已存在的应用，将覆盖..."
    rm -rf "$APP_PATH"
fi

# 创建应用目录结构
mkdir -p "$APP_MACOS"
mkdir -p "$APP_RESOURCES"

# 创建 Info.plist
cat > "$APP_CONTENTS/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>启动InspireEd</string>
    <key>CFBundleIdentifier</key>
    <string>com.inspireed.launcher</string>
    <key>CFBundleName</key>
    <string>启动InspireEd</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
</dict>
</plist>
EOF

# 创建启动脚本
cat > "$APP_MACOS/启动InspireEd" <<EOF
#!/bin/bash
cd "$PROJECT_DIR"
osascript -e 'tell application "Terminal" to activate'
osascript -e 'tell application "Terminal" to do script "cd \\"$PROJECT_DIR\\" && ./start.sh"'
EOF

chmod +x "$APP_MACOS/启动InspireEd"

# 创建简单的图标（使用系统默认图标）
# 如果没有图标文件，应用会使用默认图标

echo "✅ 应用快捷方式已创建: $APP_PATH"
echo ""
echo "💡 使用方法："
echo "   1. 双击桌面上的 '$APP_NAME' 图标"
echo "   2. 系统会自动打开终端并启动服务"
echo ""
echo "📝 注意：首次运行时，macOS 可能会提示安全警告"
echo "   请右键点击应用 → '打开' → 确认运行"

