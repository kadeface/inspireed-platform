#!/bin/bash
# 检查 CloudStudio 环境 CORS 配置

echo "🔍 检查 CloudStudio CORS 配置..."

# 检查后端容器是否运行
if ! docker ps | grep -q inspireed-backend; then
    echo "❌ 后端容器未运行"
    exit 1
fi

echo "✅ 后端容器正在运行"

# 检查后端日志中的 CORS 配置
echo ""
echo "📋 后端 CORS 配置信息："
docker logs inspireed-backend 2>&1 | grep -A 5 "CORS configured" | tail -10

# 测试 CORS 预检请求
echo ""
echo "🧪 测试 CORS 预检请求..."
ORIGIN="https://645cf02ac04c45c38ed3f5cceb49231b--5173.ap-shanghai2.cloudstudio.club"
curl -X OPTIONS \
  -H "Origin: ${ORIGIN}" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  -v http://localhost:8000/api/v1/auth/login 2>&1 | grep -i "access-control"

echo ""
echo "💡 如果看到 Access-Control-Allow-Origin 头，说明 CORS 配置正确"
echo "💡 如果没有看到，需要重启后端容器："
echo "   cd docker && docker-compose -f docker-compose.cloudstudio.yml restart backend"

