<template>
  <div class="knowledge-point-selector space-y-3">
    <!-- 知识点分类选择 -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        知识点分类
      </label>
      <div class="space-y-2">
        <!-- 大类选择 -->
        <select
          v-model="selectedCategory"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 bg-white text-gray-900 cursor-pointer"
          @change="handleCategoryChange"
          @click.stop
          @mousedown.stop
        >
          <option value="">请选择大类</option>
          <option
            v-for="category in categories"
            :key="category.name"
            :value="category.name"
          >
            {{ category.name }}
          </option>
        </select>

        <!-- 小类选择（当选择了大类后显示） -->
        <select
          v-if="selectedCategory"
          v-model="selectedSubcategory"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 bg-white text-gray-900 cursor-pointer"
          @change="handleSubcategoryChange"
          @click.stop
          @mousedown.stop
        >
          <option value="">请选择小类</option>
          <option
            v-for="subcategory in availableSubcategories"
            :key="subcategory"
            :value="subcategory"
          >
            {{ subcategory }}
          </option>
        </select>
      </div>
    </div>

    <!-- 知识点名称输入 -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        知识点名称
        <span class="text-gray-500 text-xs font-normal">（可选）</span>
      </label>
      <input
        v-model="knowledgePointName"
        type="text"
        placeholder="如：乘法口诀可视化、图形认知互动"
        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 bg-white text-gray-900 placeholder:text-gray-400"
        @input="handleNameChange"
      />
      <p class="mt-1 text-xs text-gray-500">
        输入具体的知识点名称，用于更精确地标识资源
      </p>
    </div>

    <!-- 显示已选择的信息 -->
    <div
      v-if="formattedCategory"
      class="p-3 bg-purple-50 border border-purple-200 rounded-lg"
    >
      <p class="text-sm text-purple-900">
        <span class="font-medium">已选择：</span>
        {{ formattedCategory }}
        <span v-if="knowledgePointName" class="ml-2">- {{ knowledgePointName }}</span>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import {
  MathOlympiadCategories,
  getAllCategories,
  getSubcategories,
  formatKnowledgePointCategory,
  parseKnowledgePointCategory,
  type KnowledgePointCategory
} from '@/config/knowledgePoints'

interface Props {
  modelValue?: {
    category?: string
    name?: string
  }
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: { category?: string; name?: string }]
}>()

const categories = getAllCategories()
const selectedCategory = ref<string>('')
const selectedSubcategory = ref<string>('')
const knowledgePointName = ref<string>('')

// 可用的子分类
const availableSubcategories = computed(() => {
  if (!selectedCategory.value) return []
  return getSubcategories(selectedCategory.value)
})

// 格式化后的分类字符串
const formattedCategory = computed(() => {
  if (!selectedCategory.value || !selectedSubcategory.value) return null
  return formatKnowledgePointCategory(selectedCategory.value, selectedSubcategory.value)
})


// 更新值并触发事件
const updateValue = () => {
  const value: { category?: string; name?: string } = {}
  if (formattedCategory.value) {
    value.category = formattedCategory.value
  }
  if (knowledgePointName.value.trim()) {
    value.name = knowledgePointName.value.trim()
  }
  emit('update:modelValue', value)
}

// 内部状态，用于防止watch循环更新
const isInternalUpdate = ref(false)

// 监听外部值变化（仅在外部真正变化时同步，不覆盖用户正在进行的操作）
watch(
  () => props.modelValue,
  (newValue, oldValue) => {
    // 如果是内部更新触发的，跳过
    if (isInternalUpdate.value) {
      return
    }
    
    // 如果用户正在选择（内部状态有值），且外部传入空对象，不重置（保护用户正在进行的操作）
    const hasInternalSelection = selectedCategory.value || selectedSubcategory.value
    if (hasInternalSelection && (!newValue || (!newValue.category && !newValue.name))) {
      // 用户正在选择中，外部传入空值，不重置
      return
    }
    
    // 只有当外部值真正变化时才同步
    const newCategory = newValue?.category || ''
    const oldCategory = oldValue?.category || ''
    const newName = newValue?.name || ''
    const oldName = oldValue?.name || ''
    
    // 如果值没有变化，不更新
    if (newCategory === oldCategory && newName === oldName) {
      return
    }
    
    // 只有当外部明确提供了category时才更新
    if (newValue?.category) {
      const parsed = parseKnowledgePointCategory(newValue.category)
      if (parsed) {
        selectedCategory.value = parsed.category
        selectedSubcategory.value = parsed.subcategory
      }
    }
    // 只有在外部明确设置为空且之前有值时才重置
    else if ((newValue === undefined || (newValue && !newValue.category && !newValue.name)) 
               && oldValue && (oldValue.category || oldValue.name)) {
      // 外部明确从有值变为空值，才重置
      selectedCategory.value = ''
      selectedSubcategory.value = ''
    }
    
    if (newValue?.name !== undefined) {
      knowledgePointName.value = newValue.name || ''
    } else if (newValue === undefined || (newValue && !newValue.name && oldValue && oldValue.name)) {
      // 外部明确清空name
      knowledgePointName.value = ''
    }
  },
  { immediate: true }
)

// 修改updateValue，标记为内部更新
const updateValueWithFlag = async () => {
  isInternalUpdate.value = true
  updateValue()
  // 使用nextTick确保emit完成后再重置标志
  await nextTick()
  isInternalUpdate.value = false
}

// 处理大类变化
const handleCategoryChange = () => {
  selectedSubcategory.value = ''
  updateValueWithFlag()
}

// 处理小类变化
const handleSubcategoryChange = () => {
  updateValueWithFlag()
}

// 处理名称变化
const handleNameChange = () => {
  updateValueWithFlag()
}
</script>

<style scoped>
/* 下拉选项样式 */
select {
  position: relative;
  z-index: 1;
}

select option {
  background-color: white;
  color: rgb(17, 24, 39);
}

/* 确保select可以正常交互 */
.knowledge-point-selector {
  position: relative;
  z-index: 1;
}
</style>
