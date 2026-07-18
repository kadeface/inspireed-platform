#!/usr/bin/env python3
"""
检查现有的考号映射
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 登录
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "admin@inspireed.com", "password": "admin123"}
)

if response.status_code == 200:
    token = response.json().get("access_token")

    # 查询考试39的考号映射
    exam_id = 39
    response = requests.get(
        f"{BASE_URL}/exams/{exam_id}/exam-numbers",
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        mappings = response.json()
        print(f"考试 {exam_id} 的现有考号映射:")
        if isinstance(mappings, list) and len(mappings) > 0:
            for m in mappings:
                print(f"  考号: {m.get('exam_number')}, 学生ID: {m.get('student_id')}")
        else:
            print(f"  无映射数据")
    else:
        print(f"查询失败: {response.status_code}")
else:
    print("登录失败")
