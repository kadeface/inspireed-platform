# 演示实验班（Demo Class）设计

## 文档信息

| 项 | 内容 |
|---|---|
| 状态 | 已评审（对话确认） |
| 版本 | 1.0 |
| 日期 | 2026-07-15 |

---

## 1. 背景与目标

当前学生账号通常挂在真实学校/班级下；讲座、演示等轻量场景需要一批独立、易记、可反复使用的学生账号，且任意教师都能选到该班授课，而不依赖真实学校数据。

**成功标准：**

- 存在唯一虚拟校 `DEMO School` 与班级 `Demo Class`。
- 固定 60 个学生账号 `st01`–`st60`，密码统一 `123456`，可登录并使用学生端功能。
- 任意教师在「我的班级 / 授课选班」中能看到并选择 `Demo Class`，无需预先加入该班成员。
- 平台管理员可在后台一键创建/补齐与一键重置密码。

---

## 2. 范围

### 2.1 包含

- 演示学校、班级、60 名学生用户及班级成员关系的幂等开通。
- 教师侧班级列表（及授课选班相关入口）对 `Demo Class` 的全局注入。
- 若教师学校下拉按所属校过滤，则额外露出 `DEMO School`。
- 管理后台「实验班」运维页与对应 Admin API。

### 2.2 不包含

- 新的用户角色（不新增 `demo_student`）。
- 为每位教师自动持久化写入 `ClassroomMembership`。
- 演示数据自动进入真实学校的统计/报表默认范围。
- 一键清空课堂历史、作业等业务数据（重置仅针对密码与成员关系补齐）。
- Guest 免登录旁路（沿用现有 guest 机制，本设计不改造）。

---

## 3. 组织与账号

### 3.1 组织

| 实体 | 约定 |
|---|---|
| 学校名称 | `DEMO School` |
| 学校编码 | `DEMO`（唯一，幂等查找主键） |
| 班级名称 | `Demo Class` |
| 年级 | 系统 Grade 目录中的「高一」（若不存在则 provision 失败并提示先配置） |

识别方式：优先用 `School.code == "DEMO"` 定位演示校及其下唯一 `Demo Class`。若实现时增加 `is_demo` 字段，须与 `code=DEMO` 保持一致，避免误标真实校。

### 3.2 学生账号（60）

| 项 | 值 |
|---|---|
| 用户名 | `st01` … `st60` |
| 密码 | 统一 `123456`（满足现有 ≥6 位校验） |
| 角色 | `student` |
| 显示名 | `ST01` … `ST60` |
| User 绑定 | `school_id` / `grade_id` / `classroom_id` 指向演示组织 |
| 成员关系 | `ClassroomMembership`，`role_in_class=student`，`is_primary_class=true` |

邮箱：可用内部占位（如 `st01@demo.inspireed.internal`），须保证全局唯一，且不与真实用户冲突。

### 3.3 运维语义

**创建 / 补齐（provision，幂等）**

1. 确保 `DEMO School`、`Demo Class` 存在。
2. 确保 `st01`–`st60` 用户存在；缺失则创建。
3. 确保每人 User 作用域字段与 Demo Class 的 `ClassroomMembership` 齐全。
4. 已存在且归属正确则跳过；返回创建 / 跳过 / 失败明细。

**重置密码（reset-passwords）**

- 仅作用于：用户名匹配 `st0[1-9]|st[1-5][0-9]|st60`，且属于 Demo Class 的用户。
- 密码全部改回 `123456`。
- 不删除课堂会话、课时关联等历史数据。

**冲突处理**

- 若 `st0N` 已被非演示用户占用（不属于 Demo Class / DEMO 校），provision **失败并列出冲突用户名**，不覆盖、不改密该用户。

---

## 4. 教师选班：全局注入

### 4.1 行为

教师获取「我的班级」或授课选班列表时：

1. 返回其原有班级（现有 `ClassroomMembership` 等逻辑不变）。
2. 若列表中尚无 `Demo Class`，则 **追加** 该班。
3. 学校选择若按教师所属校过滤，则额外包含 `DEMO School`。

教师无需成为 Demo Class 的持久成员即可开课、关联课时；业务流程与普通班相同。

### 4.2 学生侧

`st01`–`st60` 已有学生成员关系，可看到教师在 Demo Class 下创建的课堂/课时（与现有班级范围逻辑一致）。

### 4.3 明确不做

- 不为全体教师批量写入永久 `ClassroomMembership`（新教师注册需同步，易漏且污染成员表）。
- 数据中心、真实校报表默认范围不因列表注入而纳入演示班；如需排除，按 `School.code == "DEMO"` 过滤。

### 4.4 改动落点（实现指引）

- 后端：教师班级列表入口（至少包括 `get_my_classrooms` 及授课/开课拉班级的同类 API）统一走「原列表 + 注入 Demo Class」。
- 前端：优先依赖后端注入；若另有按 `school_id` 过滤的学校下拉，需能拿到 `DEMO School`。

---

## 5. 管理后台

### 5.1 页面

管理端「实验班 / Demo Class」运维页（可挂在组织或用户管理下），仅平台最高管理角色（`admin`）可见；学校管理员不可见。

**展示：**

- DEMO 校 / Demo Class 是否就绪
- 已就绪账号数 / 目标 60
- 账号规则摘要：`st01`–`st60`，密码 `123456`

**操作：**

1. 一键创建 / 补齐
2. 一键重置密码
3. 复制账号清单（纯文本，便于讲座材料）

### 5.2 API

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/admin/demo-class/status` | 组织与账号就绪状态 |
| POST | `/admin/demo-class/provision` | 幂等创建/补齐 |
| POST | `/admin/demo-class/reset-passwords` | 重置演示账号密码 |

权限：与现有 admin 用户管理同级校验。

---

## 6. 架构与组件

```
Admin UI (Demo Class 页)
    → Admin API (status / provision / reset-passwords)
        → DemoClassService
            → School / Classroom / Grade
            → User + ClassroomMembership

Teacher class list APIs
    → existing membership query
    → + DemoClassService.resolve_demo_classroom() inject
```

- **DemoClassService**：唯一封装「找 DEMO 校/班、provision、reset、resolve」逻辑，避免多处硬编码 `DEMO`。
- 不引入平行账号体系；复用现有 `User`、`Classroom`、`ClassroomMembership`。

---

## 7. 错误处理

| 情况 | 行为 |
|---|---|
| Grade「高一」不存在 | provision 失败，明确提示先配置年级目录 |
| 用户名被非演示用户占用 | 失败并返回冲突列表，不修改冲突用户 |
| 部分账号创建失败 | 返回已创建/跳过/失败明细；允许再次 provision 补齐 |
| Demo Class 尚未 provision | 教师列表注入：无班可注入则不加项（或不阻断原列表）；管理端 status 显示未就绪 |

---

## 8. 测试要点

1. **幂等：** provision 连续执行两次，仍为 1 校、1 班、60 学生用户与成员关系。
2. **登录：** `st01` / `123456` 可登录，角色为 student。
3. **教师注入：** 与 Demo Class 无成员关系的教师，班级列表仍含 Demo Class。
4. **授课冒烟：** 教师选 Demo Class 开课/会话后，演示学生能按现有逻辑看到。
5. **重置：** 改密后执行 reset-passwords，可用 `123456` 再登录。
6. **冲突：** 预置同名非演示用户时，provision 失败且不破坏该用户。
7. **权限：** 非 admin 无法调用 demo-class 管理 API。

---

## 9. 决策记录

| 决策 | 选择 | 说明 |
|---|---|---|
| 组织模型 | 虚拟 DEMO 校 + Demo Class | 跨真实校使用，不绑真实组织 |
| 教师可见性 | 列表全局注入 | 全体教师可选，不写永久教师成员 |
| 账号形态 | 普通 student | 避免新角色带来的权限面 |
| 密码 | 统一 `123456` | 满足现有校验；讲座易记 |
| 运维 | 管理后台一键 | 非仅脚本 |
| 历史数据 | 重置不删课 | 轻量场景够用 |

---

## 10. 实现备注

- 密码创建走现有哈希与 `min_length=6` 校验；本设计不放宽全局密码策略。
- `Classroom.capacity` 仅为元数据，60 人无需改容量逻辑。
- 开通时须同时写 User 作用域字段与 `ClassroomMembership`（与现有「仅改 User.classroom_id」的路径区分，避免课时列表为空）。
