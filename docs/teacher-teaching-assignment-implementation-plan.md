# 教师教学任务管理功能实施计划

## 项目概述

实现教师教学任务（TeacherTeachingAssignment）的完整CRUD功能，支持教师与学校、年级、班级、学科的关联管理，为教师绩效统计提供数据基础。

---

## 阶段一：数据库层（Database Layer）

### 1.1 创建数据模型

**文件**: `backend/app/models/teacher.py` (新建)

**任务清单**:
- [ ] 创建 `TeachingAssignmentType` 枚举（HEAD_TEACHER, SUBJECT_TEACHER）
- [ ] 创建 `TeacherTeachingAssignment` 模型
- [ ] 定义所有字段和关系
- [ ] 添加唯一约束和索引
- [ ] 在 `backend/app/models/__init__.py` 中导入新模型

**关键字段**:
```python
- teacher_id (ForeignKey -> users.id)
- school_id (ForeignKey -> schools.id)
- grade_id (ForeignKey -> grades.id)
- classroom_id (ForeignKey -> classrooms.id)
- subject_id (ForeignKey -> subjects.id)
- semester_id (ForeignKey -> semesters.id)
- academic_year (String)
- assignment_type (Enum)
- is_active (Boolean)
```

**唯一约束**:
```python
UniqueConstraint('teacher_id', 'semester_id', 'classroom_id', 'subject_id')
```

### 1.2 创建数据库迁移

**文件**: `backend/alembic/versions/xxxx_add_teacher_teaching_assignments.py` (自动生成)

**任务清单**:
- [ ] 运行 `alembic revision --autogenerate -m "add teacher teaching assignments table"`
- [ ] 检查生成的迁移文件
- [ ] 手动调整迁移脚本（如需要）
- [ ] 运行 `alembic upgrade head` 应用迁移
- [ ] 验证表结构

**迁移命令**:
```bash
cd backend
source venv/bin/activate
alembic revision --autogenerate -m "add teacher teaching assignments table"
alembic upgrade head
```

---

## 阶段二：数据层（Data Layer - Schemas）

### 2.1 创建 Pydantic Schemas

**文件**: `backend/app/schemas/teacher.py` (新建)

**任务清单**:
- [ ] 创建 `TeachingAssignmentType` 枚举（与模型保持一致）
- [ ] 创建 `TeacherTeachingAssignmentBase` 基类
- [ ] 创建 `TeacherTeachingAssignmentCreate` 创建请求
- [ ] 创建 `TeacherTeachingAssignmentUpdate` 更新请求
- [ ] 创建 `TeacherTeachingAssignmentResponse` 响应模型
- [ ] 创建 `TeacherTeachingAssignmentListResponse` 列表响应

**Schema 结构**:
```python
# 基础字段
class TeacherTeachingAssignmentBase(BaseModel):
    teacher_id: int
    school_id: int
    grade_id: int
    classroom_id: int
    subject_id: int
    semester_id: int
    academic_year: str
    assignment_type: TeachingAssignmentType
    is_active: bool = True

# 创建请求（所有字段必填）
class TeacherTeachingAssignmentCreate(TeacherTeachingAssignmentBase):
    pass

# 更新请求（所有字段可选）
class TeacherTeachingAssignmentUpdate(BaseModel):
    teacher_id: Optional[int] = None
    school_id: Optional[int] = None
    grade_id: Optional[int] = None
    classroom_id: Optional[int] = None
    subject_id: Optional[int] = None
    semester_id: Optional[int] = None
    academic_year: Optional[str] = None
    assignment_type: Optional[TeachingAssignmentType] = None
    is_active: Optional[bool] = None

# 响应模型（包含ID和时间戳）
class TeacherTeachingAssignmentResponse(TeacherTeachingAssignmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    # 关联对象（可选）
    teacher: Optional[UserResponse] = None
    school: Optional[SchoolResponse] = None
    grade: Optional[GradeResponse] = None
    classroom: Optional[ClassroomResponse] = None
    subject: Optional[SubjectResponse] = None
    semester: Optional[SemesterResponse] = None

# 列表响应
class TeacherTeachingAssignmentListResponse(BaseModel):
    assignments: List[TeacherTeachingAssignmentResponse]
    total: int
    page: int
    size: int
    total_pages: int
```

---

## 阶段三：服务层（Service Layer）

### 3.1 创建业务逻辑服务

**文件**: `backend/app/services/teacher_service.py` (新建)

**任务清单**:
- [ ] 创建 `TeacherService` 类
- [ ] 实现 `create_assignment` 方法（创建教学任务）
- [ ] 实现 `get_assignment` 方法（获取单个任务）
- [ ] 实现 `list_assignments` 方法（列表查询，支持筛选）
- [ ] 实现 `update_assignment` 方法（更新任务）
- [ ] 实现 `delete_assignment` 方法（删除任务）
- [ ] 实现 `get_teacher_assignments` 方法（获取某教师的所有任务）
- [ ] 实现数据验证逻辑（检查教师、学校、班级等是否存在）

**关键方法签名**:
```python
class TeacherService:
    @staticmethod
    async def create_assignment(
        db: AsyncSession,
        assignment_data: TeacherTeachingAssignmentCreate
    ) -> TeacherTeachingAssignment:
        # 验证教师是否存在且角色为TEACHER
        # 验证学校、年级、班级、学科、学期是否存在
        # 检查唯一约束
        # 创建记录
        pass
    
    @staticmethod
    async def list_assignments(
        db: AsyncSession,
        teacher_id: Optional[int] = None,
        school_id: Optional[int] = None,
        grade_id: Optional[int] = None,
        classroom_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        semester_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        size: int = 10
    ) -> Tuple[List[TeacherTeachingAssignment], int]:
        # 构建查询
        # 应用筛选条件
        # 分页
        # 返回结果和总数
        pass
```

---

## 阶段四：API层（API Layer）

### 4.1 创建API路由

**文件**: `backend/app/api/v1/teachers.py` (新建)

**任务清单**:
- [ ] 创建 FastAPI router
- [ ] 实现 `POST /api/v1/teachers/assignments` - 创建教学任务
- [ ] 实现 `GET /api/v1/teachers/assignments` - 获取任务列表（支持筛选）
- [ ] 实现 `GET /api/v1/teachers/assignments/{id}` - 获取单个任务
- [ ] 实现 `PUT /api/v1/teachers/assignments/{id}` - 更新任务
- [ ] 实现 `DELETE /api/v1/teachers/assignments/{id}` - 删除任务
- [ ] 实现 `GET /api/v1/teachers/{teacher_id}/assignments` - 获取某教师的所有任务
- [ ] 添加权限检查（需要管理员权限）
- [ ] 添加错误处理

**API端点设计**:
```python
@router.post("/assignments", response_model=TeacherTeachingAssignmentResponse, status_code=201)
async def create_assignment(
    assignment_data: TeacherTeachingAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """创建教师教学任务"""
    pass

@router.get("/assignments", response_model=TeacherTeachingAssignmentListResponse)
async def list_assignments(
    teacher_id: Optional[int] = Query(None),
    school_id: Optional[int] = Query(None),
    grade_id: Optional[int] = Query(None),
    classroom_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    semester_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取教学任务列表"""
    pass

@router.get("/assignments/{assignment_id}", response_model=TeacherTeachingAssignmentResponse)
async def get_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取单个教学任务"""
    pass

@router.put("/assignments/{assignment_id}", response_model=TeacherTeachingAssignmentResponse)
async def update_assignment(
    assignment_id: int,
    assignment_data: TeacherTeachingAssignmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """更新教学任务"""
    pass

@router.delete("/assignments/{assignment_id}")
async def delete_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """删除教学任务"""
    pass

@router.get("/{teacher_id}/assignments", response_model=TeacherTeachingAssignmentListResponse)
async def get_teacher_assignments(
    teacher_id: int,
    semester_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取某教师的所有教学任务"""
    pass
```

### 4.2 注册路由

**文件**: `backend/app/api/v1/__init__.py` 或 `backend/app/main.py`

**任务清单**:
- [ ] 导入新创建的 router
- [ ] 将 router 注册到主应用
- [ ] 验证路由前缀正确

---

## 阶段五：前端服务层（Frontend Service Layer）

### 5.1 创建TypeScript类型定义

**文件**: `frontend/src/types/teacher.ts` (新建)

**任务清单**:
- [ ] 定义 `TeachingAssignmentType` 枚举
- [ ] 定义 `TeacherTeachingAssignment` 接口
- [ ] 定义 `TeacherTeachingAssignmentCreate` 接口
- [ ] 定义 `TeacherTeachingAssignmentUpdate` 接口
- [ ] 定义 `TeacherTeachingAssignmentListResponse` 接口

**类型定义**:
```typescript
export enum TeachingAssignmentType {
  HEAD_TEACHER = 'head_teacher',
  SUBJECT_TEACHER = 'subject_teacher'
}

export interface TeacherTeachingAssignment {
  id: number
  teacher_id: number
  school_id: number
  grade_id: number
  classroom_id: number
  subject_id: number
  semester_id: number
  academic_year: string
  assignment_type: TeachingAssignmentType
  is_active: boolean
  created_at: string
  updated_at: string
  // 关联对象（可选）
  teacher?: User
  school?: School
  grade?: Grade
  classroom?: Classroom
  subject?: Subject
  semester?: Semester
}

export interface TeacherTeachingAssignmentCreate {
  teacher_id: number
  school_id: number
  grade_id: number
  classroom_id: number
  subject_id: number
  semester_id: number
  academic_year: string
  assignment_type: TeachingAssignmentType
  is_active?: boolean
}

export interface TeacherTeachingAssignmentUpdate {
  teacher_id?: number
  school_id?: number
  grade_id?: number
  classroom_id?: number
  subject_id?: number
  semester_id?: number
  academic_year?: string
  assignment_type?: TeachingAssignmentType
  is_active?: boolean
}

export interface TeacherTeachingAssignmentListResponse {
  assignments: TeacherTeachingAssignment[]
  total: number
  page: number
  size: number
  total_pages: number
}
```

### 5.2 创建API服务

**文件**: `frontend/src/services/teacher.ts` (新建)

**任务清单**:
- [ ] 导入类型定义
- [ ] 创建 `teacherApi` 对象
- [ ] 实现 `createAssignment` 方法
- [ ] 实现 `getAssignments` 方法（支持查询参数）
- [ ] 实现 `getAssignment` 方法
- [ ] 实现 `updateAssignment` 方法
- [ ] 实现 `deleteAssignment` 方法
- [ ] 实现 `getTeacherAssignments` 方法

**服务方法**:
```typescript
import api from './api'
import type {
  TeacherTeachingAssignment,
  TeacherTeachingAssignmentCreate,
  TeacherTeachingAssignmentUpdate,
  TeacherTeachingAssignmentListResponse
} from '@/types/teacher'

export const teacherApi = {
  // 创建教学任务
  async createAssignment(
    data: TeacherTeachingAssignmentCreate
  ): Promise<TeacherTeachingAssignment> {
    return await api.post('/teachers/assignments', data)
  },

  // 获取任务列表
  async getAssignments(params: {
    teacher_id?: number
    school_id?: number
    grade_id?: number
    classroom_id?: number
    subject_id?: number
    semester_id?: number
    is_active?: boolean
    page?: number
    size?: number
  } = {}): Promise<TeacherTeachingAssignmentListResponse> {
    return await api.get('/teachers/assignments', { params })
  },

  // 获取单个任务
  async getAssignment(id: number): Promise<TeacherTeachingAssignment> {
    return await api.get(`/teachers/assignments/${id}`)
  },

  // 更新任务
  async updateAssignment(
    id: number,
    data: TeacherTeachingAssignmentUpdate
  ): Promise<TeacherTeachingAssignment> {
    return await api.put(`/teachers/assignments/${id}`, data)
  },

  // 删除任务
  async deleteAssignment(id: number): Promise<void> {
    return await api.delete(`/teachers/assignments/${id}`)
  },

  // 获取某教师的所有任务
  async getTeacherAssignments(
    teacherId: number,
    semesterId?: number,
    isActive?: boolean
  ): Promise<TeacherTeachingAssignmentListResponse> {
    return await api.get(`/teachers/${teacherId}/assignments`, {
      params: {
        semester_id: semesterId,
        is_active: isActive
      }
    })
  }
}
```

---

## 阶段六：前端UI层（Frontend UI Layer）

### 6.1 创建教学任务管理页面

**文件**: `frontend/src/pages/Admin/TeacherAssignmentManagement.vue` (新建)

**任务清单**:
- [ ] 创建页面布局（列表 + 表单）
- [ ] 实现任务列表展示（表格）
- [ ] 实现筛选功能（教师、学校、年级、班级、学科、学期）
- [ ] 实现创建任务表单（对话框）
- [ ] 实现编辑任务表单（对话框）
- [ ] 实现删除确认对话框
- [ ] 实现分页功能
- [ ] 添加加载状态和错误处理

**页面结构**:
```vue
<template>
  <div class="teacher-assignment-management">
    <!-- 顶部操作栏 -->
    <div class="toolbar">
      <button @click="openCreateDialog">+ 创建教学任务</button>
      <!-- 筛选器 -->
      <select v-model="filters.teacher_id">...</select>
      <select v-model="filters.school_id">...</select>
      <select v-model="filters.grade_id">...</select>
      <select v-model="filters.classroom_id">...</select>
      <select v-model="filters.subject_id">...</select>
      <select v-model="filters.semester_id">...</select>
      <button @click="loadAssignments">搜索</button>
    </div>

    <!-- 任务列表表格 -->
    <table>
      <thead>
        <tr>
          <th>教师</th>
          <th>学校</th>
          <th>年级</th>
          <th>班级</th>
          <th>学科</th>
          <th>学期</th>
          <th>学年</th>
          <th>任务类型</th>
          <th>状态</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="assignment in assignments" :key="assignment.id">
          <td>{{ assignment.teacher?.full_name }}</td>
          <td>{{ assignment.school?.name }}</td>
          <td>{{ assignment.grade?.name }}</td>
          <td>{{ assignment.classroom?.name }}</td>
          <td>{{ assignment.subject?.name }}</td>
          <td>{{ assignment.semester?.name }}</td>
          <td>{{ assignment.academic_year }}</td>
          <td>{{ getAssignmentTypeName(assignment.assignment_type) }}</td>
          <td>{{ assignment.is_active ? '激活' : '停用' }}</td>
          <td>
            <button @click="editAssignment(assignment)">编辑</button>
            <button @click="deleteAssignment(assignment)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 分页 -->
    <div class="pagination">...</div>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="showDialog" :title="editingAssignment ? '编辑任务' : '创建任务'">
      <el-form :model="formData" @submit.prevent="saveAssignment">
        <el-form-item label="教师">
          <el-select v-model="formData.teacher_id">...</el-select>
        </el-form-item>
        <el-form-item label="学校">
          <el-select v-model="formData.school_id">...</el-select>
        </el-form-item>
        <el-form-item label="年级">
          <el-select v-model="formData.grade_id">...</el-select>
        </el-form-item>
        <el-form-item label="班级">
          <el-select v-model="formData.classroom_id">...</el-select>
        </el-form-item>
        <el-form-item label="学科">
          <el-select v-model="formData.subject_id">...</el-select>
        </el-form-item>
        <el-form-item label="学期">
          <el-select v-model="formData.semester_id">...</el-select>
        </el-form-item>
        <el-form-item label="学年">
          <el-input v-model="formData.academic_year" />
        </el-form-item>
        <el-form-item label="任务类型">
          <el-select v-model="formData.assignment_type">...</el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="formData.is_active" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveAssignment">保存</el-button>
          <el-button @click="closeDialog">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>
```

### 6.2 集成到管理后台

**文件**: `frontend/src/pages/Admin/OrganizationManagement.vue` 或创建新的管理页面

**任务清单**:
- [ ] 添加"教师教学任务管理"标签页或菜单项
- [ ] 导入 `TeacherAssignmentManagement.vue` 组件
- [ ] 配置路由（如需要）

---

## 阶段七：测试与验证

### 7.1 后端测试

**任务清单**:
- [ ] 测试创建教学任务API
- [ ] 测试获取任务列表API（各种筛选条件）
- [ ] 测试更新任务API
- [ ] 测试删除任务API
- [ ] 测试唯一约束验证
- [ ] 测试权限控制

### 7.2 前端测试

**任务清单**:
- [ ] 测试页面加载和数据展示
- [ ] 测试创建任务功能
- [ ] 测试编辑任务功能
- [ ] 测试删除任务功能
- [ ] 测试筛选功能
- [ ] 测试分页功能
- [ ] 测试错误处理

---

## 实施顺序建议

### 第一步：数据库层（1-2小时）
1. 创建数据模型
2. 生成并应用迁移
3. 验证表结构

### 第二步：后端API（3-4小时）
1. 创建Schemas
2. 创建Service
3. 创建API路由
4. 测试API端点

### 第三步：前端实现（4-5小时）
1. 创建类型定义
2. 创建API服务
3. 创建UI组件
4. 集成到管理后台

### 第四步：测试与优化（2-3小时）
1. 端到端测试
2. 修复bug
3. 优化用户体验

**总预计时间**: 10-14小时

---

## 注意事项

1. **数据验证**：
   - 确保教师角色为 `TEACHER`
   - 验证学校、年级、班级、学科、学期是否存在
   - 检查唯一约束（同一教师、学期、班级、学科不能重复）

2. **权限控制**：
   - 所有API需要管理员权限
   - 考虑是否需要学校管理员只能管理本校教师

3. **数据迁移**：
   - 如果要从现有数据迁移，需要编写迁移脚本
   - 确保数据完整性

4. **性能优化**：
   - 列表查询需要添加适当的索引
   - 考虑使用 `selectinload` 预加载关联对象

5. **用户体验**：
   - 表单验证提示要清晰
   - 加载状态要明确
   - 错误信息要友好

---

## 相关文件清单

### 新建文件
- `backend/app/models/teacher.py`
- `backend/app/schemas/teacher.py`
- `backend/app/services/teacher_service.py`
- `backend/app/api/v1/teachers.py`
- `frontend/src/types/teacher.ts`
- `frontend/src/services/teacher.ts`
- `frontend/src/pages/Admin/TeacherAssignmentManagement.vue`

### 修改文件
- `backend/app/models/__init__.py` - 导入新模型
- `backend/app/api/v1/__init__.py` 或 `backend/app/main.py` - 注册路由
- `frontend/src/router/index.ts` - 添加路由（如需要）

### 迁移文件
- `backend/alembic/versions/xxxx_add_teacher_teaching_assignments.py` - 自动生成
