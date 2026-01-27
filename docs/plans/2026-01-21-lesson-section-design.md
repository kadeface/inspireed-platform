# 教案大环节（Section）功能设计文档

## 1. 概述

### 1.1 功能目标
在现有教案的 Cell（模块）层级之上，增加一个"大环节"（Section）层级，使教案结构更加清晰和规范。

### 1.2 核心需求
- **5个默认大环节**：
  1. 教学目标、教学重点难点、学生学情分析
  2. 教学过程
  3. 课堂练习
  4. 课程资源
  5. 反思总结
- **支持自定义大环节**：用户可以添加、删除、重命名自定义大环节
- **每个大环节可以有多个 Cell**
- **支持拖拽排序**：大环节之间、Cell 之间都可以拖拽排序
- **支持跨大环节移动 Cell**：可以将 Cell 从一个大环节拖拽到另一个大环节
- **数据迁移**：现有教案的所有 Cell 自动归到默认的"教学过程"大环节

## 2. 数据结构设计

### 2.1 数据模型选择

**方案A：新增 Section 表（推荐）**
- 优点：数据结构规范，便于查询和统计
- 缺点：需要数据库迁移，修改现有代码较多

**方案B：在 Lesson.content 中存储结构化数据**
- 优点：向后兼容性好，无需数据库迁移
- 缺点：查询和统计不够方便

**最终选择：方案A** - 虽然需要更多工作，但长期维护性更好。

### 2.2 数据库模型

#### Section 表
```python
class Section(Base):
    __tablename__ = "sections"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)  # 大环节名称
    type = Column(String(50), nullable=False)  # 'default' | 'custom'
    order = Column(Integer, default=0, nullable=False)  # 排序顺序
    is_collapsed = Column(Boolean, default=False)  # 是否折叠（前端状态）
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    lesson = relationship("Lesson", back_populates="sections")
    cells = relationship("Cell", back_populates="section", cascade="all, delete-orphan", order_by="Cell.order")
```

#### Cell 表修改
```python
# 在 Cell 表中新增字段
section_id = Column(Integer, ForeignKey("sections.id"), nullable=True, index=True)
# 注意：nullable=True 是为了兼容现有数据，迁移后应改为 nullable=False
```

#### Lesson 表修改
```python
# 在 Lesson 模型中新增关联
sections = relationship("Section", back_populates="lesson", cascade="all, delete-orphan", order_by="Section.order")
```

### 2.3 默认大环节定义

```python
DEFAULT_SECTIONS = [
    {"name": "教学目标、教学重点难点、学生学情分析", "type": "default", "order": 0},
    {"name": "教学过程", "type": "default", "order": 1},
    {"name": "课堂练习", "type": "default", "order": 2},
    {"name": "课程资源", "type": "default", "order": 3},
    {"name": "反思总结", "type": "default", "order": 4},
]
```

### 2.4 前端数据结构

```typescript
// frontend/src/types/section.ts
export interface Section {
  id: number | string  // 支持字符串ID（新建时）
  lesson_id: number
  name: string
  type: 'default' | 'custom'
  order: number
  is_collapsed?: boolean
  cells: Cell[]
  created_at?: string
  updated_at?: string
}

// Lesson 接口修改
export interface Lesson {
  // ... 其他字段
  sections?: Section[]  // 新增：大环节列表
  content?: Cell[]     // 保留：向后兼容，但优先使用 sections
}
```

## 3. API 设计

### 3.1 Section 管理 API

```
POST   /api/v1/lessons/{lesson_id}/sections          # 创建大环节
GET    /api/v1/lessons/{lesson_id}/sections          # 获取大环节列表
GET    /api/v1/sections/{section_id}                 # 获取大环节详情
PUT    /api/v1/sections/{section_id}                 # 更新大环节
DELETE /api/v1/sections/{section_id}                # 删除大环节
POST   /api/v1/sections/{section_id}/move            # 移动大环节（调整顺序）
POST   /api/v1/cells/{cell_id}/move                  # 移动 Cell 到指定大环节
```

### 3.2 数据迁移 API

```
POST   /api/v1/lessons/{lesson_id}/migrate-sections  # 将现有 Cell 迁移到默认大环节
```

## 4. 前端界面设计

### 4.1 LessonEditor 组件结构

```
LessonEditor
├── 顶部工具栏（保持不变）
├── 左侧 Cell 工具箱（保持不变）
└── 中间编辑区
    ├── Section 列表
    │   ├── Section 1（可折叠）
    │   │   ├── Section 标题栏（名称、操作按钮）
    │   │   └── Cell 列表（可拖拽）
    │   ├── Section 2
    │   └── ...
    └── 添加大环节按钮
```

### 4.2 Section 组件设计

**SectionHeader.vue** - 大环节标题栏
- 显示大环节名称
- 折叠/展开按钮
- 编辑名称按钮
- 删除按钮（仅自定义大环节）
- 拖拽手柄

**SectionContainer.vue** - 大环节容器
- 包含 SectionHeader 和 Cell 列表
- 支持拖拽排序
- 支持折叠/展开

### 4.3 交互设计

1. **添加大环节**：
   - 点击"添加大环节"按钮
   - 弹出对话框输入名称
   - 创建后插入到列表末尾

2. **编辑大环节名称**：
   - 点击编辑按钮
   - 内联编辑或弹出对话框

3. **删除大环节**：
   - 仅自定义大环节可删除
   - 删除前确认，并处理其中的 Cell（移动到其他大环节或删除）

4. **拖拽排序**：
   - 使用 SortableJS 实现
   - 支持大环节之间拖拽
   - 支持 Cell 在大环节内拖拽
   - 支持 Cell 跨大环节拖拽

5. **折叠/展开**：
   - 点击折叠按钮，收起/展开该大环节的 Cell 列表
   - 状态保存在前端（is_collapsed），可选同步到后端

## 5. 数据迁移策略

### 5.1 迁移时机
- 在用户首次打开已有教案时自动迁移
- 或提供手动迁移按钮

### 5.2 迁移逻辑
```python
def migrate_lesson_to_sections(lesson_id: int):
    """
    将现有教案的 Cell 迁移到默认大环节结构
    """
    lesson = get_lesson(lesson_id)
    
    # 1. 检查是否已迁移（已有 sections）
    if lesson.sections:
        return
    
    # 2. 创建默认大环节
    default_section = create_section(
        lesson_id=lesson_id,
        name="教学过程",
        type="default",
        order=1
    )
    
    # 3. 将所有现有 Cell 关联到"教学过程"大环节
    cells = get_cells_by_lesson(lesson_id)
    for cell in cells:
        cell.section_id = default_section.id
        update_cell(cell)
    
    # 4. 创建其他默认大环节（空）
    for section_data in DEFAULT_SECTIONS:
        if section_data["name"] != "教学过程":
            create_section(
                lesson_id=lesson_id,
                name=section_data["name"],
                type=section_data["type"],
                order=section_data["order"]
            )
```

## 6. 实施计划

### 阶段一：后端数据模型（Week 1）
- [ ] 创建 Section 模型
- [ ] 修改 Cell 模型（添加 section_id）
- [ ] 数据库迁移脚本
- [ ] 创建 Section API
- [ ] 数据迁移 API

### 阶段二：前端基础功能（Week 2）
- [ ] 定义 Section 类型
- [ ] 修改 LessonEditor 组件结构
- [ ] 实现 Section 列表展示
- [ ] 实现 Section 折叠/展开

### 阶段三：Section 管理功能（Week 2-3）
- [ ] 添加大环节功能
- [ ] 编辑大环节名称
- [ ] 删除大环节功能
- [ ] 大环节拖拽排序

### 阶段四：Cell 跨大环节拖拽（Week 3）
- [ ] 实现 Cell 在大环节内拖拽
- [ ] 实现 Cell 跨大环节拖拽
- [ ] 优化拖拽体验

### 阶段五：数据迁移和测试（Week 4）
- [ ] 实现数据迁移逻辑
- [ ] 测试现有教案迁移
- [ ] 集成测试
- [ ] 用户验收测试

## 7. 技术要点

### 7.1 拖拽实现
- 使用 SortableJS 库（项目已使用）
- 配置 `group` 选项支持跨容器拖拽
- 处理拖拽事件，更新 Cell 的 section_id 和 order

### 7.2 性能优化
- 大环节折叠时，不渲染 Cell 组件（使用 v-if）
- 使用虚拟滚动（如果 Cell 数量很多）
- 批量更新 API（拖拽后批量保存）

### 7.3 向后兼容
- 前端优先使用 `sections`，如果没有则使用 `content`
- 后端 API 同时返回 `sections` 和 `content`（兼容旧版本）

## 8. 成功指标

- ✅ 所有现有教案可以正常迁移
- ✅ 支持 5 个默认大环节 + 自定义大环节
- ✅ 拖拽功能流畅，无卡顿
- ✅ 数据保存正确
- ✅ 用户体验良好，操作直观

---

**文档版本**：v1.0  
**创建日期**：2026-01-21  
**维护者**：InspireEd 开发团队
