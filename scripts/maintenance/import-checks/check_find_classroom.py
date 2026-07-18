#!/usr/bin/env python3
"""
测试班级查找逻辑（模拟 StudentImportService.find_classroom）
"""
import requests
import re

BASE_URL = "http://localhost:8000/api/v1"

def parse_classroom_code(classroom_code: str):
    """解析班级编号"""
    code = str(classroom_code).strip()
    match = re.match(r'^(\d+)(\d{1,2})$', code)
    if match:
        grade_part = match.group(1)
        class_part = match.group(2)
        try:
            grade_level = int(grade_part)
            class_seq = int(class_part)
            if 1 <= grade_level <= 12 and 1 <= class_seq <= 99:
                return grade_level, class_seq
        except ValueError:
            pass
    return None, None

# 登录
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "admin@inspireed.com", "password": "admin123"}
)

if response.status_code == 200:
    token = response.json().get("access_token")

    # 测试解析
    classroom_code = "0701"  # 使用4位格式
    grade_level, class_seq = parse_classroom_code(classroom_code)
    print(f"解析班级编号: {classroom_code}")
    print(f"  -> grade_level = {grade_level}")
    print(f"  -> class_seq = {class_seq}")

    if grade_level and class_seq:
        # 查询年级
        response = requests.get(
            f"{BASE_URL}/curriculum/grades",
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code == 200:
            grades = response.json()
            grade = None
            for g in grades:
                if g["level"] == grade_level:
                    grade = g
                    break

            if grade:
                print(f"\n找到年级: {grade['name']} (ID: {grade['id']})")

                # 查询班级
                school_id = 556
                response = requests.get(
                    f"{BASE_URL}/admin/organization/classrooms",
                    params={"school_id": school_id},
                    headers={"Authorization": f"Bearer {token}"}
                )

                if response.status_code == 200:
                    data = response.json()
                    classrooms = data.get("classrooms", data.get("items", [])) if isinstance(data, dict) else data

                    print(f"\n学校 {school_id} 的所有班级:")
                    for cls in classrooms:
                        if isinstance(cls, dict):
                            print(f"  ID={cls.get('id')}, name='{cls.get('name')}', code='{cls.get('code')}', grade_id={cls.get('grade_id')}")

                    # 测试匹配模式
                    print(f"\n尝试匹配班级 (grade_id={grade['id']}, class_seq={class_seq}):")
                    classroom_name_patterns = [
                        f"{grade['name']}{class_seq}班",  # 如：七年级1班
                        f"{grade['name']}第{class_seq}班",  # 如：七年级第1班
                        f"{class_seq}班",  # 如：1班
                    ]

                    for pattern in classroom_name_patterns:
                        print(f"  模式: '{pattern}'")
                        for cls in classrooms:
                            if isinstance(cls, dict) and cls.get("grade_id") == grade["id"]:
                                if cls.get("name") == pattern or cls.get("code") == classroom_code:
                                    print(f"    ✅ 匹配成功: ID={cls.get('id')}, name='{cls.get('name')}', code='{cls.get('code')}'")
                                    break
else:
    print("登录失败")
