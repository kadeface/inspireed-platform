#!/usr/bin/env python3
"""
测试lesson API返回的URL格式
"""
import sys
import os
import requests
import json

# 测试lesson 97的API响应
lesson_id = 97
base_url = "http://localhost:8000"  # 根据实际情况修改
token = input("请输入访问token（或按Enter使用默认）: ").strip() or "test_token"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 获取lesson
url = f"{base_url}/api/v1/lessons/{lesson_id}"
print(f"请求URL: {url}")
print(f"请求headers: {headers}")
print()

response = requests.get(url, headers=headers)
print(f"响应状态码: {response.status_code}")
print()

if response.status_code == 200:
    lesson_data = response.json()
    print("=" * 80)
    print("Lesson API 响应中的URL格式检查")
    print("=" * 80)
    
    content = lesson_data.get("content", [])
    print(f"\n内容单元数量: {len(content)}")
    
    for idx, cell in enumerate(content):
        cell_type = cell.get("type", "unknown")
        print(f"\n单元 {idx} (type={cell_type})")
        
        if cell_type == "text":
            cell_content = cell.get("content", {})
            html = cell_content.get("html", "")
            
            if html:
                import re
                img_srcs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
                
                if img_srcs:
                    print(f"  包含 {len(img_srcs)} 个图片:")
                    for i, src in enumerate(img_srcs, 1):
                        print(f"    图片 {i}: {src}")
                        if src.startswith("http://") or src.startswith("https://"):
                            print(f"      ✅ API返回的是完整URL（正确！）")
                        elif "/" not in src:
                            print(f"      ❌ API返回的是文件名（后端未转换）")
                        else:
                            print(f"      ⚠️  其他格式")
        elif cell_type == "video":
            cell_content = cell.get("content", {})
            video_url = cell_content.get("videoUrl") or cell_content.get("video_url")
            if video_url:
                print(f"  视频URL: {video_url}")
                if video_url.startswith("http://") or video_url.startswith("https://"):
                    print(f"    ✅ API返回的是完整URL（正确！）")
                else:
                    print(f"    ❌ API返回的是文件名（后端未转换）")
else:
    print(f"错误: {response.status_code}")
    print(response.text)

