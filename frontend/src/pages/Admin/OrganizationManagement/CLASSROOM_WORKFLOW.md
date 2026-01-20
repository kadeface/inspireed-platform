# 班级管理工作流分析

## 📋 工作流概览

本文档详细说明点击"班级管理"后的完整工作流程，包括组件初始化、数据加载、筛选、CRUD 操作等各个环节。

---

## 1. 入口流程

### 1.1 用户操作
1. 用户在 `OrganizationManagement.vue` 主页面看到"班级管理"卡片
2. 点击班级管理卡片
3. 触发 `@click="activeTab = 'classrooms'"`
4. `activeTab` 值变为 `'classrooms'`

### 1.2 组件渲染
```vue
<!-- OrganizationManagement.vue -->
<ClassroomManagementCard v-if="activeTab === 'classrooms'" />
```
- Vue 检测到 `activeTab === 'classrooms'` 为 `true`
- `ClassroomManagementCard` 组件被渲染并挂载

---

## 2. 组件初始化流程

### 2.1 组件挂载（onMounted）

```typescript
onMounted(async () => {
  await Promise.all([
    loadAllRegions(),      // 加载所有区域
    loadGradesList(),      // 加载所有年级
    loadAllClassrooms(),   // 加载班级列表
  ])
})
```

**并行执行的任务：**

#### 2.1.1 loadAllRegions()
```typescript
async function loadAllRegions() {
  const response = await adminService.getRegions({ size: 1000 })
  allRegions.value = response.regions
}
```
- **API 调用**：`GET /api/v1/regions?size=1000`
- **数据存储**：`allRegions.value`
- **用途**：用于区域筛选下拉框

#### 2.1.2 loadGradesList()
```typescript
async function loadGradesList() {
  grades.value = await curriculumService.getGrades(true)
}
```
- **API 调用**：`GET /api/v1/grades?active=true`
- **数据存储**：`grades.value`
- **用途**：用于年级筛选下拉框和创建/编辑班级表单

#### 2.1.3 loadAllClassrooms()
**这是最复杂的初始化流程，包含多个步骤：**

```typescript
async function loadAllClassrooms() {
  allClassroomsLoading.value = true
  
  // 步骤 1: 确保基础数据已加载
  if (allRegions.value.length === 0) {
    await loadAllRegions()
  }
  if (grades.value.length === 0) {
    await loadGradesList()
  }
  
  // 步骤 2: 根据区域筛选加载学校列表
  await loadAllSchools()
  
  // 步骤 3: 加载班级列表
  const response = await adminService.getClassrooms({
    page: classroomPagination.value.page,
    size: classroomPagination.value.size,
    region_id: classroomFilters.value.region_id,
    school_id: classroomFilters.value.school_id,
    grade_id: classroomFilters.value.grade_id,
    search: classroomSearchQuery.value || undefined,
  })
  
  // 步骤 4: 更新班级列表和分页信息
  allClassrooms.value = response.classrooms
  classroomPagination.value.total = response.total || 0
  classroomPagination.value.totalPages = response.total_pages || 0
  
  // 步骤 5: 补充缺失的学校信息（边缘情况处理）
  const schoolIds = [...new Set(response.classrooms.map(c => c.school_id))]
  const missingSchoolIds = schoolIds.filter(id => !schools.value.find(s => s.id === id))
  if (missingSchoolIds.length > 0) {
    for (const schoolId of missingSchoolIds) {
      const school = await adminService.getSchool(schoolId)
      schools.value.push(school)
    }
  }
  
  allClassroomsLoading.value = false
}
```

**loadAllSchools() 子流程：**
```typescript
async function loadAllSchools() {
  const params: any = { page: 1, size: 1000 }
  if (classroomFilters.value.region_id) {
    params.region_id = classroomFilters.value.region_id
  }
  const response = await adminService.getSchools(params)
  schools.value = response.schools
}
```
- **API 调用**：`GET /api/v1/schools?page=1&size=1000&region_id=xxx`（如果有区域筛选）
- **数据存储**：`schools.value`
- **用途**：用于学校筛选下拉框和创建/编辑班级表单

### 2.2 初始化完成状态

初始化完成后，组件状态如下：

| 状态变量 | 数据来源 | 用途 |
|---------|---------|------|
| `allRegions` | `loadAllRegions()` | 区域筛选下拉框 |
| `schools` | `loadAllSchools()` | 学校筛选下拉框、创建表单 |
| `grades` | `loadGradesList()` | 年级筛选下拉框、创建表单 |
| `allClassrooms` | `loadAllClassrooms()` | 班级列表表格 |
| `classroomFilters` | 初始化为 `{ region_id: undefined, school_id: undefined, grade_id: undefined }` | 筛选状态 |
| `classroomSearchQuery` | 初始化为 `''` | 搜索关键词 |

---

## 3. 筛选工作流

### 3.1 筛选组件配置

```typescript
const classroomFilterConfigs = computed<FilterConfig[]>(() => [
  {
    key: 'region_id',
    label: '县区',
    options: allRegions.value,
    type: 'number',
  },
  {
    key: 'school_id',
    label: '学校',
    computedOptions: () => filteredSchoolsForClassroom.value,  // 动态计算
    dependsOn: 'region_id',  // 依赖区域筛选
    type: 'number',
  },
  {
    key: 'grade_id',
    label: '年级',
    options: grades.value,
    type: 'number',
  },
])
```

**级联筛选逻辑：**
```typescript
const filteredSchoolsForClassroom = computed(() => {
  if (!classroomFilters.value.region_id) {
    return schools.value  // 无区域筛选时，返回所有学校
  }
  return schools.value.filter(school => 
    school.region_id === classroomFilters.value.region_id
  )
})
```

### 3.2 筛选变化处理

#### 3.2.1 用户操作筛选器

用户在下拉框中选择筛选条件：

```vue
<FilterBar
  v-model="classroomFilters"
  @filter-change="handleClassroomFilterChange"
  ...
/>
```

#### 3.2.2 区域筛选变化

```typescript
async function handleClassroomFilterChange(key: string, value: any) {
  if (key === 'region_id') {
    // FilterBar 会自动清空 school_id（因为 dependsOn: 'region_id'）
    classroomPagination.value.page = 1  // 重置页码
    await loadAllSchools()  // 重新加载学校列表（根据新区域）
    await loadAllClassrooms()  // 重新加载班级列表
  }
  ...
}
```

**流程图：**
```
用户选择区域
    ↓
FilterBar 触发 @filter-change 事件
    ↓
handleClassroomFilterChange('region_id', newValue)
    ↓
classroomFilters.region_id = newValue
    ↓
FilterBar 自动清空 school_id（dependsOn）
    ↓
重置页码为 1
    ↓
loadAllSchools() - 根据新区域加载学校
    ↓
loadAllClassrooms() - 加载班级列表
    ↓
更新 UI（学校下拉框 + 班级列表）
```

#### 3.2.3 学校/年级筛选变化

```typescript
else {
  // 学校或年级筛选改变时，重置页码并加载班级列表
  classroomPagination.value.page = 1
  loadAllClassrooms()  // 直接加载班级列表，不需要重新加载学校
}
```

**流程图：**
```
用户选择学校/年级
    ↓
FilterBar 触发 @filter-change 事件
    ↓
handleClassroomFilterChange('school_id'/'grade_id', newValue)
    ↓
classroomFilters.school_id/grade_id = newValue
    ↓
重置页码为 1
    ↓
loadAllClassrooms() - 加载班级列表（带筛选条件）
    ↓
更新 UI（班级列表）
```

### 3.3 搜索工作流

```typescript
const classroomSearchConfig: SearchConfig = {
  placeholder: '搜索学校或班级名称...',
  debounce: false,
  enterToSearch: true,  // 按 Enter 键触发搜索
}

function handleClassroomSearchEnter(value: string) {
  classroomPagination.value.page = 1
  loadAllClassrooms()
}
```

**流程图：**
```
用户在搜索框输入关键词
    ↓
用户按 Enter 键
    ↓
FilterBar 触发 @search-enter 事件
    ↓
handleClassroomSearchEnter(searchValue)
    ↓
classroomSearchQuery = searchValue
    ↓
重置页码为 1
    ↓
loadAllClassrooms() - 加载班级列表（带搜索条件）
    ↓
更新 UI（班级列表）
```

---

## 4. CRUD 操作工作流

### 4.1 创建班级

#### 4.1.1 打开创建对话框

```typescript
function openCreateClassroomModal() {
  editingClassroom.value = null
  classroomNameError.value = ''
  classroomForm.value = {
    name: '',
    code: '',
    school_id: undefined,
    grade_id: undefined,
    enrollment_year: undefined,
    capacity: undefined,
    description: '',
    is_active: true,
  }
  showClassroomModal.value = true
}
```

#### 4.1.2 保存班级

```typescript
async function saveClassroom() {
  // 验证必填字段
  if (!classroomForm.value.name || !classroomForm.value.school_id || !classroomForm.value.grade_id) {
    classroomNameError.value = '请填写必填字段'
    return
  }

  try {
    classroomSaving.value = true
    
    if (editingClassroom.value) {
      // 更新
      await adminService.updateClassroom(editingClassroom.value.id, classroomForm.value)
      ElMessage.success('班级更新成功')
    } else {
      // 创建
      await adminService.createClassroom(classroomForm.value)
      ElMessage.success('班级创建成功')
    }

    closeClassroomModal()
    await loadAllClassrooms()  // 重新加载列表
  } catch (error: any) {
    classroomNameError.value = error.response?.data?.detail || '保存失败，请重试'
  } finally {
    classroomSaving.value = false
  }
}
```

**API 调用：**
- 创建：`POST /api/v1/classrooms`
- 更新：`PUT /api/v1/classrooms/{id}`

### 4.2 编辑班级

```typescript
function editClassroom(classroom: Classroom) {
  editingClassroom.value = classroom
  classroomNameError.value = ''
  classroomForm.value = {
    name: classroom.name,
    code: classroom.code || '',
    school_id: classroom.school_id,
    grade_id: classroom.grade_id,
    enrollment_year: classroom.enrollment_year || undefined,
    capacity: (classroom as any).capacity || undefined,
    description: classroom.description || '',
    is_active: classroom.is_active,
  }
  showClassroomModal.value = true
}
```

### 4.3 删除班级

```typescript
async function deleteClassroom(classroom: Classroom) {
  try {
    await ElMessageBox.confirm(
      `确定要删除班级 "${classroom.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await adminService.deleteClassroom(classroom.id)
    ElMessage.success('班级删除成功')
    await loadAllClassrooms()  // 重新加载列表
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败，请重试')
    }
  }
}
```

**API 调用：** `DELETE /api/v1/classrooms/{id}`

---

## 5. 分页工作流

### 5.1 页码变化

```typescript
function handleClassroomPageChange(page: number) {
  classroomPagination.value.page = page
  loadAllClassrooms()  // 重新加载当前页数据
}
```

**流程图：**
```
用户点击页码
    ↓
el-pagination 触发 @current-change 事件
    ↓
handleClassroomPageChange(newPage)
    ↓
classroomPagination.page = newPage
    ↓
loadAllClassrooms() - 加载新页数据
    ↓
更新 UI（班级列表）
```

### 5.2 每页条数变化

```typescript
function handleClassroomPageSizeChange(size: number) {
  classroomPagination.value.size = size
  classroomPagination.value.page = 1  // 重置到第一页
  loadAllClassrooms()
}
```

---

## 6. 批量导入工作流

### 6.1 打开导入对话框

```typescript
function openClassroomImportDialog() {
  showClassroomImportDialog.value = true
  classroomImportStep.value = 0  // 步骤 1: 下载模板
  selectedClassroomFile.value = null
  classroomImportForm.value = {
    enrollmentYear: undefined,
    capacity: undefined,
    updateExisting: false
  }
  // 重置导入结果
}
```

### 6.2 导入流程（三步）

#### 步骤 1: 下载模板
```typescript
function downloadClassroomTemplate() {
  const template = [
    ['学校名称*', '学校代码', '年级级别*', '年级名称', '班级编号*', '班级名称', '入学年份', '班级容量', '班级描述'],
    ['开平市第一中学', '10001', 7, '七年级', '701', '七年级1班', 2024, 45, '重点班'],
    ...
  ]
  const ws = XLSX.utils.aoa_to_sheet(template)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '班级信息')
  XLSX.writeFile(wb, '班级信息导入模板.xlsx')
}
```

#### 步骤 2: 上传文件
```typescript
const handleClassroomFileChange: UploadProps['onChange'] = (uploadFile) => {
  selectedClassroomFile.value = uploadFile.raw || null
}

async function startClassroomImport() {
  classroomImporting.value = true
  const result = await adminService.importClassrooms(
    selectedClassroomFile.value,
    undefined,  // school_id（县区端不需要）
    undefined,  // region_id（可选）
    classroomImportForm.value.updateExisting,
    classroomImportForm.value.enrollmentYear,
    classroomImportForm.value.capacity
  )
  classroomImportResult.value = result
  classroomImportStep.value = 2  // 步骤 3: 查看结果
}
```

**API 调用：** `POST /api/v1/classrooms/import`

#### 步骤 3: 查看结果
- 显示导入统计（总数、成功、失败、创建、更新、跳过）
- 显示错误详情表格
- 点击"完成"关闭对话框并刷新列表

---

## 7. 成员管理工作流

### 7.1 打开成员管理

**注意：** 成员管理功能在表格中不可见，需要通过其他方式触发（可能是未来功能或隐藏功能）。

```typescript
async function openMemberManager(classroom: Classroom) {
  selectedClassroom.value = classroom
  showMemberManager.value = true
  await loadMembers()
}
```

### 7.2 加载成员列表

```typescript
async function loadMembers() {
  if (!selectedClassroom.value) return
  const response = await classroomAssistantService.getClassroomMembers(
    selectedClassroom.value.id,
    memberPagination.value.page,
    memberPagination.value.size
  )
  members.value = response.members
  memberPagination.value.total = response.total
  memberPagination.value.totalPages = response.totalPages
}
```

**API 调用：** `GET /api/v1/classrooms/{id}/members?page=1&size=10`

---

## 8. 数据依赖关系图

```
┌─────────────────────────────────────────────────────────────┐
│                  ClassroomManagementCard                     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ loadAllRegions│    │loadGradesList│    │loadAllClassrooms│
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ allRegions   │    │   grades     │    │  allClassrooms│
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────┐
│              FilterBar (筛选组件)                        │
│  - region_id: allRegions                                 │
│  - school_id: filteredSchoolsForClassroom (计算属性)    │
│  - grade_id: grades                                      │
│  - search: classroomSearchQuery                          │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │loadAllSchools()  │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   schools        │
                    └──────────────────┘
```

---

## 9. 潜在问题和优化建议

### 9.1 发现的问题

1. **成员管理功能缺失入口**
   - `openMemberManager()` 函数存在但表格中没有"成员管理"按钮
   - 建议：在操作列添加"成员管理"按钮

2. **学校列表可能不完整**
   - `loadAllSchools()` 只加载 1000 条，如果学校数量超过 1000 可能会遗漏
   - 建议：使用 `size: 10000` 或动态加载

3. **筛选配置计算属性依赖**
   - `classroomFilterConfigs` 依赖 `allRegions` 和 `grades`，但这些数据在初始化时可能还未加载完成
   - 建议：使用 `watch` 监听数据加载完成后再更新配置

### 9.2 优化建议

1. **错误处理增强**
   - 添加更详细的错误提示
   - 区分网络错误和业务错误

2. **加载状态优化**
   - 为每个数据加载操作添加独立的 loading 状态
   - 使用骨架屏提升用户体验

3. **性能优化**
   - 使用 `v-if` 而不是 `v-show` 控制组件渲染（已实现）
   - 考虑使用虚拟滚动处理大量数据

4. **数据缓存**
   - 区域、年级等基础数据可以缓存，避免重复加载
   - 使用 Vuex/Pinia 管理全局状态

---

## 10. 工作流时序图

```
用户点击班级管理
    │
    ▼
组件挂载 (onMounted)
    │
    ├─▶ loadAllRegions() ────┐
    ├─▶ loadGradesList() ────┼──▶ Promise.all 并行执行
    └─▶ loadAllClassrooms() ─┘
            │
            ├─▶ 检查基础数据（如果需要）
            ├─▶ loadAllSchools()
            └─▶ 加载班级列表 API
    │
    ▼
UI 渲染完成
    │
    ▼
用户操作筛选器
    │
    ▼
handleClassroomFilterChange()
    │
    ├─▶ region_id 变化 → loadAllSchools() → loadAllClassrooms()
    └─▶ school_id/grade_id 变化 → loadAllClassrooms()
    │
    ▼
更新 UI
```

---

**文档版本：** v1.0  
**创建日期：** 2026-01-17  
**维护者：** InspireEd 开发团队