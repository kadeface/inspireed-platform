# 学校批量导入功能实施计划

## 方案概述

在组织架构管理的**学校管理**页面中，增加**批量导入学校**功能。管理员可以：
1. 下载学校导入模板（Excel）
2. 填写学校信息（区域、学校名称、学校代码等）
3. 上传Excel文件批量导入
4. 系统自动匹配现有学校或创建新学校

**优势**：
- ✅ 数据治理更规范：先维护组织架构，再导入考生信息
- ✅ 职责清晰：组织架构管理独立于业务导入
- ✅ 可审核：导入前可预览，导入后可审核
- ✅ 可复用：导入的学校数据可在多个场景使用

## 任务列表（13个任务）

### 阶段一：后端服务层（任务1-5）

#### 任务1：创建学校导入Schema
**文件**：`backend/app/schemas/organization.py`（新建或扩展）

**内容**：
```python
class SchoolImportItem(BaseModel):
    """学校导入项"""
    region_name: str = Field(..., description="区域名称")
    school_name: str = Field(..., description="学校名称")
    school_code: Optional[str] = Field(None, description="学校代码（可选，用于精确匹配）")
    school_type: Optional[str] = Field(None, description="学校类型：小学/初中/高中/大学等")
    address: Optional[str] = Field(None, description="学校地址")
    phone: Optional[str] = Field(None, description="联系电话")
    email: Optional[str] = Field(None, description="邮箱")
    principal: Optional[str] = Field(None, description="校长姓名")

class SchoolImportRequest(BaseModel):
    """学校批量导入请求"""
    schools: List[SchoolImportItem]
    auto_create_region: bool = Field(True, description="是否自动创建不存在的区域")

class SchoolImportResponse(BaseModel):
    """学校批量导入响应"""
    total: int
    success: int
    failed: int
    created_regions: int
    created_schools: int
    updated_schools: int
    skipped_schools: int
    errors: List[Dict[str, Any]]  # {row: int, field: str, message: str}
```

**依赖**：无

**验收标准**：
- Schema定义完整
- 类型检查通过

---

#### 任务2：创建学校导入服务
**文件**：`backend/app/services/school_import_service.py`（新建）

**内容**：
创建服务类 `SchoolImportService`，包含方法框架：
- `parse_school_excel(file_path: str) -> List[Dict[str, Any]]`
- `find_or_create_region(db, region_name: str) -> Region`
- `find_or_create_school(db, school_data: dict, region_id: int) -> School`
- `import_schools(db, schools: List[Dict], auto_create_region: bool) -> Dict`

**依赖**：任务1

**验收标准**：
- 服务类创建成功
- 方法签名定义完成

---

#### 任务3：实现Excel解析
**文件**：`backend/app/services/school_import_service.py`

**内容**：
实现 `parse_school_excel()` 方法：
- 支持列名映射：
  - `区域名称` / `市(区)` → `region_name`
  - `学校名称` / `学校` → `school_name`
  - `学校代码` → `school_code`
  - `学校类型` → `school_type`
  - `地址` → `address`
  - `联系电话` / `电话` → `phone`
  - `邮箱` → `email`
  - `校长` / `校长姓名` → `principal`
- 必需字段：`region_name`, `school_name`
- 可选字段：其他字段
- 返回记录列表和错误列表

**依赖**：任务2

**验收标准**：
- 能正确解析所有字段
- 能识别格式错误
- 能处理空值和缺失字段
- 单元测试通过

---

#### 任务4：实现区域匹配逻辑
**文件**：`backend/app/services/school_import_service.py`

**内容**：
实现 `find_or_create_region()` 方法：
1. **精确匹配**：按 `name` 精确匹配
2. **模糊匹配**：按 `name` 使用 `ilike` 模糊匹配
3. **自动创建**（如果 `auto_create_region=True`）：
   - 生成唯一 `code`：使用名称拼音首字母+时间戳
   - 推断 `level`：根据名称中的"省"、"市"、"区"等
   - 设置默认值：`is_active=True`

**依赖**：任务2

**验收标准**：
- 精确匹配功能正常
- 模糊匹配功能正常
- 自动创建功能正常（可选）
- code唯一性保证
- 单元测试通过

---

#### 任务5：实现学校匹配逻辑
**文件**：`backend/app/services/school_import_service.py`

**内容**：
实现 `find_or_create_school()` 方法：
1. **按学校代码精确匹配**：如果提供了 `school_code`，优先按code匹配
2. **按名称+区域匹配**：按 `name` + `region_id` 精确匹配
3. **创建新学校**（匹配失败时）：
   - 使用提供的 `school_code`，或自动生成唯一code
   - 使用提供的 `school_type`，或根据其他信息推断
   - 设置其他可选字段
4. **更新现有学校**（匹配成功时，可选）：
   - 更新可选字段（如果提供了新值）

**依赖**：任务2, 任务4

**验收标准**：
- 按代码匹配功能正常
- 按名称+区域匹配功能正常
- 自动创建功能正常
- 更新功能正常（可选）
- code唯一性保证
- 单元测试通过

---

### 阶段二：API层（任务6-7）

#### 任务6：创建学校批量导入API
**文件**：`backend/app/api/v1/admin_organization.py`

**内容**：
添加API端点：
```python
@router.post("/schools/import", response_model=SchoolImportResponse)
async def import_schools(
    file: UploadFile = File(...),
    auto_create_region: bool = Query(True, description="是否自动创建不存在的区域"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """批量导入学校
    
    Excel格式要求：
    - 必需列：区域名称、学校名称
    - 可选列：学校代码、学校类型、地址、联系电话、邮箱、校长
    - 支持格式：.xlsx, .xls
    """
```

**依赖**：任务5

**验收标准**：
- API端点创建成功
- 路由注册成功
- 权限检查正确

---

#### 任务7：实现导入API逻辑
**文件**：`backend/app/api/v1/admin_organization.py`

**内容**：
实现导入逻辑：
1. 验证文件格式（.xlsx, .xls）
2. 保存文件到临时目录
3. 调用 `SchoolImportService.parse_school_excel()` 解析
4. 调用 `SchoolImportService.import_schools()` 导入
5. 事务处理：确保所有操作在同一事务中
6. 错误处理：收集所有错误，返回详细报告
7. 清理临时文件
8. 返回导入结果

**依赖**：任务6

**验收标准**：
- 导入功能正常
- 错误处理完善
- 事务处理正确
- 文件清理正确
- 集成测试通过

---

### 阶段三：前端界面（任务8-10）

#### 任务8：前端：在学校管理页面添加批量导入按钮
**文件**：`frontend/src/pages/Admin/Organization/SchoolManagement.vue`（需要查找实际文件路径）

**内容**：
- 在学校列表页面顶部添加"批量导入"按钮
- 点击后打开导入对话框

**依赖**：任务7

**验收标准**：
- 按钮显示正常
- 对话框可以打开

---

#### 任务9：前端：实现文件上传和导入进度
**文件**：`frontend/src/pages/Admin/Organization/SchoolImport.vue`（新建）或在学校管理页面中

**内容**：
- 文件上传组件（支持拖拽）
- 导入进度显示（进度条）
- 导入结果展示：
  - 成功/失败统计
  - 错误列表（行号、字段、错误信息）
  - 创建/更新的学校列表

**依赖**：任务8

**验收标准**：
- 文件上传功能正常
- 进度显示正常
- 结果展示清晰

---

#### 任务10：前端：添加导入模板下载功能
**文件**：`frontend/src/pages/Admin/Organization/SchoolImport.vue`

**内容**：
- 添加"下载模板"按钮
- 生成Excel模板文件
- 包含示例数据

**模板字段**：
- 区域名称*（必填）
- 学校名称*（必填）
- 学校代码（选填）
- 学校类型（选填：小学/初中/高中/大学）
- 地址（选填）
- 联系电话（选填）
- 邮箱（选填）
- 校长（选填）

**依赖**：任务8

**验收标准**：
- 模板下载功能正常
- 模板格式正确
- 示例数据合理

---

### 阶段四：考生信息导入简化（任务11）

#### 任务11：更新考生信息导入：移除自动创建学校逻辑
**文件**：`backend/app/services/student_import_service.py`（如果已存在）或相关导入服务

**内容**：
- 考生信息导入时，只匹配已存在的学校
- 如果学校不存在，返回明确的错误提示
- 提示用户先在学校管理中导入学校

**依赖**：任务7

**验收标准**：
- 只匹配已存在的学校
- 错误提示清晰
- 不影响现有功能

---

### 阶段五：测试（任务12-13）

#### 任务12：单元测试
**文件**：`backend/tests/test_school_import_service.py`（新建）

**内容**：
编写测试用例：
- 测试Excel解析
- 测试区域匹配/创建
- 测试学校匹配/创建
- 测试错误处理

**依赖**：任务5

**验收标准**：
- 所有测试用例通过
- 测试覆盖率 > 80%

---

#### 任务13：集成测试
**文件**：`backend/tests/test_school_import_integration.py`（新建）

**内容**：
编写集成测试：
- 测试完整导入流程
- 测试区域自动创建
- 测试学校匹配和创建
- 测试错误处理
- 测试事务回滚

**依赖**：任务7

**验收标准**：
- 所有集成测试通过
- 覆盖主要场景

---

## 实施顺序建议

### 第一周：后端服务（任务1-5）
- 完成Schema定义
- 完成服务层实现
- 完成Excel解析和匹配逻辑

### 第二周：API和前端（任务6-10）
- 完成API集成
- 完成前端界面
- 完成模板下载

### 第三周：简化和测试（任务11-13）
- 更新考生信息导入
- 完成测试

## 关键依赖关系

```
任务1 → 任务2 → 任务3 → 任务4 → 任务5
                ↓
任务6 → 任务7
                ↓
任务8 → 任务9 → 任务10
                ↓
任务11
                ↓
任务12 → 任务13
```

## Excel模板示例

| 区域名称* | 学校名称* | 学校代码 | 学校类型 | 地址 | 联系电话 | 邮箱 | 校长 |
|---------|---------|---------|---------|------|---------|------|------|
| 北京市 | 北京市第一中学 | 10001 | 高中 | 北京市XX区XX路 | 010-12345678 | school1@example.com | 张校长 |
| 北京市 | 北京市第二小学 | 10002 | 小学 | 北京市XX区XX街 | 010-87654321 | school2@example.com | 李校长 |

## 验收标准总结

1. **功能完整性**：所有核心功能实现完成
2. **数据准确性**：学校匹配准确，数据创建正确
3. **错误处理**：错误信息清晰，异常情况处理完善
4. **用户体验**：前端界面友好，操作流程顺畅
5. **测试覆盖**：单元测试和集成测试覆盖主要场景
6. **代码质量**：代码规范，注释完整，可维护性强
