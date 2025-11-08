#!/bin/bash

# 课程可见性测试脚本

echo "=========================================="
echo "测试课程可见性修复"
echo "=========================================="

# 获取教师token
echo ""
echo "1. 获取教师token..."
TEACHER_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=teacher&password=teacher123" | jq -r '.access_token')

if [ "$TEACHER_TOKEN" = "null" ] || [ -z "$TEACHER_TOKEN" ]; then
  echo "❌ 获取教师token失败"
  exit 1
fi
echo "✅ 教师token获取成功"

# 获取学生token
echo ""
echo "2. 获取学生token..."
STUDENT_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student&password=student123" | jq -r '.access_token')

if [ "$STUDENT_TOKEN" = "null" ] || [ -z "$STUDENT_TOKEN" ]; then
  echo "❌ 获取学生token失败"
  exit 1
fi
echo "✅ 学生token获取成功"

# 教师查询课程
echo ""
echo "3. 教师查询已发布课程..."
TEACHER_LESSONS=$(curl -s -X GET "http://localhost:8000/api/v1/lessons?status=published&page=1&page_size=100" \
  -H "Authorization: Bearer $TEACHER_TOKEN")

TEACHER_COUNT=$(echo $TEACHER_LESSONS | jq '.total')
echo "   教师看到的已发布课程数: $TEACHER_COUNT"

if [ "$TEACHER_COUNT" -gt 0 ]; then
  echo "✅ 教师可以看到已发布的课程"
  echo "   课程列表:"
  echo $TEACHER_LESSONS | jq -r '.items[] | "   - \(.title)"'
else
  echo "❌ 教师没有看到已发布的课程"
fi

# 学生查询课程
echo ""
echo "4. 学生查询已发布课程..."
STUDENT_LESSONS=$(curl -s -X GET "http://localhost:8000/api/v1/lessons?status=published&page=1&page_size=100" \
  -H "Authorization: Bearer $STUDENT_TOKEN")

STUDENT_COUNT=$(echo $STUDENT_LESSONS | jq '.total')
echo "   学生看到的已发布课程数: $STUDENT_COUNT"

if [ "$STUDENT_COUNT" -gt 0 ]; then
  echo "✅ 学生可以看到已发布的课程"
  echo "   课程列表:"
  echo $STUDENT_LESSONS | jq -r '.items[] | "   - \(.title)"'
else
  echo "❌ 学生没有看到已发布的课程"
fi

# 比较结果
echo ""
echo "=========================================="
echo "测试总结"
echo "=========================================="
echo "教师看到的课程数: $TEACHER_COUNT"
echo "学生看到的课程数: $STUDENT_COUNT"

if [ "$STUDENT_COUNT" -gt 0 ]; then
  echo ""
  echo "✅ 测试通过！学生现在可以看到已发布的课程了！"
  echo ""
  echo "📊 课程分布:"
  echo "   - 教师创建并发布: $TEACHER_COUNT 门"
  echo "   - 学生可见: $STUDENT_COUNT 门"
  exit 0
else
  echo ""
  echo "❌ 测试失败！学生仍然看不到课程。"
  echo ""
  echo "🔍 可能的原因:"
  echo "   1. 后端服务未重启"
  echo "   2. 数据库中没有已发布的课程"
  echo "   3. 修改未生效"
  exit 1
fi

