# Docker Compose 文件结构说明

## 为什么要在 docker-compose.yml 中添加服务？

**Docker Compose** 是一个用于定义和运行多容器 Docker 应用程序的工具。通过 `docker-compose.yml` 文件，你可以：

1. **统一管理**：所有服务在一个配置文件中定义，便于管理和维护
2. **一键启动**：使用 `docker-compose up -d` 可以同时启动所有服务
3. **依赖管理**：可以定义服务之间的依赖关系（如 backend 依赖 postgres）
4. **网络隔离**：所有服务可以在同一个 Docker 网络中，方便互相访问
5. **数据持久化**：统一管理数据卷（volumes）

**如果不添加到 docker-compose.yml**：
- 需要使用 `docker run` 单独启动每个容器
- 无法统一管理，需要记住每个容器的启动命令
- 服务之间可能无法正常通信（网络隔离）
- 难以管理服务依赖关系

---

## 文件结构详解

### 1. 顶层结构

```yaml
services:     # 定义所有服务（容器）
  service1:   # 服务名称
    ...
  service2:
    ...

volumes:      # 定义数据卷（持久化存储）
  volume1:
  volume2:

networks:     # 定义网络（可选，用于服务间通信）
  network1:
    ...
```

---

## 2. Services（服务）部分

每个服务代表一个 Docker 容器。以 Neo4j 为例：

```yaml
services:
  # Neo4j 图数据库
  neo4j:                                    # ← 服务名称（在 docker-compose 中引用）
    image: neo4j:5.15-community            # ← Docker 镜像名称和版本
    container_name: inspireed-neo4j         # ← 容器名称（在 docker ps 中显示）
    ports:                                  # ← 端口映射（宿主机:容器）
      - "7474:7474"                         #   HTTP 界面端口
      - "7687:7687"                         #   Bolt 协议端口
    environment:                            # ← 环境变量（传递给容器）
      NEO4J_AUTH: neo4j/neo4j123           #   认证信息：用户名/密码
      NEO4J_PLUGINS: '["apoc"]'            #   插件配置
    volumes:                                # ← 数据卷挂载（持久化数据）
      - neo4j_data:/data                   #   数据目录
      - neo4j_logs:/logs                   #   日志目录
    healthcheck:                            # ← 健康检查（检测服务是否正常）
      test: ["CMD-SHELL", "..."]           #   检查命令
      interval: 30s                         #   检查间隔
      timeout: 10s                          #   超时时间
      retries: 5                            #   重试次数
      start_period: 60s                     #   启动等待时间
    restart: unless-stopped                # ← 重启策略
```

### 各配置项详解

#### `image` - Docker 镜像
```yaml
image: neo4j:5.15-community
```
- 指定要使用的 Docker 镜像
- 格式：`镜像名:标签`（标签通常是版本号）
- 如果本地没有，会自动从 Docker Hub 下载

#### `container_name` - 容器名称
```yaml
container_name: inspireed-neo4j
```
- 容器的名称，用于 `docker ps`、`docker logs` 等命令
- 如果不指定，Docker Compose 会自动生成（格式：`项目名_服务名_序号`）

#### `ports` - 端口映射
```yaml
ports:
  - "7474:7474"  # 宿主机端口:容器端口
  - "7687:7687"
```
- 将容器内的端口映射到宿主机的端口
- 格式：`"宿主机端口:容器端口"`
- 访问 `localhost:7474` 即可访问容器内的 7474 端口

#### `environment` - 环境变量
```yaml
environment:
  NEO4J_AUTH: neo4j/neo4j123
  NEO4J_PLUGINS: '["apoc"]'
```
- 传递给容器的环境变量
- 容器内的应用程序可以读取这些变量
- 也可以使用 `.env` 文件或 `${变量名}` 引用

#### `volumes` - 数据卷
```yaml
volumes:
  - neo4j_data:/data        # 命名卷（在 volumes 部分定义）
  - neo4j_logs:/logs
  - ./config:/app/config    # 绑定挂载（本地目录）
```
- **命名卷**：Docker 管理的持久化存储，数据保存在 Docker 的存储区域
- **绑定挂载**：直接挂载本地目录到容器
- 数据卷的作用：即使容器删除，数据也不会丢失

#### `healthcheck` - 健康检查
```yaml
healthcheck:
  test: ["CMD-SHELL", "cypher-shell -u neo4j -p neo4j123 'RETURN 1' || exit 1"]
  interval: 30s      # 每 30 秒检查一次
  timeout: 10s       # 超时时间 10 秒
  retries: 5         # 失败后重试 5 次
  start_period: 60s  # 启动后等待 60 秒再开始检查
```
- 定期检查容器是否正常运行
- 如果检查失败，Docker 会标记容器为不健康
- 其他服务可以通过 `depends_on` 等待健康检查通过

#### `restart` - 重启策略
```yaml
restart: unless-stopped
```
可选值：
- `no`：不自动重启（默认）
- `always`：总是重启（即使手动停止）
- `on-failure`：只在失败时重启
- `unless-stopped`：除非手动停止，否则总是重启

#### `depends_on` - 依赖关系
```yaml
depends_on:
  postgres:
    condition: service_healthy  # 等待 postgres 健康检查通过
  redis:
    condition: service_started  # 等待 redis 启动
```
- 定义服务启动顺序
- `service_healthy`：等待健康检查通过
- `service_started`：等待服务启动（不检查健康状态）

#### `networks` - 网络配置
```yaml
networks:
  - inspireed-network
```
- 将服务加入指定的 Docker 网络
- 同一网络内的服务可以通过服务名互相访问
- 例如：`postgres` 服务可以通过 `postgres:5432` 访问

---

## 3. Volumes（数据卷）部分

```yaml
volumes:
  postgres_data:      # 命名卷，用于 PostgreSQL 数据
  redis_data:         # 命名卷，用于 Redis 数据
  minio_data:         # 命名卷，用于 MinIO 数据
  neo4j_data:         # 命名卷，用于 Neo4j 数据
  neo4j_logs:         # 命名卷，用于 Neo4j 日志
```

- 定义命名数据卷
- 数据卷是持久化存储，即使容器删除，数据也不会丢失
- 可以通过 `docker volume ls` 查看所有数据卷
- 可以通过 `docker volume inspect 卷名` 查看数据卷详情

---

## 4. Networks（网络）部分（在 docker-compose.prod.yml 中）

```yaml
networks:
  inspireed-network:
    name: docker_inspireed-network  # 网络名称
    driver: bridge                  # 网络驱动（bridge 是最常用的）
```

- 定义 Docker 网络
- 同一网络内的服务可以通过服务名互相访问
- 例如：backend 服务可以通过 `postgres:5432` 访问 PostgreSQL

---

## 5. 两个配置文件的区别

### `docker-compose.yml`（开发环境）
- 用于本地开发
- 服务直接暴露端口到 localhost
- 不定义网络（使用默认网络）

### `docker-compose.prod.yml`（生产环境）
- 用于生产部署
- 服务在同一个 Docker 网络中
- 通过服务名互相访问（如 `postgres:5432` 而不是 `localhost:5432`）
- 包含 backend 和 frontend 服务

---

## 6. 常用命令

### 启动服务
```bash
# 启动所有服务
docker-compose up -d

# 启动指定服务
docker-compose up -d neo4j

# 使用生产环境配置
docker-compose -f docker-compose.prod.yml up -d
```

### 查看状态
```bash
# 查看所有服务状态
docker-compose ps

# 查看日志
docker-compose logs neo4j

# 实时查看日志
docker-compose logs -f neo4j
```

### 停止服务
```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（⚠️ 会删除数据）
docker-compose down -v
```

### 重启服务
```bash
# 重启指定服务
docker-compose restart neo4j
```

---

## 7. 服务间通信

### 在 docker-compose.yml 中（开发环境）
- 服务可以通过 `localhost:端口` 访问其他服务
- 例如：backend 通过 `localhost:5432` 访问 PostgreSQL

### 在 docker-compose.prod.yml 中（生产环境）
- 服务在同一个 Docker 网络中
- 可以通过**服务名:端口**访问
- 例如：backend 通过 `postgres:5432` 访问 PostgreSQL
- 这样更安全，服务不暴露到宿主机

---

## 8. 为什么 Neo4j 需要添加到 docker-compose.yml？

**之前的问题**：
- Neo4j 使用 `docker run` 单独启动
- 无法通过 `docker-compose ps` 查看
- 无法统一管理启动/停止
- 如果使用生产环境配置，backend 无法通过服务名访问 Neo4j

**添加后的好处**：
- ✅ 统一管理：`docker-compose ps` 可以看到所有服务
- ✅ 一键启动：`docker-compose up -d` 启动所有服务
- ✅ 依赖管理：backend 可以等待 Neo4j 健康检查通过
- ✅ 网络通信：在生产环境中可以通过 `neo4j:7687` 访问
- ✅ 数据持久化：数据卷统一管理

---

## 总结

`docker-compose.yml` 文件是 Docker Compose 的核心配置文件，它：

1. **定义服务**：每个服务对应一个容器
2. **配置环境**：通过环境变量配置服务
3. **管理数据**：通过数据卷持久化数据
4. **网络隔离**：通过网络配置服务间通信
5. **依赖管理**：通过 depends_on 管理启动顺序

**核心原则**：所有需要统一管理的服务都应该添加到 `docker-compose.yml` 中！

