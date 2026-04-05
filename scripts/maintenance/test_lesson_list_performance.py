#!/usr/bin/env python3
"""
测试教案列表API性能
比较优化前后的响应时间
"""

import requests
import time
import json
from typing import Dict, Any

# 配置
BASE_URL = "http://localhost:8000"
USERNAME = "admin"  # 请替换为实际用户名
PASSWORD = "admin"  # 请替换为实际密码


def login() -> str:
    """登录并获取token"""
    print("🔐 登录中...")
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "username": USERNAME,
            "password": PASSWORD
        }
    )

    if response.status_code == 200:
        token = response.json().get("access_token")
        print("✓ 登录成功")
        return token
    else:
        print(f"❌ 登录失败: {response.status_code}")
        print(f"响应: {response.text}")
        exit(1)


def test_lesson_list_performance(token: str) -> Dict[str, Any]:
    """测试教案列表API性能"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("\n📊 测试教案列表API性能...")
    print("=" * 60)

    # 第一次请求（预热）
    print("🔄 预热请求...")
    requests.get(
        f"{BASE_URL}/api/v1/lessons",
        headers=headers,
        params={"page": 1, "page_size": 20}
    )

    # 正式测试 - 进行3次请求取平均值
    times = []
    lesson_counts = []

    for i in range(3):
        print(f"\n📝 第 {i+1} 次请求...")
        start_time = time.time()

        response = requests.get(
            f"{BASE_URL}/api/v1/lessons",
            headers=headers,
            params={"page": 1, "page_size": 20}
        )

        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000  # 转换为毫秒

        if response.status_code == 200:
            data = response.json()
            lesson_count = len(data.get("items", []))
            total = data.get("total", 0)

            times.append(elapsed_time)
            lesson_counts.append(lesson_count)

            print(f"  ✓ 响应时间: {elapsed_time:.2f}ms")
            print(f"  ✓ 返回教案数: {lesson_count}")
            print(f"  ✓ 总教案数: {total}")
        else:
            print(f"  ❌ 请求失败: {response.status_code}")
            print(f"  响应: {response.text}")
            return {"error": "请求失败"}

    # 计算统计信息
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print("\n" + "=" * 60)
    print("📈 性能统计:")
    print(f"  平均响应时间: {avg_time:.2f}ms")
    print(f"  最快响应时间: {min_time:.2f}ms")
    print(f"  最慢响应时间: {max_time:.2f}ms")
    print(f"  每次返回教案数: {lesson_counts[0]}")
    print("=" * 60)

    # 性能评估
    print("\n✨ 性能评估:")
    if avg_time < 500:
        print("  🚀 优秀！响应时间 < 500ms")
    elif avg_time < 1000:
        print("  ✓ 良好！响应时间 < 1秒")
    elif avg_time < 2000:
        print("  ⚠️ 一般。响应时间 < 2秒")
    elif avg_time < 5000:
        print("  ❌ 较慢。响应时间 > 2秒")
    else:
        print("  🔴 很慢！响应时间 > 5秒")

    return {
        "avg_time_ms": avg_time,
        "min_time_ms": min_time,
        "max_time_ms": max_time,
        "lesson_count": lesson_counts[0] if lesson_counts else 0
    }


def test_lesson_detail_performance(token: str) -> Dict[str, Any]:
    """测试单个教案详情API性能（这个会进行URL转换）"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("\n📊 测试教案详情API性能...")
    print("=" * 60)

    # 先获取一个教案ID
    list_response = requests.get(
        f"{BASE_URL}/api/v1/lessons",
        headers=headers,
        params={"page": 1, "page_size": 1}
    )

    if list_response.status_code != 200:
        print("❌ 无法获取教案列表")
        return {"error": "无法获取教案列表"}

    lessons = list_response.json().get("items", [])
    if not lessons:
        print("❌ 没有找到教案")
        return {"error": "没有找到教案"}

    lesson_id = lessons[0].get("id")
    print(f"📝 测试教案 ID: {lesson_id}")

    # 测试详情API
    start_time = time.time()
    response = requests.get(
        f"{BASE_URL}/api/v1/lessons/{lesson_id}",
        headers=headers
    )
    end_time = time.time()

    elapsed_time = (end_time - start_time) * 1000

    if response.status_code == 200:
        lesson = response.json()
        print(f"  ✓ 响应时间: {elapsed_time:.2f}ms")
        print(f"  ✓ 教案标题: {lesson.get('title', 'N/A')}")
        print(f"  ✓ cell数量: {lesson.get('cell_count', 0)}")
        print("=" * 60)

        return {
            "time_ms": elapsed_time,
            "lesson_id": lesson_id,
            "cell_count": lesson.get('cell_count', 0)
        }
    else:
        print(f"  ❌ 请求失败: {response.status_code}")
        return {"error": "请求失败"}


def main():
    print("🚀 开始性能测试...")
    print(f"后端地址: {BASE_URL}")

    try:
        # 登录
        token = login()

        # 测试列表API
        list_result = test_lesson_list_performance(token)

        # 测试详情API
        detail_result = test_lesson_detail_performance(token)

        # 总结
        print("\n" + "=" * 60)
        print("📋 测试总结:")
        if "error" not in list_result:
            print(f"  列表API平均响应: {list_result['avg_time_ms']:.2f}ms")
        if "error" not in detail_result:
            print(f"  详情API响应: {detail_result['time_ms']:.2f}ms")

        # 对比优化效果
        if "error" not in list_result and list_result['avg_time_ms'] < 1000:
            print("\n🎉 优化成功！列表API响应时间 < 1秒")
        elif "error" not in list_result:
            print("\n⚠️ 列表API仍需优化")

        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到后端服务器")
        print("请确保后端服务正在运行: http://localhost:8000")
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")


if __name__ == "__main__":
    main()
