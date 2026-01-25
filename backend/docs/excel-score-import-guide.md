# Excel成绩导入使用指南

## 📋 概述

本指南介绍如何使用Excel批量导入考试成绩数据到增值评价系统。

## ✨ 功能特性

- ✅ 支持批量导入成绩数据（1000+记录，<10秒）
- ✅ 异步处理，不阻塞系统
- ✅ 实时进度跟踪
- ✅ 完善的数据验证
- ✅ 详细的错误报告
- ✅ 支持重复导入（自动更新已有记录）
- ✅ 灵活的Excel格式（支持多种列名）

## 📊 Excel模板格式

### 基本格式

Excel文件必须包含以下列（列名可以有多种表达方式）：

| 必需列 | 可选列名 | 说明 |
|--------|---------|------|
| **考号** | 考号、考试号、准考证号 | 考试编号（必须已建立考号映射） |
| **学籍号** | 学籍号、学生学籍号、身份证号 | 学生唯一标识 |
| **科目** | 科目、学科、考试科目 | 科目名称 |
| **原始分** | 原始分、分数、成绩、得分 | 考试分数 |
| （可选）| 姓名、学生姓名 | 学生姓名（仅供参考） |
| （可选）| 缺考、是否缺考 | 缺考标记：是/否 |
| （可选）| 作弊、是否作弊 | 作弊标记：是/否 |

### 示例Excel

```
| 考号       | 学籍号        | 姓名   | 科目   | 原始分 | 缺考 | 作弊 |
|------------|--------------|--------|--------|--------|------|------|
| 202401001  | 11010120200101| 张三   | 数学   | 95     | 否   | 否   |
| 202401002  | 11010120200102| 李四   | 数学   | 87     | 否   | 否   |
| 202401003  | 11010120200103| 王五   | 数学   |        | 是   | 否   |
| 202401004  | 11010120200104| 赵六   | 数学   | 0      | 否   | 是   |
```

### 文件要求

- **文件格式**: `.xlsx` 或 `.xls`
- **文件大小**: 建议不超过10MB
- **编码**: UTF-8或GBK（Excel默认）
- **表头**: 第一行必须是列名

## 🔧 使用流程

### 步骤1：准备考号映射

在导入成绩之前，必须先建立考号映射关系。

**API**: `POST /api/v1/exam-number-mapping/batch`

**请求示例**:
```json
{
  "exam_id": 1,
  "mappings": [
    {
      "exam_number": "202401001",
      "student_id_number": "11010120200101",
      "school_id": 1,
      "classroom_id": 1
    },
    {
      "exam_number": "202401002",
      "student_id_number": "11010120200102",
      "school_id": 1,
      "classroom_id": 1
    }
  ]
}
```

### 步骤2：上传Excel并创建导入任务

**API**: `POST /api/v1/import-tasks/`

**参数**:
- `task_name`: 任务名称
- `exam_id`: 考试ID
- `file`: Excel文件
- `auto_process`: 是否自动处理（默认true）

**使用Python**:
```python
import requests

url = "http://localhost:8000/api/v1/import-tasks/"
files = {"file": open("scores.xlsx", "rb")}
data = {
    "task_name": "2024年期末数学成绩",
    "exam_id": 1,
    "auto_process": True
}
headers = {
    "Authorization": "Bearer YOUR_TOKEN"
}

response = requests.post(url, files=files, data=data, headers=headers)
task = response.json()

print(f"导入任务已创建: {task['id']}")
print(f"状态: {task['status']}")
```

**使用JavaScript (fetch)**:
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('task_name', '2024年期末数学成绩');
formData.append('exam_id', '1');
formData.append('auto_process', 'true');

fetch('http://localhost:8000/api/v1/import-tasks/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  body: formData
})
.then(response => response.json())
.then(task => {
  console.log('导入任务已创建:', task.id);
  console.log('状态:', task.status);
});
```

**响应示例**:
```json
{
  "id": 1,
  "task_name": "2024年期末数学成绩",
  "task_type": "score_data",
  "exam_id": 1,
  "file_url": "a1b2c3d4-e5f6-7890-abcd-ef1234567890.xlsx",
  "file_name": "scores.xlsx",
  "file_size": 10240,
  "status": "pending",
  "progress": 0,
  "total_rows": null,
  "processed_rows": 0,
  "failed_rows": 0,
  "error_message": null,
  "error_details": null,
  "created_by": 1,
  "started_at": null,
  "completed_at": null,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### 步骤3：查询导入进度

**API**: `GET /api/v1/import-tasks/{task_id}`

**使用Python**:
```python
import requests
import time

task_id = 1
url = f"http://localhost:8000/api/v1/import-tasks/{task_id}"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

while True:
    response = requests.get(url, headers=headers)
    task = response.json()

    print(f"进度: {task['progress']}%")
    print(f"状态: {task['status']}")
    print(f"已处理: {task['processed_rows']}/{task['total_rows']}")

    if task['status'] in ['completed', 'failed', 'cancelled']:
        break

    time.sleep(2)  # 每2秒查询一次
```

### 步骤4：查看错误详情（如果有）

**API**: `GET /api/v1/import-tasks/{task_id}/errors`

**响应示例**:
```json
{
  "task_id": 1,
  "error_message": "导入完成，但有 2 条记录失败",
  "errors": [
    {
      "row": 5,
      "exam_number": "202401005",
      "error": "考号 '202401005' 不存在或未关联到该考试"
    },
    {
      "row": 8,
      "exam_number": "202401008",
      "error": "分数 150 超出合理范围 (0-150)"
    }
  ]
}
```

## ⚠️ 数据验证规则

### 1. 考号验证
- 考号必须存在于`ExamNumberMapping`表中
- 考号必须关联到指定的考试

### 2. 学籍号验证
- 学籍号必须存在于`User`表中
- 学籍号必须与考号映射中的学生ID一致

### 3. 科目验证
- 科目名称必须存在于`Subject`表中
- 科目名称必须完全匹配

### 4. 分数验证
- 分数必须是数字
- 分数范围：0-150（可根据需要调整）
- 如果标记为缺考或作弊，分数可以为空或0

### 5. 缺考/作弊标记
- 支持值：是/否、Y/N、yes/no、1/0、True/False
- 大小写不敏感

## 🔄 重复导入处理

如果导入了相同的成绩（相同的考试、学生、科目）：

- **更新模式**: 系统会更新已有记录的分数、缺考、作弊标记
- **不会创建重复记录**
- 原始ID和时间戳保持不变

## 🛠️ 任务管理

### 取消任务

**API**: `POST /api/v1/import-tasks/{task_id}/cancel`

**条件**:
- 只能取消状态为 `pending` 或 `processing` 的任务
- 已完成、失败或已取消的任务无法取消

### 重试失败任务

**API**: `POST /api/v1/import-tasks/{task_id}/retry`

**说明**:
- 重置任务状态为 `pending`
- 清空进度和错误信息
- 重新开始处理

### 删除任务

**API**: `DELETE /api/v1/import-tasks/{task_id}`

**注意**:
- 删除任务不会删除已导入的成绩数据
- 只删除任务记录和上传的Excel文件

## 📈 性能指标

| 指标 | 值 |
|------|-----|
| 导入速度 | >100行/秒 |
| 1000条成绩 | <10秒 |
| 支持最大文件 | 10MB |
| 并发任务数 | 无限制 |

## 🔐 权限说明

| 角色 | 创建任务 | 查看任务 | 取消任务 | 删除任务 |
|------|---------|---------|---------|---------|
| 管理员 | ✓ | 所有 | 所有 | 所有 |
| 区县管理员 | ✓ | 所有 | 所有 | 所有 |
| 学校管理员 | ✓ | 所有 | 所有 | 自己的 |
| 其他角色 | ✗ | 自己的 | ✗ | ✗ |

## 📝 最佳实践

### 1. 准备阶段
- ✅ 确保所有学生已在系统中
- ✅ 确保所有科目已创建
- ✅ 先建立考号映射
- ✅ 准备正确的Excel模板

### 2. 导入阶段
- ✅ 使用有意义的任务名称（如"2024年期末数学成绩"）
- ✅ 开启自动处理（`auto_process=True`）
- ✅ 监控导入进度
- ✅ 检查错误报告

### 3. 错误处理
- ✅ 修复Excel中的错误数据
- ✅ 重新上传或使用重试功能
- ✅ 保留错误日志用于追溯

### 4. 数据验证
- ✅ 导入后随机抽查部分记录
- ✅ 使用统计API验证总数
- ✅ 检查分数范围和分布

## 🐛 常见问题

### Q1: 导入任务一直处于pending状态

**A**: 检查`auto_process`参数是否为`True`。如果为`False`，需要手动调用处理API。

### Q2: 所有记录都验证失败

**A**: 检查以下项：
- 考号映射是否已建立
- 学生学籍号是否正确
- 科目名称是否完全匹配
- Excel列名是否正确

### Q3: 部分记录导入失败

**A**:
1. 调用错误详情API查看具体错误
2. 修复Excel中的错误数据
3. 重新上传或更新失败的记录

### Q4: 如何批量建立考号映射？

**A**: 使用考号映射批量创建API：
```python
POST /api/v1/exam-number-mapping/batch
```

### Q5: 如何导出成绩模板？

**A**: 可以在系统中创建一个Excel模板，包含所有必需的列名。

## 🔗 相关API

- 考号映射管理: `POST /api/v1/exam-number-mapping/batch`
- 成绩查询: `GET /api/v1/scores`
- 考试统计: `GET /api/v1/scores/exams/{exam_id}/statistics`

## 📞 技术支持

如有问题，请联系技术支持团队或查看：
- [API参考文档](./evaluation-api-reference.md)
- [实施进度报告](./implementation-progress-report.md)
