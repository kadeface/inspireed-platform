# InspireEd 角色与权限系统设计

## 文档版本
- **版本**: v1.0
- **日期**: 2025-10-19
- **状态**: 设计阶段

---

## 一、系统角色定义

### 1.1 角色层级

```
管理员 (Admin)
    ↓ 管理账号和系统
区域/学校层级
    ↓
教研员 (Researcher)
    ↓ 管理课程体系和官方资源
教师 (Teacher)
    ↓ 创建教案和教学活动
学生 (Student)
    ↓ 学习和参与活动
```

### 1.2 角色职责

#### 管理员 (Admin)
**定位**: 纯系统管理员，不参与教学内容管理

**核心职责**:
- ✅ 用户账号管理（增删改查所有用户）
- ✅ 组织架构管理（区域、学校配置）
- ✅ 系统配置（权限、参数设置）
- ✅ 数据备份与恢复
- ✅ 系统监控与日志查看
- ❌ **不负责**：课程内容、教案编辑

#### 教研员 (Researcher)
**定位**: 课程体系设计者，官方资源管理者

**核心职责**:
- ✅ **课程体系管理**
  - 创建/编辑学科、年级、课程
  - 导入/编辑章节目录结构
  - 定义课程标准和教学大纲
- ✅ **官方资源管理**
  - 上传官方教学资源（课件、文档、视频）
  - 编辑和更新资源版本
  - 关联资源到章节
- ✅ **教研观摩**
  - 查看所有教师的教案（只读）
  - 统计分析教师使用情况
  - 推荐优秀教案
- ✅ **资源发布控制**
  - 决定哪些课程向教师开放
  - 管理资源的可见性

#### 教师 (Teacher)
**定位**: 教案创建者，教学活动设计者

**核心职责**:
- ✅ **班级管理**
  - 创建和管理自己的班级
  - 邀请学生加入班级
  - 设置班级学期和课程安排
- ✅ **教案创建**
  - 基于官方课程创建教案（Fork模式）
  - 从零开始创建教案
  - 复用自己的历史教案
- ✅ **教案编辑**
  - 编辑教案的所有Cell单元
  - 设计学生版教学活动
  - 管理教案状态（草稿/发布/归档）
- ✅ **教案共享与协作**
  - 将教案设为私有/班级内/学校内/全平台共享
  - 邀请其他教师协作编辑
  - 查看和复用其他教师共享的教案
- ✅ **教学管理**
  - 发布教案给指定班级
  - 查看学生学习进度
  - 批改作业和评分
- 📖 **学习参考**
  - 查看官方课程和资源
  - 参考其他教师的共享教案

#### 学生 (Student)
**定位**: 学习者，活动参与者

**核心职责**:
- ✅ **加入班级**
  - 通过邀请码加入班级
  - 查看自己的班级列表
- ✅ **学习活动**
  - 查看教师发布的教案（只读）
  - 执行代码单元
  - 参与互动活动（问答、仿真、竞赛）
- ✅ **作业提交**
  - 完成教师布置的作业
  - 查看批改结果和评分
- ✅ **学习记录**
  - 查看自己的学习进度
  - 保存学习笔记
  - 查看成绩和统计
- ✅ **反馈互动**
  - 对教案进行评价和反馈
  - 提问和讨论

---

## 二、组织架构设计

### 2.1 层级结构

```
平台 (Platform)
  ├── 区域 (Region)
  │   ├── 学校 (School)
  │   │   ├── 年级组 (Grade Group)
  │   │   │   └── 班级 (Class)
  │   │   │       ├── 教师 (Teachers)
  │   │   │       └── 学生 (Students)
```

### 2.2 数据模型

#### Region (区域)
```python
class Region(Base):
    id: int                    # 区域ID
    name: str                  # 区域名称（如：浙江省、杭州市）
    code: str                  # 区域代码
    level: str                 # 层级（province/city/district）
    parent_id: int | None      # 父级区域ID
    is_active: bool            # 是否启用
    created_at: datetime
    updated_at: datetime
```

#### School (学校)
```python
class School(Base):
    id: int                    # 学校ID
    name: str                  # 学校名称
    code: str                  # 学校代码
    region_id: int             # 所属区域
    type: str                  # 学校类型（小学/初中/高中）
    address: str               # 地址
    contact: str               # 联系方式
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

#### Class (班级)
```python
class Class(Base):
    id: int                    # 班级ID
    name: str                  # 班级名称（如：高一(3)班）
    code: str                  # 班级代码
    school_id: int             # 所属学校
    grade_id: int              # 年级（关联curriculum中的grade）
    academic_year: str         # 学年（如：2024-2025）
    semester: str              # 学期（spring/fall）
    creator_id: int            # 创建教师ID
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

#### ClassMember (班级成员)
```python
class ClassMember(Base):
    id: int
    class_id: int              # 班级ID
    user_id: int               # 用户ID（教师或学生）
    role: str                  # 角色（teacher/student/assistant）
    join_date: datetime        # 加入日期
    is_active: bool
```

#### 更新 User 模型
```python
class User(Base):
    # 原有字段...
    id: int
    email: str
    username: str
    role: UserRole             # admin/researcher/teacher/student
    
    # 新增组织关联字段
    school_id: int | None      # 所属学校（教师、学生）
    region_id: int | None      # 所属区域（教研员可能跨校）
    employee_id: str | None    # 工号/学号
    
    # 原有字段...
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

---

## 三、教案共享与协作机制

### 3.1 教案可见性级别

```python
class LessonVisibility(str, Enum):
    PRIVATE = "private"              # 私有（仅创建者）
    CLASS_SHARED = "class_shared"    # 班级内共享
    SCHOOL_SHARED = "school_shared"  # 学校内共享
    PUBLIC = "public"                # 全平台共享
```

### 3.2 教案协作权限

```python
class LessonCollaborator(Base):
    id: int
    lesson_id: int                   # 教案ID
    user_id: int                     # 协作者ID
    permission: str                  # 权限（view/edit/admin）
    invited_by: int                  # 邀请人ID
    invited_at: datetime
    is_active: bool
```

**权限说明**:
- `view`: 只读查看
- `edit`: 可编辑内容
- `admin`: 可管理协作者和删除教案

### 3.3 教案与官方课程的关系

```python
class Lesson(Base):
    # 原有字段...
    id: int
    title: str
    content: JSON
    
    # 新增关联字段
    course_id: int | None           # 基于的官方课程
    source_lesson_id: int | None    # 来源教案（fork/复制）
    visibility: LessonVisibility    # 可见性级别
    
    # 协作相关
    is_collaborative: bool          # 是否允许协作
    
    creator_id: int
    status: LessonStatus
    created_at: datetime
    updated_at: datetime
```

### 3.4 协作工作流

```
教师A创建教案
    ↓
设置为"学校内共享"
    ↓
教师B发现并申请协作
    ↓
教师A同意，授予"edit"权限
    ↓
教师A和教师B可以同时编辑
    ↓
每次保存记录操作者
```

---

## 四、权限矩阵

### 4.1 功能权限表

| 功能模块 | 管理员 | 教研员 | 教师 | 学生 |
|---------|-------|-------|-----|-----|
| **账号管理** |
| 创建用户 | ✅ | ❌ | ❌ | ❌ |
| 编辑用户 | ✅ | ❌ | 🔹自己 | 🔹自己 |
| 删除用户 | ✅ | ❌ | ❌ | ❌ |
| 导入账号 | ✅ | ❌ | ❌ | ❌ |
| **组织管理** |
| 创建区域 | ✅ | ❌ | ❌ | ❌ |
| 创建学校 | ✅ | ❌ | ❌ | ❌ |
| 创建班级 | ❌ | ❌ | ✅ | ❌ |
| 管理班级成员 | ✅全部 | 👁️查看 | ✅自己的 | ❌ |
| **课程体系** |
| 创建学科/年级 | ❌ | ✅ | ❌ | ❌ |
| 创建课程 | ❌ | ✅ | ❌ | ❌ |
| 导入章节 | ❌ | ✅ | ❌ | ❌ |
| 查看课程体系 | 👁️ | ✅ | 👁️ | 👁️ |
| **官方资源** |
| 上传资源 | ❌ | ✅ | ❌ | ❌ |
| 编辑资源 | ❌ | ✅ | ❌ | ❌ |
| 删除资源 | ❌ | ✅ | ❌ | ❌ |
| 查看资源 | 👁️ | ✅ | 👁️ | 👁️ |
| **教师教案** |
| 创建教案 | ❌ | ❌ | ✅ | ❌ |
| 编辑教案 | ❌ | ❌ | ✅自己的+协作的 | ❌ |
| 删除教案 | ❌ | ❌ | ✅自己的 | ❌ |
| 查看教案 | 👁️全部 | 👁️全部 | 👁️共享的 | 👁️已发布的 |
| 发布教案 | ❌ | ❌ | ✅自己的 | ❌ |
| 协作编辑 | ❌ | ❌ | ✅被授权的 | ❌ |
| **学生数据** |
| 查看学习记录 | 👁️全部 | 📊统计 | 👁️自己班级 | 🔹自己 |
| 批改作业 | ❌ | ❌ | ✅自己班级 | ❌ |
| 查看成绩 | 👁️全部 | 📊统计 | 👁️自己班级 | 🔹自己 |
| **系统管理** |
| 系统配置 | ✅ | ❌ | ❌ | ❌ |
| 数据备份 | ✅ | ❌ | ❌ | ❌ |
| 日志查看 | ✅ | ❌ | ❌ | ❌ |

**图例说明**:
- ✅ = 完全权限
- 👁️ = 只读查看
- 🔹 = 仅限自己的数据
- 📊 = 统计分析
- ❌ = 无权限

### 4.2 数据访问范围

| 角色 | 数据访问范围 |
|------|------------|
| **管理员** | 全平台所有数据 |
| **教研员** | 全平台课程体系 + 所属区域的使用统计 |
| **教师** | 所属学校的课程 + 自己创建/协作的教案 + 自己班级的学生数据 |
| **学生** | 所在班级的已发布教案 + 自己的学习数据 |

---

## 五、官方资源更新机制

### 5.1 更新策略

根据需求，采用**直接更新策略**：

```
教研员更新官方资源
    ↓
资源版本号+1（记录历史）
    ↓
所有引用该资源的教案自动使用新版本
    ↓
（可选）通知相关教师资源已更新
```

### 5.2 版本记录

虽然采用直接更新，但保留版本历史用于审计：

```python
class ResourceVersion(Base):
    id: int
    resource_id: int           # 资源ID
    version: int               # 版本号
    content: str               # 文件路径或内容
    updated_by: int            # 更新者
    updated_at: datetime
    change_note: str           # 更新说明
```

### 5.3 通知机制（可选）

```python
class ResourceUpdateNotification(Base):
    id: int
    resource_id: int
    old_version: int
    new_version: int
    message: str
    notified_users: JSON       # 被通知的教师列表
    created_at: datetime
```

---

## 六、实施路线图

### 阶段1：数据模型与后端基础 (Week 1-2)

**任务列表**:
1. ✅ 创建数据库迁移
   - Region 模型
   - School 模型
   - Class 模型
   - ClassMember 模型
   - LessonCollaborator 模型
   - ResourceVersion 模型

2. ✅ 更新现有模型
   - User 添加 school_id, region_id
   - Lesson 添加 visibility, is_collaborative, source_lesson_id
   - Resource 添加版本控制字段

3. ✅ API 开发
   - 组织管理 API (Region, School, Class)
   - 班级成员管理 API
   - 教案协作 API
   - 权限验证中间件

### 阶段2：教研员功能 (Week 3)

**任务列表**:
1. ✅ 课程管理从 Admin 迁移到 Researcher
   - 创建 `/researcher/curriculum` 页面
   - 复用现有的 CurriculumManagement 组件
   - 添加教研员权限检查

2. ✅ 官方资源管理
   - 资源版本控制界面
   - 资源使用统计

3. ✅ 教研观摩功能
   - 查看所有教师教案列表
   - 教案使用统计分析

### 阶段3：教师协作与班级管理 (Week 4-5)

**任务列表**:
1. ✅ 班级管理
   - 班级创建/编辑界面
   - 学生邀请与管理
   - 班级课程安排

2. ✅ 教案共享
   - 教案可见性设置
   - 协作者邀请与权限管理
   - 教案 Fork 功能

3. ✅ 协作编辑
   - 多人编辑权限控制
   - 编辑历史记录
   - 冲突提示（简单版本）

### 阶段4：学生端与管理员优化 (Week 6)

**任务列表**:
1. ✅ 学生端
   - 班级加入流程
   - 教案浏览（按班级筛选）
   - 学习记录查看

2. ✅ 管理员端重构
   - 移除课程管理功能
   - 专注账号和组织管理
   - 批量导入功能优化

3. ✅ 权限系统完善
   - 前端路由守卫
   - API 权限验证
   - 错误处理优化

### 阶段5：测试与文档 (Week 7)

**任务列表**:
1. ✅ 功能测试
   - 各角色功能测试
   - 权限边界测试
   - 协作流程测试

2. ✅ 性能优化
   - 数据库查询优化
   - 缓存策略

3. ✅ 文档完善
   - 用户使用手册
   - API 文档
   - 部署文档

---

## 七、关键设计决策

### 7.1 为什么选择 Fork 模式而非引用模式？

**原因**:
1. **教学独立性**: 教师需要自由修改教案，不受官方资源更新影响
2. **简化逻辑**: 避免复杂的版本同步和冲突处理
3. **性能考虑**: 查询时不需要递归查找引用链

**保留追溯**:
- Lesson 保留 `source_lesson_id` 字段
- 可以查看教案的来源和衍生关系

### 7.2 为什么需要 Region 和 School 层级？

**原因**:
1. **教育管理现实**: 教育系统本身就是区域-学校-班级的层级结构
2. **数据隔离**: 不同学校的数据需要隔离
3. **统计分析**: 区域、学校维度的数据分析需求
4. **权限控制**: 教研员可能负责整个区域的课程

### 7.3 为什么教师可以创建班级而非管理员？

**原因**:
1. **实际工作流**: 教师最清楚自己的班级需求
2. **灵活性**: 教师可以快速创建临时班级或兴趣小组
3. **减轻管理员负担**: 管理员只需管理学校架构，不需要关注每个班级

### 7.4 协作编辑如何处理冲突？

**简化方案**:
- **不实现实时协作**: 避免复杂的 CRDT/OT 算法
- **后保存覆盖**: 最后保存的版本生效
- **保存时提示**: 如果有其他人最近编辑过，给予提示
- **编辑历史**: 记录每次修改，可回滚

**未来增强**:
- 可以引入编辑锁机制
- 或者实现 Cell 级别的细粒度锁

---

## 八、风险与挑战

### 8.1 数据迁移风险

**问题**: 现有系统可能已有数据，迁移时需要处理

**解决方案**:
1. 创建默认学校（"默认学校"）
2. 现有用户关联到默认学校
3. 现有教案保持私有状态
4. 提供数据导入工具

### 8.2 权限系统复杂度

**问题**: 多层级组织 + 多角色权限容易出错

**解决方案**:
1. 使用权限装饰器统一管理
2. 编写详细的权限测试用例
3. 前端和后端双重权限验证
4. 日志记录所有权限相关操作

### 8.3 协作编辑冲突

**问题**: 多人同时编辑可能导致数据丢失

**解决方案**:
1. 保存时检查 `updated_at` 时间戳
2. 如果有冲突，提示用户并显示差异
3. 保留编辑历史，支持回滚
4. （未来）实现编辑锁或实时同步

### 8.4 性能问题

**问题**: 组织层级查询、权限检查可能影响性能

**解决方案**:
1. 数据库索引优化
2. Redis 缓存用户权限信息
3. 使用 SQL JOIN 而非 N+1 查询
4. 分页加载大数据集

---

## 九、未来扩展方向

### 9.1 协作增强
- [ ] 实时协作编辑（WebSocket + CRDT）
- [ ] 评论和讨论功能
- [ ] 教案模板市场

### 9.2 数据分析
- [ ] 教研员数据看板（课程使用率、教师活跃度）
- [ ] 教师数据看板（学生学习分析、教案效果）
- [ ] 学生学习路径分析

### 9.3 移动端
- [ ] 教师移动端（班级管理、作业批改）
- [ ] 学生移动端（学习、作业提交）

### 9.4 集成功能
- [ ] 与学校教务系统对接
- [ ] 与第三方内容平台对接
- [ ] 导出到常见格式（PDF, Word, PPT）

---

## 十、参考资料

### 相关文档
- `docs/architecture.md` - 系统架构文档
- `docs/TEACHER_WORKFLOW.md` - 教师工作流程
- `backend/app/models/user.py` - 用户模型

### 技术参考
- SQLAlchemy 关系模型: https://docs.sqlalchemy.org/en/14/orm/relationships.html
- FastAPI 权限管理: https://fastapi.tiangolo.com/tutorial/dependencies/
- Vue Router 权限控制: https://router.vuejs.org/guide/advanced/navigation-guards.html

---

**文档维护者**: InspireEd 开发团队  
**最后更新**: 2025-10-19  
**审核状态**: 待审核

