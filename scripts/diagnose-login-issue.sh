#!/bin/bash
# 诊断 CloudStudio 登录问题

echo "🔍 诊断 CloudStudio 登录问题..."
echo ""

# 1. 检查后端服务是否运行
echo "1️⃣ 检查后端服务状态..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ 后端服务正在运行"
    curl -s http://localhost:8000/health | head -5
else
    echo "   ❌ 后端服务未运行或无法访问"
    echo "   💡 请检查："
    echo "      - 后端服务是否已启动"
    echo "      - 端口 8000 是否被占用"
    echo "      - 防火墙是否阻止了连接"
fi

echo ""
echo "2️⃣ 检查端口占用情况..."
if command -v lsof > /dev/null 2>&1; then
    PORT_8000=$(lsof -ti:8000 2>/dev/null)
    if [ ! -z "$PORT_8000" ]; then
        echo "   ✅ 端口 8000 被进程 $PORT_8000 占用"
        ps -p $PORT_8000 -o pid,cmd 2>/dev/null || echo "   进程信息不可用"
    else
        echo "   ❌ 端口 8000 未被占用"
    fi
else
    echo "   ⚠️  lsof 命令不可用，无法检查端口"
fi

echo ""
echo "3️⃣ 检查 Docker 容器状态..."
if command -v docker > /dev/null 2>&1; then
    if docker ps | grep -q inspireed-backend; then
        echo "   ✅ 后端 Docker 容器正在运行"
        docker ps | grep inspireed-backend
    else
        echo "   ❌ 后端 Docker 容器未运行"
        echo "   💡 尝试启动：cd docker && docker-compose -f docker-compose.cloudstudio.yml up -d backend"
    fi
else
    echo "   ⚠️  Docker 未安装或未运行"
fi

echo ""
echo "4️⃣ 测试 CORS 预检请求..."
ORIGIN="https://645cf02ac04c45c38ed3f5cceb49231b--5173.ap-shanghai2.cloudstudio.club"
echo "   Origin: $ORIGIN"
echo "   测试 OPTIONS 请求..."
RESPONSE=$(curl -s -X OPTIONS \
  -H "Origin: ${ORIGIN}" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  -i http://localhost:8000/api/v1/auth/login 2>&1)

if echo "$RESPONSE" | grep -qi "access-control-allow-origin"; then
    echo "   ✅ CORS 配置正确"
    echo "$RESPONSE" | grep -i "access-control"
else
    echo "   ❌ CORS 配置可能有问题"
    echo "   响应头："
    echo "$RESPONSE" | head -20
fi

echo ""
echo "5️⃣ 测试登录端点..."
echo "   测试 POST 请求..."
LOGIN_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Origin: ${ORIGIN}" \
  -d '{"email":"test@test.com","password":"test"}' \
  -w "\nHTTP Status: %{http_code}\n" \
  http://localhost:8000/api/v1/auth/login 2>&1)

if echo "$LOGIN_RESPONSE" | grep -q "HTTP Status: 200\|HTTP Status: 401\|HTTP Status: 422"; then
    echo "   ✅ 登录端点可访问（返回了 HTTP 状态码）"
    echo "$LOGIN_RESPONSE" | tail -5
else
    echo "   ❌ 登录端点无法访问"
    echo "   响应："
    echo "$LOGIN_RESPONSE" | head -10
fi

echo ""
echo "6️⃣ 检查后端日志（最近 20 行）..."
if command -v docker > /dev/null 2>&1 && docker ps | grep -q inspireed-backend; then
    echo "   后端容器日志："
    docker logs inspireed-backend --tail 20 2>&1 | grep -E "(CORS|ERROR|Exception|OPTIONS|POST)" || echo "   无相关日志"
else
    echo "   ⚠️  无法获取后端日志（容器未运行）"
fi

echo ""
echo "=========================================="
echo "💡 故障排查建议："
echo "=========================================="
echo "1. 如果后端服务未运行："
echo "   - 使用 preview.yml 启动后端服务"
echo "   - 或手动运行: bash .vscode/start-backend-cloudstudio.sh"
echo ""
echo "2. 如果 CORS 配置有问题："
echo "   - 检查 backend/.env 中的 ALLOW_LAN_ACCESS 设置"
echo "   - 重启后端服务使配置生效"
echo ""
echo "3. 如果端口被占用："
echo "   - 停止占用端口的进程"
echo "   - 或修改后端端口配置"
echo ""
echo "4. 查看详细日志："
echo "   - 后端日志: docker logs inspireed-backend -f"
echo "   - 或查看启动脚本的输出"

