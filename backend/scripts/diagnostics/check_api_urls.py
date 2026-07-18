#!/usr/bin/env python3
"""
测试API返回的URL格式
验证所有URL是否为完整URL格式
"""
import requests
import json
import re
import sys
from typing import List, Dict, Any


def check_url_format(url: str, field_name: str) -> bool:
    """检查URL格式是否正确"""
    if not url:
        return True  # None或空字符串视为有效
    
    # blob URL和data URL是临时的，不需要检查
    if url.startswith(('blob:', 'data:')):
        return True
    
    # 完整URL格式：http:// 或 https://
    if url.startswith(('http://', 'https://')):
        return True
    
    # 文件名格式或相对路径格式都是错误的
    print(f"    ❌ {field_name} 格式错误: {url}")
    return False


def test_lesson_urls(base_url: str, token: str, lesson_id: int) -> bool:
    """测试教案API返回的URL格式"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 获取教案详情
    try:
        response = requests.get(f"{base_url}/api/v1/lessons/{lesson_id}", headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"❌ API请求失败: {e}")
        return False
    
    if response.status_code != 200:
        print(f"❌ API请求失败: HTTP {response.status_code}")
        print(f"响应: {response.text[:200]}")
        return False
    
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        return False
    
    print("=" * 80)
    print(f"测试教案 ID={lesson_id}")
    print(f"标题: {data.get('title', 'N/A')}")
    print("=" * 80)
    
    all_correct = True
    
    # 检查封面图URL
    cover_url = data.get('cover_image_url')
    if cover_url:
        print(f"\n封面图URL: {cover_url}")
        if not check_url_format(cover_url, "cover_image_url"):
            all_correct = False
        else:
            print("  ✅ 封面图URL格式正确: 完整URL")
    
    # 检查content中的URL
    content = data.get('content', [])
    print(f"\n检查 {len(content)} 个单元:")
    
    for idx, cell in enumerate(content):
        cell_type = cell.get('type')
        cell_content = cell.get('content', {})
        
        print(f"\n  单元 {idx+1} (类型: {cell_type}):")
        
        if cell_type == 'video':
            video_url = cell_content.get('videoUrl')
            if video_url:
                print(f"    videoUrl: {video_url}")
                if check_url_format(video_url, "videoUrl"):
                    print("      ✅ videoUrl格式正确: 完整URL")
                else:
                    all_correct = False
            
            thumbnail = cell_content.get('thumbnail')
            if thumbnail:
                print(f"    thumbnail: {thumbnail}")
                if check_url_format(thumbnail, "thumbnail"):
                    print("      ✅ thumbnail格式正确: 完整URL")
                else:
                    all_correct = False
        
        elif cell_type == 'text':
            html = cell_content.get('html', '')
            if html and '<img' in html:
                # 提取img标签的src
                img_srcs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
                if img_srcs:
                    print(f"    找到 {len(img_srcs)} 个图片URL:")
                    for i, src in enumerate(img_srcs[:5], 1):  # 只显示前5个
                        print(f"      图片{i}: {src[:80]}{'...' if len(src) > 80 else ''}")
                        if not check_url_format(src, f"图片{i}"):
                            all_correct = False
                        elif src.startswith(('http://', 'https://')):
                            print(f"        ✅ 图片URL格式正确: 完整URL")
    
    print("\n" + "=" * 80)
    if all_correct:
        print("✅ 所有URL格式正确！")
    else:
        print("❌ 发现URL格式错误")
    print("=" * 80)
    
    return all_correct


def test_resource_urls(base_url: str, token: str) -> bool:
    """测试资源API返回的URL格式"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{base_url}/api/v1/resources/?page_size=5", headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"❌ API请求失败: {e}")
        return False
    
    if response.status_code != 200:
        print(f"❌ API请求失败: HTTP {response.status_code}")
        return False
    
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        return False
    
    resources = data.get('items', [])
    print(f"\n测试资源API: 检查 {len(resources)} 个资源")
    
    all_correct = True
    for resource in resources[:3]:  # 只检查前3个
        file_url = resource.get('file_url')
        thumbnail_url = resource.get('thumbnail_url')
        resolved_file_url = resource.get('resolved_file_url')
        
        print(f"\n  资源 ID={resource.get('id')}, 类型={resource.get('resource_type')}")
        
        if file_url:
            if not check_url_format(file_url, "file_url"):
                all_correct = False
            else:
                print(f"      ✅ file_url格式正确")
        
        if thumbnail_url:
            if not check_url_format(thumbnail_url, "thumbnail_url"):
                all_correct = False
            else:
                print(f"      ✅ thumbnail_url格式正确")
        
        if resolved_file_url:
            if not check_url_format(resolved_file_url, "resolved_file_url"):
                all_correct = False
            else:
                print(f"      ✅ resolved_file_url格式正确")
    
    return all_correct


def main():
    """主函数"""
    # 配置（从命令行参数或环境变量获取）
    if len(sys.argv) > 1:
        lesson_id = int(sys.argv[1])
    else:
        lesson_id = 97  # 默认测试教案ID
    
    if len(sys.argv) > 2:
        token = sys.argv[2]
    else:
        token = input("请输入JWT Token（或设置环境变量 TOKEN）: ").strip()
        if not token:
            print("❌ 需要提供Token")
            sys.exit(1)
    
    base_url = "http://localhost:8000"
    
    print("\n" + "=" * 80)
    print(" API URL格式测试")
    print("=" * 80)
    print(f"Base URL: {base_url}")
    print(f"Token: {token[:20]}...")
    print()
    
    # 测试教案API
    lesson_ok = test_lesson_urls(base_url, token, lesson_id)
    
    # 测试资源API
    resource_ok = test_resource_urls(base_url, token)
    
    # 总结
    print("\n" + "=" * 80)
    print(" 测试总结")
    print("=" * 80)
    print(f"教案API URL格式: {'✅ 通过' if lesson_ok else '❌ 失败'}")
    print(f"资源API URL格式: {'✅ 通过' if resource_ok else '❌ 失败'}")
    
    if lesson_ok and resource_ok:
        print("\n✅ 所有测试通过！URL格式转换功能正常工作。")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败，请检查URL转换逻辑。")
        sys.exit(1)


if __name__ == "__main__":
    main()

