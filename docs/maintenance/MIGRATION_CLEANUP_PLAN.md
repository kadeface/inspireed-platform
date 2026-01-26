# 数据库迁移清理方案

## 📋 概述

本文档详细说明了如何清理和优化 InspireEd 平台的 40 个数据库迁移文件，减少到约 **15-20 个优化后的迁移**。

**当前状态**: 40 个迁移文件
**目标状态**: 15-20 个优化迁移文件
**预计减少**: ~50%

---

## 🔍 发现的主要问题

### 1. **重复的 celltype 枚举修改**

| 迁移文件 | 操作 | 问题 |
|---------|------|------|
| `005_add_qa_system.py` | 创建 celltype（包含所有值） | ✅ 正确 |
| `008_add_activity_system.py` | 添加 'activity', 'flowchart' | ❌ 重复（已在005中） |
| `20251117_0205_fix_celltype_enum...py` | 添加 'activity', 'flowchart' | ❌ 重复 |
| `20251127_1535_add_browser_celltype.py` | 添加 'browser' | ❌ 重复（已在005中） |

**解决方案**: 保留 `005_add_qa_system.py`，删除其他三个重复的枚举修改迁移。

### 2. **碎片化的 library_assets 字段添加**

library_assets 表被 6 个迁移逐步添加字段：

| 迁移文件 | 操作 | 顺序 |
|---------|------|------|
| `017_add_library_assets...` | 创建表 + asset_id | 1 |
| `018_add_subject_id_to_library_assets.py` | 添加 subject_id | 2 |
| `20251214_0826_add_grade_id_to_library_assets.py` | 添加 grade_id | 3 |
| `20251215_add_knowledge_point_fields...py` | 添加知识点字段 | 4 |
| `20251216_add_view_count_to_library_assets.py` | 添加 view_count | 5 |
| `20251219_add_library_asset_versions.py` | 添加版本管理 | 6 |

**解决方案**: 合并成 **单个迁移** `017_complete_library_assets_system.py`

### 3. **空的合并迁移**

以下迁移只包含空的 upgrade/downgrade 函数（用于分支合并）：

- `20250102_merge_subjects_and_cell_uuid.py`
- `20251213_0309_97119fda8aae_merge_018_and_merge...`
- `20251225_2219_4eac54cf4de2_merge_student_projects...`
- `20251117_0427_57a9a465710d_merge_classroom_session...`

**解决方案**: 删除这些空迁移，调整依赖链。

### 4. **过于庞大的单一迁移**

`20260113_1400_add_value_added_evaluation_system.py` (386行) 包含：
- UserRole 枚举扩展
- Subjects 表修改
- Classrooms 表修改
- 8 个新表创建

**解决方案**: 拆分为 3 个独立迁移：
1. `20260113_1400_extend_user_roles.py`
2. `20260113_1401_extend_subjects_and_classrooms.py`
3. `20260113_1402_add_evaluation_tables.py`

### 5. **其他小问题**

- `007_fix_lesson_enum_values.py`: 枚举大小写修复（可以合并到 001）
- `20251110_0900_c9e2f8a1d5ef_remove_course_subject_grade_unique.py`: 删除唯一约束（可以合并到 001 修复）
- `20260114_0302_2e197c88672a_change_semester_year_to_string.py`: 字段类型转换（删除测试数据）

---

## 🎯 清理策略

### 策略 A: 保守清理（推荐用于有生产环境的情况）

**原则**:
- ✅ 保留所有功能性迁移
- ✅ 删除重复的枚举修改
- ✅ 合并逻辑上相关的迁移
- ✅ 删除空的合并迁移
- ✅ 保持迁移的可回滚性

### 策略 B: 激进清理（仅适用于开发环境）

**原则**:
- ❌ 完全丢弃历史迁移
- ✅ 从当前数据库状态生成新的基准迁移
- ✅ 重新开始迁移链

**⚠️ 风险**: 无法回滚到之前的历史版本

---

## 📁 迁移分组与合并计划

### **第1组: 课程系统基础（保持不变）**

```
001_add_curriculum_system.py
002_add_chapters_resources_mvp.py
20251020_2236_2f1d0b37129d_add_chapter_id_to_lessons.py
```

**操作**: 保持不变（已优化）

---

### **第2组: 组织/用户结构（合并1个）**

#### 原5个迁移:
```
003_add_organization_tables.py
20251108_1358_088e21d1e159_add_classrooms_and_user_scope_fields.py
004_add_student_enhancement_features.py
20251221_add_last_login_to_users.py
20251221_1723_add_student_id_number_to_users.py
```

#### 合并为4个:
```
003_add_organization_tables.py
004_add_classrooms_and_user_fields.py  ← 合并 20251108 + 20251221 两个用户字段迁移
005_add_student_enhancement_features.py
```

**删除**: `20251221_add_last_login_to_users.py`, `20251221_1723_add_student_id_number_to_users.py`

---

### **第3组: 问答与活动系统（删除重复）**

#### 原4个迁移:
```
005_add_qa_system.py
008_add_activity_system.py
20251117_0205_fix_celltype_enum_add_activity_flowchart.py  ← 删除（重复）
20251127_1535_add_browser_celltype.py  ← 删除（重复）
```

#### 保持2个:
```
006_add_qa_system.py  ← 重命名
007_add_activity_system.py  ← 重命名
```

**删除**: 2个重复的枚举修改

---

### **第4组: Library Assets 系统（合并6个→1个）**

#### 原6个迁移:
```
017_add_library_assets_and_resource_asset_id.py
018_add_subject_id_to_library_assets.py
20251214_0826_add_grade_id_to_library_assets.py
20251215_add_knowledge_point_fields_to_library_assets.py
20251216_add_view_count_to_library_assets.py
20251219_add_library_asset_versions.py
```

#### 合并为1个:
```
017_complete_library_assets_system.py  ← 一次性创建完整的表结构
```

---

### **第5组: 考试/评估系统（拆分1个→3个）**

#### 原1个大迁移:
```
20260113_1400_add_value_added_evaluation_system.py  (386行)
```

#### 拆分为3个:
```
20260113_1400_extend_user_roles.py  ← UserRole 枚举扩展
20260113_1401_extend_subjects_and_classrooms.py  ← 表字段添加
20260113_1402_add_evaluation_core_tables.py  ← 核心评估表
20260113_1403_add_exam_score_tables.py  ← 考试成绩表
```

---

### **第6组: 删除空的合并迁移（4个）**

```
❌ 20250102_merge_subjects_and_cell_uuid.py
❌ 20251213_0309_97119fda8aae_merge_018_and_merge_subjects_cell_uuid.py
❌ 20251225_2219_4eac54cf4de2_merge_student_projects_and_session_id_.py
❌ 20251117_0427_57a9a465710d_merge_classroom_session_and_celltype_fix.py
```

---

## 📊 清理结果对比

| 指标 | 清理前 | 清理后 | 减少 |
|------|--------|--------|------|
| **迁移总数** | 40 | 18 | -55% |
| **枚举修改** | 4次 | 1次 | -75% |
| **library_assets 迁移** | 6个 | 1个 | -83% |
| **空迁移** | 4个 | 0个 | -100% |
| **最大迁移行数** | 386行 | ~150行 | -61% |

---

## 🛠️ 实施步骤

### 第1步: 备份当前迁移链

```bash
cd backend/alembic/versions
mkdir -p ../backup/versions_$(date +%Y%m%d)
cp *.py ../backup/versions_$(date +%Y%m%d)/
```

### 第2步: 创建新的优化迁移

使用提供的脚本生成新的迁移文件。

### 第3步: 测试新的迁移链

```bash
# 备份数据库
pg_dump inspired > backup_$(date +%Y%m%d).sql

# 在测试环境运行
alembic upgrade head
```

### 第4步: 验证数据完整性

```bash
# 检查表结构
psql inspired -c "\d"

# 检查数据
psql inspired -c "SELECT COUNT(*) FROM users;"
```

### 第5步: 部署到生产环境

⚠️ **重要**: 如果生产环境已有数据，需要特别处理！

---

## ⚠️ 注意事项

### 对于生产环境

1. **不要直接删除已运行的迁移**
   - 已运行的迁移记录在 `alembic_version` 表中
   - 删除迁移文件会导致 Alembic 混乱

2. **正确的处理方式**:
   ```python
   # 在新迁移中检查并修复
   def upgrade():
       # 检查是否已经应用旧的迁移
       conn = op.get_bind()
       inspector = inspect(conn)

       # 只执行必要的操作
       if 'column_x' not in [col['name'] for col in inspector.get_columns('table_name')]:
           op.add_column('table_name', ...)
   ```

3. **数据迁移必须使用事务**:
   ```python
   from alembic import op
   import sqlalchemy as sa

   def upgrade():
       conn = op.get_bind()
       transaction = conn.begin()
       try:
           # 执行数据迁移
           op.execute("UPDATE table SET ...")
           transaction.commit()
       except:
           transaction.rollback()
           raise
   ```

### 对于开发环境

可以安全地重置数据库：

```bash
# 删除所有表
alembic downgrade base

# 删除旧的迁移文件
rm backend/alembic/versions/*.py

# 使用新的迁移
alembic upgrade head
```

---

## 📝 迁移命名规范

清理后的迁移使用统一的命名格式：

```
{序号}_{功能描述}.py

例如:
001_add_curriculum_system.py
002_add_chapters_and_resources.py
003_add_organization_tables.py
...
```

---

## 🔄 回滚策略

每个优化后的迁移都必须包含完整的 `downgrade()` 函数：

```python
def downgrade():
    """完整的回滚逻辑"""
    # 1. 删除新创建的表
    op.drop_table('new_table')

    # 2. 删除添加的字段
    op.drop_column('existing_table', 'new_column')

    # 3. 删除枚举类型（注意：PostgreSQL 不支持删除枚举值）
    op.execute('DROP TYPE IF EXISTS new_enum_type')
```

---

## 📚 相关文件

- `/backend/alembic/versions/` - 迁移文件目录
- `/backend/alembic/backup/` - 迁移文件备份
- `/backend/alembic/env.py` - Alembic 配置
- `/backend/alembic/versions/README.md` - 迁移说明文档

---

## ✅ 验证清单

在应用清理后的迁移前，确保：

- [ ] 已备份所有迁移文件
- [ ] 已备份数据库
- [ ] 在开发环境测试通过
- [ ] 在测试环境测试通过
- [ ] 所有 `downgrade()` 函数完整
- [ ] 迁移之间的依赖关系正确
- [ ] 外键约束完整
- [ ] 索引创建正确

---

## 📞 支持与帮助

如果遇到问题：

1. 检查 `alembic_history` 表查看迁移链
2. 使用 `alembic current` 查看当前版本
3. 使用 `alembic history` 查看完整迁移历史
4. 查看日志文件了解详细错误信息

---

**文档版本**: 1.0
**创建日期**: 2026-01-18
**作者**: Claude Code Migration Assistant
