#!/usr/bin/env python3
"""
课程导出导入功能测试脚本
"""
import requests
import json
import os
from typing import Dict, Any

class CourseExportImportTester:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = None
        
    def login(self) -> bool:
        """登录获取访问令牌"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                data={
                    "username": self.username,
                    "password": self.password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                print("✅ 登录成功")
                return True
            else:
                print(f"❌ 登录失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 登录异常: {str(e)}")
            return False
    
    def test_download_template(self) -> bool:
        """测试下载导出模板"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/course-export/export-template")
            
            if response.status_code == 200:
                # 保存模板文件
                with open("course_export_template.json", "wb") as f:
                    f.write(response.content)
                print("✅ 模板下载成功")
                return True
            else:
                print(f"❌ 模板下载失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 模板下载异常: {str(e)}")
            return False
    
    def test_export_all_courses(self) -> bool:
        """测试导出所有课程"""
        try:
            params = {
                "include_lessons": "true",
                "include_resources": "true"
            }
            
            response = self.session.get(
                f"{self.base_url}/api/v1/course-export/export-all",
                params=params
            )
            
            if response.status_code == 200:
                # 保存导出文件
                with open("all_courses_export.json", "wb") as f:
                    f.write(response.content)
                print("✅ 全课程导出成功")
                return True
            else:
                print(f"❌ 全课程导出失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 全课程导出异常: {str(e)}")
            return False
    
    def test_export_single_course(self, course_id: int) -> bool:
        """测试导出单个课程"""
        try:
            params = {
                "include_lessons": "true",
                "include_resources": "true"
            }
            
            response = self.session.get(
                f"{self.base_url}/api/v1/course-export/courses/{course_id}/export",
                params=params
            )
            
            if response.status_code == 200:
                # 保存导出文件
                with open(f"course_{course_id}_export.json", "wb") as f:
                    f.write(response.content)
                print(f"✅ 课程 {course_id} 导出成功")
                return True
            else:
                print(f"❌ 课程 {course_id} 导出失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 课程 {course_id} 导出异常: {str(e)}")
            return False
    
    def test_import_courses(self, file_path: str) -> bool:
        """测试导入课程"""
        try:
            if not os.path.exists(file_path):
                print(f"❌ 导入文件不存在: {file_path}")
                return False
            
            with open(file_path, "rb") as f:
                files = {"file": f}
                data = {"overwrite_existing": "false"}
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/course-export/import",
                    files=files,
                    data=data
                )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 课程导入成功")
                print(f"   创建: {result['summary']['total_created']}")
                print(f"   跳过: {result['summary']['total_skipped']}")
                print(f"   错误: {result['summary']['total_errors']}")
                
                if result['result']['errors']:
                    print("   错误详情:")
                    for error in result['result']['errors']:
                        print(f"     - {error}")
                
                return True
            else:
                print(f"❌ 课程导入失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 课程导入异常: {str(e)}")
            return False
    
    def get_courses(self) -> list:
        """获取课程列表"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/curriculum/courses")
            
            if response.status_code == 200:
                courses = response.json()
                print(f"✅ 获取到 {len(courses)} 个课程")
                return courses
            else:
                print(f"❌ 获取课程列表失败: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ 获取课程列表异常: {str(e)}")
            return []
    
    def validate_export_file(self, file_path: str) -> bool:
        """验证导出文件格式"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 检查必需字段
            required_fields = ["version", "export_time", "data"]
            for field in required_fields:
                if field not in data:
                    print(f"❌ 导出文件缺少必需字段: {field}")
                    return False
            
            # 检查数据结构
            if not isinstance(data["data"], dict):
                print("❌ 导出文件data字段格式错误")
                return False
            
            data_section = data["data"]
            expected_sections = ["subjects", "grades", "courses", "chapters", "lessons", "resources"]
            
            for section in expected_sections:
                if section not in data_section:
                    print(f"❌ 导出文件缺少数据段: {section}")
                    return False
                
                if not isinstance(data_section[section], list):
                    print(f"❌ 导出文件{section}段格式错误")
                    return False
            
            print("✅ 导出文件格式验证通过")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ 导出文件JSON格式错误: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ 导出文件验证异常: {str(e)}")
            return False
    
    def run_full_test(self):
        """运行完整测试"""
        print("🚀 开始课程导出导入功能测试")
        print("=" * 50)
        
        # 1. 登录
        if not self.login():
            return False
        
        # 2. 获取课程列表
        courses = self.get_courses()
        if not courses:
            print("⚠️  没有课程数据，跳过单课程导出测试")
        
        # 3. 测试下载模板
        print("\n📋 测试下载导出模板...")
        self.test_download_template()
        
        # 4. 测试导出所有课程
        print("\n📤 测试导出所有课程...")
        self.test_export_all_courses()
        
        # 5. 测试导出单个课程
        if courses:
            print(f"\n📤 测试导出单个课程 (ID: {courses[0]['id']})...")
            self.test_export_single_course(courses[0]['id'])
        
        # 6. 验证导出文件
        print("\n🔍 验证导出文件格式...")
        if os.path.exists("all_courses_export.json"):
            self.validate_export_file("all_courses_export.json")
        
        # 7. 测试导入（使用模板文件）
        print("\n📥 测试导入课程数据...")
        if os.path.exists("course_export_template.json"):
            self.test_import_courses("course_export_template.json")
        
        print("\n" + "=" * 50)
        print("✅ 测试完成")
        
        # 清理测试文件
        test_files = [
            "course_export_template.json",
            "all_courses_export.json"
        ]
        
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
                print(f"🗑️  清理测试文件: {file}")

def main():
    """主函数"""
    # 配置参数
    BASE_URL = "http://localhost:8000"  # 修改为实际的服务器地址
    USERNAME = "admin"  # 修改为实际的管理员用户名
    PASSWORD = "admin123"  # 修改为实际的管理员密码
    
    print("课程导出导入功能测试")
    print(f"服务器地址: {BASE_URL}")
    print(f"用户名: {USERNAME}")
    print()
    
    # 创建测试器并运行测试
    tester = CourseExportImportTester(BASE_URL, USERNAME, PASSWORD)
    tester.run_full_test()

if __name__ == "__main__":
    main()
