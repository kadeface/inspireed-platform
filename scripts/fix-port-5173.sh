#!/bin/bash
# 清理端口 5173 的脚本

echo "🔍 检查端口 5173 占用情况..."

# 方法1: 使用 lsof（如果可用）
if command -v lsof > /dev/null 2>&1; then
    PORT_PID=$(lsof -ti:5173 2>/dev/null)
    if [ ! -z "$PORT_PID" ]; then
        echo "⚠️  发现端口 5173 被进程 $PORT_PID 占用"
        echo "📋 进程详情:"
        ps -p $PORT_PID -o pid,ppid,cmd 2>/dev/null || true
        echo ""
        echo "🛑 正在停止进程 $PORT_PID..."
        kill $PORT_PID 2>/dev/null || true
        sleep 2
        
        # 检查是否还在运行，如果是则强制停止
        if ps -p $PORT_PID > /dev/null 2>&1; then
            echo "⚠️  进程仍在运行，强制停止..."
            kill -9 $PORT_PID 2>/dev/null || true
            sleep 1
        fi
        
        # 再次检查端口
        if lsof -ti:5173 > /dev/null 2>&1; then
            echo "❌ 端口仍然被占用，强制清理所有占用该端口的进程..."
            kill -9 $(lsof -ti:5173) 2>/dev/null || true
            sleep 1
        fi
    fi
fi

# 方法2: 使用 pkill 停止可能的前端进程
echo "🔍 查找并停止所有前端相关进程..."
pkill -f "vite" 2>/dev/null && echo "✅ 已停止 vite 进程" || echo "ℹ️  没有找到运行中的 vite 进程"
pkill -f "pnpm dev" 2>/dev/null && echo "✅ 已停止 pnpm dev 进程" || echo "ℹ️  没有找到运行中的 pnpm dev 进程"
pkill -f "npm run dev" 2>/dev/null && echo "✅ 已停止 npm run dev 进程" || echo "ℹ️  没有找到运行中的 npm run dev 进程"
sleep 1

# 方法3: 停止可能占用端口的 Docker 容器
if command -v docker > /dev/null 2>&1; then
    echo "🔍 检查是否有 Docker 容器占用端口 5173..."
    CONFLICTING_CONTAINERS=$(docker ps -q --filter "publish=5173")
    if [ ! -z "$CONFLICTING_CONTAINERS" ]; then
        echo "⚠️  发现 Docker 容器占用端口 5173，正在停止..."
        docker stop $CONFLICTING_CONTAINERS 2>/dev/null || true
        sleep 2
    fi
fi

# 最终检查
if command -v lsof > /dev/null 2>&1; then
    if lsof -ti:5173 > /dev/null 2>&1; then
        echo "❌ 端口 5173 仍然被占用:"
        lsof -i:5173
        echo ""
        echo "💡 请手动执行以下命令:"
        echo "   kill -9 \$(lsof -ti:5173)"
    else
        echo "✅ 端口 5173 已成功释放"
    fi
else
    echo "✅ 清理完成（无法验证端口状态，lsof 不可用）"
fi

echo ""
echo "💡 现在可以重新启动前端服务了"

