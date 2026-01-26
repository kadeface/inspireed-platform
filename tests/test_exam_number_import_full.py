#!/usr/bin/env python3
"""
带考号的学生导入完整测试脚本

测试流程：
1. 登录获取 token
2. 查找现有学校和学期
3. 创建考试
4. 导入考号映射
5. 验证导入结果
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# 测试数据
TEST_EXAM = {
    "name": "2024期中考试（测试）",
    "exam_date": "2024-01-15",
    "description": "自动化测试用的期中考试"
}


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
        print(response.text)
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
                print(f"✅ 找到学校: {school['name']} (ID: {school['id']})")
                return school

        print(f"⚠️  未找到测试学校（代码: 9999）")
        print(f"📊 现有学校列表（前5个）:")
        for school in schools[:5]:
            if isinstance(school, dict):
                print(f"  - {school.get('name')} (代码: {school.get('code')})")
        return None
    else:
        print(f"❌ 查询学校失败: {response.status_code}")
        return None


def get_semester(token):
    """获取当前学期"""
    print_step("步骤3: 获取当前学期")

    response = requests.get(
        f"{BASE_URL}/semesters",
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        semesters = response.json()
        if semesters and len(semesters) > 0:
            # 获取第一个学期
            semester = semesters[0]
            print(f"✅ 使用学期: {semester['name']} (ID: {semester['id']})")
            return semester
        else:
            print(f"⚠️  系统中没有学期")
            return None
    else:
        print(f"❌ 查询学期失败: {response.status_code}")
        return None


def create_exam(token, school, semester):
    """创建考试"""
    print_step("步骤4: 创建考试")

    print(f"📝 创建考试: {TEST_EXAM['name']}")
    print(f"   学校: {school['name']}")
    print(f"   学期: {semester['name']}")
    print(f"   日期: {TEST_EXAM['exam_date']}")

    # 首先需要查询年级ID（7年级）
    grades_response = requests.get(
        f"{BASE_URL}/curriculum/grades",
        headers={"Authorization": f"Bearer {token}"}
    )

    grade_id = None
    if grades_response.status_code == 200:
        grades = grades_response.json()
        for g in grades:
            if g["level"] == 7:
                grade_id = g["id"]
                print(f"   年级: {g['name']} (ID: {grade_id})")
                break

    if not grade_id:
        print("⚠️  未找到7年级，无法创建考试")
        return None

    # 创建考试
    response = requests.post(
        f"{BASE_URL}/exams",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": TEST_EXAM["name"],
            "exam_date": f"{TEST_EXAM['exam_date']} 09:00:00",  # 完整的datetime格式
            "exam_type": "midterm",  # 使用枚举值: midterm, final, monthly, unit, mock, district_unified, entrance
            "description": TEST_EXAM["description"],
            "semester_id": semester["id"],
            "grade_id": grade_id,
            "school_id": school["id"]
        }
    )

    if response.status_code in [200, 201]:  # 200 OK 或 201 Created
        exam = response.json()
        print(f"✅ 考试创建成功 (ID: {exam['id']})")
        return exam
    else:
        print(f"❌ 考试创建失败: {response.status_code}")
        print(f"响应: {response.text[:500]}")
        return None


def import_exam_numbers(token, exam):
    """导入考号映射"""
    print_step("步骤5: 导入考号映射")

    excel_file = "/Users/382241106qq.com/inspireed-platform-main/test_exam_numbers_import.xlsx"

    print(f"📂 Excel 文件: {excel_file}")
    print(f"📊 考试ID: {exam['id']}")
    print(f"📝 考试名称: {exam['name']}")

    with open(excel_file, "rb") as f:
        files = {
            "file": (
                "test_exam_numbers_import.xlsx",
                f,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        }

        # 注意：API 端点是 /api/v1/exams/{exam_id}/students/import
        response = requests.post(
            f"{BASE_URL}/exams/{exam['id']}/students/import",
            headers={"Authorization": f"Bearer {token}"},
            files=files,
            timeout=60
        )

    print(f"\n状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ 导入完成")
        print(f"📊 总记录数: {result.get('total', 'N/A')}")
        print(f"✅ 成功: {result.get('success', 'N/A')}")
        print(f"❌ 失败: {result.get('failed', 'N/A')}")
        print(f"🆕 创建: {result.get('created', 'N/A')}")
        print(f"🔄 更新: {result.get('updated', 'N/A')}")

        if result.get('errors'):
            print(f"\n⚠️  错误详情:")
            for error in result['errors'][:10]:
                print(f"  行 {error['row']}: {error.get('message', 'Unknown error')}")
            if len(result['errors']) > 10:
                print(f"  ... 还有 {len(result['errors']) - 10} 个错误")

        return result
    else:
        print(f"❌ 导入失败")
        print(f"响应: {response.text[:500]}")
        return None


def verify_mappings(token, exam):
    """验证考号映射"""
    print_step("步骤6: 验证考号映射")

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
                print(f"    学生: {mapping.get('student_name', 'N/A')}")
                print(f"    身份证号: {mapping.get('student_id_number', 'N/A')}")
                print(f"    学校: {mapping.get('school_name', 'N/A')}")
                print(f"    班级: {mapping.get('classroom_name', 'N/A')}")
                print()

        return mappings
    else:
        print(f"❌ 查询失败: {response.status_code}")
        print(response.text)
        return None


def export_exam_numbers(token, exam):
    """导出考号（可选功能测试）"""
    print_step("步骤7: 导出考号Excel")

    response = requests.get(
        f"{BASE_URL}/exams/{exam['id']}/exam-numbers/export",
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        print(f"✅ 导出成功")
        print(f"📄 文件大小: {len(response.content)} 字节")

        # 保存导出的文件
        output_file = "/Users/382241106qq.com/inspireed-platform-main/exported_exam_numbers.xlsx"
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"💾 已保存到: {output_file}")
        return True
    else:
        print(f"⚠️  导出失败: {response.status_code}")
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  带考号的学生导入测试")
    print("="*60)

    try:
        # 1. 登录
        token = login()
        time.sleep(1)

        # 2. 获取学校
        school = get_school(token)
        if not school:
            print("\n⚠️  无法找到测试学校，测试终止")
            print("提示: 请先运行不带考号的学生导入测试来创建学校")
            return

        time.sleep(1)

        # 3. 获取学期
        semester = get_semester(token)
        if not semester:
            print("\n⚠️  无法获取学期，测试终止")
            return

        time.sleep(1)

        # 4. 创建考试
        exam = create_exam(token, school, semester)
        if not exam:
            print("\n⚠️  无法创建考试，测试终止")
            return

        time.sleep(1)

        # 5. 导入考号
        import_result = import_exam_numbers(token, exam)
        time.sleep(1)

        # 6. 验证映射
        if import_result and import_result.get('success', 0) > 0:
            verify_mappings(token, exam)
            time.sleep(1)

            # 7. 导出考号（可选）
            export_exam_numbers(token, exam)

            print("\n" + "="*60)
            print("  ✅ 测试完成！")
            print("="*60)
            print(f"\n最终统计:")
            print(f"  考试: {exam['name']} (ID: {exam['id']})")
            print(f"  总记录数: {import_result.get('total', 'N/A')}")
            print(f"  成功: {import_result.get('success', 'N/A')}")
            print(f"  失败: {import_result.get('failed', 'N/A')}")
            print(f"  创建映射: {import_result.get('created', 'N/A')}")
            print(f"  更新映射: {import_result.get('updated', 'N/A')}")
        else:
            print("\n" + "="*60)
            print("  ⚠️  测试完成，但有错误")
            print("="*60)

    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
