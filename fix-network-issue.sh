#!/bin/bash

echo "🔧 修复教师端网络存储问题..."
echo ""

# 获取服务器IP
SERVER_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)
echo "检测到服务器IP: $SERVER_IP"
echo ""

# 备份配置文件
echo "📦 备份配置文件..."
timestamp=$(date +"%Y%m%d_%H%M%S")

if [ -f "backend/.env" ]; then
    cp backend/.env "backend/.env.backup.$timestamp"
    echo "✅ 后端配置已备份: backend/.env.backup.$timestamp"
fi

if [ -f "frontend/.env.local" ]; then
    cp frontend/.env.local "frontend/.env.local.backup.$timestamp"
    echo "✅ 前端配置已备份: frontend/.env.local.backup.$timestamp"
fi
echo ""

# 修复后端配置
echo "🔧 修复后端CORS配置..."

if [ ! -f "backend/.env" ]; then
    echo "❌ backend/.env 不存在，从示例创建..."
    cp backend/env.example backend/.env
fi

# 检查是否已有 ALLOW_LAN_ACCESS 配置
if grep -q "^ALLOW_LAN_ACCESS=" backend/.env; then
    echo "⚠️  ALLOW_LAN_ACCESS 已存在，更新为 true"
    sed -i.bak 's/^ALLOW_LAN_ACCESS=.*/ALLOW_LAN_ACCESS=true/' backend/.env
else
    echo "➕ 添加 ALLOW_LAN_ACCESS=true"
    echo "" >> backend/.env
    echo "# 允许局域网访问（自动添加）" >> backend/.env
    echo "ALLOW_LAN_ACCESS=true" >> backend/.env
fi

echo "✅ 后端CORS配置已更新"
echo ""

# 修复前端配置
echo "🔧 配置前端API地址..."

if [ ! -f "frontend/.env.local" ]; then
    echo "❌ frontend/.env.local 不存在，从示例创建..."
    cp frontend/env.example frontend/.env.local
fi

# 注释掉现有的 VITE_API_BASE_URL（使用动态检测）
if grep -q "^VITE_API_BASE_URL=" frontend/.env.local; then
    echo "⚠️  VITE_API_BASE_URL 已存在，注释掉以使用动态检测"
    sed -i.bak 's/^VITE_API_BASE_URL=/#VITE_API_BASE_URL=/' frontend/.env.local
fi

# 添加注释说明
if ! grep -q "# API配置 - 留空将自动根据访问地址动态适配" frontend/.env.local; then
    sed -i.bak '1i\
# API配置 - 留空将自动根据访问地址动态适配\
# VITE_API_BASE_URL=\
' frontend/.env.local
fi

echo "✅ 前端配置已更新（使用动态检测）"
echo ""

# 显示当前配置
echo "📋 当前配置:"
echo "================================"
echo "服务器IP: $SERVER_IP"
echo ""
echo "后端 ALLOW_LAN_ACCESS:"
grep "ALLOW_LAN_ACCESS" backend/.env || echo "  (使用默认值 true)"
echo ""
echo "前端 API 地址:"
grep "VITE_API_BASE_URL" frontend/.env.local || echo "  (使用动态检测)"
echo ""

# 询问是否重启服务
echo "⚠️  需要重启服务以应用更改"
echo ""
read -p "是否现在重启服务? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔄 重启服务..."
    ./restart.sh
    
    echo ""
    echo "⏳ 等待服务启动..."
    sleep 5
    
    # 测试连接
    echo ""
    echo "🧪 测试连接..."
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 本地连接正常: http://localhost:8000"
    else
        echo "❌ 本地连接失败"
    fi
    
    if [ -n "$SERVER_IP" ]; then
        if curl -s http://$SERVER_IP:8000/health > /dev/null 2>&1; then
            echo "✅ 局域网连接正常: http://$SERVER_IP:8000"
        else
            echo "❌ 局域网连接失败"
            echo "   可能原因: 防火墙阻止"
        fi
    fi
else
    echo ""
    echo "⚠️  请稍后手动重启服务:"
    echo "   ./restart.sh"
fi

echo ""
echo "================================================"
echo "✅ 配置修复完成！"
echo ""
echo "📱 从其他电脑访问:"
echo "   前端: http://$SERVER_IP:5173"
echo "   后端: http://$SERVER_IP:8000"
echo ""
echo "🧪 测试连通性:"
echo "   1. 将 test-from-remote.html 复制到其他电脑"
echo "   2. 在浏览器中打开并运行测试"
echo ""
echo "📖 详细文档:"
echo "   - 快速指南: README_NETWORK_FIX.md"
echo "   - 完整排查: docs/network/TEACHER_STORAGE_ISSUE.md"
echo "   - 诊断脚本: ./diagnose-network.sh"
echo ""

# 检查防火墙
echo "🔐 防火墙提醒:"
echo "   如果从其他电脑无法访问，请检查防火墙设置"
echo "   macOS: 系统偏好设置 → 安全性与隐私 → 防火墙"
echo "   确保允许 Python 的入站连接"
echo ""

echo "如需帮助，请查看 README_NETWORK_FIX.md"

