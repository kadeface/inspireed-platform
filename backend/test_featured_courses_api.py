#!/usr/bin/env python3
"""
测试精选科创课程 API
"""

import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000/api/v1"


def test_health_check():
    """测试健康检查"""
    print("=" * 60)
    print("1. 测试健康检查")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=5)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端服务已启动")
        print("   启动命令: cd backend && source venv/bin/activate && uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_get_featured_courses(category: Optional[str] = None, limit: int = 20):
    """测试获取精选课程"""
    print("\n" + "=" * 60)
    print(f"2. 测试获取精选课程 (category={category or '全部'}, limit={limit})")
    print("=" * 60)
    
    url = f"{BASE_URL}/public/curriculum/featured-courses"
    params = {"limit": limit}
    if category:
        params["category"] = category
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"请求 URL: {response.url}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功获取 {len(data)} 个精选课程")
            
            if len(data) > 0:
                print("\n前 3 个课程信息:")
                for i, course in enumerate(data[:3], 1):
                    print(f"\n  [{i}] {course.get('name', 'N/A')}")
                    print(f"      ID: {course.get('id')}")
                    print(f"      学科: {course.get('subject', {}).get('name', 'N/A') if course.get('subject') else 'N/A'}")
                    print(f"      年级: {course.get('grade', {}).get('name', 'N/A') if course.get('grade') else 'N/A'}")
                    print(f"      精选: {course.get('is_featured', False)}")
                    print(f"      分类: {course.get('category', '未设置')}")
                    if course.get('description'):
                        desc = course['description'][:50] + "..." if len(course['description']) > 50 else course['description']
                        print(f"      描述: {desc}")
            else:
                print("⚠️  当前没有精选课程，请先在数据库中设置课程的 is_featured=true")
            
            return True
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_category_filters():
    """测试不同分类的筛选"""
    print("\n" + "=" * 60)
    print("3. 测试分类筛选功能")
    print("=" * 60)
    
    categories = [
        ("人工智能", "人工智能"),
        ("无人机", "无人机"),
        ("轮式机器人", "轮式机器人"),
        ("开源硬件", "开源硬件"),
        ("虚拟仿真", "虚拟仿真"),
        ("3D打印", "3D打印"),
    ]
    
    for label, value in categories:
        print(f"\n测试分类: {label}")
        url = f"{BASE_URL}/public/curriculum/featured-courses"
        params = {"category": value, "limit": 5}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ 找到 {len(data)} 个课程")
            else:
                print(f"  ⚠️  状态码: {response.status_code}")
        except Exception as e:
            print(f"  ❌ 错误: {e}")


def main():
    """主测试函数"""
    print("\n" + "🚀 开始测试精选科创课程 API" + "\n")
    
    # 1. 健康检查
    if not test_health_check():
        print("\n❌ 后端服务未运行，请先启动后端服务")
        return
    
    # 2. 测试获取全部精选课程
    test_get_featured_courses()
    
    # 3. 测试分类筛选
    test_category_filters()
    
    # 4. 测试特定分类
    print("\n" + "=" * 60)
    print("4. 测试特定分类（人工智能）")
    print("=" * 60)
    test_get_featured_courses(category="人工智能", limit=10)
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
    print("\n提示:")
    print("1. 如果返回空列表，需要在数据库中设置课程的 is_featured=true")
    print("2. 可以使用以下 SQL 设置精选课程:")
    print("   UPDATE courses SET is_featured = true, category = '人工智能' WHERE id = <course_id>;")
    print("3. 支持的分类: 人工智能、无人机、轮式机器人、开源硬件、虚拟仿真、3D打印")


if __name__ == "__main__":
    main()

