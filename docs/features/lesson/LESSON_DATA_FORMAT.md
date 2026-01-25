# 教案数据格式说明

本文档详细说明前端教案的编码格式以及后端存储格式。

## 概述

教案的核心内容是 **Cell 数组**，每个 Cell 代表教案中的一个教学单元。前端使用 TypeScript 类型定义，后端使用 PostgreSQL 的 JSON 类型存储。

## 前端编码格式

### 1. 教案整体结构

前端使用 TypeScript 接口定义教案结构：

```typescript
// frontend/src/types/lesson.ts
export interface Lesson {
  id: number
  title: string
  description?: string
  creator_id: number
  course_id: number
  chapter_id?: number
  status: LessonStatus  // 'draft' | 'published' | 'archived'
  content: Cell[]       // 核心：Cell 数组
  version: number
  parent_id?: number
  tags?: string[]
  // ... 其他字段
}
```

### 2. Cell 类型定义

Cell 是教案内容的基本单元，支持多种类型：

```typescript
// frontend/src/types/cell.ts
export const CellType = {
  TEXT: 'text',              // 文本单元
  VIDEO: 'video',            // 视频单元
  CODE: 'code',              // 代码单元
  SIM: 'sim',                // 仿真单元（PhET等）
  CHART: 'chart',            // 图表单元
  CONTEST: 'contest',        // 竞赛单元
  PARAM: 'param',            // 参数单元
  ACTIVITY: 'activity',     // 教学活动单元
  FLOWCHART: 'flowchart',    // 流程图单元
  REFERENCE_MATERIAL: 'reference_material',  // 参考资料单元
} as const
```

### 3. Cell 基础结构

所有 Cell 都继承自 `CellBase`：

```typescript
export interface CellBase {
  id: number | string        // 支持数字ID或字符串ID（如"cell-1"）
  type: CellType
  order: number              // 顺序
  title?: string
  stage_label?: string
  editable: boolean
  
  // 🎓 学习科学字段
  cognitive_level?: 'remember' | 'understand' | 'apply' | 'analyze' | 'evaluate' | 'create'
  prerequisite_cells?: (string | number)[]  // 前置单元ID列表
  mastery_criteria?: {
    min_attempts?: number
    min_accuracy?: number
    max_time_seconds?: number
  }
}
```

### 4. 各类型 Cell 的具体结构

#### 文本单元 (TextCell)

```typescript
export interface TextCell extends CellBase {
  type: 'text'
  content: {
    html: string           // HTML 格式的文本内容
    json?: any            // TipTap JSON 格式（可选）
  }
}
```

#### 视频单元 (VideoCell)

```typescript
export interface VideoCell extends CellBase {
  type: 'video'
  content: {
    videoUrl: string
    title?: string
    description?: string
    duration?: number      // 视频时长（秒）
    thumbnail?: string     // 缩略图URL
    subtitles?: Array<{
      language: string
      url: string
    }>
    chapters?: Array<{
      title: string
      startTime: number
      endTime: number
    }>
  }
  config: {
    autoplay?: boolean
    controls?: boolean
    loop?: boolean
    muted?: boolean
    startTime?: number
    endTime?: number
    playbackRate?: number
  }
}
```

#### 代码单元 (CodeCell)

```typescript
export interface CodeCell extends CellBase {
  type: 'code'
  content: {
    code: string
    language: 'python' | 'javascript' | 'html'
    output?: any
  }
  config: {
    timeout?: number
    maxMemory?: number
    environment?: 'jupyterlite' | 'jupyterhub'
  }
}
```

#### 仿真单元 (SimCell)

```typescript
export interface SimCell extends CellBase {
  type: 'sim'
  content: {
    type: 'phet' | 'threejs' | 'matterjs' | 'iframe' | 'custom'
    phetSim?: string      // PhET simulation name/ID
    phetCategory?: 'physics' | 'chemistry' | 'biology' | 'earth' | 'math'
    url?: string          // Generic iframe/URL
    config: {
      width?: number
      height?: number
      locale?: string
      autoplay?: boolean
      fullScreen?: boolean
      [key: string]: any
    }
  }
}
```

#### 教学活动单元 (ActivityCell)

```typescript
export interface ActivityCell extends CellBase {
  type: 'activity'
  content: ActivityCellContent  // 详见 activity.ts
  config?: {
    allowOffline?: boolean
  }
}
```

#### 流程图单元 (FlowchartCell)

```typescript
export interface FlowchartCell extends CellBase {
  type: 'flowchart'
  content: {
    nodes: FlowchartNode[]
    edges: FlowchartEdge[]
    style?: {
      theme?: 'light' | 'dark'
      layoutDirection?: 'TB' | 'LR' | 'BT' | 'RL'
    }
  }
  config?: {
    editable?: boolean
    showMinimap?: boolean
  }
}
```

### 5. 数据序列化

前端通过 HTTP API 发送教案数据时：

1. **使用 axios** 进行 HTTP 请求
2. **自动序列化**：TypeScript 对象自动转换为 JSON 字符串
3. **Content-Type**: `application/json`

示例请求：

```typescript
// frontend/src/services/lesson.ts
async updateLesson(id: number, data: LessonUpdate): Promise<Lesson> {
  const response = await api.put<Lesson>(`${this.basePath}/${id}`, data)
  return response
}
```

实际发送的 JSON 格式：

```json
{
  "title": "教案标题",
  "description": "教案描述",
  "content": [
    {
      "id": 1,
      "type": "text",
      "order": 0,
      "title": "文本单元",
      "editable": false,
      "content": {
        "html": "<p>这是文本内容</p>"
      }
    },
    {
      "id": 2,
      "type": "video",
      "order": 1,
      "title": "视频单元",
      "editable": false,
      "content": {
        "videoUrl": "https://example.com/video.mp4",
        "title": "教学视频"
      },
      "config": {
        "autoplay": false,
        "controls": true
      }
    }
  ],
  "tags": ["标签1", "标签2"]
}
```

## 后端存储格式

### 1. 数据库模型

后端使用 SQLAlchemy 定义教案模型：

```python
# backend/app/models/lesson.py
class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # 教案内容（JSON格式存储Cell配置）
    content = Column(JSON, nullable=False, default=list)
    
    # 其他字段...
```

**关键点**：
- `content` 字段类型为 `JSON`（PostgreSQL 的 JSON 类型）
- 默认值为空列表 `[]`
- 直接存储 JSON 数据，无需额外序列化

### 2. API Schema

后端使用 Pydantic 定义请求/响应 Schema：

```python
# backend/app/schemas/lesson.py
class LessonCreate(LessonBase):
    course_id: int
    chapter_id: Optional[int] = None
    content: List[dict] = Field(default_factory=list)  # 接收字典列表
    national_resource_id: Optional[str] = None

class LessonResponse(LessonBase):
    id: int
    content: List[dict]  # 返回字典列表
    # ... 其他字段
```

**关键点**：
- 接收时：`List[dict]`（Python 字典列表）
- 存储时：直接存储为 PostgreSQL JSON 类型
- 返回时：`List[dict]`（从 JSON 字段自动反序列化）

### 3. 数据流转过程

```
前端 TypeScript 对象
    ↓ (HTTP POST/PUT, JSON 序列化)
后端接收: List[dict] (Pydantic)
    ↓ (SQLAlchemy ORM)
PostgreSQL JSON 字段
    ↓ (查询时自动反序列化)
后端返回: List[dict] (Pydantic)
    ↓ (HTTP GET, JSON 响应)
前端 TypeScript 对象
```

### 4. 实际存储示例

在 PostgreSQL 数据库中，`content` 字段存储的 JSON 示例：

```json
[
  {
    "id": 1,
    "type": "text",
    "order": 0,
    "title": "文本单元",
    "editable": false,
    "content": {
      "html": "<p>这是文本内容</p>"
    }
  },
  {
    "id": 2,
    "type": "video",
    "order": 1,
    "title": "视频单元",
    "editable": false,
    "content": {
      "videoUrl": "https://example.com/video.mp4",
      "title": "教学视频"
    },
    "config": {
      "autoplay": false,
      "controls": true
    }
  }
]
```

### 5. 后端处理代码

```python
# backend/app/api/v1/lessons.py
async def create_lesson(
    lesson_in: LessonCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """创建教案"""
    lesson = Lesson(
        title=lesson_in.title,
        description=lesson_in.description,
        creator_id=current_user.id,
        course_id=lesson_in.course_id,
        chapter_id=lesson_in.chapter_id,
        content=lesson_in.content,  # 直接赋值，SQLAlchemy 自动处理 JSON
        tags=lesson_in.tags or [],
    )
    db.add(lesson)
    await db.commit()
    # ...
```

## 数据格式特点

### 1. 类型一致性

- **前端**：使用 TypeScript 类型系统，编译时类型检查
- **后端**：使用 Pydantic Schema，运行时数据验证
- **数据库**：PostgreSQL JSON 类型，灵活存储

### 2. 序列化/反序列化

- **前端 → 后端**：axios 自动序列化 TypeScript 对象为 JSON
- **后端 → 数据库**：SQLAlchemy 自动处理 JSON 字段的序列化
- **数据库 → 后端**：SQLAlchemy 自动反序列化 JSON 为 Python dict
- **后端 → 前端**：FastAPI 自动序列化 Python dict 为 JSON

### 3. 数据验证

- **前端**：TypeScript 编译时检查
- **后端**：Pydantic 运行时验证（字段类型、必填项等）
- **数据库**：PostgreSQL JSON 类型验证（确保是有效的 JSON）

## Cell ID 类型问题与优化建议

### 问题描述

当前系统中，Cell 的 `id` 字段存在类型不一致的问题：

1. **前端**：`id: number | string`（支持 UUID 字符串或数字 ID）
2. **后端存储**：`lesson.content` JSON 中可能同时存在 UUID 字符串和数字 ID
3. **数据库**：`cells` 表使用 `Integer` 主键
4. **问题**：类型不一致导致后端处理复杂，容易出现错误

### 当前实现

- **前端创建**：使用 `uuidv4()` 生成临时 UUID（如 `"a6121660-02ea-4c80-8fe0-8002928b31e5"`）
- **后端存储**：`lesson.content` 中直接存储前端发送的 Cell 对象（包含 UUID）
- **数据库查询**：需要通过 `order` 字段匹配，或从 `lesson.content` 中查找并创建 Cell 记录

### 优化方案

#### 方案 1：保存时统一转换（推荐）⭐

**核心思想**：在保存教案时，将 UUID 转换为数字 ID，并同步创建/更新 `cells` 表记录。

**实现步骤**：

1. **前端保存前处理**：
   ```typescript
   // 保存教案时，标记需要同步的 Cell
   async function saveLesson(lesson: Lesson) {
     const cellsToSync = lesson.content.map((cell, index) => ({
       uuid: typeof cell.id === 'string' ? cell.id : null,
       order: index,
       data: cell
     }))
     
     // 发送到后端，后端会处理 ID 转换
     await lessonService.updateLesson(lesson.id, {
       ...lesson,
       _cellsToSync: cellsToSync  // 临时字段，用于同步
     })
   }
   ```

2. **后端保存时同步**：
   ```python
   # backend/app/api/v1/lessons.py
   async def update_lesson(
       lesson_id: int,
       lesson_in: LessonUpdate,
       db: AsyncSession = Depends(get_db),
   ):
       lesson = await db.get(Lesson, lesson_id)
       
       # 同步 Cell 记录
       for index, cell_data in enumerate(lesson_in.content):
           cell_uuid = cell_data.get('id')
           cell_order = cell_data.get('order', index)
           
           # 查找已存在的 Cell（通过 order 匹配）
           existing_cell = await db.execute(
               select(Cell).where(
                   and_(
                       Cell.lesson_id == lesson_id,
                       Cell.order == cell_order
                   )
               )
           ).scalar_one_or_none()
           
           if existing_cell:
               # 更新现有 Cell
               existing_cell.content = cell_data.get('content', {})
               existing_cell.config = cell_data.get('config', {})
               # ... 更新其他字段
           else:
               # 创建新 Cell
               new_cell = Cell(
                   lesson_id=lesson_id,
                   cell_type=CellType(cell_data.get('type')),
                   order=cell_order,
                   content=cell_data.get('content', {}),
                   # ...
               )
               db.add(new_cell)
               await db.flush()  # 获取 ID
               
               # 更新 lesson.content 中的 ID
               cell_data['id'] = new_cell.id
       
       # 保存更新后的 content
       lesson.content = lesson_in.content
       await db.commit()
   ```

**优点**：
- ✅ 保存后 `lesson.content` 中的 ID 统一为数字
- ✅ 数据库中有完整的 Cell 记录
- ✅ 后续查询和导航更简单
- ✅ 类型一致性更好

**缺点**：
- ⚠️ 需要修改保存逻辑
- ⚠️ 草稿状态的 Cell 也会创建记录

#### 方案 2：使用辅助字段存储数据库 ID

**核心思想**：保留 UUID 作为主 ID，添加 `_dbId` 字段存储数据库 ID。

**实现**：

1. **前端类型定义**：
   ```typescript
   export interface CellBase {
     id: string  // 统一使用 UUID
     _dbId?: number  // 数据库 ID（如果已保存）
     // ... 其他字段
   }
   ```

2. **保存时处理**：
   ```typescript
   // 保存后，更新 _dbId
   const savedLesson = await lessonService.updateLesson(lesson.id, lesson)
   savedLesson.content.forEach((cell, index) => {
     // 从后端返回的数据中获取数据库 ID
     if (cell._dbId) {
       currentLesson.value.content[index]._dbId = cell._dbId
     }
   })
   ```

3. **后端返回时添加**：
   ```python
   # 返回教案时，为每个 Cell 添加 _dbId
   for cell_data in lesson.content:
       cell_order = cell_data.get('order')
       db_cell = await find_cell_by_order(lesson_id, cell_order)
       if db_cell:
           cell_data['_dbId'] = db_cell.id
   ```

**优点**：
- ✅ 保持 UUID 作为主标识符
- ✅ 向后兼容性好
- ✅ 前端逻辑清晰

**缺点**：
- ⚠️ 需要维护两个 ID 字段
- ⚠️ 类型定义更复杂

#### 方案 3：完全使用数字 ID（需要后端先创建）

**核心思想**：前端创建 Cell 时，立即调用后端 API 创建记录，获取数字 ID。

**实现**：

1. **前端创建 Cell**：
   ```typescript
   async function createCell(lessonId: number, cellType: CellType, order: number) {
     // 立即创建数据库记录
     const cell = await cellService.createCell({
       lesson_id: lessonId,
       cell_type: cellType,
       order: order,
       content: getDefaultContent(cellType),
     })
     
     // 使用数据库返回的数字 ID
     return {
       id: cell.id,  // 数字 ID
       type: cellType,
       order: order,
       // ...
     }
   }
   ```

**优点**：
- ✅ ID 类型完全统一
- ✅ 不需要 UUID 转换逻辑

**缺点**：
- ❌ 草稿状态的 Cell 也会创建记录
- ❌ 创建 Cell 需要网络请求，可能影响性能
- ❌ 删除未保存的 Cell 需要额外处理

#### 方案 4：完全使用 UUID（需要修改数据库）

**核心思想**：将数据库 `cells.id` 改为 UUID 类型。

**实现**：
- 修改 `backend/app/models/cell.py`：`id = Column(UUID, primary_key=True, default=uuid.uuid4)`
- 需要数据库迁移

**优点**：
- ✅ 前后端 ID 类型完全一致
- ✅ 不需要转换逻辑

**缺点**：
- ❌ 需要修改数据库结构
- ❌ 可能影响现有数据
- ❌ UUID 作为主键性能略低于整数

### 推荐方案

**推荐使用方案 1（保存时统一转换）**，原因：

1. **类型一致性**：保存后所有 ID 都是数字，类型统一
2. **向后兼容**：不需要修改前端类型定义
3. **实现简单**：只需修改保存逻辑
4. **性能友好**：批量处理，减少数据库查询

### 实施建议

1. **短期**（快速修复）：
   - 在保存教案 API 中添加 Cell 同步逻辑
   - 确保保存后 `lesson.content` 中的 ID 都是数字

2. **中期**（优化体验）：
   - 添加前端工具函数，统一处理 ID 转换
   - 优化错误提示，明确 UUID 和数字 ID 的区别

3. **长期**（架构优化）：
   - 考虑是否完全使用 UUID（如果性能可接受）
   - 或者完全使用数字 ID（如果愿意接受草稿也创建记录）

## 注意事项

1. **字段命名**：前端使用驼峰命名（camelCase），后端使用蛇形命名（snake_case），但在 `content` 字段内部保持前端命名
2. **可选字段**：前端使用 `?` 标记可选字段，后端使用 `Optional[...]`，数据库字段可为 `nullable=True`
3. **默认值**：前端 TypeScript 接口不包含默认值，后端 Pydantic Schema 和数据库模型可以设置默认值
4. **ID 类型**：建议在保存教案时统一将 UUID 转换为数字 ID，确保类型一致性

## 相关文件

- 前端类型定义：`frontend/src/types/lesson.ts`, `frontend/src/types/cell.ts`
- 后端模型：`backend/app/models/lesson.py`
- 后端 Schema：`backend/app/schemas/lesson.py`
- API 端点：`backend/app/api/v1/lessons.py`
- 前端服务：`frontend/src/services/lesson.ts`

