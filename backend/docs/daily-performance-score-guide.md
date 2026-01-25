# 日常表现成绩系统使用指南

## 📋 概述

日常表现成绩系统将学生的日常表现数据（考勤、课堂表现、纪律、值日）整合为独立的百分制成绩，与考试成绩体系一致，但独立于增值评价系统。

## 🎯 核心特性

### 1. 百分制评分
- 采用0-100分制，与考试分数体系一致
- 支持等级评价：优秀/良好/合格/不合格

### 2. 灵活的统计周期
- ✅ 按学期：整个学期汇总
- ✅ 按月：每月统计
- ✅ 按考试周期：与考试同步
- ✅ 自定义：任意时间范围

### 3. 独立于增值评价
- ✅ 只记录和展示日常表现
- ✅ 不参与首尾对比的增值计算

### 4. 多维度评价
- 考勤（20%）：出勤、迟到、请假、缺勤
- 课堂表现（40%）：积极回答、作业优秀等
- 纪律（30%）：违纪次数
- 值日（10%）：值日完成情况

## 📊 数据模型

### DailyPerformanceScore 表结构

```python
class DailyPerformanceScore(Base):
    """日常表现成绩表"""

    # 关联信息
    student_id: Integer      # 学生ID
    classroom_id: Integer    # 班级ID
    semester_id: Integer     # 学期ID（可选）

    # 统计时间范围
    period_name: String      # "2024年上学期"/"2024年3月"
    start_date: DateTime     # 统计开始日期
    end_date: DateTime       # 统计结束日期

    # 原始数据统计
    positive_behavior_count: Integer    # 正面行为次数
    positive_behavior_points: Integer   # 正面行为总积分
    discipline_count: Integer           # 纪律次数
    discipline_points: Integer          # 纪律扣分
    attendance_present_count: Integer   # 出勤次数
    attendance_late_count: Integer      # 迟到次数
    attendance_leave_count: Integer     # 请假次数
    attendance_absent_count: Integer    # 缺勤次数
    duty_completed_count: Integer       # 值日完成次数

    # 百分制成绩
    final_score: Float        # 最终百分制成绩（0-100）
    grade_level: String        # 等级：优秀/良好/合格/不合格

    # 详细分类得分（JSON）
    detail_scores: JSON        # 各分类详细得分和权重

    # 备注
    note: Text                # 教师评语
```

## 🔧 使用方法

### 1. 为单个学生计算成绩

```python
from datetime import datetime
from app.services.daily_performance_calculator import DailyPerformanceCalculator
from sqlalchemy.ext.asyncio import AsyncSession

async def calculate_student_performance(
    session: AsyncSession,
    student_id: int
):
    # 计算3月份的表现成绩
    score = await DailyPerformanceCalculator.calculate_for_student(
        session=session,
        student_id=student_id,
        classroom_id=1,
        start_date=datetime(2024, 3, 1),
        end_date=datetime(2024, 3, 31, 23, 59, 59),
        period_name="2024年3月",
        semester_id=1,
        created_by=1  # 教师ID
    )

    # 保存到数据库
    session.add(score)
    await session.commit()

    print(f"成绩: {score.final_score}分 ({score.grade_level})")
```

### 2. 批量为班级计算成绩

```python
async def calculate_classroom_performance(
    session: AsyncSession,
    classroom_id: int
):
    # 计算整个学期的表现成绩
    scores = await DailyPerformanceCalculator.batch_calculate_for_classroom(
        session=session,
        classroom_id=classroom_id,
        start_date=datetime(2024, 2, 26),
        end_date=datetime(2024, 7, 15),
        period_name="2023-2024学年下学期",
        semester_id=1,
        weights={  # 自定义权重（可选）
            "attendance": 0.25,  # 考勤 25%
            "behavior": 0.35,    # 表现 35%
            "discipline": 0.30,  # 纪律 30%
            "duty": 0.10,        # 值日 10%
        },
        created_by=1
    )

    # 批量保存
    session.add_all(scores)
    await session.commit()

    print(f"已计算 {len(scores)} 名学生的表现成绩")

    # 统计班级平均分
    avg_score = sum(s.final_score for s in scores) / len(scores)
    print(f"班级平均分: {avg_score:.2f}")
```

## 📐 计算逻辑

### 默认权重配置

```python
DEFAULT_WEIGHTS = {
    "attendance": 0.20,    # 考勤权重 20%
    "behavior": 0.40,      # 课堂表现权重 40%
    "discipline": 0.30,    # 纪律权重 30%
    "duty": 0.10,          # 值日权重 10%
}
```

### 各分类得分计算

#### 1. 考勤得分（0-100分）
```python
attendance_score = 100 - (缺勤次数 × 10) - (迟到次数 × 2)
attendance_score = max(0, min(100, attendance_score))
```

**示例：**
- 全勤：100分
- 迟到1次：98分
- 缺勤1次：90分
- 缺勤2次+迟到3次：74分

#### 2. 课堂表现得分（0-100分）
```python
behavior_score = min(100, 正面行为总积分 × 2)
```

**示例：**
- 无正面行为记录：60分（及格）
- 获得积分30分：100分（满分）
- 获得积分15分：30分 × 2 = 60分

#### 3. 纪律得分（0-100分）
```python
discipline_score = max(0, 100 - (违纪次数 × 5))
```

**示例：**
- 无违纪：100分
- 违纪1次：95分
- 违纪3次：85分
- 违纪20次以上：0分

#### 4. 值日得分（0-100分）
```python
duty_score = min(100, 完成值日次数 × 10)
```

**示例：**
- 完成值日5次：50分
- 完成值日10次：100分
- 完成值日15次：100分（上限）

### 最终成绩计算

```python
final_score = (
    attendance_score × 0.20 +
    behavior_score × 0.40 +
    discipline_score × 0.30 +
    duty_score × 0.10
)
```

### 等级划分

| 分数范围 | 等级 |
|---------|------|
| 90-100 | 优秀 |
| 80-89 | 良好 |
| 60-79 | 合格 |
| 0-59 | 不合格 |

## 🔄 数据流程

```
日常行为数据收集
├── PositiveBehavior (正面行为)
├── DisciplineRecord (违纪记录)
├── AttendanceEntry (考勤记录)
└── DutyAssignment (值日任务)
         ↓
    统计汇总
         ↓
    计算各分类得分
         ↓
    加权计算总分
         ↓
DailyPerformanceScore (日常表现成绩)
         ↓
    展示和报告
```

## 📝 API 接口设计建议

### 1. 计算单个学生成绩
```http
POST /api/v1/daily-performance/calculate
Content-Type: application/json

{
  "student_id": 1,
  "classroom_id": 1,
  "start_date": "2024-03-01",
  "end_date": "2024-03-31",
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

### 2. 批量计算班级成绩
```http
POST /api/v1/classrooms/{id}/daily-performance/calculate
Content-Type: application/json

{
  "start_date": "2024-02-26",
  "end_date": "2024-07-15",
  "period_name": "2023-2024学年下学期"
}
```

### 3. 查询学生历史成绩
```http
GET /api/v1/students/{id}/daily-performance?semester_id=1
```

### 4. 获取班级统计
```http
GET /api/v1/classrooms/{id}/daily-performance/statistics
```

## 🎨 前端展示建议

### 1. 成绩卡片
```
┌─────────────────────────────┐
│  2024年3月日常表现成绩        │
├─────────────────────────────┤
│  总分: 87.5分  良好          │
│                             │
│  考勤: 95分 ██████████████  │
│  表现: 88分 █████████████  │
│  纪律: 90分 ██████████████ │
│  值日: 70分 ██████████     │
└─────────────────────────────┘
```

### 2. 详细数据展示
```
正面行为: 15次 (+30分)
违纪记录: 1次 (-5分)
考勤: 出勤20, 迟到1, 缺勤0
值日: 完成7次
```

### 3. 趋势图表
```
成绩趋势（折线图）
100 |
 90 |     ●
 80 |   ●   ●
 70 | ●
 60 +─────────────
    1月  2月  3月  4月
```

## ⚙️ 配置管理

### 1. 权重配置
建议在系统设置中提供权重配置界面，允许学校管理员自定义：
- 考勤权重：0-100%
- 表现权重：0-100%
- 纪律权重：0-100%
- 值日权重：0-100%

### 2. 分数线配置
允许自定义等级划分：
- 优秀线：默认90分
- 良好线：默认80分
- 合格线：默认60分

### 3. 扣分规则
- 缺勤扣分：每次-10分（可配置）
- 迟到扣分：每次-2分（可配置）
- 违纪扣分：每次-5分（可配置）

## 💡 最佳实践

### 1. 定期计算
- 每月自动计算一次月度成绩
- 每学期末计算学期成绩
- 重要考试前计算近期成绩

### 2. 数据可视化
- 展示学生的进步趋势
- 对比不同时期的表现
- 班级/年级排名（可选）

### 3. 及时反馈
- 学生可随时查看当前表现
- 家长可了解孩子日常表现
- 教师可调整教学策略

### 4. 正向激励
- 公开表扬优秀学生
- 鼓励进步明显的学生
- 关注需要帮助的学生

## 🔍 常见问题

### Q1: 日常表现成绩和考试成绩如何综合？
A: 可以在前端展示时同时呈现两者，例如：
- 考试成绩：85分
- 日常表现：92分
- 综合评价：优秀

### Q2: 学生转班后如何计算？
A: 按时间段分别计算：
- 1-3月在A班：使用A班数据
- 4-6月在B班：使用B班数据

### Q3: 历史数据可以修改吗？
A: 不建议修改。如果计算规则变更，应该重新计算并创建新记录。

### Q4: 如何处理请假？
A: 请假不扣分，但也不加考勤分。只有缺勤才扣分。

### Q5: 正面行为积分如何获得？
A: 教师通过"班级助手"功能记录正面行为，系统自动加分。

## 📚 相关文档

- [StudentType 使用指南](./student-type-usage.md)
- [增值评价系统PRD](../prd-value-added-evaluation-v3.md)
- [班级助手系统说明](./classroom-assistant-guide.md)

## 🚀 下一步功能

1. **自动计算任务**
   - 定时任务每月自动计算
   - 学期末自动汇总

2. **家长端展示**
   - 微信通知
   - 成绩报告单

3. **数据分析**
   - 班级对比
   - 年级排名
   - 趋势分析

4. **激励机制**
   - 优秀学生表彰
   - 进步奖励
   - 个性化建议
