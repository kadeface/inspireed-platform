# SurveyJS 快速开始

## 快速启用

### 在 ActivityCell 中使用

在 `ActivityCell.vue` 中，可以通过 prop 启用 SurveyJS：

```vue
<ActivityCell
  :cell="cell"
  :editable="false"
  :lesson-id="lessonId"
  :session-id="sessionId"
/>
```

然后在 `ActivityViewer` 中启用 SurveyJS：

```vue
<!-- 在 ActivityViewer.vue 中 -->
<ActivityViewer
  :cell="cell"
  :lesson-id="lessonId"
  :session-id="sessionId"
  :use-survey-js="true"
/>
```

### 直接使用 SurveyJSViewer

```vue
<template>
  <div class="activity-page">
    <SurveyJSViewer
      :content="cell.content"
      :is-submitted="isSubmitted"
      :submission-data="submissionData"
      :existing-answers="answers"
      @submit="handleSubmit"
      @change="handleChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import SurveyJSViewer from '@/components/Activity/SurveyJSViewer.vue'
import type { ActivityCellContent, ActivitySubmission } from '@/types/activity'

const cell = ref({
  content: {
    title: '测试活动',
    activityType: 'quiz',
    items: [
      {
        id: 'q1',
        type: 'single-choice',
        question: '这是第一题？',
        required: true,
        order: 1,
        config: {
          options: [
            { id: 'opt1', text: '选项1', isCorrect: true },
            { id: 'opt2', text: '选项2' },
          ],
          correctAnswer: 'opt1',
        },
      },
    ],
    // ... 其他配置
  } as ActivityCellContent,
})

const isSubmitted = ref(false)
const submissionData = ref<ActivitySubmission | undefined>()
const answers = ref<Record<string, any>>({})

function handleSubmit(answers: Record<string, any>) {
  console.log('提交答案:', answers)
  // 调用 API 提交
  isSubmitted.value = true
}

function handleChange(answers: Record<string, any>) {
  console.log('答案变化:', answers)
  // 可以在这里实现自动保存
}
</script>
```

## 数据转换示例

### 创建 SurveyJS JSON

```typescript
import { convertActivityToSurveyJson } from '@/utils/surveyjsConverter'
import type { ActivityCellContent } from '@/types/activity'

const content: ActivityCellContent = {
  title: '数学测验',
  activityType: 'quiz',
  items: [
    {
      id: 'q1',
      type: 'single-choice',
      question: '1 + 1 = ?',
      required: true,
      points: 10,
      order: 1,
      config: {
        options: [
          { id: 'a', text: '1', isCorrect: false },
          { id: 'b', text: '2', isCorrect: true },
          { id: 'c', text: '3', isCorrect: false },
        ],
        correctAnswer: 'b',
        explanation: '1 + 1 = 2',
      },
    },
    {
      id: 'q2',
      type: 'multiple-choice',
      question: '以下哪些是偶数？',
      required: true,
      points: 10,
      order: 2,
      config: {
        options: [
          { id: 'a', text: '2', isCorrect: true },
          { id: 'b', text: '3', isCorrect: false },
          { id: 'c', text: '4', isCorrect: true },
        ],
        correctAnswers: ['a', 'c'],
      },
    },
    {
      id: 'q3',
      type: 'short-answer',
      question: '请简述什么是质数？',
      required: false,
      points: 20,
      order: 3,
      config: {
        minLength: 10,
        maxLength: 200,
        placeholder: '请输入答案',
      },
    },
  ],
  timing: {
    phase: 'in-class',
    duration: 30,
  },
  grading: {
    enabled: true,
    totalPoints: 40,
    autoGrade: true,
  },
  submission: {
    allowMultiple: false,
  },
  display: {
    showProgress: true,
  },
}

const surveyJson = convertActivityToSurveyJson(content, false)
console.log(surveyJson)
```

### 转换答案

```typescript
import {
  convertSurveyResultToAnswers,
  convertAnswersToSurveyData,
} from '@/utils/surveyjsConverter'

// SurveyJS 提交结果
const surveyResult = {
  q1: 'b',
  q2: ['a', 'c'],
  q3: '质数是只能被1和自身整除的大于1的自然数',
}

// 转换为系统格式
const answers = convertSurveyResultToAnswers(surveyResult, content.items)
console.log(answers)
// {
//   q1: { answer: 'b' },
//   q2: { answer: ['a', 'c'] },
//   q3: { text: '质数是只能被1和自身整除的大于1的自然数' }
// }

// 系统格式转回 SurveyJS 数据（用于回显）
const surveyData = convertAnswersToSurveyData(answers, content.items)
console.log(surveyData)
// {
//   q1: 'b',
//   q2: ['a', 'c'],
//   q3: '质数是只能被1和自身整除的大于1的自然数'
// }
```

## 自定义配置

### 修改 SurveyJS 样式

确保已导入 SurveyJS CSS：

```typescript
import 'survey-core/survey-core.min.css'
```

在 `SurveyJSViewer.vue` 中修改样式：

```vue
<style scoped>
/* 自定义 SurveyJS 样式 */
:deep(.sv-root) {
  @apply font-sans;
}

:deep(.sv-title) {
  @apply text-3xl font-bold text-blue-900 mb-6;
}

:deep(.sv-question__title) {
  @apply text-xl font-semibold text-gray-800 mb-4;
}

:deep(.sv-btn--action) {
  @apply bg-blue-600 text-white hover:bg-blue-700 px-6 py-3 rounded-lg;
}
</style>
```

### 添加自定义验证

在转换器中可以添加自定义验证规则：

```typescript
// 在 convertItemToSurveyQuestion 中
case 'short-answer': {
  return {
    ...baseQuestion,
    type: 'text',
    validators: [
      {
        type: 'text',
        minLength: item.config.minLength || 0,
        maxLength: item.config.maxLength || 1000,
      },
    ],
  }
}
```

## 常见问题

### Q: 如何禁用 SurveyJS 的自动提交按钮？

A: SurveyJS 默认会在完成时显示提交按钮。如果需要自定义，可以在 SurveyJS JSON 中设置：

```typescript
const surveyJson = {
  // ...
  completeButtonText: '提交',
  showCompleteButton: true,
}
```

### Q: 如何实现自动保存？

A: 监听 `@change` 事件：

```vue
<SurveyJSViewer
  @change="handleChange"
/>

<script setup>
function handleChange(answers) {
  // 自动保存到本地存储或服务器
  localStorage.setItem('draft-answers', JSON.stringify(answers))
}
</script>
```

### Q: 如何显示正确答案？

A: 在已提交状态下，SurveyJS 会自动显示正确答案（如果配置了 `correctAnswer`）：

```vue
<SurveyJSViewer
  :is-submitted="true"
  :submission-data="submissionData"
/>
```

### Q: 如何处理文件上传？

A: SurveyJS 支持文件上传，但需要配置服务器端处理：

```typescript
// 在转换器中
case 'file-upload': {
  return {
    ...baseQuestion,
    type: 'file',
    storeDataAsText: false,
    allowMultiple: item.config.multiple,
    acceptedTypes: item.config.acceptedTypes.join(','),
    maxSize: item.config.maxSize * 1024 * 1024,
  }
}
```

然后在服务器端处理文件上传。

## 下一步

- 查看 [完整集成文档](./SURVEYJS_INTEGRATION.md)
- 查看 [SurveyJS 官方文档](https://surveyjs.io/)
- 探索更多自定义选项

