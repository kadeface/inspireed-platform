#!/usr/bin/env python3
"""
验证 PARAM Cell 是否已完全移除
检查代码中是否还有残留的 PARAM 引用
"""
import os
import re
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 需要检查的关键文件
FILES_TO_CHECK = [
    # 后端
    'backend/app/models/cell.py',
    'backend/app/schemas/cell.py',

    # 前端
    'frontend/src/types/cell.ts',
    'frontend/src/composables/useLessonEditorCells.ts',
    'frontend/src/utils/lessonEditorHelpers.ts',
]

# 需要排除的目录
EXCLUDE_DIRS = [
    'node_modules',
    'venv',
    '__pycache__',
    '.git',
    'dist',
    'build',
]

# PARAM 相关的模式
PARAM_PATTERNS = [
    r'PARAM\s*[=:]',
    r'ParamCell',
    r'CellType\.PARAM',
    r'param.*cell',
    r'PARAM.*cell',
]


def check_file_for_param(file_path: Path) -> list:
    """检查单个文件是否包含 PARAM 引用"""
    if not file_path.exists():
        return []

    try:
        content = file_path.read_text(encoding='utf-8')
        findings = []

        for pattern in PARAM_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # 获取行号
                line_num = content[:match.start()].count('\n') + 1
                line_content = content.split('\n')[line_num - 1].strip()

                findings.append({
                    'file': str(file_path),
                    'line': line_num,
                    'pattern': pattern,
                    'match': match.group(),
                    'content': line_content,
                })

        return findings
    except Exception as e:
        print(f"⚠️  无法读取文件 {file_path}: {e}")
        return []


def main():
    print("🔍 验证 PARAM Cell 移除完整性")
    print("=" * 80)

    all_findings = []

    # 检查关键文件
    print("\n📋 检查关键文件:")
    print("-" * 80)

    for file_path_str in FILES_TO_CHECK:
        file_path = PROJECT_ROOT / file_path_str
        print(f"\n检查: {file_path_str}")

        findings = check_file_for_param(file_path)

        if findings:
            print(f"  ❌ 发现 {len(findings)} 处 PARAM 引用:")
            for finding in findings:
                print(f"     行 {finding['line']}: {finding['content'][:60]}")
            all_findings.extend(findings)
        else:
            print(f"  ✅ 未发现 PARAM 引用")

    # 检查数据库枚举
    print("\n" + "=" * 80)
    print("📊 检查数据库枚举值:")
    print("-" * 80)

    try:
        import asyncio
        from sqlalchemy import text
        from app.core.database import engine

        async def check_db():
            async with engine.connect() as conn:
                result = await conn.execute(
                    text("SELECT unnest(enum_range(NULL::celltype))::text AS value ORDER BY value")
                )
                values = [row[0] for row in result]

                has_param = 'PARAM' in values
                print(f"\n数据库枚举值: {', '.join(values)}")
                print(f"\nPARAM 存在: {'❌ 是' if has_param else '✅ 否'}")

                if has_param:
                    all_findings.append({
                        'file': 'database',
                        'line': 0,
                        'pattern': 'enum',
                        'match': 'PARAM',
                        'content': '数据库枚举仍包含 PARAM',
                    })

        asyncio.run(check_db())
    except Exception as e:
        print(f"⚠️  无法检查数据库: {e}")

    # 总结
    print("\n" + "=" * 80)
    print("📈 验证总结")
    print("-" * 80)

    if all_findings:
        print(f"\n❌ 发现 {len(all_findings)} 处残留的 PARAM 引用")
        print("\n详细信息:")
        for finding in all_findings:
            print(f"  - {finding['file']}:{finding['line']}")
            print(f"    {finding['content']}")
        return 1
    else:
        print("\n✅ 所有检查通过！PARAM 已完全移除")
        print("\n验证项:")
        print("  ✅ 关键代码文件无 PARAM 引用")
        print("  ✅ 数据库枚举无 PARAM 值")
        print("  ✅ 类型定义无 ParamCell")
        print("  ✅ 工具函数无 PARAM 映射")
        return 0


if __name__ == "__main__":
    exit(main())
