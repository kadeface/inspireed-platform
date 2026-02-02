#!/bin/bash
# 测试教案列表API性能 - 使用curl

set -e

# 配置
BASE_URL="http://localhost:8000"
USERNAME="admin"
PASSWORD="admin"

echo "🚀 开始性能测试..."
echo "后端地址: $BASE_URL"
echo ""

# 登录获取token
echo "🔐 登录中..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null || echo "")

if [ -z "$TOKEN" ]; then
    echo "❌ 登录失败，请检查用户名和密码"
    echo "响应: $LOGIN_RESPONSE"
    exit 1
fi

echo "✓ 登录成功"
echo ""

# 测试列表API性能
echo "📊 测试教案列表API性能..."
echo "============================================================"

# 预热请求
echo "🔄 预热请求..."
curl -s "$BASE_URL/api/v1/lessons?page=1&page_size=20" \
  -H "Authorization: Bearer $TOKEN" > /dev/null

# 进行3次测试
TOTAL_TIME=0
for i in {1..3}; do
    echo ""
    echo "📝 第 $i 次请求..."

    START_TIME=$(date +%s%3N)
    RESPONSE=$(curl -s "$BASE_URL/api/v1/lessons?page=1&page_size=20" \
      -H "Authorization: Bearer $TOKEN")
    END_TIME=$(date +%s%3N)

    ELAPSED_TIME=$((END_TIME - START_TIME))

    # 检查响应并统计
    LESSON_COUNT=$(echo $RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('items', [])))" 2>/dev/null || echo "0")
    TOTAL_LESSONS=$(echo $RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total', 0))" 2>/dev/null || echo "0")

    if [ "$LESSON_COUNT" -gt 0 ] || [ "$TOTAL_LESSONS" -eq 0 ]; then
        echo "  ✓ 响应时间: ${ELAPSED_TIME}ms"
        echo "  ✓ 返回教案数: $LESSON_COUNT"
        echo "  ✓ 总教案数: $TOTAL_LESSONS"
        TOTAL_TIME=$((TOTAL_TIME + ELAPSED_TIME))
    else
        echo "  ❌ 请求失败或返回格式错误"
        echo "  响应: $RESPONSE" | head -c 200
    fi
done

# 计算平均值
AVG_TIME=$((TOTAL_TIME / 3))

echo ""
echo "============================================================"
echo "📈 性能统计:"
echo "  平均响应时间: ${AVG_TIME}ms"
echo "============================================================"

# 性能评估
echo ""
echo "✨ 性能评估:"
if [ $AVG_TIME -lt 500 ]; then
    echo "  🚀 优秀！响应时间 < 500ms"
    echo ""
    echo "🎉 优化成功！列表API性能非常好"
elif [ $AVG_TIME -lt 1000 ]; then
    echo "  ✓ 良好！响应时间 < 1秒"
    echo ""
    echo "✅ 优化成功！列表API性能良好"
elif [ $AVG_TIME -lt 2000 ]; then
    echo "  ⚠️ 一般。响应时间 < 2秒"
    echo ""
    echo "⚠️ 列表API性能一般，可能需要进一步优化"
elif [ $AVG_TIME -lt 5000 ]; then
    echo "  ❌ 较慢。响应时间 > 2秒"
    echo ""
    echo "❌ 列表API仍需优化"
else
    echo "  🔴 很慢！响应时间 > 5秒"
    echo ""
    echo "🔴 列表API性能严重不达标，需要立即优化"
fi

echo ""
echo "============================================================"
echo "📋 测试完成"
echo "============================================================"
