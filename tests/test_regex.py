#!/usr/bin/env python3
import re

def parse_classroom_code(classroom_code: str):
    """带调试输出的解析函数"""
    if not classroom_code:
        return None, None

    code = str(classroom_code).strip()

    print(f"测试代码: '{code}'")

    # 匹配格式：前N位是年级，后M位是班级序号
    match = re.match(r'^(\d+)(\d{1,2})$', code)
    if not match:
        print("  ❌ 正则表达式不匹配")
        return None, None

    print("  ✅ 正则表达式匹配成功")

    grade_part = match.group(1)
    class_part = match.group(2)

    print(f"  grade_part = '{grade_part}'")
    print(f"  class_part = '{class_part}'")

    try:
        grade_level = int(grade_part)
        class_seq = int(class_part)

        print(f"  grade_level = {grade_level}")
        print(f"  class_seq = {class_seq}")

        # 验证范围：年级1-12，班级序号1-99
        if 1 <= grade_level <= 12 and 1 <= class_seq <= 99:
            print(f"  ✅ 验证通过")
            return grade_level, class_seq
        else:
            print(f"  ❌ 验证失败: grade_level={grade_level}, class_seq={class_seq}")
    except ValueError as e:
        print(f"  ❌ 转换失败: {e}")

    return None, None

# 测试不同格式
test_cases = [
    "701",    # 3位
    "0701",   # 4位（以0开头）
    "1001",   # 4位（10年级）
    "1203",   # 4位（12年级）
    "00701",  # 5位（以00开头）
    "01001",  # 5位（10年级）
    "01203",  # 5位（12年级）
]

for code in test_cases:
    print(f"\n{'='*50}")
    result = parse_classroom_code(code)
    print(f"结果: {result}")
