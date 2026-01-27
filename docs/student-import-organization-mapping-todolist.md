# 考生信息导入与组织架构关联实施计划

## 任务概览

本计划包含20个任务，分为5个阶段实施。

## 阶段一：数据模型和基础服务（任务1-4）

### 任务1：数据模型增强
**文件**：`backend/app/models/organization.py`

**内容**：
- 在 `Region` 模型中添加：
  - `created_from_import: Boolean = False`
  - `import_source: Optional[String(200)] = None`
- 在 `School` 模型中添加：
  - `created_from_import: Boolean = False`
  - `import_source: Optional[String(200)] = None`

**依赖**：无

**验收标准**：
- 模型字段添加成功
- 数据库迁移文件创建成功

---

### 任务2：创建组织架构匹配服务
**文件**：`backend/app/services/organization_mapping_service.py`（新建）

**内容**：
创建服务类 `OrganizationMappingService`，包含以下方法框架：
- `find_or_create_region()`
- `find_or_create_school()`
- `generate_region_code()`
- `generate_school_code()`
- `infer_region_level()`
- `infer_school_type()`

**依赖**：任务1

**验收标准**：
- 服务类创建成功
- 所有方法签名定义完成

---

### 任务3：实现区域匹配逻辑
**文件**：`backend/app/services/organization_mapping_service.py`

**内容**：
实现 `find_or_create_region()` 方法：
1. **精确匹配**：按 `name` 精确匹配
2. **模糊匹配**：按 `name` 使用 `ilike` 模糊匹配
3. **自动创建**：
   - 调用 `generate_region_code()` 生成唯一code
   - 调用 `infer_region_level()` 推断level（根据名称中的"省"、"市"、"区"等）
   - 设置 `created_from_import=True`
   - 设置 `import_source` 为导入来源标识

**辅助方法**：
- `generate_region_code(region_name: str) -> str`：生成唯一区域编码
  - 规则：使用拼音首字母+时间戳，或使用名称hash
- `infer_region_level(region_name: str) -> int`：推断区域级别
  - 包含"省" → level=1
  - 包含"市" → level=2
  - 包含"区"/"县" → level=3
  - 默认 → level=3

**依赖**：任务2

**验收标准**：
- 精确匹配功能正常
- 模糊匹配功能正常
- 自动创建功能正常
- code唯一性保证
- 单元测试通过

---

### 任务4：实现学校匹配逻辑
**文件**：`backend/app/services/organization_mapping_service.py`

**内容**：
实现 `find_or_create_school()` 方法：
1. **按学校代码精确匹配**：如果提供了 `school_code`，优先按code匹配
2. **按名称+区域匹配**：按 `name` + `region_id` 精确匹配
3. **自动创建**：
   - 使用提供的 `school_code`，或调用 `generate_school_code()` 生成
   - 调用 `infer_school_type()` 推断学校类型
   - 设置 `created_from_import=True`
   - 设置 `import_source`

**辅助方法**：
- `generate_school_code(school_name: str, region_id: int) -> str`：生成唯一学校编码
  - 规则：`{region_code}_{school_name_hash}` 或使用时间戳
- `infer_school_type(grade_name: Optional[str] = None) -> str`：推断学校类型
  - 根据年级名称推断：
    - 包含"一"到"六"年级 → "小学"
    - 包含"初一"到"初三"或"七"到"九"年级 → "初中"
    - 包含"高一"到"高三"或"十"到"十二"年级 → "高中"
    - 默认 → "高中"

**依赖**：任务2, 任务3

**验收标准**：
- 按代码匹配功能正常
- 按名称+区域匹配功能正常
- 自动创建功能正常
- code唯一性保证
- school_type推断准确
- 单元测试通过

---

## 阶段二：考生信息导入服务（任务5-9）

### 任务5：创建考生信息导入服务
**文件**：`backend/app/services/student_import_service.py`（新建）

**内容**：
创建服务类 `StudentImportService`，包含：
- `parse_student_excel()`：解析Excel文件
- `validate_student_data()`：验证学生数据
- `import_students()`：执行导入

**依赖**：任务4

**验收标准**：
- 服务类创建成功
- 方法框架定义完成

---

### 任务6：实现Excel解析
**文件**：`backend/app/services/student_import_service.py`

**内容**：
实现 `parse_student_excel()` 方法：
- 支持列名映射：
  - `市(区)` → `region_name`
  - `学校` → `school_name`
  - `姓名` → `full_name`
  - `身份证号` → `id_number`
  - `考生号` → `exam_number`
  - `学校代码` → `school_code`（可选）
  - `班级` → `classroom_code`（如501、1001）
- 解析每一行数据为字典
- 返回记录列表和错误列表

**依赖**：任务5

**验收标准**：
- 能正确解析所有必需字段
- 能处理可选字段
- 能识别格式错误
- 单元测试通过

---

### 任务7：实现班级匹配/创建逻辑
**文件**：`backend/app/services/student_import_service.py`

**内容**：
实现 `find_or_create_classroom()` 方法：
1. **解析班级编号**：
   - 501 → 5年级1班
   - 1001 → 高一1班
   - 解析规则：
     - 3位数：前1位=年级，后2位=班级号
     - 4位数：前2位=年级（10=高一，11=高二，12=高三），后2位=班级号
2. **匹配年级**：根据班级编号推断年级，查找Grade
3. **匹配班级**：按 `school_id` + `grade_id` + 班级名称匹配
4. **创建班级**：如果不存在，创建新班级

**依赖**：任务5, 任务6

**验收标准**：
- 班级编号解析正确
- 年级匹配准确
- 班级匹配/创建功能正常
- 单元测试通过

---

### 任务8：实现学生用户匹配/创建
**文件**：`backend/app/services/student_import_service.py`

**内容**：
实现 `find_or_create_student()` 方法：
1. **匹配用户**：按 `student_id_number`（身份证号）精确匹配
2. **创建用户**：如果不存在：
   - 创建User记录
   - 设置 `role=STUDENT`
   - 关联 `region_id`, `school_id`, `grade_id`, `classroom_id`
   - 生成默认 `username` 和 `email`
   - 设置默认密码（或要求后续激活）
3. **更新用户**：如果存在，更新组织架构关联

**依赖**：任务5, 任务7

**验收标准**：
- 用户匹配功能正常
- 用户创建功能正常
- 组织架构关联正确
- 单元测试通过

---

### 任务9：实现考号映射创建
**文件**：`backend/app/services/student_import_service.py`

**内容**：
实现 `create_exam_number_mapping()` 方法：
- 创建 `ExamNumberMapping` 记录
- 关联 `exam_id`, `student_id`, `exam_number`
- 设置冗余字段：`student_id_number`, `school_id`, `classroom_id`
- 处理重复考号的情况（更新或报错）

**依赖**：任务5, 任务8

**验收标准**：
- 考号映射创建成功
- 重复考号处理正确
- 单元测试通过

---

## 阶段三：API集成（任务10-13）

### 任务10：创建API Schema
**文件**：`backend/app/schemas/evaluation.py`

**内容**：
添加以下Schema：
```python
class StudentImportItem(BaseModel):
    """考生信息导入项"""
    region_name: str
    school_name: str
    school_code: Optional[str] = None
    full_name: str
    id_number: str
    exam_number: str
    classroom_code: str

class StudentImportRequest(BaseModel):
    """考生信息导入请求"""
    exam_id: int
    students: List[StudentImportItem]
    auto_create_org: bool = True

class StudentImportResponse(BaseModel):
    """考生信息导入响应"""
    total: int
    success: int
    failed: int
    created_regions: int
    created_schools: int
    created_classrooms: int
    created_students: int
    errors: List[str]
```

**依赖**：任务9

**验收标准**：
- Schema定义完整
- 类型检查通过

---

### 任务11：创建考生信息导入API
**文件**：`backend/app/api/v1/exams.py`

**内容**：
添加API端点：
```python
@router.post("/exams/{exam_id}/students/import")
async def import_exam_students(
    exam_id: int,
    file: UploadFile,
    auto_create_org: bool = Query(True),
    preview_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> StudentImportResponse:
```

**依赖**：任务10

**验收标准**：
- API端点创建成功
- 路由注册成功

---

### 任务12：实现导入API逻辑
**文件**：`backend/app/api/v1/exams.py`

**内容**：
实现导入逻辑：
1. 验证考试存在
2. 验证文件格式
3. 调用 `StudentImportService.parse_student_excel()` 解析
4. 调用 `OrganizationMappingService` 匹配/创建组织架构
5. 调用 `StudentImportService` 导入学生和考号映射
6. 事务处理：确保所有操作在同一事务中
7. 错误处理：收集所有错误，返回详细报告
8. 返回导入结果

**依赖**：任务11

**验收标准**：
- 导入功能正常
- 错误处理完善
- 事务处理正确
- 集成测试通过

---

### 任务13：添加导入预览功能（可选）
**文件**：`backend/app/api/v1/exams.py`

**内容**：
实现预览功能：
- 如果 `preview_only=True`，只解析和匹配，不实际创建
- 返回将要创建的组织架构统计：
  - 将要创建的区域列表
  - 将要创建的学校列表
  - 将要创建的班级列表
  - 将要创建/更新的学生数量

**依赖**：任务12

**验收标准**：
- 预览功能正常
- 统计数据准确

---

## 阶段四：数据库迁移和测试（任务14-17）

### 任务14：数据库迁移
**文件**：`backend/alembic/versions/XXXX_add_import_fields_to_org.py`（新建）

**内容**：
创建Alembic迁移文件：
- 在 `regions` 表添加 `created_from_import` 和 `import_source` 字段
- 在 `schools` 表添加 `created_from_import` 和 `import_source` 字段

**依赖**：任务1

**验收标准**：
- 迁移文件创建成功
- 迁移可以正常执行和回滚

---

### 任务15：组织架构匹配服务单元测试
**文件**：`backend/tests/test_organization_mapping_service.py`（新建）

**内容**：
编写测试用例：
- 测试区域精确匹配
- 测试区域模糊匹配
- 测试区域自动创建
- 测试学校代码匹配
- 测试学校名称+区域匹配
- 测试学校自动创建
- 测试code唯一性保证

**依赖**：任务4

**验收标准**：
- 所有测试用例通过
- 测试覆盖率 > 80%

---

### 任务16：考生信息导入服务单元测试
**文件**：`backend/tests/test_student_import_service.py`（新建）

**内容**：
编写测试用例：
- 测试Excel解析
- 测试数据验证
- 测试班级编号解析
- 测试学生匹配/创建
- 测试考号映射创建

**依赖**：任务9

**验收标准**：
- 所有测试用例通过
- 测试覆盖率 > 80%

---

### 任务17：集成测试
**文件**：`backend/tests/test_student_import_integration.py`（新建）

**内容**：
编写集成测试：
- 测试完整导入流程
- 测试组织架构自动创建
- 测试错误处理
- 测试事务回滚

**依赖**：任务12

**验收标准**：
- 所有集成测试通过
- 覆盖主要场景

---

## 阶段五：优化和完善（任务18-20）

### 任务18：错误处理优化
**文件**：`backend/app/services/student_import_service.py`

**内容**：
优化错误信息：
- 包含行号
- 包含字段名
- 包含具体错误原因
- 提供修复建议

**依赖**：任务12

**验收标准**：
- 错误信息清晰明确
- 便于用户定位问题

---

### 任务19：事务处理优化
**文件**：`backend/app/services/student_import_service.py`

**内容**：
确保事务一致性：
- Region → School → Classroom → User → ExamNumberMapping
- 任何一步失败，整个事务回滚
- 使用数据库事务管理

**依赖**：任务12

**验收标准**：
- 事务处理正确
- 数据一致性保证

---

### 任务20：日志记录
**文件**：`backend/app/services/organization_mapping_service.py`

**内容**：
添加日志记录：
- 记录所有自动创建的区域
- 记录所有自动创建的学校
- 记录导入来源信息
- 便于后续审核和清理

**依赖**：任务4

**验收标准**：
- 日志记录完整
- 便于审计追踪

---

## 实施顺序建议

### 第一周：阶段一 + 阶段二（任务1-9）
- 完成数据模型和基础服务
- 完成考生信息导入服务核心功能

### 第二周：阶段三 + 阶段四（任务10-17）
- 完成API集成
- 完成数据库迁移
- 完成测试

### 第三周：阶段五（任务18-20）
- 优化和完善
- 文档更新

## 关键依赖关系

```
任务1 → 任务2 → 任务3 → 任务4
                ↓
任务5 → 任务6 → 任务7 → 任务8 → 任务9
                ↓
任务10 → 任务11 → 任务12 → 任务13
                ↓
任务14 → 任务15 → 任务16 → 任务17
                ↓
任务18 → 任务19 → 任务20
```

## 验收标准总结

1. **功能完整性**：所有核心功能实现完成
2. **数据准确性**：组织架构匹配准确，数据创建正确
3. **错误处理**：错误信息清晰，异常情况处理完善
4. **测试覆盖**：单元测试和集成测试覆盖主要场景
5. **代码质量**：代码规范，注释完整，可维护性强
