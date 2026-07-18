#!/usr/bin/env python3
"""
学生账户导入完整测试脚本

步骤：
1. 登录获取 token
2. 创建测试学校
3. 检查/创建年级
4. 创建班级
5. 导入学生
6. 验证结果
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

# 测试数据
TEST_SCHOOL = {
    "name": "测试中学",
    "code": "0001",
    "region_name": "测试区"
}

TEST_GRADES = [7, 8, 10, 12]

TEST_CLASSROOMS = [
    {"grade_level": 7, "code": "701", "name": "7年级1班"},
    {"grade_level": 7, "code": "702", "name": "7年级2班"},
    {"grade_level": 8, "code": "801", "name": "8年级1班"},
    {"grade_level": 10, "code": "1001", "name": "10年级1班"},
    {"grade_level": 12, "code": "1203", "name": "12年级3班"},
]


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
        json={
            "username": "admin@inspireed.com",
            "password": "admin123"
        }
    )

    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ 登录成功")
        print(f"Token: {token[:20]}...")
        return token
    else:
        print(f"❌ 登录失败: {response.status_code}")
        print(response.text)
        exit(1)


def create_school(token):
    """创建测试学校"""
    print_step("步骤2: 创建测试学校")

    # 先检查学校是否已存在
    response = requests.get(
        f"{BASE_URL}/schools",
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        schools = response.json()
        for school in schools:
            if school.get("code") == TEST_SCHOOL["code"]:
                print(f"✅ 学校已存在: {school['name']} (ID: {school['id']})")
                return school["id"]

    # 创建新学校
    print(f"📝 创建学校: {TEST_SCHOOL['name']}")

    # 首先需要创建测试区域或查找现有区域
    region_response = requests.get(
        f"{BASE_URL}/regions",
        headers={"Authorization": f"Bearer {token}"}
    )

    region_id = None
    if region_response.status_code == 200:
        regions = region_response.json()
        if regions:
            region_id = regions[0]["id"]
            print(f"✅ 使用现有区域: {regions[0]['name']} (ID: {region_id})")
        else:
            print("⚠️  没有找到区域，请先创建区域")
            return None

    # 创建学校
    response = requests.post(
        f"{BASE_URL}/schools",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": TEST_SCHOOL["name"],
            "code": TEST_SCHOOL["code"],
            "region_id": region_id,
            "address": "测试地址",
            "phone": "010-12345678"
        }
    )

    if response.status_code == 200:
        school = response.json()
        print(f"✅ 学校创建成功 (ID: {school['id']})")
        return school["id"]
    else:
        print(f"❌ 学校创建失败: {response.status_code}")
        print(response.text)
        return None


def check_grades(token):
    """检查年级是否存在"""
    print_step("步骤3: 检查年级")

    response = requests.get(
        f"{BASE_URL}/grades",
        headers={"Authorization": f"Bearer {token}"}
    )

    existing_grades = []
    if response.status_code == 200:
        grades = response.json()
        grade_dict = {g["level"]: g["id"] for g in grades}

        for level in TEST_GRADES:
            if level in grade_dict:
                existing_grades.append(level)
                print(f"✅ 年级 {level} 已存在 (ID: {grade_dict[level]})")
            else:
                print(f"⚠️  年级 {level} 不存在")

        return existing_grades
    else:
        print(f"❌ 查询年级失败: {response.status_code}")
        return []


def create_classrooms(token, school_id):
    """创建班级"""
    print_step("步骤4: 创建班级")

    classroom_ids = []

    for classroom_data in TEST_CLASSROOMS:
        # 检查班级是否已存在
        response = requests.get(
            f"{BASE_URL}/schools/{school_id}/classrooms",
            headers={"Authorization": f"Bearer {token}"}
        )

        exists = False
        if response.status_code == 200:
            classrooms = response.json()
            for cls in classrooms:
                if cls.get("code") == classroom_data["code"]:
                    print(f"✅ 班级已存在: {classroom_data['name']} (ID: {cls['id']})")
                    classroom_ids.append(cls["id"])
                    exists = True
                    break

        if not exists:
            print(f"📝 创建班级: {classroom_data['name']}")

            # 获取年级ID
            grades_response = requests.get(
                f"{BASE_URL}/grades",
                headers={"Authorization": f"Bearer {token}"}
            )

            if grades_response.status_code == 200:
                grades = grades_response.json()
                grade_id = None
                for g in grades:
                    if g["level"] == classroom_data["grade_level"]:
                        grade_id = g["id"]
                        break

                if grade_id:
                    response = requests.post(
                        f"{BASE_URL}/schools/{school_id}/classrooms",
                        headers={"Authorization": f"Bearer {token}"},
                        json={
                            "name": classroom_data["name"],
                            "code": classroom_data["code"],
                            "grade_id": grade_id
                        }
                    )

                    if response.status_code == 200:
                        classroom = response.json()
                        print(f"✅ 班级创建成功 (ID: {classroom['id']})")
                        classroom_ids.append(classroom["id"])
                    else:
                        print(f"❌ 班级创建失败: {response.status_code}")
                        print(response.text)
                else:
                    print(f"⚠️  年级 {classroom_data['grade_level']} 不存在，无法创建班级")

    return classroom_ids


def import_students(token):
    """导入学生"""
    print_step("步骤5: 导入学生账户")

    excel_file = "/Users/382241106qq.com/inspireed-platform-main/test_students_import.xlsx"

    with open(excel_file, "rb") as f:
        files = {"file": ("test_students_import.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}

        response = requests.post(
            f"{BASE_URL}/import?strategy_type=student_account&update_existing=false",
            headers={"Authorization": f"Bearer {token}"},
            files=files
        )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ 导入完成")
        print(f"📊 总记录数: {result['total']}")
        print(f"✅ 成功: {result['success']}")
        print(f"❌ 失败: {result['failed']}")
        print(f"🆕 创建: {result['created']}")
        print(f"🔄 更新: {result['updated']}")

        if result['errors']:
            print(f"\n⚠️  错误详情:")
            for error in result['errors'][:5]:  # 只显示前5个错误
                print(f"  行 {error['row']}: {error['message']}")
            if len(result['errors']) > 5:
                print(f"  ... 还有 {len(result['errors']) - 5} 个错误")

        return result
    else:
        print(f"❌ 导入失败: {response.status_code}")
        print(response.text)
        return None


def verify_import(token):
    """验证导入结果"""
    print_step("步骤6: 验证导入结果")

    # 查询导入的学生
    response = requests.get(
        f"{BASE_URL}/users?role=student&limit=10",
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        users = response.json()
        if isinstance(users, dict) and "items" in users:
            users = users["items"]

        print(f"📊 系统中的学生总数: {len(users) if isinstance(users, list) else 'N/A'}")

        if isinstance(users, list) and len(users) > 0:
            print(f"\n最近导入的学生:")
            for user in users[-5:]:
                print(f"  - {user.get('full_name')} ({user.get('username')}) - 学籍号: {user.get('student_id_number')}")

        return users
    else:
        print(f"❌ 查询失败: {response.status_code}")
        return None


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  学生账户导入测试")
    print("="*60)

    try:
        # 1. 登录
        token = login()

        # 等待一下
        time.sleep(0.5)

        # 2. 创建学校
        school_id = create_school(token)
        if not school_id:
            print("\n⚠️  无法创建学校，测试终止")
            return

        time.sleep(0.5)

        # 3. 检查年级
        existing_grades = check_grades(token)
        missing_grades = set(TEST_GRADES) - set(existing_grades)

        if missing_grades:
            print(f"\n⚠️  以下年级不存在，请先手动创建: {missing_grades}")
            print(f"    可以通过后端管理界面或 API 创建年级")

        time.sleep(0.5)

        # 4. 创建班级
        classroom_ids = create_classrooms(token, school_id)
        print(f"\n✅ 成功准备 {len(classroom_ids)} 个班级")

        time.sleep(0.5)

        # 5. 导入学生
        import_result = import_students(token)

        time.sleep(0.5)

        # 6. 验证
        if import_result and import_result['success'] > 0:
            verify_import(token)

            print("\n" + "="*60)
            print("  ✅ 测试完成！")
            print("="*60)
            print(f"\n导入统计:")
            print(f"  总计: {import_result['total']}")
            print(f"  成功: {import_result['success']}")
            print(f"  失败: {import_result['failed']}")
            print(f"  创建: {import_result['created']}")
            print(f"  更新: {import_result['updated']}")
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
