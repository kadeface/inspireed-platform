#!/usr/bin/env python3
"""
更新班级名称为正确的格式
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

    # 更新班级名称
    classrooms = [
        {"id": 200, "name": "七年级1班"},
        {"id": 201, "name": "七年级2班"},
    ]

    for cls in classrooms:
        response = requests.put(
            f"{BASE_URL}/admin/organization/classrooms/{cls['id']}",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": cls["name"]}
        )

        if response.status_code == 200:
            print(f"✅ 更新班级 {cls['id']} -> {cls['name']}")
        else:
            print(f"❌ 更新失败 {cls['id']}: {response.status_code}")
            print(response.text[:200])
else:
    print("登录失败")
