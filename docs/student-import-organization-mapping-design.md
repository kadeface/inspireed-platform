# 考生信息导入与组织架构关联方案设计

## 问题分析

在导入考生信息时，Excel中包含：
- **市(区)** - 需要匹配或创建 Region
- **学校** - 需要匹配或创建 School（必须关联 Region）
- **学校代码** - 可选，可用于精确匹配

现有组织架构约束：
- `Region.code` 必须唯一
- `School.code` 必须唯一
- `School.region_id` 必须存在（外键约束）
- `School.school_type` 必填（小学/初中/高中等）

## 方案对比

### 方案1：完全自动创建（不推荐）

**实现方式**：
- 导入时自动创建不存在的 Region 和 School

**优点**：
- 操作简单，无需预先维护

**缺点**：
- ❌ 数据质量不可控（可能创建重复、不规范数据）
- ❌ Region.code 自动生成困难（需要唯一性）
- ❌ School.school_type 无法从Excel推断
- ❌ 可能产生大量脏数据，后续清理困难
- ❌ 违反数据治理原则

### 方案2：预检查+拒绝导入（保守方案）

**实现方式**：
- 导入前验证所有 Region 和 School 必须存在
- 不存在则拒绝导入，提示用户先创建

**优点**：
- ✅ 数据质量可控
- ✅ 实现简单

**缺点**：
- ❌ 用户体验差，需要额外步骤
- ❌ 批量导入时效率低

### 方案3：智能匹配+自动创建（推荐⭐）

**实现方式**：
1. **匹配阶段**：
   - 优先按 `学校代码` 精确匹配 School
   - 其次按 `学校名称` + `区域名称` 模糊匹配
   - 按 `市(区)名称` 匹配 Region（支持模糊匹配）

2. **创建阶段**（匹配失败时）：
   - 自动创建 Region（如果不存在）
   - 自动创建 School（如果不存在）
   - 创建的数据标记为 `is_active=True`，但添加 `created_from_import=True` 标记

3. **数据验证**：
   - 学校代码自动生成规则：`{region_code}_{school_name_hash}` 或使用 Excel 中的学校代码
   - School.school_type 默认值：根据年级推断（如高一/高二/高三 → 高中）

**优点**：
- ✅ 平衡了便利性和数据质量
- ✅ 支持批量导入
- ✅ 可追溯数据来源

**缺点**：
- ⚠️ 需要处理匹配逻辑（名称相似度、去重等）
- ⚠️ 需要合理的默认值策略

### 方案4：交互式映射（最佳用户体验）

**实现方式**：
1. 导入时检测到不存在的 Region/School
2. 暂停导入，显示映射对话框
3. 用户选择：
   - 选择已存在的 Region/School
   - 或创建新的 Region/School（填写完整信息）
4. 保存映射关系，继续导入

**优点**：
- ✅ 数据最准确
- ✅ 用户可控
- ✅ 可复用映射关系

**缺点**：
- ⚠️ 实现复杂
- ⚠️ 批量导入时可能多次交互

## 推荐方案：方案3（智能匹配+自动创建）+ 方案4（可选交互式确认）

### 实现策略

#### 阶段1：基础实现（方案3）

```python
# 伪代码示例
async def find_or_create_region(
    db: AsyncSession,
    region_name: str,
    current_user: User
) -> Region:
    """查找或创建区域"""
    # 1. 精确匹配
    region = await db.execute(
        select(Region).where(Region.name == region_name)
    )
    if region := region.scalar_one_or_none():
        return region
    
    # 2. 模糊匹配（容错）
    region = await db.execute(
        select(Region).where(Region.name.ilike(f"%{region_name}%"))
    )
    if region := region.scalar_one_or_none():
        return region
    
    # 3. 自动创建
    # 生成唯一code：使用名称拼音首字母+时间戳
    region_code = generate_region_code(region_name)
    
    # 推断level：根据名称判断（省/市/区）
    level = infer_region_level(region_name)
    
    region = Region(
        name=region_name,
        code=region_code,
        level=level,
        is_active=True,
        created_from_import=True  # 标记来源
    )
    db.add(region)
    await db.flush()
    return region


async def find_or_create_school(
    db: AsyncSession,
    school_name: str,
    school_code: Optional[str],
    region_id: int,
    current_user: User
) -> School:
    """查找或创建学校"""
    # 1. 按学校代码精确匹配
    if school_code:
        school = await db.execute(
            select(School).where(School.code == school_code)
        )
        if school := school.scalar_one_or_none():
            return school
    
    # 2. 按名称+区域匹配
    school = await db.execute(
        select(School).where(
            School.name == school_name,
            School.region_id == region_id
        )
    )
    if school := school.scalar_one_or_none():
        return school
    
    # 3. 自动创建
    if not school_code:
        school_code = generate_school_code(school_name, region_id)
    
    school = School(
        name=school_name,
        code=school_code,
        region_id=region_id,
        school_type="高中",  # 默认值，或根据年级推断
        is_active=True,
        created_from_import=True
    )
    db.add(school)
    await db.flush()
    return school
```

#### 阶段2：增强功能（可选）

1. **导入前预览**：显示将要创建的新 Region/School 列表，用户确认
2. **导入后审核**：管理员可审核自动创建的数据，补充完整信息
3. **映射缓存**：保存名称映射关系，下次导入时自动使用

### 数据模型增强建议

```python
# 在 Region 和 School 模型中添加字段
class Region(Base):
    # ... 现有字段
    created_from_import = Column(Boolean, default=False, comment="是否由导入创建")
    import_source = Column(String(200), nullable=True, comment="导入来源标识")

class School(Base):
    # ... 现有字段
    created_from_import = Column(Boolean, default=False, comment="是否由导入创建")
    import_source = Column(String(200), nullable=True, comment="导入来源标识")
```

### API 设计

```python
@router.post("/exams/{exam_id}/students/import")
async def import_students(
    exam_id: int,
    file: UploadFile,
    auto_create_org: bool = True,  # 是否自动创建组织架构
    preview_only: bool = False,  # 仅预览，不实际导入
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """
    导入考生信息
    
    - auto_create_org: 是否自动创建不存在的 Region/School
    - preview_only: 仅预览将要创建的组织架构，不实际导入
    """
    # 1. 解析Excel
    # 2. 提取组织架构信息
    # 3. 匹配或创建 Region/School
    # 4. 导入学生数据
    # 5. 返回导入结果（包含创建的组织架构统计）
```

## 实施建议

### 优先级

1. **第一阶段**：实现方案3的基础功能
   - 智能匹配（精确+模糊）
   - 自动创建 Region/School
   - 添加 `created_from_import` 标记

2. **第二阶段**：增强用户体验
   - 导入前预览功能
   - 导入后审核功能
   - 映射关系缓存

3. **第三阶段**（可选）：交互式映射
   - 批量映射对话框
   - 映射关系管理界面

### 注意事项

1. **数据去重**：同一批导入中，相同名称的 Region/School 只创建一次
2. **事务处理**：确保 Region → School → Student 的创建在同一事务中
3. **错误处理**：创建失败时提供详细错误信息
4. **权限控制**：只有管理员可以自动创建组织架构
5. **日志记录**：记录所有自动创建的组织架构，便于审计

## 总结

**推荐采用方案3（智能匹配+自动创建）**，理由：
- 平衡了便利性和数据质量
- 实现复杂度适中
- 可扩展性强（后续可加入审核、映射等功能）
- 符合实际业务场景（批量导入时无法逐个确认）

**关键点**：
- 优先匹配，匹配不到再创建
- 创建的数据要有标记，便于后续审核和清理
- 提供合理的默认值策略
- 支持导入前预览（可选）
