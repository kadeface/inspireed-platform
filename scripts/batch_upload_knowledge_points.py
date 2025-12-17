#!/usr/bin/env python3
"""
批量上传小学奥数知识点HTML互动课件到资源库

使用方法:
    python batch_upload_knowledge_points.py <html_directory> [--api-base <url>] [--token <token>]

文件名格式:
    [年级]_[分类]_[知识点].html
    例如: 三年级_计算类_速算技巧_乘法口诀可视化.html
         一年级_几何类_图形认知_认识基本图形.html
"""

import os
import sys
import re
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict, Tuple

# 知识点分类映射
KNOWLEDGE_POINT_CATEGORIES = {
    '计算类': {
        '速算技巧': '计算类/速算技巧',
        '巧算方法': '计算类/巧算方法',
        '数论基础': '计算类/数论基础',
    },
    '几何类': {
        '图形认知': '几何类/图形认知',
        '面积周长': '几何类/面积周长',
        '立体图形': '几何类/立体图形',
    },
    '应用题类': {
        '行程问题': '应用题类/行程问题',
        '工程问题': '应用题类/工程问题',
        '浓度问题': '应用题类/浓度问题',
    },
    '逻辑推理类': {
        '排列组合': '逻辑推理类/排列组合',
        '逻辑推理': '逻辑推理类/逻辑推理',
        '数独游戏': '逻辑推理类/数独游戏',
    },
}

# 年级映射
GRADE_MAP = {
    '一年级': 1,
    '二年级': 2,
    '三年级': 3,
    '四年级': 4,
    '五年级': 5,
    '六年级': 6,
}


def parse_filename(filename: str) -> Optional[Dict[str, str]]:
    """
    解析文件名，提取年级、分类、知识点信息
    
    格式: [年级]_[分类]_[子分类]_[知识点名称].html
    """
    # 移除扩展名
    name = filename.replace('.html', '').replace('.htm', '')
    
    # 按下划线分割
    parts = name.split('_')
    
    if len(parts) < 3:
        return None
    
    result = {
        'grade': parts[0],
        'category': parts[1] if len(parts) > 1 else None,
        'subcategory': parts[2] if len(parts) > 2 else None,
        'knowledge_point': '_'.join(parts[3:]) if len(parts) > 3 else parts[2],
    }
    
    return result


def get_grade_id(grade_name: str) -> Optional[int]:
    """根据年级名称获取年级ID"""
    return GRADE_MAP.get(grade_name)


def get_knowledge_point_category(category: str, subcategory: str) -> Optional[str]:
    """获取知识点分类字符串"""
    if category in KNOWLEDGE_POINT_CATEGORIES:
        if subcategory in KNOWLEDGE_POINT_CATEGORIES[category]:
            return KNOWLEDGE_POINT_CATEGORIES[category][subcategory]
    return None


def upload_file(
    file_path: Path,
    api_base: str,
    token: str,
    metadata: Dict
) -> bool:
    """上传文件到资源库"""
    url = f"{api_base}/api/v1/library/assets"
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.name, f, 'text/html')}
        
        data = {
            'title': metadata['title'],
            'description': metadata.get('description', ''),
            'asset_type': 'interactive',
            'visibility': 'school',
            'subject_id': metadata.get('subject_id'),
            'grade_id': metadata.get('grade_id'),
            'knowledge_point_category': metadata.get('knowledge_point_category'),
            'knowledge_point_name': metadata.get('knowledge_point_name'),
        }
        
        # 移除None值
        data = {k: v for k, v in data.items() if v is not None}
        
        try:
            response = requests.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()
            result = response.json()
            print(f"✓ 上传成功: {metadata['title']} (ID: {result.get('id')})")
            return True
        except requests.exceptions.RequestException as e:
            print(f"✗ 上传失败: {metadata['title']} - {str(e)}")
            return False


def main():
    parser = argparse.ArgumentParser(description='批量上传知识点HTML课件到资源库')
    parser.add_argument('directory', help='HTML文件目录')
    parser.add_argument('--api-base', default='http://localhost:8000', help='API基础URL')
    parser.add_argument('--token', required=True, help='认证Token')
    parser.add_argument('--subject-id', type=int, default=1, help='学科ID（默认：数学=1）')
    parser.add_argument('--dry-run', action='store_true', help='仅显示将要上传的文件，不实际上传')
    
    args = parser.parse_args()
    
    directory = Path(args.directory)
    if not directory.exists() or not directory.is_dir():
        print(f"错误: 目录不存在: {directory}")
        sys.exit(1)
    
    # 查找所有HTML文件
    html_files = list(directory.glob('*.html')) + list(directory.glob('*.htm'))
    
    if not html_files:
        print(f"未找到HTML文件: {directory}")
        sys.exit(1)
    
    print(f"找到 {len(html_files)} 个HTML文件")
    print("-" * 60)
    
    success_count = 0
    fail_count = 0
    
    for html_file in html_files:
        # 解析文件名
        parsed = parse_filename(html_file.name)
        
        if not parsed:
            print(f"✗ 跳过（文件名格式不正确）: {html_file.name}")
            fail_count += 1
            continue
        
        # 构建元数据
        grade_id = get_grade_id(parsed['grade'])
        knowledge_point_category = get_knowledge_point_category(
            parsed['category'],
            parsed['subcategory']
        )
        
        metadata = {
            'title': parsed['knowledge_point'] or html_file.stem,
            'description': f"知识点分类: {knowledge_point_category or parsed['category']}",
            'subject_id': args.subject_id,
            'grade_id': grade_id,
            'knowledge_point_category': knowledge_point_category,
            'knowledge_point_name': parsed['knowledge_point'],
        }
        
        print(f"处理: {html_file.name}")
        print(f"  标题: {metadata['title']}")
        print(f"  年级: {parsed['grade']} (ID: {grade_id})")
        print(f"  分类: {knowledge_point_category}")
        
        if args.dry_run:
            print("  [DRY RUN] 将上传此文件")
        else:
            if upload_file(html_file, args.api_base, args.token, metadata):
                success_count += 1
            else:
                fail_count += 1
        
        print("-" * 60)
    
    print(f"\n完成!")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")


if __name__ == '__main__':
    main()
