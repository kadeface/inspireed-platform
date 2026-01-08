"""
Neo4j 图数据库服务层
用于资源库知识图谱功能：推荐、相似资源查询、关系分析等
"""

from typing import List, Optional, Dict, Any
from neo4j import AsyncTransaction, Record
from app.core.neo4j_db import get_neo4j_driver
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class Neo4jService:
    """Neo4j 图数据库服务"""

    @staticmethod
    async def _execute_query(
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Record]:
        """执行 Cypher 查询"""
        if not settings.NEO4J_ENABLED:
            return []

        driver = await get_neo4j_driver()
        if driver is None:
            return []

        try:
            async with driver.session(database=settings.NEO4J_DATABASE) as session:
                # type: ignore - Neo4j driver accepts string queries
                result = await session.run(query, parameters or {})  # type: ignore[arg-type]
                records = []
                async for record in result:
                    records.append(record.values())
                return records
        except Exception as e:
            logger.error(f"Neo4j 查询执行失败: {e}")
            return []

    @staticmethod
    async def _execute_write_query(
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """执行 Cypher 写入查询"""
        if not settings.NEO4J_ENABLED:
            return False

        driver = await get_neo4j_driver()
        if driver is None:
            return False

        try:
            async with driver.session(database=settings.NEO4J_DATABASE) as session:
                # type: ignore - Neo4j driver accepts string queries
                await session.run(query, parameters or {})  # type: ignore[arg-type]
                return True
        except Exception as e:
            logger.error(f"Neo4j 写入查询执行失败: {e}")
            return False

    # ========== 节点创建和更新 ==========

    @staticmethod
    async def create_or_update_asset(
        asset_id: int,
        title: str,
        asset_type: str,
        school_id: int,
        owner_user_id: int,
        subject_id: Optional[int] = None,
        grade_id: Optional[int] = None,
        knowledge_point_category: Optional[str] = None,
        knowledge_point_name: Optional[str] = None,
    ) -> bool:
        """创建或更新资源资产节点"""
        query = """
        MERGE (a:Asset {id: $asset_id})
        SET a.title = $title,
            a.asset_type = $asset_type,
            a.school_id = $school_id,
            a.updated_at = datetime()
        
        WITH a
        
        // 关联学校
        MERGE (s:School {id: $school_id})
        MERGE (a)-[:BELONGS_TO_SCHOOL]->(s)
        
        // 关联用户
        MERGE (u:User {id: $owner_user_id})
        MERGE (a)-[:CREATED_BY]->(u)
        
        // 关联学科（如果提供）
        FOREACH (_ IN CASE WHEN $subject_id IS NOT NULL THEN [1] ELSE [] END |
            MERGE (sub:Subject {id: $subject_id})
            MERGE (a)-[:BELONGS_TO_SUBJECT]->(sub)
        )
        
        // 关联年级（如果提供）
        FOREACH (_ IN CASE WHEN $grade_id IS NOT NULL THEN [1] ELSE [] END |
            MERGE (g:Grade {id: $grade_id})
            MERGE (a)-[:BELONGS_TO_GRADE]->(g)
        )
        
        // 关联知识点（如果提供）
        FOREACH (_ IN CASE WHEN $knowledge_point_category IS NOT NULL AND $knowledge_point_name IS NOT NULL THEN [1] ELSE [] END |
            MERGE (kp:KnowledgePoint {
                category: $knowledge_point_category,
                name: $knowledge_point_name
            })
            MERGE (a)-[:HAS_KNOWLEDGE_POINT]->(kp)
        )
        """

        return await Neo4jService._execute_write_query(
            query,
            {
                "asset_id": asset_id,
                "title": title,
                "asset_type": asset_type,
                "school_id": school_id,
                "owner_user_id": owner_user_id,
                "subject_id": subject_id,
                "grade_id": grade_id,
                "knowledge_point_category": knowledge_point_category,
                "knowledge_point_name": knowledge_point_name,
            },
        )

    @staticmethod
    async def delete_asset(asset_id: int) -> bool:
        """删除资源资产节点及其所有关系"""
        query = """
        MATCH (a:Asset {id: $asset_id})
        DETACH DELETE a
        """
        return await Neo4jService._execute_write_query(query, {"asset_id": asset_id})

    # ========== 关系创建 ==========

    @staticmethod
    async def create_similarity_relationship(
        asset_id_1: int,
        asset_id_2: int,
        similarity_score: float,
    ) -> bool:
        """创建资源相似关系"""
        query = """
        MATCH (a1:Asset {id: $asset_id_1}), (a2:Asset {id: $asset_id_2})
        WHERE a1.id < a2.id  // 避免重复关系
        MERGE (a1)-[r:SIMILAR_TO]->(a2)
        SET r.score = $similarity_score,
            r.updated_at = datetime()
        """
        return await Neo4jService._execute_write_query(
            query,
            {
                "asset_id_1": asset_id_1,
                "asset_id_2": asset_id_2,
                "similarity_score": similarity_score,
            },
        )

    @staticmethod
    async def create_used_together_relationship(
        asset_id_1: int,
        asset_id_2: int,
        count: int = 1,
    ) -> bool:
        """创建资源一起使用关系（基于使用统计）"""
        query = """
        MATCH (a1:Asset {id: $asset_id_1}), (a2:Asset {id: $asset_id_2})
        WHERE a1.id < a2.id  // 避免重复关系
        MERGE (a1)-[r:USED_WITH]->(a2)
        SET r.count = COALESCE(r.count, 0) + $count,
            r.updated_at = datetime()
        """
        return await Neo4jService._execute_write_query(
            query,
            {
                "asset_id_1": asset_id_1,
                "asset_id_2": asset_id_2,
                "count": count,
            },
        )

    # ========== 查询功能 ==========

    @staticmethod
    async def get_similar_assets(
        asset_id: int,
        limit: int = 10,
        min_similarity: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """获取相似资源"""
        query = """
        MATCH (a:Asset {id: $asset_id})-[r:SIMILAR_TO]-(similar:Asset)
        WHERE r.score >= $min_similarity
        RETURN similar.id AS id,
               similar.title AS title,
               similar.asset_type AS asset_type,
               r.score AS similarity_score
        ORDER BY r.score DESC
        LIMIT $limit
        """
        records = await Neo4jService._execute_query(
            query,
            {
                "asset_id": asset_id,
                "limit": limit,
                "min_similarity": min_similarity,
            },
        )

        results = []
        for record in records:
            if len(record) >= 4:
                results.append(
                    {
                        "id": record[0],
                        "title": record[1],
                        "asset_type": record[2],
                        "similarity_score": record[3],
                    }
                )
        return results

    @staticmethod
    async def get_related_assets(
        asset_id: int,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """获取相关资源（基于知识图谱路径）"""
        query = """
        MATCH (a:Asset {id: $asset_id})
        MATCH path = (a)-[*1..2]-(related:Asset)
        WHERE related.id <> $asset_id
        WITH related, count(DISTINCT path) AS path_count
        RETURN related.id AS id,
               related.title AS title,
               related.asset_type AS asset_type,
               path_count AS relevance_score
        ORDER BY path_count DESC, related.title
        LIMIT $limit
        """
        records = await Neo4jService._execute_query(
            query,
            {
                "asset_id": asset_id,
                "limit": limit,
            },
        )

        results = []
        for record in records:
            if len(record) >= 4:
                results.append(
                    {
                        "id": record[0],
                        "title": record[1],
                        "asset_type": record[2],
                        "relevance_score": record[3],
                    }
                )
        return results

    @staticmethod
    async def get_recommended_assets(
        user_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        grade_id: Optional[int] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """获取推荐资源"""
        # 构建查询条件
        conditions = []
        params = {"limit": limit}

        if user_id:
            conditions.append("(u:User {id: $user_id})-[:CREATED_BY]-(a:Asset)")
            params["user_id"] = user_id
        else:
            conditions.append("(a:Asset)")

        if subject_id:
            conditions.append("(a)-[:BELONGS_TO_SUBJECT]->(:Subject {id: $subject_id})")
            params["subject_id"] = subject_id

        if grade_id:
            conditions.append("(a)-[:BELONGS_TO_GRADE]->(:Grade {id: $grade_id})")
            params["grade_id"] = grade_id

        match_clause = "MATCH " + ", ".join(conditions)

        query = f"""
        {match_clause}
        WITH a, count(DISTINCT a) AS score
        RETURN a.id AS id,
               a.title AS title,
               a.asset_type AS asset_type,
               score AS recommendation_score
        ORDER BY score DESC, a.title
        LIMIT $limit
        """
        records = await Neo4jService._execute_query(query, params)

        results = []
        for record in records:
            if len(record) >= 4:
                results.append(
                    {
                        "id": record[0],
                        "title": record[1],
                        "asset_type": record[2],
                        "recommendation_score": record[3],
                    }
                )
        return results

    @staticmethod
    async def get_assets_by_knowledge_point(
        knowledge_point_category: str,
        knowledge_point_name: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """根据知识点获取资源"""
        query = """
        MATCH (kp:KnowledgePoint {category: $category, name: $name})<-[:HAS_KNOWLEDGE_POINT]-(a:Asset)
        RETURN a.id AS id,
               a.title AS title,
               a.asset_type AS asset_type
        ORDER BY a.title
        LIMIT $limit
        """
        records = await Neo4jService._execute_query(
            query,
            {
                "category": knowledge_point_category,
                "name": knowledge_point_name,
                "limit": limit,
            },
        )

        results = []
        for record in records:
            if len(record) >= 3:
                results.append(
                    {
                        "id": record[0],
                        "title": record[1],
                        "asset_type": record[2],
                    }
                )
        return results

    @staticmethod
    async def get_knowledge_point_graph(
        knowledge_point_category: Optional[str] = None,
        max_depth: int = 2,
    ) -> Dict[str, Any]:
        """获取知识点图谱"""
        if knowledge_point_category:
            query = """
            MATCH path = (kp:KnowledgePoint {category: $category})-[*1..$max_depth]-(related)
            RETURN path
            LIMIT 100
            """
            params = {"category": knowledge_point_category, "max_depth": max_depth}
        else:
            query = """
            MATCH (kp:KnowledgePoint)
            OPTIONAL MATCH (kp)<-[:HAS_KNOWLEDGE_POINT]-(a:Asset)
            RETURN kp.category AS category,
                   kp.name AS name,
                   count(a) AS asset_count
            ORDER BY asset_count DESC, category, name
            LIMIT 100
            """
            params = {}

        records = await Neo4jService._execute_query(query, params)
        # 这里可以进一步处理结果，返回图谱数据
        return {"nodes": [], "edges": []}  # 简化版本

    # ========== 统计分析 ==========

    @staticmethod
    async def calculate_asset_similarity(
        asset_id_1: int,
        asset_id_2: int,
    ) -> float:
        """计算两个资源的相似度（基于共同特征）"""
        query = """
        MATCH (a1:Asset {id: $asset_id_1}), (a2:Asset {id: $asset_id_2})
        
        // 计算共同特征数量
        OPTIONAL MATCH (a1)-[:BELONGS_TO_SUBJECT]->(sub:Subject)<-[:BELONGS_TO_SUBJECT]-(a2)
        WITH a1, a2, count(sub) AS common_subjects
        
        OPTIONAL MATCH (a1)-[:BELONGS_TO_GRADE]->(g:Grade)<-[:BELONGS_TO_GRADE]-(a2)
        WITH a1, a2, common_subjects, count(g) AS common_grades
        
        OPTIONAL MATCH (a1)-[:HAS_KNOWLEDGE_POINT]->(kp:KnowledgePoint)<-[:HAS_KNOWLEDGE_POINT]-(a2)
        WITH a1, a2, common_subjects, common_grades, count(kp) AS common_knowledge_points
        
        OPTIONAL MATCH (a1)-[:CREATED_BY]->(u:User)<-[:CREATED_BY]-(a2)
        WITH common_subjects, common_grades, common_knowledge_points, count(u) AS common_creators
        
        // 计算相似度（简单加权平均）
        RETURN (common_subjects * 0.3 + common_grades * 0.2 + common_knowledge_points * 0.4 + common_creators * 0.1) AS similarity
        """
        records = await Neo4jService._execute_query(
            query,
            {
                "asset_id_1": asset_id_1,
                "asset_id_2": asset_id_2,
            },
        )

        if records and len(records[0]) > 0:
            return float(records[0][0] or 0.0)
        return 0.0

    @staticmethod
    async def sync_all_assets_from_postgres(
        assets: List[Dict[str, Any]],
    ) -> int:
        """从 PostgreSQL 同步所有资源到 Neo4j（批量操作）"""
        if not settings.NEO4J_ENABLED:
            return 0

        driver = await get_neo4j_driver()
        if driver is None:
            return 0

        count = 0
        try:
            async with driver.session(database=settings.NEO4J_DATABASE) as session:
                for asset in assets:
                    await Neo4jService.create_or_update_asset(
                        asset_id=asset["id"],
                        title=asset["title"],
                        asset_type=asset["asset_type"],
                        school_id=asset["school_id"],
                        owner_user_id=asset["owner_user_id"],
                        subject_id=asset.get("subject_id"),
                        grade_id=asset.get("grade_id"),
                        knowledge_point_category=asset.get("knowledge_point_category"),
                        knowledge_point_name=asset.get("knowledge_point_name"),
                    )
                    count += 1
        except Exception as e:
            logger.error(f"批量同步资源到 Neo4j 失败: {e}")

        return count


# 创建单例实例
neo4j_service = Neo4jService()

