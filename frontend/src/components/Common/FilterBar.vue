<template>
  <div class="filter-bar">
    <div class="flex flex-nowrap items-center gap-2 overflow-x-auto">
      <!-- 下拉筛选器 -->
      <template v-for="(filter, index) in normalizedFilters" :key="`filter-${filter.key}-${index}`">
        <select
          v-model="filterValues[filter.key]"
          @change="handleFilterChange(filter)"
          :class="['px-3 py-2 border rounded-lg flex-shrink-0', filter.class || '']"
          :style="filter.style || { minWidth: '120px', maxWidth: '180px' }"
        >
          <option :value="getEmptyValue(filter.type)">
            {{ filter.placeholder || `所有${filter.label}` }}
          </option>
          <option
            v-for="option in getFilterOptions(filter)"
            :key="`option-${filter.key}-${getOptionValue(option, filter.valueKey)}`"
            :value="getOptionValue(option, filter.valueKey)"
          >
            {{ getOptionLabel(option, filter.labelKey) }}
          </option>
        </select>
      </template>

      <!-- 搜索框（支持自动完成） -->
      <el-autocomplete
        v-if="searchConfig"
        v-model="searchValue"
        :fetch-suggestions="searchConfig.fetchSuggestions"
        :placeholder="searchConfig.placeholder || '搜索...'"
        :trigger-on-focus="searchConfig.triggerOnFocus !== false"
        :clearable="searchConfig.clearable !== false"
        @select="handleSuggestionSelect"
        @input="handleSearchInput"
        @keyup.enter="handleSearchEnter"
        :class="['flex-shrink-0', searchConfig.class || '']"
        :style="searchConfig.style || { minWidth: '180px', width: '240px', maxWidth: '320px' }"
        class="filter-bar-search"
      >
        <template #default="{ item }">
          <div class="flex items-center gap-2">
            <span v-if="item.type" class="text-xs px-1.5 py-0.5 rounded" :class="getTypeClass(item.type)">
              {{ item.type === 'school' ? '学校' : '班级' }}
            </span>
            <span class="flex-1">{{ item.value }}</span>
            <span v-if="item.subtitle" class="text-xs text-gray-500">{{ item.subtitle }}</span>
          </div>
        </template>
      </el-autocomplete>

      <!-- 自定义插槽 -->
      <slot name="extra" :filterValues="filterValues" :searchValue="searchValue" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'

/**
 * 筛选器配置
 */
export interface FilterConfig {
  /** 筛选器的唯一标识（用于 v-model） */
  key: string
  /** 显示标签 */
  label: string
  /** 占位符文本（默认为"所有{label}"） */
  placeholder?: string
  /** 选项数据源 */
  options?: any[]
  /** 选项值字段名（默认为 "id"） */
  valueKey?: string
  /** 选项标签字段名（默认为 "name"） */
  labelKey?: string
  /** 筛选器类型（决定空值的类型） */
  type?: 'number' | 'string' | 'boolean'
  /** 依赖的父筛选器 key（当父筛选器变化时，会清空当前筛选器） */
  dependsOn?: string
  /** 计算属性（动态计算选项列表） */
  computedOptions?: () => any[]
  /** 自定义样式类 */
  class?: string
  /** 自定义样式 */
  style?: Record<string, any>
}

/**
 * 搜索建议项
 */
export interface SearchSuggestion {
  /** 显示值 */
  value: string
  /** 类型（如 'school', 'classroom'） */
  type?: string
  /** 副标题（如学校名称、班级编码等） */
  subtitle?: string
  /** 原始数据 */
  data?: any
}

/**
 * 搜索配置
 */
export interface SearchConfig {
  /** 占位符文本 */
  placeholder?: string
  /** 是否启用防抖（默认 true） */
  debounce?: boolean
  /** 防抖延迟（毫秒，默认 300） */
  debounceDelay?: number
  /** 是否按 Enter 键触发（默认 false，实时触发） */
  enterToSearch?: boolean
  /** 获取搜索建议的函数 */
  fetchSuggestions?: (queryString: string, callback: (suggestions: SearchSuggestion[]) => void) => void
  /** 是否在获得焦点时触发搜索建议（默认 true） */
  triggerOnFocus?: boolean
  /** 是否可清空（默认 true） */
  clearable?: boolean
  /** 自定义样式类 */
  class?: string
  /** 自定义样式 */
  style?: Record<string, any>
}

interface Props {
  /** 筛选器配置列表 */
  filters: FilterConfig[]
  /** 搜索配置（可选） */
  searchConfig?: SearchConfig
  /** 筛选值（v-model） */
  modelValue?: Record<string, any>
  /** 搜索值（v-model） */
  searchModelValue?: string
}

interface Emits {
  (e: 'update:modelValue', value: Record<string, any>): void
  (e: 'update:searchModelValue', value: string): void
  (e: 'filter-change', key: string, value: any, allFilters: Record<string, any>): void
  (e: 'search', value: string): void
  (e: 'search-enter', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => ({}),
  searchModelValue: '',
  searchConfig: undefined,
})

const emit = defineEmits<Emits>()

// 获取空值（需要在初始化前定义）
function getEmptyValue(type: FilterConfig['type'] = 'number'): any {
  switch (type) {
    case 'number':
      return undefined
    case 'string':
      return ''
    case 'boolean':
      return undefined
    default:
      return undefined
  }
}

// 初始化筛选值（确保所有筛选器的 key 都存在）
function initFilterValues(): Record<string, any> {
  const initial: Record<string, any> = { ...props.modelValue }
  props.filters.forEach((filter) => {
    if (!(filter.key in initial)) {
      initial[filter.key] = getEmptyValue(filter.type)
    }
  })
  return initial
}

// 筛选值（初始化时确保所有筛选器的 key 都存在）
const filterValues = ref<Record<string, any>>(initFilterValues())

// 搜索值
const searchValue = ref(props.searchModelValue || '')

// 防抖定时器
let searchDebounceTimer: number | null = null

// 监听外部 modelValue 变化
watch(
  () => props.modelValue,
  (newValue) => {
    const updated = { ...newValue }
    // 确保所有筛选器的 key 都存在
    props.filters.forEach((filter) => {
      if (!(filter.key in updated)) {
        updated[filter.key] = getEmptyValue(filter.type)
      }
    })
    filterValues.value = updated
  },
  { deep: true }
)

// 监听外部 searchModelValue 变化
watch(
  () => props.searchModelValue,
  (newValue) => {
    searchValue.value = newValue || ''
  }
)

// 规范化 filters 数组，确保 key 的唯一性和稳定性
const normalizedFilters = computed(() => {
  if (!props.filters || props.filters.length === 0) {
    return []
  }
  // 返回一个新数组，确保引用稳定
  return props.filters.map((filter, index) => ({
    ...filter,
    _index: index, // 添加索引以确保唯一性
  }))
})

// 监听 filters 变化，确保 filterValues 包含所有 key
watch(
  () => props.filters,
  (newFilters) => {
    if (!newFilters || newFilters.length === 0) return
    
    const updated = { ...filterValues.value }
    let hasChanges = false
    
    newFilters.forEach((filter) => {
      if (!(filter.key in updated)) {
        updated[filter.key] = getEmptyValue(filter.type)
        hasChanges = true
      }
    })
    
    // 移除不再存在的 filter key
    const filterKeys = new Set(newFilters.map(f => f.key))
    Object.keys(updated).forEach(key => {
      if (!filterKeys.has(key)) {
        delete updated[key]
        hasChanges = true
      }
    })
    
    if (hasChanges) {
      filterValues.value = updated
      emit('update:modelValue', { ...updated })
    }
  },
  { immediate: true, deep: true }
)

// 获取选项列表
function getFilterOptions(filter: FilterConfig): any[] {
  if (filter.computedOptions) {
    return filter.computedOptions()
  }
  return filter.options || []
}

// 获取选项值
function getOptionValue(option: any, valueKey: string = 'id'): any {
  if (typeof option === 'string' || typeof option === 'number') {
    return option
  }
  return option[valueKey]
}

// 获取选项标签
function getOptionLabel(option: any, labelKey: string = 'name'): string {
  if (typeof option === 'string' || typeof option === 'number') {
    return String(option)
  }
  return option[labelKey] || String(option.id || option.value || option)
}

// 处理筛选器变化
function handleFilterChange(filter: FilterConfig) {
  const value = filterValues.value[filter.key]

  // 如果有依赖的父筛选器，检查是否需要清空依赖的子筛选器
  props.filters.forEach((f) => {
    if (f.dependsOn === filter.key) {
      // 清空依赖的筛选器
      filterValues.value[f.key] = getEmptyValue(f.type)
    }
  })

  // 更新 v-model
  emit('update:modelValue', { ...filterValues.value })

  // 触发事件
  emit('filter-change', filter.key, value, { ...filterValues.value })
}

// 处理搜索输入
function handleSearchInput() {
  if (!props.searchConfig) return

  emit('update:searchModelValue', searchValue.value)

  if (props.searchConfig.enterToSearch) {
    // 只在按 Enter 时触发搜索
    return
  }

  // 实时搜索，使用防抖
  if (props.searchConfig.debounce !== false) {
    if (searchDebounceTimer) {
      clearTimeout(searchDebounceTimer)
    }
    const delay = props.searchConfig.debounceDelay || 300
    searchDebounceTimer = window.setTimeout(() => {
      emit('search', searchValue.value)
      searchDebounceTimer = null
    }, delay)
  } else {
    // 不使用防抖，立即触发
    emit('search', searchValue.value)
  }
}

// 处理搜索建议选择
function handleSuggestionSelect(item: SearchSuggestion) {
  searchValue.value = item.value
  emit('update:searchModelValue', item.value)
  // 选择建议后立即触发搜索
  emit('search-enter', item.value)
  emit('search', item.value)
}

// 获取类型样式类
function getTypeClass(type: string): string {
  if (type === 'school') {
    return 'bg-blue-100 text-blue-800'
  } else if (type === 'classroom') {
    return 'bg-green-100 text-green-800'
  }
  return 'bg-gray-100 text-gray-800'
}

// 处理搜索 Enter 键
function handleSearchEnter() {
  if (!props.searchConfig) return
  emit('search-enter', searchValue.value)
  emit('search', searchValue.value)
}

// 暴露方法供外部调用
defineExpose({
  /** 获取所有筛选值 */
  getFilters: () => ({ ...filterValues.value }),
  /** 获取搜索值 */
  getSearch: () => searchValue.value,
  /** 重置所有筛选器 */
  reset: () => {
    props.filters.forEach((filter) => {
      filterValues.value[filter.key] = getEmptyValue(filter.type)
    })
    searchValue.value = ''
    emit('update:modelValue', { ...filterValues.value })
    emit('update:searchModelValue', '')
  },
  /** 设置筛选值 */
  setFilter: (key: string, value: any) => {
    filterValues.value[key] = value
    emit('update:modelValue', { ...filterValues.value })
  },
  /** 设置搜索值 */
  setSearch: (value: string) => {
    searchValue.value = value
    emit('update:searchModelValue', value)
  },
})
</script>

<style scoped>
.filter-bar {
  @apply w-full;
}

.filter-bar > div {
  /* 隐藏滚动条但保持滚动功能 */
  scrollbar-width: thin;
  scrollbar-color: transparent transparent;
}

.filter-bar > div::-webkit-scrollbar {
  height: 4px;
}

.filter-bar > div::-webkit-scrollbar-track {
  background: transparent;
}

.filter-bar > div::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 2px;
}

.filter-bar > div::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.3);
}

/* 自动完成组件样式 */
.filter-bar-search :deep(.el-autocomplete) {
  width: 100%;
}

.filter-bar-search :deep(.el-input__wrapper) {
  border-radius: 0.5rem;
}
</style>