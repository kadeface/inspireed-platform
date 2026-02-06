#!/usr/bin/env python
"""检查 PARAM Cell 的使用情况"""
import asyncio
from sqlalchemy import text
from app.core.database import engine
from app.core.config import settings


async def check_param_cells():
    """检查 PARAM cell 的使用情况"""
    print(f"🔍 连接数据库: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
    print("=" * 80)

    async with engine.connect() as conn:
        # 1. 检查枚举值中是否包含 PARAM
        print("\n📋 步骤1：检查 CellType 枚举值")
        print("-" * 80)
        result = await conn.execute(
            text("SELECT unnest(enum_range(NULL::celltype))::text AS value ORDER BY value")
        )
        enum_values = [row[0] for row in result]

        has_param_enum = 'PARAM' in enum_values
        print(f"PARAM 枚举值: {'✅ 存在' if has_param_enum else '❌ 不存在'}")

        if has_param_enum:
            print(f"  当前所有枚举值: {', '.join(enum_values)}")

        # 2. 统计各类型 cell 数量
        print("\n📊 步骤2：统计各类型 Cell 数量")
        print("-" * 80)
        result = await conn.execute(
            text("""
                SELECT
                    cell_type,
                    COUNT(*) as count
                FROM cells
                GROUP BY cell_type
                ORDER BY count DESC
            """)
        )

        total_cells = 0
        param_count = 0
        cell_stats = []

        for row in result:
            cell_type, count = row
            total_cells += count
            cell_stats.append((cell_type, count))
            if cell_type == 'PARAM':
                param_count = count

        print(f"Cell 总数: {total_cells}")
        print("\n类型分布:")
        for cell_type, count in cell_stats:
            percentage = (count / total_cells * 100) if total_cells > 0 else 0
            marker = '⚠️  ' if cell_type == 'PARAM' else '   '
            print(f"{marker}{cell_type:15} {count:6} 个 ({percentage:5.2f}%)")

        # 3. 检查 PARAM cell 的详细信息
        if param_count > 0:
            print(f"\n⚠️  发现 {param_count} 个 PARAM Cell！")
            print("=" * 80)
            print("\n📋 步骤3：PARAM Cell 详细信息")
            print("-" * 80)

            result = await conn.execute(
                text("""
                    SELECT
                        c.id,
                        c.lesson_id,
                        c.cell_type,
                        c.title,
                        c.order,
                        l.title as lesson_title,
                        l.subject_id,
                        l.grade_id
                    FROM cells c
                    LEFT JOIN lessons l ON c.lesson_id = l.id
                    WHERE c.cell_type = 'PARAM'
                    ORDER BY c.lesson_id, c.order
                """)
            )

            param_cells = result.fetchall()

            print(f"\n找到 {len(param_cells)} 个 PARAM cell:\n")

            current_lesson_id = None
            for idx, cell in enumerate(param_cells, 1):
                (cell_id, lesson_id, cell_type, title, order,
                 lesson_title, subject_id, grade_id) = cell

                if lesson_id != current_lesson_id:
                    if current_lesson_id is not None:
                        print()
                    print(f"📚 教案 ID: {lesson_id} | 标题: {lesson_title or '(无标题)'}")
                    print(f"   学科ID: {subject_id} | 年级ID: {grade_id}")
                    current_lesson_id = lesson_id

                print(f"   └─ Cell #{idx:3} | ID: {cell_id:5} | 顺序: {order:3} | 标题: {title or '(无标题)'}")

            # 4. 分析影响范围
            print("\n" + "=" * 80)
            print("📈 影响分析")
            print("-" * 80)
            affected_lessons = len(set(cell[1] for cell in param_cells))
            print(f"涉及教案数量: {affected_lessons}")
            print(f"涉及 Cell 数量: {param_count}")
            print(f"占总 Cell 比例: {(param_count / total_cells * 100):.2f}%")

            # 5. 提供迁移建议
            print("\n" + "=" * 80)
            print("💡 迁移建议")
            print("-" * 80)
            print("\n选项 A: 删除所有 PARAM cell（推荐）")
            print(f"  - 影响: {param_count} 个 cell 将被删除")
            print("  - 优点: 彻底清理未使用的类型")
            print("  - 风险: 如果有教案依赖这些 cell，需要先修复")
            print("\n选项 B: 将 PARAM cell 转换为 TEXT cell")
            print(f"  - 影响: {param_count} 个 cell 将被转换")
            print("  - 优点: 保留数据，仅改变类型")
            print("  - 风险: 转换后的内容可能需要手动调整")

            print("\n" + "=" * 80)
            print("⚠️  注意：执行迁移前请备份数据库！")
            print("=" * 80)

        else:
            print(f"\n✅ 未发现 PARAM Cell！")
            print("=" * 80)
            print("\n结论: 可以安全移除 PARAM 类型")
            print("\n建议操作:")
            print("  1. 从后端 CellType 枚举中移除 PARAM")
            print("  2. 从前端类型定义中移除 ParamCell")
            print("  3. 清理相关创建函数和工具函数")

        print("\n" + "=" * 80)

        return {
            'has_param_enum': has_param_enum,
            'param_count': param_count,
            'total_cells': total_cells,
            'affected_lessons': len(set(cell[1] for cell in param_cells)) if param_count > 0 else 0
        }


if __name__ == "__main__":
    result = asyncio.run(check_param_cells())
