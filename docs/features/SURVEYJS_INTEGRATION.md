# SurveyJS 集成文档

## 概述

本项目已集成 SurveyJS，这是一个成熟的开源表单和问卷库，支持多种题型、数据验证、条件逻辑等功能。

## 安装

SurveyJS 已通过以下包安装：

```bash
pnpm add survey-core survey-vue3-ui
```

## 功能特性

### 支持的题型

- ✅ **单选题** (`single-choice`) - 转换为 `radiogroup`
- ✅ **多选题** (`multiple-choice`) - 转换为 `checkbox`
- ✅ **判断题** (`true-false`) - 转换为 `boolean`
- ✅ **简答题** (`short-answer`) - 转换为 `text`
- ✅ **论述题** (`long-answer`) - 转换为 `comment`
- ✅ **量表评分** (`scale`) - 转换为 `rating`
- ⚠️ **文件上传** (`file-upload`) - 转换为 `file`（需要额外配置）
- ⚠️ **代码提交** (`code-submission`) - 转换为 `comment`（作为文本输入）
- ⚠️ **评价标准项** (`rubric-item`) - 转换为 `dropdown`

### 数据转换

系统提供了完整的数据转换器 (`surveyjsConverter.ts`)，可以：

1. **ActivityCellContent → SurveyJS JSON**
   - 自动转换活动内容为 SurveyJS 格式
   - 支持题目排序、必答验证、分值显示等

2. **SurveyJS 结果 → ItemAnswer**
   - 将 SurveyJS 提交结果转换回系统标准格式
   - 保持与现有后端 API 兼容

3. **ItemAnswer → SurveyJS 数据**
   - 支持回显已提交的答案
   - 支持显示正确答案和解析

## 使用方法

### 方式 1: 在 ActivityViewer 中使用

在 `ActivityViewer` 组件中，通过 `useSurveyJS` prop 启用 SurveyJS：

```vue
<ActivityViewer
  :cell="cell"
  :lesson-id="lessonId"
  :session-id="sessionId"
  :use-survey-js="true"
  @submit="handleSubmit"
/>
```

### 方式 2: 直接使用 SurveyJSViewer

直接使用 `SurveyJSViewer` 组件：

```vue
<template>
  <SurveyJSViewer
    :content="activityContent"
    :is-submitted="isSubmitted"
    :submission-data="submissionData"
    :existing-answers="answers"
    @submit="handleSubmit"
    @change="handleChange"
  />
</template>

<script setup lang="ts">
import SurveyJSViewer from '@/components/Activity/SurveyJSViewer.vue'
import type { ActivityCellContent } from '@/types/activity'

const activityContent: ActivityCellContent = {
  // ... 活动内容
}

function handleSubmit(answers: Record<string, any>) {
  // 处理提交
}

function handleChange(answers: Record<string, any>) {
  // 处理答案变化
}
</script>
```

## 配置选项

### SurveyJS JSON 配置

转换器会根据 `ActivityCellContent` 自动生成 SurveyJS JSON，包括：

- `showProgressBar`: 根据 `display.showProgress` 设置
- `showQuestionNumbers`: 始终显示题号
- `showTimerPanel`: 根据 `timing.duration` 设置
- `maxTimeToFinish`: 时长限制（秒）

### 自定义样式

SurveyJS 组件已包含基础样式覆盖，匹配项目风格：

```css
:deep(.sv-root) {
  @apply font-sans;
}

:deep(.sv-title) {
  @apply text-2xl font-bold text-gray-900 mb-4;
}
```

可以在 `SurveyJSViewer.vue` 中进一步自定义样式。

## 与现有系统的兼容性

### API 兼容

- ✅ 完全兼容现有的后端 API
- ✅ 答案格式与现有系统一致
- ✅ 支持所有现有的提交流程

### 功能对比

| 功能 | 传统视图 | SurveyJS 视图 |
|------|---------|--------------|
| 题型支持 | 部分实现 | 完整支持 |
| 数据验证 | 基础验证 | 高级验证 |
| 条件逻辑 | 不支持 | 支持 |
| 样式定制 | 完全控制 | 需要覆盖样式 |
| 互评功能 | 支持 | 需要扩展 |
| 代码编辑器 | 支持 | 不支持（使用文本输入） |

## 迁移建议

### 渐进式迁移

1. **阶段 1**: 在新功能中使用 SurveyJS
2. **阶段 2**: 逐步替换现有组件
3. **阶段 3**: 完全迁移到 SurveyJS（可选）

### 保留自定义功能

对于 SurveyJS 不直接支持的功能（如互评、代码编辑器），可以：

1. 继续使用传统视图
2. 混合使用：SurveyJS 处理标准题型，自定义组件处理特殊题型
3. 扩展 SurveyJS：创建自定义 SurveyJS 组件

## 示例代码

### 基本使用

```typescript
import { convertActivityToSurveyJson } from '@/utils/surveyjsConverter'
import type { ActivityCellContent } from '@/types/activity'

const content: ActivityCellContent = {
  title: '测试活动',
  activityType: 'quiz',
  items: [
    {
      id: 'q1',
      type: 'single-choice',
      question: '这是第一题？',
      required: true,
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
}

const surveyJson = convertActivityToSurveyJson(content)
// 使用 surveyJson 创建 SurveyJS 模型
```

### 答案转换

```typescript
import {
  convertSurveyResultToAnswers,
  convertAnswersToSurveyData,
} from '@/utils/surveyjsConverter'

// SurveyJS 结果 → 系统格式
const surveyResult = {
  q1: 'opt1',
  q2: ['opt1', 'opt2'],
}

const answers = convertSurveyResultToAnswers(surveyResult, content.items)
// { q1: { answer: 'opt1' }, q2: { answer: ['opt1', 'opt2'] } }

// 系统格式 → SurveyJS 数据（用于回显）
const surveyData = convertAnswersToSurveyData(answers, content.items)
// { q1: 'opt1', q2: ['opt1', 'opt2'] }
```

## 已知限制

1. **代码编辑器**: SurveyJS 不支持代码高亮，使用普通文本输入替代
2. **文件上传**: 需要额外配置服务器端文件处理
3. **互评功能**: 需要自定义扩展
4. **实时协作**: SurveyJS 不直接支持，需要结合 WebSocket

## 故障排除

### 样式问题

如果 SurveyJS 样式与项目不匹配：

1. 检查 CSS 导入：确保 `survey-core/survey-core.min.css` 已导入
2. 使用 `:deep()` 选择器覆盖样式
3. 检查 Tailwind CSS 冲突

### 数据转换问题

如果答案格式不正确：

1. 检查 `convertSurveyResultToAnswers` 的转换逻辑
2. 验证题型映射是否正确
3. 查看浏览器控制台的错误信息

### 提交问题

如果提交失败：

1. 确保答案格式符合后端 API 要求
2. 检查 `ItemAnswer` 类型定义
3. 验证必答题是否已全部完成

## 参考资料

- [SurveyJS 官方文档](https://surveyjs.io/)
- [SurveyJS Vue 3 集成](https://surveyjs.io/form-library/documentation/get-started-vue)
- [SurveyJS GitHub](https://github.com/surveyjs/survey-library)

## 更新日志

### 2024-11-30
- ✅ 初始集成 SurveyJS
- ✅ 创建数据转换器
- ✅ 创建 SurveyJSViewer 组件
- ✅ 集成到 ActivityViewer

