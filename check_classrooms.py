#!/usr/bin/env python3
"""
检查自动化测试学校的班级信息
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

    # 查询学校的班级
    school_id = 556  # 自动化测试学校
    response = requests.get(
        f"{BASE_URL}/admin/organization/classrooms",
        params={"school_id": school_id, "size": 100},
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        data = response.json()
        classrooms = data.get("classrooms", data.get("items", [])) if isinstance(data, dict) else data

        print(f"学校ID {school_id} 的班级列表:")
        print(f"共 {len(classrooms)} 个班级\n")

        for cls in classrooms:
            if isinstance(cls, dict):
                print(f"班级ID: {cls.get('id')}")
                print(f"名称: {cls.get('name')}")
                print(f"代码: {cls.get('code')}")
                print(f"年级ID: {cls.get('grade_id')}")
                print("-" * 40)
    else:
        print(f"查询失败: {response.status_code}")
        print(response.text)
else:
    print("登录失败")
