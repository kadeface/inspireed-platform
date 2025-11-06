#!/bin/bash

echo "🔍 诊断教师端网络存储问题..."
echo ""

# 1. 检测本机IP地址
echo "1️⃣ 检测服务器IP地址"
echo "================================"
SERVER_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)
echo "服务器IP: $SERVER_IP"
echo ""

# 2. 检查后端进程
echo "2️⃣ 检查后端服务"
echo "================================"
BACKEND_PROCESS=$(ps aux | grep "uvicorn" | grep -v grep)
if [ -z "$BACKEND_PROCESS" ]; then
    echo "❌ 后端服务未运行"
    echo "   请运行: ./start.sh"
else
    echo "✅ 后端服务正在运行"
    echo "$BACKEND_PROCESS"
    
    # 检查监听地址
    if echo "$BACKEND_PROCESS" | grep -q "0.0.0.0"; then
        echo "✅ 后端监听所有网络接口 (0.0.0.0)"
    else
        echo "⚠️  后端可能只监听本地接口"
        echo "   建议：确保启动时使用 --host 0.0.0.0"
    fi
fi
echo ""

# 3. 检查端口监听
echo "3️⃣ 检查端口监听状态"
echo "================================"
if command -v lsof &> /dev/null; then
    echo "后端端口 8000:"
    lsof -i :8000 | grep LISTEN || echo "❌ 端口8000未监听"
    echo ""
    echo "前端端口 5173:"
    lsof -i :5173 | grep LISTEN || echo "❌ 端口5173未监听"
else
    echo "⚠️  lsof 命令不可用，跳过端口检查"
fi
echo ""

# 4. 检查后端配置
echo "4️⃣ 检查后端CORS配置"
echo "================================"
if [ -f "backend/.env" ]; then
    echo "ALLOW_LAN_ACCESS 配置:"
    grep "ALLOW_LAN_ACCESS" backend/.env || echo "   未配置 (使用默认值 True)"
    echo ""
    echo "BACKEND_CORS_ORIGINS 配置:"
    grep "BACKEND_CORS_ORIGINS" backend/.env || echo "   未配置 (使用默认值)"
else
    echo "❌ 后端 .env 文件不存在"
fi
echo ""

# 5. 检查前端配置
echo "5️⃣ 检查前端API配置"
echo "================================"
if [ -f "frontend/.env.local" ]; then
    echo "VITE_API_BASE_URL 配置:"
    grep "VITE_API_BASE_URL" frontend/.env.local || echo "   未配置 (使用动态检测)"
else
    echo "❌ 前端 .env.local 文件不存在"
fi
echo ""

# 6. 测试后端连接
echo "6️⃣ 测试后端API连接"
echo "================================"
echo "测试 localhost 连接:"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ localhost:8000 可访问"
else
    echo "❌ localhost:8000 不可访问"
fi

if [ -n "$SERVER_IP" ]; then
    echo ""
    echo "测试局域网IP连接:"
    if curl -s http://$SERVER_IP:8000/health > /dev/null 2>&1; then
        echo "✅ $SERVER_IP:8000 可访问"
    else
        echo "❌ $SERVER_IP:8000 不可访问"
        echo "   可能原因: 防火墙阻止或服务未监听0.0.0.0"
    fi
fi
echo ""

# 7. 检查浏览器控制台
echo "7️⃣ 常见问题排查建议"
echo "================================"
echo "如果在其他电脑上无法保存教学设计，请检查："
echo ""
echo "A. 浏览器开发者工具 (F12)"
echo "   1. 打开 Network 标签"
echo "   2. 尝试保存教学设计"
echo "   3. 查看是否有红色的失败请求"
echo "   4. 点击失败请求查看详细错误信息"
echo ""
echo "B. 检查请求URL"
echo "   - 正确: http://$SERVER_IP:8000/api/v1/..."
echo "   - 错误: http://localhost:8000/api/v1/..."
echo "   - 错误: http://127.0.0.1:8000/api/v1/..."
echo ""
echo "C. 检查CORS错误"
echo "   如果看到 'CORS policy' 错误，说明后端拒绝了跨域请求"
echo "   解决方法见下方修复建议"
echo ""

# 8. 提供修复建议
echo "8️⃣ 修复建议"
echo "================================"
echo ""
echo "📝 方案1: 确保后端正确配置并重启"
echo "-----------------------------------"
echo "1. 编辑 backend/.env，确保包含："
echo "   ALLOW_LAN_ACCESS=true"
echo ""
echo "2. 重启服务:"
echo "   ./restart.sh"
echo ""
echo "3. 验证后端监听 0.0.0.0:"
echo "   ps aux | grep uvicorn | grep '0.0.0.0'"
echo ""

echo "📝 方案2: 检查防火墙设置"
echo "-----------------------------------"
echo "macOS 允许端口 8000:"
echo "   系统偏好设置 -> 安全性与隐私 -> 防火墙 -> 防火墙选项"
echo "   确保允许 Python/uvicorn 的入站连接"
echo ""

echo "📝 方案3: 手动配置API地址（如果动态检测失败）"
echo "-----------------------------------"
echo "1. 编辑 frontend/.env.local，设置:"
echo "   VITE_API_BASE_URL=http://$SERVER_IP:8000/api/v1"
echo ""
echo "2. 重启前端服务:"
echo "   cd frontend && pnpm dev"
echo ""

echo "📝 方案4: 测试网络连通性"
echo "-----------------------------------"
echo "从其他电脑上测试:"
echo "1. 在浏览器访问: http://$SERVER_IP:8000/health"
echo "   应该看到: {\"status\":\"healthy\"}"
echo ""
echo "2. 如果无法访问，可能原因:"
echo "   - 防火墙阻止"
echo "   - 不在同一局域网"
echo "   - 服务器未监听0.0.0.0"
echo ""

echo "✅ 诊断完成"
echo ""
echo "如需帮助，请将此诊断结果截图或保存"

