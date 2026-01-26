#!/usr/bin/env python3
"""
更新班级代码为4位格式
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

    # 更新班级代码（使用4位格式：年级2位 + 班级2位）
    classrooms = [
        {"id": 200, "code": "0701"},
        {"id": 201, "code": "0702"},
    ]

    for cls in classrooms:
        response = requests.put(
            f"{BASE_URL}/admin/organization/classrooms/{cls['id']}",
            headers={"Authorization": f"Bearer {token}"},
            json={"code": cls["code"]}
        )

        if response.status_code == 200:
            print(f"✅ 更新班级 {cls['id']} code -> {cls['code']}")
        else:
            print(f"❌ 更新失败 {cls['id']}: {response.status_code}")
            print(response.text[:200])
else:
    print("登录失败")
