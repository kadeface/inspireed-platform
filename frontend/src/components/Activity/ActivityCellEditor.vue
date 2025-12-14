<template>
  <div class="activity-cell-editor">
    <!-- 活动配置区域 -->
    <div class="editor-section">
      <h3 class="section-title">📋 活动设置</h3>
      
      <!-- 基本信息 -->
      <div class="form-group">
        <label class="form-label">活动标题 *</label>
        <input
          v-model="localContent.title"
          type="text"
          class="form-input"
          placeholder="例如：第一章测验"
          @input="emitUpdate"
        />
      </div>

      <div class="form-group">
        <label class="form-label">活动描述</label>
        <textarea
          v-model="localContent.description"
          class="form-input"
          rows="2"
          placeholder="简要说明活动目的和要求"
          @input="emitUpdate"
        />
      </div>

      <!-- 活动类型 -->
      <div class="form-group">
        <label class="form-label">活动类型 *</label>
        <select 
          v-model="localContent.activityType" 
          class="form-input" 
          @change="handleActivityTypeChange"
        >
          <option value="" disabled>请选择活动类型</option>
          <option value="quiz">测验 (Quiz)</option>
          <option value="survey">问卷 (Survey)</option>
          <option value="assignment">作业 (Assignment)</option>
          <option value="rubric">评价量表 (Rubric)</option>
          <option value="mixed">混合 (Mixed)</option>
        </select>
        <p class="form-hint">
          <span v-if="localContent.activityType === 'quiz'">适合课堂测验，支持自动评分</span>
          <span v-if="localContent.activityType === 'survey'">适合课前调查，收集学生反馈</span>
          <span v-if="localContent.activityType === 'assignment'">适合课后作业，支持多种提交方式</span>
          <span v-if="localContent.activityType === 'rubric'">适合复杂评价，多维度评分</span>
          <span v-if="localContent.activityType === 'mixed'">灵活组合不同题型</span>
        </p>
      </div>

      <!-- 快速模板选择 -->
      <div class="form-group">
        <label class="form-label">使用模板</label>
        <div class="template-grid">
          <button
            v-for="template in activityTemplates"
            :key="template.id"
            @click="applyTemplate(template)"
            class="template-card"
            type="button"
          >
            <span class="text-2xl">{{ template.icon }}</span>
            <div class="text-sm font-medium">{{ template.name }}</div>
            <div class="text-xs text-gray-500">{{ template.description }}</div>
          </button>
        </div>
      </div>
    </div>

    <!-- 时间设置 -->
    <div class="editor-section">
      <h3 class="section-title">⏰ 时间设置</h3>
      
      <div class="form-row">
        <div class="form-group flex-1">
          <label class="form-label">课程阶段</label>
          <select v-model="localContent.timing.phase" class="form-input" @change="emitUpdate">
            <option value="pre-class">课前</option>
            <option value="in-class">课中</option>
            <option value="post-class">课后</option>
          </select>
        </div>

        <div class="form-group flex-1">
          <label class="form-label">时长限制（分钟）</label>
          <input
            v-model.number="localContent.timing.duration"
            type="number"
            class="form-input"
            placeholder="留空表示不限时"
            @input="emitUpdate"
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group flex-1">
          <label class="form-label">开始时间</label>
          <input
            v-model="localContent.timing.startTime"
            type="datetime-local"
            class="form-input"
            @input="emitUpdate"
          />
        </div>

        <div class="form-group flex-1">
          <label class="form-label">截止时间</label>
          <input
            v-model="localContent.timing.deadline"
            type="datetime-local"
            class="form-input"
            @input="emitUpdate"
          />
        </div>
      </div>

      <div class="form-group">
        <label class="checkbox-label">
          <input
            v-model="localContent.timing.allowLateSubmission"
            type="checkbox"
            @change="emitUpdate"
          />
          <span>允许迟交（扣分比例: 
            <input
              v-model.number="localContent.timing.lateSubmissionPenalty"
              type="number"
              class="inline-input"
              min="0"
              max="1"
              step="0.1"
              :disabled="!localContent.timing.allowLateSubmission"
              @input="emitUpdate"
            />
          )</span>
        </label>
      </div>
    </div>

    <!-- 评分设置 -->
    <div class="editor-section">
      <h3 class="section-title">💯 评分设置</h3>
      
      <div class="form-group">
        <label class="checkbox-label">
          <input
            v-model="localContent.grading.enabled"
            type="checkbox"
            @change="emitUpdate"
            :disabled="isSurveyActivity"
          />
          <span>
            启用评分
            <span v-if="isSurveyActivity" class="text-xs text-gray-500 ml-1">(问卷活动默认不评分)</span>
          </span>
        </label>
      </div>

      <div v-if="localContent.grading.enabled" class="ml-6 space-y-4">
        <div class="form-row">
          <div class="form-group flex-1">
            <label class="form-label">总分</label>
            <input
              v-model.number="localContent.grading.totalPoints"
              type="number"
              class="form-input"
              @input="emitUpdate"
            />
          </div>

          <div class="form-group flex-1">
            <label class="form-label">及格分</label>
            <input
              v-model.number="localContent.grading.passingScore"
              type="number"
              class="form-input"
              @input="emitUpdate"
            />
          </div>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input v-model="localContent.grading.autoGrade" type="checkbox" @change="emitUpdate" />
            <span>自动评分（仅适用于选择题等客观题）</span>
          </label>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input v-model="localContent.grading.showScoreToStudent" type="checkbox" @change="emitUpdate" />
            <span>向学生显示分数</span>
          </label>
        </div>
      </div>
    </div>

    <!-- 提交设置 -->
    <div class="editor-section">
      <h3 class="section-title">📤 提交设置</h3>
      
      <div class="form-group">
        <label class="checkbox-label">
          <input v-model="localContent.submission.allowMultiple" type="checkbox" @change="emitUpdate" />
          <span>允许多次提交</span>
        </label>
      </div>

      <div class="form-group">
        <label class="form-label">反馈时机</label>
        <select v-model="localContent.submission.showFeedback" class="form-input" @change="emitUpdate">
          <option value="immediate">立即显示</option>
          <option value="after_deadline">截止后显示</option>
          <option value="manual">手动发布</option>
        </select>
      </div>

      <div class="form-group">
        <label class="checkbox-label">
          <input v-model="localContent.submission.anonymous" type="checkbox" @change="emitUpdate" />
          <span>匿名提交（适用于问卷调查）</span>
        </label>
      </div>
    </div>

    <!-- 显示设置 -->
    <div class="editor-section">
      <h3 class="section-title">👁️ 显示设置</h3>
      
      <div class="form-group">
        <label class="checkbox-label">
          <input v-model="localContent.display.shuffle" type="checkbox" @change="emitUpdate" />
          <span>随机打乱题目顺序</span>
        </label>
      </div>

      <div class="form-group">
        <label class="checkbox-label">
          <input v-model="localContent.display.showProgress" type="checkbox" @change="emitUpdate" />
          <span>显示答题进度</span>
        </label>
      </div>

      <div class="form-group">
        <label class="checkbox-label">
          <input v-model="localContent.display.showResults" type="checkbox" @change="emitUpdate" />
          <span>显示统计结果</span>
        </label>
      </div>

      <div v-if="localContent.display.showResults" class="ml-6">
        <label class="form-label">结果可见范围</label>
        <select v-model="localContent.display.resultVisibility" class="form-input" @change="emitUpdate">
          <option value="teacher_only">仅教师可见</option>
          <option value="all_students">所有学生可见</option>
          <option value="after_submission">提交后可见</option>
        </select>
      </div>
    </div>

    <!-- 题目列表 -->
    <div class="editor-section">
      <div class="flex items-center justify-between mb-4">
        <h3 class="section-title mb-0">📝 题目列表 ({{ localContent.items.length }})</h3>
        <button
          @click="showAddItemModal = true"
          class="btn-primary"
          type="button"
        >
          <span class="text-lg">+</span> 添加题目
        </button>
      </div>

      <!-- 题目列表 -->
      <div v-if="localContent.items.length === 0" class="empty-state">
        <p class="text-gray-500">还没有添加题目，点击上方按钮开始添加</p>
      </div>

      <div v-else class="items-list">
        <div
          v-for="(item, index) in localContent.items"
          :key="item.id"
          class="item-card"
        >
          <div class="item-header">
            <div class="flex items-center gap-2">
              <button class="drag-handle" type="button">
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                </svg>
              </button>
              <span class="item-number">题目 {{ index + 1 }}</span>
              <span class="item-type-badge">{{ getItemTypeLabel(item.type) }}</span>
              <span v-if="item.required" class="required-badge">必答</span>
              <span v-if="item.points" class="points-badge">{{ item.points }}分</span>
            </div>
            <div class="flex gap-2">
              <button @click="editItem(index)" class="btn-sm btn-secondary" type="button">
                编辑
              </button>
              <button @click="deleteItem(index)" class="btn-sm btn-danger" type="button">
                删除
              </button>
            </div>
          </div>
          <div class="item-preview">
            <p class="text-sm text-gray-700">{{ item.question }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加题目模态框 -->
    <ActivityItemModal
      v-if="showAddItemModal"
      :activity-type="localContent.activityType"
      @close="showAddItemModal = false"
      @add="addItem"
    />

    <!-- 编辑题目模态框 -->
    <ActivityItemModal
      v-if="editingItemIndex !== null"
      :activity-type="localContent.activityType"
      :initial-item="localContent.items[editingItemIndex]"
      @close="editingItemIndex = null"
      @update="updateItem"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import type { ActivityCell } from '../../types/cell'
import type { ActivityCellContent, ActivityItem, ActivityItemType } from '../../types/activity'
import { ACTIVITY_TEMPLATES } from '../../types/activity'
import ActivityItemModal from './ActivityItemModal.vue'

interface Props {
  cell: ActivityCell
}

const props = defineProps<Props>()

const emit = defineEmits<{
  update: [cell: ActivityCell]
}>()

// 本地状态
const localContent = reactive<ActivityCellContent>({
  ...props.cell.content,
  // 确保 activityType 有默认值
  activityType: props.cell.content.activityType || 'quiz',
})

// 是否为问卷活动
const isSurveyActivity = computed(() => localContent.activityType === 'survey')

const showAddItemModal = ref(false)
const editingItemIndex = ref<number | null>(null)
const activityTemplates = ACTIVITY_TEMPLATES

// 处理活动类型变化
function handleActivityTypeChange() {
  // 确保值已更新后再触发其他逻辑
  emitUpdate()
}

// 监听 props 变化
watch(() => props.cell.content, (newContent) => {
  // 如果 activityType 有值且与当前不同，才更新
  if (newContent.activityType && newContent.activityType !== localContent.activityType) {
    localContent.activityType = newContent.activityType
  }
  // 更新其他字段
  const currentActivityType = localContent.activityType
  Object.assign(localContent, newContent)
  // 保留当前的 activityType（如果新内容没有或为空）
  if (!newContent.activityType || newContent.activityType === '') {
    localContent.activityType = currentActivityType || 'quiz'
  }
}, { deep: true })

// 当活动类型切换为问卷时，自动关闭评分，避免出现分值和正确答案相关设置
watch(() => localContent.activityType, (type, oldType) => {
  // 只在类型真正改变时执行（避免初始化时的干扰）
  if (type && type !== oldType && type === 'survey') {
    if (localContent.grading) {
      localContent.grading.enabled = false
      localContent.grading.totalPoints = 0
      localContent.grading.autoGrade = false
      localContent.grading.passingScore = undefined
      emitUpdate()
    }
  }
})

// 题型标签映射
function getItemTypeLabel(type: ActivityItemType): string {
  const labels: Record<ActivityItemType, string> = {
    'single-choice': '单选题',
    'multiple-choice': '多选题',
    'true-false': '判断题',
    'short-answer': '简答题',
    'long-answer': '论述题',
    'file-upload': '文件上传',
    'code-submission': '代码提交',
    'scale': '量表评分',
    'rubric-item': '评价标准',
  }
  return labels[type] || type
}

// 发送更新事件
function emitUpdate() {
  emit('update', {
    ...props.cell,
    content: { ...localContent },
  })
}

// 应用模板
function applyTemplate(template: any) {
  if (confirm(`确定要应用"${template.name}"模板吗？这将重置当前配置。`)) {
    Object.assign(localContent, template.template)
    emitUpdate()
  }
}

// 添加题目
function addItem(item: ActivityItem) {
  localContent.items.push({
    ...item,
    id: uuidv4(),
    order: localContent.items.length,
  })
  showAddItemModal.value = false
  emitUpdate()
}

// 编辑题目
function editItem(index: number) {
  editingItemIndex.value = index
}

// 更新题目
function updateItem(item: ActivityItem) {
  if (editingItemIndex.value !== null) {
    localContent.items[editingItemIndex.value] = { ...item }
    editingItemIndex.value = null
    emitUpdate()
  }
}

// 删除题目
function deleteItem(index: number) {
  if (confirm('确定要删除这道题目吗？')) {
    localContent.items.splice(index, 1)
    // 更新顺序
    localContent.items.forEach((item, idx) => {
      item.order = idx
    })
    emitUpdate()
  }
}
</script>

<style scoped>
.activity-cell-editor {
  @apply space-y-6;
}

.editor-section {
  @apply bg-white rounded-lg border border-gray-200 p-6;
}

.section-title {
  @apply text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2;
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
  @apply w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900;
}

.form-input::placeholder {
  @apply text-gray-400;
}

.form-hint {
  @apply text-xs text-gray-500 mt-1;
}

.checkbox-label {
  @apply flex items-center gap-2 text-sm text-gray-700 cursor-pointer;
}

.checkbox-label input[type="checkbox"] {
  @apply w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500;
}

.inline-input {
  @apply w-20 px-2 py-1 border border-gray-300 rounded text-sm bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

.inline-input::placeholder {
  @apply text-gray-400;
}

.inline-input:disabled {
  @apply bg-gray-100 text-gray-500 cursor-not-allowed;
}

.template-grid {
  @apply grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3;
}

.template-card {
  @apply p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors cursor-pointer text-center;
}

.template-card:hover {
  @apply shadow-md;
}

.btn-primary {
  @apply px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors flex items-center gap-2;
}

.btn-secondary {
  @apply px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors;
}

.btn-danger {
  @apply px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors;
}

.btn-sm {
  @apply text-sm;
}

.empty-state {
  @apply text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300;
}

.item-card {
  @apply bg-white border border-gray-200 rounded-lg p-4 mb-3 hover:shadow-md transition-shadow;
}

.item-header {
  @apply flex items-center justify-between mb-2;
}

.drag-handle {
  @apply cursor-move p-1;
}

.item-number {
  @apply text-sm font-semibold text-gray-700;
}

.item-type-badge {
  @apply px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded;
}

.required-badge {
  @apply px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded;
}

.points-badge {
  @apply px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded;
}

.item-preview {
  @apply mt-2 pl-6;
}
</style>

