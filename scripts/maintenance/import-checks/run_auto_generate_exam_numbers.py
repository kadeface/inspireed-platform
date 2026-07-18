#!/usr/bin/env python3
"""
系统自动生成考号测试脚本

测试流程：
1. 登录获取 token
2. 查找/创建考试
3. 为考试自动生成考号
4. 验证生成的考号
5. 测试冲突处理（重复生成）
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"


def print_step(step_name):
    """打印步骤标题"""
    print(f"\n{'='*60}")
    print(f"  {step_name}")
    print(f"{'='*60}")


def login():
    """登录获取 token"""
    print_step("步骤1: 登录系统")

    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin@inspireed.com", "password": "admin123"}
    )

    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ 登录成功")
        return token
    else:
        print(f"❌ 登录失败: {response.status_code}")
        exit(1)


def get_school(token):
    """获取测试学校"""
    print_step("步骤2: 获取测试学校")

    response = requests.get(
        f"{BASE_URL}/admin/organization/schools",
        params={"size": 100},
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        data = response.json()
        schools = data.get("schools", data.get("items", [])) if isinstance(data, dict) else data

        for school in schools:
            if isinstance(school, dict) and school.get("code") == "9999":
                print(f"✅ 找到学校: {school['name']} (代码: {school['code']})")
                return school

        print(f"⚠️  未找到测试学校")
        return None
    else:
        print(f"❌ 查询失败: {response.status_code}")
        return None


def get_exam(token, school):
    """获取或创建考试"""
    print_step("步骤3: 创建新考试（用于自动生成考号测试）")

    # 直接创建新考试（避免使用已有考号的考试）
    print(f"📝 创建新考试")

    # 获取学期
    response = requests.get(
        f"{BASE_URL}/semesters",
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code != 200 or not response.json():
        print(f"❌ 无法获取学期")
        return None

    semester = response.json()[0]

    # 获取年级
    response = requests.get(
        f"{BASE_URL}/curriculum/grades",
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code != 200:
        print(f"❌ 无法获取年级")
        return None

    grades = response.json()
    grade_id = None
    for g in grades:
        if g["level"] == 7:
            grade_id = g["id"]
            break

    if not grade_id:
        print(f"❌ 未找到7年级")
        return None

    # 创建考试
    response = requests.post(
        f"{BASE_URL}/exams",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "自动生成考号测试",
            "exam_date": "2024-01-20 09:00:00",
            "exam_type": "midterm",
            "description": "用于测试自动生成考号功能",
            "semester_id": semester["id"],
            "grade_id": grade_id,
            "school_id": school["id"]
        }
    )

    if response.status_code in [200, 201]:
        exam = response.json()
        print(f"✅ 考试创建成功 (ID: {exam['id']})")
        return exam
    else:
        print(f"❌ 考试创建失败: {response.status_code}")
        print(response.text[:200])
        return None


def generate_exam_numbers(token, exam, school):
    """自动生成考号"""
    print_step("步骤4: 自动生成考号")

    print(f"📝 考试: {exam['name']} (ID: {exam['id']})")
    print(f"🏫 学校: {school['name']} (代码: {school['code']})")

    # 调用生成考号API
    response = requests.post(
        f"{BASE_URL}/exams/generate-exam-numbers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "exam_id": exam["id"],
            "school_id": school["id"],
            "auto_generate": True
        }
    )

    print(f"\n状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ 生成完成")
        print(f"📊 生成数量: {result.get('generated', 'N/A')}")
        print(f"⚠️  解决冲突: {result.get('conflicts', 'N/A')}")

        # 显示生成的考号（前10个）
        exam_numbers = result.get("exam_numbers", [])
        if exam_numbers:
            print(f"\n生成的考号列表（前10个）:")
            for item in exam_numbers[:10]:
                print(f"  学生ID: {item.get('student_id')} -> 考号: {item.get('exam_number')}")

        return result
    else:
        print(f"❌ 生成失败")
        print(f"响应: {response.text[:500]}")
        return None


def verify_mappings(token, exam):
    """验证考号映射"""
    print_step("步骤5: 验证考号映射")

    # 查询考号映射
    response = requests.get(
        f"{BASE_URL}/exams/{exam['id']}/exam-numbers",
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        mappings = response.json()
        print(f"📊 考号映射数量: {len(mappings) if isinstance(mappings, list) else 'N/A'}")

        if isinstance(mappings, list) and len(mappings) > 0:
            print(f"\n考号映射列表:")
            for mapping in mappings:
                print(f"  - 考号: {mapping.get('exam_number')}")
                print(f"    学生ID: {mapping.get('student_id')}")
                print(f"    身份证号: {mapping.get('student_id_number')}")
                print(f"    学校: {mapping.get('school_name')}")
                print(f"    班级: {mapping.get('classroom_name')}")
                print()

            # 验证考号格式
            print(f"\n✅ 考号格式验证:")
            for mapping in mappings[:5]:
                exam_number = mapping.get("exam_number")
                if exam_number:
                    print(f"  {exam_number} - ", end="")
                    if len(exam_number) == 12 and exam_number.isdigit():
                        print(f"✅ 格式正确 (12位数字)")
                        # 解析考号
                        school_code = exam_number[0:4]
                        year = exam_number[4:8]
                        class_seq = exam_number[8:10]
                        seat = exam_number[10:12]
                        print(f"      学校代码: {school_code}, 年份: {year}, 班级: {class_seq}, 座位: {seat}")
                    else:
                        print(f"❌ 格式错误")
        return mappings
    else:
        print(f"❌ 查询失败: {response.status_code}")
        return None


def test_conflict_handling(token, exam, school):
    """测试冲突处理（重复生成）"""
    print_step("步骤6: 测试冲突处理")

    print(f"📝 再次调用生成考号API（测试冲突处理）")

    # 第二次调用生成考号API
    response = requests.post(
        f"{BASE_URL}/exams/generate-exam-numbers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "exam_id": exam["id"],
            "school_id": school["id"],
            "auto_generate": True
        }
    )

    print(f"\n状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ 生成完成")
        print(f"📊 生成数量: {result.get('generated', 'N/A')}")
        print(f"⚠️  解决冲突: {result.get('conflicts', 'N/A')}")

        # 检查是否有字母后缀
        exam_numbers = result.get("exam_numbers", [])
        if exam_numbers:
            print(f"\n检查字母后缀（冲突处理）:")
            has_suffix = False
            for item in exam_numbers[:10]:
                exam_number = item.get("exam_number", "")
                if exam_number and not exam_number[-1].isdigit():
                    print(f"  {exam_number} - ✅ 检测到字母后缀")
                    has_suffix = True
                elif exam_number:
                    print(f"  {exam_number}")

            if not has_suffix:
                print(f"  ℹ️  本次生成未检测到冲突（所有考号都是数字）")

        return result
    else:
        print(f"❌ 生成失败")
        print(f"响应: {response.text[:500]}")
        return None


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  系统自动生成考号测试")
    print("="*60)

    try:
        # 1. 登录
        token = login()
        time.sleep(1)

        # 2. 获取学校
        school = get_school(token)
        if not school:
            print("\n⚠️  无法找到测试学校，测试终止")
            return

        time.sleep(1)

        # 3. 获取/创建考试
        exam = get_exam(token, school)
        if not exam:
            print("\n⚠️  无法获取考试，测试终止")
            return

        time.sleep(1)

        # 4. 生成考号
        generate_result = generate_exam_numbers(token, exam, school)
        if not generate_result:
            print("\n⚠️  生成考号失败")
            return

        time.sleep(1)

        # 5. 验证映射
        mappings = verify_mappings(token, exam)

        time.sleep(1)

        # 6. 测试冲突处理
        conflict_result = test_conflict_handling(token, exam, school)

        print("\n" + "="*60)
        print("  ✅ 测试完成！")
        print("="*60)

        print(f"\n最终统计:")
        print(f"  考试: {exam['name']} (ID: {exam['id']})")
        print(f"  学校: {school['name']} (代码: {school['code']})")
        print(f"  首次生成: {generate_result.get('generated', 'N/A')} 个考号")
        print(f"  冲突解决: {generate_result.get('conflicts', 'N/A')} 个")
        if conflict_result:
            print(f"  重复生成: {conflict_result.get('generated', 'N/A')} 个考号")
            print(f"  新冲突: {conflict_result.get('conflicts', 'N/A')} 个")

        print(f"\n考号格式说明:")
        print(f"  学校代码(4位) + 入学年份(4位) + 班级序号(2位) + 座位号(2位)")
        print(f"  示例: {school['code']} + 2024 + 01 + 01 = {school['code']}20240101")

    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
