#!/usr/bin/env python3
"""
检查年级信息
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

    # 查询年级
    response = requests.get(
        f"{BASE_URL}/curriculum/grades",
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        grades = response.json()

        print("系统中的年级列表:")
        for g in grades:
            if g["level"] in [7, 8, 10, 12]:
                print(f"年级 {g['level']}: 名称='{g['name']}', ID={g['id']}")
    else:
        print(f"查询失败: {response.status_code}")
else:
    print("登录失败")
