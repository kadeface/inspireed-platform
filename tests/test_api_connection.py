#!/usr/bin/env python3
"""
简单的 API 连接测试
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print("="*60)
print("  API 连接测试")
print("="*60)

# 测试1: 健康检查
print("\n测试1: 健康检查")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"✅ 健康检查: {response.status_code}")
    print(f"响应: {response.text}")
except Exception as e:
    print(f"❌ 健康检查失败: {e}")
    exit(1)

# 测试2: 登录
print("\n测试2: 登录")
try:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin@inspireed.com", "password": "admin123"},  # 使用 form data
        timeout=10
    )
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ 登录成功")
        print(f"Token: {token[:30]}...")

        # 测试3: 查询学校
        print("\n测试3: 查询学校")
        response = requests.get(
            f"{BASE_URL}/schools",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            schools = response.json()
            print(f"✅ 查询成功，找到 {len(schools)} 所学校")
            for school in schools[:3]:
                print(f"  - {school.get('name')} (代码: {school.get('code')})")
        else:
            print(f"❌ 查询失败")
            print(response.text)

    else:
        print(f"❌ 登录失败")
        print(response.text)

except Exception as e:
    print(f"❌ 请求失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("  测试完成")
print("="*60)
