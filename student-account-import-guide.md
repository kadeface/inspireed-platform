# 学生账户批量导入使用指南

## 概述

已成功创建**学生账户批量导入功能**，用于快速创建学生用户账户。此功能使用与班级导入相同的友好格式（使用名称而不是ID），大幅提升用户体验。

---

## ✅ 已实现功能

### 后端实现

#### 1. 新增导入策略
**文件**: `/backend/app/services/import_strategies/student_account_import_strategy.py`

**特性**:
- ✅ 双模式支持（区县管理员/学校管理员）
- ✅ 使用名称而非ID（学校名称、年级级别、班级编号）
- ✅ 自动生成用户名和邮箱
- ✅ 自动关联班级和年级
- ✅ 支持更新已存在的学生
- ✅ 默认密码：`123456`

#### 2. 注册到统一导入系统
**文件**:
- `backend/app/services/import_strategies/__init__.py`
- `backend/app/services/import_orchestrator.py`
- `backend/app/schemas/import_schemas.py`
- `backend/app/api/v1/unified_import.py`

**新增导入类型**: `student_account`

---

## 📋 导入字段说明

### 区县管理员模式

| 列名 | 必填 | 说明 | 示例 |
|------|------|------|------|
| **学校名称** | ✅ | 学校全称 | 第一中学 |
| 学校代码 | ❌ | 学校编码（可选） | 101 |
| **年级级别** | ✅ | 年级数字（1-12） | 7 |
| **班级编号** | ✅ | 班级代码（如701=7年级1班） | 701 |
| **学籍号*** | ✅ | 学生唯一标识号 | 2024070001 |
| **姓名*** | ✅ | 学生真实姓名 | 张三 |
| 用户名 | ❌ | 登录用户名（默认=学籍号） | 2024070001 |
| 邮箱 | ❌ | 电子邮箱（自动生成） | 2024070001@inspireed.com |
| 手机号 | ❌ | 联系电话 | 13800138000 |
| 性别 | ❌ | 性别 | 男/女 |

### 学校管理员模式

与区县管理员模式相同，但**不需要学校名称列**（自动使用当前学校）。

---

## 📊 Excel模板示例

### 区县管理员模板

```
学校名称*    学校代码    年级级别*    班级编号*    学籍号*        姓名*    用户名        邮箱                      手机号        性别
第一中学      101        7           701         2024070001     张三      2024070001    2024070001@inspireed.com  13800138000   男
第一中学      101        7           701         2024070002     李四      2024070002    2024070002@inspireed.com  13800138001   女
第一中学      101        7           702         2024070003     王五      2024070003    2024070003@inspireed.com  13800138002   男
第二中学      102        7           701         2024070004     赵六      2024070004    2024070004@inspireed.com  13800138003   男
```

### 学校管理员模板

```
年级级别*    班级编号*    学籍号*        姓名*    用户名        邮箱                      手机号        性别
7           701         2024070001     张三      2024070001    2024070001@inspireed.com  13800138000   男
7           701         2024070002     李四      2024070002    2024070002@inspireed.com  13800138001   女
7           702         2024070003     王五      2024070003    2024070003@inspireed.com  13800138002   男
```

---

## 🔧 API使用

### 端点
```
POST /api/v1/import?strategy_type=student_account
```

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `strategy_type` | query | ✅ | 固定值：`student_account` |
| `file` | form-data | ✅ | Excel文件（.xlsx或.xls） |
| `update_existing` | query | ❌ | 更新已存在的学生（默认：false） |
| `school_id` | query | ❌ | 学校ID（学校管理员模式） |
| `region_id` | query | ❌ | 区县ID（可选） |
| `is_school_admin` | query | ❌ | 是否为学校管理员模式（默认：false） |

### 请求示例（curl）

```bash
# 区县管理员导入
curl -X POST "https://localhost:8000/api/v1/import?strategy_type=student_account&update_existing=false" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@students.xlsx"

# 学校管理员导入
curl -X POST "https://localhost:8000/api/v1/import?strategy_type=student_account&update_existing=false&is_school_admin=true&school_id=101" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@students.xlsx"
```

### 响应示例

**成功响应** (200 OK):
```json
{
  "total": 100,
  "success": 95,
  "failed": 5,
  "created": 90,
  "updated": 5,
  "skipped": 0,
  "errors": [
    {
      "row": 3,
      "field": "classroom_code",
      "message": "班级编号 '799' 在年级 7 中不存在"
    },
    {
      "row": 15,
      "field": "student_id_number",
      "message": "学籍号 '2024070001' 已存在"
    }
  ]
}
```

---

## 📝 完整工作流程

### 步骤1：准备Excel文件

创建Excel文件，按照以下格式填写数据：

**重要提示**：
- 列名必须使用中文名称（支持别名）
- 带`*`的列为必填项
- 年级级别使用数字（1-12）
- 班级编号格式：年级+班级序号（如701=7年级1班）

### 步骤2：确保组织架构存在

在导入学生之前，确保已创建：
1. ✅ 学校（使用"学校导入"功能）
2. ✅ 年级（使用"年级管理"功能）
3. ✅ 班级（使用"班级导入"功能）

### 步骤3：执行导入

#### 方法A：使用API（推荐）

```bash
# 登录获取token
TOKEN=$(curl -X POST "https://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@inspireed.com","password":"admin123"}' \
  | jq -r '.access_token')

# 导入学生
curl -X POST "https://localhost:8000/api/v1/import?strategy_type=student_account" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@students.xlsx"
```

#### 方法B：使用Swagger UI

1. 访问：`https://localhost:8000/docs`
2. 找到 `/api/v1/import` 端点
3. 点击"Try it out"
4. 设置 `strategy_type` 为 `student_account`
5. 上传Excel文件
6. 点击"Execute"

### 步骤4：验证导入结果

导入成功后：
1. 检查响应中的统计数据
2. 查看错误列表（如果有）
3. 登录系统验证学生账户

**学生默认登录信息**：
- 用户名：学籍号（或Excel中指定的用户名）
- 密码：`123456`

---

## 🎯 使用场景

### 场景1：新学期批量创建学生账户

```
开始
 ↓
1. 导入学校（如果不存在）
 ↓
2. 导入/创建年级
 ↓
3. 导入班级
 ↓
4. ✨ 导入学生账户（新功能）
 ↓
5. 创建考试
 ↓
6. 安排考场（学生已存在，可正常分配）
```

### 场景2：区县统考准备

```
开始
 ↓
1. 区县管理员创建统考
 ↓
2. 各学校导入学生账户
 ↓
3. 考场自动分配
 ↓
4. 生成座位表、准考证
```

---

## ⚠️ 注意事项

### 1. 班级编号格式

班级编号必须与系统中已创建的班级匹配：

| 班级编号 | 含义 | 年级级别 |
|---------|------|---------|
| 101 | 1年级1班 | 1 |
| 701 | 7年级1班 | 7 |
| 1001 | 10年级1班 | 10 |
| 1203 | 12年级3班 | 12 |

### 2. 学籍号唯一性

- 学籍号是学生的唯一标识
- 如果学籍号已存在，默认会跳过（除非设置`update_existing=true`）

### 3. 自动生成字段

- **用户名**：默认使用学籍号
- **邮箱**：格式为 `{username}@inspireed.com`
- **密码**：默认为 `123456`（首次登录后应修改）

### 4. 双模式选择

- **区县管理员**：必须提供"学校名称"
- **学校管理员**：自动使用当前学校，无需提供学校名称

---

## 🔍 错误排查

### 常见错误及解决方法

| 错误信息 | 原因 | 解决方法 |
|---------|------|---------|
| 学校 'XXX' 未找到 | 学校名称不存在 | 先使用"学校导入"创建学校 |
| 年级级别 X 不存在 | 年级未创建 | 在系统中先创建对应年级 |
| 班级编号 'XXX' 在年级 X 中不存在 | 班级未创建 | 先使用"班级导入"创建班级 |
| 学籍号 'XXX' 已存在 | 学生账户已存在 | 设置`update_existing=true`更新，或使用不同学籍号 |
| 用户名 'XXX' 已存在 | 用户名冲突 | 在Excel中指定不同的用户名 |

---

## 📚 相关API端点

### 查看导入策略列表
```
GET /api/v1/import/strategies
```

返回所有可用的导入类型及其说明。

### 学校导入
```
POST /api/v1/import?strategy_type=school
```

### 班级导入
```
POST /api/v1/import?strategy_type=classroom
```

### 学生考号导入（考试映射）
```
POST /api/v1/import?strategy_type=student
```

---

## ✅ 验证清单

导入前检查：
- [ ] Excel文件格式正确（.xlsx或.xls）
- [ ] 必填列已填写完整
- [ ] 学校已创建（或使用学校管理员模式）
- [ ] 年级已存在
- [ ] 班级已导入且班级编号正确
- [ ] 学籍号唯一（不重复）

导入后验证：
- [ ] 响应显示成功数量 > 0
- [ ] 检查错误列表（如果有）
- [ ] 使用学生账户登录测试
- [ ] 验证学生关联到正确的班级
- [ ] 检查考场分配功能正常

---

## 🎉 成功案例

假设你要为**第一中学**的**7年级**创建100个学生账户：

### 1. 准备Excel数据

```excel
学校名称      年级级别    班级编号    学籍号        姓名
第一中学      7          701        2024070001    张三
第一中学      7          701        2024070002    李四
第一中学      7          701        2024070003    王五
...（共100行）
```

### 2. 执行导入

```bash
curl -X POST "https://localhost:8000/api/v1/import?strategy_type=student_account" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@grade7_students.xlsx"
```

### 3. 查看结果

```json
{
  "total": 100,
  "success": 100,
  "failed": 0,
  "created": 100,
  "updated": 0,
  "skipped": 0,
  "errors": []
}
```

✅ **100名学生账户创建成功！**

### 4. 创建考试并分配考场

现在学生已存在，可以正常进行：
- 创建考试
- 自动分配考场
- 生成座位表和准考证

---

## 📞 技术支持

如有问题，请查看：
- **API文档**: https://localhost:8000/docs
- **后端日志**: `tail -f logs/backend.log`
- **数据库**: 检查 `users` 表验证学生账户

---

**创建日期**: 2026-01-17
**版本**: v1.0
**状态**: ✅ 已实现并测试
