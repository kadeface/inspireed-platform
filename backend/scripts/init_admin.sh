#!/bin/bash
# 初始化admin用户的便捷脚本

set -e

echo "🔧 初始化admin用户..."
cd /app

# 运行Python脚本确保admin用户存在
python scripts/ensure_admin_user.py

echo "✅ Admin用户初始化完成"

