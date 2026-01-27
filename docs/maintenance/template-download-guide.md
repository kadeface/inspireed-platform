# 📥 Excel模板下载 - 使用指南

## ✅ 已添加模板下载功能

现在可以通过API直接下载Excel导入模板，无需手动创建！

---

## 🎯 快速使用

### 方法1：浏览器直接下载（推荐）

```
https://localhost:8000/api/v1/import/template/student_account
```

会自动下载文件：`student_account_import_template.xlsx`

### 方法2：使用curl下载

```bash
# 下载学生账户模板（区县管理员模式）
curl -X GET "https://localhost:8000/api/v1/import/template/student_account" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o student_account_import_template.xlsx

# 下载学生账户模板（学校管理员模式）
curl -X GET "https://localhost:8000/api/v1/import/template/student_account?is_school_admin=true" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o student_account_import_template.xlsx
```

### 方法3：Swagger UI下载

1. 访问：`https://localhost:8000/docs`
2. 找到 `/api/v1/import/template/{strategy_type}` 端点
3. 点击"Try it out"
4. 选择 `strategy_type` 为 `student_account`
5. 点击"Execute"下载文件

---

## 📋 所有可用模板

| 策略类型 | URL路径 | 模板文件名 | 说明 |
|---------|---------|-----------|------|
| **学校导入** | `/template/school` | `school_import_template.xlsx` | 导入学校信息 |
| **班级导入** | `/template/classroom` | `classroom_import_template.xlsx` | 导入班级（双模式） |
| **学生考号导入** | `/template/student` | `student_exam_import_template.xlsx` | 导入考号映射 |
| **学生账户导入** | `/template/student_account` | `student_account_import_template.xlsx` | ✨ 创建学生账户 |
| **教师导入** | `/template/teacher` | `teacher_import_template.xlsx` | 导入教师教学任务 |

---

## 📊 学生账户模板说明

### 区县管理员模式

**列结构**：
```
学校名称* | 学校代码 | 年级级别* | 班级编号* | 学籍号* | 姓名* | 用户名 | 邮箱 | 手机号 | 性别
```

**示例数据**：
```
第一中学 | 101 | 10 | 1001 | 2024100001 | 张三 | 2024100001 | 2024100001@inspireed.com | 13800138000 | 男
第一中学 | 101 | 10 | 1001 | 2024100002 | 李四 | 2024100002 | 2024100002@inspireed.com | 13800138001 | 女
第一中学 | 101 | 10 | 1002 | 2024100003 | 王五 | 2024100003 | 2024100003@inspireed.com | 13800138002 | 男
```

### 学校管理员模式

**列结构**（不需要学校名称）：
```
年级级别* | 班级编号* | 学籍号* | 姓名* | 用户名 | 邮箱 | 手机号 | 性别
```

**示例数据**：
```
10 | 1001 | 2024100001 | 张三 | 2024100001 | 2024100001@inspireed.com | 13800138000 | 男
10 | 1001 | 2024100002 | 李四 | 2024100002 | 2024100002@inspireed.com | 13800138001 | 女
10 | 1002 | 2024100003 | 王五 | 2024100003 | 2024100003@inspireed.com | 13800138002 | 男
```

---

## 🎨 模板特性

### Excel格式

- ✅ **标题行**：模板名称和日期
- ✅ **说明行**：红色文字提示注意事项
- ✅ **表头行**：蓝色背景，白色文字，居中对齐
- ✅ **示例行**：灰色斜体文字，3行示例数据
- ✅ **说明行**：标注必填/可选
- ✅ **列宽**：自动调整（15字符宽度）

### 颜色标识

- 🔵 **蓝色表头**：列名
- 🟙 **灰色文字**：示例数据
- 🟤 **灰色小字**：必填/可选说明
- 🔴 **红色说明**：重要提示

---

## 📝 使用步骤

### 1. 下载模板

```bash
# 下载学生账户导入模板
curl -X GET "https://localhost:8000/api/v1/import/template/student_account" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o students.xlsx
```

### 2. 打开并编辑

- 用Excel或WPS打开下载的模板文件
- **删除示例数据**（第6-8行）
- 保留第5行的表头
- 从第6行开始填写真实数据

### 3. 填写数据

**必填字段**（5个）：
1. **学校名称**（区县模式）/ **年级级别**（学校模式）
2. **年级级别**
3. **班级编号**（如：1001=10年级1班）
4. **学籍号**（唯一标识）
5. **姓名**

**可选字段**：
- 用户名（默认=学籍号）
- 邮箱（自动生成）
- 手机号
- 性别

### 4. 保存并导入

- 保存Excel文件
- 使用统一导入API上传

```bash
curl -X POST "https://localhost:8000/api/v1/import?strategy_type=student_account" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@students.xlsx"
```

---

## 🔍 模板字段详解

### 区县管理员模板（10列）

| 列 | 必填 | 说明 | 示例 |
|----|------|------|------|
| 学校名称 | ✅ | 学校全称 | 第一中学 |
| 学校代码 | ❌ | 学校编码 | 101 |
| 年级级别 | ✅ | 数字（1-12） | 10 |
| 班级编号 | ✅ | 年级+班级 | 1001 |
| 学籍号 | ✅ | 唯一标识 | 2024100001 |
| 姓名 | ✅ | 学生姓名 | 张三 |
| 用户名 | ❌ | 登录名（默认学籍号） | 2024100001 |
| 邮箱 | ❌ | 自动生成 | 2024100001@inspireed.com |
| 手机号 | ❌ | 联系电话 | 13800138000 |
| 性别 | ❌ | 男/女 | 男 |

### 学校管理员模板（8列）

| 列 | 必填 | 说明 | 示例 |
|----|------|------|------|
| 年级级别 | ✅ | 数字（1-12） | 10 |
| 班级编号 | ✅ | 年级+班级 | 1001 |
| 学籍号 | ✅ | 唯一标识 | 2024100001 |
| 姓名 | ✅ | 学生姓名 | 张三 |
| 用户名 | ❌ | 登录名 | 2024100001 |
| 邮箱 | ❌ | 自动生成 | 2024100001@inspireed.com |
| 手机号 | ❌ | 联系电话 | 13800138000 |
| 性别 | ❌ | 男/女 | 男 |

---

## 🚀 完整工作流

```
第1步：下载模板
GET /api/v1/import/template/student_account
↓
下载文件：student_account_import_template.xlsx

第2步：编辑Excel
- 删除示例数据
- 填写真实学生信息
- 保存文件

第3步：导入数据
POST /api/v1/import?strategy_type=student_account
- 上传Excel文件
- 查看导入结果

第4步：验证结果
- 检查成功数量
- 学生可以登录（密码：123456）
- 考场分配功能正常
```

---

## 💡 提示

### 数据验证

导入前检查：
- ✅ Excel文件格式正确（.xlsx）
- ✅ 必填列已填写完整
- ✅ 学校/年级/班级已存在
- ✅ 学籍号唯一（不重复）
- ✅ 年级级别是数字（1-12）
- ✅ 班级编号格式正确（如：1001）

### 常见错误

| 错误 | 原因 | 解决方法 |
|------|------|---------|
| 学校 'XXX' 未找到 | 学校名称不匹配 | 先用school导入创建学校 |
| 年级级别 X 不存在 | 年级未创建 | 在系统中创建对应年级 |
| 班级编号 'XXX' 不存在 | 班级未创建 | 先用classroom导入创建班级 |
| 学籍号 'XXX' 已存在 | 学生已存在 | 设置`update_existing=true` |
| 用户名 'XXX' 已存在 | 用户名冲突 | 在Excel中指定不同用户名 |

---

## 📚 API参考

### 下载模板端点

```
GET /api/v1/import/template/{strategy_type}
```

**参数**：
- `strategy_type` (路径参数): 导入类型
  - `school` - 学校导入
  - `classroom` - 班级导入
  - `student` - 学生考号导入
  - `student_account` - 学生账户导入
  - `teacher` - 教师导入
- `is_school_admin` (查询参数，可选): 学校管理员模式（默认false）
  - 适用于：`classroom`、`student_account`

**响应**：
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- 文件下载

### 示例请求

```bash
# 下载学生账户模板（区县管理员）
curl -X GET "https://localhost:8000/api/v1/import/template/student_account" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o template.xlsx

# 下载学生账户模板（学校管理员）
curl -X GET "https://localhost:8000/api/v1/import/template/student_account?is_school_admin=true" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o template.xlsx

# 下载班级模板
curl -X GET "https://localhost:8000/api/v1/import/template/classroom" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o template.xlsx

# 下载学校模板
curl -X GET "https://localhost:8000/api/v1/import/template/school" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o template.xlsx
```

---

## ✅ 总结

✅ **模板下载功能已添加**
- 支持5种导入类型
- 双模式模板（区县/学校）
- Excel格式美观易用
- 包含示例数据和说明

✅ **现在可以**：
1. 下载模板 → 一键下载
2. 编辑数据 → 填写真实信息
3. 导入系统 → 快速批量创建
4. 验证结果 → 查看导入统计

---

**更新日期**: 2026-01-17
**版本**: v1.1
**状态**: ✅ 已实现并可用
