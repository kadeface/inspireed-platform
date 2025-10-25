#!/usr/bin/env python3
"""
Cell API 测试脚本
测试新实现的Cell API功能
"""
import asyncio
import httpx
import json
from typing import Dict, Any

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

# 测试数据
TEST_LESSON_ID = 1  # 假设存在一个测试教案
TEST_CELL_DATA = {
    "lesson_id": TEST_LESSON_ID,
    "cell_type": "qa",
    "title": "测试QA Cell",
    "content": {
        "question": "",
        "answer": "",
        "isAIAnswer": False
    },
    "config": {},
    "order": 0,
    "editable": True
}

async def test_cell_api():
    """测试Cell API功能"""
    async with httpx.AsyncClient() as client:
        print("🚀 开始测试Cell API...")
        
        # 1. 测试创建Cell
        print("\n1. 测试创建Cell...")
        try:
            response = await client.post(
                f"{BASE_URL}/cells/",
                json=TEST_CELL_DATA,
                headers={"Authorization": "Bearer test-token"}  # 需要有效的token
            )
            if response.status_code == 201:
                cell_data = response.json()
                cell_id = cell_data["id"]
                print(f"✅ Cell创建成功，ID: {cell_id}")
            else:
                print(f"❌ Cell创建失败: {response.status_code} - {response.text}")
                return
        except Exception as e:
            print(f"❌ Cell创建异常: {e}")
            return
        
        # 2. 测试获取Cell
        print(f"\n2. 测试获取Cell {cell_id}...")
        try:
            response = await client.get(
                f"{BASE_URL}/cells/{cell_id}",
                headers={"Authorization": "Bearer test-token"}
            )
            if response.status_code == 200:
                print("✅ Cell获取成功")
            else:
                print(f"❌ Cell获取失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Cell获取异常: {e}")
        
        # 3. 测试更新Cell
        print(f"\n3. 测试更新Cell {cell_id}...")
        try:
            update_data = {
                "title": "更新后的QA Cell",
                "content": {
                    "question": "这是一个测试问题",
                    "answer": "",
                    "isAIAnswer": False
                }
            }
            response = await client.put(
                f"{BASE_URL}/cells/{cell_id}",
                json=update_data,
                headers={"Authorization": "Bearer test-token"}
            )
            if response.status_code == 200:
                print("✅ Cell更新成功")
            else:
                print(f"❌ Cell更新失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Cell更新异常: {e}")
        
        # 4. 测试QA问答功能
        print(f"\n4. 测试QA问答功能...")
        try:
            qa_data = {
                "question": "什么是Python？",
                "ask_ai": True
            }
            response = await client.post(
                f"{BASE_URL}/cells/{cell_id}/ask",
                json=qa_data,
                headers={"Authorization": "Bearer test-token"}
            )
            if response.status_code == 200:
                qa_response = response.json()
                print(f"✅ QA问答成功: {qa_response['answer'][:100]}...")
                print(f"   置信度: {qa_response.get('confidence', 'N/A')}")
            else:
                print(f"❌ QA问答失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ QA问答异常: {e}")
        
        # 5. 测试获取相关问题建议
        print(f"\n5. 测试获取相关问题建议...")
        try:
            response = await client.get(
                f"{BASE_URL}/cells/{cell_id}/qa/suggestions",
                headers={"Authorization": "Bearer test-token"}
            )
            if response.status_code == 200:
                suggestions = response.json()
                print(f"✅ 获取建议成功: {suggestions.get('suggestions', [])}")
            else:
                print(f"❌ 获取建议失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ 获取建议异常: {e}")
        
        # 6. 测试Cell执行
        print(f"\n6. 测试Cell执行...")
        try:
            execution_data = {
                "cell_id": cell_id,
                "parameters": {}
            }
            response = await client.post(
                f"{BASE_URL}/cells/{cell_id}/execute",
                json=execution_data,
                headers={"Authorization": "Bearer test-token"}
            )
            if response.status_code == 200:
                execution_response = response.json()
                print(f"✅ Cell执行成功: {execution_response['output'][:100]}...")
            else:
                print(f"❌ Cell执行失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Cell执行异常: {e}")
        
        # 7. 测试获取教案的所有Cells
        print(f"\n7. 测试获取教案的所有Cells...")
        try:
            response = await client.get(
                f"{BASE_URL}/cells/lesson/{TEST_LESSON_ID}",
                headers={"Authorization": "Bearer test-token"}
            )
            if response.status_code == 200:
                cells = response.json()
                print(f"✅ 获取Cells成功，共 {len(cells)} 个Cell")
            else:
                print(f"❌ 获取Cells失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ 获取Cells异常: {e}")
        
        # 8. 测试复制Cell
        print(f"\n8. 测试复制Cell...")
        try:
            response = await client.post(
                f"{BASE_URL}/cells/{cell_id}/duplicate",
                headers={"Authorization": "Bearer test-token"}
            )
            if response.status_code == 201:
                duplicate_cell = response.json()
                print(f"✅ Cell复制成功，新ID: {duplicate_cell['id']}")
            else:
                print(f"❌ Cell复制失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Cell复制异常: {e}")
        
        print("\n🎉 Cell API测试完成！")

def print_api_endpoints():
    """打印API端点信息"""
    print("📋 Cell API端点列表:")
    print("=" * 50)
    print("POST   /api/v1/cells/                    - 创建Cell")
    print("GET    /api/v1/cells/{cell_id}           - 获取单个Cell")
    print("PUT    /api/v1/cells/{cell_id}           - 更新Cell")
    print("DELETE /api/v1/cells/{cell_id}           - 删除Cell")
    print("GET    /api/v1/cells/lesson/{lesson_id}  - 获取教案的所有Cells")
    print("POST   /api/v1/cells/{cell_id}/duplicate - 复制Cell")
    print("POST   /api/v1/cells/{cell_id}/execute   - 执行Cell")
    print("POST   /api/v1/cells/{cell_id}/ask       - QA问答")
    print("GET    /api/v1/cells/{cell_id}/qa/suggestions - 获取相关问题建议")
    print("POST   /api/v1/cells/{cell_id}/qa/evaluate    - 评估回答质量")
    print("PUT    /api/v1/cells/{cell_id}/qa        - 更新QA Cell内容")
    print("=" * 50)

if __name__ == "__main__":
    print_api_endpoints()
    print("\n注意: 此测试需要后端服务运行在 http://localhost:8000")
    print("并且需要有效的认证token")
    print("\n要运行测试，请执行: python test_cell_api.py")
    
    # 取消注释下面的行来运行测试
    # asyncio.run(test_cell_api())
