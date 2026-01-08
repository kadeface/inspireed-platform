#!/usr/bin/env python3
"""
Neo4j 连接和功能测试脚本
用于验证 Neo4j 集成是否正常工作
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.neo4j_db import get_neo4j_driver, verify_neo4j_connection, close_neo4j
from app.services.neo4j_service import neo4j_service


async def test_connection():
    """测试 Neo4j 连接"""
    print("=" * 60)
    print("测试 1: Neo4j 连接测试")
    print("=" * 60)
    
    if not settings.NEO4J_ENABLED:
        print("⚠️  Neo4j 未启用（NEO4J_ENABLED=False）")
        print("   请在 .env 文件中设置 NEO4J_ENABLED=true 来启用")
        return False
    
    print(f"配置信息:")
    print(f"  URI: {settings.NEO4J_URI}")
    print(f"  User: {settings.NEO4J_USER}")
    print(f"  Database: {settings.NEO4J_DATABASE}")
    print(f"  Enabled: {settings.NEO4J_ENABLED}")
    print()
    
    try:
        driver = await get_neo4j_driver()
        if driver is None:
            print("❌ 无法获取 Neo4j 驱动实例")
            return False
        
        # 验证连接
        is_connected = await verify_neo4j_connection()
        if is_connected:
            print("✅ Neo4j 连接成功！")
            return True
        else:
            print("❌ Neo4j 连接验证失败")
            return False
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False


async def test_create_asset():
    """测试创建资源节点"""
    print("\n" + "=" * 60)
    print("测试 2: 创建资源节点")
    print("=" * 60)
    
    try:
        result = await neo4j_service.create_or_update_asset(
            asset_id=999999,  # 使用测试ID
            title="测试资源",
            asset_type="test",
            school_id=1,
            owner_user_id=1,
            subject_id=1,
            grade_id=1,
            knowledge_point_category="测试分类",
            knowledge_point_name="测试知识点",
        )
        
        if result:
            print("✅ 资源节点创建成功")
            return True
        else:
            print("❌ 资源节点创建失败")
            return False
    except Exception as e:
        print(f"❌ 创建节点时出错: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_query_asset():
    """测试查询资源"""
    print("\n" + "=" * 60)
    print("测试 3: 查询资源节点")
    print("=" * 60)
    
    try:
        # 查询相似资源（可能为空，但应该不会报错）
        similar = await neo4j_service.get_similar_assets(
            asset_id=999999,
            limit=5,
            min_similarity=0.5,
        )
        print(f"✅ 查询相似资源成功，返回 {len(similar)} 条结果")
        
        # 查询相关资源
        related = await neo4j_service.get_related_assets(
            asset_id=999999,
            limit=5,
        )
        print(f"✅ 查询相关资源成功，返回 {len(related)} 条结果")
        
        return True
    except Exception as e:
        print(f"❌ 查询资源时出错: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_delete_asset():
    """测试删除资源节点"""
    print("\n" + "=" * 60)
    print("测试 4: 删除资源节点")
    print("=" * 60)
    
    try:
        result = await neo4j_service.delete_asset(asset_id=999999)
        
        if result:
            print("✅ 资源节点删除成功")
            return True
        else:
            print("❌ 资源节点删除失败")
            return False
    except Exception as e:
        print(f"❌ 删除节点时出错: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_calculate_similarity():
    """测试计算相似度"""
    print("\n" + "=" * 60)
    print("测试 5: 计算资源相似度")
    print("=" * 60)
    
    try:
        # 先创建两个测试资源
        await neo4j_service.create_or_update_asset(
            asset_id=999998,
            title="测试资源1",
            asset_type="test",
            school_id=1,
            owner_user_id=1,
            subject_id=1,
            grade_id=1,
        )
        
        await neo4j_service.create_or_update_asset(
            asset_id=999997,
            title="测试资源2",
            asset_type="test",
            school_id=1,
            owner_user_id=1,
            subject_id=1,
            grade_id=1,
        )
        
        # 计算相似度
        similarity = await neo4j_service.calculate_asset_similarity(
            asset_id_1=999998,
            asset_id_2=999997,
        )
        
        print(f"✅ 相似度计算成功，相似度: {similarity:.2f}")
        
        # 清理测试数据
        await neo4j_service.delete_asset(999998)
        await neo4j_service.delete_asset(999997)
        
        return True
    except Exception as e:
        print(f"❌ 计算相似度时出错: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("Neo4j 集成功能测试")
    print("=" * 60)
    print()
    
    results = []
    
    # 测试连接
    if await test_connection():
        results.append(("连接测试", True))
        
        # 测试创建节点
        if await test_create_asset():
            results.append(("创建节点", True))
        else:
            results.append(("创建节点", False))
        
        # 测试查询
        if await test_query_asset():
            results.append(("查询节点", True))
        else:
            results.append(("查询节点", False))
        
        # 测试删除
        if await test_delete_asset():
            results.append(("删除节点", True))
        else:
            results.append(("删除节点", False))
        
        # 测试相似度计算
        if await test_calculate_similarity():
            results.append(("相似度计算", True))
        else:
            results.append(("相似度计算", False))
    else:
        results.append(("连接测试", False))
        print("\n⚠️  由于连接失败，跳过其他测试")
    
    # 关闭连接
    await close_neo4j()
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查配置和 Neo4j 服务状态")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

