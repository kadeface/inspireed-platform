#!/usr/bin/env python3
"""
学生账户导入完整测试脚本 - 使用正确的 API 路径
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

# 测试数据
TEST_SCHOOL = {
    "name": "自动化测试学校",
    "code": "9999",  # 使用不太可能冲突的代码
}

TEST_CLASSROOMS = [
    {"grade_level": 7, "code": "701", "name": "七年级1班"},  # 使用年级中文名称
    {"grade_level": 7, "code": "702", "name": "七年级2班"},
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


def check_or_create_school(token):
    """检查或创建测试学校"""
    print_step("步骤2: 检查/创建学校")

    # 查询现有学校（增加页面大小）
    response = requests.get(
        f"{BASE_URL}/admin/organization/schools",
        params={"size": 100},  # 增加页面大小
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        try:
            data = response.json()
            # API 返回格式: {'schools': [...]}
            schools = data.get("schools", data.get("items", [])) if isinstance(data, dict) else data

            for school in schools:
                if isinstance(school, dict) and school.get("code") == TEST_SCHOOL["code"]:
                    print(f"✅ 学校已存在: {school['name']} (ID: {school.get('id')})")
                    return school.get("id")

            # 如果没找到目标学校，检查所有学校
            print(f"📊 查找学校，当前页共有 {len(schools)} 所学校...")

            # 如果分页，获取所有学校
            page = 1
            while len(schools) > 0:
                for school in schools:
                    if isinstance(school, dict) and school.get("code") == TEST_SCHOOL["code"]:
                        print(f"✅ 学校已存在: {school['name']} (ID: {school.get('id')})")
                        return school.get("id")

                # 获取下一页
                page += 1
                response = requests.get(
                    f"{BASE_URL}/admin/organization/schools",
                    params={"page": page, "size": 100},
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code != 200:
                    break
                data = response.json()
                schools = data.get("schools", data.get("items", [])) if isinstance(data, dict) else data

            # 如果还是没找到，打印现有学校列表（前10个）
            print(f"⚠️  未找到目标学校 (代码: {TEST_SCHOOL['code']})")
            print(f"📊 现有学校列表（前10个）:")
            response = requests.get(
                f"{BASE_URL}/admin/organization/schools",
                params={"page": 1, "size": 10},
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                data = response.json()
                schools = data.get("schools", data.get("items", [])) if isinstance(data, dict) else data
                for school in schools[:10]:
                    if isinstance(school, dict):
                        print(f"  - {school.get('name')} (代码: {school.get('code')})")
        except Exception as e:
            print(f"⚠️  解析响应失败: {e}")

    # 需要创建学校，但首先需要获取 region_id
    print(f"📝 需要创建学校: {TEST_SCHOOL['name']}")

    # 获取区域
    regions_response = requests.get(
        f"{BASE_URL}/admin/organization/regions",
        headers={"Authorization": f"Bearer {token}"}
    )

    if regions_response.status_code == 200:
        regions_data = regions_response.json()
        # API 返回格式: {'regions': [...]}
        regions = regions_data.get("regions", regions_data.get("items", [])) if isinstance(regions_data, dict) else regions_data

        if not regions:
            print("⚠️  系统中没有区域，请先创建区域")
            return None

        region_id = regions[0]["id"]
        print(f"✅ 使用区域: {regions[0]['name']} (ID: {region_id})")

        # 创建学校
        create_response = requests.post(
            f"{BASE_URL}/admin/organization/schools",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": TEST_SCHOOL["name"],
                "code": TEST_SCHOOL["code"],
                "region_id": region_id,
                "school_type": "小学",  # 使用字符串类型
                "address": "测试地址",
            }
        )

        if create_response.status_code == 200:
            school = create_response.json()
            print(f"✅ 学校创建成功 (ID: {school['id']})")
            return school["id"]
        else:
            print(f"❌ 学校创建失败: {create_response.status_code}")
            print(create_response.text)
            return None
    else:
        print(f"❌ 获取区域失败: {regions_response.status_code}")
        return None


def check_or_create_classrooms(token, school_id):
    """检查或创建班级"""
    print_step("步骤3: 检查/创建班级")
    print(f"学校ID: {school_id}")
    print(f"需要创建的班级数量: {len(TEST_CLASSROOMS)}")

    for idx, classroom_data in enumerate(TEST_CLASSROOMS, 1):
        print(f"\n处理班级 {idx}/{len(TEST_CLASSROOMS)}: {classroom_data['name']}")
        # 检查班级是否已存在
        response = requests.get(
            f"{BASE_URL}/admin/organization/classrooms",
            params={"school_id": school_id},
            headers={"Authorization": f"Bearer {token}"}
        )

        exists = False
        if response.status_code == 200:
            try:
                data = response.json()
                # API 返回格式可能是 {'classrooms': [...]} 或 {'items': [...]}
                classrooms = data.get("classrooms", data.get("items", [])) if isinstance(data, dict) else data

                for cls in classrooms:
                    if isinstance(cls, dict) and cls.get("code") == classroom_data["code"]:
                        print(f"✅ 班级已存在: {classroom_data['name']} (ID: {cls.get('id')})")
                        exists = True
                        break
            except Exception as e:
                print(f"⚠️  解析班级列表失败: {e}")

        if not exists:
            print(f"📝 需要创建班级: {classroom_data['name']} (年级: {classroom_data['grade_level']})")

            # 获取年级ID
            grades_response = requests.get(
                f"{BASE_URL}/curriculum/grades",
                headers={"Authorization": f"Bearer {token}"}
            )

            print(f"  查询年级API: {grades_response.status_code}")

            if grades_response.status_code == 200:
                grades = grades_response.json()
                print(f"  系统中共有 {len(grades)} 个年级")

                grade_id = None
                for g in grades:
                    if g["level"] == classroom_data["grade_level"]:
                        grade_id = g["id"]
                        print(f"  找到年级: {g['name']} (ID: {grade_id})")
                        break

                if grade_id:
                    print(f"  准备创建班级...")

                    create_response = requests.post(
                        f"{BASE_URL}/admin/organization/classrooms",
                        headers={"Authorization": f"Bearer {token}"},
                        json={
                            "name": classroom_data["name"],
                            "code": classroom_data["code"],
                            "grade_id": grade_id,
                            "school_id": school_id
                        }
                    )

                    print(f"  创建班级API响应: {create_response.status_code}")

                    if create_response.status_code == 200:
                        classroom = create_response.json()
                        print(f"✅ 班级创建成功 (ID: {classroom['id']})")
                    else:
                        print(f"❌ 班级创建失败: {create_response.status_code}")
                        print(f"响应: {create_response.text[:200]}")
                else:
                    print(f"⚠️  年级 {classroom_data['grade_level']} 不存在，无法创建班级")
                    print(f"提示: 请先在系统中创建该年级")
            else:
                print(f"❌ 查询年级失败: {grades_response.status_code}")


def import_students(token):
    """导入学生"""
    print_step("步骤4: 导入学生账户")

    excel_file = "/Users/382241106qq.com/inspireed-platform-main/test_students_import.xlsx"

    print(f"📂 Excel 文件: {excel_file}")
    print(f"📊 文件大小: {len(open(excel_file, 'rb').read())} 字节")

    with open(excel_file, "rb") as f:
        files = {
            "file": (
                "test_students_import.xlsx",
                f,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        }

        response = requests.post(
            f"{BASE_URL}/import?strategy_type=student_account&update_existing=false",
            headers={"Authorization": f"Bearer {token}"},
            files=files,
            timeout=60  # 增加超时时间
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
            for error in result['errors'][:10]:  # 显示前10个错误
                print(f"  行 {error['row']}: {error.get('message', 'Unknown error')}")
            if len(result['errors']) > 10:
                print(f"  ... 还有 {len(result['errors']) - 10} 个错误")

        return result
    else:
        print(f"❌ 导入失败")
        print(f"响应: {response.text[:500]}")
        return None


def verify_results(token):
    """验证导入结果"""
    print_step("步骤5: 验证导入结果")

    # 查询最近的学生
    response = requests.get(
        f"{BASE_URL}/admin/users",
        params={"role": "student", "limit": 10},
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        data = response.json()
        users = data.get("items", data) if isinstance(data, dict) else data

        print(f"📊 查询结果: {len(users) if isinstance(users, list) else 'N/A'} 条学生记录")

        if isinstance(users, list) and len(users) > 0:
            print(f"\n最近导入的学生:")
            for user in users[-5:]:
                print(f"  - {user.get('full_name')} ({user.get('username')})")
                print(f"    学籍号: {user.get('student_id_number')}")
                print(f"    学校: {user.get('school_name', 'N/A')}")
        return users
    else:
        print(f"❌ 查询失败: {response.status_code}")
        print(response.text)
        return None


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  学生账户导入完整测试")
    print("="*60)

    try:
        # 1. 登录
        token = login()
        time.sleep(1)

        # 2. 检查/创建学校
        school_id = check_or_create_school(token)
        if not school_id:
            print("\n⚠️  无法准备学校，测试终止")
            print("\n提示：请确保系统中至少有一个区域（Region）")
            return

        time.sleep(1)

        # 3. 检查/创建班级
        check_or_create_classrooms(token, school_id)
        time.sleep(1)

        # 4. 导入学生
        import_result = import_students(token)
        time.sleep(1)

        # 5. 验证结果
        if import_result and import_result.get('success', 0) > 0:
            verify_results(token)

            print("\n" + "="*60)
            print("  ✅ 测试完成！")
            print("="*60)
            print(f"\n最终统计:")
            print(f"  总计: {import_result.get('total', 'N/A')}")
            print(f"  成功: {import_result.get('success', 'N/A')}")
            print(f"  失败: {import_result.get('failed', 'N/A')}")
            print(f"  创建: {import_result.get('created', 'N/A')}")
        else:
            print("\n" + "="*60)
            print("  ⚠️  测试完成，但有错误")
            print("="*60)
            print("\n可能的问题:")
            print("  1. Excel 文件格式不正确")
            print("  2. 学校/年级/班级不存在")
            print("  3. 学籍号重复")

    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
