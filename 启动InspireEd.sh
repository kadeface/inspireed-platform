#!/bin/bash

# InspireEd 快捷启动脚本
# 双击此文件即可启动服务

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 打开终端并运行启动脚本
osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$SCRIPT_DIR' && ./start.sh && echo '' && echo '按任意键关闭此窗口...' && read -n 1"
end tell
EOF

