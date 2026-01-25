# 授课模式下教师查看学生提交界面位置

## 📍 界面位置

在**授课模式**（Classroom Teaching Mode）下，教师查看学生提交的界面位于：

### 主界面：`TeacherControlPanel.vue`

**路径**: `frontend/src/components/Classroom/TeacherControlPanel.vue`

**显示位置**：
1. 在导播台（ClassroomControlBoard）下方
2. 当教师点击导播台中的**活动模块**（activity 类型）时自动显示

### 界面结构

```
TeacherControlPanel (授课模式主界面)
  ├── 会话状态栏（上课中/暂停/剩余时间）
  ├── 控制按钮（暂停/结束课程）
  ├── 在线学生列表
  └── 导播台
      └── 活动统计面板（当选中活动模块时显示）
          ├── SubmissionStatistics（实时统计）
          └── SubmissionList（学生提交详细列表）✨ 新增
```

## 🎯 显示逻辑

### 代码位置

```vue:208-223:frontend/src/components/Classroom/TeacherControlPanel.vue
<!-- 活动统计面板（当前 Cell 是 activity 类型时显示） -->
<div v-if="currentCell && currentCell.type === 'activity' && currentActivityDbCell" class="activity-panel mt-6">
  <SubmissionStatistics
    :cell-id="currentActivityDbCell.id"
    :lesson-id="lesson?.id || lessonId"
    :session-id="session.id"
  />
  
  <!-- 学生提交详细列表 -->
  <div class="mt-4">
    <SubmissionList
      :cell-id="currentActivityDbCell.id"
      :activity="currentCell.content"
    />
  </div>
</div>
```

### 显示条件

1. ✅ 当前选中的 Cell 类型为 `activity`
2. ✅ 已找到对应的数据库 Cell 记录（`currentActivityDbCell`）
3. ✅ 课堂会话已创建（`session` 存在）

## 📊 显示内容

### 1. SubmissionStatistics（实时统计）

**组件**: `frontend/src/components/Activity/SubmissionStatistics.vue`

**显示内容**：
- 总学生数
- 已提交数（绿色）
- 草稿中（黄色）
- 未开始（灰色）
- 平均分（蓝色）
- 平均用时（紫色）
- 提交进度条
- 实时连接状态

**特性**：
- ✅ WebSocket 实时更新
- ✅ 自动刷新统计数据

### 2. SubmissionList（学生提交详细列表）✨

**组件**: `frontend/src/components/Activity/Teacher/SubmissionList.vue`

**显示内容**：
- 📋 学生提交列表（表格形式）
  - 学生姓名和邮箱
  - 提交状态（草稿/已提交/已评分/已退回）
  - 分数（如果有）
  - 提交时间
  - 用时
  - 操作按钮（查看/评分）

**功能**：
- ✅ 按状态筛选（全部/草稿/已提交/已评分/已退回）
- ✅ 批量操作（批量评分/批量退回）
- ✅ 查看单个提交详情
- ✅ 评分功能（打开 GradingModal）

## 🔄 工作流程

### 教师操作流程

1. **开始上课**
   - 点击"创建课堂" → "开始上课"
   - 进入授课模式界面

2. **切换到活动模块**
   - 在导播台中点击活动模块（如"知识测试"）
   - 系统自动显示活动统计面板

3. **查看学生提交**
   - 查看实时统计（SubmissionStatistics）
   - 查看详细提交列表（SubmissionList）
   - 点击"查看"按钮查看单个学生答案
   - 点击"评分"按钮进行评分

4. **评分操作**
   - 在 SubmissionList 中点击"评分"
   - 打开 GradingModal 评分界面
   - 输入分数和反馈
   - 保存后自动刷新列表

## 🎨 界面截图位置

在授课模式下，界面布局如下：

```
┌─────────────────────────────────────────────────┐
│  上课中  剩余时间: 37:18  ⏸️ 暂停  ⏹️ 结束课程   │
├─────────────────────────────────────────────────┤
│  在线学生                                        │
│  在线: 1 / 1  已完成: 0  平均进度: 0%          │
│  ┌─────┐                                        │
│  │ 张  │ 张慧1  0%                              │
│  └─────┘                                        │
├─────────────────────────────────────────────────┤
│  📺 导播台                                       │
│  共 6 个模块                                     │
│  [1] 📄 人脸识别概念                             │
│  [2] 📹 AI识别技术导入                           │
│  [3] 📊 流程图                                   │
│  [4] 📝 知识测试  ← 点击这里                     │
│  [5] 💻 物体识别原理动画演示                     │
│  [6] 📹 视频                                     │
├─────────────────────────────────────────────────┤
│  📊 实时统计                                     │
│  ┌─────┬─────┬─────┬─────┬─────┬─────┐         │
│  │总学生│已提交│草稿中│未开始│平均分│平均用时│         │
│  │  1   │  0   │  0   │  1   │  -   │   -    │         │
│  └─────┴─────┴─────┴─────┴─────┴─────┘         │
│  [============                    ] 0%          │
├─────────────────────────────────────────────────┤
│  📝 学生提交列表                                 │
│  ┌──────────────────────────────────────────┐   │
│  │ [筛选] [刷新]                             │   │
│  ├──────────────────────────────────────────┤   │
│  │ ☑ 学生      │状态│分数│提交时间│操作    │   │
│  ├──────────────────────────────────────────┤   │
│  │ ☐ 张慧1     │草稿│ -  │  -     │查看    │   │
│  │    zhang... │    │    │        │        │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## 🔧 技术实现

### 关键计算属性

```typescript
// 当前选中的 Cell（从 lesson.content 中获取）
const currentCell = computed(() => {
  // 通过 selectedCellIndex 或 current_cell_id 查找
  return props.lesson.content[selectedCellIndex.value]
})

// 当前活动 Cell 的数据库记录（用于查询提交数据）
const currentActivityDbCell = computed(() => {
  if (currentCell.value?.type !== 'activity') return null
  // 通过 order 匹配数据库中的 Cell 记录
  return dbCells.value.find(dbCell => 
    dbCell.order === currentCell.value.order && 
    dbCell.cell_type === 'ACTIVITY'
  )
})
```

### 数据流

```
教师点击导播台活动模块
  ↓
更新 selectedCellIndex
  ↓
currentCell 计算属性更新
  ↓
currentActivityDbCell 计算属性更新
  ↓
显示 SubmissionStatistics + SubmissionList
  ↓
SubmissionList 调用 API: GET /activities/cells/{cell_id}/submissions
  ↓
显示学生提交列表
```

## ✅ 功能确认

### 已实现功能

- ✅ 在授课模式下显示活动统计
- ✅ 在授课模式下显示学生提交详细列表
- ✅ 实时统计更新（WebSocket）
- ✅ 提交列表筛选和刷新
- ✅ 查看单个提交详情
- ✅ 评分功能

### 使用说明

1. **进入授课模式**：在教案编辑页面点击"开始上课"
2. **切换到活动模块**：在导播台中点击活动模块
3. **查看提交**：自动显示统计和详细列表
4. **评分**：点击"评分"按钮，在弹窗中输入分数和反馈

## 📝 相关文件

- `frontend/src/components/Classroom/TeacherControlPanel.vue` - 授课模式主界面
- `frontend/src/components/Activity/SubmissionStatistics.vue` - 实时统计组件
- `frontend/src/components/Activity/Teacher/SubmissionList.vue` - 提交列表组件
- `frontend/src/components/Activity/Teacher/GradingModal.vue` - 评分弹窗组件
- `frontend/src/services/activity.ts` - 活动 API 服务

