# InspireEd 架构设计文档

## 系统架构概览

InspireEd 采用前后端分离的微服务架构，基于 Jupyter 式可执行文档模型设计。

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     前端层 (Frontend)                          │
│  Vue3 + TipTap + CodeMirror + JupyterLite + Three.js       │
└─────────────────────────────────────────────────────────────┘
                            ↓ REST/WebSocket
┌─────────────────────────────────────────────────────────────┐
│                     应用层 (Backend)                           │
│              FastAPI + Pydantic + SQLAlchemy                │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │ 认证服务  │ 教案服务  │ 执行服务  │ AI服务   │ 分析服务  │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     执行层 (Execution)                         │
│  JupyterLite (Browser) + JupyterHub (Server) + 仿真引擎      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     数据层 (Data Storage)                      │
│  PostgreSQL + TimescaleDB + Redis + MinIO + Kafka          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     分析层 (Analytics)                         │
│            ClickHouse + Power BI / Superset                │
└─────────────────────────────────────────────────────────────┘
```

## 核心模块设计

### 1. 前端架构

#### 技术栈
- **框架**: Vue3 + TypeScript
- **状态管理**: Pinia
- **路由**: Vue Router
- **UI**: TailwindCSS
- **编辑器**: TipTap (富文本) + CodeMirror (代码)
- **执行引擎**: JupyterLite (Pyodide)
- **3D渲染**: Three.js
- **物理引擎**: Matter.js

#### 组件结构
```
components/
├── Cell/               # Cell组件
│   ├── TextCell.vue    # 富文本单元
│   ├── CodeCell.vue    # 代码执行单元
│   ├── ParamCell.vue   # 参数配置单元
│   ├── SimCell.vue     # 仿真单元
│   ├── QACell.vue      # 问答单元
│   ├── ChartCell.vue   # 图表单元
│   └── ContestCell.vue # 竞技单元
├── Editor/             # 编辑器组件
│   ├── TipTapEditor.vue
│   └── StructureTree.vue
├── AIChat/             # AI聊天组件
└── Dashboard/          # 看板组件
```

### 2. 后端架构

#### 服务模块

**认证服务 (Auth Service)**
- JWT token生成与验证
- OAuth2密码流
- 角色权限控制 (RBAC)

**教案服务 (Lesson Service)**
- 教案CRUD
- 版本控制
- 发布管理
- 资源映射

**执行服务 (Execution Service)**
- Cell执行调度
- JupyterHub API集成
- 结果收集与存储
- 执行日志管理

**AI服务 (AI Service)**
- LangChain集成
- OpenAI API调用
- 向量检索 (FAISS)
- 问答管理

**分析服务 (Analytics Service)**
- 数据聚合
- 指标计算
- 报表生成

### 3. 数据模型

#### 核心实体

**User (用户)**
```python
- id: int
- email: str
- username: str
- role: UserRole (teacher/student/researcher)
- hashed_password: str
```

**Lesson (教案)**
```python
- id: int
- title: str
- content: JSON  # Cell配置数组
- status: LessonStatus (draft/published/archived)
- creator_id: int
- version: int
```

**Cell (单元)**
```python
- id: int
- lesson_id: int
- cell_type: CellType
- content: JSON
- config: JSON
- order: int
```

**ExecutionLog (执行日志)**
```python
- id: int
- lesson_id: int
- cell_id: int
- user_id: int
- status: ExecutionStatus
- input_params: JSON
- output: JSON
- duration: float
```

**QARecord (问答记录)**
```python
- id: int
- user_id: int
- question: str
- answer: str
- is_ai_answer: bool
- tags: JSON
```

### 4. Cell类型设计

| Cell类型 | 功能描述 | 前端实现 | 后端支持 |
|---------|---------|---------|---------|
| TextCell | 富文本内容 | TipTap | 存储JSON |
| CodeCell | 可执行代码 | CodeMirror + JupyterLite | JupyterHub |
| ParamCell | 参数配置 | JSON Schema Form | 验证参数 |
| SimCell | 仿真预览 | Three.js/Matter.js | WebSocket |
| QACell | 问答交互 | 聊天界面 | AI API |
| ChartCell | 数据可视化 | ECharts | 数据处理 |
| ContestCell | 竞技任务 | 排行榜 | 计分逻辑 |

### 5. 执行引擎设计

#### JupyterLite (浏览器端)
- **优势**: 零延迟、离线可用
- **限制**: 计算能力受限
- **适用**: 简单Python脚本、数据处理

#### JupyterHub (服务端)
- **优势**: 完整Python环境、GPU支持
- **限制**: 需要网络请求
- **适用**: 复杂计算、机器学习

#### 执行流程
```
1. 用户点击运行 → 前端判断复杂度
2. 简单任务 → JupyterLite 执行
3. 复杂任务 → 提交到 JupyterHub
4. 结果返回 → 渲染输出
5. 日志上报 → TimescaleDB
```

### 6. AI子系统设计

#### LangChain集成
```python
from langchain import LLM, PromptTemplate
from langchain.agents import Agent

# 教师助手Agent
teacher_agent = Agent(
    llm=OpenAI(model="gpt-4"),
    tools=[课程生成工具, 参数建议工具],
    prompt=教师助手提示词
)

# 学生助手Agent
student_agent = Agent(
    llm=OpenAI(model="gpt-4"),
    tools=[答疑工具, 资源推荐工具],
    prompt=学生助手提示词
)
```

#### 向量检索流程
```
1. 教案内容 → 文本分块
2. 分块文本 → Embedding (OpenAI)
3. 向量存储 → FAISS索引
4. 用户提问 → 向量检索
5. 相关内容 → GPT生成答案
```

### 7. 数据中台设计

#### 日志采集流程
```
前端/后端 → 事件埋点 → Kafka → ClickHouse → 聚合分析 → Dashboard
```

#### 核心指标
- 学生完成率
- 实验准确率
- AI答疑频次
- 教师活跃度
- 教研优化频率

### 8. 安全设计

#### 认证与授权
- JWT token (7天有效期)
- 刷新token机制
- RBAC权限控制
- API速率限制

#### 数据安全
- HTTPS全链路加密
- 密码bcrypt哈希
- SQL注入防护 (ORM)
- XSS/CSRF防护

#### 执行安全
- JupyterHub容器隔离
- 资源限制 (CPU/内存/时间)
- 代码沙箱
- 文件系统隔离

### 9. 性能优化

#### 前端优化
- 路由懒加载
- 组件按需加载
- 图片懒加载
- 代码分割

#### 后端优化
- 数据库连接池
- Redis缓存
- 异步IO (async/await)
- 批量查询优化

#### 缓存策略
- 用户信息 → Redis (30分钟)
- 教案内容 → Redis (10分钟)
- 执行结果 → Redis (5分钟)
- 静态资源 → CDN

### 10. 部署架构

#### Docker容器化
```yaml
services:
  frontend:   # Vue3 应用
  backend:    # FastAPI 服务
  postgres:   # 主数据库
  redis:      # 缓存
  minio:      # 对象存储
  jupyterhub: # 执行引擎
  kafka:      # 消息队列
  clickhouse: # 分析数据库
```

#### 扩展性考虑
- 水平扩展: 多个backend实例 + 负载均衡
- 数据分片: 按用户ID分表
- 读写分离: PostgreSQL主从复制
- 消息队列: Kafka分区机制

## 技术选型理由

| 技术 | 选型理由 |
|------|---------|
| Vue3 | 响应式强、生态成熟、学习曲线平缓 |
| FastAPI | 高性能、自动文档、类型安全 |
| PostgreSQL | 可靠性高、JSON支持、扩展性强 |
| TimescaleDB | 时序数据优化、PostgreSQL兼容 |
| JupyterLite | 浏览器端执行、零服务器负担 |
| LangChain | AI应用框架、工具链完整 |
| TipTap | 灵活扩展、Vue3原生支持 |
| Pinia | Vue3官方推荐、简洁API |

## 未来演进方向

1. **实时协作编辑** - 使用 CRDT 或 OT 算法
2. **离线模式** - PWA + IndexedDB
3. **移动端适配** - 响应式设计 + 原生App
4. **跨校数据共享** - 联邦学习 + 隐私计算
5. **AI自动评分** - 代码相似度 + 结果校验

