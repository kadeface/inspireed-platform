# 班级批量导入设计文档审核报告

## 审核依据
基于项目架构文档（CLAUDE.md）和现有代码模式（SchoolImportService, StudentImportService）

## 一、架构一致性检查

### ✅ 1. API路由设计
**现状：**
- 设计文档：`POST /api/v1/admin/organization/classrooms/import`
- 学校端：`POST /api/v1/school/classrooms/import`

**审核结果：**
- ✅ 县区管理端路由符合现有模式（`/api/v1/admin/organization/...`）
- ⚠️ **问题**：学校端路由 `/api/v1/school/...` 在项目中不存在
  - 检查发现：没有 `backend/app/api/v1/school*.py` 文件
  - 现有路由都在 `admin_organization.py` 中
  - **建议**：学校端也使用相同路由，通过权限控制区分

**修改建议：**
```python
# 学校端应使用相同的路由，但在API中检查当前用户的学校
POST /api/v1/admin/organization/classrooms/import
# 或创建新的路由前缀（如果将来有学校管理模块）
POST /api/v1/admin/organization/school/classrooms/import
```

### ✅ 2. Schema定义位置
**现状：**
- 设计文档未明确Schema定义位置

**审核结果：**
- ✅ 参考 `SchoolImportResponse` 和 `SchoolImportError`，应在 `admin_organization.py` 中定义
- ✅ 命名规范：`ClassroomImportResponse`、`ClassroomImportError`

**符合现有模式：**
```python
# 在 backend/app/api/v1/admin_organization.py 中定义
class ClassroomImportError(BaseModel):
    row: int
    field: Optional[str] = None
    message: str

class ClassroomImportResponse(BaseModel):
    total: int
    success: int
    failed: int
    created: int
    updated: int
    skipped: int
    errors: List[ClassroomImportError]
```

### ✅ 3. 服务层设计
**现状：**
- 设计文档：创建 `ClassroomImportService`

**审核结果：**
- ✅ 符合项目模式（参考 `SchoolImportService`、`StudentImportService`）
- ✅ 文件位置：`backend/app/services/classroom_import_service.py`
- ✅ 使用静态方法，返回 `(records, errors)` 元组

### ✅ 4. 响应结构
**现状：**
- 设计文档的响应结构与 `SchoolImportResponse` 不完全一致

**审核结果：**
- ⚠️ **不一致**：
  - 文档使用：`created`, `updated`, `skipped`
  - `SchoolImportResponse` 使用：`created_regions`, `created_schools`, `updated_schools`, `skipped_schools`
  - `StudentImportResponse` 使用：`created`, `updated`, `skipped`
  
**建议：**
- 使用与 `StudentImportResponse` 一致的简化命名（更适合班级导入）

## 二、技术实现检查

### ✅ 5. Excel解析库
**现状：**
- 设计文档未明确指定库

**审核结果：**
- ✅ 项目使用 `openpyxl`（参考 `SchoolImportService`）
- ✅ 使用 `load_workbook(..., read_only=True, data_only=True)`

### ✅ 6. 文件处理
**现状：**
- 设计文档提到了文件上传

**审核结果：**
- ✅ 应使用 `tempfile.NamedTemporaryFile` 创建临时文件
- ✅ 处理完成后必须清理临时文件（在 `finally` 块中）
- ✅ 使用 `UploadFile` 从 FastAPI 接收文件

### ✅ 7. 错误处理模式
**现状：**
- 设计文档定义了错误类型

**审核结果：**
- ✅ 应创建自定义异常类：`ClassroomImportServiceError`
- ✅ 解析错误返回给用户，不抛出异常
- ✅ 业务错误记录到 errors 列表，不中断整个导入

### ✅ 8. 事务管理
**现状：**
- 设计文档未明确事务处理

**审核结果：**
- ✅ 应在导入成功后调用 `await db.commit()`
- ✅ 发生错误时调用 `await db.rollback()`
- ✅ 参考 `import_schools` 的实现模式

## 三、数据模型检查

### ✅ 9. 班级编号解析
**现状：**
- 设计文档：班级编号格式如 `701` = 7年级1班

**审核结果：**
- ✅ 与 `StudentImportService.parse_classroom_code` 逻辑一致
- ✅ 可直接复用该方法（或在同一个服务中实现）

### ✅ 10. 年级匹配
**现状：**
- 设计文档：通过 `grade_level` 查找年级

**审核结果：**
- ✅ 符合 `Grade` 模型结构（`level` 字段是唯一索引）
- ✅ 查询方式：`select(Grade).where(Grade.level == grade_level)`

### ✅ 11. 学校匹配（县区端）
**现状：**
- 设计文档：优先使用学校代码，其次使用学校名称+区域

**审核结果：**
- ✅ 与 `StudentImportService.find_school` 逻辑一致
- ✅ 可复用该方法的匹配逻辑

## 四、前端实现检查

### ✅ 12. 前端服务层
**现状：**
- 设计文档未明确前端API调用位置

**审核结果：**
- ✅ 应在 `frontend/src/services/admin.ts` 中添加方法
- ✅ 命名：`importClassrooms`（参考 `importSchools`）
- ✅ 处理 FormData 上传（参考 `evaluation.ts` 的修复）

### ✅ 13. 页面实现
**现状：**
- 设计文档指定了页面位置

**审核结果：**
- ✅ 县区端：在 `OrganizationManagement.vue` 的"学校管理"标签页
- ✅ 学校端：在班级管理抽屉中
- ✅ 使用对话框模式（参考学校批量导入的实现）

## 五、需要补充的内容

### ⚠️ 1. Schema定义需要明确
**建议在文档中补充：**
```python
# 在 backend/app/api/v1/admin_organization.py 中定义
class ClassroomImportError(BaseModel):
    """班级导入错误"""
    row: int = Field(..., description="行号")
    field: Optional[str] = Field(None, description="字段名")
    message: str = Field(..., description="错误信息")

class ClassroomImportResponse(BaseModel):
    """班级批量导入响应"""
    total: int = Field(..., description="总记录数")
    success: int = Field(..., description="成功数")
    failed: int = Field(..., description="失败数")
    created: int = Field(0, description="创建的班级数")
    updated: int = Field(0, description="更新的班级数")
    skipped: int = Field(0, description="跳过的班级数（已存在）")
    errors: List[ClassroomImportError] = Field(default_factory=list, description="错误列表")
```

### ⚠️ 2. 学校端API路由需要调整
**问题：** `/api/v1/school/classrooms/import` 路由不存在

**建议：**
- 选项1：使用相同路由，在API中检查 `current_user.school_id`
- 选项2：创建 `/api/v1/admin/organization/school/classrooms/import`（但需要创建新的router）
- 选项3：在现有的 `admin_organization.py` 中添加一个端点，通过查询参数区分（`?school_id=xxx`）

**推荐方案：** 选项1，使用相同路由，通过权限检查确保学校管理员只能导入本校班级。

### ⚠️ 3. 权限检查需要明确
**建议补充：**
```python
# 县区管理端
current_user: User = Depends(get_current_admin)  # 系统管理员、区县管理员

# 学校端
current_user: User = Depends(get_current_school_admin)  # 需要创建新的依赖，或复用现有依赖
```

### ⚠️ 4. 服务层异常类定义
**建议补充：**
```python
class ClassroomImportServiceError(Exception):
    """班级导入服务错误"""
    pass
```

### ⚠️ 5. 前端类型定义
**建议在 `frontend/src/types/admin.ts` 或 `organization.ts` 中补充：**
```typescript
export interface ClassroomImportError {
  row: number;
  field?: string | null;
  message: string;
}

export interface ClassroomImportResponse {
  total: number;
  success: number;
  failed: number;
  created: number;
  updated: number;
  skipped: number;
  errors: ClassroomImportError[];
}
```

## 六、技术细节补充

### ✅ 6.1 批量提交策略
**建议：** 每100条记录提交一次（参考设计文档）

### ✅ 6.2 缓存策略
**建议：**
- 缓存年级查询结果（level → Grade对象）
- 缓存学校查询结果（避免重复查询同一学校）
- 使用字典缓存，key为level或school_name

### ✅ 6.3 日志记录
**建议：** 参考 `import_schools` 的实现：
- 记录文件上传开始
- 记录解析完成（记录数、错误数）
- 记录导入结果
- 记录异常信息（使用 `exc_info=True`）

## 七、总体评价

### ✅ 优点
1. 设计思路清晰，符合项目架构模式
2. 字段设计合理，支持自动生成和手动填写
3. 错误处理完善，支持部分成功导入
4. 区分县区端和学校端，符合实际使用场景

### ⚠️ 需要改进
1. **API路由**：学校端路由需要调整，应与现有架构保持一致
2. **Schema定义**：需要明确Schema定义位置和结构
3. **权限检查**：需要明确学校管理员的权限检查方式
4. **类型定义**：前端TypeScript类型需要补充

### 📋 建议优先级
1. **高优先级**：修正API路由设计（学校端）
2. **高优先级**：补充Schema定义
3. **中优先级**：明确权限检查机制
4. **低优先级**：补充前端类型定义（可在实现时添加）

---

**审核日期：** 2026-01-14  
**审核者：** AI Code Reviewer  
**文档版本：** v1.0
