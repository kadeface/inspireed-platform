# 基于课程模板的教案设计方案

## 一、设计理念

### 核心思想
教师创建教案时，不是从零开始，而是基于**课程标准教案模板**进行二次修改，形成个性化的教学内容。

### 设计合理性分析

#### ✅ 优势
1. **符合真实教学场景**
   - 教师通常基于教材、大纲、参考教案进行备课
   - 不是完全原创，而是在标准基础上做个性化调整

2. **提高教学效率**
   - 避免重复创建基础内容
   - 教师专注于个性化改进和创新

3. **保证教学质量**
   - 标准模板确保知识点完整性
   - 降低新教师的备课门槛

4. **促进知识共享**
   - 优秀教案可以成为新的模板
   - 教师间可以互相学习和改进

5. **支持迭代优化**
   - 模板可以持续更新
   - 教师可以选择同步最新版本

#### 🎯 适用场景
- 新教师快速上手
- 标准化课程教学
- 教研组协作备课
- 精品课程建设

---

## 二、数据模型设计

### 2.1 概念模型

```
课程体系
  └── 课程（Course）
       ├── 章节（Chapter）
       │    └── 资源（Resource）
       │         └── 📋 标准教案模板（LessonTemplate）
       │              ↓ [复制/引用]
       │         👤 教师教案（TeacherLesson）
       │              - 个性化修改
       │              - 保留模板引用
       │              - 可同步更新
```

### 2.2 数据库模型

#### LessonTemplate (标准教案模板)
```python
class LessonTemplate(Base):
    """标准教案模板 - 课程资源的一部分"""
    __tablename__ = "lesson_templates"
    
    id: int
    resource_id: int  # 关联到 Resource
    title: str  # 教案标题
    description: str  # 教案描述
    content: JSON  # Cell 数组
    version: str  # 版本号，如 "1.0.0"
    difficulty: str  # 难度：basic/intermediate/advanced
    estimated_duration: int  # 预计时长（分钟）
    tags: List[str]  # 标签
    
    # 元数据
    created_by: int  # 创建者（通常是管理员或专家）
    is_official: bool  # 是否官方模板
    usage_count: int  # 被使用次数
    rating: float  # 评分
    
    # 时间戳
    created_at: datetime
    updated_at: datetime
```

#### Lesson (教师教案)
```python
class Lesson(Base):
    """教师教案 - 教师个人的教学内容"""
    __tablename__ = "lessons"
    
    id: int
    course_id: int  # 所属课程
    teacher_id: int  # 所属教师
    
    # 基本信息
    title: str
    description: str
    content: JSON  # Cell 数组
    tags: List[str]
    
    # 模板关联
    template_id: int | None  # 来源模板ID（可选）
    template_version: str | None  # 复制时的模板版本
    is_modified: bool  # 是否已修改
    modification_summary: str | None  # 修改摘要
    
    # 状态
    status: str  # draft/published/archived
    visibility: str  # private/shared/public
    
    # 统计
    view_count: int
    student_count: int
    
    # 时间戳
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None
```

#### LessonModificationLog (修改日志)
```python
class LessonModificationLog(Base):
    """记录教师对模板的修改"""
    __tablename__ = "lesson_modification_logs"
    
    id: int
    lesson_id: int
    teacher_id: int
    
    # 修改内容
    modification_type: str  # add_cell/remove_cell/edit_cell/reorder
    cell_id: str | None
    changes: JSON  # 具体变更内容
    
    created_at: datetime
```

### 2.3 关联关系

```
Subject (学科)
  └── Grade (年级)
       └── Course (课程)
            ├── Chapter (章节)
            │    └── Resource (资源)
            │         └── LessonTemplate (标准教案模板) ←─┐
            │                                              │
            └── Lesson (教师教案) ─────────────────────────┘
                 - teacher_id                    [引用关系]
                 - template_id
```

---

## 三、用户交互流程设计

### 3.1 浏览课程到创建教案

#### 流程图
```
┌─────────────────────────────────────────────────────────┐
│ 1. 浏览课程结构                                          │
│    学科 → 年级 → 课程 → 章节 → 资源                     │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│ 2. 查看资源详情                                          │
│    - 显示资源说明                                        │
│    - 显示关联的教案模板列表                              │
│    - 每个模板显示：标题、描述、难度、时长、评分          │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│ 3. 选择教案模板                                          │
│    [选项A] 预览模板内容                                  │
│    [选项B] 基于此模板创建我的教案                        │
│    [选项C] 从空白开始                                    │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│ 4. 创建教案对话框                                        │
│    ✓ 已选课程：[显示课程名称]                            │
│    ✓ 已选模板：[显示模板名称]（可修改）                  │
│    - 输入教案标题（默认：模板标题）                      │
│    - 输入教案描述                                        │
│    - 添加个性化标签                                      │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│ 5. 生成教师教案                                          │
│    - 复制模板的所有 Cell                                 │
│    - 记录模板引用关系                                    │
│    - 跳转到编辑器                                        │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│ 6. 个性化编辑                                            │
│    - 修改 Cell 内容                                      │
│    - 添加/删除 Cell                                      │
│    - 调整顺序                                            │
│    - 系统自动标记"已修改"                                │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│ 7. 保存和发布                                            │
│    - 自动保存修改                                        │
│    - 可查看与模板的差异                                  │
│    - 发布给学生使用                                      │
└─────────────────────────────────────────────────────────┘
```

### 3.2 界面设计草图

#### A. 课程结构浏览页（增强版）

```
┌──────────────────────────────────────────────────────────┐
│ 课程：高一数学                                            │
├──────────────────────────────────────────────────────────┤
│ 📚 第一章：集合与函数                                     │
│   └─ 📖 1.1 集合的概念                                   │
│        ├─ 📄 教材资源                                    │
│        ├─ 🎥 视频资源                                    │
│        └─ 📋 标准教案 (2个模板)              [查看详情] │
│                                                           │
│   └─ 📖 1.2 集合的运算                                   │
│        └─ 📋 标准教案 (3个模板)              [查看详情] │
└──────────────────────────────────────────────────────────┘
```

#### B. 教案模板详情对话框

```
┌──────────────────────────────────────────────────────────┐
│  📋 教案模板：集合的概念                      [×]        │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  📊 基本信息                                             │
│     难度：★★☆☆☆ 基础                                    │
│     时长：45 分钟                                        │
│     评分：⭐ 4.8 (126 位教师使用)                        │
│     版本：v1.2.0                                         │
│                                                           │
│  📝 内容概览                                             │
│     1. 文本单元：课程导入                                │
│     2. 文本单元：集合的定义                              │
│     3. 代码单元：Python 集合操作演示                     │
│     4. 问答单元：集合练习题 (5题)                        │
│     5. 仿真单元：维恩图交互                              │
│                                                           │
│  💬 教师评价                                             │
│     "内容完整，代码示例很实用" - 王老师                  │
│     "学生反馈很好，互动性强" - 李老师                    │
│                                                           │
├──────────────────────────────────────────────────────────┤
│  [预览模板内容]  [基于此模板创建我的教案]  [取消]        │
└──────────────────────────────────────────────────────────┘
```

#### C. 创建教案对话框（基于模板）

```
┌──────────────────────────────────────────────────────────┐
│  创建我的教案                                  [×]        │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ✓ 选定课程                                              │
│    学科：数学  年级：高一                                │
│    课程：高一数学 → 第一章 → 1.1 集合的概念             │
│                                                           │
│  ✓ 选定模板                                              │
│    📋 集合的概念 (v1.2.0)                    [更换模板] │
│    包含 5 个教学单元                                     │
│                                                           │
│  ✏️ 个性化信息                                           │
│    教案标题 *                                            │
│    ┌──────────────────────────────────────┐            │
│    │ 集合的概念 - 2025高一(3)班           │            │
│    └──────────────────────────────────────┘            │
│                                                           │
│    教案描述                                              │
│    ┌──────────────────────────────────────┐            │
│    │ 针对本班学生基础，增加更多实例       │            │
│    │ 强化编程实践环节                     │            │
│    └──────────────────────────────────────┘            │
│                                                           │
│    标签（可选）                                          │
│    ┌──────────────────────────────────────┐            │
│    │ 集合, Python, 高一3班                │            │
│    └──────────────────────────────────────┘            │
│                                                           │
│  ℹ️ 提示：创建后，您可以自由修改所有内容                │
│                                                           │
├──────────────────────────────────────────────────────────┤
│                         [取消]  [创建教案]               │
└──────────────────────────────────────────────────────────┘
```

#### D. 编辑器中的模板关联提示

```
┌──────────────────────────────────────────────────────────┐
│ ← | 集合的概念 - 2025高一(3)班 | 已保存 | 保存 | 发布    │
├──────────────────────────────────────────────────────────┤
│ ℹ️ 基于模板："集合的概念 v1.2.0"                         │
│    [查看原模板] [对比差异] [同步模板更新]       [×关闭] │
├──────────────────────────────────────────────────────────┤
│  🛠️  │                                                    │
│  工具 │   [文本单元] 课程导入                     [✎] [×] │
│  栏   │   这是从模板复制的内容...                         │
│       │                                                    │
│       │   [➕ 在此添加单元]                               │
│       │                                                    │
│       │   [代码单元] Python 集合操作               [✎] [×] │
│       │   # 我的个性化修改                                │
│       │   students = {"张三", "李四", ...}   🔵 已修改    │
└──────────────────────────────────────────────────────────┘
```

---

## 四、核心功能设计

### 4.1 模板浏览与选择

#### 功能要求
- ✅ 在课程结构中显示资源的教案模板数量
- ✅ 点击查看模板列表和详情
- ✅ 预览模板内容（只读模式）
- ✅ 显示模板评分和使用统计
- ✅ 支持按难度、评分、时长筛选

#### API 设计
```typescript
// 获取资源的教案模板列表
GET /api/v1/resources/{resource_id}/templates
Response: {
  templates: [
    {
      id: 1,
      title: "集合的概念",
      description: "基础教案，适合新课导入",
      version: "1.2.0",
      difficulty: "basic",
      estimated_duration: 45,
      cell_count: 5,
      usage_count: 126,
      rating: 4.8,
      is_official: true,
      created_by: {...},
      preview_image_url: "...",
    }
  ]
}

// 获取模板详情
GET /api/v1/templates/{template_id}
Response: {
  ...基本信息,
  content: [...cells],
  reviews: [...教师评价],
  statistics: {...使用统计}
}
```

### 4.2 基于模板创建教案

#### 功能要求
- ✅ 复制模板的所有 Cell 到新教案
- ✅ 记录模板引用关系（template_id, template_version）
- ✅ 允许教师修改标题、描述、标签
- ✅ 自动关联到对应的课程

#### API 设计
```typescript
// 基于模板创建教案
POST /api/v1/lessons/from-template
Request: {
  template_id: 1,
  course_id: 10,
  title: "集合的概念 - 2025高一(3)班",
  description: "...",
  tags: ["集合", "Python", "高一3班"]
}
Response: {
  lesson: {
    id: 123,
    template_id: 1,
    template_version: "1.2.0",
    is_modified: false,
    content: [...从模板复制的cells],
    ...
  }
}
```

#### 实现逻辑
```python
async def create_lesson_from_template(
    template_id: int,
    course_id: int,
    teacher_id: int,
    customization: LessonCustomization
):
    # 1. 获取模板
    template = await get_template(template_id)
    
    # 2. 深拷贝模板内容
    content = deep_copy_cells(template.content)
    
    # 3. 创建教案
    lesson = Lesson(
        course_id=course_id,
        teacher_id=teacher_id,
        title=customization.title or template.title,
        description=customization.description or template.description,
        content=content,
        tags=customization.tags or template.tags,
        template_id=template.id,
        template_version=template.version,
        is_modified=False,
        status="draft"
    )
    
    # 4. 保存
    await db.save(lesson)
    
    # 5. 更新模板使用统计
    await increment_template_usage(template_id)
    
    return lesson
```

### 4.3 修改跟踪

#### 功能要求
- ✅ 自动检测教师对模板内容的修改
- ✅ 标记已修改的 Cell
- ✅ 生成修改摘要
- ✅ 支持查看与原模板的差异

#### 修改检测逻辑
```typescript
// Cell 层面的修改检测
interface CellWithMetadata extends Cell {
  _metadata?: {
    fromTemplate: boolean
    originalCellId?: string
    isModified: boolean
    modificationDate?: Date
  }
}

// 自动标记修改
function detectModifications(lesson: Lesson, template: LessonTemplate) {
  const modifications = {
    added: [],
    removed: [],
    modified: [],
    reordered: false
  }
  
  // 检测添加/删除
  const templateCellIds = template.content.map(c => c.id)
  const lessonCellIds = lesson.content.map(c => c._metadata?.originalCellId)
  
  modifications.added = lesson.content.filter(
    c => !c._metadata?.fromTemplate
  )
  
  modifications.removed = templateCellIds.filter(
    id => !lessonCellIds.includes(id)
  )
  
  // 检测内容修改
  lesson.content.forEach(cell => {
    if (cell._metadata?.fromTemplate) {
      const originalCell = findCell(template.content, cell._metadata.originalCellId)
      if (!deepEqual(cell.content, originalCell.content)) {
        modifications.modified.push(cell.id)
        cell._metadata.isModified = true
      }
    }
  })
  
  // 检测顺序变化
  modifications.reordered = checkOrderChanged(lesson, template)
  
  return modifications
}
```

### 4.4 差异对比

#### 功能要求
- ✅ 并排显示原模板和当前教案
- ✅ 高亮显示差异部分
- ✅ 支持逐项对比
- ✅ 显示修改统计

#### UI 设计
```
┌──────────────────────────────────────────────────────────┐
│ 与模板对比                                      [×]       │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  📊 修改摘要                                             │
│     ✓ 新增 2 个单元                                      │
│     ✓ 修改 3 个单元                                      │
│     ✓ 删除 1 个单元                                      │
│     ✓ 调整了顺序                                         │
│                                                           │
│  📋 详细对比                                             │
│  ┌────────────────────┬────────────────────┐            │
│  │  原模板 (v1.2.0)   │  我的教案          │            │
│  ├────────────────────┼────────────────────┤            │
│  │ [文本] 课程导入    │ [文本] 课程导入    │ 无变化     │
│  ├────────────────────┼────────────────────┤            │
│  │ [文本] 集合定义    │ [文本] 集合定义    │ 🔵 已修改  │
│  │ 集合是...          │ 集合是...          │            │
│  │                    │ + 增加了本地化案例 │            │
│  ├────────────────────┼────────────────────┤            │
│  │ [代码] Python演示  │ [代码] Python演示  │ 🔵 已修改  │
│  │ set1 = {1,2,3}     │ students = {...}   │            │
│  ├────────────────────┼────────────────────┤            │
│  │                    │ [问答] 课堂小测    │ ➕ 新增    │
│  ├────────────────────┼────────────────────┤            │
│  │ [仿真] 维恩图      │                    │ ➖ 已删除  │
│  └────────────────────┴────────────────────┘            │
│                                                           │
├──────────────────────────────────────────────────────────┤
│              [还原为模板]  [保留修改]  [关闭]            │
└──────────────────────────────────────────────────────────┘
```

### 4.5 模板更新同步

#### 功能要求
- ✅ 检测模板是否有新版本
- ✅ 提示教师同步更新
- ✅ 智能合并（保留教师的个性化修改）
- ✅ 冲突解决机制

#### 更新检测
```typescript
// 检查模板更新
async function checkTemplateUpdate(lesson: Lesson) {
  if (!lesson.template_id) return null
  
  const currentTemplate = await fetchTemplate(lesson.template_id)
  
  if (currentTemplate.version > lesson.template_version) {
    return {
      hasUpdate: true,
      currentVersion: lesson.template_version,
      latestVersion: currentTemplate.version,
      changeLog: currentTemplate.changeLog
    }
  }
  
  return null
}
```

#### 智能合并策略
```typescript
async function syncTemplateUpdate(
  lesson: Lesson,
  template: LessonTemplate,
  strategy: 'auto' | 'manual'
) {
  if (strategy === 'auto') {
    // 自动合并：保留教师修改，添加模板新增内容
    const mergedContent = []
    
    // 1. 保留教师新增的 Cell
    const teacherAddedCells = lesson.content.filter(
      c => !c._metadata?.fromTemplate
    )
    
    // 2. 更新来自模板且未修改的 Cell
    lesson.content.forEach(cell => {
      if (cell._metadata?.fromTemplate && !cell._metadata?.isModified) {
        const updatedCell = findCellInTemplate(template, cell._metadata.originalCellId)
        if (updatedCell) {
          mergedContent.push(updatedCell)
        }
      } else {
        mergedContent.push(cell)
      }
    })
    
    // 3. 添加模板新增的 Cell
    const newCells = template.content.filter(
      c => !findCellInLesson(lesson, c.id)
    )
    mergedContent.push(...newCells)
    
    return mergedContent
  } else {
    // 手动合并：显示冲突解决界面
    return showMergeConflictDialog(lesson, template)
  }
}
```

---

## 五、技术实现

### 5.1 前端组件结构

```typescript
// 新增/修改的组件

// 1. 教案模板列表组件
<LessonTemplateList
  :resource-id="resourceId"
  @select="handleTemplateSelect"
/>

// 2. 模板详情对话框
<TemplateDetailModal
  :template-id="templateId"
  @create-lesson="handleCreateFromTemplate"
  @preview="handlePreview"
/>

// 3. 基于模板创建教案对话框（增强版CreateLessonModal）
<CreateLessonModal
  :course-id="courseId"
  :template-id="templateId"  // 可选
  @create="handleCreate"
/>

// 4. 模板差异对比组件
<TemplateDiffViewer
  :lesson="currentLesson"
  :template-id="templateId"
  @restore="handleRestore"
/>

// 5. 模板更新提示组件
<TemplateUpdateAlert
  :lesson="currentLesson"
  @sync="handleSync"
  @dismiss="handleDismiss"
/>
```

### 5.2 前端服务层

```typescript
// frontend/src/services/template.ts

export const templateService = {
  // 获取资源的模板列表
  async getTemplatesByResource(resourceId: number) {
    const response = await api.get(`/resources/${resourceId}/templates`)
    return response.data
  },
  
  // 获取模板详情
  async getTemplate(templateId: number) {
    const response = await api.get(`/templates/${templateId}`)
    return response.data
  },
  
  // 基于模板创建教案
  async createLessonFromTemplate(data: CreateFromTemplateRequest) {
    const response = await api.post('/lessons/from-template', data)
    return response.data
  },
  
  // 检查模板更新
  async checkTemplateUpdate(lessonId: number) {
    const response = await api.get(`/lessons/${lessonId}/check-template-update`)
    return response.data
  },
  
  // 同步模板更新
  async syncTemplateUpdate(lessonId: number, strategy: 'auto' | 'manual') {
    const response = await api.post(`/lessons/${lessonId}/sync-template`, { strategy })
    return response.data
  },
  
  // 对比差异
  async compareLessonWithTemplate(lessonId: number) {
    const response = await api.get(`/lessons/${lessonId}/compare-template`)
    return response.data
  }
}
```

### 5.3 后端 API 路由

```python
# backend/app/api/v1/templates.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List

router = APIRouter()

@router.get("/resources/{resource_id}/templates")
async def get_resource_templates(
    resource_id: int,
    difficulty: Optional[str] = None,
    sort_by: str = "rating",
    current_user: User = Depends(get_current_user)
) -> List[LessonTemplateResponse]:
    """获取资源的教案模板列表"""
    templates = await template_service.get_by_resource(
        resource_id,
        difficulty=difficulty,
        sort_by=sort_by
    )
    return templates

@router.get("/templates/{template_id}")
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_user)
) -> LessonTemplateDetail:
    """获取模板详情"""
    template = await template_service.get_by_id(template_id)
    if not template:
        raise HTTPException(404, "Template not found")
    return template

@router.post("/lessons/from-template")
async def create_lesson_from_template(
    data: CreateFromTemplateRequest,
    current_user: User = Depends(get_current_teacher)
) -> LessonResponse:
    """基于模板创建教案"""
    lesson = await lesson_service.create_from_template(
        template_id=data.template_id,
        course_id=data.course_id,
        teacher_id=current_user.id,
        customization=data
    )
    return lesson

@router.get("/lessons/{lesson_id}/check-template-update")
async def check_template_update(
    lesson_id: int,
    current_user: User = Depends(get_current_teacher)
) -> TemplateUpdateInfo:
    """检查模板是否有更新"""
    lesson = await lesson_service.get_by_id(lesson_id)
    if lesson.teacher_id != current_user.id:
        raise HTTPException(403, "Not authorized")
    
    update_info = await template_service.check_update(lesson)
    return update_info

@router.post("/lessons/{lesson_id}/sync-template")
async def sync_template_update(
    lesson_id: int,
    strategy: SyncStrategy,
    current_user: User = Depends(get_current_teacher)
) -> LessonResponse:
    """同步模板更新"""
    lesson = await lesson_service.sync_template(
        lesson_id,
        strategy=strategy.strategy
    )
    return lesson

@router.get("/lessons/{lesson_id}/compare-template")
async def compare_with_template(
    lesson_id: int,
    current_user: User = Depends(get_current_teacher)
) -> DiffResult:
    """对比教案与模板的差异"""
    lesson = await lesson_service.get_by_id(lesson_id)
    if not lesson.template_id:
        raise HTTPException(400, "Lesson not based on template")
    
    diff = await template_service.compare(lesson)
    return diff
```

### 5.4 数据库迁移

```python
# backend/alembic/versions/002_add_lesson_templates.py

def upgrade():
    # 创建模板表
    op.create_table(
        'lesson_templates',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('resource_id', sa.Integer(), sa.ForeignKey('resources.id')),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('version', sa.String(20), nullable=False),
        sa.Column('difficulty', sa.String(20)),
        sa.Column('estimated_duration', sa.Integer()),
        sa.Column('tags', sa.JSON()),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('is_official', sa.Boolean(), default=False),
        sa.Column('usage_count', sa.Integer(), default=0),
        sa.Column('rating', sa.Float(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    # 为 lessons 表添加模板关联字段
    op.add_column('lessons', sa.Column('template_id', sa.Integer(), sa.ForeignKey('lesson_templates.id')))
    op.add_column('lessons', sa.Column('template_version', sa.String(20)))
    op.add_column('lessons', sa.Column('is_modified', sa.Boolean(), default=False))
    op.add_column('lessons', sa.Column('modification_summary', sa.Text()))
    
    # 创建修改日志表
    op.create_table(
        'lesson_modification_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('lesson_id', sa.Integer(), sa.ForeignKey('lessons.id')),
        sa.Column('teacher_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('modification_type', sa.String(50)),
        sa.Column('cell_id', sa.String(100)),
        sa.Column('changes', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
```

---

## 六、用户故事

### 故事1：新教师快速创建教案

**角色：** 李老师（新入职教师）

**场景：**
1. 李老师登录系统，需要准备"集合的概念"这节课
2. 在课程结构中找到"高一数学 → 第一章 → 1.1 集合的概念"
3. 看到有2个官方教案模板可用
4. 点击查看模板详情，发现"基础版"模板很合适
5. 点击"基于此模板创建我的教案"
6. 修改标题为"集合的概念 - 高一(1)班"
7. 系统自动创建教案，包含了模板的所有内容
8. 李老师根据班级情况，修改了其中的代码示例
9. 添加了一个针对本班学生的课堂小测
10. 保存并发布教案

**价值：** 李老师在30分钟内完成备课，而不是从零开始花费2小时

### 故事2：经验教师个性化改进

**角色：** 王老师（资深教师）

**场景：**
1. 王老师看到官方模板不错，但想加入自己的教学经验
2. 基于模板创建教案后，进行大量个性化修改：
   - 重新编写了导入部分
   - 添加了3个实战案例
   - 删除了一个不适合的仿真单元
   - 调整了教学顺序
3. 系统自动标记"已修改"
4. 期中后，官方更新了模板到 v1.3.0
5. 系统提示："模板有更新，是否同步？"
6. 王老师选择"智能合并"：
   - 保留自己的个性化修改
   - 添加模板新增的优质内容
7. 解决少量冲突后，完成更新

**价值：** 既享受模板的便利，又保持个性化，还能持续改进

### 故事3：教研组协作

**角色：** 数学教研组

**场景：**
1. 教研组长创建了一个精品教案作为模板
2. 将教案提交为"教研组模板"
3. 组内5位老师都基于此模板创建自己的教案
4. 每位老师根据不同班级特点进行调整
5. 期末总结时，对比各版本的差异
6. 提炼最佳实践，更新模板到 v2.0
7. 所有老师收到更新提示，选择性同步

**价值：** 促进教研协作，知识共享，持续改进

---

## 七、实施计划

### 阶段1：基础功能（MVP）
**目标：** 实现基本的模板创建和使用

- [ ] 数据库模型和迁移
- [ ] 模板 CRUD API
- [ ] 基于模板创建教案
- [ ] 模板列表和详情展示
- [ ] 修改 CreateLessonModal 支持模板选择

**时间：** 1周

### 阶段2：修改跟踪
**目标：** 跟踪教师的个性化修改

- [ ] Cell 元数据系统
- [ ] 修改检测逻辑
- [ ] 修改标记UI
- [ ] 修改日志记录

**时间：** 1周

### 阶段3：差异对比
**目标：** 可视化对比教案与模板

- [ ] 差异对比算法
- [ ] 并排对比UI
- [ ] 修改摘要生成
- [ ] 还原功能

**时间：** 1周

### 阶段4：更新同步
**目标：** 智能同步模板更新

- [ ] 版本检测机制
- [ ] 更新提示UI
- [ ] 智能合并算法
- [ ] 冲突解决界面

**时间：** 1.5周

### 阶段5：优化和增强
**目标：** 用户体验优化

- [ ] 模板评分和评论
- [ ] 模板搜索和筛选
- [ ] 使用统计和分析
- [ ] 性能优化

**时间：** 1周

**总计：** 5.5周

---

## 八、总结

### 核心价值
1. **提高效率：** 教师不需要从零开始，基于优质模板快速创建
2. **保证质量：** 标准模板确保教学内容的完整性和规范性
3. **鼓励创新：** 教师可以自由修改，添加个性化内容
4. **持续改进：** 模板可以迭代更新，教师可以同步最新版本
5. **促进协作：** 优秀教案可以沉淀为模板，实现知识共享

### 设计原则
- **灵活性：** 支持从模板创建，也支持从空白创建
- **可追溯：** 记录模板来源和修改历史
- **非侵入：** 不影响现有的教案创建流程
- **用户友好：** 简化操作流程，智能化合并

### 下一步
1. 与教师用户访谈，验证需求
2. 设计详细的UI原型
3. 实施阶段1，获取早期反馈
4. 迭代优化

---

**文档版本：** v1.0  
**最后更新：** 2025-10-17

