# FilterBar 通用筛选组件使用指南

## 简介

`FilterBar` 是一个通用的筛选组件，支持多个下拉筛选器和搜索框，可以用于替换组织管理页面中重复的筛选代码。

## 基本用法

### 1. 导入组件

```vue
<script setup lang="ts">
import FilterBar, { type FilterConfig, type SearchConfig } from '@/components/Common/FilterBar.vue'
</script>
```

### 2. 定义筛选配置

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'

// 筛选器配置
const filterConfigs: FilterConfig[] = [
  {
    key: 'region_id',
    label: '区域',
    placeholder: '所有区域',
    options: allRegions.value,
    type: 'number',
  },
  {
    key: 'school_id',
    label: '学校',
    placeholder: '所有学校',
    computedOptions: () => filteredSchools.value, // 使用计算属性
    dependsOn: 'region_id', // 依赖区域筛选，当区域改变时会被清空
    type: 'number',
  },
  {
    key: 'grade_id',
    label: '年级',
    placeholder: '所有年级',
    options: grades.value,
    type: 'number',
  },
]

// 搜索配置
const searchConfig: SearchConfig = {
  placeholder: '搜索学校或班级名称...',
  debounce: true,
  debounceDelay: 300,
  enterToSearch: false, // 实时搜索
}

// 筛选值
const filters = ref({
  region_id: undefined,
  school_id: undefined,
  grade_id: undefined,
})

// 搜索值
const searchQuery = ref('')

// 计算属性：根据区域筛选学校
const filteredSchools = computed(() => {
  if (!filters.value.region_id) {
    return allSchools.value
  }
  return allSchools.value.filter(s => s.region_id === filters.value.region_id)
})
</script>
```

### 3. 在模板中使用

```vue
<template>
  <div class="bg-white rounded-lg shadow p-4">
    <div class="flex justify-between items-center">
      <!-- 操作按钮 -->
      <div class="flex gap-4">
        <button @click="openCreateModal" class="px-4 py-2 bg-blue-600 text-white rounded-lg">
          + 创建
        </button>
      </div>

      <!-- 筛选组件 -->
      <FilterBar
        :filters="filterConfigs"
        :search-config="searchConfig"
        v-model="filters"
        v-model:search-model-value="searchQuery"
        @filter-change="handleFilterChange"
        @search="handleSearch"
      >
        <template #extra="{ filterValues, searchValue }">
          <button
            @click="loadData"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            🔄 刷新
          </button>
        </template>
      </FilterBar>
    </div>
  </div>
</template>
```

## 完整示例：改造 ClassroomManagementCard

### 改造前（原代码）

```vue
<template>
  <div class="flex gap-2">
    <select v-model="allClassroomRegionFilter" @change="handleRegionFilterChange">
      <option value="">所有县区</option>
      <option v-for="region in allRegions" :key="region.id" :value="region.id">
        {{ region.name }}
      </option>
    </select>
    <select v-model="allClassroomSchoolFilter" @change="handleSchoolFilterChange">
      <option value="">所有学校</option>
      <option v-for="school in filteredSchoolsForClassroom" :key="school.id" :value="school.id">
        {{ school.name }}
      </option>
    </select>
    <select v-model="allClassroomGradeFilter" @change="handleGradeFilterChange">
      <option value="">所有年级</option>
      <option v-for="grade in grades" :key="grade.id" :value="grade.id">
        {{ grade.name }}
      </option>
    </select>
    <input
      v-model="allClassroomSearchQuery"
      @keyup.enter="loadAllClassrooms"
      type="text"
      placeholder="搜索学校或班级名称..."
      class="px-3 py-2 border rounded-lg w-64"
    />
  </div>
</template>

<script setup lang="ts">
const allClassroomSearchQuery = ref('')
const allClassroomRegionFilter = ref<number | ''>('')
const allClassroomSchoolFilter = ref<number | ''>('')
const allClassroomGradeFilter = ref<number | ''>('')

const filteredSchoolsForClassroom = computed(() => {
  if (!allClassroomRegionFilter.value) {
    return schools.value
  }
  return schools.value.filter(school => school.region_id === Number(allClassroomRegionFilter.value))
})

function handleRegionFilterChange() {
  allClassroomSchoolFilter.value = ''
  loadAllClassrooms()
}

function handleSchoolFilterChange() {
  classroomPagination.page = 1
  loadAllClassrooms()
}

function handleGradeFilterChange() {
  classroomPagination.page = 1
  loadAllClassrooms()
}
</script>
```

### 改造后（使用 FilterBar）

```vue
<template>
  <div class="bg-white rounded-lg shadow p-4">
    <div class="flex justify-between items-center">
      <div class="flex gap-4">
        <button @click="openCreateClassroomModal" class="px-4 py-2 bg-blue-600 text-white rounded-lg">
          + 创建班级
        </button>
      </div>

      <FilterBar
        :filters="classroomFilterConfigs"
        :search-config="classroomSearchConfig"
        v-model="classroomFilters"
        v-model:search-model-value="classroomSearchQuery"
        @filter-change="handleClassroomFilterChange"
        @search="handleClassroomSearch"
      >
        <template #extra>
          <button
            @click="loadAllClassrooms"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            🔄 刷新
          </button>
        </template>
      </FilterBar>
    </div>
  </div>
</template>

<script setup lang="ts">
import FilterBar, { type FilterConfig, type SearchConfig } from '@/components/Common/FilterBar.vue'

// 筛选器配置
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
    dependsOn: 'region_id', // 区域变化时自动清空
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

// 搜索配置
const classroomSearchConfig: SearchConfig = {
  placeholder: '搜索学校或班级名称...',
  debounce: true,
  debounceDelay: 300,
  enterToSearch: false,
}

// 筛选值（使用统一的 filters 对象）
const classroomFilters = ref({
  region_id: undefined,
  school_id: undefined,
  grade_id: undefined,
})

// 搜索值
const classroomSearchQuery = ref('')

// 计算属性：根据区域筛选学校
const filteredSchoolsForClassroom = computed(() => {
  if (!classroomFilters.value.region_id) {
    return schools.value
  }
  return schools.value.filter(school => school.region_id === classroomFilters.value.region_id)
})

// 处理筛选变化
function handleClassroomFilterChange(key: string, value: any) {
  if (key === 'region_id') {
    // 区域改变时，页码已自动重置（在 loadAllClassrooms 中处理）
    loadAllClassrooms()
  } else {
    classroomPagination.page = 1
    loadAllClassrooms()
  }
}

// 处理搜索
function handleClassroomSearch(value: string) {
  classroomPagination.page = 1
  loadAllClassrooms()
}

// 加载班级列表（需要调整参数映射）
async function loadAllClassrooms() {
  try {
    allClassroomsLoading.value = true
    const params: any = {
      page: classroomPagination.page,
      size: classroomPagination.size,
    }
    
    if (classroomFilters.value.region_id) {
      params.region_id = classroomFilters.value.region_id
    }
    if (classroomFilters.value.school_id) {
      params.school_id = classroomFilters.value.school_id
    }
    if (classroomFilters.value.grade_id) {
      params.grade_id = classroomFilters.value.grade_id
    }
    if (classroomSearchQuery.value) {
      params.search = classroomSearchQuery.value
    }

    const response = await classroomService.getAllClassrooms(params)
    // ... 处理响应
  } catch (error) {
    // ... 错误处理
  } finally {
    allClassroomsLoading.value = false
  }
}
</script>
```

## 更多使用场景

### 1. 简单筛选（只有搜索框）

```vue
<FilterBar
  :filters="[]"
  :search-config="{ placeholder: '搜索...' }"
  v-model:search-model-value="searchQuery"
  @search="handleSearch"
/>
```

### 2. 字符串类型筛选

```vue
const typeFilterConfig: FilterConfig = {
  key: 'school_type',
  label: '类型',
  placeholder: '所有类型',
  options: [
    { id: '小学', name: '小学' },
    { id: '初中', name: '初中' },
    { id: '高中', name: '高中' },
  ],
  type: 'string',
}
```

### 3. 布尔类型筛选

```vue
const statusFilterConfig: FilterConfig = {
  key: 'is_active',
  label: '状态',
  placeholder: '全部状态',
  options: [
    { id: true, name: '激活' },
    { id: false, name: '停用' },
  ],
  type: 'boolean',
}
```

### 4. 自定义样式

```vue
const filterConfigs: FilterConfig[] = [
  {
    key: 'region_id',
    label: '区域',
    options: regions.value,
    class: 'custom-select',
    style: { minWidth: '150px' },
  },
]

const searchConfig: SearchConfig = {
  placeholder: '搜索...',
  class: 'custom-search',
  style: { width: '300px' },
}
```

### 5. 使用 ref 获取组件实例

```vue
<template>
  <FilterBar ref="filterBarRef" :filters="filterConfigs" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const filterBarRef = ref<InstanceType<typeof FilterBar>>()

// 重置所有筛选器
function resetFilters() {
  filterBarRef.value?.reset()
}

// 设置筛选值
function setRegionFilter(regionId: number) {
  filterBarRef.value?.setFilter('region_id', regionId)
}
</script>
```

## API 参考

### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `filters` | `FilterConfig[]` | `[]` | 筛选器配置列表（必填） |
| `searchConfig` | `SearchConfig` | `undefined` | 搜索配置（可选） |
| `modelValue` | `Record<string, any>` | `{}` | 筛选值（v-model） |
| `searchModelValue` | `string` | `''` | 搜索值（v-model） |

### Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| `update:modelValue` | `value: Record<string, any>` | 筛选值变化时触发 |
| `update:searchModelValue` | `value: string` | 搜索值变化时触发 |
| `filter-change` | `key: string, value: any, allFilters: Record<string, any>` | 筛选器值变化时触发 |
| `search` | `value: string` | 搜索输入时触发（带防抖） |
| `search-enter` | `value: string` | 按 Enter 键搜索时触发 |

### Methods (通过 ref 调用)

| 方法名 | 参数 | 返回值 | 说明 |
|--------|------|--------|------|
| `getFilters()` | - | `Record<string, any>` | 获取所有筛选值 |
| `getSearch()` | - | `string` | 获取搜索值 |
| `reset()` | - | `void` | 重置所有筛选器和搜索框 |
| `setFilter(key, value)` | `key: string, value: any` | `void` | 设置指定筛选器的值 |
| `setSearch(value)` | `value: string` | `void` | 设置搜索值 |

### Slots

| 插槽名 | 作用域 | 说明 |
|--------|--------|------|
| `extra` | `{ filterValues, searchValue }` | 额外的操作按钮等 |

## 注意事项

1. **级联筛选**：使用 `dependsOn` 属性可以实现级联筛选，当父筛选器变化时，子筛选器会自动清空。

2. **类型一致性**：筛选器的 `type` 决定了空值的类型（`undefined`、`''` 或 `false`），需要与后端 API 保持一致。

3. **计算属性选项**：如果选项列表需要根据其他筛选器的值动态计算，使用 `computedOptions` 而不是 `options`。

4. **防抖搜索**：默认搜索框使用 300ms 防抖，避免频繁请求。如果需要在输入时立即触发，设置 `debounce: false`。

5. **Enter 键搜索**：如果设置 `enterToSearch: true`，搜索只会在按 Enter 键时触发。

## 迁移建议

1. **逐步迁移**：不要一次性替换所有组件，建议先在一个组件中试用，确认无误后再迁移其他组件。

2. **保持 API 兼容**：确保替换后不影响现有的数据加载逻辑和用户体验。

3. **统一命名**：建议统一使用 `filters` 对象管理所有筛选值，而不是多个独立的 ref。

4. **测试覆盖**：迁移后需要测试所有筛选场景，特别是级联筛选的逻辑。