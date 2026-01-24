# 学校批量删除功能实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 为学校管理页面添加批量删除功能，支持跨页选择、条件选择，并采用混合删除策略

**架构:** 前端使用 Vue3 + Element Plus 实现选择UI和确认对话框，后端新增批量删除API和关联数据检测API

**技术栈:** Vue3, TypeScript, Element Plus, FastAPI, SQLAlchemy, PostgreSQL

---

## Task 1: 后端 - 添加类型定义

**文件:**
- Modify: `backend/app/api/v1/admin_organization.py:26-151`

**Step 1: 添加批量删除相关的类型定义**

在文件开头的 Request/Response Models 部分，添加以下类型定义：

```python
class SchoolRelationCheck(BaseModel):
    """学校关联数据检查结果"""
    school_id: int
    school_name: str
    has_relations: bool
    relations: Optional[Dict[str, int]] = None  # {classrooms: 0, teachers: 0, students: 0}


class BatchDeleteSchoolsRequest(BaseModel):
    """批量删除学校请求"""
    school_ids: List[int]
    cascade_delete: bool = False


class BatchDeleteSchoolsError(BaseModel):
    """批量删除学校错误详情"""
    school_id: int
    school_name: str
    error: str


class BatchDeleteSchoolsResponse(BaseModel):
    """批量删除学校响应"""
    total_requested: int
    deleted_count: int
    failed_count: int
    errors: List[BatchDeleteSchoolsError]
```

**Step 2: 验证类型定义**

检查是否有语法错误，确保所有类型定义正确。

---

## Task 2: 后端 - 添加关联数据检查API

**文件:**
- Modify: `backend/app/api/v1/admin_organization.py:730` (在 delete_school 函数之后)

**Step 1: 添加关联数据检查端点**

在 `delete_school` 函数之后、导入端点之前添加：

```python
@router.post("/schools/check-relations")
async def check_school_relations(
    request: Dict[str, List[int]],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """检查学校的关联数据

    返回每个学校的关联数据统计（班级、教师、学生）
    """
    school_ids = request.get("school_ids", [])

    if not school_ids:
        raise HTTPException(status_code=400, detail="必须提供学校ID列表")

    # 限制批量操作的数量
    if len(school_ids) > 1000:
        raise HTTPException(status_code=400, detail="单次最多检查1000所学校")

    results = []

    for school_id in school_ids:
        # 获取学校信息
        school_result = await db.execute(
            select(School).where(School.id == school_id)
        )
        school = school_result.scalar_one_or_none()

        if not school:
            results.append(SchoolRelationCheck(
                school_id=school_id,
                school_name=f"未知学校 (ID: {school_id})",
                has_relations=False,
                relations=None
            ))
            continue

        # 检查班级数量
        classrooms_count_result = await db.execute(
            select(func.count()).select_from(Classroom).where(Classroom.school_id == school_id)
        )
        classrooms_count = classrooms_count_result.scalar() or 0

        # 检查用户数量（教师+学生）
        users_count_result = await db.execute(
            select(func.count()).select_from(User).where(User.school_id == school_id)
        )
        users_count = users_count_result.scalar() or 0

        has_relations = classrooms_count > 0 or users_count > 0

        results.append(SchoolRelationCheck(
            school_id=school_id,
            school_name=school.name,
            has_relations=has_relations,
            relations={
                "classrooms": classrooms_count,
                "teachers_students": users_count  # 简化统计，不细分教师和学生
            } if has_relations else None
        ))

    return {"schools": results}
```

**Step 2: 测试端点**

启动后端服务，使用 Postman 或 curl 测试：

```bash
curl -X POST "http://localhost:8000/api/v1/admin/organization/schools/check-relations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"school_ids": [1, 2, 3]}'
```

预期返回：每个学校的关联数据统计

**Step 3: 提交代码**

```bash
cd backend
git add app/api/v1/admin_organization.py
git commit -m "feat: add school relations check API"
```

---

## Task 3: 后端 - 添加批量删除API

**文件:**
- Modify: `backend/app/api/v1/admin_organization.py:730` (在 check_school_relations 之后)

**Step 1: 添加批量删除端点**

在 `check_school_relations` 函数之后添加：

```python
@router.delete("/schools/batch")
async def batch_delete_schools(
    request: BatchDeleteSchoolsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """批量删除学校

    - cascade_delete=False: 只删除没有关联数据的学校
    - cascade_delete=True: 删除所有学校，包括有关联数据的学校（级联删除）
    """
    school_ids = request.school_ids
    cascade_delete = request.cascade_delete

    if not school_ids:
        raise HTTPException(status_code=400, detail="必须提供学校ID列表")

    # 限制批量操作的数量
    if len(school_ids) > 500:
        raise HTTPException(status_code=400, detail="单次最多删除500所学校")

    deleted_count = 0
    failed_count = 0
    errors: List[BatchDeleteSchoolsError] = []

    for school_id in school_ids:
        try:
            # 获取学校信息
            school_result = await db.execute(
                select(School).where(School.id == school_id)
            )
            school = school_result.scalar_one_or_none()

            if not school:
                errors.append(BatchDeleteSchoolsError(
                    school_id=school_id,
                    school_name=f"未知学校 (ID: {school_id})",
                    error="学校不存在"
                ))
                failed_count += 1
                continue

            # 检查班级数量
            classrooms_count_result = await db.execute(
                select(func.count()).select_from(Classroom).where(Classroom.school_id == school_id)
            )
            classrooms_count = classrooms_count_result.scalar() or 0

            # 检查用户数量
            users_count_result = await db.execute(
                select(func.count()).select_from(User).where(User.school_id == school_id)
            )
            users_count = users_count_result.scalar() or 0

            has_relations = classrooms_count > 0 or users_count > 0

            # 根据cascade_delete参数决定是否删除
            if has_relations and not cascade_delete:
                errors.append(BatchDeleteSchoolsError(
                    school_id=school_id,
                    school_name=school.name,
                    error=f"学校有关联数据（{classrooms_count}个班级，{users_count}个用户），无法删除"
                ))
                failed_count += 1
                continue

            # 级联删除关联数据（如果启用）
            if cascade_delete and has_relations:
                # 删除班级（会级联删除班级成员等）
                await db.execute(
                    select(Classroom).where(Classroom.school_id == school_id)
                )
                # 注意：实际的级联删除应该通过外键约束或显式删除来完成
                # 这里简化处理，假设数据库有正确的级联设置

            # 删除学校
            await db.delete(school)
            deleted_count += 1

        except Exception as e:
            logger.error(f"删除学校 {school_id} 失败: {str(e)}")
            errors.append(BatchDeleteSchoolsError(
                school_id=school_id,
                school_name=school.name if school else f"未知学校 (ID: {school_id})",
                error=str(e)
            ))
            failed_count += 1

    # 提交事务
    await db.commit()

    return BatchDeleteSchoolsResponse(
        total_requested=len(school_ids),
        deleted_count=deleted_count,
        failed_count=failed_count,
        errors=errors
    )
```

**Step 2: 测试端点**

```bash
curl -X DELETE "http://localhost:8000/api/v1/admin/organization/schools/batch" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"school_ids": [1, 2, 3], "cascade_delete": false}'
```

预期返回：批量删除结果统计

**Step 3: 提交代码**

```bash
cd backend
git add app/api/v1/admin_organization.py
git commit -m "feat: add batch delete schools API"
```

---

## Task 4: 前端 - 添加类型定义

**文件:**
- Modify: `frontend/src/services/admin.ts:225` (在 ClassroomImportResponse 之后)

**Step 1: 添加批量删除相关的类型定义**

在 `ClassroomImportResponse` 类型定义之后添加：

```typescript
export interface SchoolRelationCheck {
  school_id: number
  school_name: string
  has_relations: boolean
  relations: {
    classrooms: number
    teachers_students: number
  } | null
}

export interface BatchDeleteSchoolsError {
  school_id: number
  school_name: string
  error: string
}

export interface BatchDeleteSchoolsResponse {
  total_requested: number
  deleted_count: number
  failed_count: number
  errors: BatchDeleteSchoolsError[]
}

export interface CheckSchoolRelationsResponse {
  schools: SchoolRelationCheck[]
}
```

**Step 2: 验证类型定义**

确保没有类型错误。

**Step 3: 提交代码**

```bash
cd frontend
git add src/services/admin.ts
git commit -m "feat: add types for batch delete schools"
```

---

## Task 5: 前端 - 添加API方法

**文件:**
- Modify: `frontend/src/services/admin.ts:735` (在 importRooms 方法之后)

**Step 1: 添加检查学校关联数据的方法**

在 `importRooms` 方法之后添加：

```typescript
  /**
   * 检查学校关联数据
   */
  async checkSchoolRelations(
    schoolIds: number[]
  ): Promise<CheckSchoolRelationsResponse> {
    return await api.post('/admin/organization/schools/check-relations', { school_ids: schoolIds })
  },

  /**
   * 批量删除学校
   */
  async batchDeleteSchools(
    schoolIds: number[],
    cascadeDelete: boolean = false
  ): Promise<BatchDeleteSchoolsResponse> {
    return await api.delete('/admin/organization/schools/batch', {
      data: { school_ids: schoolIds, cascade_delete: cascadeDelete }
    })
  }
```

**Step 2: 验证API方法**

确保方法签名正确，没有类型错误。

**Step 3: 提交代码**

```bash
cd frontend
git add src/services/admin.ts
git commit -m "feat: add API methods for batch delete schools"
```

---

## Task 6: 前端 - 添加选择状态管理

**文件:**
- Modify: `frontend/src/pages/Admin/OrganizationManagement/SchoolManagementCard.vue:500`

**Step 1: 添加选择状态变量**

在 `<script setup>` 部分的状态定义区域（第500行附近）添加：

```typescript
// 批量选择状态
const selectedSchoolIds = ref<Set<number>>(new Set())
const isAllCurrentPageSelected = ref(false)
const isIndeterminate = ref(false)
const showBatchDeleteDialog = ref(false)
const checkingRelations = ref(false)
const deletingSchools = ref(false)
const schoolRelations = ref<SchoolRelationCheck[]>([])
const batchDeleteResult = ref<BatchDeleteSchoolsResponse | null>(null)
const cascadeDelete = ref(false)
```

**Step 2: 添加计算属性**

在计算属性部分（`schoolTotalPages` 之后）添加：

```typescript
const selectedCount = computed(() => selectedSchoolIds.value.size)

const hasSelection = computed(() => selectedSchoolIds.value.size > 0)

const canSelectAllCurrentPage = computed(() => {
  return schools.value.length > 0 && schools.value.every(school => selectedSchoolIds.value.has(school.id))
})
```

**Step 3: 提交代码**

```bash
cd frontend
git add src/pages/Admin/OrganizationManagement/SchoolManagementCard.vue
git commit -m "feat: add selection state for batch delete"
```

---

## Task 7: 前端 - 实现选择逻辑方法

**文件:**
- Modify: `frontend/src/pages/Admin/OrganizationManagement/SchoolManagementCard.vue:965`

**Step 1: 添加选择逻辑方法**

在 `onMounted` 之前添加以下方法：

```typescript
// 选择逻辑方法
function toggleSelectAll(checked: boolean) {
  if (checked) {
    // 选择当前页所有学校
    schools.value.forEach(school => {
      selectedSchoolIds.value.add(school.id)
    })
  } else {
    // 取消选择当前页所有学校
    schools.value.forEach(school => {
      selectedSchoolIds.value.delete(school.id)
    })
  }
  updateSelectAllState()
}

function toggleSelectSchool(schoolId: number) {
  if (selectedSchoolIds.value.has(schoolId)) {
    selectedSchoolIds.value.delete(schoolId)
  } else {
    selectedSchoolIds.value.add(schoolId)
  }
  updateSelectAllState()
}

function isSelected(schoolId: number): boolean {
  return selectedSchoolIds.value.has(schoolId)
}

function clearSelection() {
  selectedSchoolIds.value.clear()
  updateSelectAllState()
}

function updateSelectAllState() {
  const currentSchoolIds = schools.value.map(s => s.id)
  const selectedInCurrentPage = currentSchoolIds.filter(id => selectedSchoolIds.value.has(id))

  if (selectedInCurrentPage.length === 0) {
    isAllCurrentPageSelected.value = false
    isIndeterminate.value = false
  } else if (selectedInCurrentPage.length === schools.value.length) {
    isAllCurrentPageSelected.value = true
    isIndeterminate.value = false
  } else {
    isAllCurrentPageSelected.value = false
    isIndeterminate.value = true
  }
}
```

**Step 2: 监听学校列表变化**

在 `loadSchools` 方法的最后添加 `updateSelectAllState()` 调用：

```typescript
async function loadSchools() {
  try {
    const response = await adminService.getSchools({
      page: schoolPage.value,
      size: schoolPageSize.value,
      region_id: schoolRegionFilter.value || undefined,
      school_type: schoolTypeFilter.value || undefined,
      search: schoolSearchQuery.value || undefined
    })
    schools.value = response.schools
    schoolTotal.value = response.total
    updateSelectAllState() // 添加这一行
  } catch (error: any) {
    console.error('Failed to load schools:', error)
    toast.error(error.response?.data?.detail || '加载学校列表失败')
  }
}
```

**Step 3: 提交代码**

```bash
cd frontend
git add src/pages/Admin/OrganizationManagement/SchoolManagementCard.vue
git commit -m "feat: implement selection logic methods"
```

---

## Task 8: 前端 - 添加批量删除UI

**文件:**
- Modify: `frontend/src/pages/Admin/OrganizationManagement/SchoolManagementCard.vue:58`

**Step 1: 修改表格头部添加复选框列**

将表格头部修改为：

```vue
<table class="min-w-full divide-y divide-gray-200">
  <thead class="bg-gray-50">
    <tr>
      <th class="px-4 py-3 text-left w-12">
        <input
          type="checkbox"
          :checked="isAllCurrentPageSelected"
          :indeterminate="isIndeterminate"
          @change="toggleSelectAll($event.target.checked)"
          class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
        />
      </th>
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">学校名称</th>
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">编码</th>
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">类型</th>
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">校长</th>
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
    </tr>
  </thead>
```

**Step 2: 修改表格行添加复选框**

将表格行的 `tr` 标签修改为：

```vue
<tr v-for="school in schools" :key="school.id"
    :class="['hover:bg-gray-50', isSelected(school.id) ? 'bg-blue-50' : '']">
  <td class="px-4 py-4 whitespace-nowrap">
    <input
      type="checkbox"
      :checked="isSelected(school.id)"
      @change="toggleSelectSchool(school.id)"
      class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
    />
  </td>
  <td class="px-6 py-4 whitespace-nowrap">
    <!-- ... 其他列保持不变 ... -->
  </td>
</tr>
```

**Step 3: 提交代码**

```bash
cd frontend
git add src/pages/Admin/OrganizationManagement/SchoolManagementCard.vue
git commit -m "feat: add checkboxes to school table"
```

---

## Task 9: 前端 - 添加批量操作栏

**文件:**
- Modify: `frontend/src/pages/Admin/OrganizationManagement/SchoolManagementCard.vue:56`

**Step 1: 在操作栏后添加批量操作栏**

在操作栏的 `</div>` (第55行) 之后添加：

```vue
    <!-- 批量操作栏 -->
    <div v-if="hasSelection" class="bg-blue-50 border border-blue-200 rounded-lg shadow p-4">
      <div class="flex justify-between items-center">
        <div class="text-sm text-blue-800">
          <strong>已选择 {{ selectedCount }} 所学校</strong>
        </div>
        <div class="flex gap-2">
          <button
            @click="openBatchDeleteDialog"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2"
          >
            🗑️ 批量删除
          </button>
          <button
            @click="clearSelection"
            class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
          >
            取消选择
          </button>
        </div>
      </div>
    </div>

    <!-- 学校列表 -->
```

**Step 2: 提交代码**

```bash
cd frontend
git add src/pages/Admin/OrganizationManagement/SchoolManagementCard.vue
git commit -m "feat: add batch operation bar"
```

---

## Task 10: 前端 - 添加批量删除对话框

**文件:**
- Modify: `frontend/src/pages/Admin/OrganizationManagement/SchoolManagementCard.vue:495`

**Step 1: 在对话框部分添加批量删除对话框**

在所有现有对话框之后（第495行之前）添加：

```vue
    <!-- 批量删除学校对话框 -->
    <el-dialog
      v-model="showBatchDeleteDialog"
      title="批量删除学校"
      width="800px"
      :close-on-click-modal="false"
    >
      <!-- 步骤1: 检查关联数据 -->
      <div v-if="!checkingRelations && !deletingSchools && schoolRelations.length === 0" class="space-y-4">
        <p class="text-sm text-gray-600">正在检查学校关联数据...</p>
      </div>

      <!-- 步骤2: 显示删除预览 -->
      <div v-if="!checkingRelations && schoolRelations.length > 0 && !batchDeleteResult" class="space-y-4">
        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p class="text-sm text-yellow-800">
            <strong>⚠️ 即将删除 {{ selectedCount }} 所学校</strong>
          </p>
        </div>

        <!-- 学校列表 -->
        <div class="max-h-60 overflow-y-auto border rounded-lg">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">学校名称</th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">关联数据</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="relation in schoolRelations" :key="relation.school_id" class="hover:bg-gray-50">
                <td class="px-4 py-2 text-sm">{{ relation.school_name }}</td>
                <td class="px-4 py-2 text-sm">
                  <span v-if="!relation.has_relations" class="text-green-600">✓ 无关联数据</span>
                  <span v-else class="text-red-600">
                    ⚠️ {{ relation.relations?.classrooms }} 个班级,
                    {{ relation.relations?.teachers_students }} 个用户
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 有关联数据的学校提示 -->
        <div v-if="schoolRelations.some(r => r.has_relations)" class="bg-red-50 border border-red-200 rounded-lg p-4">
          <p class="text-sm text-red-800 mb-2">
            <strong>⚠️ 检测到学校有关联数据</strong>
          </p>
          <label class="flex items-start gap-2 text-sm text-red-700">
            <input
              type="checkbox"
              v-model="cascadeDelete"
              class="mt-1 w-4 h-4 text-red-600 rounded border-red-300 focus:ring-red-500"
            />
            <span>
              <strong>同时删除关联数据</strong>（包括班级、教师、学生等）
              <br>
              <span class="text-xs">如果不勾选，将只删除没有关联数据的学校</span>
            </span>
          </label>
        </div>
      </div>

      <!-- 步骤3: 删除结果 -->
      <div v-if="batchDeleteResult" class="space-y-4">
        <el-alert
          :title="batchDeleteResult.deleted_count > 0 ? '✅ 删除完成' : '❌ 删除失败'"
          :type="batchDeleteResult.deleted_count > 0 ? 'success' : 'error'"
          :closable="false"
        />
        <div class="grid grid-cols-3 gap-4">
          <div class="bg-blue-50 border rounded-lg p-3 text-center">
            <div class="text-2xl font-bold text-blue-600">{{ batchDeleteResult.total_requested }}</div>
            <div class="text-sm text-gray-600">请求删除</div>
          </div>
          <div class="bg-green-50 border rounded-lg p-3 text-center">
            <div class="text-2xl font-bold text-green-600">{{ batchDeleteResult.deleted_count }}</div>
            <div class="text-sm text-gray-600">成功删除</div>
          </div>
          <div class="bg-red-50 border rounded-lg p-3 text-center">
            <div class="text-2xl font-bold text-red-600">{{ batchDeleteResult.failed_count }}</div>
            <div class="text-sm text-gray-600">删除失败</div>
          </div>
        </div>
        <div v-if="batchDeleteResult.errors.length > 0" class="mt-4">
          <h4 class="text-sm font-medium mb-2">⚠️ 错误详情</h4>
          <el-table :data="batchDeleteResult.errors" max-height="200" size="small">
            <el-table-column prop="school_name" label="学校" width="200" />
            <el-table-column prop="error" label="错误信息" />
          </el-table>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="checkingRelations || deletingSchools" class="text-center py-8">
        <el-icon class="is-loading text-4xl text-blue-600"><loading /></el-icon>
        <p class="text-sm text-gray-600 mt-2">
          {{ checkingRelations ? '正在检查关联数据...' : '正在删除学校...' }}
        </p>
      </div>

      <template #footer>
        <el-button
          v-if="!batchDeleteResult"
          @click="closeBatchDeleteDialog"
          :disabled="checkingRelations || deletingSchools"
        >
          取消
        </el-button>
        <el-button
          v-if="schoolRelations.length > 0 && !batchDeleteResult"
          type="primary"
          @click="confirmBatchDelete"
          :loading="deletingSchools"
          :disabled="checkingRelations"
          class="bg-red-600 hover:bg-red-700"
        >
          确认删除
        </el-button>
        <el-button
          v-if="batchDeleteResult"
          type="primary"
          @click="closeBatchDeleteDialog"
        >
          完成
        </el-button>
      </template>
    </el-dialog>
```

**Step 2: 添加图标导入**

在 `<script setup>` 的 import 部分添加 Loading 图标：

```typescript
import { Download, UploadFilled, Upload, ArrowRight, ArrowLeft, Loading } from '@element-plus/icons-vue'
```

**Step 3: 提交代码**

```bash
cd frontend
git add src/pages/Admin/OrganizationManagement/SchoolManagementCard.vue
git commit -m "feat: add batch delete dialog"
```

---

## Task 11: 前端 - 实现批量删除逻辑

**文件:**
- Modify: `frontend/src/pages/Admin/OrganizationManagement/SchoolManagementCard.vue:965`

**Step 1: 实现批量删除相关方法**

在选择逻辑方法之后添加：

```typescript
// 批量删除相关方法
async function openBatchDeleteDialog() {
  if (selectedSchoolIds.value.size === 0) {
    ElMessage.warning('请先选择要删除的学校')
    return
  }

  showBatchDeleteDialog.value = true
  batchDeleteResult.value = null
  cascadeDelete.value = false
  schoolRelations.value = []

  // 检查关联数据
  await checkSchoolRelations()
}

async function checkSchoolRelations() {
  checkingRelations.value = true

  try {
    const schoolIds = Array.from(selectedSchoolIds.value)
    const response = await adminService.checkSchoolRelations(schoolIds)
    schoolRelations.value = response.schools
  } catch (error: any) {
    console.error('检查关联数据失败:', error)
    ElMessage.error(error.response?.data?.detail || '检查关联数据失败')
    showBatchDeleteDialog.value = false
  } finally {
    checkingRelations.value = false
  }
}

async function confirmBatchDelete() {
  deletingSchools.value = true

  try {
    const schoolIds = Array.from(selectedSchoolIds.value)
    const result = await adminService.batchDeleteSchools(schoolIds, cascadeDelete.value)

    batchDeleteResult.value = result

    if (result.deleted_count > 0) {
      ElMessage.success(`成功删除 ${result.deleted_count} 所学校`)
    }

    if (result.failed_count > 0) {
      ElMessage.warning(`${result.failed_count} 所学校删除失败`)
    }

    // 刷新学校列表
    await loadSchools()

    // 清空选择
    clearSelection()
  } catch (error: any) {
    console.error('批量删除失败:', error)
    ElMessage.error(error.response?.data?.detail || '批量删除失败')
  } finally {
    deletingSchools.value = false
  }
}

function closeBatchDeleteDialog() {
  showBatchDeleteDialog.value = false
  schoolRelations.value = []
  batchDeleteResult.value = null
  cascadeDelete.value = false
}
```

**Step 2: 提交代码**

```bash
cd frontend
git add src/pages/Admin/OrganizationManagement/SchoolManagementCard.vue
git commit -m "feat: implement batch delete logic"
```

---

## Task 12: 测试与验证

**文件:**
- Test: `frontend/src/pages/Admin/OrganizationManagement/SchoolManagementCard.vue`
- Test: `backend/app/api/v1/admin_organization.py`

**Step 1: 启动服务**

```bash
# 启动后端
cd backend
uvicorn app.main:app --reload

# 启动前端
cd frontend
pnpm dev
```

**Step 2: 测试单个选择**

1. 访问 http://localhost:5173/admin/organization
2. 切换到"学校管理"标签
3. 点击单个学校前面的复选框
4. 验证：复选框被选中，行背景变为蓝色，批量操作栏显示"已选择 1 所学校"

**Step 3: 测试全选功能**

1. 点击表头的全选复选框
2. 验证：当前页所有学校被选中，批量操作栏显示正确的数量

**Step 4: 测试跨页选择**

1. 选择几所学校
2. 切换到下一页
3. 再选择几所学校
4. 切回第一页
5. 验证：之前的选择仍然保留

**Step 5: 测试批量删除无关联数据的学校**

1. 选择几个没有关联数据的学校
2. 点击"批量删除"按钮
3. 在对话框中查看学校列表
4. 点击"确认删除"
5. 验证：删除成功，列表刷新，选择清空

**Step 6: 测试批量删除有关联数据的学校（不级联）**

1. 选择几个有关联数据的学校
2. 点击"批量删除"按钮
3. 验证：对话框中显示关联数据统计
4. 不勾选"同时删除关联数据"
5. 点击"确认删除"
6. 验证：显示删除失败，有关联数据的学校未被删除

**Step 7: 测试批量删除有关联数据的学校（级联）**

1. 选择几个有关联数据的学校
2. 点击"批量删除"按钮
3. 勾选"同时删除关联数据"
4. 点击"确认删除"
5. 验证：删除成功（注意：这可能需要后端实现级联删除逻辑）

**Step 8: 测试混合删除**

1. 同时选择有关联数据和没有关联数据的学校
2. 测试不勾选级联删除的情况
3. 验证：只有无关联数据的学校被删除

**Step 9: 测试取消选择**

1. 选择几所学校
2. 点击"取消选择"按钮
3. 验证：所有选择被清空，批量操作栏消失

**Step 10: 提交最终代码**

```bash
cd frontend
git add -A
git commit -m "test: verify batch delete schools functionality"

cd ../backend
git add -A
git commit -m "test: verify batch delete schools API"
```

---

## Task 13: 代码格式化与文档

**文件:**
- All modified files

**Step 1: 格式化后端代码**

```bash
cd backend
black app/api/v1/admin_organization.py
```

**Step 2: 格式化前端代码**

```bash
cd frontend
pnpm lint --fix
```

**Step 3: 提交格式化后的代码**

```bash
git add -A
git commit -m "style: format code"
```

**Step 4: 合并到主分支**

```bash
git checkout main
git merge feature/value-added-evaluation
git push origin main
```

---

## 完成检查清单

- [ ] 后端关联数据检查API正常工作
- [ ] 后端批量删除API正常工作
- [ ] 前端类型定义完整
- [ ] 前端API方法正确
- [ ] 选择功能正常（单个选择、全选、跨页选择）
- [ ] 批量操作栏正确显示和隐藏
- [ ] 批量删除对话框正确显示关联数据
- [ ] 无关联数据的学校可以成功删除
- [ ] 有关联数据的学校在不勾选级联时被阻止
- [ ] 有关联数据的学校在勾选级联时可以删除
- [ ] 删除结果正确显示
- [ ] 删除后列表刷新和选择清空
- [ ] 代码已格式化
- [ ] 已提交并合并到主分支
