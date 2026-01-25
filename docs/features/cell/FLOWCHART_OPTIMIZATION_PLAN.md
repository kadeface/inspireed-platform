# 流程图模块优化方案

## 📊 现状分析

### 现有组件架构

1. **FlowchartCell.vue** - 教师编辑/学生查看模式切换
2. **FlowchartStudentCell.vue** - 学生任务流程图（支持本地存储、教师示例对比）
3. **FlowchartViewerCell.vue** - 简单查看器（只读）
4. **FlowchartEditor.vue** - 流程图编辑器（基于 Vue Flow）
5. **FlowchartViewer.vue** - 流程图查看器（只读模式）

### 后端支持

- `FlowchartSnapshot` 模型：保存学生流程图快照
- 仅在 Activity 提交时保存快照
- 缺少独立的流程图保存/加载 API

---

## ❌ 主要问题

### 1. **数据持久化问题**
- ❌ `FlowchartStudentCell` 仅使用 `localStorage`，数据易丢失
- ❌ 没有自动同步到后端
- ❌ 跨设备无法访问
- ❌ 没有版本控制

### 2. **组件职责混乱**
- ❌ `FlowchartCell`、`FlowchartViewerCell`、`FlowchartStudentCell` 功能重叠
- ❌ 缺少统一的组件选择逻辑
- ❌ 教师端和学生端组件分离不清晰

### 3. **性能问题**
- ❌ 深度 watch 导致频繁更新
- ❌ 每次更新都触发 JSON.stringify 比较
- ❌ 没有防抖优化
- ❌ 大量节点时渲染性能差

### 4. **功能缺失**
- ❌ 缺少撤销/重做功能
- ❌ 缺少流程图结构验证（孤立节点、循环检测等）
- ❌ 缺少版本历史查看
- ❌ 缺少实时协作
- ❌ 缺少流程图模板
- ❌ 缺少导入/导出（JSON格式）
- ❌ 缺少批量操作（复制、删除多个节点）

### 5. **代码质量问题**
- ❌ `FlowchartEditor` 和 `FlowchartViewer` 有大量重复代码
- ❌ 缺少统一的类型定义
- ❌ 错误处理不完善
- ❌ 缺少单元测试

### 6. **用户体验问题**
- ❌ 保存状态反馈不及时
- ❌ 没有冲突解决机制（教师更新时）
- ❌ 缺少快捷键支持
- ❌ 缺少操作提示

---

## ✅ 优化方案

### 一、架构重构

#### 1.1 统一组件架构

```
FlowchartCell (统一入口)
├── FlowchartEditor (编辑模式)
│   ├── FlowchartCanvas (画布核心)
│   ├── FlowchartToolbar (工具栏)
│   └── FlowchartSidebar (侧边栏：历史、模板等)
└── FlowchartViewer (查看模式)
    └── FlowchartCanvas (复用画布)
```

**优化点：**
- 统一入口组件，根据 `editable` 和用户角色选择模式
- 提取公共画布组件，减少代码重复
- 清晰的职责分离

#### 1.2 数据流优化

```
用户操作
  ↓
本地状态更新 (immediate)
  ↓
防抖处理 (600ms)
  ↓
保存到 localStorage (backup)
  ↓
API 同步到后端 (auto-save)
  ↓
版本快照 (重要节点)
```

### 二、功能增强

#### 2.1 数据持久化

**新增 API：**
```python
# backend/app/api/v1/cells.py

@router.post("/{cell_id}/flowchart/save")
async def save_flowchart(
    cell_id: int,
    content: FlowchartCellContent,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FlowchartSaveResponse:
    """保存流程图（自动保存）"""
    pass

@router.get("/{cell_id}/flowchart/history")
async def get_flowchart_history(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[FlowchartVersion]:
    """获取流程图版本历史"""
    pass

@router.post("/{cell_id}/flowchart/restore/{version_id}")
async def restore_flowchart_version(
    cell_id: int,
    version_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FlowchartCellContent:
    """恢复指定版本"""
    pass
```

**前端实现：**
- 自动保存到后端（防抖 2s）
- localStorage 作为离线备份
- 版本历史管理
- 冲突检测和解决

#### 2.2 撤销/重做功能

**实现方案：**
```typescript
// composables/useFlowchartHistory.ts
export function useFlowchartHistory() {
  const history = ref<FlowchartCellContent[]>([])
  const currentIndex = ref(-1)
  
  function push(content: FlowchartCellContent) {
    // 限制历史记录数量（最多50条）
    history.value = history.value.slice(0, currentIndex.value + 1)
    history.value.push(JSON.parse(JSON.stringify(content)))
    currentIndex.value = history.value.length - 1
  }
  
  function undo() {
    if (currentIndex.value > 0) {
      currentIndex.value--
      return history.value[currentIndex.value]
    }
  }
  
  function redo() {
    if (currentIndex.value < history.value.length - 1) {
      currentIndex.value++
      return history.value[currentIndex.value]
    }
  }
  
  return { push, undo, redo, canUndo, canRedo }
}
```

#### 2.3 流程图验证

**验证规则：**
- ✅ 检查孤立节点（没有连接的节点）
- ✅ 检查循环依赖
- ✅ 检查必须有开始和结束节点
- ✅ 检查决策节点必须有至少两个出口
- ✅ 检查节点标签不能为空

**实现：**
```typescript
// utils/flowchartValidator.ts
export function validateFlowchart(content: FlowchartCellContent): ValidationResult {
  const errors: string[] = []
  const warnings: string[] = []
  
  // 检查开始节点
  const startNodes = content.nodes.filter(n => n.type === 'start')
  if (startNodes.length === 0) {
    errors.push('流程图必须至少有一个开始节点')
  }
  
  // 检查结束节点
  const endNodes = content.nodes.filter(n => n.type === 'end')
  if (endNodes.length === 0) {
    errors.push('流程图必须至少有一个结束节点')
  }
  
  // 检查孤立节点
  const connectedNodeIds = new Set<string>()
  content.edges.forEach(edge => {
    connectedNodeIds.add(edge.source)
    connectedNodeIds.add(edge.target)
  })
  const isolatedNodes = content.nodes.filter(n => !connectedNodeIds.has(n.id))
  if (isolatedNodes.length > 0) {
    warnings.push(`发现 ${isolatedNodes.length} 个孤立节点`)
  }
  
  // 检查决策节点
  content.nodes.filter(n => n.type === 'decision').forEach(node => {
    const outgoingEdges = content.edges.filter(e => e.source === node.id)
    if (outgoingEdges.length < 2) {
      warnings.push(`决策节点 "${node.label}" 应该有至少两个出口`)
    }
  })
  
  return { valid: errors.length === 0, errors, warnings }
}
```

#### 2.4 性能优化

**优化措施：**
1. **虚拟滚动**：大量节点时使用虚拟列表
2. **按需渲染**：只渲染可见区域的节点
3. **防抖优化**：减少不必要的更新
4. **浅比较**：使用浅比较替代深度比较
5. **Web Worker**：复杂计算移到 Worker

```typescript
// 使用浅比较替代深度比较
const hasChanges = computed(() => {
  if (nodes.value.length !== props.content.nodes.length) return true
  if (edges.value.length !== props.content.edges.length) return true
  // 只比较关键字段
  return nodes.value.some((n, i) => 
    n.id !== props.content.nodes[i].id ||
    n.position.x !== props.content.nodes[i].position.x ||
    n.position.y !== props.content.nodes[i].position.y
  )
})
```

#### 2.5 用户体验优化

**新增功能：**
- ✅ 快捷键支持（Ctrl+Z 撤销，Ctrl+Y 重做，Delete 删除节点）
- ✅ 操作提示（Toast 通知）
- ✅ 加载状态指示
- ✅ 错误恢复机制
- ✅ 拖拽优化（更流畅的交互）
- ✅ 节点搜索功能
- ✅ 批量选择操作

### 三、代码质量提升

#### 3.1 提取公共逻辑

**创建 composables：**
- `useFlowchartEditor.ts` - 编辑器核心逻辑
- `useFlowchartHistory.ts` - 历史记录管理
- `useFlowchartValidation.ts` - 验证逻辑
- `useFlowchartPersistence.ts` - 持久化逻辑
- `useFlowchartAutoSave.ts` - 自动保存

#### 3.2 类型定义完善

```typescript
// types/flowchart.ts
export interface FlowchartValidationResult {
  valid: boolean
  errors: string[]
  warnings: string[]
}

export interface FlowchartVersion {
  id: number
  version: number
  content: FlowchartCellContent
  created_at: string
  created_by: number
}

export interface FlowchartSaveResponse {
  success: boolean
  version_id?: number
  saved_at: string
}
```

#### 3.3 错误处理

```typescript
// utils/flowchartErrorHandler.ts
export class FlowchartError extends Error {
  constructor(
    message: string,
    public code: string,
    public recoverable: boolean = false
  ) {
    super(message)
  }
}

export function handleFlowchartError(error: unknown) {
  if (error instanceof FlowchartError) {
    if (error.recoverable) {
      // 显示错误提示，允许重试
      showErrorToast(error.message, { retry: true })
    } else {
      // 严重错误，需要用户干预
      showErrorDialog(error.message)
    }
  } else {
    // 未知错误
    showErrorToast('发生未知错误，请刷新页面重试')
  }
}
```

---

## 🎯 实施计划

### Phase 1: 基础重构（优先级：高）
1. ✅ 统一组件架构
2. ✅ 提取公共画布组件
3. ✅ 实现自动保存到后端
4. ✅ 优化性能（防抖、浅比较）

### Phase 2: 核心功能（优先级：高）
1. ✅ 撤销/重做功能
2. ✅ 流程图验证
3. ✅ 版本历史查看
4. ✅ 错误处理完善

### Phase 3: 体验优化（优先级：中）
1. ✅ 快捷键支持
2. ✅ 操作提示
3. ✅ 批量操作
4. ✅ 节点搜索

### Phase 4: 高级功能（优先级：低）
1. ⏳ 实时协作（WebSocket）
2. ⏳ 流程图模板
3. ⏳ 导入/导出（JSON）
4. ⏳ 流程图分析（复杂度、路径等）

---

## 📝 技术细节

### 数据模型扩展

```typescript
// 扩展 FlowchartCellContent
export interface FlowchartCellContent {
  nodes: FlowchartNode[]
  edges: FlowchartEdge[]
  style?: {
    theme?: 'light' | 'dark'
    layoutDirection?: 'TB' | 'LR' | 'BT' | 'RL'
  }
  metadata?: {
    version?: number
    lastSaved?: string
    createdBy?: number
  }
}
```

### 后端模型扩展

```python
# backend/app/models/cell.py

class FlowchartVersion(Base):
    """流程图版本历史"""
    __tablename__ = "flowchart_versions"
    
    id = Column(Integer, primary_key=True)
    cell_id = Column(Integer, ForeignKey("cells.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    cell = relationship("Cell", back_populates="flowchart_versions")
    user = relationship("User")
```

---

## 🔍 测试计划

### 单元测试
- ✅ 流程图验证逻辑
- ✅ 历史记录管理
- ✅ 数据持久化
- ✅ 性能优化验证

### 集成测试
- ✅ 自动保存流程
- ✅ 版本恢复
- ✅ 冲突解决
- ✅ 离线同步

### E2E 测试
- ✅ 完整编辑流程
- ✅ 撤销/重做
- ✅ 版本历史查看
- ✅ 多设备同步

---

## 📊 预期收益

1. **数据安全**：自动保存到后端，避免数据丢失
2. **用户体验**：撤销/重做、验证提示等提升体验
3. **性能提升**：优化后支持更大规模的流程图
4. **代码质量**：减少重复代码，提高可维护性
5. **功能完整**：补齐缺失的核心功能

---

## 🚀 下一步行动

1. 创建优化任务清单
2. 开始 Phase 1 实施
3. 逐步迭代优化
4. 收集用户反馈
5. 持续改进

