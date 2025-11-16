<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3 class="modal-title">{{ isEditing ? '编辑题目' : '添加题目' }}</h3>
        <button @click="emit('close')" class="modal-close">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="modal-body">
        <!-- 选择题型 -->
        <div class="form-group">
          <label class="form-label">题型 *</label>
          <select v-model="itemData.type" class="form-input" :disabled="isEditing">
            <option value="" disabled>请选择题型</option>
            <optgroup label="客观题（自动评分）">
              <option value="single-choice">单选题</option>
              <option value="multiple-choice">多选题</option>
              <option value="true-false">判断题</option>
            </optgroup>
            <optgroup label="主观题（手动评分）">
              <option value="short-answer">简答题</option>
              <option value="long-answer">论述题</option>
            </optgroup>
            <optgroup label="特殊题型">
              <option value="file-upload">文件上传</option>
              <option value="code-submission">代码提交</option>
              <option value="scale">量表评分</option>
              <option value="rubric-item">评价标准项</option>
            </optgroup>
          </select>
        </div>

        <!-- 题目内容 -->
        <div class="form-group">
          <label class="form-label">题目/问题 *</label>
          <textarea
            v-model="itemData.question"
            class="form-input"
            rows="3"
            placeholder="输入题目内容"
          />
        </div>

        <!-- 基本设置 -->
        <div class="form-row">
          <div class="form-group flex-1">
            <label class="form-label">分值</label>
            <input
              v-model.number="itemData.points"
              type="number"
              class="form-input"
              min="0"
              placeholder="例如：10"
            />
          </div>
          <div class="form-group flex-1 flex items-end">
            <label class="checkbox-label">
              <input v-model="itemData.required" type="checkbox" />
              <span>必答题</span>
            </label>
          </div>
        </div>

        <!-- 根据题型显示不同的配置 -->
        <div v-if="itemData.type" class="config-section">
          <h4 class="config-title">题型配置</h4>

          <!-- 单选题 -->
          <div v-if="itemData.type === 'single-choice'" class="space-y-4">
            <div class="form-group">
              <label class="form-label">
                选项 <span class="text-red-500">*</span>
                <span class="text-sm text-gray-500 ml-2">（点击左侧单选按钮设置正确答案）</span>
              </label>
              <div class="space-y-2">
                <div
                  v-for="(option, index) in singleChoiceConfig.options"
                  :key="option.id"
                  class="option-row"
                  :class="{ 'border-green-300 bg-green-50': singleChoiceConfig.correctAnswer === option.id }"
                >
                  <input
                    type="radio"
                    :name="'correct-answer'"
                    :checked="singleChoiceConfig.correctAnswer === option.id"
                    @change="singleChoiceConfig.correctAnswer = option.id"
                    class="w-5 h-5 text-blue-600"
                  />
                  <input
                    v-model="option.text"
                    type="text"
                    class="flex-1 form-input"
                    :placeholder="`选项 ${String.fromCharCode(65 + index)}`"
                  />
                  <span v-if="singleChoiceConfig.correctAnswer === option.id" class="text-green-600 font-semibold text-sm">
                    ✓ 正确答案
                  </span>
                  <button @click="removeOption(index)" class="btn-icon text-red-600" type="button">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
              <button @click="addOption" class="btn-secondary mt-2" type="button">
                + 添加选项
              </button>
              <p v-if="!singleChoiceConfig.correctAnswer" class="text-sm text-red-600 mt-2">
                ⚠️ 请选择一个选项作为正确答案
              </p>
            </div>

            <div class="form-group">
              <label class="form-label">答案解析（可选）</label>
              <textarea
                v-model="singleChoiceConfig.explanation"
                class="form-input"
                rows="2"
                placeholder="向学生解释正确答案的原因"
              />
            </div>
          </div>

          <!-- 多选题 -->
          <div v-if="itemData.type === 'multiple-choice'" class="space-y-4">
            <div class="form-group">
              <label class="form-label">
                选项 <span class="text-red-500">*</span>
                <span class="text-sm text-gray-500 ml-2">（勾选左侧复选框设置正确答案）</span>
              </label>
              <div class="space-y-2">
                <div
                  v-for="(option, index) in multipleChoiceConfig.options"
                  :key="option.id"
                  class="option-row"
                  :class="{ 'border-green-300 bg-green-50': multipleChoiceConfig.correctAnswers?.includes(option.id) }"
                >
                  <input
                    type="checkbox"
                    :checked="multipleChoiceConfig.correctAnswers?.includes(option.id)"
                    @change="toggleMultipleAnswer(option.id)"
                    class="w-5 h-5 text-blue-600"
                  />
                  <input
                    v-model="option.text"
                    type="text"
                    class="flex-1 form-input"
                    :placeholder="`选项 ${String.fromCharCode(65 + index)}`"
                  />
                  <span v-if="multipleChoiceConfig.correctAnswers?.includes(option.id)" class="text-green-600 font-semibold text-sm">
                    ✓ 正确答案
                  </span>
                  <button @click="removeOption(index)" class="btn-icon text-red-600" type="button">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
              <button @click="addOption" class="btn-secondary mt-2" type="button">
                + 添加选项
              </button>
              <p v-if="!multipleChoiceConfig.correctAnswers || multipleChoiceConfig.correctAnswers.length === 0" class="text-sm text-red-600 mt-2">
                ⚠️ 请至少选择一个选项作为正确答案
              </p>
            </div>

            <div class="form-group">
              <label class="form-label">答案解析（可选）</label>
              <textarea
                v-model="multipleChoiceConfig.explanation"
                class="form-input"
                rows="2"
              />
            </div>
          </div>

          <!-- 判断题 -->
          <div v-if="itemData.type === 'true-false'" class="space-y-4">
            <div class="form-group">
              <label class="form-label">正确答案</label>
              <select v-model="trueFalseConfig.correctAnswer" class="form-input">
                <option :value="true">正确 (True)</option>
                <option :value="false">错误 (False)</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">答案解析（可选）</label>
              <textarea
                v-model="trueFalseConfig.explanation"
                class="form-input"
                rows="2"
              />
            </div>
          </div>

          <!-- 简答题/论述题 -->
          <div v-if="itemData.type === 'short-answer' || itemData.type === 'long-answer'">
            <div class="form-row">
              <div class="form-group flex-1">
                <label class="form-label">最少字数</label>
                <input
                  v-model.number="textConfig.minLength"
                  type="number"
                  class="form-input"
                  min="0"
                />
              </div>
              <div class="form-group flex-1">
                <label class="form-label">最多字数</label>
                <input
                  v-model.number="textConfig.maxLength"
                  type="number"
                  class="form-input"
                  min="0"
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">占位提示</label>
              <input
                v-model="textConfig.placeholder"
                type="text"
                class="form-input"
                placeholder="例如：请用自己的话简要回答"
              />
            </div>
          </div>

          <!-- 文件上传 -->
          <div v-if="itemData.type === 'file-upload'" class="space-y-4">
            <div class="form-group">
              <label class="form-label">允许的文件类型</label>
              <input
                v-model="fileUploadTypesInput"
                type="text"
                class="form-input"
                placeholder="例如：pdf, docx, zip (用逗号分隔)"
              />
            </div>

            <div class="form-row">
              <div class="form-group flex-1">
                <label class="form-label">最大文件大小 (MB)</label>
                <input
                  v-model.number="fileUploadConfig.maxSize"
                  type="number"
                  class="form-input"
                  min="1"
                  max="100"
                />
              </div>
              <div class="form-group flex-1 flex items-end">
                <label class="checkbox-label">
                  <input v-model="fileUploadConfig.multiple" type="checkbox" />
                  <span>允许多个文件</span>
                </label>
              </div>
            </div>
          </div>

          <!-- 代码提交 -->
          <div v-if="itemData.type === 'code-submission'" class="space-y-4">
            <div class="form-group">
              <label class="form-label">编程语言</label>
              <select v-model="codeConfig.language" class="form-input">
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="java">Java</option>
                <option value="cpp">C++</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">代码模板（可选）</label>
              <textarea
                v-model="codeConfig.template"
                class="form-input font-mono text-sm"
                rows="6"
                placeholder="# 在此编写代码"
              />
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input v-model="codeConfig.autoTest" type="checkbox" />
                <span>启用自动测试</span>
              </label>
            </div>
          </div>

          <!-- 量表 -->
          <div v-if="itemData.type === 'scale'" class="space-y-4">
            <div class="form-row">
              <div class="form-group flex-1">
                <label class="form-label">最小值</label>
                <input
                  v-model.number="scaleConfig.min"
                  type="number"
                  class="form-input"
                />
              </div>
              <div class="form-group flex-1">
                <label class="form-label">最大值</label>
                <input
                  v-model.number="scaleConfig.max"
                  type="number"
                  class="form-input"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group flex-1">
                <label class="form-label">最小值标签</label>
                <input
                  v-model="scaleConfig.minLabel"
                  type="text"
                  class="form-input"
                  placeholder="例如：非常不同意"
                />
              </div>
              <div class="form-group flex-1">
                <label class="form-label">最大值标签</label>
                <input
                  v-model="scaleConfig.maxLabel"
                  type="text"
                  class="form-input"
                  placeholder="例如：非常同意"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="emit('close')" class="btn-secondary" type="button">
          取消
        </button>
        <button @click="handleSubmit" class="btn-primary" type="button">
          {{ isEditing ? '保存' : '添加' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import type { ActivityItem, ActivityType } from '../../types/activity'

interface Props {
  activityType: ActivityType
  initialItem?: ActivityItem
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  add: [item: ActivityItem]
  update: [item: ActivityItem]
}>()

const isEditing = computed(() => !!props.initialItem)

// 基础题目数据
const itemData = reactive<Partial<ActivityItem>>({
  type: props.initialItem?.type || '',
  question: props.initialItem?.question || '',
  required: props.initialItem?.required ?? true,
  points: props.initialItem?.points || 10,
  order: props.initialItem?.order || 0,
})

// 单选题配置
const singleChoiceConfig = reactive({
  options: props.initialItem?.type === 'single-choice' 
    ? props.initialItem.config.options 
    : [
      { id: uuidv4(), text: '', isCorrect: false },
      { id: uuidv4(), text: '', isCorrect: false },
    ],
  correctAnswer: props.initialItem?.type === 'single-choice' 
    ? props.initialItem.config.correctAnswer 
    : undefined,
  explanation: props.initialItem?.type === 'single-choice' 
    ? props.initialItem.config.explanation 
    : '',
})

// 多选题配置
const multipleChoiceConfig = reactive({
  options: props.initialItem?.type === 'multiple-choice' 
    ? props.initialItem.config.options 
    : [
      { id: uuidv4(), text: '', isCorrect: false },
      { id: uuidv4(), text: '', isCorrect: false },
    ],
  correctAnswers: props.initialItem?.type === 'multiple-choice' 
    ? props.initialItem.config.correctAnswers 
    : [],
  explanation: props.initialItem?.type === 'multiple-choice' 
    ? props.initialItem.config.explanation 
    : '',
})

// 判断题配置
const trueFalseConfig = reactive({
  correctAnswer: props.initialItem?.type === 'true-false' 
    ? props.initialItem.config.correctAnswer 
    : true,
  explanation: props.initialItem?.type === 'true-false' 
    ? props.initialItem.config.explanation 
    : '',
})

// 文本题配置
const textConfig = reactive({
  minLength: props.initialItem?.type === 'short-answer' || props.initialItem?.type === 'long-answer'
    ? props.initialItem.config.minLength
    : undefined,
  maxLength: props.initialItem?.type === 'short-answer' || props.initialItem?.type === 'long-answer'
    ? props.initialItem.config.maxLength
    : undefined,
  placeholder: props.initialItem?.type === 'short-answer' || props.initialItem?.type === 'long-answer'
    ? props.initialItem.config.placeholder
    : '',
})

// 文件上传配置
const fileUploadConfig = reactive({
  acceptedTypes: props.initialItem?.type === 'file-upload'
    ? props.initialItem.config.acceptedTypes
    : ['pdf', 'docx'],
  maxSize: props.initialItem?.type === 'file-upload'
    ? props.initialItem.config.maxSize
    : 10,
  multiple: props.initialItem?.type === 'file-upload'
    ? props.initialItem.config.multiple
    : false,
})

const fileUploadTypesInput = ref(
  props.initialItem?.type === 'file-upload'
    ? props.initialItem.config.acceptedTypes.join(', ')
    : 'pdf, docx'
)

// 代码提交配置
const codeConfig = reactive({
  language: props.initialItem?.type === 'code-submission'
    ? props.initialItem.config.language
    : 'python' as any,
  template: props.initialItem?.type === 'code-submission'
    ? props.initialItem.config.template
    : '',
  autoTest: props.initialItem?.type === 'code-submission'
    ? props.initialItem.config.autoTest
    : false,
  testCases: props.initialItem?.type === 'code-submission'
    ? props.initialItem.config.testCases
    : [],
})

// 量表配置
const scaleConfig = reactive({
  min: props.initialItem?.type === 'scale'
    ? props.initialItem.config.min
    : 1,
  max: props.initialItem?.type === 'scale'
    ? props.initialItem.config.max
    : 5,
  minLabel: props.initialItem?.type === 'scale'
    ? props.initialItem.config.minLabel
    : '',
  maxLabel: props.initialItem?.type === 'scale'
    ? props.initialItem.config.maxLabel
    : '',
})

// 添加选项
function addOption() {
  const newOption = { id: uuidv4(), text: '', isCorrect: false }
  if (itemData.type === 'single-choice') {
    singleChoiceConfig.options.push(newOption)
  } else if (itemData.type === 'multiple-choice') {
    multipleChoiceConfig.options.push(newOption)
  }
}

// 删除选项
function removeOption(index: number) {
  if (itemData.type === 'single-choice') {
    singleChoiceConfig.options.splice(index, 1)
  } else if (itemData.type === 'multiple-choice') {
    multipleChoiceConfig.options.splice(index, 1)
  }
}

// 切换多选答案
function toggleMultipleAnswer(optionId: string) {
  const answers = multipleChoiceConfig.correctAnswers || []
  const index = answers.indexOf(optionId)
  if (index > -1) {
    answers.splice(index, 1)
  } else {
    answers.push(optionId)
  }
}

// 提交
function handleSubmit() {
  if (!itemData.type || !itemData.question) {
    alert('请填写题型和题目内容')
    return
  }

  // 验证选项是否填写
  if (itemData.type === 'single-choice') {
    // 检查选项是否为空
    if (singleChoiceConfig.options.length < 2) {
      alert('单选题至少需要2个选项')
      return
    }
    // 检查选项文本是否填写
    const emptyOptions = singleChoiceConfig.options.filter(opt => !opt.text || opt.text.trim() === '')
    if (emptyOptions.length > 0) {
      alert('请填写所有选项的内容')
      return
    }
    // 检查是否设置了正确答案
    if (!singleChoiceConfig.correctAnswer) {
      alert('请选择正确答案（点击选项前的单选按钮）')
      return
    }
  } else if (itemData.type === 'multiple-choice') {
    // 检查选项是否为空
    if (multipleChoiceConfig.options.length < 2) {
      alert('多选题至少需要2个选项')
      return
    }
    // 检查选项文本是否填写
    const emptyOptions = multipleChoiceConfig.options.filter(opt => !opt.text || opt.text.trim() === '')
    if (emptyOptions.length > 0) {
      alert('请填写所有选项的内容')
      return
    }
    // 检查是否设置了正确答案
    if (!multipleChoiceConfig.correctAnswers || multipleChoiceConfig.correctAnswers.length === 0) {
      alert('请至少选择一个正确答案（勾选选项前的复选框）')
      return
    }
  } else if (itemData.type === 'true-false') {
    // 判断题的正确答案总是有默认值，不需要验证
  }

  // 组装配置
  let config: any = {}
  
  if (itemData.type === 'single-choice') {
    // 确保保存完整的配置，包括选项和正确答案
    config = {
      options: singleChoiceConfig.options.map(opt => ({
        id: opt.id,
        text: opt.text,
      })),
      correctAnswer: singleChoiceConfig.correctAnswer,
      explanation: singleChoiceConfig.explanation || '',
    }
  } else if (itemData.type === 'multiple-choice') {
    // 确保保存完整的配置，包括选项和正确答案
    config = {
      options: multipleChoiceConfig.options.map(opt => ({
        id: opt.id,
        text: opt.text,
      })),
      correctAnswers: multipleChoiceConfig.correctAnswers || [],
      explanation: multipleChoiceConfig.explanation || '',
    }
  } else if (itemData.type === 'true-false') {
    config = {
      correctAnswer: trueFalseConfig.correctAnswer,
      explanation: trueFalseConfig.explanation || '',
    }
  } else if (itemData.type === 'short-answer' || itemData.type === 'long-answer') {
    config = textConfig
  } else if (itemData.type === 'file-upload') {
    config = {
      ...fileUploadConfig,
      acceptedTypes: fileUploadTypesInput.value.split(',').map(t => t.trim()),
    }
  } else if (itemData.type === 'code-submission') {
    config = codeConfig
  } else if (itemData.type === 'scale') {
    config = scaleConfig
  }

  const item: ActivityItem = {
    id: props.initialItem?.id || uuidv4(),
    type: itemData.type,
    question: itemData.question!,
    required: itemData.required!,
    points: itemData.points,
    order: itemData.order!,
    config,
  } as any

  if (isEditing.value) {
    emit('update', item)
  } else {
    emit('add', item)
  }
}
</script>

<style scoped>
.modal-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4;
}

.modal-content {
  @apply bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] flex flex-col;
}

.modal-header {
  @apply flex items-center justify-between p-6 border-b border-gray-200;
}

.modal-title {
  @apply text-xl font-semibold text-gray-900;
}

.modal-close {
  @apply text-gray-400 hover:text-gray-600 transition-colors;
}

.modal-body {
  @apply p-6 overflow-y-auto flex-1;
}

.modal-footer {
  @apply flex items-center justify-end gap-3 p-6 border-t border-gray-200;
}

.form-group {
  @apply mb-4;
}

.form-row {
  @apply flex gap-4;
}

.form-label {
  @apply block text-sm font-medium text-gray-700 mb-2;
}

.form-input {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

.checkbox-label {
  @apply flex items-center gap-2 text-sm text-gray-700 cursor-pointer;
}

.checkbox-label input[type="checkbox"] {
  @apply w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500;
}

.config-section {
  @apply mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200;
}

.config-title {
  @apply text-sm font-semibold text-gray-700 mb-4;
}

.option-row {
  @apply flex items-center gap-2;
}

.btn-primary {
  @apply px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors;
}

.btn-secondary {
  @apply px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors;
}

.btn-icon {
  @apply p-1 hover:bg-gray-100 rounded transition-colors;
}
</style>

