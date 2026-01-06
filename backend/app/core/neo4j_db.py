"""
Neo4j 图数据库连接管理
用于资源库知识图谱功能
"""

from typing import Optional
from neo4j import AsyncGraphDatabase, AsyncDriver
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# 全局 Neo4j 驱动实例
_neo4j_driver: Optional[AsyncDriver] = None


async def get_neo4j_driver() -> Optional[AsyncDriver]:
    """
    获取 Neo4j 驱动实例（单例模式）
    如果 Neo4j 未启用或连接失败，返回 None
    """
    global _neo4j_driver

    if not settings.NEO4J_ENABLED:
        return None

    if _neo4j_driver is None:
        try:
            _neo4j_driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                database=settings.NEO4J_DATABASE,
            )
            # 验证连接
            await _neo4j_driver.verify_connectivity()
            logger.info(f"✅ Neo4j 连接成功: {settings.NEO4J_URI}")
        except Exception as e:
            logger.warning(f"⚠️ Neo4j 连接失败: {e}，Neo4j 功能将被禁用")
            _neo4j_driver = None

    return _neo4j_driver


async def close_neo4j() -> None:
    """
    关闭 Neo4j 连接
    """
    global _neo4j_driver

    if _neo4j_driver is not None:
        try:
            await _neo4j_driver.close()
            logger.info("✅ Neo4j 连接已关闭")
        except Exception as e:
            logger.error(f"❌ 关闭 Neo4j 连接时出错: {e}")
        finally:
            _neo4j_driver = None


async def verify_neo4j_connection() -> bool:
    """
    验证 Neo4j 连接是否可用
    """
    if not settings.NEO4J_ENABLED:
        return False

    driver = await get_neo4j_driver()
    if driver is None:
        return False

    try:
        await driver.verify_connectivity()
        return True
    except Exception:
        return False

