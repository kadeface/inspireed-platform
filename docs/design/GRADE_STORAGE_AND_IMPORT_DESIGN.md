# 成绩存储方式与外部导入功能设计

## 📋 目录

1. [存储方式选择分析](#存储方式选择分析)
2. [期末统考成绩导入功能设计](#期末统考成绩导入功能设计)
3. [数据模型扩展](#数据模型扩展)
4. [API设计](#api设计)
5. [前端界面设计](#前端界面设计)
6. [实施建议](#实施建议)

---

## 📊 存储方式选择分析

### 问题描述

学生成绩的存储方式有两种选择：

1. **宽存储（Wide Format）**：一个学生一次考试的所有科目成绩作为一个记录
2. **短存储（Long Format）**：一个科目一个记录

### 方案对比

#### 方案一：宽存储

**数据结构示例**：
```sql
CREATE TABLE exam_scores_wide (
    id SERIAL PRIMARY KEY,
    student_id INTEGER,
    exam_id VARCHAR(100),
    exam_name VARCHAR(200),
    chinese_score FLOAT,
    math_score FLOAT,
    english_score FLOAT,
    physics_score FLOAT,
    chemistry_score FLOAT,
    -- ... 更多科目
    created_at TIMESTAMP
);
```

**优点**：
- ✅ 一次考试一条记录，查询一次考试的所有成绩更快
- ✅ 数据更紧凑，存储空间相对较小

**缺点**：
- ❌ **不够灵活**：科目数量变化时需要修改表结构
- ❌ **不符合数据库范式**：难以扩展和维护
- ❌ **大量NULL字段**：不同考试包含不同科目时会造成大量NULL
- ❌ **难以支持动态科目**：无法支持不同学校、不同年级的科目差异
- ❌ **查询复杂**：查询单个科目成绩需要指定列名
- ❌ **统计困难**：跨科目统计需要复杂的SQL

#### 方案二：短存储（推荐）

**数据结构示例**：
```sql
CREATE TABLE grade_records (
    id SERIAL PRIMARY KEY,
    student_id INTEGER,
    course_id INTEGER,
    exam_id VARCHAR(100),  -- 关联同一考试的不同科目
    exam_name VARCHAR(200),
    score FLOAT,
    max_score FLOAT,
    created_at TIMESTAMP
);
```

**优点**：
- ✅ **高度灵活**：易于扩展新科目，无需修改表结构
- ✅ **符合数据库范式**：数据规范化，易于维护
- ✅ **支持动态科目**：不同考试可以包含不同科目
- ✅ **查询简单**：查询单个科目或所有科目都很简单
- ✅ **统计方便**：跨科目统计使用标准SQL即可
- ✅ **易于扩展**：可以轻松添加新字段（如等级、排名等）

**缺点**：
- ⚠️ 一次考试需要多条记录（但可以通过`exam_id`关联）
- ⚠️ 存储空间略大（但现代数据库优化后差异可忽略）

### 最终决策：短存储 + 考试关联字段

**推荐采用短存储方式**，并在`GradeRecord`模型中增加`exam_id`和`exam_name`字段用于关联同一考试的不同科目成绩。

**设计理由**：
1. **灵活性优先**：教育系统中科目配置经常变化，短存储更适应这种变化
2. **扩展性**：未来可能需要支持更多成绩类型和属性
3. **查询性能**：通过`exam_id`索引可以快速查询一次考试的所有成绩
4. **标准化**：符合数据库设计最佳实践

### 数据示例

**期末统考成绩存储示例**：

```
考试信息：
- exam_id: "final_exam_2024_2025_1"
- exam_name: "2024-2025学年第一学期期末统考"

学生张三（student_id=1）的成绩记录：
记录1: {student_id=1, course_id=1(语文), exam_id="final_exam_2024_2025_1", score=85, max_score=100}
记录2: {student_id=1, course_id=2(数学), exam_id="final_exam_2024_2025_1", score=90, max_score=100}
记录3: {student_id=1, course_id=3(英语), exam_id="final_exam_2024_2025_1", score=88, max_score=100}
```

**查询一次考试的所有成绩**：
```sql
SELECT * FROM grade_records 
WHERE exam_id = 'final_exam_2024_2025_1' AND student_id = 1;
```

**查询一次考试所有学生的某个科目成绩**：
```sql
SELECT * FROM grade_records 
WHERE exam_id = 'final_exam_2024_2025_1' AND course_id = 1;
```

---

## 📥 期末统考成绩导入功能设计

### 功能需求

1. **支持批量导入**：一次导入多个学生的多个科目成绩
2. **数据格式支持**：Excel、CSV、JSON
3. **数据校验**：学生ID、课程ID、成绩范围等
4. **错误处理**：详细的错误报告和警告
5. **导入预览**：导入前预览数据
6. **考试关联**：自动或手动设置exam_id
7. **重复处理**：覆盖/跳过已存在的成绩

### 导入文件格式

#### Excel/CSV格式

**必需列**：
- `student_id` 或 `学号`：学生ID或学号
- `course_id` 或 `课程代码`：课程ID或课程代码
- `score` 或 `成绩`：实际得分
- `max_score` 或 `满分`：满分（可选，默认100）

**可选列**：
- `student_name` 或 `学生姓名`：用于验证
- `course_name` 或 `课程名称`：用于验证
- `exam_id` 或 `考试ID`：如果不提供，系统自动生成
- `exam_name` 或 `考试名称`：考试名称
- `remark` 或 `备注`：备注信息

**示例**：

| 学号 | 学生姓名 | 课程代码 | 课程名称 | 成绩 | 满分 | 考试ID | 考试名称 |
|------|---------|---------|---------|------|------|--------|---------|
| 2024001 | 张三 | MATH_001 | 数学 | 90 | 100 | final_2024_1 | 2024-2025学年第一学期期末统考 |
| 2024001 | 张三 | CHINESE_001 | 语文 | 85 | 100 | final_2024_1 | 2024-2025学年第一学期期末统考 |
| 2024002 | 李四 | MATH_001 | 数学 | 88 | 100 | final_2024_1 | 2024-2025学年第一学期期末统考 |

#### JSON格式

```json
{
  "exam_id": "final_exam_2024_2025_1",
  "exam_name": "2024-2025学年第一学期期末统考",
  "semester": "2024-2025-1",
  "category_id": 3,
  "records": [
    {
      "student_id": 1,
      "course_id": 1,
      "score": 85.0,
      "max_score": 100.0,
      "remark": "期末统考"
    },
    {
      "student_id": 1,
      "course_id": 2,
      "score": 90.0,
      "max_score": 100.0
    }
  ]
}
```

### 数据校验规则

1. **学生身份匹配**（详见`GRADE_STUDENT_IDENTIFICATION_DESIGN.md`）：
   - 支持多种学生标识方式：学号、姓名+年级、学生ID、身份证号
   - 自动匹配学生身份，支持历史学号匹配
   - 匹配置信度评估，低置信度需要人工确认
   - 匹配失败时提供详细错误信息

2. **学生ID校验**：
   - 学生必须存在
   - 学生必须是活跃状态
   - 如果通过学号匹配，需要验证学号的有效性

3. **课程ID校验**：
   - 课程必须存在
   - 课程必须与成绩产生时的年级匹配（使用`student_grade_id_at_time`）

4. **成绩范围校验**：
   - 成绩不能为负数
   - 成绩不能超过满分
   - 成绩不能为空

5. **重复数据校验**：
   - 检查是否已存在相同的成绩记录（student_id + course_id + exam_id + semester）
   - 根据`overwrite_existing`参数决定处理方式

6. **考试ID校验**：
   - 如果提供exam_id，检查格式是否正确
   - 如果不提供，自动生成（格式：`exam_{timestamp}_{category_id}`）

7. **年级快照记录**：
   - 自动记录成绩产生时的年级（`student_grade_id_at_time`）
   - 自动记录成绩产生时的学号（`student_number_at_time`）
   - 自动记录成绩产生时的班级（`student_classroom_id_at_time`）

### 导入流程

```
1. 文件上传
   ↓
2. 文件解析（Excel/CSV/JSON）
   ↓
3. 学生身份匹配
   ├─ 尝试多种匹配方式（学号、姓名+年级、学生ID等）
   ├─ 计算匹配置信度
   ├─ 标记需要确认的匹配
   └─ 记录匹配失败的行
   ↓
4. 数据校验
   ├─ 格式校验
   ├─ 业务规则校验
   ├─ 学生身份验证
   └─ 重复数据检查
   ↓
5. 预览模式（可选）
   ├─ 显示解析结果
   ├─ 显示匹配结果和置信度
   ├─ 显示需要确认的匹配
   ├─ 显示错误和警告
   └─ 用户确认或修正
   ↓
6. 批量创建成绩记录
   ├─ 使用匹配到的student_id
   ├─ 记录成绩产生时的年级快照
   ├─ 记录成绩产生时的学号快照
   ├─ 事务处理
   ├─ 错误收集
   └─ 成功统计
   ↓
7. 返回导入结果
   ├─ 成功数量
   ├─ 跳过数量
   ├─ 错误数量
   ├─ 匹配统计
   └─ 详细错误信息
```

---

## 🗄️ 数据模型扩展

### GradeRecord模型扩展

在原有`GradeRecord`模型基础上增加以下字段：

```python
class GradeRecord(Base):
    """成绩记录模型"""
    
    __tablename__ = "grade_records"
    
    # ... 原有字段 ...
    
    # 考试关联（用于关联同一考试的不同科目成绩）
    exam_id = Column(
        String(100), 
        nullable=True, 
        index=True, 
        comment="考试ID，用于关联同一考试的不同科目成绩"
    )
    exam_name = Column(
        String(200), 
        nullable=True, 
        comment="考试名称，如'2024-2025学年第一学期期末统考'"
    )
    
    # 导入来源信息（可选）
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

### 导入日志模型（可选）

```python
class GradeImportLog(Base):
    """成绩导入日志模型"""
    
    __tablename__ = "grade_import_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 导入信息
    import_batch_id = Column(String(100), nullable=False, unique=True, index=True)
    file_name = Column(String(200), nullable=True)
    file_type = Column(String(20), nullable=False)  # excel, csv, json
    
    # 导入配置
    exam_id = Column(String(100), nullable=True, index=True)
    exam_name = Column(String(200), nullable=True)
    category_id = Column(Integer, ForeignKey("grade_categories.id"), nullable=True)
    semester = Column(String(20), nullable=True)
    
    # 导入结果
    total_rows = Column(Integer, default=0, nullable=False)
    imported_count = Column(Integer, default=0, nullable=False)
    skipped_count = Column(Integer, default=0, nullable=False)
    error_count = Column(Integer, default=0, nullable=False)
    
    # 错误详情（JSON格式）
    errors_detail = Column(JSON, nullable=True, default=list)
    
    # 操作信息
    imported_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    imported_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关联关系
    importer = relationship("User", foreign_keys=[imported_by])
    category = relationship("GradeCategory")
```

---

## 🔌 API设计

### 1. 导入成绩（支持预览模式）

```python
POST /api/v1/grades/records/import
Content-Type: multipart/form-data

Parameters:
- file: File (必需) - Excel/CSV/JSON文件
- preview: bool (可选, 默认false) - 是否仅预览，不实际导入
- exam_id: str (可选) - 考试ID，如果不提供则自动生成
- exam_name: str (可选) - 考试名称
- category_id: int (可选) - 成绩类别ID
- semester: str (可选) - 学期
- overwrite_existing: bool (可选, 默认false) - 是否覆盖已存在的成绩
- skip_errors: bool (可选, 默认true) - 遇到错误时是否跳过继续导入
```

**响应示例**：
```json
{
    "success": true,
    "preview": false,
    "total_rows": 120,
    "imported": 115,
    "skipped": 3,
    "errors": 2,
    "exam_id": "final_exam_2024_2025_1",
    "import_batch_id": "batch_20250102_123456",
    "errors_detail": [
        {
            "row": 5,
            "student_id": "2024005",
            "course_id": "MATH_001",
            "error": "学生不存在",
            "error_code": "STUDENT_NOT_FOUND"
        },
        {
            "row": 12,
            "student_id": "2024012",
            "course_id": "CHINESE_001",
            "error": "成绩超出范围：150（满分100）",
            "error_code": "SCORE_OUT_OF_RANGE"
        }
    ],
    "warnings": [
        {
            "row": 8,
            "message": "成绩已存在，已跳过（如需覆盖请设置overwrite_existing=true）",
            "warning_code": "RECORD_EXISTS"
        }
    ]
}
```

### 2. 按考试ID查询成绩

```python
GET /api/v1/grades/records/by-exam/{exam_id}?student_id={student_id}&course_id={course_id}
```

**查询参数**：
- `student_id` (可选) - 筛选特定学生
- `course_id` (可选) - 筛选特定课程
- `classroom_id` (可选) - 筛选特定班级

**响应示例**：
```json
{
    "exam_id": "final_exam_2024_2025_1",
    "exam_name": "2024-2025学年第一学期期末统考",
    "total_students": 40,
    "total_courses": 5,
    "records": [
        {
            "id": 1001,
            "student_id": 1,
            "student_name": "张三",
            "course_id": 1,
            "course_name": "语文",
            "score": 85.0,
            "max_score": 100.0,
            "percentage": 0.85,
            "rank_in_course": 15
        },
        {
            "id": 1002,
            "student_id": 1,
            "student_name": "张三",
            "course_id": 2,
            "course_name": "数学",
            "score": 90.0,
            "max_score": 100.0,
            "percentage": 0.90,
            "rank_in_course": 8
        }
    ],
    "statistics": {
        "average_score": 87.5,
        "total_score": 175.0,
        "rank_in_class": 5
    }
}
```

### 3. 下载导入模板

```python
GET /api/v1/grades/records/import/template?format=excel|csv
```

返回Excel或CSV格式的导入模板文件。

### 4. 查询导入历史

```python
GET /api/v1/grades/import-logs?page=1&page_size=20&exam_id={exam_id}
```

---

## 🎨 前端界面设计

### 导入页面组件结构

```
GradeImportModal.vue
├── 文件上传区域
│   ├── 文件选择
│   ├── 拖拽上传
│   └── 模板下载按钮
├── 导入配置区域
│   ├── 考试信息设置
│   │   ├── 考试ID（自动生成/手动输入）
│   │   └── 考试名称
│   ├── 成绩类别选择
│   ├── 学期选择
│   └── 导入选项
│       ├── 覆盖已存在成绩
│       └── 遇到错误时跳过
├── 数据预览区域（预览模式）
│   ├── 数据表格
│   ├── 校验状态显示
│   └── 错误/警告提示
└── 导入结果区域
    ├── 统计信息
    ├── 成功列表
    ├── 错误列表
    └── 警告列表
```

### 交互流程

1. **文件上传**：
   - 支持拖拽上传
   - 支持点击选择文件
   - 文件格式验证（Excel、CSV、JSON）

2. **数据预览**（可选）：
   - 自动解析文件
   - 显示解析后的数据表格
   - 高亮显示错误和警告
   - 显示数据统计信息

3. **配置导入选项**：
   - 设置考试信息
   - 选择成绩类别
   - 配置导入选项

4. **执行导入**：
   - 显示导入进度
   - 实时更新导入状态
   - 显示成功/失败统计

5. **查看结果**：
   - 显示导入结果摘要
   - 详细错误列表
   - 支持导出错误报告

---

## 💡 实施建议

### 阶段一：数据模型扩展（1周）

1. 在`GradeRecord`模型中增加`exam_id`和`exam_name`字段
2. 创建`GradeImportLog`模型（可选）
3. 编写数据库迁移脚本
4. 更新相关索引

### 阶段二：后端API开发（2周）

1. 实现文件解析功能（Excel、CSV、JSON）
2. 实现数据校验逻辑
3. 实现批量导入API
4. 实现导入预览API
5. 实现按考试ID查询API
6. 编写单元测试

### 阶段三：前端界面开发（2周）

1. 创建导入页面组件
2. 实现文件上传功能
3. 实现数据预览功能
4. 实现导入配置表单
5. 实现导入结果展示
6. 实现错误处理

### 阶段四：测试与优化（1周）

1. 功能测试
2. 性能测试（大数据量导入）
3. 错误处理测试
4. 用户体验优化

### 技术栈建议

- **文件解析**：
  - Excel: `openpyxl` 或 `pandas`
  - CSV: `pandas` 或标准库 `csv`
  - JSON: 标准库 `json`

- **数据校验**：
  - 使用Pydantic进行数据验证
  - 自定义验证器处理业务规则

- **批量操作**：
  - 使用SQLAlchemy的`bulk_insert_mappings`提高性能
  - 使用事务确保数据一致性

---

## 📝 总结

1. **存储方式**：推荐采用**短存储**（一个科目一个记录），通过`exam_id`字段关联同一考试的不同科目成绩，既保持了灵活性又支持关联查询。

2. **导入功能**：需要增加**期末统考成绩导入功能**，支持Excel/CSV/JSON格式，包含数据校验、错误处理和导入预览等功能。

3. **学生身份匹配**：支持多种学生标识方式（学号、姓名+年级、学生ID等），自动匹配学生身份，支持历史学号匹配，提供置信度评估机制。

4. **年级和学号变化处理**：通过快照机制记录成绩产生时的年级和学号信息，确保历史成绩的准确性和可追溯性。

5. **扩展性**：设计考虑了未来可能的需求变化，如支持更多成绩类型、更多导入来源等。

### 相关设计文档

- **成绩管理系统总体设计**：`docs/design/GRADE_MANAGEMENT_SYSTEM_DESIGN.md`
- **学生身份识别与年级变化处理设计**：`docs/design/GRADE_STUDENT_IDENTIFICATION_DESIGN.md`

该设计方案为成绩管理系统的实施提供了清晰的指导，可以根据实际需求分阶段实施。
