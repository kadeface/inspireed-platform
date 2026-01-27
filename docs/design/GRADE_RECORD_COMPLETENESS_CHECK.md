# 学生成绩存储设计完整性检查

## 📋 检查清单

### ✅ 已完成的字段和功能

#### 1. 学生身份标识
- ✅ `student_id` - 系统内部ID（稳定）
- ✅ `student_registration_number` - 学籍号（全国唯一，永久不变）
- ✅ `student_grade_id_at_time` - 成绩产生时的年级快照
- ✅ `student_classroom_id_at_time` - 成绩产生时的班级快照
- ✅ `student_number_at_time` - 成绩产生时的学号快照

#### 2. 课程和班级信息
- ✅ `course_id` - 课程ID
- ✅ `classroom_id` - 班级ID（当前）
- ✅ `semester` - 学期

#### 3. 成绩类别和项目
- ✅ `category_id` - 成绩类别ID
- ✅ `item_id` - 具体项目ID（可选）
- ✅ `item_name` - 具体项目名称（可选）

#### 4. 考试关联
- ✅ `exam_id` - 考试ID（用于关联同一考试的不同科目成绩）
- ✅ `exam_name` - 考试名称

#### 5. 成绩数据
- ✅ `score` - 实际得分
- ✅ `max_score` - 满分
- ✅ `percentage` - 百分比得分（自动计算）

#### 6. 数据来源
- ✅ `source_type` - 数据来源类型（manual/activity/auto）
- ✅ `source_id` - 来源ID（如ActivitySubmission.id）

#### 7. 状态管理
- ✅ `status` - 成绩状态（draft/confirmed/locked）

#### 8. 审核和追溯
- ✅ `recorded_by` - 录入人
- ✅ `recorded_at` - 录入时间
- ✅ `reviewed_by` - 审核人（可选）
- ✅ `reviewed_at` - 审核时间（可选）
- ✅ `remark` - 备注

#### 9. 时间戳
- ✅ `created_at` - 创建时间
- ✅ `updated_at` - 更新时间

#### 10. 导入追踪（建议补充）
- ⚠️ `import_batch_id` - 导入批次ID（用于追踪同一批导入的记录）
- ⚠️ `import_source` - 导入来源（excel/csv/json/api）

---

## 🔍 需要补充的字段

### 1. 导入追踪字段（建议添加）

```python
# 导入来源信息（可选，用于追踪导入记录）
import_batch_id = Column(
    String(100), 
    nullable=True, 
    index=True, 
    comment="导入批次ID，用于追踪同一批导入的记录"
)
import_source = Column(
    String(50), 
    nullable=True, 
    comment="导入来源：excel, csv, json, api"
)
```

**用途**：
- 批量导入时可以追踪哪些记录是同一批导入的
- 如果导入有问题，可以批量回滚
- 便于统计和分析导入数据

### 2. 成绩等级字段（可选，建议添加）

```python
# 成绩等级（可选，根据成绩自动计算或手动设置）
grade_level = Column(
    String(10), 
    nullable=True, 
    index=True,
    comment="成绩等级：A+, A, B+, B, C+, C, D, F 或 优秀/良好/及格/不及格"
)
```

**用途**：
- 支持等级制成绩
- 便于统计和分析
- 符合某些学校的成绩管理习惯

### 3. 是否计入总评字段（可选）

```python
# 是否计入总评成绩
is_included_in_total = Column(
    Boolean, 
    default=True, 
    nullable=False,
    comment="是否计入总评成绩（某些成绩可能不计入总评）"
)
```

**用途**：
- 某些成绩可能不计入总评（如补考成绩、重修成绩等）
- 提供更灵活的成绩管理

### 4. 成绩有效期字段（可选，特殊场景）

```python
# 成绩有效期（可选，用于某些特殊场景）
valid_from = Column(
    DateTime, 
    nullable=True,
    comment="成绩生效时间"
)
valid_to = Column(
    DateTime, 
    nullable=True,
    comment="成绩失效时间（NULL表示永久有效）"
)
```

**用途**：
- 某些成绩可能有有效期（如某些认证考试）
- 支持成绩的时效性管理

---

## 📊 索引和约束检查

### 已定义的索引

✅ `idx_grade_student_course` - (student_id, course_id)
✅ `idx_grade_classroom_semester` - (classroom_id, semester)
✅ 各字段的单独索引（student_id, course_id, classroom_id, semester, category_id等）

### 建议补充的索引

1. **学籍号索引**（如果使用学籍号查询）
   ```python
   Index("idx_grade_registration_number", "student_registration_number")
   ```

2. **考试ID索引**（如果经常按考试查询）
   ```python
   Index("idx_grade_exam", "exam_id", "student_id")
   ```

3. **学期+年级索引**（如果经常按学期和年级查询）
   ```python
   Index("idx_grade_semester_grade", "semester", "student_grade_id_at_time")
   ```

4. **状态索引**（如果经常按状态筛选）
   ```python
   Index("idx_grade_status", "status", "recorded_at")
   ```

### 唯一性约束

✅ `uq_grade_record` - (student_id, course_id, classroom_id, semester, category_id, item_id)

**注意**：这个唯一性约束可能需要调整，因为：
- 如果允许同一学生同一课程同一类别有多个成绩（如多次考试），需要包含`exam_id`或`item_id`
- 如果`item_id`可以为NULL，唯一性约束可能需要调整

**建议的唯一性约束**：
```python
__table_args__ = (
    # 方案1：如果item_id不为空，使用item_id区分
    UniqueConstraint(
        "student_id", "course_id", "classroom_id", "semester", 
        "category_id", "item_id", 
        name="uq_grade_record"
    ),
    # 方案2：如果允许同一类别多个成绩，使用exam_id区分
    UniqueConstraint(
        "student_id", "course_id", "classroom_id", "semester", 
        "category_id", "exam_id", 
        name="uq_grade_record_exam"
    ),
)
```

---

## 🔒 数据完整性检查

### 1. 外键约束

✅ 所有外键都已定义：
- `student_id` → `users.id`
- `course_id` → `courses.id`
- `classroom_id` → `classrooms.id`
- `category_id` → `grade_categories.id`
- `student_grade_id_at_time` → `grades.id`
- `student_classroom_id_at_time` → `classrooms.id`
- `recorded_by` → `users.id`
- `reviewed_by` → `users.id`

### 2. 数据校验规则

✅ 成绩范围校验（score >= 0, score <= max_score）
✅ 百分比自动计算（percentage = score / max_score）
✅ 状态枚举校验（draft/confirmed/locked）
✅ 来源类型枚举校验（manual/activity/auto）

### 3. 业务规则校验

⚠️ **需要补充的业务规则**：

1. **成绩不能为负数**
   ```python
   @validates("score")
   def validate_score(self, key, value):
       if value < 0:
           raise ValueError("成绩不能为负数")
       return value
   ```

2. **成绩不能超过满分**
   ```python
   @validates("score", "max_score")
   def validate_score_range(self, key, value):
       if key == "score" and hasattr(self, "max_score") and self.max_score:
           if value > self.max_score:
               raise ValueError("成绩不能超过满分")
       return value
   ```

3. **百分比自动计算**
   ```python
   @property
   def percentage(self):
       if self.max_score and self.max_score > 0:
           return self.score / self.max_score
       return None
   ```

---

## 🚀 性能优化建议

### 1. 分区策略（大数据量场景）

如果成绩记录数量很大（百万级以上），可以考虑按学期分区：

```python
# PostgreSQL分区表示例
__table_args__ = (
    {
        'postgresql_partition_by': 'RANGE (semester)'
    },
)
```

### 2. 归档策略

对于历史成绩（如3年以上的成绩），可以考虑：
- 归档到历史表
- 使用冷热数据分离
- 定期清理草稿状态的旧记录

### 3. 缓存策略

- 缓存成绩汇总数据（GradeSummary）
- 缓存统计数据（GradeStatistics）
- 使用Redis缓存热点查询

---

## 📝 总结

### 已完成的核心功能

✅ **学生身份管理**：支持学籍号、学号、年级快照等
✅ **成绩数据存储**：完整的成绩字段和计算逻辑
✅ **数据来源追踪**：支持手动、自动、活动等多种来源
✅ **状态管理**：草稿、确认、锁定等状态流转
✅ **审核追溯**：完整的审核和变更历史
✅ **考试关联**：支持期末统考等批量成绩管理

### 建议补充的内容

1. **导入追踪字段**：`import_batch_id`、`import_source`
2. **成绩等级字段**：`grade_level`（可选）
3. **是否计入总评**：`is_included_in_total`（可选）
4. **补充索引**：学籍号、考试ID等常用查询字段
5. **数据校验**：在模型层面增加验证器
6. **唯一性约束优化**：根据业务需求调整唯一性约束

### 整体评估

**学生成绩存储设计已经比较完善**，涵盖了：
- ✅ 学生身份识别（学籍号优先）
- ✅ 年级和学号变化处理（快照机制）
- ✅ 多种数据来源支持
- ✅ 完整的审核和追溯机制
- ✅ 考试关联和批量导入支持

**建议优先补充**：
1. 导入追踪字段（便于问题排查和数据管理）
2. 数据校验规则（保证数据质量）
3. 索引优化（提升查询性能）

其他可选字段可以根据实际业务需求逐步添加。
