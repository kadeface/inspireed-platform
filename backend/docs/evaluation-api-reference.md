# 增值评价系统 API 参考文档

## 概述

本文档描述了增值评价系统的所有 API 端点，包括学期管理、考试管理、成绩查询、日常表现成绩和高中总分评价。

**基础路径**: `/api/v1`

**认证**: 所有端点需要 Bearer Token (JWT)

---

## 1. 学期管理 API (`/semesters`)

### 1.1 创建学期

```http
POST /api/v1/semesters/
Content-Type: application/json
Authorization: Bearer <token>

{
  "year": 2024,
  "semester_type": "上学期",
  "name": "2024年上学期",
  "start_date": "2024-02-26T00:00:00Z",
  "end_date": "2024-07-15T23:59:59Z",
  "is_current": true,
  "region_id": 1
}
```

**权限**: `admin`, `district_admin`, `school_admin`

**响应**: `200 OK` - 返回创建的学期对象

### 1.2 获取学期列表

```http
GET /api/v1/semesters/?skip=0&limit=100&year=2024&is_current=true
Authorization: Bearer <token>
```

**查询参数**:
- `skip`: 跳过记录数 (默认: 0)
- `limit`: 返回记录数 (默认: 100, 最大: 100)
- `year`: 学年筛选 (可选)
- `is_current`: 是否当前学期 (可选)
- `region_id`: 区县ID筛选 (可选)

**响应**: `200 OK` - 返回学期列表

### 1.3 获取当前学期

```http
GET /api/v1/semesters/current/?region_id=1
Authorization: Bearer <token>
```

**响应**: `200 OK` - 返回当前学期

### 1.4 获取学期详情

```http
GET /api/v1/semesters/{semester_id}
Authorization: Bearer <token>
```

**响应**: `200 OK` - 返回学期详情

### 1.5 更新学期

```http
PUT /api/v1/semesters/{semester_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "is_current": false
}
```

**权限**: `admin`, `district_admin`, `school_admin`

**响应**: `200 OK` - 返回更新后的学期

### 1.6 删除学期

```http
DELETE /api/v1/semesters/{semester_id}
Authorization: Bearer <token>
```

**权限**: `admin`, `district_admin`

**响应**: `204 No Content`

---

## 2. 考试管理 API (`/exams`)

### 2.1 创建考试

```http
POST /api/v1/exams/
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "2024年3月月考",
  "exam_type": "monthly",
  "exam_date": "2024-03-15T09:00:00Z",
  "semester_id": 1,
  "grade_id": 10,
  "region_id": 1,
  "school_id": 1,
  "status": "scheduled"
}
```

**权限**: `admin`, `district_admin`, `school_admin`

**响应**: `201 Created` - 返回创建的考试对象

**exam_type 枚举值**:
- `midterm`: 期中考试
- `final`: 期末考试
- `monthly`: 月考
- `unit`: 单元测试
- `mock`: 模拟考试
- `district_unified`: 区县统考
- `entrance`: 中考/高考

**status 枚举值**:
- `draft`: 草稿
- `scheduled`: 已安排
- `in_progress`: 进行中
- `completed`: 已完成
- `cancelled`: 已取消

### 2.2 获取考试列表

```http
GET /api/v1/exams/?skip=0&limit=100&semester_id=1&exam_type=monthly&status=completed
Authorization: Bearer <token>
```

**查询参数**:
- `skip`: 跳过记录数
- `limit`: 返回记录数
- `semester_id`: 学期ID筛选
- `exam_type`: 考试类型筛选
- `status`: 状态筛选
- `grade_id`: 年级ID筛选
- `region_id`: 区县ID筛选
- `school_id`: 学校ID筛选

**响应**: `200 OK` - 返回考试列表（按考试日期降序）

### 2.3 获取考试详情

```http
GET /api/v1/exams/{exam_id}
Authorization: Bearer <token>
```

**响应**: `200 OK` - 返回考试详情

### 2.4 更新考试

```http
PUT /api/v1/exams/{exam_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "status": "completed"
}
```

**权限**: `admin`, `district_admin`, `school_admin`, 或创建者

**响应**: `200 OK` - 返回更新后的考试

### 2.5 删除考试

```http
DELETE /api/v1/exams/{exam_id}
Authorization: Bearer <token>
```

**权限**: `admin`, `district_admin`

**响应**: `204 No Content`

### 2.6 添加考试科目

```http
POST /api/v1/exams/{exam_id}/subjects
Content-Type: application/json
Authorization: Bearer <token>

{
  "subject_id": 1,
  "full_score": 100,
  "pass_line": 60,
  "excellent_line": 85,
  "good_line": 75
}
```

**权限**: `admin`, `district_admin`, `school_admin`

**响应**: `201 Created` - 返回创建的考试科目关联

### 2.7 获取考试科目列表

```http
GET /api/v1/exams/{exam_id}/subjects
Authorization: Bearer <token>
```

**响应**: `200 OK` - 返回考试的所有科目

---

## 3. 成绩查询 API (`/scores`)

### 3.1 获取成绩列表

```http
GET /api/v1/scores/?skip=0&limit=100&exam_id=1&subject_id=1&min_score=60&max_score=100
Authorization: Bearer <token>
```

**查询参数**:
- `skip`: 跳过记录数
- `limit`: 返回记录数
- `exam_id`: 考试ID筛选
- `subject_id`: 科目ID筛选
- `student_id`: 学生ID筛选
- `min_score`: 最低分数筛选
- `max_score`: 最高分数筛选
- `grade_level`: 等级筛选

**响应**: `200 OK` - 返回成绩列表（按分数降序）

**权限说明**:
- **学生**: 只能查看自己的成绩
- **教师**: 只能查看所教班级/年级的成绩
- **管理员/教研员**: 可查看所有成绩

### 3.2 获取成绩详情

```http
GET /api/v1/scores/{score_id}
Authorization: Bearer <token>
```

**响应**: `200 OK` - 返回成绩详情

### 3.3 获取考试成绩统计

```http
GET /api/v1/scores/exams/{exam_id}/statistics?subject_id=1
Authorization: Bearer <token>
```

**查询参数**:
- `subject_id`: 科目ID（可选，不填则统计所有科目）

**响应**: `200 OK`

```json
{
  "exam_id": 1,
  "subject_id": 1,
  "total_count": 100,
  "absent_count": 2,
  "cheated_count": 0,
  "valid_count": 98,
  "average_score": 78.5,
  "max_score": 100,
  "min_score": 45,
  "excellent_rate": 35.71,
  "good_rate": 65.31,
  "pass_rate": 89.8,
  "fail_rate": 10.2,
  "score_distribution": {
    "90-100": 15,
    "80-89": 20,
    "70-79": 35,
    "60-69": 28,
    "0-59": 10
  }
}
```

### 3.4 获取学生的所有考试成绩

```http
GET /api/v1/scores/students/{student_id}/exams?semester_id=1
Authorization: Bearer <token>
```

**查询参数**:
- `semester_id`: 学期ID筛选（可选）

**响应**: `200 OK`

```json
{
  "student_id": 1,
  "exams": [
    {
      "exam_id": 1,
      "exam_name": "2024年3月月考",
      "exam_date": "2024-03-15T09:00:00Z",
      "exam_type": "monthly",
      "subject_id": 1,
      "raw_score": 85,
      "standard_score": null,
      "percentile": null,
      "grade_level": "优秀",
      "is_absent": false,
      "is_cheated": false
    }
  ]
}
```

### 3.5 获取班级考试成绩

```http
GET /api/v1/scores/classrooms/{classroom_id}/exams/{exam_id}?subject_id=1
Authorization: Bearer <token>
```

**查询参数**:
- `subject_id`: 科目ID筛选（可选）

**权限**: `admin`, `district_admin`, `school_admin`, `teacher`

**响应**: `200 OK`

```json
{
  "classroom_id": 1,
  "exam_id": 1,
  "subject_id": 1,
  "total_count": 30,
  "scores": [
    {
      "score_id": 1,
      "student_id": 1,
      "student_name": "张三",
      "student_number": "202401001",
      "subject_id": 1,
      "raw_score": 95,
      "standard_score": null,
      "percentile": null,
      "grade_level": "优秀",
      "is_absent": false,
      "is_cheated": false
    }
  ]
}
```

---

## 4. 日常表现成绩 API (`/daily-performance`)

### 4.1 计算单个学生日常表现成绩

```http
POST /api/v1/daily-performance/calculate
Content-Type: application/json
Authorization: Bearer <token>

{
  "student_id": 1,
  "classroom_id": 1,
  "start_date": "2024-03-01T00:00:00Z",
  "end_date": "2024-03-31T23:59:59Z",
  "period_name": "2024年3月",
  "semester_id": 1,
  "weights": {
    "attendance": 0.20,
    "behavior": 0.40,
    "discipline": 0.30,
    "duty": 0.10
  }
}
```

**权限**: `admin`, `district_admin`, `school_admin`, `teacher`

**响应**: `201 Created` - 返回计算的日常表现成绩

### 4.2 批量计算班级日常表现成绩

```http
POST /api/v1/daily-performance/batch-calculate
Content-Type: application/json
Authorization: Bearer <token>

{
  "classroom_id": 1,
  "start_date": "2024-03-01T00:00:00Z",
  "end_date": "2024-03-31T23:59:59Z",
  "period_name": "2024年3月",
  "semester_id": 1,
  "weights": {
    "attendance": 0.25,
    "behavior": 0.35,
    "discipline": 0.30,
    "duty": 0.10
  }
}
```

**权限**: `admin`, `district_admin`, `school_admin`, `teacher`

**响应**: `200 OK` - 返回班级所有学生的日常表现成绩列表

### 4.3 获取日常表现成绩列表

```http
GET /api/v1/daily-performance/?skip=0&limit=100&student_id=1&classroom_id=1&semester_id=1
Authorization: Bearer <token>
```

**响应**: `200 OK` - 返回日常表现成绩列表

### 4.4 获取单个日常表现成绩

```http
GET /api/v1/daily-performance/{score_id}
Authorization: Bearer <token>
```

**响应**: `200 OK` - 返回日常表现成绩详情

### 4.5 更新日常表现成绩

```http
PUT /api/v1/daily-performance/{score_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "final_score": 88.5,
  "grade_level": "良好",
  "note": "表现有进步"
}
```

**权限**: 创建者或管理员

**响应**: `200 OK` - 返回更新后的成绩

### 4.6 删除日常表现成绩

```http
DELETE /api/v1/daily-performance/{score_id}
Authorization: Bearer <token>
```

**权限**: `admin`, `district_admin`, `school_admin`

**响应**: `204 No Content`

### 4.7 获取学生日常表现历史

```http
GET /api/v1/daily-performance/students/{student_id}/history?semester_id=1
Authorization: Bearer <token>
```

**响应**: `200 OK` - 返回学生历史日常表现成绩列表

### 4.8 获取班级日常表现统计

```http
GET /api/v1/daily-performance/classrooms/{classroom_id}/statistics?period_name=2024年3月
Authorization: Bearer <token>
```

**响应**: `200 OK`

```json
{
  "classroom_id": 1,
  "period_name": "2024年3月",
  "total_count": 30,
  "average_score": 82.3,
  "grade_distribution": {
    "优秀": "8人 (26.7%)",
    "良好": "15人 (50.0%)",
    "合格": "6人 (20.0%)",
    "不合格": "1人 (3.3%)"
  },
  "dimension_averages": {
    "attendance_score": 95.5,
    "behavior_score": 78.2,
    "discipline_score": 88.0,
    "duty_score": 70.0
  }
}
```

---

## 5. 高中总分评价 API (`/total-scores`)

### 5.1 创建高中总分评价

```http
POST /api/v1/total-scores/
Content-Type: application/json
Authorization: Bearer <token>

{
  "exam_id": 1,
  "student_id": 1,
  "student_type": "science",
  "total_score": 680
}
```

**权限**: `admin`, `district_admin`, `school_admin`, `teacher`

**响应**: `201 Created` - 返回创建的总分评价

**student_type 枚举值**:
- `none`: 未分科（小学、初中、高中未分科阶段）
- `arts`: 文科（历史方向/偏文）
- `science`: 理科（物理方向/偏理）

### 5.2 批量创建高中总分评价

```http
POST /api/v1/total-scores/batch
Content-Type: application/json
Authorization: Bearer <token>

{
  "exam_id": 1,
  "scores": [
    {
      "student_id": 1,
      "total_score": 685,
      "student_type": "science"
    },
    {
      "student_id": 2,
      "total_score": 655,
      "student_type": "arts"
    }
  ]
}
```

**权限**: `admin`, `district_admin`, `school_admin`, `teacher`

**响应**: `200 OK` - 返回批量创建的总分评价列表

### 5.3 获取高中总分评价列表

```http
GET /api/v1/total-scores/?skip=0&limit=100&exam_id=1&student_id=1&student_type=science
Authorization: Bearer <token>
```

**查询参数**:
- `skip`: 跳过记录数
- `limit`: 返回记录数
- `exam_id`: 考试ID筛选
- `student_id`: 学生ID筛选
- `student_type`: 学生类型筛选 (none/arts/science)

**响应**: `200 OK` - 返回总分评价列表（按总分降序）

### 5.4 获取单个高中总分评价

```http
GET /api/v1/total-scores/{score_id}
Authorization: Bearer <token>
```

**响应**: `200 OK` - 返回总分评价详情

### 5.5 更新高中总分评价

```http
PUT /api/v1/total-scores/{score_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "total_score": 690,
  "student_type": "science"
}
```

**权限**: 创建者或管理员

**响应**: `200 OK` - 返回更新后的总分评价

### 5.6 删除高中总分评价

```http
DELETE /api/v1/total-scores/{score_id}
Authorization: Bearer <token>
```

**权限**: `admin`, `district_admin`, `school_admin`

**响应**: `204 No Content`

### 5.7 获取考试总分统计

```http
GET /api/v1/total-scores/exams/{exam_id}/statistics?student_type=science
Authorization: Bearer <token>
```

**查询参数**:
- `student_type`: 学生类型筛选 (none/arts/science，可选)

**响应**: `200 OK`

```json
{
  "exam_id": 1,
  "student_type": "science",
  "total_count": 100,
  "c9_count": 15,
  "special_control_count": 45,
  "undergraduate_count": 85,
  "junior_college_count": 98,
  "average_score": 565.5,
  "max_score": 710,
  "min_score": 380,
  "score_distribution": {
    "700+": 5,
    "650-699": 12,
    "600-649": 25,
    "550-599": 30,
    "500-549": 18,
    "450-499": 8,
    "400-449": 2,
    "400以下": 0
  }
}
```

### 5.8 获取学生高中总分历史

```http
GET /api/v1/total-scores/students/{student_id}/history?skip=0&limit=100
Authorization: Bearer <token>
```

**响应**: `200 OK` - 返回学生历史总分评价列表

### 5.9 获取考试总分排名

```http
GET /api/v1/total-scores/exams/{exam_id}/ranking?student_type=science&top_n=50
Authorization: Bearer <token>
```

**查询参数**:
- `student_type`: 学生类型筛选 (none/arts/science，可选)
- `top_n`: 返回前N名 (默认: 50，最大: 100)

**响应**: `200 OK`

```json
{
  "exam_id": 1,
  "student_type": "science",
  "total_count": 50,
  "ranking": [
    {
      "rank": 1,
      "student_id": 1,
      "total_score": 710,
      "student_type": "science",
      "grade_level": "C9联盟",
      "reached_c9": true,
      "reached_special_control": true,
      "reached_undergraduate": true,
      "reached_junior_college": true
    }
  ]
}
```

---

## 权限说明

### 角色枚举

```python
class UserRole(str, Enum):
    ADMIN = "admin"                    # 系统管理员
    DISTRICT_ADMIN = "district_admin"  # 区县管理员
    SCHOOL_ADMIN = "school_admin"      # 学校管理员
    RESEARCHER = "researcher"          # 教研员
    TEACHER = "teacher"                # 教师（含班主任）
    STUDENT = "student"                # 学生
```

### 数据访问权限矩阵

| 功能 | ADMIN | DISTRICT_ADMIN | SCHOOL_ADMIN | RESEARCHER | TEACHER | STUDENT |
|------|-------|----------------|--------------|------------|---------|---------|
| 创建学期/考试 | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| 查看所有学期/考试 | ✓ | ✓ | ✓ | ✓* | ✓* | ✓ |
| 更新学期/考试 | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| 删除学期/考试 | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| 查看所有成绩 | ✓ | ✓ | 本校 | ✓* | 本班 | 本人 |
| 创建成绩 | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| 查看成绩统计 | ✓ | ✓ | 本校 | ✓* | 本班 | ✗ |
| 创建日常表现成绩 | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ |
| 创建总分评价 | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ |

*注：教研员只能访问所属区县/学校的数据

---

## 错误响应

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

**解决方案**: 在请求头中提供有效的 JWT Token

### 403 Forbidden
```json
{
  "detail": "只有管理员可以执行此操作"
}
```

**解决方案**: 确认用户角色具有相应权限

### 404 Not Found
```json
{
  "detail": "考试不存在"
}
```

**解决方案**: 确认资源ID正确

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "exam_type"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

**解决方案**: 检查请求参数格式和枚举值

---

## 使用示例

### Python (使用 requests)

```python
import requests
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your_jwt_token_here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 1. 创建学期
semester_data = {
    "year": 2024,
    "semester_type": "上学期",
    "name": "2024年上学期",
    "start_date": "2024-02-26T00:00:00Z",
    "end_date": "2024-07-15T23:59:59Z",
    "is_current": True
}
response = requests.post(f"{BASE_URL}/semesters/", json=semester_data, headers=headers)
semester = response.json()
print(f"Created semester: {semester['id']}")

# 2. 创建考试
exam_data = {
    "name": "2024年3月月考",
    "exam_type": "monthly",
    "exam_date": "2024-03-15T09:00:00Z",
    "semester_id": semester['id'],
    "grade_id": 10,
    "status": "scheduled"
}
response = requests.post(f"{BASE_URL}/exams/", json=exam_data, headers=headers)
exam = response.json()
print(f"Created exam: {exam['id']}")

# 3. 计算学生日常表现成绩
performance_data = {
    "student_id": 1,
    "classroom_id": 1,
    "start_date": "2024-03-01T00:00:00Z",
    "end_date": "2024-03-31T23:59:59Z",
    "period_name": "2024年3月",
    "semester_id": semester['id']
}
response = requests.post(
    f"{BASE_URL}/daily-performance/calculate",
    json=performance_data,
    headers=headers
)
performance = response.json()
print(f"Student performance: {performance['final_score']}分 ({performance['grade_level']})")

# 4. 查看考试成绩统计
response = requests.get(
    f"{BASE_URL}/scores/exams/{exam['id']}/statistics",
    headers=headers
)
stats = response.json()
print(f"Exam average: {stats['average_score']}")
print(f"Pass rate: {stats['pass_rate']}%")
```

### JavaScript/TypeScript (使用 fetch)

```typescript
const BASE_URL = 'http://localhost:8000/api/v1';
const token = 'your_jwt_token_here';

const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json',
};

// 创建学期
async function createSemester() {
  const semesterData = {
    year: 2024,
    semester_type: '上学期',
    name: '2024年上学期',
    start_date: '2024-02-26T00:00:00Z',
    end_date: '2024-07-15T23:59:59Z',
    is_current: true,
  };

  const response = await fetch(`${BASE_URL}/semesters/`, {
    method: 'POST',
    headers,
    body: JSON.stringify(semesterData),
  });

  const semester = await response.json();
  console.log('Created semester:', semester.id);
  return semester;
}

// 计算学生日常表现成绩
async function calculatePerformance(studentId: number, classroomId: number) {
  const performanceData = {
    student_id: studentId,
    classroom_id: classroomId,
    start_date: '2024-03-01T00:00:00Z',
    end_date: '2024-03-31T23:59:59Z',
    period_name: '2024年3月',
  };

  const response = await fetch(`${BASE_URL}/daily-performance/calculate`, {
    method: 'POST',
    headers,
    body: JSON.stringify(performanceData),
  });

  const performance = await response.json();
  console.log(`Performance: ${performance.final_score}分 (${performance.grade_level})`);
  return performance;
}
```

---

## 附录

### A. 状态码参考

| 状态码 | 说明 |
|--------|------|
| 200 | OK - 请求成功 |
| 201 | Created - 资源创建成功 |
| 204 | No Content - 删除成功 |
| 400 | Bad Request - 请求参数错误 |
| 401 | Unauthorized - 未认证 |
| 403 | Forbidden - 权限不足 |
| 404 | Not Found - 资源不存在 |
| 422 | Unprocessable Entity - 参数验证失败 |
| 500 | Internal Server Error - 服务器错误 |

### B. 日期时间格式

所有日期时间字段使用 ISO 8601 格式：
```
2024-03-15T09:00:00Z
2024-03-15T09:00:00+08:00
```

### C. 分页参数

- `skip`: 跳过的记录数（从0开始）
- `limit`: 返回的记录数（默认100，最大100）

**示例**:
- 第一页: `skip=0&limit=20`
- 第二页: `skip=20&limit=20`
- 第三页: `skip=40&limit=20`

### D. 相关文档

- [增值评价系统PRD](../prd-value-added-evaluation-v3.md)
- [日常表现成绩使用指南](./daily-performance-score-guide.md)
- [学生类型使用指南](./student-type-usage.md)
- [Swagger UI](http://localhost:8000/docs) - 自动生成的API文档

---

## 更新日志

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v1.0.0 | 2026-01-14 | 初始版本，包含学期、考试、成绩、日常表现、总分评价API |
