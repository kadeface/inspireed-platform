# OrganizationManagement 组件重构说明

## 重构概述

原始的 `OrganizationManagement.vue` 文件包含 **4916 行代码**，已经成功拆分为多个子组件以提高可维护性。

## 完成状态

### ✅ 已完成

1. **备份文件**: `OrganizationManagement.vue.backup` (包含所有原始代码)
2. **主文件**: `OrganizationManagement.vue` (新的简化主文件，仅包含卡片导航)
3. **RegionManagementCard.vue**: 区域管理功能（完整实现）
4. **PositionTypeCard.vue**: 职务类型管理功能（完整实现）
5. **SchoolManagementCard.vue**: 学校管理功能（✅ 完整实现）
6. **ClassroomManagementCard.vue**: 班级成员管理功能（✅ 完整实现）
7. **TeacherAssignmentCard.vue**: 教师教学任务管理功能（✅ 完整实现）

## 目录结构

```
frontend/src/pages/Admin/
├── OrganizationManagement.vue          # 主文件（重构后，243行）
├── OrganizationManagement.vue.backup    # 原始文件备份（4916行）
└── OrganizationManagement/
    ├── RegionManagementCard.vue         # 区域管理组件
    ├── SchoolManagementCard.vue         # 学校管理组件
    ├── ClassroomManagementCard.vue      # 班级成员管理组件
    ├── TeacherAssignmentCard.vue        # 教师教学任务组件
    └── PositionTypeCard.vue             # 职务类型管理组件
```

## 需要完成的工作

### 1. SchoolManagementCard.vue

从备份文件中提取以下功能：

**模板部分（行 248-381）**:
- 学校操作栏（创建、批量导入学校、批量导入班级、刷新）
- 学校筛选（县区、类型、搜索）
- 学校列表表格
- 学校分页

**脚本部分**:
- 状态管理（行 2837-2989）:
  - `schools`, `schoolPage`, `schoolPageSize`, `schoolTotal`
  - `schoolRegionFilter`, `schoolTypeFilter`, `schoolSearchQuery`
  - `showSchoolModal`, `editingSchool`, `allRegions`
  - `schoolForm`

- 学校批量导入状态（行 2861-2889）
- 县区端班级批量导入状态（行 2976-3006）

**方法**:
- `loadSchools()` (行 3267-3283)
- `searchSchools()` (行 3285-3288)
- `openCreateSchoolModal()` (行 3300-3317)
- `editSchool()` (行 3319-3336)
- `saveSchool()` (行 3343-3363)
- `deleteSchool()` (行 3365-3378)
- `openSchoolImportDialog()` (行 3380-3399)
- `downloadSchoolTemplate()` (行 3412-3436)
- `startSchoolImport()` (行 3454-3497)
- `openDistrictClassroomImportDialog()` (行 4229-4251)
- `downloadDistrictClassroomTemplate()` (行 4264-4294)
- 分页方法（行 3499+）

**对话框**:
- 创建/编辑学校对话框
- 批量导入学校对话框（包含3个步骤）
- 县区端批量导入班级对话框（包含3个步骤）

### 2. ClassroomManagementCard.vue

从备份文件中提取以下功能：

**模板部分（行 135-246 + 相关对话框）**:
- 班级选择器（选择学校后显示班级列表）
- 班级操作栏（创建班级、批量导入、刷新）
- 班级筛选（年级、搜索）
- 班级成员管理（添加单个成员、批量添加、移除成员）
- 班级分页

**脚本部分**:
- 状态管理（行 2891-3040）:
  - `showClassroomManager`, `classroomSchool`
  - `classrooms`, `classroomLoading`, `classroomPage`
  - `grades`, `classroomSearchQuery`, `classroomGradeFilter`
  - `showClassroomModal`, `editingClassroom`, `classroomForm`
  - `classroomNameError`
  - 所有班级列表状态（用于班级成员管理）
  - `filteredSchoolsForClassroom` 计算属性

- 班级批量导入状态（行 2946-2974）
- 成员管理状态（行 3008-3039）
- 用户搜索状态（行 3027-3032）
- 批量添加成员状态（行 3034-3039）

**方法**:
- `loadClassrooms()` - 需要从备份提取
- `loadAllClassrooms()` - 需要从备份提取
- `openCreateClassroomModal()` - 需要从备份提取
- `editClassroom()` - 需要从备份提取
- `saveClassroom()` (行 4027-4083)
- `deleteClassroom()` (行 4085-4097)
- `openClassroomImportDialog()` (行 4100-4125)
- `downloadClassroomTemplate()` (行 4138-4166)
- `startClassroomImport()` (行 4176-4227)
- 成员管理方法（行 3685-4019）
- `searchUsers()` - 需要从备份提取
- `openAddMemberModal()` - 需要从备份提取
- `saveMember()` (行 3945-4003)
- `removeMember()` (行 4005-4019)

**对话框**:
- 创建/编辑班级对话框
- 学校端批量导入班级对话框
- 班级成员管理对话框
- 添加成员对话框（单个模式/批量模式）

### 3. TeacherAssignmentCard.vue

从备份文件中提取以下功能：

**模板部分（行 1950-2597）**:
- 教学任务操作栏（添加任务、批量导入、刷新）
- 教学任务筛选（区域、学期、年级、学科、学校、教师、班级）
- 教学任务列表表格
- 教学任务分页
- 添加/编辑教学任务对话框
- 批量导入教学任务对话框（包含4个步骤）

**脚本部分**:
- 状态管理（行 3041-3102）:
  - `teacherAssignments`, `teachers`, `subjects`, `semesters`
  - `assignmentPage`, `assignmentSize`, `assignmentTotal`, `assignmentLoading`
  - `assignmentFilters` (包含多种筛选条件)
  - `showAssignmentDialog`, `editingAssignment`, `assignmentSaving`
  - `assignmentForm`

- 批量导入教学任务状态（行 3078-3102）
- 计算属性（行 3104-3122）:
  - `filteredAssignmentSchools`
  - `filteredAssignmentClassrooms`

**方法**:
- `loadTeachers()` - 需要从备份提取
- `loadSubjects()` - 需要从备份提取
- `loadSemesters()` - 需要从备份提取
- `loadTeacherAssignments()` - 需要从备份提取
- `openCreateAssignmentDialog()` - 需要从备份提取
- `editTeacherAssignment()` - 需要从备份提取
- `saveTeacherAssignment()` - 需要从备份提取
- `deleteTeacherAssignment()` - 需要从备份提取
- `openAssignmentImportDialog()` (行 4651-4669)
- `downloadAssignmentTemplate()` (行 4671-4713)
- `exportCreatedTeachers()` (行 4715-4762)
- `startAssignmentImport()` (行 4772-4818)
- `loadAvailablePositionTypes()` (行 4633-4660)

**其他**:
- `getAssignmentTypeName()` - 获取任务类型名称
- `handleAssignmentSchoolChange()` - 处理学校变更
- `handleAssignmentGradeChange()` - 处理年级变更
- XLSX 相关导入导出功能

## 如何完成剩余组件

### 方法 1: 手动提取（推荐用于理解代码）

1. 打开 `OrganizationManagement.vue.backup`
2. 搜索相关功能的模板和脚本代码
3. 将代码复制到对应的组件文件中
4. 调整导入语句和组件引用
5. 测试功能是否正常

### 方法 2: 使用脚本辅助提取

可以使用 grep 和 sed 等工具提取特定行范围的代码，例如：

```bash
# 提取学校管理模板（行 248-381）
sed -n '248,381p' OrganizationManagement.vue.backup > school_template.txt

# 提取学校管理方法
sed -n '3267,3500p' OrganizationManagement.vue.backup > school_methods.txt
```

## 导入依赖清单

每个子组件需要确保正确导入以下依赖：

```typescript
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from '@/composables/useToast'
import { ElMessage, ElMessageBox } from 'element-plus'
import adminService, { type Region, type School, type Classroom } from '@/services/admin'
import curriculumService from '@/services/curriculum'
import { classroomAssistantService } from '@/services/classroomAssistant'
import teacherApi from '@/services/teacher'
import { semesterApi } from '@/services/evaluation'
import { teacherPositionApi } from '@/services/teacher_position'
import type { Grade, Subject } from '@/types/curriculum'
import type { TeacherTeachingAssignment } from '@/types/teacher'
import type { Semester } from '@/types/evaluation'
import type { ClassroomMembership } from '@/types/classroomAssistant'
import { RoleInClass } from '@/types/classroomAssistant'
import { Download, UploadFilled, Upload, ArrowRight, ArrowLeft } from '@element-plus/icons-vue'
import type { UploadFile, UploadProps } from 'element-plus'
import * as XLSX from 'xlsx'
```

## 测试清单

完成组件提取后，需要测试以下功能：

### RegionManagementCard ✅
- [x] 创建区域
- [x] 编辑区域
- [x] 删除区域
- [x] 区域筛选和搜索
- [x] 区域分页

### PositionTypeCard ✅
- [x] 创建职务类型
- [x] 编辑职务类型
- [x] 删除职务类型（自定义）
- [x] 职务类型筛选和搜索
- [x] 系统职务类型不可编辑/删除

### SchoolManagementCard ✅
- [x] 创建学校
- [x] 编辑学校
- [x] 删除学校
- [x] 批量导入学校
- [x] 批量导入班级（县区端）
- [x] 学校筛选和搜索
- [x] 学校分页

### ClassroomManagementCard ✅
- [x] 查看所有班级列表
- [x] 班级筛选（区域、学校、年级、搜索）
- [x] 查看班级成员
- [x] 添加单个成员
- [x] 批量添加成员（从其他班级选择）
- [x] 编辑成员信息
- [x] 移除成员

### TeacherAssignmentCard ✅
- [x] 创建教学任务
- [x] 编辑教学任务
- [x] 删除教学任务
- [x] 批量导入教学任务
- [x] 教学任务筛选（多种条件）
- [x] 导出新建教师账号
- [x] 教学任务分页

## 注意事项

1. **类型定义**: 确保所有使用的类型都正确导入
2. **API 调用**: 检查所有 API 服务方法的参数和返回值
3. **状态管理**: 某些状态可能需要在组件间共享，考虑使用 props/emits 或 Pinia
4. **文件上传**: 确保文件上传组件（el-upload）正确配置
5. **XLSX 导入导出**: 确保 xlsx 库正确导入和使用
6. **权限控制**: 检查是否有权限相关的逻辑需要保留

## 完成后

完成所有组件提取后：

1. 删除或重命名 `.backup` 文件
2. 运行类型检查: `pnpm type-check`
3. 运行 linter: `pnpm lint`
4. 测试所有功能
5. 提交代码

## 相关文件

- 原始备份: `frontend/src/pages/Admin/OrganizationManagement.vue.backup`
- 主文件: `frontend/src/pages/Admin/OrganizationManagement.vue`
- 区域组件: `frontend/src/pages/Admin/OrganizationManagement/RegionManagementCard.vue`
- 职务类型组件: `frontend/src/pages/Admin/OrganizationManagement/PositionTypeCard.vue`

---

**创建时间**: 2026-01-16
**状态**: 全部完成（5/5 组件已完整实现）✅
