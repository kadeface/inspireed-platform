# 课堂模式系统设计

## 🎯 问题分析

当前系统缺少的关键功能：
1. **课堂会话概念**：每次上课应该是独立的会话，有开始和结束时间
2. **教师控制状态**：教师电脑应该处于"上课模式"，可以控制课堂进度
3. **内容同步**：教师切换Cell/活动时，学生端应该同步更新
4. **在线状态管理**：教师应该能看到哪些学生在线参与课堂
5. **数据关联**：课堂中的所有活动数据应该关联到同一个会话

## 🏗️ 架构设计

### 1. 数据模型

#### A. 课堂会话（ClassSession）
```python
class ClassSession(Base):
    """课堂会话"""
    __tablename__ = "class_sessions"
    
    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 会话状态
    status = Column(Enum(ClassSessionStatus), default=ClassSessionStatus.PENDING)
    # PENDING: 准备中（教师已创建但未开始）
    # ACTIVE: 进行中
    # PAUSED: 已暂停
    # ENDED: 已结束
    
    # 时间信息
    scheduled_start = Column(DateTime, nullable=True)  # 计划开始时间
    actual_start = Column(DateTime, nullable=True)     # 实际开始时间
    ended_at = Column(DateTime, nullable=True)         # 结束时间
    duration_minutes = Column(Integer, nullable=True)  # 实际时长（分钟）
    
    # 当前状态
    current_cell_id = Column(Integer, ForeignKey("cells.id"), nullable=True)  # 当前显示的Cell
    current_activity_id = Column(Integer, nullable=True)  # 当前活动的Cell ID
    
    # 会话设置
    settings = Column(JSON, default=dict)  # 会话配置
    # {
    #   "allow_advance": true,      # 允许学生提前查看
    #   "sync_mode": "strict",      # 同步模式：strict/free
    #   "show_leaderboard": false,  # 显示排行榜
    #   "auto_save": true           # 自动保存学生答案
    # }
    
    # 统计数据
    total_students = Column(Integer, default=0)  # 参与学生数
    active_students = Column(Integer, default=0)  # 在线学生数
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### B. 学生会话参与（StudentSessionParticipation）
```python
class StudentSessionParticipation(Base):
    """学生会话参与记录"""
    __tablename__ = "student_session_participations"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("class_sessions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 参与状态
    joined_at = Column(DateTime, default=datetime.utcnow)  # 加入时间
    last_active_at = Column(DateTime, default=datetime.utcnow)  # 最后活跃时间
    left_at = Column(DateTime, nullable=True)  # 离开时间
    is_active = Column(Boolean, default=True)  # 是否在线
    
    # 进度信息
    current_cell_id = Column(Integer, nullable=True)  # 当前所在Cell
    completed_cells = Column(JSON, default=list)  # 已完成的Cell ID列表
    progress_percentage = Column(Float, default=0.0)  # 完成百分比
    
    # 活动数据关联
    activity_submissions = relationship("ActivitySubmission", 
                                       foreign_keys="ActivitySubmission.session_id",
                                       back_populates="session_participation")
```

#### C. 更新ActivitySubmission模型
```python
# 在 ActivitySubmission 中添加
session_id = Column(Integer, ForeignKey("class_sessions.id"), nullable=True)  # 关联课堂会话
# 如果为NULL，表示非课堂时间的提交（如课后作业）
```

### 2. 状态流转

```
教师创建会话 → PENDING（准备中）
    ↓
教师点击"开始上课" → ACTIVE（进行中）
    ↓
教师点击"暂停" → PAUSED（已暂停）
    ↓
教师点击"继续" → ACTIVE（进行中）
    ↓
教师点击"结束课程" → ENDED（已结束）
```

## 🔄 核心功能设计

### 1. 教师端功能

#### A. 课堂控制面板（TeacherClassroomControl）

```vue
<template>
  <div class="classroom-control-panel">
    <!-- 会话状态指示器 -->
    <div class="session-status">
      <div v-if="session.status === 'active'" class="status-indicator active">
        <span class="pulse-dot"></span>
        <span>上课中</span>
        <span class="duration">{{ formatDuration(session.duration) }}</span>
      </div>
      <div v-else-if="session.status === 'paused'" class="status-indicator paused">
        <span>已暂停</span>
      </div>
      <div v-else class="status-indicator pending">
        <span>准备中</span>
      </div>
    </div>
    
    <!-- 在线学生列表 -->
    <div class="students-panel">
      <h4>在线学生 ({{ activeStudents.length }}/{{ totalStudents }})</h4>
      <div class="students-grid">
        <div 
          v-for="student in activeStudents" 
          :key="student.id"
          class="student-card"
          :class="{ 'at-current-cell': student.current_cell_id === currentCellId }"
        >
          <div class="student-avatar">{{ student.name[0] }}</div>
          <div class="student-info">
            <div class="student-name">{{ student.name }}</div>
            <div class="student-progress">{{ student.progress_percentage }}%</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 课堂控制按钮 -->
    <div class="control-buttons">
      <button 
        v-if="!session || session.status === 'pending'"
        @click="startSession"
        class="btn-primary"
      >
        ▶️ 开始上课
      </button>
      
      <button 
        v-if="session?.status === 'active'"
        @click="pauseSession"
        class="btn-secondary"
      >
        ⏸️ 暂停
      </button>
      
      <button 
        v-if="session?.status === 'paused'"
        @click="resumeSession"
        class="btn-primary"
      >
        ▶️ 继续
      </button>
      
      <button 
        v-if="session && session.status !== 'ended'"
        @click="endSession"
        class="btn-danger"
      >
        ⏹️ 结束课程
      </button>
    </div>
    
    <!-- 内容控制 -->
    <div class="content-control">
      <h4>控制内容</h4>
      <div class="cell-navigator">
        <button @click="previousCell" :disabled="!canGoPrevious">← 上一个</button>
        <select v-model="selectedCellId" @change="navigateToCell">
          <option v-for="(cell, index) in lesson.content" :key="cell.id" :value="cell.id">
            {{ index + 1 }}. {{ cell.title || cell.type }}
          </option>
        </select>
        <button @click="nextCell" :disabled="!canGoNext">下一个 →</button>
      </div>
      
      <!-- 开始活动 -->
      <button 
        v-if="currentCell?.type === 'activity'"
        @click="startActivity"
        class="btn-primary"
      >
        🎯 开始活动
      </button>
      
      <!-- 结束活动 -->
      <button 
        v-if="activeActivityId"
        @click="endActivity"
        class="btn-secondary"
      >
        ✅ 结束活动
      </button>
    </div>
    
    <!-- 实时统计 -->
    <RealtimeStatistics 
      v-if="activeActivityId"
      :session-id="session.id"
      :cell-id="activeActivityId"
    />
  </div>
</template>
```

#### B. 学生端同步显示

```vue
<!-- StudentLessonView.vue -->
<template>
  <div class="student-lesson-view">
    <!-- 课堂模式提示 -->
    <div v-if="isInClassroomMode" class="classroom-banner">
      <div class="banner-content">
        <span class="live-indicator"></span>
        <span>正在上课：{{ session.lesson.title }}</span>
        <span class="teacher-name">授课教师：{{ session.teacher_name }}</span>
      </div>
      
      <!-- 同步状态 -->
      <div v-if="isSyncing" class="sync-status">
        <span>教师正在切换内容...</span>
      </div>
    </div>
    
    <!-- 当前Cell显示 -->
    <div v-if="currentCellId">
      <component 
        :is="getCellComponent(currentCell.type)"
        :cell="currentCell"
        :session-id="session.id"
        :sync-mode="session.settings.sync_mode"
      />
    </div>
    
    <!-- 等待提示 -->
    <div v-else class="waiting-message">
      <p>等待教师开始课程...</p>
    </div>
  </div>
</template>
```

### 3. WebSocket 实时通信

#### A. 事件定义
```typescript
interface ClassroomEvent {
  type: 'session_started' | 'session_ended' | 'cell_changed' | 
        'activity_started' | 'activity_ended' | 'student_joined' | 
        'student_left' | 'student_progress' | 'statistics_updated'
  
  session_id: number
  data: any
}

// 示例事件
{
  type: 'cell_changed',
  session_id: 123,
  data: {
    cell_id: 456,
    cell_title: '植物的生长过程',
    timestamp: '2024-01-01T10:00:00Z'
  }
}
```

#### B. 教师端WebSocket
```python
@router.websocket("/ws/classroom/{session_id}/teacher")
async def teacher_classroom_ws(
    websocket: WebSocket,
    session_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """教师端课堂WebSocket"""
    await websocket.accept()
    
    # 验证权限
    session = await db.get(ClassSession, session_id)
    if not session or session.teacher_id != current_user.id:
        await websocket.close(code=1008, reason="无权访问")
        return
    
    # 注册教师连接
    classroom_manager.register_teacher(session_id, websocket)
    
    try:
        # 发送当前状态
        await websocket.send_json({
            "type": "initial_state",
            "session": session.to_dict(),
            "students": await get_active_students(session_id),
            "current_cell": session.current_cell_id
        })
        
        # 接收教师操作
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "navigate_to_cell":
                # 切换Cell
                await navigate_to_cell(session_id, data["cell_id"])
                # 广播给学生端
                await classroom_manager.broadcast_to_students(session_id, {
                    "type": "cell_changed",
                    "cell_id": data["cell_id"]
                })
            
            elif data["type"] == "start_activity":
                await start_activity(session_id, data["cell_id"])
                await classroom_manager.broadcast_to_students(session_id, {
                    "type": "activity_started",
                    "cell_id": data["cell_id"]
                })
            
            # ... 其他操作
            
    except WebSocketDisconnect:
        classroom_manager.unregister_teacher(session_id)
```

#### C. 学生端WebSocket
```python
@router.websocket("/ws/classroom/{session_id}/student")
async def student_classroom_ws(
    websocket: WebSocket,
    session_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """学生端课堂WebSocket"""
    await websocket.accept()
    
    # 验证权限和加入会话
    participation = await join_session(session_id, current_user.id)
    classroom_manager.register_student(session_id, current_user.id, websocket)
    
    try:
        # 发送当前状态
        await websocket.send_json({
            "type": "initial_state",
            "session": session.to_dict(),
            "current_cell": session.current_cell_id,
            "participation": participation.to_dict()
        })
        
        # 发送心跳（保持在线状态）
        async def send_heartbeat():
            while True:
                await asyncio.sleep(30)
                await update_last_active(session_id, current_user.id)
        
        heartbeat_task = asyncio.create_task(send_heartbeat())
        
        # 接收学生进度更新
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "progress_update":
                await update_progress(
                    session_id, 
                    current_user.id, 
                    data["current_cell_id"],
                    data["completed_cells"]
                )
                # 通知教师端
                await classroom_manager.notify_teacher(session_id, {
                    "type": "student_progress",
                    "student_id": current_user.id,
                    "progress": data
                })
            
    except WebSocketDisconnect:
        await leave_session(session_id, current_user.id)
        classroom_manager.unregister_student(session_id, current_user.id)
        heartbeat_task.cancel()
```

### 4. API 接口设计

#### A. 创建会话
```python
@router.post("/lessons/{lesson_id}/sessions", response_model=ClassSessionResponse)
async def create_class_session(
    lesson_id: int,
    classroom_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建课堂会话"""
    # 验证权限
    # 创建会话
    # 返回会话信息
```

#### B. 开始会话
```python
@router.post("/sessions/{session_id}/start", response_model=ClassSessionResponse)
async def start_class_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """开始课堂会话"""
    session.status = ClassSessionStatus.ACTIVE
    session.actual_start = datetime.utcnow()
    # 广播给学生
```

#### C. 切换Cell
```python
@router.post("/sessions/{session_id}/navigate", response_model=dict)
async def navigate_to_cell(
    session_id: int,
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """切换当前Cell"""
    session.current_cell_id = cell_id
    # 通过WebSocket广播
```

#### D. 开始活动
```python
@router.post("/sessions/{session_id}/start-activity", response_model=dict)
async def start_activity_in_session(
    session_id: int,
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """在会话中开始活动"""
    session.current_activity_id = cell_id
    # 通知所有学生开始答题
```

## 📊 数据关联关系

```
Lesson (教案)
  └── ClassSession (课堂会话) - 一次上课
       ├── Teacher (教师)
       ├── Classroom (班级)
       ├── StudentSessionParticipation (学生参与)
       │    └── ActivitySubmission (活动提交) - 关联session_id
       └── CurrentCell (当前Cell)
            └── ActivitySubmission (活动提交) - 在课堂中提交的
```

## 🎨 UI/UX 设计要点

### 教师端
1. **状态清晰**：大号状态指示器，一眼看出是否在上课
2. **学生可视**：实时看到在线学生和他们的进度
3. **操作简单**：一键开始/暂停/结束，快速切换内容
4. **实时反馈**：看到学生答题进度、统计数据

### 学生端
1. **同步显示**：跟随教师切换内容
2. **状态提示**：知道是否在课堂模式
3. **进度可视**：看到自己的学习进度
4. **互动反馈**：答题后立即看到统计

## 🚀 实施步骤

### 阶段1：基础会话模型（1周）
1. 创建 ClassSession 和 StudentSessionParticipation 模型
2. 实现会话的CRUD API
3. 更新 ActivitySubmission 关联session_id

### 阶段2：教师控制面板（1-2周）
1. 创建课堂控制组件
2. 实现开始/暂停/结束功能
3. 实现内容导航功能

### 阶段3：WebSocket实时同步（2周）
1. 实现WebSocket服务器
2. 实现教师端广播
3. 实现学生端接收同步

### 阶段4：在线状态管理（1周）
1. 实现学生在线状态追踪
2. 实现心跳机制
3. 显示在线学生列表

### 阶段5：数据关联和统计（1周）
1. 更新活动提交关联session_id
2. 实现会话级别的统计
3. 生成课堂报告

## 💡 使用场景示例

### 场景1：常规上课
```
1. 教师登录 → 选择教案 → 点击"开始上课"
2. 系统创建会话 → 状态变为"ACTIVE"
3. 学生端显示"正在上课" → 同步显示第一个Cell
4. 教师讲解 → 切换到下一个Cell → 学生端自动更新
5. 教师开始活动 → 学生开始答题 → 实时统计数据
6. 活动结束 → 教师查看统计 → 继续讲解
7. 课程结束 → 教师点击"结束课程" → 生成课堂报告
```

### 场景2：课后复习
```
1. 学生登录 → 查看已发布的教案（非课堂模式）
2. 自主浏览内容 → 提交作业
3. ActivitySubmission 的 session_id 为 NULL
4. 教师可以查看所有提交（课堂+课后）
```

## 🔍 关键问题解答

### Q1: 教师电脑和学生电脑如何关联？
**A**: 通过 `ClassSession` 关联：
- 教师端创建会话，控制 `current_cell_id` 和 `current_activity_id`
- 学生端通过WebSocket接收更新，同步显示相同内容

### Q2: 数据如何区分课堂和课后？
**A**: 通过 `session_id` 字段：
- 课堂中的提交：`session_id` 有值，关联到 `ClassSession`
- 课后的提交：`session_id` 为 NULL

### Q3: 如果学生晚到怎么办？
**A**: 
- 学生加入会话时，自动定位到当前 `current_cell_id`
- 可以查看之前的Cell（根据配置）
- 教师可以看到学生的加入时间和当前位置

### Q4: 教师如何看到学生状态？
**A**: 
- 实时在线列表（WebSocket心跳）
- 每个学生的当前位置和进度
- 可视化显示哪些学生在当前Cell

## 📝 总结

这个设计解决了：
1. ✅ **课堂会话管理**：每次上课是独立的会话
2. ✅ **教师控制**：教师可以控制课堂进度和内容
3. ✅ **内容同步**：教师和学生看到相同内容
4. ✅ **数据关联**：课堂中的所有数据都关联到会话
5. ✅ **实时互动**：WebSocket实现实时通信
6. ✅ **状态管理**：清晰的在线状态和进度追踪

