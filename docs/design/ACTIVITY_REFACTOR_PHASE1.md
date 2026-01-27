# Activity 组件重构 - 第一阶段：拆分题型组件

## 📋 目标

将 `ActivityViewer.vue` 中内联的题型渲染逻辑（约 165 行）拆分为独立的题型组件，实现：
- **代码量减少**：ActivityViewer 从 1140 行 → 约 900 行（减少 ~20%）
- **可维护性提升**：每个题型独立维护，职责清晰
- **可扩展性提升**：新增题型只需添加新组件
- **向后兼容**：不影响现有功能

---

## 📁 文件结构规划

```
frontend/src/components/Activity/
├── ActivityViewer.vue              # 主组件（简化后）
├── ActivityItemModal.vue           # 保持不变
├── ActivityCellEditor.vue          # 保持不变
├── SubmissionStatistics.vue        # 保持不变
│
└── ItemTypes/                      # 🆕 题型组件目录
    ├── ItemRenderer.vue            # 🆕 题型渲染器（根据类型动态加载）
    ├── SingleChoiceItem.vue        # 🆕 单选题组件
    ├── MultipleChoiceItem.vue      # 🆕 多选题组件
    ├── TrueFalseItem.vue          # 🆕 判断题组件
    ├── ShortAnswerItem.vue         # 🆕 简答题组件
    ├── LongAnswerItem.vue          # 🆕 论述题组件
    ├── ScaleItem.vue               # 🆕 量表评分组件
    └── shared/                      # 🆕 共享组件
        └── ItemFeedback.vue        # 🆕 反馈信息组件（统一）
```

---

## 🎯 实施步骤

### Step 1: 创建共享反馈组件

**文件**: `ItemTypes/shared/ItemFeedback.vue`

**职责**: 统一显示答题反馈（正确/错误、得分等）

**Props**:
```typescript
interface Props {
  answer: any              // 题目答案数据
  points?: number          // 题目分值
  showScore?: boolean      // 是否显示得分
}
```

**功能**:
- 显示正确/错误提示
- 显示正确答案
- 显示得分（如果已评分）

---

### Step 2: 创建单选题组件

**文件**: `ItemTypes/SingleChoiceItem.vue`

**职责**: 渲染单选题界面

**Props**:
```typescript
interface Props {
  item: SingleChoiceItem           // 题目数据
  modelValue: string | undefined   // 当前答案（v-model）
  isSubmitted: boolean             // 是否已提交
  answerData?: any                 // 提交后的答案数据（包含正确性）
}
```

**Emits**:
```typescript
{
  'update:modelValue': [value: string]
  'change': [itemId: string]
}
```

**功能**:
- 渲染选项列表（radio）
- 显示选中状态
- 提交后显示正确/错误标记
- 集成 ItemFeedback 组件

**代码量**: 约 80-100 行

---

### Step 3: 创建多选题组件

**文件**: `ItemTypes/MultipleChoiceItem.vue`

**职责**: 渲染多选题界面

**Props**:
```typescript
interface Props {
  item: MultipleChoiceItem
  modelValue: string[] | undefined
  isSubmitted: boolean
  answerData?: any
}
```

**功能**:
- 渲染选项列表（checkbox）
- 显示选中状态
- 提交后显示正确/错误标记
- 集成 ItemFeedback 组件

**代码量**: 约 80-100 行

---

### Step 4: 创建判断题组件

**文件**: `ItemTypes/TrueFalseItem.vue`

**职责**: 渲染判断题界面

**Props**:
```typescript
interface Props {
  item: TrueFalseItem
  modelValue: boolean | undefined
  isSubmitted: boolean
  answerData?: any
}
```

**功能**:
- 渲染"正确"/"错误"两个选项
- 显示选中状态
- 提交后显示正确/错误标记
- 集成 ItemFeedback 组件

**代码量**: 约 60-80 行

---

### Step 5: 创建文本题组件（简答+论述）

**文件**: `ItemTypes/ShortAnswerItem.vue` 和 `ItemTypes/LongAnswerItem.vue`

**职责**: 渲染文本输入题界面

**Props**:
```typescript
interface Props {
  item: ShortAnswerItem | LongAnswerItem
  modelValue: string | undefined
  isSubmitted: boolean
  answerData?: any
}
```

**功能**:
- 渲染 textarea
- 显示字数统计（如果有 maxLength）
- 集成 ItemFeedback 组件

**代码量**: 约 50-70 行（两个组件可共享大部分代码）

---

### Step 6: 创建量表评分组件

**文件**: `ItemTypes/ScaleItem.vue`

**职责**: 渲染量表评分界面

**Props**:
```typescript
interface Props {
  item: ScaleItem
  modelValue: number | undefined
  isSubmitted: boolean
  answerData?: any
}
```

**功能**:
- 渲染量表选项（1-5 或自定义范围）
- 显示标签（minLabel, maxLabel）
- 集成 ItemFeedback 组件

**代码量**: 约 60-80 行

---

### Step 7: 创建题型渲染器

**文件**: `ItemTypes/ItemRenderer.vue`

**职责**: 根据题型类型动态加载对应的题型组件

**Props**:
```typescript
interface Props {
  item: ActivityItem
  modelValue: any
  isSubmitted: boolean
  answerData?: any
}
```

**实现方式**:
```vue
<template>
  <component
    :is="componentName"
    :item="item"
    :model-value="modelValue"
    :is-submitted="isSubmitted"
    :answer-data="answerData"
    @update:model-value="$emit('update:modelValue', $event)"
    @change="$emit('change', $event)"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ActivityItem } from '@/types/activity'
import SingleChoiceItem from './SingleChoiceItem.vue'
import MultipleChoiceItem from './MultipleChoiceItem.vue'
// ... 其他组件

const componentMap = {
  'single-choice': SingleChoiceItem,
  'multiple-choice': MultipleChoiceItem,
  'true-false': TrueFalseItem,
  'short-answer': ShortAnswerItem,
  'long-answer': LongAnswerItem,
  'scale': ScaleItem,
  // 'file-upload': FileUploadItem,  // 待实现
  // 'code-submission': CodeSubmissionItem,  // 待实现
  // 'rubric-item': RubricItem,  // 待实现
}

const componentName = computed(() => {
  return componentMap[props.item.type] || 'div' // 未实现的题型显示占位
})
</script>
```

**代码量**: 约 50-70 行

---

### Step 8: 重构 ActivityViewer

**修改点**:

1. **移除题型渲染逻辑**（第 75-240 行）
   ```vue
   <!-- 旧代码：165 行内联逻辑 -->
   <div v-if="item.type === 'single-choice'">...</div>
   <div v-if="item.type === 'multiple-choice'">...</div>
   <!-- ... -->
   
   <!-- 新代码：1 行 -->
   <ItemRenderer
     :item="item"
     v-model="answers[item.id]"
     :is-submitted="isSubmitted"
     :answer-data="getItemAnswer(item.id)"
     @change="saveAnswer(item.id)"
   />
   ```

2. **移除题型判断函数**（保留 getItemAnswer，移除 isCorrectAnswerForSingle 等）

3. **导入新组件**
   ```typescript
   import ItemRenderer from './ItemTypes/ItemRenderer.vue'
   ```

4. **保留必要的辅助函数**
   - `getItemAnswer()` - 仍需要，用于获取答案数据
   - `getItemTypeLabel()` - 仍需要，用于显示题型标签
   - `scaleRange()` - 可移到 ScaleItem 组件内部

---

## 📊 预期效果

### 代码量对比

| 文件 | 重构前 | 重构后 | 变化 |
|------|--------|--------|------|
| ActivityViewer.vue | 1140 行 | ~900 行 | -240 行 (-21%) |
| ItemTypes/ (新增) | 0 | ~600 行 | +600 行 |
| **总计** | 1140 行 | 1500 行 | +360 行 |

**说明**: 虽然总代码量增加，但：
- ✅ 代码组织更清晰（单一职责）
- ✅ 每个组件更易维护（50-100 行 vs 1140 行）
- ✅ 可复用性提升（题型组件可在其他地方使用）
- ✅ 测试更容易（可单独测试每个题型）

### 可维护性提升

- **修改单选题逻辑**：只需修改 `SingleChoiceItem.vue`（~100 行）
- **新增题型**：只需添加新组件 + 在 ItemRenderer 中注册
- **统一反馈样式**：只需修改 `ItemFeedback.vue`

---

## ✅ 实施检查清单

### 开发阶段

- [ ] Step 1: 创建 `ItemFeedback.vue` 共享组件
- [ ] Step 2: 创建 `SingleChoiceItem.vue`
- [ ] Step 3: 创建 `MultipleChoiceItem.vue`
- [ ] Step 4: 创建 `TrueFalseItem.vue`
- [ ] Step 5: 创建 `ShortAnswerItem.vue` 和 `LongAnswerItem.vue`
- [ ] Step 6: 创建 `ScaleItem.vue`
- [ ] Step 7: 创建 `ItemRenderer.vue`
- [ ] Step 8: 重构 `ActivityViewer.vue`

### 测试阶段

- [ ] 单选题：选择、提交、反馈显示正常
- [ ] 多选题：多选、提交、反馈显示正常
- [ ] 判断题：选择、提交、反馈显示正常
- [ ] 简答题：输入、字数统计、提交正常
- [ ] 论述题：输入、字数统计、提交正常
- [ ] 量表题：选择、提交正常
- [ ] 离线保存：所有题型答案能正确保存
- [ ] 数据恢复：刷新后答案能正确恢复

### 兼容性检查

- [ ] 现有活动数据正常显示
- [ ] 提交功能正常
- [ ] 离线功能正常
- [ ] 反馈显示正常

---

## 🔄 迁移策略

### 渐进式迁移（推荐）

1. **并行开发**：先创建新组件，不删除旧代码
2. **功能开关**：添加 feature flag，可选择使用新旧组件
3. **逐步切换**：先切换一个题型，验证无误后再切换其他
4. **完全切换**：所有题型验证通过后，删除旧代码

### 一次性迁移

- 适合：团队有充分测试时间
- 风险：需要全面测试所有题型

---

## 📝 注意事项

1. **Props 接口统一**：所有题型组件使用相同的 props 结构
2. **事件命名统一**：使用 `update:modelValue` 和 `change` 事件
3. **样式隔离**：每个组件使用 `scoped` 样式
4. **类型安全**：使用 TypeScript 严格类型检查
5. **向后兼容**：确保现有功能不受影响

---

## 🚀 下一步（第二阶段）

完成第一阶段后，可继续：
- 提取业务逻辑到 composables（useActivityState, useCellIdResolver）
- 统一配置表单（ItemConfigForm）
- 进一步优化 ActivityViewer

---

## 📚 参考

- Vue 3 组件设计最佳实践
- TypeScript 类型定义：`frontend/src/types/activity.ts`
- 现有实现：`frontend/src/components/Activity/ActivityViewer.vue` (75-240 行)

