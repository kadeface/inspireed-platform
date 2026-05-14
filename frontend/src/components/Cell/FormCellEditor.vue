<template>
  <div class="form-cell-editor">
    <div class="editor-header">
      <h3 class="text-xl font-semibold text-gray-900">编辑互动投票</h3>
      <div class="header-actions">
        <button
          v-if="!isFormActive"
          @click="handleStart"
          class="btn-start"
          :disabled="!hasValidOptions"
        >
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          开始投票
        </button>
        <button
          v-else
          @click="handleStop"
          class="btn-stop"
        >
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
          </svg>
          停止投票
        </button>
      </div>
    </div>

    <div class="editor-content">
      <!-- 基本信息 -->
      <div class="form-section">
        <label class="form-label">投票标题</label>
        <input
          v-model="formData.title"
          type="text"
          class="form-input"
          placeholder="输入投票标题..."
          maxlength="200"
        />

        <label class="form-label mt-4">描述（可选）</label>
        <textarea
          v-model="formData.description"
          class="form-textarea"
          placeholder="输入投票描述..."
          rows="3"
          maxlength="1000"
        />
      </div>

      <!-- 投票类型 -->
      <div class="form-section">
        <label class="form-label">投票类型</label>
        <div class="type-selector">
          <button
            v-for="type in formTypes"
            :key="type.value"
            @click="formData.cell_type = type.value"
            :class="['type-btn', { active: formData.cell_type === type.value }]"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="type.value === 'single_choice'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              <path v-else-if="type.value === 'multiple_choice'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
            </svg>
            <span class="ml-2">{{ type.label }}</span>
          </button>
        </div>
      </div>

      <!-- 选项管理 -->
      <div class="form-section">
        <div class="section-header">
          <label class="form-label mb-0">选项列表</label>
          <button @click="addOption" class="btn-add-option">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            添加选项
          </button>
        </div>

        <div class="options-list">
          <div
            v-for="(option, index) in formData.options"
            :key="index"
            class="option-item"
          >
            <div class="option-drag">
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
              </svg>
            </div>

            <input
              v-model="option.text"
              type="text"
              class="form-input flex-1"
              :placeholder="`选项 ${index + 1}`"
              maxlength="100"
            />

            <input
              v-model="option.image_url"
              type="text"
              class="form-input w-48 ml-2"
              placeholder="图片URL（可选）"
            />

            <button
              @click="removeOption(index)"
              :disabled="formData.options.length <= 2"
              class="btn-remove-option"
              title="删除选项"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>

        <p v-if="!hasValidOptions" class="text-sm text-red-500 mt-2">
          至少需要2个选项才能开始投票
        </p>
      </div>

      <!-- 高级设置 -->
      <div class="form-section">
        <button @click="showAdvanced = !showAdvanced" class="advanced-toggle">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          高级设置
          <svg class="w-4 h-4 ml-1 transition-transform" :class="{ 'rotate-180': showAdvanced }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <div v-if="showAdvanced" class="advanced-settings">
          <div class="setting-item">
            <input
              id="anonymous"
              v-model="formData.settings.anonymous"
              type="checkbox"
              class="form-checkbox"
            />
            <label for="anonymous" class="setting-label">匿名模式</label>
          </div>

          <div class="setting-item">
            <input
              id="allow_change"
              v-model="formData.settings.allow_change"
              type="checkbox"
              class="form-checkbox"
            />
            <label for="allow_change" class="setting-label">允许修改答案</label>
          </div>

          <div class="setting-item">
            <input
              id="show_results"
              v-model="formData.settings.show_results"
              type="checkbox"
              class="form-checkbox"
            />
            <label for="show_results" class="setting-label">显示结果给学生</label>
          </div>

          <div class="setting-item">
            <label class="setting-label">时间限制（秒）</label>
            <input
              v-model.number="formData.time_limit"
              type="number"
              class="form-input w-24"
              min="10"
              max="600"
              placeholder="无限制"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <div class="editor-footer">
      <div class="footer-info">
        <span v-if="isFormActive" class="text-green-600 font-medium">
          ✓ 投票进行中
        </span>
        <span v-else class="text-gray-500">
          准备就绪
        </span>
      </div>

      <div class="footer-actions">
        <button @click="handleCancel" class="btn-cancel">
          取消
        </button>
        <button @click="handleSave" class="btn-save" :disabled="!hasValidOptions">
          保存更改
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Cell } from '../../types/cell'
import type { FormCellCreate, FormCellUpdate, FormOptionCreate, FormType, FormSettings } from '../../types/form'

interface Props {
  cell: Cell
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'save', data: FormCellCreate | FormCellUpdate): void
  (e: 'start'): void
  (e: 'stop'): void
}>()

// 表单数据
const formData = ref<{
  title: string
  description: string
  cell_type: FormType
  options: FormOptionCreate[]
  settings: FormSettings
  time_limit?: number
}>({
  title: props.cell.title || '',
  description: props.cell.description || '',
  cell_type: (props.cell.content?.cell_type as FormType) || 'single_choice',
  options: props.cell.content?.options || [],
  settings: props.cell.content?.settings || {},
  time_limit: props.cell.content?.time_limit,
})

// 状态
const showAdvanced = ref(false)
const isFormActive = ref(false) // TODO: 从store获取

// 表单类型选项
const formTypes = [
  { value: 'single_choice', label: '单选' },
  { value: 'multiple_choice', label: '多选' },
  { value: 'ranking', label: '排序' },
]

// 计算属性
const hasValidOptions = computed(() => {
  return formData.value.options.length >= 2 &&
         formData.value.options.every(opt => opt.text.trim().length > 0)
})

// 方法
function addOption() {
  formData.value.options.push({
    text: '',
    order: formData.value.options.length,
  })
}

function removeOption(index: number) {
  if (formData.value.options.length > 2) {
    formData.value.options.splice(index, 1)
    // 更新order
    formData.value.options.forEach((opt, i) => {
      opt.order = i
    })
  }
}

function handleSave() {
  const data: FormCellUpdate = {
    title: formData.value.title,
    description: formData.value.description,
    cell_type: formData.value.cell_type,
    options: formData.value.options,
    settings: formData.value.settings,
    time_limit: formData.value.time_limit,
  }
  emit('save', data)
}

function handleStart() {
  emit('start')
  isFormActive.value = true
}

function handleStop() {
  emit('stop')
  isFormActive.value = false
}

function handleCancel() {
  // 重置为原始数据
  formData.value = {
    title: props.cell.title || '',
    description: props.cell.description || '',
    cell_type: (props.cell.content?.cell_type as FormType) || 'single_choice',
    options: props.cell.content?.options || [],
    settings: props.cell.content?.settings || {},
    time_limit: props.cell.content?.time_limit,
  }
}
</script>

<style scoped>
.form-cell-editor {
  @apply space-y-6;
}

.editor-header {
  @apply flex justify-between items-center;
}

.header-actions {
  @apply flex gap-2;
}

.btn-start {
  @apply flex items-center px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-stop {
  @apply flex items-center px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-md font-medium transition-colors;
}

.editor-content {
  @apply space-y-6;
}

.form-section {
  @apply space-y-3;
}

.form-label {
  @apply block text-sm font-medium text-gray-700;
}

.form-input {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent;
}

.form-textarea {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none;
}

.type-selector {
  @apply flex gap-2;
}

.type-btn {
  @apply flex items-center px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors;
}

.type-btn.active {
  @apply bg-blue-50 border-blue-500 text-blue-700;
}

.section-header {
  @apply flex justify-between items-center;
}

.btn-add-option {
  @apply flex items-center px-3 py-1.5 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded-md transition-colors;
}

.options-list {
  @apply space-y-2;
}

.option-item {
  @apply flex items-center gap-2;
}

.option-drag {
  @apply cursor-move flex items-center;
}

.btn-remove-option {
  @apply p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.advanced-toggle {
  @apply flex items-center text-sm text-gray-700 hover:text-gray-900;
}

.advanced-settings {
  @apply mt-3 space-y-2 p-3 bg-gray-50 rounded-md;
}

.setting-item {
  @apply flex items-center gap-2;
}

.form-checkbox {
  @apply w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500;
}

.setting-label {
  @apply text-sm text-gray-700;
}

.editor-footer {
  @apply flex justify-between items-center pt-4 border-t border-gray-200;
}

.footer-actions {
  @apply flex gap-2;
}

.btn-cancel {
  @apply px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md font-medium transition-colors;
}

.btn-save {
  @apply px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}
</style>
