#!/usr/bin/env python3
"""
数据库迁移验证脚本

用于检查迁移文件的逻辑一致性、依赖关系和潜在问题。
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple


class MigrationValidator:
    """迁移文件验证器"""

    def __init__(self, versions_dir: str):
        self.versions_dir = Path(versions_dir)
        self.migrations: Dict[str, dict] = {}
        self.issues: List[str] = []

    def load_migrations(self):
        """加载所有迁移文件"""
        for py_file in self.versions_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue

            migration = self._parse_migration_file(py_file)
            if migration:
                self.migrations[migration['revision']] = migration

    def _parse_migration_file(self, file_path: Path) -> dict:
        """解析单个迁移文件"""
        content = file_path.read_text()

        # 提取 revision 和 down_revision
        revision_match = re.search(r'revision\s*[:=]\s*["\']([^"\']+)["\']', content)
        down_revision_match = re.search(r'down_revision\s*[:=]\s*["\']?([^"\']+)["\']?', content)

        if not revision_match:
            return None

        return {
            'file': file_path.name,
            'path': str(file_path),
            'revision': revision_match.group(1),
            'down_revision': down_revision_match.group(1) if down_revision_match else None,
            'content': content,
        }

    def validate_dependencies(self):
        """验证迁移依赖链"""
        print("\n🔍 验证迁移依赖链...")

        revisions = set(self.migrations.keys())
        visited = set()
        has_cycle = False

        def check_cycle(revision: str, path: Set[str]) -> bool:
            if revision in path:
                self.issues.append(f"❌ 检测到循环依赖: {' -> '.join(path | {revision})}")
                return True

            if revision in visited or revision not in self.migrations:
                return False

            visited.add(revision)
            down_revision = self.migrations[revision]['down_revision']

            if down_revision:
                if down_revision not in revisions:
                    self.issues.append(
                        f"⚠️  迁移 {self.migrations[revision]['file']} "
                        f"依赖不存在的版本: {down_revision}"
                    )
                return check_cycle(down_revision, path | {revision})

            return False

        for revision in revisions:
            if check_cycle(revision, set()):
                has_cycle = True

        if not has_cycle and not self.issues:
            print("✅ 依赖链完整，无循环依赖")

    def validate_duplicates(self):
        """检查重复的表创建或字段添加"""
        print("\n🔍 检查重复操作...")

        # 收集所有创建表的操作
        create_table_pattern = r'op\.create_table\(\s*["\']([^"\']+)["\']'
        add_column_pattern = r'op\.add_column\(\s*["\']([^"\']+)["\']\s*,\s*sa\.Column\(\s*["\']([^"\']+)["\']'

        table_creates: Dict[str, List[str]] = {}
        column_additions: Dict[Tuple[str, str], List[str]] = {}

        for revision, migration in self.migrations.items():
            # 检查表创建
            for match in re.finditer(create_table_pattern, migration['content']):
                table_name = match.group(1)
                if table_name not in table_creates:
                    table_creates[table_name] = []
                table_creates[table_name].append(migration['file'])

            # 检查字段添加
            for match in re.finditer(add_column_pattern, migration['content']):
                table_name = match.group(1)
                column_name = match.group(2)
                key = (table_name, column_name)
                if key not in column_additions:
                    column_additions[key] = []
                column_additions[key].append(migration['file'])

        # 报告重复的表创建
        for table, files in table_creates.items():
            if len(files) > 1:
                self.issues.append(f"⚠️  表 '{table}' 被创建多次:")
                for file in files:
                    self.issues.append(f"    - {file}")

        # 报告重复的字段添加
        for (table, column), files in column_additions.items():
            if len(files) > 1:
                self.issues.append(f"⚠️  字段 '{table}.{column}' 被添加多次:")
                for file in files:
                    self.issues.append(f"    - {file}")

        if not any('表' in issue or '字段' in issue for issue in self.issues):
            print("✅ 未发现重复操作")

    def validate_enums(self):
        """检查 ENUM 类型的重复修改"""
        print("\n🔍 检查 ENUM 修改...")

        enum_pattern = r'(?:CREATE TYPE|ALTER TYPE.*ADD VALUE)\s+["\']?(\w+)["\']?'
        enum_modifications: Dict[str, List[str]] = {}

        for revision, migration in self.migrations.items():
            for match in re.finditer(enum_pattern, migration['content'], re.IGNORECASE):
                enum_name = match.group(1)
                if enum_name not in enum_modifications:
                    enum_modifications[enum_name] = []
                enum_modifications[enum_name].append(migration['file'])

        for enum_name, files in enum_modifications.items():
            if len(files) > 1:
                self.issues.append(f"⚠️  枚举类型 '{enum_name}' 被修改 {len(files)} 次:")
                for file in files:
                    self.issues.append(f"    - {file}")

        if not any('枚举' in issue for issue in self.issues):
            print("✅ ENUM 修改正常")

    def validate_foreign_keys(self):
        """检查外键约束的一致性"""
        print("\n🔍 检查外键约束...")

        fk_pattern = r'op\.create_foreign_key\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']'
        foreign_keys: Dict[Tuple[str, str], List[str]] = {}

        for revision, migration in self.migrations.items():
            for match in re.finditer(fk_pattern, migration['content']):
                fk_name = match.group(1)
                table = match.group(2)
                ref_table = match.group(3)
                key = (table, ref_table)

                if key not in foreign_keys:
                    foreign_keys[key] = []
                foreign_keys[key].append((fk_name, migration['file']))

        # 检查重复的外键
        for (table, ref_table), fks in foreign_keys.items():
            if len(fks) > 1:
                self.issues.append(f"⚠️  重复的外键 {table} -> {ref_table}:")
                for fk_name, file in fks:
                    self.issues.append(f"    - {fk_name} in {file}")

        if not any('外键' in issue for issue in self.issues):
            print("✅ 外键约束正常")

    def check_migration_complexity(self):
        """检查迁移复杂度"""
        print("\n🔍 检查迁移复杂度...")

        for revision, migration in self.migrations.items():
            lines = len(migration['content'].split('\n'))

            # 检查是否超过300行
            if lines > 300:
                self.issues.append(
                    f"⚠️  迁移 {migration['file']} 过长 ({lines} 行)，建议拆分"
                )

            # 检查是否包含多个创建表操作
            create_table_count = len(re.findall(r'op\.create_table', migration['content']))
            if create_table_count > 5:
                self.issues.append(
                    f"⚠️  迁移 {migration['file']} 创建了 {create_table_count} 个表，"
                    f"建议拆分为多个迁移"
                )

        if not any('过长' in issue or '创建了' in issue for issue in self.issues):
            print("✅ 迁移复杂度合理")

    def generate_report(self):
        """生成验证报告"""
        print("\n" + "="*60)
        print("📊 迁移验证报告")
        print("="*60)

        print(f"\n📁 扫描目录: {self.versions_dir}")
        print(f"📝 发现迁移文件: {len(self.migrations)} 个")

        if self.issues:
            print(f"\n⚠️  发现 {len(self.issues)} 个问题:")
            print("\n".join(self.issues))
        else:
            print("\n✅ 未发现问题！所有迁移文件看起来都很健康。")

        print("\n" + "="*60)

        # 返回是否通过验证
        return len(self.issues) == 0

    def run(self):
        """运行所有验证"""
        print("🚀 开始验证迁移文件...")

        self.load_migrations()
        self.validate_dependencies()
        self.validate_duplicates()
        self.validate_enums()
        self.validate_foreign_keys()
        self.check_migration_complexity()

        return self.generate_report()


def main():
    """主函数"""
    import sys

    # 默认验证当前的迁移文件
    versions_dir = Path(__file__).parent.parent / "alembic" / "versions"

    if len(sys.argv) > 1:
        versions_dir = Path(sys.argv[1])

    if not versions_dir.exists():
        print(f"❌ 目录不存在: {versions_dir}")
        sys.exit(1)

    validator = MigrationValidator(str(versions_dir))
    success = validator.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
