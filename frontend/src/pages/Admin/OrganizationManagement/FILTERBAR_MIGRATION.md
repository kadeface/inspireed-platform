# FilterBar 组件迁移记录

## 迁移日期
2026-01-17

## 已迁移组件
- ✅ `ClassroomManagementCard.vue`

## 迁移详情

### ClassroomManagementCard.vue

#### 迁移前状态
- 使用 3 个独立的 `ref` 管理筛选值：
  - `allClassroomRegionFilter: ref<number | ''>('')`
  - `allClassroomSchoolFilter: ref<number | ''>('')`
  - `allClassroomGradeFilter: ref<number | ''>('')`
- 使用独立的 `ref` 管理搜索：
  - `allClassroomSearchQuery: ref('')`
- 有 3 个独立的筛选变化处理函数：
  - `handleRegionFilterChange()`
  - `handleSchoolFilterChange()`
  - `handleGradeFilterChange()`
- 模板中有 3 个 `<select>` 和 1 个 `<input>` 元素

#### 迁移后状态
- 使用统一的 `filters` 对象：
  ```typescript
  const classroomFilters = ref({
    region_id: undefined as number | undefined,
    school_id: undefined as number | undefined,
    grade_id: undefined as number | undefined,
  })
  const classroomSearchQuery = ref('')
  ```
- 定义筛选配置（计算属性）：
  ```typescript
  const classroomFilterConfigs = computed<FilterConfig[]>(() => [
    {
      key: 'region_id',
      label: '县区',
      placeholder: '所有县区',
      options: allRegions.value,
      type: 'number',
    },
    {
      key: 'school_id',
      label: '学校',
      placeholder: '所有学校',
      computedOptions: () => filteredSchoolsForClassroom.value,
      dependsOn: 'region_id', // 区域变化时自动清空学校筛选
      type: 'number',
    },
    {
      key: 'grade_id',
      label: '年级',
      placeholder: '所有年级',
      options: grades.value,
      type: 'number',
    },
  ])
  ```
- 定义搜索配置：
  ```typescript
  const classroomSearchConfig: SearchConfig = {
    placeholder: '搜索学校或班级名称...',
    debounce: false,
    enterToSearch: true, // 按 Enter 键触发搜索
  }
  ```
- 统一使用 `FilterBar` 组件替换原有 HTML：
  ```vue
  <FilterBar
    :filters="classroomFilterConfigs"
    :search-config="classroomSearchConfig"
    v-model="classroomFilters"
    v-model:search-model-value="classroomSearchQuery"
    @filter-change="handleClassroomFilterChange"
    @search-enter="handleClassroomSearchEnter"
  >
    <template #extra>
      <button @click="loadAllClassrooms" class="...">
        🔄 刷新
      </button>
    </template>
  </FilterBar>
  ```
- 简化为 1 个筛选变化处理函数：
  ```typescript
  async function handleClassroomFilterChange(key: string, value: any) {
    if (key === 'region_id') {
      // 区域改变时，重新加载学校列表（FilterBar 会自动清空 school_id）
      classroomPagination.value.page = 1
      await loadAllSchools()
      await loadAllClassrooms()
    } else {
      // 学校或年级筛选改变时，重置页码并加载班级列表
      classroomPagination.value.page = 1
      loadAllClassrooms()
    }
  }

  function handleClassroomSearchEnter(value: string) {
    classroomPagination.value.page = 1
    loadAllClassrooms()
  }
  ```

#### 代码行数变化
- 模板：从 ~40 行 HTML 减少到 ~12 行组件调用
- 脚本：筛选相关代码从 ~50 行减少到 ~30 行（但增加了配置代码）
- 总体：代码更简洁、更易维护

#### 功能验证
- ✅ 区域筛选正常工作
- ✅ 学校筛选根据区域级联过滤（依赖关系）
- ✅ 年级筛选独立工作
- ✅ 搜索框按 Enter 键触发搜索
- ✅ 筛选变化时页码自动重置
- ✅ 刷新按钮位置合理（在 FilterBar 的 extra 插槽中）

## 待迁移组件

以下组件仍使用原有的筛选实现方式，建议逐步迁移：

1. `SchoolManagementCard.vue`
   - 筛选器：区域、类型
   - 搜索：学校名称

2. `StudentManagementTab.vue`
   - 筛选器：区域、学校、年级、班级
   - 搜索：姓名、学号、学籍号

3. `TeacherAssignmentTab.vue`
   - 筛选器：区域、学期、年级、学科、学校、教师、状态
   - 搜索：无

4. `TeacherProfileTab.vue`
   - 筛选器：区域、学校
   - 搜索：姓名、邮箱、工号

5. `PositionTypeTab.vue`
   - 筛选器：类别、状态
   - 搜索：职务名称、代码

6. `RoomManagementCard.vue`
   - 筛选器：学校、类型、建筑
   - 搜索：课室名称或编码

## 迁移收益

1. **代码复用**：多个组件共享统一的筛选组件，减少重复代码
2. **易于维护**：筛选逻辑集中管理，修改时只需更新 FilterBar 组件
3. **一致性**：所有页面的筛选交互保持一致，提升用户体验
4. **类型安全**：使用 TypeScript 类型定义，减少运行时错误
5. **功能增强**：自动支持级联筛选、防抖搜索等高级功能

## 注意事项

1. **向后兼容**：迁移时确保功能逻辑保持一致，不影响现有业务
2. **测试覆盖**：迁移后需要测试所有筛选场景，特别是级联筛选
3. **渐进迁移**：建议逐个组件迁移，而不是一次性全部替换
4. **文档更新**：及时更新组件文档和使用示例

## 相关文件

- 通用组件：`frontend/src/components/Common/FilterBar.vue`
- 使用文档：`frontend/src/components/Common/FilterBar.example.md`
- 迁移示例：`frontend/src/pages/Admin/OrganizationManagement/ClassroomManagementCard.vue`