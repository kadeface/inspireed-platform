# Neo4j 资源库知识图谱集成方案

## 概述

本文档说明如何使用 Neo4j 图数据库优化 InspireEd 平台的资源库功能。Neo4j 用于构建知识图谱，实现智能推荐、相似资源查询、关系分析等功能。

## 架构设计

### 数据存储策略

- **PostgreSQL（主存储）**：存储资源的所有元数据和文件信息（原有功能）
- **Neo4j（图存储）**：存储资源之间的关系图谱，用于高级查询和推荐

### 同步机制

- **实时同步**：在资源创建、更新、删除时，自动同步到 Neo4j
- **异步处理**：Neo4j 同步失败不会影响主要功能（降级处理）
- **可选功能**：可以通过配置 `NEO4J_ENABLED=false` 禁用 Neo4j

## 图数据模型

### 节点类型（Nodes）

1. **Asset**：资源资产
   - 属性：`id`, `title`, `asset_type`, `school_id`, `updated_at`

2. **School**：学校
   - 属性：`id`

3. **User**：用户（资源创建者）
   - 属性：`id`

4. **Subject**：学科
   - 属性：`id`

5. **Grade**：年级
   - 属性：`id`

6. **KnowledgePoint**：知识点
   - 属性：`category`, `name`

### 关系类型（Relationships）

1. **BELONGS_TO_SCHOOL**：资源属于学校
   - `(Asset)-[:BELONGS_TO_SCHOOL]->(School)`

2. **CREATED_BY**：资源由用户创建
   - `(Asset)-[:CREATED_BY]->(User)`

3. **BELONGS_TO_SUBJECT**：资源属于学科
   - `(Asset)-[:BELONGS_TO_SUBJECT]->(Subject)`

4. **BELONGS_TO_GRADE**：资源属于年级
   - `(Asset)-[:BELONGS_TO_GRADE]->(Grade)`

5. **HAS_KNOWLEDGE_POINT**：资源包含知识点
   - `(Asset)-[:HAS_KNOWLEDGE_POINT]->(KnowledgePoint)`

6. **SIMILAR_TO**：资源相似关系（带相似度分数）
   - `(Asset)-[:SIMILAR_TO {score: 0.8}]->(Asset)`

7. **USED_WITH**：资源一起使用关系（基于使用统计）
   - `(Asset)-[:USED_WITH {count: 10}]->(Asset)`

## 功能特性

### 1. 相似资源查询

基于知识图谱查找相似资源，考虑以下因素：
- 共同学科
- 共同年级
- 共同知识点
- 相同创建者

**API 端点**：`GET /api/v1/library/assets/{asset_id}/similar`

**参数**：
- `limit`：返回数量（默认 10）
- `min_similarity`：最小相似度（默认 0.5）

### 2. 相关资源查询

基于图路径查找相关资源（1-2 跳关系）。

**API 端点**：`GET /api/v1/library/assets/{asset_id}/related`

**参数**：
- `limit`：返回数量（默认 10）

### 3. 推荐资源

基于用户、学科、年级等因素推荐资源。

**API 端点**：`GET /api/v1/library/assets/recommended`

**参数**：
- `subject_id`：学科ID（可选）
- `grade_id`：年级ID（可选）
- `limit`：返回数量（默认 10）

### 4. 知识点图谱

构建知识点之间的关系图谱，支持查询知识点的层级关系。

## 配置

### 环境变量

在 `backend/.env` 文件中配置：

```bash
# Neo4j 图数据库配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j
NEO4J_DATABASE=neo4j
NEO4J_ENABLED=true
```

### Docker Compose

Neo4j 服务已添加到 `docker/docker-compose.yml` 和 `docker/docker-compose.prod.yml`：

```yaml
neo4j:
  image: neo4j:5.15-community
  container_name: inspireed-neo4j
  ports:
    - "7474:7474"  # HTTP 界面
    - "7687:7687"  # Bolt 协议
  environment:
    NEO4J_AUTH: neo4j/neo4j
    NEO4J_PLUGINS: '["apoc"]'
  volumes:
    - neo4j_data:/data
    - neo4j_logs:/logs
```

## 安装和启动

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动 Neo4j（Docker）

```bash
# 启动所有服务（包括 Neo4j）
cd docker
docker-compose up -d neo4j

# 或使用生产环境脚本
../start-prod.sh
```

### 3. 首次启动配置

首次启动 Neo4j 后，需要修改默认密码：

1. 访问 Neo4j 浏览器：http://localhost:7474
2. 使用默认密码登录：`neo4j/neo4j`
3. 修改密码（建议）
4. 更新 `.env` 文件中的 `NEO4J_PASSWORD`

### 4. 验证连接

启动后端服务后，检查日志中是否有：

```
✅ Neo4j connection verified
```

如果连接失败，会显示：

```
⚠️ Neo4j is enabled but connection failed, graph features will be disabled
```

## 使用示例

### 查询相似资源

```bash
curl -X GET "http://localhost:8000/api/v1/library/assets/1/similar?limit=5&min_similarity=0.6" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 查询相关资源

```bash
curl -X GET "http://localhost:8000/api/v1/library/assets/1/related?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 获取推荐资源

```bash
curl -X GET "http://localhost:8000/api/v1/library/assets/recommended?subject_id=1&grade_id=1&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 数据同步

### 自动同步

资源库资产的创建、更新、删除操作会自动同步到 Neo4j：

- **创建资源**：调用 `neo4j_service.create_or_update_asset()`
- **更新资源**：调用 `neo4j_service.create_or_update_asset()`
- **删除资源**：调用 `neo4j_service.delete_asset()`

### 手动同步（批量）

如果需要将现有数据批量同步到 Neo4j，可以编写脚本：

```python
from app.services.neo4j_service import neo4j_service
from app.models import LibraryAsset
# ... 获取所有资源并同步
```

## 性能优化

1. **索引**：Neo4j 会自动为节点属性创建索引（如 `Asset.id`）
2. **批量操作**：使用事务批量写入以提高性能
3. **查询优化**：限制路径深度和返回数量
4. **降级处理**：Neo4j 不可用时，相关 API 会降级使用 PostgreSQL 查询

## 监控和维护

### Neo4j 浏览器

访问 http://localhost:7474 使用 Neo4j 浏览器查看和查询图谱数据。

### 常用查询

**查看所有资源节点**：
```cypher
MATCH (a:Asset) RETURN a LIMIT 100
```

**查看资源关系**：
```cypher
MATCH (a:Asset)-[r]->(n) RETURN a, r, n LIMIT 50
```

**统计节点数量**：
```cypher
MATCH (a:Asset) RETURN count(a) AS asset_count
```

### 备份和恢复

Neo4j 数据存储在 Docker volume `neo4j_data` 中，备份方法：

```bash
# 备份
docker run --rm -v inspireed-neo4j-data:/data -v $(pwd):/backup alpine tar czf /backup/neo4j-backup.tar.gz /data

# 恢复
docker run --rm -v inspireed-neo4j-data:/data -v $(pwd):/backup alpine tar xzf /backup/neo4j-backup.tar.gz -C /
```

## 故障排除

### Neo4j 连接失败

1. 检查 Neo4j 服务是否运行：`docker ps | grep neo4j`
2. 检查端口是否被占用：`netstat -an | grep 7687`
3. 检查环境变量配置是否正确
4. 查看 Neo4j 日志：`docker logs inspireed-neo4j`

### 同步失败

- 同步失败不会影响主要功能，只会在日志中记录警告
- 检查后端日志中的 Neo4j 相关错误
- 确保 Neo4j 服务正常运行

### 性能问题

- 检查 Neo4j 内存配置（`NEO4J_dbms_memory_heap_max__size`）
- 优化 Cypher 查询（限制路径深度和返回数量）
- 考虑使用 Neo4j 的 APOC 插件进行复杂查询

## 未来扩展

1. **用户行为分析**：追踪用户浏览、下载资源的行为路径
2. **智能标签系统**：基于内容相似度自动生成标签
3. **学习路径推荐**：基于知识点关系推荐学习路径
4. **资源质量评分**：基于使用频率和用户反馈构建评分模型
5. **知识图谱可视化**：在前端展示资源之间的关系图谱

## 参考资源

- [Neo4j 官方文档](https://neo4j.com/docs/)
- [Neo4j Python 驱动文档](https://neo4j.com/docs/python-manual/current/)
- [Cypher 查询语言](https://neo4j.com/developer/cypher/)
- [Neo4j APOC 插件](https://neo4j.com/labs/apoc/)

