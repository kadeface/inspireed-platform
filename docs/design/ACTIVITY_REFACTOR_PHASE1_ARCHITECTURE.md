# Activity 组件重构 - 第一阶段架构图

## 📐 组件关系图

```
┌─────────────────────────────────────────────────────────────┐
│                    ActivityViewer.vue                        │
│                    (主组件，简化后 ~900 行)                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  题目列表循环 (v-for item in items)                   │  │
│  │                                                       │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │  ItemRenderer.vue                            │   │  │
│  │  │  (题型渲染器，根据 item.type 动态加载)         │   │  │
│  │  │                                               │   │  │
│  │  │  Props:                                       │   │  │
│  │  │  - item: ActivityItem                        │   │  │
│  │  │  - modelValue: any (v-model)                │   │  │
│  │  │  - isSubmitted: boolean                     │   │  │
│  │  │  - answerData: any                          │   │  │
│  │  │                                               │   │  │
│  │  │  ┌─────────────────────────────────────┐   │   │  │
│  │  │  │  component :is="componentMap[type]"   │   │   │  │
│  │  │  │                                       │   │   │  │
│  │  │  │  ┌───────────────────────────────┐   │   │   │  │
│  │  │  │  │ SingleChoiceItem.vue          │   │   │   │  │
│  │  │  │  │ (单选题组件)                   │   │   │   │  │
│  │  │  │  └───────────────────────────────┘   │   │   │  │
│  │  │  │                                       │   │   │  │
│  │  │  │  ┌───────────────────────────────┐   │   │   │  │
│  │  │  │  │ MultipleChoiceItem.vue       │   │   │   │  │
│  │  │  │  │ (多选题组件)                   │   │   │   │  │
│  │  │  │  └───────────────────────────────┘   │   │   │  │
│  │  │  │                                       │   │   │  │
│  │  │  │  ┌───────────────────────────────┐   │   │   │  │
│  │  │  │  │ TrueFalseItem.vue            │   │   │   │  │
│  │  │  │  │ (判断题组件)                   │   │   │   │  │
│  │  │  │  └───────────────────────────────┘   │   │   │  │
│  │  │  │                                       │   │   │  │
│  │  │  │  ┌───────────────────────────────┐   │   │   │  │
│  │  │  │  │ ShortAnswerItem.vue          │   │   │   │  │
│  │  │  │  │ LongAnswerItem.vue           │   │   │   │  │
│  │  │  │  │ (文本题组件)                   │   │   │  │
│  │  │  │  └───────────────────────────────┘   │   │   │  │
│  │  │  │                                       │   │   │  │
│  │  │  │  ┌───────────────────────────────┐   │   │   │  │
│  │  │  │  │ ScaleItem.vue                │   │   │   │  │
│  │  │  │  │ (量表评分组件)                 │   │   │  │
│  │  │  │  └───────────────────────────────┘   │   │   │  │
│  │  │  └─────────────────────────────────────┘   │   │  │
│  │  └──────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  其他功能保持不变：                                          │
│  - 活动头部信息                                              │
│  - 进度条                                                    │
│  - 提交按钮                                                  │
│  - 离线支持逻辑                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              共享组件 (ItemTypes/shared/)                     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ItemFeedback.vue                                      │  │
│  │  (统一反馈显示组件)                                     │  │
│  │                                                         │  │
│  │  Props:                                                 │  │
│  │  - answer: any (答案数据)                               │  │
│  │  - points?: number (分值)                               │  │
│  │  - showScore?: boolean                                  │  │
│  │                                                         │  │
│  │  功能:                                                  │  │
│  │  - 显示 ✓/✗ 正确/错误提示                               │  │
│  │  - 显示正确答案                                          │  │
│  │  - 显示得分                                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 数据流

```
ActivityViewer
    │
    ├─ answers[item.id] (v-model)
    │     │
    │     └─> ItemRenderer
    │           │
    │           └─> SingleChoiceItem (或其他题型组件)
    │                 │
    │                 ├─> 用户选择选项
    │                 │
    │                 └─> emit('update:modelValue', newValue)
    │                       │
    │                       └─> ActivityViewer.answers[item.id] = newValue
    │                             │
    │                             └─> saveAnswer(item.id)
    │                                   │
    │                                   └─> syncToServer() / saveToIndexedDB()
    │
    └─ getItemAnswer(item.id) (提交后的答案数据)
          │
          └─> ItemRenderer
                │
                └─> SingleChoiceItem
                      │
                      └─> ItemFeedback (显示反馈)
```

## 📦 组件接口规范

### 所有题型组件统一接口

```typescript
interface ItemComponentProps {
  // 题目数据
  item: ActivityItem
  
  // 当前答案（v-model）
  modelValue: any
  
  // 是否已提交
  isSubmitted: boolean
  
  // 提交后的答案数据（包含正确性、得分等）
  answerData?: {
    correct?: boolean
    correctAnswer?: string | string[]
    score?: number
    // ... 其他字段
  }
}

interface ItemComponentEmits {
  // v-model 更新
  'update:modelValue': [value: any]
  
  // 答案变化（用于触发保存）
  'change': [itemId: string]
}
```

## 🎨 样式组织

```
ItemTypes/
├── SingleChoiceItem.vue
│   ├── <template> (组件结构)
│   ├── <script setup> (组件逻辑)
│   └── <style scoped> (组件样式)
│
├── shared/
│   └── ItemFeedback.vue
│       ├── <template>
│       ├── <script setup>
│       └── <style scoped>
│
└── ItemRenderer.vue
    ├── <template>
    ├── <script setup>
    └── <style scoped>
```

**样式原则**:
- 每个组件使用 `scoped` 样式
- 共享样式提取到 `shared/` 目录
- 保持与 ActivityViewer 的样式一致性

## 🔍 代码对比示例

### 重构前（ActivityViewer.vue）

```vue
<!-- 单选题渲染（约 35 行） -->
<div v-if="item.type === 'single-choice'" class="space-y-2">
  <label
    v-for="option in item.config.options"
    :key="option.id"
    class="option-label"
    :class="{
      'option-correct': isSubmitted && isCorrectAnswerForSingle(item.id, option.id),
      'option-selected': answers[item.id] === option.id,
      'option-wrong': isSubmitted && answers[item.id] === option.id && !getItemAnswer(item.id)?.correct
    }"
  >
    <input
      v-model="answers[item.id]"
      type="radio"
      :value="option.id"
      :name="`item-${item.id}`"
      :disabled="isSubmitted"
      @change="saveAnswer(item.id)"
    />
    <span>{{ option.text }}</span>
    <span v-if="isSubmitted && isCorrectAnswerForSingle(item.id, option.id)" class="correct-badge">
      ✓ 正确答案
    </span>
  </label>
  <!-- 反馈信息 -->
  <div v-if="isSubmitted && getItemAnswer(item.id)" class="feedback-info">
    <!-- ... 反馈逻辑 ... -->
  </div>
</div>

<!-- 多选题渲染（约 35 行） -->
<div v-if="item.type === 'multiple-choice'" class="space-y-2">
  <!-- ... 类似逻辑 ... -->
</div>

<!-- ... 其他题型 ... -->
```

### 重构后（ActivityViewer.vue）

```vue
<!-- 统一使用 ItemRenderer（1 行） -->
<ItemRenderer
  :item="item"
  v-model="answers[item.id]"
  :is-submitted="isSubmitted"
  :answer-data="getItemAnswer(item.id)"
  @change="saveAnswer(item.id)"
/>
```

### 新组件（SingleChoiceItem.vue）

```vue
<template>
  <div class="single-choice-item space-y-2">
    <label
      v-for="option in item.config.options"
      :key="option.id"
      class="option-label"
      :class="{
        'option-correct': isSubmitted && isCorrectOption(option.id),
        'option-selected': modelValue === option.id,
        'option-wrong': isSubmitted && modelValue === option.id && !isCorrect
      }"
    >
      <input
        :value="option.id"
        type="radio"
        :name="`item-${item.id}`"
        :checked="modelValue === option.id"
        :disabled="isSubmitted"
        @change="handleChange(option.id)"
      />
      <span>{{ option.text }}</span>
      <span v-if="isSubmitted && isCorrectOption(option.id)" class="correct-badge">
        ✓ 正确答案
      </span>
    </label>
    
    <ItemFeedback
      v-if="isSubmitted && answerData"
      :answer="answerData"
      :points="item.points"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { SingleChoiceItem } from '@/types/activity'
import ItemFeedback from './shared/ItemFeedback.vue'

const props = defineProps<{
  item: SingleChoiceItem
  modelValue: string | undefined
  isSubmitted: boolean
  answerData?: any
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'change': [itemId: string]
}>()

const isCorrect = computed(() => props.answerData?.correct ?? false)

function isCorrectOption(optionId: string): boolean {
  if (!props.answerData) return false
  return String(props.answerData.correctAnswerId || props.answerData.correctAnswer) === String(optionId)
}

function handleChange(optionId: string) {
  emit('update:modelValue', optionId)
  emit('change', props.item.id)
}
</script>

<style scoped>
/* 组件样式 */
</style>
```

## 📈 收益分析

### 代码组织

| 指标 | 重构前 | 重构后 | 改善 |
|------|--------|--------|------|
| ActivityViewer 行数 | 1140 | ~900 | -21% |
| 单个题型逻辑行数 | 35-50 (分散) | 50-100 (集中) | 更易维护 |
| 题型相关代码位置 | 1 个文件 | 7 个文件 | 职责分离 |

### 开发效率

- **修改单选题**：只需编辑 `SingleChoiceItem.vue`（~100 行）
- **新增题型**：创建新组件 + 在 ItemRenderer 注册（~5 分钟）
- **统一反馈样式**：只需修改 `ItemFeedback.vue`（~50 行）

### 测试覆盖

- **单元测试**：每个题型组件可独立测试
- **集成测试**：ActivityViewer 测试更简单（只需测试 ItemRenderer 集成）

## 🚦 实施优先级

1. **高优先级**（核心题型）：
   - ✅ SingleChoiceItem（单选题）
   - ✅ MultipleChoiceItem（多选题）
   - ✅ TrueFalseItem（判断题）

2. **中优先级**（常用题型）：
   - ✅ ShortAnswerItem（简答题）
   - ✅ LongAnswerItem（论述题）
   - ✅ ScaleItem（量表评分）

3. **低优先级**（待实现题型）：
   - ⏳ FileUploadItem（文件上传）
   - ⏳ CodeSubmissionItem（代码提交）
   - ⏳ RubricItem（评价标准）

