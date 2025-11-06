#!/bin/bash

echo "=========================================="
echo "  InspireEd 网络访问信息"
echo "=========================================="
echo ""

# 获取本机 IP 地址
get_local_ip() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        LOCAL_IP=$(hostname -I | awk '{print $1}')
    else
        # Windows (Git Bash)
        LOCAL_IP=$(ipconfig | grep "IPv4" | awk '{print $NF}' | head -n 1)
    fi
    echo $LOCAL_IP
}

LOCAL_IP=$(get_local_ip)

if [ -z "$LOCAL_IP" ]; then
    echo "⚠️  无法自动检测 IP 地址"
    echo ""
    echo "请手动运行以下命令获取 IP 地址："
    if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "  ifconfig | grep 'inet '"
    else
        echo "  ipconfig"
    fi
    exit 1
fi

echo "📍 本机信息："
echo "   IP 地址: $LOCAL_IP"
echo "   操作系统: $OSTYPE"
echo ""

echo "🌐 访问地址："
echo ""
echo "   【本机访问】"
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo ""
echo "   【局域网访问】（其他设备使用这些地址）"
echo "   前端: http://$LOCAL_IP:5173"
echo "   后端: http://$LOCAL_IP:8000"
echo "   API 文档: http://$LOCAL_IP:8000/docs"
echo ""

echo "⚙️  配置建议："
echo ""
echo "1️⃣  配置后端 CORS (backend/.env)："
echo "   BACKEND_CORS_ORIGINS=http://localhost:5173,http://$LOCAL_IP:5173"
echo ""
echo "2️⃣  配置前端 API 地址 (frontend/.env.local)："
echo "   选项 A - 本机访问："
echo "   VITE_API_BASE_URL=http://localhost:8000/api/v1"
echo ""
echo "   选项 B - 局域网访问（推荐）："
echo "   VITE_API_BASE_URL=http://$LOCAL_IP:8000/api/v1"
echo ""

echo "🧪 测试连接："
echo ""
echo "在浏览器中访问以下地址测试后端连接："
echo "   http://$LOCAL_IP:8000/health"
echo ""
echo "应该返回: {\"status\": \"healthy\"}"
echo ""

echo "📱 移动设备访问："
echo ""
echo "确保移动设备连接到同一 WiFi，然后访问："
echo "   http://$LOCAL_IP:5173"
echo ""

echo "📚 详细配置指南："
echo "   查看文件: NETWORK_ACCESS_GUIDE.md"
echo ""

echo "=========================================="

# 可选：自动应用配置
echo ""
read -p "是否自动更新配置文件？(y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔧 正在更新配置文件..."
    
    # 更新后端配置
    if [ -f "backend/.env" ]; then
        if grep -q "BACKEND_CORS_ORIGINS=" backend/.env; then
            # 如果存在，更新
            sed -i.bak "s|BACKEND_CORS_ORIGINS=.*|BACKEND_CORS_ORIGINS=http://localhost:5173,http://$LOCAL_IP:5173|" backend/.env
            echo "✅ 已更新 backend/.env"
        else
            # 如果不存在，添加
            echo "BACKEND_CORS_ORIGINS=http://localhost:5173,http://$LOCAL_IP:5173" >> backend/.env
            echo "✅ 已添加 CORS 配置到 backend/.env"
        fi
    else
        echo "⚠️  backend/.env 不存在，请先复制 backend/env.example"
    fi
    
    # 更新前端配置
    if [ -f "frontend/.env.local" ]; then
        if grep -q "VITE_API_BASE_URL=" frontend/.env.local; then
            # 如果存在，更新
            sed -i.bak "s|VITE_API_BASE_URL=.*|VITE_API_BASE_URL=http://$LOCAL_IP:8000/api/v1|" frontend/.env.local
            echo "✅ 已更新 frontend/.env.local"
        else
            # 如果不存在，添加
            echo "VITE_API_BASE_URL=http://$LOCAL_IP:8000/api/v1" >> frontend/.env.local
            echo "✅ 已添加 API 配置到 frontend/.env.local"
        fi
    else
        echo "📝 正在创建 frontend/.env.local..."
        cp frontend/env.example frontend/.env.local
        sed -i.bak "s|VITE_API_BASE_URL=.*|VITE_API_BASE_URL=http://$LOCAL_IP:8000/api/v1|" frontend/.env.local
        echo "✅ 已创建并配置 frontend/.env.local"
    fi
    
    echo ""
    echo "🎉 配置完成！请重启服务以应用更改："
    echo "   ./stop.sh && ./start.sh"
else
    echo ""
    echo "ℹ️  配置未更改。如需手动配置，请参考上面的配置建议。"
fi

echo ""

