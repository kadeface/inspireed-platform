# 学校批量删除功能设计文档

**日期**: 2026-01-21
**页面**: `/admin/organization` - 学校管理
**功能**: 批量删除学校

---

## 功能概述

为学校管理页面添加批量删除功能，支持跨页选择、条件选择，并采用混合删除策略（无关联数据直接删除，有关联数据需确认）。

---

## 第一部分：选择功能UI

### 1.1 表格选择功能

**表格头部添加全选复选框：**
- 在表格第一列添加复选框列（约50px宽）
- 表头复选框支持：
  - 点击"全选"时选择当前页所有学校
  - 当当前页全部已选时，复选框显示选中状态
  - 当部分选中时，显示半选状态（indeterminate）

**表格行选择：**
- 每行第一列添加复选框
- 点击复选框选择/取消选择单个学校
- 支持跨页选择：使用 Set 结构保存已选择的学校ID，切换页面时保持选择状态
- 已选择的行添加视觉高亮（浅蓝色背景）

**批量选择操作栏：**
当选中至少一个学校时，在操作栏下方显示一个浮动操作条：
- 左侧显示"已选择 X 所学校"
- 右侧提供操作按钮：
  - "批量删除"按钮（红色，带删除图标）
  - "取消选择"按钮

### 1.2 高级选择功能

在操作栏添加"批量选择"下拉按钮，展开选项：
- **选择当前页全部**：选择当前页的所有学校
- **取消选择当前页**：取消当前页的选择
- **按条件选择**：弹出一个对话框，支持按以下条件批量选择：
  - 区域（单选/多选）
  - 学校类型（单选/多选）
  - 状态（激活/未激活）
  - 搜索关键词
- **反向选择**：反转当前选择状态
- **取消所有选择**：清除所有跨页选择

---

## 第二部分：批量删除交互流程

### 2.1 批量删除确认对话框

点击"批量删除"按钮后，显示一个确认对话框：

**基本信息：**
- 标题："批量删除学校"
- 显示待删除学校的数量和列表（最多显示前10条，超出显示"还有 N 条..."）
- 使用可滚动的列表展示学校名称、区域、类型

**智能检测与分类：**
在后台调用API检测每所学校的关联数据，将学校分为两类：
- **可直接删除的学校**：无关联数据（班级、教师、学生）
- **需要确认的学校**：有关联数据，显示关联详情：
  - 包含 X 个班级
  - 包含 Y 名教师
  - 包含 Z 名学生

**删除选项（仅当存在需要确认的学校时显示）：**
- 复选框："同时删除关联数据"（默认不勾选）
  - 勾选时：级联删除所有关联数据
  - 不勾选时：阻止删除有关联数据的学校，显示警告

**操作按钮：**
- "取消"：关闭对话框，保留所有选择
- "仅删除可删除的"（当有需要确认的学校时）：只删除无关联数据的学校
- "全部删除"（需二次确认）：显示红色警告，要求输入"DELETE"或学校数量来确认

---

## 第三部分：技术实现与状态管理

### 3.1 前端状态管理

**选择状态存储：**
```typescript
// 使用 Set 存储选中的学校ID，支持跨页选择
const selectedSchoolIds = ref<Set<number>>(new Set())
const isAllCurrentPageSelected = ref(false)
const isIndeterminate = ref(false)
```

**选择计算逻辑：**
- `toggleSelectAll(checked: boolean)`：全选/取消当前页
- `toggleSelectSchool(id: number)`：切换单个学校选择状态
- `isSelected(id: number)`：检查学校是否已选中
- `clearSelection()`：清空所有选择
- `selectByCondition(condition)`：按条件批量选择

**批量删除方法：**
```typescript
async function batchDeleteSchools(
  schoolIds: number[],
  cascadeDelete: boolean
): Promise<BatchDeleteResult>
```

返回结果包含：
- `success`: 成功删除的学校数量
- `failed`: 删除失败的数量
- `errors`: 错误详情列表（学校ID + 错误原因）

### 3.2 后端API需求

需要新增后端接口：

**检测关联数据接口：**
```
POST /api/admin/schools/check-relations
Request: { school_ids: number[] }
Response: {
  schools: [{
    school_id: number,
    has_relations: boolean,
    relations: {
      classrooms: number,
      teachers: number,
      students: number
    }
  }]
}
```

**批量删除接口：**
```
DELETE /api/admin/schools/batch
Request: {
  school_ids: number[],
  cascade_delete: boolean
}
Response: {
  deleted: number,
  failed: number,
  errors: Array<{school_id: number, error: string}>
}
```

---

## 实现文件清单

### 前端文件
1. `frontend/src/pages/Admin/OrganizationManagement/SchoolManagementCard.vue`
   - 添加复选框列
   - 实现选择逻辑
   - 添加批量删除对话框
   - 实现批量选择功能

2. `frontend/src/services/admin.ts`
   - 添加 `checkSchoolRelations()` 方法
   - 添加 `batchDeleteSchools()` 方法

3. `frontend/src/types/admin.ts`
   - 添加 `SchoolRelation` 类型定义
   - 添加 `BatchDeleteResult` 类型定义

### 后端文件
1. `backend/app/api/admin/schools.py`（或对应路由文件）
   - 添加 `POST /schools/check-relations` 路由
   - 添加 `DELETE /schools/batch` 路由

2. `backend/app/services/school_service.py`
   - 实现 `check_school_relations()` 方法
   - 实现 `batch_delete_schools()` 方法

---

## UI组件结构

### 新增组件

**BatchDeleteDialog.vue**（可选，也可内联在主组件中）：
```vue
<template>
  <el-dialog title="批量删除学校" v-model="visible">
    <!-- 学校列表 -->
    <!-- 关联数据警告 -->
    <!-- 级联删除选项 -->
    <!-- 操作按钮 -->
  </el-dialog>
</template>
```

**ConditionSelectDialog.vue**（可选）：
```vue
<template>
  <el-dialog title="按条件选择学校" v-model="visible">
    <!-- 区域选择 -->
    <!-- 类型选择 -->
    <!-- 状态选择 -->
    <!-- 搜索关键词 -->
  </el-dialog>
</template>
```

---

## 错误处理

1. **网络错误**：显示重试按钮
2. **权限错误**：提示用户无权限删除
3. **部分删除失败**：
   - 成功删除的学校显示成功提示
   - 删除失败的学校列出详细错误信息
   - 用户可选择重试失败的项
4. **全部删除失败**：保留选择状态，允许用户修正后重试

---

## 测试要点

- [ ] 单个学校选择/取消选择
- [ ] 当前页全选/取消全选
- [ ] 跨页选择后切换页面，选择状态保持
- [ ] 条件选择功能
- [ ] 反向选择功能
- [ ] 批量删除无关联数据的学校
- [ ] 批量删除有关联数据的学校（不勾选级联删除）
- [ ] 批量删除有关联数据的学校（勾选级联删除）
- [ ] 混合删除（部分有关联数据，部分无）
- [ ] 删除过程中的错误处理
- [ ] 删除后的列表刷新和选择状态清理
