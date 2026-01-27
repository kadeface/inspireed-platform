# Schema Mastery Diagnosis Framework
## 图式掌握度认知诊断系统（K12）

### 1. 核心理念

传统测评看的是：
- 答案对不对

本系统看的是：
- 学生是否建立了正确的**认知图式（Schema）**
- 是否能在不同情境中**迁移结构**
- 是否能从操作中**抽象出关系不变量**

我们诊断的不是“会不会算”，而是：

> 学生的脑中是否已经形成  
> 可运行的结构模型（Executable Mental Model）

---

### 2. 诊断对象：六大核心图式族

| 图式族 | 典型能力 |
|--------|----------|
| A. 部分-整体 | 分数、比例、集合 |
| B. 比较差量 | 多多少、追及 |
| C. 变化-速率 | 路程、工作量、流量 |
| D. 比例缩放 | 函数、相似、倍数 |
| E. 守恒等价 | 面积、体积、方程 |
| F. 随机分布 | 概率、统计、期望 |

---

### 3. 图式掌握的四个层级（Schema Development Levels）

#### Level 1：感知层（Perceptual）

特征：
- 只能看动画
- 能描述现象
- 不能解释结构

诊断信号：
- 只能说“快了”“多了”
- 不能说“差在缩小”

---

#### Level 2：操作层（Operational）

特征：
- 会拖动
- 会调参数
- 但不理解不变量

诊断信号：
- 会调滑块
- 但无法预测结果

---

#### Level 3：结构层（Structural）

特征：
- 能指出：
  - 哪个是整体
  - 哪个是差量
  - 哪个保持不变

诊断信号：
- 能画条形图
- 能说“是速度差决定时间”

---

#### Level 4：迁移层（Transfer）

特征：
- 能跨情境识别同一图式
- 能从情境直接建模

诊断信号：
- 追及、流水、工程问题一眼看出是同一结构

---

### 4. 行为—图式映射诊断矩阵

| 学生行为 | 对应图式状态 |
|----------|--------------|
| 随机拖动 | 未建模 |
| 有目标调参 | 局部建模 |
| 先预测再验证 | 结构理解 |
| 主动构造模型 | 迁移掌握 |

---

### 5. 在 HTML Skill 中的实时诊断指标

每个交互动作都映射为：

```json
{
  "schema": "Rate_Convergence",
  "action": "adjust_speed_difference",
  "prediction_before_action": true,
  "invariant_mentioned": "same_time",
  "level": "Structural"
}
系统动态更新：
Schema Mastery Vector:
[Perceptual, Operational, Structural, Transfer]
6. 典型图式的诊断任务设计（示例：追及图式）
任务 1：感知
“哪辆车在缩小距离？”
任务 2：操作
调节速度，使追上时间缩短一半。
任务 3：结构
不用公式，说出“时间由哪两个量决定？”
任务 4：迁移
给出流水问题，让学生指出对应的“速度差”和“距离差”。
7. 诊断报告输出格式（给教师 / 系统）
{
  "student_id": "S1023",
  "schema_profile": {
    "Rate_Convergence": {
      "level": "Structural",
      "misconceptions": ["confuses speed with distance"],
      "recommended_skill": "Rate_Difference_Explorer"
    },
    "Part_Whole": {
      "level": "Transfer"
    }
  }
}
