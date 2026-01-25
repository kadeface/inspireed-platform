# 教案优化功能设计文档

## 功能概述

教案优化功能是 AI 教学助理的核心功能之一，能够基于学习科学理论对指定教案进行全面分析，提供多维度、结构化的优化建议。

## 设计思路

### 1. 功能定位

- **目标用户**：教师
- **使用场景**：教师在仪表盘查看教案列表时，想要快速了解某个教案的质量并进行优化
- **核心价值**：基于学习科学理论，提供专业、可操作的优化建议

### 2. 设计原则

#### 2.1 多维度分析
教案优化不是单一维度的评价，而是从多个角度全面分析：
- **教学目标设计**：是否明确、是否基于布鲁姆分类法
- **活动设计**：是否符合5E模型、是否有认知层次
- **学生参与度**：是否有主动输出、是否有互动
- **评价设计**：是否有形成性评价、是否有元认知反思
- **学习科学理论应用**：是否应用了相关理论

#### 2.2 结构化输出
优化报告采用结构化格式，便于教师快速理解：
- **总体评分**：0-100分的综合评分
- **维度评分**：每个维度的具体分数
- **优势分析**：当前教案的亮点
- **待改进点**：需要优化的地方
- **具体建议**：可操作的优化方案

#### 2.3 学习科学理论驱动
所有优化建议都基于学习科学理论：
- 布鲁姆分类法（Bloom's Taxonomy）
- 苏格拉底式提问法（Socratic Questioning）
- 费曼学习法（Feynman Technique）
- 5E教学模型
- 建构主义学习理论
- 学习风格和差异化教学
- 元认知和主动输出

### 3. 用户界面设计

#### 3.1 功能入口
- 位置：在"教案共创"主题下显示
- 形式：独立的优化分析卡片
- 交互：选择教案 → 点击"一键优化分析"按钮

#### 3.2 教案选择器
- 显示所有可用的教案（草稿和已发布）
- 下拉选择框，显示教案标题和状态
- 支持快速切换不同教案

#### 3.3 优化报告展示
- **总体评分卡片**：大号数字显示，进度条可视化
- **维度分析卡片**：每个维度独立卡片，包含：
  - 维度名称和分数
  - 进度条（颜色编码：绿色≥80，黄色≥60，红色<60）
  - 优势列表（绿色）
  - 待改进点列表（红色）
  - 优化建议列表（蓝色）
- **详细方案**：Markdown 格式的完整优化方案

## 技术实现

### 1. 前端实现

#### 1.1 组件结构
```vue
<TeacherAiAssistantModal>
  <!-- 教案优化功能（仅在 lesson_plan 主题显示） -->
  <div v-if="selectedTopic === 'lesson_plan'">
    <!-- 教案选择器 -->
    <select v-model="selectedLessonId">
      <option>请选择教案...</option>
      <option v-for="lesson in availableLessons">
        {{ lesson.title }} ({{ lesson.status }})
      </option>
    </select>
    
    <!-- 优化按钮 -->
    <button @click="handleOptimizeLesson">
      一键优化分析
    </button>
  </div>
  
  <!-- 优化报告展示 -->
  <div v-if="optimizationReport">
    <!-- 总体评分 -->
    <!-- 维度分析 -->
    <!-- 详细方案 -->
  </div>
</TeacherAiAssistantModal>
```

#### 1.2 状态管理
```typescript
const selectedLessonId = ref<number | null>(null)
const isOptimizing = ref(false)
const optimizationReport = ref<any>(null)
```

#### 1.3 API 调用
```typescript
async function handleOptimizeLesson() {
  // 构建优化分析问题
  const optimizationQuestion = `请对教案《${lesson.title}》进行全面优化分析...`
  
  // 调用 AI 助理 API
  const response = await assistantService.askTeacherAssistant({
    question: optimizationQuestion,
    topic: 'lesson_plan',
    lesson_id: selectedLessonId.value,
    context: { ... }
  })
  
  // 解析优化报告
  optimizationReport.value = parseOptimizationReport(response.answer)
}
```

### 2. 后端实现

#### 2.1 API 端点
使用现有的 `/teacher/assistant/query` 端点，通过 `lesson_id` 参数获取教案详情。

#### 2.2 教案分析逻辑
```python
@router.post("/query")
async def query_teacher_assistant(
    payload: AssistantRequest,
    ...
):
    # 如果提供了 lesson_id，获取教案详情
    if payload.lesson_id:
        lesson = await db.get(Lesson, payload.lesson_id)
        lesson_title = lesson.title
        lesson_content = lesson.content  # 教案结构
    
    # 构建上下文（包含教案结构）
    context_lines = _build_context_lines(payload)
    if lesson_content:
        context_lines.append(f"教案结构：{format_lesson_structure(lesson_content)}")
    
    # 调用 AI 服务
    ai_result = await ai_qa_service.ask_question(
        question=payload.question,
        context=context_text,
        lesson_title=lesson_title,
    )
    
    return AssistantResponse(...)
```

#### 2.3 AI 提示词设计
当检测到是优化分析请求时，AI 会：
1. 分析教案的各个维度
2. 基于学习科学理论进行评估
3. 生成结构化的优化报告

提示词模板：
```
请对教案《{lesson_title}》进行全面优化分析，包括：

1. 教学目标设计（是否明确、是否基于布鲁姆分类法）
2. 活动设计（是否符合5E模型、是否有认知层次）
3. 学生参与度（是否有主动输出、是否有互动）
4. 评价设计（是否有形成性评价、是否有元认知反思）
5. 学习科学理论应用（是否应用了相关理论）

请提供结构化的分析报告，包括：
- 总体评分（0-100分）
- 各维度评分和详细分析
- 优势、待改进点、具体优化建议
- 基于学习科学理论的详细优化方案

教案结构：
{lesson_structure}
```

### 3. 报告解析

#### 3.1 结构化数据提取
AI 返回的可能是：
- JSON 格式的结构化数据（理想情况）
- Markdown 格式的文本报告（需要解析）

#### 3.2 解析策略
```typescript
function parseOptimizationReport(answer: string): any {
  // 1. 尝试解析 JSON
  const jsonMatch = answer.match(/```json\s*([\s\S]*?)\s*```/)
  if (jsonMatch) {
    return JSON.parse(jsonMatch[1])
  }
  
  // 2. 从文本中提取信息
  const report = {
    overall_score: extractScore(answer),
    dimensions: extractDimensions(answer),
    detailed_suggestions: answer
  }
  
  return report
}
```

## 优化分析维度详解

### 1. 教学目标设计（0-100分）

**评估标准**：
- 教学目标是否明确、可衡量
- 是否基于布鲁姆分类法设计认知层次
- 是否包含知识、技能、态度三个维度

**优化建议示例**：
- "建议为每个教学目标添加可衡量的达成指标"
- "可以基于布鲁姆分类法，设计从记忆到创造的认知层次目标"

### 2. 活动设计（0-100分）

**评估标准**：
- 是否符合5E教学模型（Engage-Explore-Explain-Elaborate-Evaluate）
- 是否有完整的认知层次（记忆→理解→应用→分析→评价→创造）
- 活动之间是否有逻辑衔接

**优化建议示例**：
- "建议增加 Explore（探索）环节，让学生主动发现"
- "可以设计一个从低阶到高阶思维的完整活动序列"

### 3. 学生参与度（0-100分）

**评估标准**：
- 是否有主动输出活动（费曼学习法）
- 是否有互动和协作环节
- 是否考虑了不同学习风格

**优化建议示例**：
- "建议增加让学生用自己的话解释概念的活动"
- "可以设计小组讨论和同伴互评环节"

### 4. 评价设计（0-100分）

**评估标准**：
- 是否有形成性评价
- 是否有元认知反思环节
- 评价方式是否多样化

**优化建议示例**：
- "建议增加过程性评价，及时反馈学生学习情况"
- "可以设计自我评估和反思环节，培养元认知能力"

### 5. 学习科学理论应用（0-100分）

**评估标准**：
- 是否应用了布鲁姆分类法
- 是否应用了5E教学模型
- 是否应用了建构主义理论
- 是否考虑了学习风格和差异化

**优化建议示例**：
- "建议基于最近发展区理论，设计脚手架支持"
- "可以应用苏格拉底式提问法，引导学生深入思考"

## 使用流程

1. **打开 AI 教学助理**
   - 在教师仪表盘点击"AI 教学助理"按钮

2. **选择主题**
   - 选择"教案共创"主题

3. **选择教案**
   - 在"教案优化分析"卡片中选择要优化的教案

4. **触发优化**
   - 点击"一键优化分析"按钮

5. **查看报告**
   - 等待 AI 分析完成
   - 查看总体评分和维度分析
   - 阅读详细优化方案

6. **应用建议**
   - 根据优化建议改进教案
   - 可以复制报告保存

## 未来优化方向

### 1. 更智能的解析
- 使用专门的 AI 模型解析优化报告
- 支持更复杂的结构化数据提取

### 2. 历史对比
- 保存优化历史
- 对比优化前后的改进

### 3. 批量优化
- 支持一次分析多个教案
- 生成对比报告

### 4. 可视化增强
- 使用图表展示维度评分
- 提供雷达图等可视化工具

### 5. 个性化建议
- 基于教师的教学风格提供个性化建议
- 考虑学生的特点和学习数据

## 相关文件

- `frontend/src/components/Teacher/TeacherAiAssistantModal.vue` - 主组件
- `backend/app/api/v1/teacher_ai_assistant.py` - 后端 API
- `backend/app/services/ai_qa.py` - AI 服务
- `docs/features/AI_LESSON_ASSISTANT_WORKFLOW.md` - AI 助理工作流程文档

