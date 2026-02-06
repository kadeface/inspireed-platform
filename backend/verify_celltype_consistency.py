#!/usr/bin/env python3
"""
验证前后端 CellType 枚举是否一致
检查前端和后端的枚举值是否大小写匹配
"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def extract_backend_cell_types():
    """从后端models/cell.py提取CellType枚举值"""
    cell_types_file = PROJECT_ROOT / 'backend/app/models/cell.py'

    if not cell_types_file.exists():
        return None

    content = cell_types_file.read_text(encoding='utf-8')

    # 提取 CellType 类中的枚举值
    # 匹配格式: TEXT = "TEXT"
    pattern = r'(\w+)\s*=\s*"([^"]+)"'

    cell_types = {}
    in_celltype_class = False

    for line in content.split('\n'):
        if 'class CellType(str, Enum):' in line:
            in_celltype_class = True
            continue

        if in_celltype_class:
            if line.strip().startswith('class ') and 'CellType' not in line:
                break

            match = re.search(pattern, line)
            if match:
                key = match.group(1)
                value = match.group(2)
                cell_types[key] = value

    return set(cell_types.values())


def extract_frontend_cell_types():
    """从前端types/cell.ts提取CellType枚举值"""
    cell_types_file = PROJECT_ROOT / 'frontend/src/types/cell.ts'

    if not cell_types_file.exists():
        return None

    content = cell_types_file.read_text(encoding='utf-8')

    # 提取 CellType 对象中的值
    # 匹配格式: TEXT: 'TEXT',
    pattern = r"(\w+):\s*'([^']+)'"

    cell_types = {}
    in_celltype = False

    for line in content.split('\n'):
        if 'export const CellType = {' in line:
            in_celltype = True
            continue

        if in_celltype:
            if '}' in line and not "'" in line:
                break

            match = re.search(pattern, line)
            if match:
                key = match.group(1)
                value = match.group(2)
                cell_types[key] = value

    return cell_types


def check_consistency():
    """检查前后端枚举一致性"""
    print("🔍 验证前后端 CellType 枚举一致性")
    print("=" * 80)

    # 提取后端和前端枚举
    backend_types = extract_backend_cell_types()
    frontend_types = extract_frontend_cell_types()

    if not backend_types:
        print("❌ 无法提取后端枚举值")
        return False

    if not frontend_types:
        print("❌ 无法提取前端枚举值")
        return False

    print(f"\n📊 后端枚举值 ({len(backend_types)} 个):")
    print(f"   {', '.join(sorted(backend_types))}")

    print(f"\n📋 前端 CellType 枚举:")
    print("-" * 80)
    for key, value in sorted(frontend_types.items()):
        backend_has = value in backend_types
        status = "✅" if backend_has else "❌"
        print(f"{status}  {key:20} = '{value}'")

    print(f"\n总计: {len(frontend_types)} 个")

    # 检查一致性
    print("\n📊 一致性检查:")
    print("-" * 80)

    # 检查前端值是否都在后端中
    frontend_values = set(frontend_types.values())
    missing_in_backend = frontend_values - backend_types

    if missing_in_backend:
        print(f"❌ 前端有但后端没有的值: {missing_in_backend}")
    else:
        print("✅ 所有前端枚举值都在后端定义中")

    # 检查后端值是否都在前端中
    missing_in_frontend = backend_types - frontend_values

    if missing_in_frontend:
        print(f"⚠️  后端有但前端没有的值: {missing_in_frontend}")
    else:
        print("✅ 所有后端枚举值都在前端定义中")

    # 检查大小写
    print("\n🔤 大小写检查:")
    print("-" * 80)

    all_uppercase = all(v == v.upper() for v in frontend_values)

    if all_uppercase:
        print("✅ 所有前端枚举值都是大写")
    else:
        lowercase_values = [v for v in frontend_values if v != v.upper()]
        print(f"❌ 发现小写枚举值: {lowercase_values}")

    # 检查key和value是否一致
    print("\n🔄 Key-Value 一致性检查:")
    print("-" * 80)

    key_value_match = all(k == v for k, v in frontend_types.items() if not k.startswith('_'))

    if key_value_match:
        print("✅ 所有枚举的 key 和 value 一致")
    else:
        mismatched = [(k, v) for k, v in frontend_types.items() if k != v and not k.startswith('_')]
        print(f"⚠️  Key-Value 不匹配的项:")
        for k, v in mismatched:
            print(f"     {k} != {v}")

    # 总结
    print("\n" + "=" * 80)
    print("📈 验证总结")
    print("-" * 80)

    issues = []

    if missing_in_backend:
        issues.append(f"前端有 {len(missing_in_backend)} 个值在后端未定义")

    if not all_uppercase:
        issues.append(f"发现 {len(lowercase_values)} 个小写值")

    if not key_value_match:
        issues.append(f"发现 {len(mismatched)} 个 key-value 不匹配")

    if issues:
        print("\n❌ 发现问题:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("\n✅ 所有检查通过！")
        print("\n验证项:")
        print("  ✅ 前后端枚举值一致")
        print("  ✅ 所有值都是大写")
        print("  ✅ Key-Value 匹配")
        return True


if __name__ == "__main__":
    success = check_consistency()
    exit(0 if success else 1)
