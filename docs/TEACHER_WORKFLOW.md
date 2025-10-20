# 教师工作台工作流逻辑

## 概述

本文档详细描述教师在 InspireEd 平台上创建、编辑和管理教案的完整工作流程。

---

## 一、核心工作流程图

```
登录系统 → 教师仪表盘 → 创建/选择教案 → 教案编辑 → 保存/发布 → 教案管理
   ↓           ↓              ↓              ↓            ↓           ↓
 认证    浏览课程体系    选择课程模板    添加教学单元    自动保存    状态管理
```

---

## 二、详细工作流程

### 1. 登录与身份认证

**入口：** `/login`

**流程：**
- 教师输入用户名和密码
- 系统验证身份（通过 `userStore.login()`）
- 验证成功后自动跳转到教师仪表盘 `/teacher`

**相关文件：**
- `frontend/src/pages/Login.vue`
- `frontend/src/store/user.ts`
- `frontend/src/services/auth.ts`

---

### 2. 教师仪表盘（Dashboard）

**路由：** `/teacher`

**核心功能：**

#### 2.1 课程体系浏览
- 顶部展示 **课程结构组件**（EnhancedCurriculumStructure）
- 可浏览完整的 **学科 → 年级 → 课程 → 章节 → 资源** 层级结构
- 支持按年级/学科筛选教案

#### 2.2 教案列表展示
- 以卡片形式展示所有教案（LessonCard）
- 每个教案卡片显示：
  - 封面图（默认渐变背景）
  - 标题和描述
  - 状态标签（草稿/已发布/已归档）
  - 标签（tags）
  - 更新时间
  - 单元数量

#### 2.3 搜索与筛选
- **搜索框：** 按教案标题搜索（带防抖，300ms）
- **状态筛选：** 全部/草稿/已发布/已归档
- **年级筛选：** 通过课程结构组件选择

#### 2.4 分页功能
- 每页显示 20 个教案
- 支持上一页/下一页导航
- 显示当前页数和总页数

#### 2.5 教案操作
从教案卡片可以执行：
- **查看/编辑：** 点击卡片或"编辑"按钮 → 跳转到编辑页
- **复制：** 快速复制现有教案
- **发布：** 将草稿状态改为已发布
- **删除：** 删除教案（带确认对话框）

**相关文件：**
- `frontend/src/pages/Teacher/Dashboard.vue`
- `frontend/src/components/Curriculum/EnhancedCurriculumStructure.vue`
- `frontend/src/components/Lesson/LessonCard.vue`

---

### 3. 创建新教案

**触发方式：** 点击"创建新教案"按钮

**创建流程：**

#### 3.1 选择课程
1. **选择学科**（如：数学、物理、计算机科学）
2. **选择年级**（如：一年级～高三）
3. **自动加载课程**（系统根据学科+年级查找对应课程）
4. 如果课程不存在，显示提示联系管理员创建

#### 3.2 填写基本信息
- **教案标题**（必填，最多100字符）
- **教案描述**（可选）
- **标签**（可选，用逗号分隔）

#### 3.3 选择模板
提供三种初始模板：
- **空白教案** 📄 - 从零开始
- **理论课** 📚 - 预置文本单元
- **实验课** 💻 - 预置文本+代码单元

#### 3.4 创建教案
- 点击"创建教案"按钮
- 系统调用 `lessonService.createLesson()`
- 创建成功后自动跳转到编辑页面

**数据流：**
```
CreateLessonModal → lessonStore.createNewLesson() → API请求 → 跳转到编辑页
```

**相关文件：**
- `frontend/src/components/Lesson/CreateLessonModal.vue`
- `frontend/src/store/lesson.ts`
- `frontend/src/services/lesson.ts`

---

### 4. 教案编辑（核心功能）

**路由：** `/teacher/lesson/:id`

**页面布局：**

```
┌──────────────────────────────────────────────────────────┐
│  ← 返回 | [教案标题]  | 保存状态 | 保存 | 发布 | 预览模式  │
├──────────────────────────────────────────────────────────┤
│  📦     │                                                 │
│  工具栏 │              教案内容区                         │
│         │         (Cell 单元列表)                         │
│  [Cell  │                                                 │
│  类型]  │                                                 │
└──────────────────────────────────────────────────────────┘
```

#### 4.1 左侧工具栏（CellToolbar）
提供7种教学单元类型：
- **📝 文本单元（TEXT）** - 富文本编辑器
- **💻 代码单元（CODE）** - 代码编辑和执行
- **🔧 参数单元（PARAM）** - 交互式参数调整
- **🎮 仿真单元（SIM）** - 3D/2D 仿真场景
- **❓ 问答单元（QA）** - 问答交互
- **📊 图表单元（CHART）** - 数据可视化
- **🏆 竞赛单元（CONTEST）** - 竞赛任务

#### 4.2 中间编辑区
**Cell 容器特性：**
- 每个 Cell 独立编辑
- 支持拖拽排序（使用 Sortable.js）
- 支持上移/下移按钮
- Cell 之间显示"添加"按钮，可在任意位置插入新单元

**Cell 操作：**
- **编辑内容：** 每个 Cell 有自己的编辑界面
- **移动位置：** 拖拽或使用上移/下移按钮
- **删除单元：** 点击删除按钮（带确认）

#### 4.3 自动保存机制
- **自动保存间隔：** 3秒（使用 `useAutoSave` composable）
- **保存状态显示：**
  - 🔄 保存中...
  - ✅ 已保存
  - ❌ 保存失败
  - 🕐 X分钟前保存
- **手动保存：** 点击"保存"按钮强制保存

**保存逻辑：**
```typescript
监听数据变化 → 防抖（3秒） → 调用 lessonStore.saveCurrentLesson() → 更新保存状态
```

#### 4.4 预览模式
- 切换到预览模式后：
  - 隐藏左侧工具栏
  - 隐藏 Cell 操作按钮
  - 隐藏添加按钮
  - 禁用拖拽功能
  - 以学生视角查看内容

#### 4.5 发布教案
- 仅草稿状态显示"发布"按钮
- 点击发布后状态变为"已发布"
- 已发布的教案学生可见

**相关文件：**
- `frontend/src/pages/Teacher/LessonEditor.vue`
- `frontend/src/components/Lesson/CellToolbar.vue`
- `frontend/src/components/Lesson/AddCellMenu.vue`
- `frontend/src/components/Cell/CellContainer.vue`
- `frontend/src/composables/useAutoSave.ts`

---

### 5. Cell 单元详细说明

#### 5.1 文本单元（TextCell）
- 使用 TipTap 富文本编辑器
- 支持标题、段落、列表、引用等格式
- 支持插入链接、图片

#### 5.2 代码单元（CodeCell）
- 支持 Python 代码编辑
- 使用 Pyodide 在浏览器端执行
- 显示代码输出结果
- 支持 Monaco Editor 语法高亮

#### 5.3 参数单元（ParamCell）
- 动态表单生成
- 支持多种参数类型（数字、文本、选择框等）
- 参数值可被其他 Cell 引用

#### 5.4 仿真单元（SimCell）
- 支持 Three.js 3D 场景
- 支持 2D Canvas 绘图
- 可配置仿真参数

#### 5.5 问答单元（QACell）
- 教师输入问题和答案
- 可选支持 AI 生成答案
- 学生可查看答案或尝试回答

#### 5.6 图表单元（ChartCell）
- 支持柱状图、折线图、饼图等
- 使用 Chart.js 或类似库
- 可配置数据和样式

#### 5.7 竞赛单元（ContestCell）
- 定义竞赛任务标题和描述
- 设置竞赛规则
- 可配置评分标准

**相关文件：**
- `frontend/src/components/Cell/` 目录下各 Cell 组件
- `frontend/src/types/cell.ts`

---

### 6. 教案状态管理

#### 6.1 教案状态流转

```
创建 → 草稿（DRAFT）→ 已发布（PUBLISHED）→ 已归档（ARCHIVED）
        ↑_______________|
           (取消发布)
```

#### 6.2 状态说明
- **草稿（DRAFT）：** 初始状态，仅教师可见，可编辑
- **已发布（PUBLISHED）：** 学生可见，教师可继续编辑
- **已归档（ARCHIVED）：** 不再活跃，但保留历史记录

#### 6.3 权限控制
- 教师可以查看和编辑自己创建的所有教案
- 教师可以复制其他教师的已发布教案（如果系统支持）

---

## 三、数据流架构

### 3.1 状态管理（Pinia Store）

```typescript
lessonStore (frontend/src/store/lesson.ts)
├── 状态
│   ├── currentLesson: 当前编辑的教案
│   ├── lessons: 教案列表
│   ├── isLoading: 加载状态
│   ├── isSaving: 保存状态
│   ├── error: 错误信息
│   ├── totalLessons: 总教案数
│   ├── currentPage: 当前页
│   └── pageSize: 每页数量
│
├── 计算属性
│   └── cells: 当前教案的 Cell 列表
│
├── 本地操作方法
│   ├── addCell(): 添加 Cell
│   ├── updateCell(): 更新 Cell
│   ├── deleteCell(): 删除 Cell
│   └── reorderCells(): 重排 Cell 顺序
│
└── 异步操作方法
    ├── loadLessons(): 加载教案列表
    ├── loadLesson(): 加载单个教案
    ├── createNewLesson(): 创建教案
    ├── saveCurrentLesson(): 保存教案
    ├── publishCurrentLesson(): 发布教案
    ├── deleteLessonById(): 删除教案
    └── duplicateLessonById(): 复制教案
```

### 3.2 API 调用流程

```
Vue 组件 → Pinia Store → Service 层 → API 层 → Backend API
   ↓          ↓            ↓            ↓           ↓
 UI逻辑   状态管理    业务逻辑    HTTP请求   数据处理
```

---

## 四、关键技术特性

### 4.1 自动保存机制
```typescript
// 使用 composable 实现
useAutoSave({
  data: computed(() => lessonStore.currentLesson),
  saveFn: async () => await lessonStore.saveCurrentLesson(),
  delay: 3000,
  enabled: computed(() => !isPreviewMode.value)
})
```

### 4.2 搜索防抖
```typescript
// 使用 VueUse 的 useDebounceFn
const debouncedSearch = useDebounceFn(() => {
  lessonStore.currentPage = 1
  loadLessons()
}, 300)
```

### 4.3 拖拽排序
```typescript
// 使用 Sortable.js
Sortable.create(cellListRef.value, {
  animation: 150,
  handle: '.drag-handle',
  onEnd: (evt) => {
    lessonStore.reorderCells(evt.oldIndex, evt.newIndex)
  }
})
```

### 4.4 响应式数据同步
- 标题变化实时同步到 store
- Cell 内容变化触发自动保存
- 列表操作后自动刷新

---

## 五、用户交互流程示例

### 示例1：创建一个新的 Python 编程教案

1. **进入仪表盘** → 点击"创建新教案"
2. **填写信息：**
   - 学科：计算机科学
   - 年级：高一
   - 标题："Python 基础：变量和数据类型"
   - 模板：实验课 💻
3. **系统创建教案** → 自动跳转到编辑器
4. **编辑内容：**
   - 修改预置的文本单元：添加课程概述
   - 修改预置的代码单元：写示例代码
   - 从工具栏添加新的问答单元：添加练习题
   - 拖拽调整单元顺序
5. **自动保存** → 系统每3秒自动保存
6. **预览** → 切换到预览模式查看效果
7. **发布** → 点击"发布"按钮，学生可见

### 示例2：编辑现有教案

1. **进入仪表盘** → 在列表中找到目标教案
2. **搜索/筛选：**
   - 使用搜索框输入关键词
   - 或使用状态筛选器
3. **点击教案卡片** → 进入编辑器
4. **编辑：**
   - 修改某个 Cell 的内容
   - 添加新的 Cell
   - 删除不需要的 Cell
5. **保存** → 自动保存或手动点击保存
6. **返回** → 点击返回按钮回到仪表盘

### 示例3：复制并修改教案

1. **进入仪表盘** → 找到要复制的教案
2. **点击复制按钮** → 系统创建副本
3. **副本出现在列表顶部** → 标题自动加上"(副本)"
4. **点击编辑** → 修改副本内容
5. **发布** → 作为新教案发布

---

## 六、注意事项与最佳实践

### 6.1 性能优化
- 教案列表使用分页，避免一次加载过多数据
- 搜索使用防抖，减少不必要的 API 请求
- Cell 组件使用 key 优化渲染性能

### 6.2 数据安全
- 自动保存确保数据不丢失
- 删除操作需要二次确认
- 离开编辑页前检查是否有未保存的更改（可增强）

### 6.3 用户体验
- 提供实时的保存状态反馈
- 操作后显示 Toast 提示
- 加载状态使用骨架屏而非空白
- 空状态提供清晰的引导

### 6.4 教案设计建议
- 合理使用不同类型的 Cell，保持教案结构清晰
- 理论课建议：文本单元 + 问答单元
- 实验课建议：文本单元 + 代码单元 + 参数单元
- 可视化内容使用：图表单元 + 仿真单元

---

## 七、相关文件索引

### 前端页面
- `frontend/src/pages/Teacher/Dashboard.vue` - 教师仪表盘
- `frontend/src/pages/Teacher/LessonEditor.vue` - 教案编辑器
- `frontend/src/pages/Login.vue` - 登录页面

### 核心组件
- `frontend/src/components/Lesson/LessonCard.vue` - 教案卡片
- `frontend/src/components/Lesson/CreateLessonModal.vue` - 创建教案对话框
- `frontend/src/components/Lesson/CellToolbar.vue` - Cell 工具栏
- `frontend/src/components/Lesson/AddCellMenu.vue` - 添加 Cell 菜单
- `frontend/src/components/Cell/CellContainer.vue` - Cell 容器
- `frontend/src/components/Curriculum/EnhancedCurriculumStructure.vue` - 课程结构

### Cell 组件
- `frontend/src/components/Cell/TextCell.vue` - 文本单元
- `frontend/src/components/Cell/CodeCell.vue` - 代码单元
- `frontend/src/components/Cell/ParamCell.vue` - 参数单元
- `frontend/src/components/Cell/SimCell.vue` - 仿真单元
- `frontend/src/components/Cell/QACell.vue` - 问答单元
- `frontend/src/components/Cell/ChartCell.vue` - 图表单元
- `frontend/src/components/Cell/ContestCell.vue` - 竞赛单元

### 状态管理
- `frontend/src/store/lesson.ts` - 教案状态管理
- `frontend/src/store/user.ts` - 用户状态管理

### 服务层
- `frontend/src/services/lesson.ts` - 教案 API 服务
- `frontend/src/services/auth.ts` - 认证 API 服务
- `frontend/src/services/curriculum.ts` - 课程 API 服务

### 工具函数
- `frontend/src/composables/useAutoSave.ts` - 自动保存 composable

### 类型定义
- `frontend/src/types/lesson.ts` - 教案类型
- `frontend/src/types/cell.ts` - Cell 类型
- `frontend/src/types/curriculum.ts` - 课程类型
- `frontend/src/types/user.ts` - 用户类型

### 后端 API
- `backend/app/api/v1/lessons.py` - 教案 API 路由
- `backend/app/models/lesson.py` - 教案数据模型
- `backend/app/schemas/lesson.py` - 教案数据架构

---

## 八、后续优化方向

1. **协作编辑：** 支持多个教师同时编辑同一教案
2. **版本控制：** 记录教案的修改历史，支持回滚
3. **模板市场：** 教师可以分享和使用教案模板
4. **AI 辅助：** 使用 AI 生成教案内容建议
5. **批量操作：** 支持批量发布、归档、删除教案
6. **导入导出：** 支持导出为 PDF、Markdown 等格式
7. **离线编辑：** 支持离线编辑，在线同步
8. **统计分析：** 展示教案使用情况、学生反馈等数据

---

**文档版本：** v1.0  
**最后更新：** 2025-10-17  
**维护者：** InspireEd 开发团队

