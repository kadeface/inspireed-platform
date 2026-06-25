# 轮式机器人数学融合教案（合并版）

## 元信息
- 生成时间：2026-06-12T09:23:47.566Z
- 总任务数：99
- 数据来源：`js/curriculum.js`
- 使用方式：按学段/专题查阅章节，任务 ID 可与 MathLab 页面联动（`?task=…`）。

## 目录

### 第一部分 小学阶段
- 1. 二年级（5 课）
- 2. 三年级（5 课）
- 3. 四年级（6 课）
- 4. 五年级（4 课）
- 5. 六年级（4 课）

### 第二部分 初中阶段
- 1. 七年级上册（4 课）
- 2. 七年级下册（5 课）
- 3. 八年级上册（4 课）
- 4. 八年级下册（7 课）
- 5. 九年级上册（5 课）
- 6. 九年级下册（6 课）

### 第三部分 专题课程
- 行程问题（3 课）
- 轮式机器人探秘函数图像（18 课）
- 轮式机器人路径规划（5 课）
- 轮式机器人探秘微积分（18 课）


## 第一部分 小学阶段

### 第1章 二年级

#### 1.1 任务1：机器人测距员——长度单位的认识

- 任务 ID：`p2t1`
- 学段键：`primary`
- 章节键：`2`
- 章节名：二年级
- 单元：长度单位
- 场景：`distance`
- mode：`regular`
- 教学聚焦：估算 → 测量 → 编程 → 验证
- 提示：使用「前进」积木，距离填厘米数。100cm=1米。
- demo：`forward100`
- 标签：
- 厘米
- 米
- 单位换算
- 教学目标：
- 建立 1cm、1m 的长度表象
- 理解 1米=100厘米
- 编程让机器人走指定距离并验证
- 挑战任务：
- 让机器人走 100 cm（1米）
- 让机器人走 50 cm
- 让机器人走 120 cm
- 数学公式：
- 单位换算: $$1\text{ m} = 100\text{ cm}$$
- 轮子周长: $$C = \pi d \approx 9.42\text{ cm}$$（d=3）
- **`sceneConfig`**：
```json
{
  "markers": [
    30,
    50,
    100,
    120
  ],
  "unit": "cm"
}
```

- **`starter`**：
```json
{
  "forward": 100
}
```

---

#### 1.2 任务2：机器人转转转——角的初步认识

- 任务 ID：`p2t2`
- 学段键：`primary`
- 章节键：`2`
- 章节名：二年级
- 单元：角的初步认识
- 场景：`angle`
- mode：`regular`
- 教学聚焦：角的大小看张口，与边长短无关
- 提示：用「右转/左转」积木输入角度，90° 为直角。
- demo：`turn90`
- 标签：
- 直角
- 锐角
- 钝角
- 教学目标：
- 认识角的顶点与边
- 辨认直角、锐角、钝角
- 编程转出指定角度
- 挑战任务：
- 右转 90°（直角）
- 右转 45°（锐角）
- 右转 120°（钝角）
- 数学公式：
- 角分类: 锐角 $<90°$ · 直角 $=90°$ · 钝角 $>90°$
- **`sceneConfig`**：
```json
{
  "showCross": true
}
```

- **`starter`**：
```json
{
  "turns": [
    {
      "dir": "right",
      "deg": 90
    }
  ]
}
```

---

#### 1.3 任务3：机器人时钟——认识时间

- 任务 ID：`p2t3`
- 学段键：`primary`
- 章节键：`2`
- 章节名：二年级
- 单元：认识时间
- 场景：`time`
- mode：`regular`
- 教学聚焦：1时=60分，分针走1格=5分
- 提示：「等待」积木的单位是秒，可配合前进模拟指针运动。
- demo：`waitDemo`
- 标签：
- 时
- 分
- 钟面
- 教学目标：
- 认识钟面与指针
- 理解时、分的关系
- 用等待积木模拟时间流逝
- 挑战任务：
- 等待 3 秒（模拟分针走一小格）
- 等待 5 秒
- 前进+等待组合动作
- 数学公式：
- 时间: $$1\text{时} = 60\text{分}$$
- **`starter`**：
```json
{
  "wait": 3,
  "forward": 30
}
```

---

#### 1.4 任务4：机器人走图形——图形的运动（一）

- 任务 ID：`p2t4`
- 学段键：`primary`
- 章节键：`2`
- 章节名：二年级
- 单元：图形的运动
- 场景：`shape`
- mode：`regular`
- 教学聚焦：走图形 = 平移 + 旋转的组合
- 提示：重复 4 次：前进 → 右转 90°。
- demo：`square40`
- 标签：
- 平移
- 旋转
- 正方形
- 教学目标：
- 理解平移与旋转
- 让机器人走正方形路线
- 认识封闭图形
- 挑战任务：
- 走边长 40cm 的正方形
- 走边长 30cm 的正方形
- 数学公式：
- 正方形周长: $$C = 4a$$
- 走图形: 平移 + 旋转
- **`sceneConfig`**：
```json
{
  "shape": "square",
  "side": 40
}
```

- **`starter`**：
```json
{
  "repeat": 4,
  "forward": 40,
  "turn": 90
}
```

---

#### 1.5 任务5：机器人分糖果——有余数的除法

- 任务 ID：`p2t5`
- 学段键：`primary`
- 章节键：`2`
- 章节名：二年级
- 单元：有余数的除法
- 场景：`data`
- mode：`regular`
- 教学聚焦：总数 = 每份×份数 + 余数
- 提示：用「重复 3 次前进」模拟每份，最后一次单独前进表示余数。
- demo：`division17`
- 标签：
- 除法
- 余数
- 分配
- 教学目标：
- 理解除法与余数含义
- 17÷5=3…2 的分组模型
- 每份 3 颗余 2 颗
- 挑战任务：
- 编程：重复 3 次每次前进 20cm（分3份）
- 再走 20cm 表示余数部分
- 数学公式：
- 有余数除法: $$a = b \times q + r \quad (0 \le r < b)$$
- 本课实例: $$17 = 5 \times 3 + 2$$
- **`starter`**：
```json
{
  "repeat": 3,
  "forward": 20,
  "extraForward": 20
}
```

---

### 第2章 三年级

#### 2.1 任务6：机器人赛跑——时、分、秒

- 任务 ID：`p3t6`
- 学段键：`primary`
- 章节键：`3`
- 章节名：三年级
- 单元：时、分、秒
- 场景：`time`
- mode：`regular`
- 提示：先「设置速度」，再「前进」，观察用时差异。
- demo：`speedRace`
- 标签：
- 秒
- 时间换算
- 速度
- 教学目标：
- 掌握时、分、秒换算
- 比较不同速度到达同一距离的时间
- 理解 S=vt 雏形
- 挑战任务：
- 速度 10 走 50cm
- 速度 20 走 50cm（比较时间）
- 数学公式：
- 时间: $$1\text{分}=60\text{秒}$$
- 路程: $$S = v \times t$$
- **`starter`**：
```json
{
  "speed": 10,
  "forward": 50
}
```

---

#### 2.2 任务7：机器人精准测距——毫米、分米、千米

- 任务 ID：`p3t7`
- 学段键：`primary`
- 章节键：`3`
- 章节名：三年级
- 单元：测量
- 场景：`distance`
- mode：`regular`
- demo：`forward10`
- 标签：
- 毫米
- 分米
- 千米
- 教学目标：
- 认识 mm、dm、km
- 单位换算
- 精准控制距离
- 挑战任务：
- 走 10cm（1分米）
- 走 100cm（1米）
- 数学公式：
- 换算: $$1\text{dm}=10\text{cm},\;1\text{m}=10\text{dm}$$
- 千米: $$1\text{km}=1000\text{m}$$
- **`sceneConfig`**：
```json
{
  "markers": [
    10,
    100
  ]
}
```

- **`starter`**：
```json
{
  "forward": 10
}
```

---

#### 2.3 任务8：机器人走周长——长方形和正方形

- 任务 ID：`p3t8`
- 学段键：`primary`
- 章节键：`3`
- 章节名：三年级
- 单元：长方形和正方形
- 场景：`perimeter`
- mode：`regular`
- demo：`square30`
- 标签：
- 周长
- 长方形
- 正方形
- 教学目标：
- 理解周长含义
- 验证正方形 C=4a、长方形 C=2(a+b)
- 挑战任务：
- 走正方形周长 a=30cm（总 120cm）
- 走长方形 40×20cm 周长
- 数学公式：
- 正方形: $$C = 4a$$
- 长方形: $$C = 2(a+b)$$
- **`sceneConfig`**：
```json
{
  "rect": {
    "w": 40,
    "h": 20
  },
  "square": {
    "side": 30
  }
}
```

- **`starter`**：
```json
{
  "repeat": 4,
  "forward": 30,
  "turn": 90
}
```

---

#### 2.4 任务9：机器人导航员——位置与方向（一）

- 任务 ID：`p3t9`
- 学段键：`primary`
- 章节键：`3`
- 章节名：三年级
- 单元：位置与方向
- 场景：`path`
- mode：`regular`
- 提示：默认朝右（东），右转 90° 朝南。
- demo：`compass`
- 标签：
- 东
- 南
- 西
- 北
- 教学目标：
- 认识四个主方向
- 按方向指令走路线
- 描述行走路径
- 挑战任务：
- 向东走 50cm
- 右转后向南走 30cm
- 数学公式：
- 方向: 东 · 南 · 西 · 北
- 换向: 右转 $$90°$$ 换下一个主方向
- **`starter`**：
```json
{
  "forward": 50,
  "turn": 90,
  "forward2": 30
}
```

---

#### 2.5 任务10：机器人量面积——面积

- 任务 ID：`p3t10`
- 学段键：`primary`
- 章节键：`3`
- 章节名：三年级
- 单元：面积
- 场景：`grid`
- mode：`regular`
- demo：`areaRect`
- 标签：
- 面积
- 平方厘米
- 数格子
- 教学目标：
- 理解面积是面的大小
- 用单位正方形数面积
- 长方形面积=长×宽
- 挑战任务：
- 沿 3×2 格矩形走一圈
- 走 4×3 区域边界
- 数学公式：
- 长方形面积: $$S = a \times b$$
- **`sceneConfig`**：
```json
{
  "cols": 8,
  "rows": 5,
  "cellCm": 10
}
```

- **`starter`**：
```json
{
  "repeat": 2,
  "forward": 30,
  "turn": 90,
  "forward2": 20
}
```

---

### 第3章 四年级

#### 3.1 任务11：机器人转角度——角的度量

- 任务 ID：`p4t11`
- 学段键：`primary`
- 章节键：`4`
- 章节名：四年级
- 单元：角的度量
- 场景：`angle`
- mode：`regular`
- demo：`turn45`
- 标签：
- 度
- 量角
- 旋转
- 教学目标：
- 认识 1°
- 用量角器概念验证转角
- 精确转出 30°、45°、120°
- 挑战任务：
- 转 30°
- 转 45°
- 转 120°
- 数学公式：
- 周角: $$1\text{周角}=360°$$
- **`starter`**：
```json
{
  "turns": [
    {
      "dir": "right",
      "deg": 45
    }
  ]
}
```

---

#### 3.2 任务12：机器人走平行——平行四边形和梯形

- 任务 ID：`p4t12`
- 学段键：`primary`
- 章节键：`4`
- 章节名：四年级
- 单元：平行四边形和梯形
- 场景：`shape`
- mode：`regular`
- 提示：前进 50 → 转 60° → 前进 30 → 转 120°，对应平行四边形相邻两边。
- demo：`parallelogram`
- 标签：
- 平行
- 梯形
- 四边形
- 教学目标：
- 认识平行四边形、梯形
- 走平行四边形路径
- 理解对边平行
- 挑战任务：
- 走平行四边形周长路径
- 四段路程 50+30 对应相邻两边
- 数学公式：
- 平行: 平行四边形对边平行且相等
- 周长: $$C = 各边之和$$
- **`sceneConfig`**：
```json
{
  "shape": "parallelogram",
  "top": 50,
  "side": 30,
  "slant": 20
}
```

- **`starter`**：
```json
{
  "forward": 50,
  "turn": 60,
  "forward2": 30,
  "turn2": 120
}
```

---

#### 3.3 任务13：机器人最短路线——优化思想

- 任务 ID：`p4t13`
- 学段键：`primary`
- 章节键：`4`
- 章节名：四年级
- 单元：优化
- 场景：`path`
- mode：`regular`
- 提示：先走直线 80 cm；再设计折线，比较总路程。
- demo：`forward80`
- 标签：
- 最短路径
- 优化
- 教学目标：
- 比较不同路径长度
- 理解两点间线段最短
- 选择更优路线
- 挑战任务：
- 走直线 80cm
- 对比折线路径（需更长）
- 数学公式：
- 最短路径: 两点之间，线段最短
- **`starter`**：
```json
{
  "forward": 80
}
```

---

#### 3.4 任务14：机器人画三角形——三角形

- 任务 ID：`p4t14`
- 学段键：`primary`
- 章节键：`4`
- 章节名：四年级
- 单元：三角形
- 场景：`shape`
- mode：`regular`
- demo：`triangle`
- 标签：
- 三角形
- 内角
- 稳定性
- 教学目标：
- 走三角形路线
- 计算三边之和
- 认识三角形稳定性
- 挑战任务：
- 走等边三角形 a=40cm
- 数学公式：
- 等边三角形: $$C = 3a$$
- **`sceneConfig`**：
```json
{
  "shape": "triangle",
  "sides": [
    40,
    40,
    40
  ]
}
```

- **`starter`**：
```json
{
  "repeat": 3,
  "forward": 40,
  "turn": 120
}
```

---

#### 3.5 任务15：机器人走对称——图形的运动（二）

- 任务 ID：`p4t15`
- 学段键：`primary`
- 章节键：`4`
- 章节名：四年级
- 单元：图形的运动（二）
- 场景：`path`
- mode：`regular`
- 提示：L 形路径可看作沿对称轴的反射组合。
- demo：`symmetry`
- 标签：
- 轴对称
- 镜像
- 对称
- 教学目标：
- 理解轴对称
- 走对称路径
- 镜像运动
- 挑战任务：
- 走 L 形后沿对称轴返回
- 前进 50 + 转 90° + 前进 30
- 数学公式：
- 轴对称: 对应点到对称轴距离相等
- **`starter`**：
```json
{
  "forward": 50,
  "turn": 90,
  "forward2": 30
}
```

---

#### 3.6 任务16：机器人数据采集员——平均数与条形统计图

- 任务 ID：`p4t16`
- 学段键：`primary`
- 章节键：`4`
- 章节名：四年级
- 单元：平均数与统计图
- 场景：`data`
- mode：`regular`
- demo：`average`
- 标签：
- 平均数
- 统计
- 数据
- 教学目标：
- 收集多次行进距离
- 求平均数
- 理解数据波动
- 挑战任务：
- 走 3 次各 30cm 记录总距离
- 计算平均每次距离
- 数学公式：
- 平均数: $$\bar{x} = \frac{x_1+x_2+\cdots+x_n}{n}$$
- **`starter`**：
```json
{
  "repeat": 3,
  "forward": 30
}
```

---

### 第4章 五年级

#### 4.1 任务17：机器人定位棋——位置（数对）

- 任务 ID：`p5t17`
- 学段键：`primary`
- 章节键：`5`
- 章节名：五年级
- 单元：位置
- 场景：`grid`
- mode：`regular`
- 提示：目标 (3,2) 即 x=20 cm，y=10 cm；用「移动到 x y」。
- demo：`gridTarget32`
- 标签：
- 数对
- 列
- 行
- 平移
- 教学目标：
- 用数对 (列,行) 表示位置
- 从 (1,1) 走到 (3,2)
- 理解平移与数对变化
- 挑战任务：
- 从起点走到 (3,2)：右 2 格、上 1 格
- 走到 (4,3)
- 数学公式：
- 平移: 右移 $+\Delta列$，上移 $+\Delta行$
- **`sceneConfig`**：
```json
{
  "cols": 6,
  "rows": 6,
  "cellCm": 10,
  "target": [
    3,
    2
  ]
}
```

- **`starter`**：
```json
{
  "goto": {
    "x": 20,
    "y": 10
  }
}
```

---

#### 4.2 任务18：机器人走多边形——多边形的面积

- 任务 ID：`p5t18`
- 学段键：`primary`
- 章节键：`5`
- 章节名：五年级
- 单元：多边形的面积
- 场景：`shape`
- mode：`regular`
- 提示：重复 6 次：前进 25 → 左转 60°。
- demo：`hexagon`
- 标签：
- 多边形
- 面积
- 分割
- 教学目标：
- 走多边形边界
- 理解面积与周长区别
- 分割求面积思想
- 挑战任务：
- 走正六边形，边长 25cm
- 总路程 25×6=150 cm
- 数学公式：
- 正六边形: $$C = 6a$$
- **`sceneConfig`**：
```json
{
  "shape": "hexagon",
  "side": 25
}
```

- **`starter`**：
```json
{
  "repeat": 6,
  "forward": 25,
  "turn": 60
}
```

---

#### 4.3 任务19：机器人种树——植树问题

- 任务 ID：`p5t19`
- 学段键：`primary`
- 章节键：`5`
- 章节名：五年级
- 单元：植树问题
- 场景：`distance`
- mode：`regular`
- demo：`planting`
- 标签：
- 植树
- 间隔
- 两端都种
- 教学目标：
- 理解间隔数与棵数关系
- 两端都种：棵数=间隔+1
- 编程等距停顿
- 挑战任务：
- 100cm 每隔 20cm 停一次（共 6 棵）
- 数学公式：
- 两端都种: $$棵数 = 间隔数 + 1$$
- **`sceneConfig`**：
```json
{
  "markers": [
    20,
    40,
    60,
    80,
    100
  ],
  "plant": true
}
```

- **`starter`**：
```json
{
  "repeat": 5,
  "forward": 20,
  "wait": 0.5
}
```

---

#### 4.4 任务20：机器人编程解方程——简易方程

- 任务 ID：`p5t20`
- 学段键：`primary`
- 章节键：`5`
- 章节名：五年级
- 单元：简易方程
- 场景：`path`
- mode：`regular`
- demo：`equation`
- 标签：
- 方程
- 未知数
- 逆向
- 教学目标：
- 列简单方程
- x+5=12 求 x
- 逆向编程验证
- 挑战任务：
- 走 70cm 验证 x=7（每单位 10cm）
- 数学公式：
- 方程: $$x + 5 = 12 \Rightarrow x = 7$$
- **`starter`**：
```json
{
  "forward": 70
}
```

---

### 第5章 六年级

#### 5.1 任务23：机器人画圆——圆

- 任务 ID：`p6t23`
- 学段键：`primary`
- 章节键：`6`
- 章节名：六年级
- 单元：圆
- 场景：`circle`
- mode：`regular`
- demo：`oneLap`
- 标签：
- 圆
- 圆周率
- 周长
- 教学目标：
- 理解圆的周长 C=2πr
- 走圆周一段弧
- 体会 π 的意义
- 挑战任务：
- 前进 π×d ≈ 一圈（d=3 时约 9.4cm）
- 走 1/4 圆周
- 数学公式：
- 周长: $$C = 2\pi r = \pi d$$
- 面积: $$S = \pi r^2$$
- **`sceneConfig`**：
```json
{
  "radius": 40
}
```

- **`starter`**：
```json
{
  "forward": 9.42
}
```

---

#### 5.2 任务24：机器人导航2.0——位置与方向（二）

- 任务 ID：`p6t24`
- 学段键：`primary`
- 章节键：`6`
- 章节名：六年级
- 单元：位置与方向（二）
- 场景：`path`
- mode：`regular`
- 提示：右转 30° 后前进 60 cm，模拟北偏东方向行走。
- demo：`nav30`
- 标签：
- 北偏东
- 角度方向
- 导航
- 教学目标：
- 用角度描述方向
- 北偏东 30° 行走
- 综合导航
- 挑战任务：
- 转 30° 后走 60cm
- 数学公式：
- 方向角: 北偏东 $$30°$$
- 导航: 先转向，再沿该方向前进
- **`starter`**：
```json
{
  "turn": 30,
  "forward": 60
}
```

---

#### 5.3 任务25：机器人齿轮比——比

- 任务 ID：`p6t25`
- 学段键：`primary`
- 章节键：`6`
- 章节名：六年级
- 单元：比
- 场景：`data`
- mode：`regular`
- demo：`gearRatio`
- 标签：
- 比
- 齿轮
- 比例
- 教学目标：
- 理解比的意义
- 齿轮 2:1 转速关系
- 路程与圈数成比
- 挑战任务：
- 大轮走 1 圈，小轮走 2 圈（2:1）
- 数学公式：
- 比: $$a:b = \frac{a}{b}$$
- **`starter`**：
```json
{
  "forward": 18.84,
  "forward2": 9.42
}
```

---

#### 5.4 任务26：机器人比例尺地图——比例

- 任务 ID：`p6t26`
- 学段键：`primary`
- 章节键：`6`
- 章节名：六年级
- 单元：比例
- 场景：`grid`
- mode：`regular`
- demo：`scaleMap`
- 标签：
- 比例尺
- 地图
- 缩放
- 教学目标：
- 理解比例尺 1:100
- 图上 1cm 代表实际 100cm
- 按比例行走
- 挑战任务：
- 地图 3 格 = 实际 300cm，走 150cm
- 数学公式：
- 比例尺: $$1:100 = \frac{1\text{cm}}{100\text{cm}}$$
- **`sceneConfig`**：
```json
{
  "cols": 10,
  "rows": 6,
  "cellCm": 10,
  "scale": 100
}
```

- **`starter`**：
```json
{
  "forward": 150
}
```

---


## 第二部分 初中阶段

### 第1章 七年级上册

#### 1.1 任务1：数轴定位与有理数运算

- 任务 ID：`j7u1`
- 学段键：`junior`
- 章节键：`7u`
- 章节名：七年级上册
- 单元：有理数
- 场景：`numberline`
- mode：`regular`
- 提示：数轴上 1 个单位 = 20cm。先沿 → 前进 100cm（+5），再转 180° 朝 ← 前进 60cm（-3），最终停在 +2。
- demo：`numberlineRational`
- 标签：
- 数轴
- 有理数
- 加减
- 教学目标：
- 数轴三要素：原点、正方向、单位长度
- 沿正方向前进表示正数
- 转 180° 后前进表示负数（车头与移动方向一致）
- 验证 (+5)+(-3)=+2
- 挑战任务：
- 沿正方向前进 100cm（+5 个单位）
- 转 180° 后前进 60cm（-3 个单位），停在 +2
- 数学公式：
- 数轴: 原点 · 正方向 · 单位长度
- **`sceneConfig`**：
```json
{
  "min": -10,
  "max": 10,
  "unitCm": 20
}
```

- **`starter`**：
```json
{
  "forward": 100,
  "turn": 180,
  "forward2": 60
}
```

---

#### 1.2 任务2：行程方程解速度

- 任务 ID：`j7u2`
- 学段键：`junior`
- 章节键：`7u`
- 章节名：七年级上册
- 单元：一元一次方程
- 场景：`time`
- mode：`regular`
- demo：`forward100`
- 标签：
- 方程
- 速度
- S=vt
- 教学目标：
- 列行程方程
- 已知 S、t 求 v
- 编程验证
- 挑战任务：
- 100cm 用 10 秒，求速度 10cm/s
- 数学公式：
- 行程: $$S = v \times t$$
- **`starter`**：
```json
{
  "speed": 10,
  "forward": 100
}
```

---

#### 1.3 任务3：最短路径规划

- 任务 ID：`j7u3`
- 学段键：`junior`
- 章节键：`7u`
- 章节名：七年级上册
- 单元：几何初步
- 场景：`path`
- mode：`regular`
- demo：`forward100`
- 标签：
- 最短路径
- 线段
- 教学目标：
- 两点间线段最短
- 比较路径
- 优化选择
- 挑战任务：
- 直线走 100cm
- 数学公式：
- 最短路径: 两点之间，线段最短
- 比较: 折线长 $\ge$ 直线长
- **`starter`**：
```json
{
  "forward": 100
}
```

---

#### 1.4 任务4：机器人场地设计

- 任务 ID：`j7u4`
- 学段键：`junior`
- 章节键：`7u`
- 章节名：七年级上册
- 单元：几何图形
- 场景：`perimeter`
- mode：`regular`
- demo：`rect6040`
- 标签：
- 设计
- 周长
- 面积
- 教学目标：
- 设计矩形场地
- 计算周长与面积
- 编程走边界
- 数学公式：
- 周长: $$C = 2(a + b)$$
- 面积: $$S = a \times b$$
- **`sceneConfig`**：
```json
{
  "rect": {
    "w": 60,
    "h": 40
  }
}
```

- **`starter`**：
```json
{
  "repeat": 2,
  "forward": 60,
  "turn": 90,
  "forward2": 40,
  "turn2": 90
}
```

---

### 第2章 七年级下册

#### 2.1 任务5：垂直转弯与平行巡线

- 任务 ID：`j7d5`
- 学段键：`junior`
- 章节键：`7d`
- 章节名：七年级下册
- 单元：相交线与平行线
- 场景：`angle`
- mode：`regular`
- 提示：重复 4 次：前进 → 右转 90°，四直角合为周角。
- demo：`square40`
- 标签：
- 垂直
- 平行
- 90°
- 教学目标：
- 垂直=90°
- 平行线性质
- 直角转弯
- 挑战任务：
- 连续 4 次 90° 转弯
- 走完是否回到起始方向？
- 数学公式：
- 垂直: 两直线相交成 $$90°$$
- 周角: $$360° = 4 \times 90°$$
- **`starter`**：
```json
{
  "repeat": 4,
  "forward": 40,
  "turn": 90
}
```

---

#### 2.2 任务6：平移路径图案设计

- 任务 ID：`j7d6`
- 学段键：`junior`
- 章节键：`7d`
- 章节名：七年级下册
- 单元：平移
- 场景：`path`
- mode：`regular`
- 提示：每次「前进 30 → 转 90° → 前进 20」构成相同 L 形，体现平移重复。
- demo：`pattern`
- 标签：
- 平移
- 图案
- 教学目标：
- 平移性质
- 设计重复图案
- 坐标变化
- 挑战任务：
- 重复 3 次走 L 形路径
- 观察每次图案相同
- 数学公式：
- 平移: 形状、大小、方向不变
- 坐标: $$ (x,y) \to (x+a,\, y+b) $$
- **`starter`**：
```json
{
  "repeat": 3,
  "forward": 30,
  "turn": 90,
  "forward2": 20
}
```

---

#### 2.3 任务7：坐标系定位与导航

- 任务 ID：`j7d7`
- 学段键：`junior`
- 章节键：`7d`
- 章节名：七年级下册
- 单元：平面直角坐标系
- 场景：`grid`
- mode：`regular`
- 提示：目标 (4,3) 即 x=40 cm，y=30 cm；用「移动到 x y」。
- demo：`gridTarget43`
- 标签：
- 坐标
- 象限
- 导航
- 教学目标：
- 建立坐标系
- 用坐标定位
- 编程走到 (4,3)
- 挑战任务：
- 走到旗帜 (4,3)
- 读出终点坐标验证
- 数学公式：
- 坐标: $$(x,\, y)$$ 表示位置
- 格距: $$1\text{ 格} = 10\text{ cm}$$
- **`sceneConfig`**：
```json
{
  "cols": 8,
  "rows": 8,
  "cellCm": 10,
  "target": [
    4,
    3
  ]
}
```

- **`starter`**：
```json
{
  "goto": {
    "x": 40,
    "y": 30
  }
}
```

---

#### 2.4 任务8：坐标平移与编队运动

- 任务 ID：`j7d8`
- 学段键：`junior`
- 章节键：`7d`
- 章节名：七年级下册
- 单元：坐标变换
- 场景：`grid`
- mode：`regular`
- 提示：两次「移动到」：先 (40,0) 再 (40,30)，对应 a=40、b=30。
- demo：`translate`
- 标签：
- 平移
- 坐标
- 编队
- 教学目标：
- 坐标平移规律
- (x,y)→(x+a,y+b)
- 编队路径
- 挑战任务：
- 先平移 +40 cm（x 方向）
- 再平移 +30 cm（y 方向）
- 数学公式：
- 平移: $$ (x,y) \to (x+a,\, y+b) $$
- **`sceneConfig`**：
```json
{
  "cols": 8,
  "rows": 8,
  "cellCm": 10
}
```

- **`starter`**：
```json
{
  "goto": [
    {
      "x": 40,
      "y": 0
    },
    {
      "x": 40,
      "y": 30
    }
  ]
}
```

---

#### 2.5 任务9：速度与资源的方程求解

- 任务 ID：`j7d9`
- 学段键：`junior`
- 章节键：`7d`
- 章节名：七年级下册
- 单元：二元一次方程组
- 场景：`time`
- mode：`regular`
- 教学聚焦：本课重「列式→求解→代入验证」；双车相遇动画见行程专题 TV1
- 提示：先算 S_甲=10×4=40，S_乙=15×4=60；再「设速度→前进→改速度→再前进」。两车相向仿真请学「行程问题 · TV1」。
- demo：`equationVerify`
- 标签：
- 方程组
- 速度
- 验证
- 教学目标：
- 把相遇题抽象为方程组（如 v₁t=S₁，v₂t=S₂，S₁+S₂=S）
- 纸面求 S₁、S₂ 或 v₁、v₂
- 用分段速度/路程编程验证解（单轮模拟）
- 挑战任务：
- 全长 100 cm，t=4 s，v_甲=10、v_乙=15：求 S_甲、S_乙 并编程验证
- 运行后总路程是否等于 100 cm？
- 若 v_乙 改为 20，方程组的解如何变？
- 数学公式：
- 方程组: $$\begin{cases} v_1 t = S_1 \\ v_2 t = S_2 \\ S_1 + S_2 = S \end{cases}$$
- 路程: $$S = v \times t$$
- **`starter`**：
```json
{
  "speed": 10,
  "forward": 40,
  "speed2": 15,
  "forward2": 60
}
```

---

### 第3章 八年级上册

#### 3.1 任务10：三角形路径验证

- 任务 ID：`j8u10`
- 学段键：`junior`
- 章节键：`8u`
- 章节名：八年级上册
- 单元：三角形
- 场景：`shape`
- mode：`regular`
- 提示：重复 3 次：前进 50 → 左转 120°。
- demo：`triangle50`
- 标签：
- 三角形
- 三边关系
- 教学目标：
- 走三角形验证三边
- 两边之和大于第三边
- 挑战任务：
- 走边长 50 cm 的等边三角形
- 总路程是否 150 cm？
- 数学公式：
- 三边关系: $$a + b > c$$
- 周长: $$C = a + b + c$$
- **`starter`**：
```json
{
  "repeat": 3,
  "forward": 50,
  "turn": 120
}
```

---

#### 3.2 任务11：全等轨迹与距离测量

- 任务 ID：`j8u11`
- 学段键：`junior`
- 章节键：`8u`
- 章节名：八年级上册
- 单元：全等三角形
- 场景：`path`
- mode：`regular`
- 提示：走矩形两条不同顺序的邻边，对应边应相等（40 对 40，30 对 30）。
- demo：`congruent`
- 标签：
- 全等
- 对应边
- 教学目标：
- 走全等路径
- 对应边相等验证
- 挑战任务：
- 第一段 40+30，第二段 30+40
- 对应边是否相等？
- 数学公式：
- 全等: 对应边相等
- **`starter`**：
```json
{
  "forward": 40,
  "turn": 90,
  "forward2": 30,
  "turn2": 90,
  "forward3": 40
}
```

---

#### 3.3 任务12：对称路径运动

- 任务 ID：`j8u12`
- 学段键：`junior`
- 章节键：`8u`
- 章节名：八年级上册
- 单元：轴对称
- 场景：`path`
- mode：`regular`
- 提示：L 形路径可看作沿对称轴的反射组合。
- demo：`symmetry`
- 标签：
- 轴对称
- 对应点
- 教学目标：
- 轴对称性质
- 走对称路径
- 挑战任务：
- 先走 60 cm 再转 90° 走 40 cm
- 观察路径关于转角对称
- 数学公式：
- 轴对称: 对应点到对称轴距离相等
- **`starter`**：
```json
{
  "forward": 60,
  "turn": 90,
  "forward2": 40
}
```

---

#### 3.4 任务13：最短饮马路径

- 任务 ID：`j8u13`
- 学段键：`junior`
- 章节键：`8u`
- 章节名：八年级上册
- 单元：最短路径
- 场景：`path`
- mode：`regular`
- 提示：45° 转折模拟饮马问题的对称转化；直线距离 ≈ 50√2 cm。
- demo：`reflect`
- 标签：
- 反射
- 最短
- 教学目标：
- 饮马问题模型
- 对称转化最短路径
- 挑战任务：
- 转 45° 后走 50 cm
- 比较折线与直线距离
- 数学公式：
- 对称转化: 反射后走直线最短
- 最短: 两点之间，线段最短
- **`starter`**：
```json
{
  "forward": 50,
  "turn": 45,
  "forward2": 50
}
```

---

### 第4章 八年级下册

#### 4.1 任务14：距离测算与勾股定理

- 任务 ID：`j8d14`
- 学段键：`junior`
- 章节键：`8d`
- 章节名：八年级下册
- 单元：勾股定理
- 场景：`trig`
- mode：`regular`
- 教学聚焦：叠加层为 3-4-5 直角三角形；机器人路径沿三边行走
- 提示：沿叠加层：向 0° 走 30（a）→ 向 90° 走 40（b）→ 向 233° 走 50（c）闭合。
- demo：`pythagoras`
- 标签：
- 勾股定理
- a²+b²=c²
- 3-4-5
- 教学目标：
- 对照叠加层认识直角边 a、b 与斜边 c
- 沿 0°→90°→233° 走 30+40+50 cm 闭合路径
- 验证 30²+40²=50²
- 挑战任务：
- 沿 a→b→c 走完全程
- 口算验证 900+1600=2500
- 数学公式：
- 勾股定理: $$a^2 + b^2 = c^2$$
- 本课: $$30^2 + 40^2 = 50^2$$
- **`sceneConfig`**：
```json
{
  "cols": 10,
  "rows": 8,
  "cellCm": 10,
  "shape": "triangle",
  "sides": [
    30,
    40,
    50
  ],
  "trigTriangle": {
    "adjacent": 30,
    "opposite": 40,
    "mode": "pythagoras"
  }
}
```

- **`starter`**：
```json
{
  "move2d": [
    {
      "angle": 0,
      "dist": 30
    },
    {
      "angle": 90,
      "dist": 40
    },
    {
      "angle": 233.13,
      "dist": 50
    }
  ]
}
```

---

#### 4.2 任务15：圆柱面最短路径

- 任务 ID：`j8d15`
- 学段键：`junior`
- 章节键：`8d`
- 章节名：八年级下册
- 单元：展开图
- 场景：`path`
- mode：`regular`
- 提示：本课为抽象模型：折线模拟侧面路径；展开后直线为最短。
- demo：`cylinder`
- 标签：
- 展开
- 最短路径
- 教学目标：
- 圆柱侧面展开
- 最短路径转化
- 挑战任务：
- 走折线 80+50 cm
- 想象展开后直线更短
- 数学公式：
- 侧面展开: 圆柱侧面展开为矩形
- 最短路径: 展开后两点间线段最短
- **`starter`**：
```json
{
  "forward": 80,
  "turn": 90,
  "forward2": 50
}
```

---

#### 4.3 任务16：匀速运动的函数建模

- 任务 ID：`j8d16`
- 学段键：`junior`
- 章节键：`8d`
- 章节名：八年级下册
- 单元：一次函数
- 场景：`time`
- mode：`regular`
- demo：`linear`
- 标签：
- 一次函数
- s=vt
- 教学目标：
- s=vt 函数模型
- 匀速运动图象
- 斜率=速度
- 数学公式：
- 一次函数: $$s = vt + s_0$$
- **`starter`**：
```json
{
  "speed": 5,
  "forward": 100
}
```

---

#### 4.4 任务17：追及问题的图象分析

- 任务 ID：`j8d17`
- 学段键：`junior`
- 章节键：`8d`
- 章节名：八年级下册
- 单元：追及问题
- 场景：`time`
- mode：`regular`
- 教学聚焦：本课重「列式→求解→代入验证」；双车追及动画见行程专题 TV3
- 提示：先算 t=40÷(14-8)≈6.7 s，S_慢=8t≈54，S_快=14t≈94；再分段设速度前进。双车追及请学「行程问题 · TV3」。
- demo：`chaseVerify`
- 标签：
- 追及
- 函数图象
- 验证
- 教学目标：
- 把追及题抽象为方程（Δs=(v₂-v₁)t）
- 纸面求 t、S₁、S₂
- 用分段速度/路程编程验证解（单轮模拟）
- 挑战任务：
- 间距 40 cm，v_慢=8、v_快=14：求 t 与两车路程
- 运行后总路程是否等于 S_慢+S_快？
- 数学公式：
- 追及: $$t = \frac{\Delta s}{v_2 - v_1}$$
- 路程: $$S = v \times t$$
- **`starter`**：
```json
{
  "speed": 8,
  "forward": 54,
  "speed2": 14,
  "forward2": 94
}
```

---

#### 4.5 任务18：传感器数据统计分析

- 任务 ID：`j8d18`
- 学段键：`junior`
- 章节键：`8d`
- 章节名：八年级下册
- 单元：数据分析
- 场景：`data`
- mode：`regular`
- 提示：用「重复 5 次前进 30」模拟 5 次测量；运行后看总距离求平均。
- demo：`average`
- 标签：
- 统计
- 分析
- 教学目标：
- 多次测量
- 求平均与方差思想
- 数据可视化
- 挑战任务：
- 重复 5 次每次前进 30 cm
- 总距离 150 cm，平均每次 30 cm
- 数学公式：
- 平均数: $$\bar{x} = \frac{x_1 + x_2 + \cdots + x_n}{n}$$
- **`starter`**：
```json
{
  "repeat": 5,
  "forward": 30
}
```

---

#### 4.6 任务19：30°方向移动与 sin、cos

- 任务 ID：`j8d_trig1`
- 学段键：`junior`
- 章节键：`8d`
- 章节名：八年级下册
- 单元：三角函数入门
- 场景：`trig`
- mode：`regular`
- 教学聚焦：平面角 0°=东、90°=北；位移 x=r·cosθ，y=r·sinθ
- 提示：「向角度移动」填 30 与 20；或用 sin(30°)×20 算高度再编程。
- demo：`trig30`
- 标签：
- sin
- cos
- 特殊角
- 30°
- 教学目标：
- 理解 sin30°=1/2、cos30°=√3/2
- 用「向角度移动」走 30° 方向
- 用三角积木计算竖直分量 sin30°×20
- 挑战任务：
- 向 30° 移动 20 cm
- 用 sin30°×20 验证竖直约 10 cm
- 数学公式：
- 30°: $$\sin 30°=\frac{1}{2},\; \cos 30°=\frac{\sqrt{3}}{2}$$
- 位移分解: $$x=r\cos\theta,\; y=r\sin\theta$$
- **`sceneConfig`**：
```json
{
  "cols": 12,
  "rows": 8,
  "cellCm": 10,
  "trigTriangle": {
    "angle": 30,
    "hypotenuse": 20,
    "mode": "coords"
  }
}
```

- **`starter`**：
```json
{
  "move2d": {
    "angle": 30,
    "dist": 20
  }
}
```

---

#### 4.7 任务20：45°与 tan45°=1

- 任务 ID：`j8d_trig2`
- 学段键：`junior`
- 章节键：`8d`
- 章节名：八年级下册
- 单元：三角函数入门
- 场景：`trig`
- mode：`regular`
- 提示：tan45°=对边/邻边=1，故水平路程≈竖直路程。
- demo：`trig45`
- 标签：
- tan
- 45°
- 等腰直角三角形
- 教学目标：
- 认识 tan45°=1
- 45° 方向水平与竖直分量相等
- 走等腰直角三角形路线
- 挑战任务：
- 向 45° 移动 28 cm
- 水平、竖直分量各约 20 cm
- 数学公式：
- 45°: $$\tan 45° = 1,\; \sin 45°=\cos 45°=\frac{\sqrt{2}}{2}$$
- **`sceneConfig`**：
```json
{
  "trigTriangle": {
    "angle": 45,
    "adjacent": 20,
    "opposite": 20,
    "mode": "standard"
  }
}
```

- **`starter`**：
```json
{
  "move2d": [
    {
      "angle": 45,
      "dist": 28
    },
    {
      "angle": 0,
      "dist": 20
    },
    {
      "angle": 90,
      "dist": 20
    }
  ]
}
```

---

### 第5章 九年级上册

#### 5.1 任务19：圆形巡检路径设计

- 任务 ID：`j9u19`
- 学段键：`junior`
- 章节键：`9u`
- 章节名：九年级上册
- 单元：圆
- 场景：`circle`
- mode：`regular`
- 提示：1/4 圆周 L=πr/2≈78.5 cm（r=50）；可对照虚线圆验证。
- demo：`arcQuarter`
- 标签：
- 圆
- 巡检
- 周长
- 教学目标：
- 圆形路径巡检
- C=2πr 应用
- 挑战任务：
- 走 1/4 圆周（r=50 cm）
- 弧长约 78.5 cm
- 数学公式：
- 周长: $$C = 2\pi r$$
- 弧长: $$L = \frac{n\pi r}{180}$$
- **`sceneConfig`**：
```json
{
  "radius": 50
}
```

- **`starter`**：
```json
{
  "forward": 78.5
}
```

---

#### 5.2 任务20：转弯圆弧半径计算

- 任务 ID：`j9u20`
- 学段键：`junior`
- 章节键：`9u`
- 章节名：九年级上册
- 单元：圆
- 场景：`circle`
- mode：`regular`
- demo：`arc90`
- 标签：
- 弧长
- 半径
- 教学目标：
- 弧长公式 L=nπr/180
- 转弯半径计算
- 数学公式：
- 弧长: $$L = \frac{n\pi r}{180}$$
- **`starter`**：
```json
{
  "turn": 90,
  "forward": 40
}
```

---

#### 5.3 任务21：抛物线轨迹模拟

- 任务 ID：`j9u21`
- 学段键：`junior`
- 章节键：`9u`
- 章节名：九年级上册
- 单元：二次函数
- 场景：`path`
- mode：`regular`
- demo：`parabola`
- 标签：
- 抛物线
- 二次函数
- 教学目标：
- 理解抛物线轨迹
- 分段模拟 y=ax²
- 数学公式：
- 二次函数: $$y = ax^2 + bx + c$$
- **`starter`**：
```json
{
  "forward": 20,
  "turn": 30,
  "forward2": 25,
  "turn2": -30,
  "forward3": 20
}
```

---

#### 5.4 任务22：旋转后的坐标换算

- 任务 ID：`j9u22`
- 学段键：`junior`
- 章节键：`9u`
- 章节名：九年级上册
- 单元：旋转
- 场景：`grid`
- mode：`regular`
- 提示：先移动到 (40,0)，再移动到 (0,40)，对应旋转 90° 的坐标变换。
- demo：`rotate90`
- 标签：
- 旋转
- 坐标变换
- 教学目标：
- 绕原点旋转
- 坐标变换规律
- 挑战任务：
- (40,0) 绕原点转 90° 变为 (0,40)
- 用两次「移动到」验证
- 数学公式：
- 旋转 90°: $$ (x,y) \to (-y,\, x) $$
- **`sceneConfig`**：
```json
{
  "cols": 8,
  "rows": 8,
  "cellCm": 10
}
```

- **`starter`**：
```json
{
  "goto": [
    {
      "x": 40,
      "y": 0
    },
    {
      "x": 0,
      "y": 40
    }
  ]
}
```

---

#### 5.5 任务23：随机运行的概率实验

- 任务 ID：`j9u23`
- 学段键：`junior`
- 章节键：`9u`
- 章节名：九年级上册
- 单元：概率
- 场景：`data`
- mode：`regular`
- 提示：固定程序多次运行，统计右转次数，用频率估计概率。
- demo：`random`
- 标签：
- 概率
- 随机
- 频率
- 教学目标：
- 随机转向实验
- 频率估计概率
- 挑战任务：
- 重复 4 次：前进 20 → 转 90°
- 多次运行记录转向次数
- 数学公式：
- 频率: 频率 $\approx$ 概率（试验次数足够大时）
- **`starter`**：
```json
{
  "repeat": 4,
  "forward": 20,
  "turn": 90
}
```

---

### 第6章 九年级下册

#### 6.1 任务24：定程巡检的速度规划

- 任务 ID：`j9d24`
- 学段键：`junior`
- 章节键：`9d`
- 章节名：九年级下册
- 单元：函数应用
- 场景：`time`
- mode：`regular`
- 提示：同路程 30 cm，速度越大用时越短；用「设速度→前进」分三段。
- demo：`calcPiecewiseSpeed`
- 标签：
- 规划
- 速度
- 教学目标：
- 定路程变速度
- 时间规划
- 挑战任务：
- 三段各 30 cm，速度 5→10→15
- 比较各段用时
- 数学公式：
- 行程: $$S = v \times t$$
- 定程: 定 $S$ 则 $t = S / v$
- **`starter`**：
```json
{
  "speed": 5,
  "forward": 30,
  "speed2": 10,
  "forward2": 30,
  "speed3": 15,
  "forward3": 30
}
```

---

#### 6.2 任务25：视觉测距与相似

- 任务 ID：`j9d25`
- 学段键：`junior`
- 章节键：`9d`
- 章节名：九年级下册
- 单元：相似三角形
- 场景：`path`
- mode：`regular`
- demo：`similar`
- 标签：
- 相似
- 测距
- 教学目标：
- 相似比测距
- 比例计算
- 数学公式：
- 相似比: 对应边之比 $k$ 相等
- **`starter`**：
```json
{
  "forward": 60,
  "turn": 90,
  "forward2": 40
}
```

---

#### 6.3 任务26：坐标与 sin、cos

- 任务 ID：`j9d_trig1`
- 学段键：`junior`
- 章节键：`9d`
- 章节名：九年级下册
- 单元：锐角三角函数
- 场景：`trig`
- mode：`regular`
- 提示：用 cos(30°)×20、sin(30°)×20 积木算出坐标，再「移动到 x y」。
- demo：`trigGoto`
- 标签：
- sin
- cos
- 坐标
- 教学目标：
- 已知 r=20、θ=30°，求终点坐标
- 用 cosθ·r 与 sinθ·r 计算 x、y
- 编程移动到 (17.3, 10) 附近
- 挑战任务：
- 移动到 x≈17.3, y≈10
- 再向 90° 移动 10 cm
- 数学公式：
- 坐标: $$x=r\cos\theta,\; y=r\sin\theta$$
- 本课: $$x=20\cos30°\approx17.3,\; y=20\sin30°=10$$
- **`sceneConfig`**：
```json
{
  "cols": 12,
  "rows": 8,
  "cellCm": 10,
  "trigTriangle": {
    "angle": 30,
    "hypotenuse": 20,
    "mode": "coords"
  }
}
```

- **`starter`**：
```json
{
  "goto": {
    "x": 17.3,
    "y": 10
  }
}
```

---

#### 6.4 任务27：仰角测高度

- 任务 ID：`j9d_trig2`
- 学段键：`junior`
- 章节键：`9d`
- 章节名：九年级下册
- 单元：锐角三角函数
- 场景：`trig`
- mode：`regular`
- 提示：用「向角度移动」模拟仰角；tan(30°)×水平距离 算高度。
- demo：`elevation30`
- 标签：
- 仰角
- tan
- 测高
- 教学目标：
- 仰角 α 时高度 h=l·tanα
- 沿仰角方向前进模拟视线
- 理解 tan 为对边/邻边
- 挑战任务：
- 沿 30° 移动 40 cm
- 水平 40 cm 时高度 tan30°×40≈23 cm
- 数学公式：
- 仰角: $$h = l \cdot \tan\alpha$$
- 30°示例: $$h = 40 \times \tan 30° \approx 23.1\text{ cm}$$
- **`sceneConfig`**：
```json
{
  "trigTriangle": {
    "angle": 30,
    "adjacent": 40,
    "mode": "elevation"
  }
}
```

- **`starter`**：
```json
{
  "move2d": {
    "angle": 30,
    "dist": 40
  }
}
```

---

#### 6.5 任务28：坡度与角度测量

- 任务 ID：`j9d26`
- 学段键：`junior`
- 章节键：`9d`
- 章节名：九年级下册
- 单元：锐角三角函数
- 场景：`trig`
- mode：`regular`
- 提示：右转 15° 后前进；爬升≈tan(15°)×80≈21 cm。
- demo：`slope`
- 标签：
- 坡度
- tan
- 角度
- 教学目标：
- 坡度 i=tanα
- 水平路程 l 与高度 h 的关系 h=l·tanα
- 编程走斜坡路线
- 挑战任务：
- 先转 15° 再走 80 cm
- 用 tan15°×80 估算爬升高度
- 数学公式：
- 坡度: $$i = \tan\alpha = \frac{h}{l}$$
- **`sceneConfig`**：
```json
{
  "trigTriangle": {
    "angle": 15,
    "adjacent": 80,
    "mode": "slope"
  }
}
```

- **`starter`**：
```json
{
  "turn": 15,
  "forward": 80
}
```

---

#### 6.6 任务29：综合感知与自主规划

- 任务 ID：`j9d27`
- 学段键：`junior`
- 章节键：`9d`
- 章节名：九年级下册
- 单元：综合应用
- 场景：`path`
- mode：`regular`
- 提示：先定总路程与各段长度，再排顺序：前进→转弯→前进→转弯→前进。
- demo：`comprehensive`
- 标签：
- 综合
- 规划
- 项目
- 教学目标：
- 综合数学与编程
- 自主规划路径
- 完成任务目标
- 挑战任务：
- 设计一条包含 2 次转弯的总长 150 cm 路径
- 示例：50+50+50，两次 90° 转弯
- 数学公式：
- 路径长: $$L = s_1 + s_2 + \cdots + s_n$$
- **`starter`**：
```json
{
  "forward": 50,
  "turn": 90,
  "forward2": 50,
  "turn2": 90,
  "forward3": 50
}
```

---


## 第三部分 专题课程

### 行程问题


## 双车并行说明

本专题任务使用 **「当程序开始时（双车并行）」** 入口：在 **A 程序** / **B 程序** 槽分别编写甲、乙两车逻辑，运行后同时执行。
简单相向/同向场景可用「同时 A/B 前进」积木；**延迟出发**请在 B 槽使用「等待」后再前进。

#### 第1章 L4 基础追及

##### 1.1 TV3：同向追及

- 任务 ID：`tv_chase1`
- 学段键：`travel`
- 章节键：`chase_basic`
- 章节名：L4 基础追及
- 单元：行程问题
- 场景：`path`
- mode：`travel`
- travelSubtype：`chase`
- 提示：双车同向追及：A 槽写慢车前进、B 槽写快车前进，从 s-t 图读交点时刻。
- demo：`travelChase`
- 标签：
- 追及
- 速度差
- 教学目标：
- 理解追及核心是速度差
- 从 s-t 图读交点与追及时刻
- 数学公式：
- 追及: $$t=\frac{\Delta s}{v_2-v_1}$$
- **`sceneConfig`**：
```json
{
  "robots": [
    {
      "id": "A",
      "label": "慢车",
      "xCm": 0,
      "yCm": 0,
      "speed": 8,
      "color": "#22d3ee"
    },
    {
      "id": "B",
      "label": "快车",
      "xCm": -40,
      "yCm": 0,
      "speed": 14,
      "color": "#f97316"
    }
  ],
  "trackLengthCm": 120,
  "trackAxisDeg": 0,
  "chaseValidate": {
    "toleranceCm": 6
  },
  "stGraph": {
    "enabled": true,
    "tMaxSec": 20,
    "sMaxCm": 140,
    "showBoth": true
  }
}
```

- **`starter`**：
```json
{
  "travelParallel": [],
  "autoMeet": true
}
```

---

#### 第2章 L1 基础相遇

##### 2.1 TV1：两地相向而行（相遇）

- 任务 ID：`tv_meet1`
- 学段键：`travel`
- 章节键：`meet_basic`
- 章节名：L1 基础相遇
- 单元：行程问题
- 场景：`path`
- mode：`travel`
- travelSubtype：`meet`
- 提示：使用「双车并行」入口：A 槽写甲车前进、B 槽写乙车前进，运行后观察 s-t 图两线同时上升。
- demo：`travelMeet`
- 标签：
- 行程
- 相遇
- S=vt
- 教学目标：
- 理解相向而行总路程守恒
- 用双车并行仿真观察交点
- 用 s-t 图读出相遇时刻
- 数学公式：
- 相遇: $$t=\frac{S}{v_1+v_2}$$
- **`sceneConfig`**：
```json
{
  "robots": [
    {
      "id": "A",
      "label": "甲车",
      "xCm": 0,
      "yCm": 0,
      "speed": 10,
      "color": "#22d3ee"
    },
    {
      "id": "B",
      "label": "乙车",
      "xCm": 100,
      "yCm": 0,
      "speed": 15,
      "color": "#f97316",
      "face": 180
    }
  ],
  "trackLengthCm": 100,
  "trackAxisDeg": 0,
  "meetValidate": {
    "toleranceCm": 5
  },
  "stGraph": {
    "enabled": true,
    "tMaxSec": 10,
    "sMaxCm": 120,
    "showBoth": true
  }
}
```

- **`starter`**：
```json
{
  "travelParallel": [],
  "autoMeet": true
}
```

---

#### 第3章 L2 相遇变式

##### 3.1 TV2：乙车延迟出发

- 任务 ID：`tv_meet3`
- 学段键：`travel`
- 章节键：`meet_var`
- 章节名：L2 相遇变式
- 单元：行程问题
- 场景：`path`
- mode：`travel`
- travelSubtype：`meet`
- 提示：A 槽写甲车立即前进；B 槽先「等待 2 秒」再写乙车前进，模拟延迟出发。
- demo：`travelMeetDelay`
- 标签：
- 行程
- 延迟出发
- 教学目标：
- 理解非同时起步的相遇
- 能用程序表示“先后出发”
- 数学公式：
- 分段: $$S=v_1t_1+v_2t_2$$
- **`sceneConfig`**：
```json
{
  "robots": [
    {
      "id": "A",
      "label": "甲车",
      "xCm": 0,
      "yCm": 0,
      "speed": 12,
      "color": "#22d3ee"
    },
    {
      "id": "B",
      "label": "乙车",
      "xCm": 90,
      "yCm": 0,
      "speed": 18,
      "color": "#f97316",
      "face": 180
    }
  ],
  "trackLengthCm": 90,
  "trackAxisDeg": 0,
  "meetValidate": {
    "toleranceCm": 6
  },
  "stGraph": {
    "enabled": true,
    "tMaxSec": 14,
    "sMaxCm": 110,
    "showBoth": true
  }
}
```

- **`starter`**：
```json
{
  "travelDelayStart": {
    "waitSec": 2,
    "autoMeet": true
  }
}
```

---

### 轮式机器人探秘函数图像

#### 第1章 L0 数轴与对应

##### 1.1 数轴上的位置

- 任务 ID：`fg_l0_1`
- 学段键：`funcGraph`
- 章节键：`l0`
- 章节名：L0 数轴与对应
- 单元：数轴与对应
- 场景：`numberline`
- mode：`regular`
- series：`funcGraph`
- level：`L0`
- 提示：车头默认朝正方向 →。用「向角度 0° 移动」走正半轴；要走负半轴时「右转 180°」再「前进」，勿用后退（车头应与移动方向一致）。
- demo：`numberline`
- 标签：
- 数轴
- 位置
- 正方向
- 教学目标：
- 认识原点、正方向（→）与单位长度
- 沿正方向前进表示向正半轴移动
- 转 180° 后前进表示向负半轴移动
- 理解数与位置的一一对应
- 挑战任务：
- 沿正方向走到 +3
- 沿正方向走到 +7
- 转 180° 后走到 -2
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "min": -5,
  "max": 10,
  "unitCm": 20
}
```

- **`starter`**：
```json
{
  "forward": 60,
  "turn": 180,
  "forward2": 40
}
```

---

##### 1.2 步长与数列

- 任务 ID：`fg_l0_2`
- 学段键：`funcGraph`
- 章节键：`l0`
- 章节名：L0 数轴与对应
- 单元：数轴与对应
- 场景：`distance`
- mode：`regular`
- series：`funcGraph`
- level：`L0`
- demo：`forward10`
- 标签：
- 数列
- 重复
- 教学目标：
- 每次走相同步长
- 观察 5,10,15,20 的规律
- 挑战任务：
- 每次走 5 cm，重复 4 次
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`starter`**：
```json
{
  "repeat": 4,
  "forward": 5
}
```

---

##### 1.3 输入与输出

- 任务 ID：`fg_l0_3`
- 学段键：`funcGraph`
- 章节键：`l0`
- 章节名：L0 数轴与对应
- 单元：数轴与对应
- 场景：`distance`
- mode：`regular`
- series：`funcGraph`
- level：`L0`
- demo：`forward30`
- 标签：
- 对应关系
- 教学目标：
- 走 x 格记录终点
- 建立输入→输出直觉
- 挑战任务：
- 走 10、20、30 cm，记录总距离
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`starter`**：
```json
{
  "forward": 10,
  "forward2": 10,
  "forward3": 10
}
```

---

#### 第2章 L1 数对与比例

##### 2.1 数对定位

- 任务 ID：`fg_l1_1`
- 学段键：`funcGraph`
- 章节键：`l1`
- 章节名：L1 数对与比例
- 单元：数对与比例
- 场景：`grid`
- mode：`regular`
- series：`funcGraph`
- level：`L1`
- demo：`grid32`
- 标签：
- 坐标
- 数对
- 教学目标：
- 用 goto 走到 (2,3)、(4,6)
- 理解横纵坐标
- 挑战任务：
- 走到 (20,30) cm
- 走到 (40,60) cm
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "cols": 10,
  "rows": 8,
  "cellCm": 10
}
```

- **`starter`**：
```json
{
  "goto": [
    {
      "x": 20,
      "y": 30
    },
    {
      "x": 40,
      "y": 60
    }
  ]
}
```

---

##### 2.2 倍数关系

- 任务 ID：`fg_l1_2`
- 学段键：`funcGraph`
- 章节键：`l1`
- 章节名：L1 数对与比例
- 单元：数对与比例
- 场景：`grid`
- mode：`regular`
- series：`funcGraph`
- level：`L1`
- demo：`grid43`
- 标签：
- 正比例
- 倍数
- 教学目标：
- 走 (1,2)(2,4)(3,6) 对应点
- 发现 y=2x 关系
- 挑战任务：
- 依次走到 (10,20)(20,40)(30,60)
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "cols": 10,
  "rows": 10,
  "cellCm": 10
}
```

- **`starter`**：
```json
{
  "goto": [
    {
      "x": 10,
      "y": 20
    },
    {
      "x": 20,
      "y": 40
    },
    {
      "x": 30,
      "y": 60
    }
  ]
}
```

---

##### 2.3 正比例初探

- 任务 ID：`fg_l1_3`
- 学段键：`funcGraph`
- 章节键：`l1`
- 章节名：L1 数对与比例
- 单元：数对与比例
- 场景：`grid`
- mode：`regular`
- series：`funcGraph`
- level：`L1`
- 提示：轨迹点应落在 y=2x 参考线附近。
- demo：`grid43`
- 标签：
- y=2x
- 教学目标：
- 验证轨迹是否满足 y=2x
- 理解比例关系
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "cols": 12,
  "rows": 10,
  "cellCm": 10,
  "referenceLine": {
    "k": 2,
    "label": "y=2x"
  }
}
```

- **`starter`**：
```json
{
  "goto": [
    {
      "x": 10,
      "y": 20
    },
    {
      "x": 20,
      "y": 40
    },
    {
      "x": 30,
      "y": 60
    },
    {
      "x": 40,
      "y": 80
    }
  ]
}
```

---

#### 第3章 L2 直线世界

##### 3.1 描点成线

- 任务 ID：`fg_l2_1`
- 学段键：`funcGraph`
- 章节键：`l2`
- 章节名：L2 直线世界
- 单元：正比例
- 场景：`function`
- mode：`regular`
- series：`funcGraph`
- level：`L2`
- 提示：每个描点：停止绘制 → 移动到 (x,y) → 开始绘制；可切换 ● 点模式观察离散顶点。
- demo：`plotLinear`
- 标签：
- 描点
- 正比例
- 教学目标：
- 在 x=0,1,2,3 处描点
- 观察点连成直线
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "cols": 10,
  "rows": 10,
  "cellCm": 10,
  "plot": {
    "expr": "2*x",
    "xMin": 0,
    "xMax": 3,
    "step": 1,
    "color": "#38bdf8",
    "label": "y=2x"
  }
}
```

- **`starter`**：
```json
{
  "goto": [
    {
      "x": 0,
      "y": 0
    },
    {
      "x": 10,
      "y": 20
    },
    {
      "x": 20,
      "y": 40
    },
    {
      "x": 30,
      "y": 60
    }
  ]
}
```

- **`plotValidate`**：
```json
{
  "expr": "2*x",
  "toleranceCm": 1.5,
  "mode": "vertices"
}
```

---

##### 3.2 斜率 k 的意义

- 任务 ID：`fg_l2_2`
- 学段键：`funcGraph`
- 章节键：`l2`
- 章节名：L2 直线世界
- 单元：正比例
- 场景：`function`
- mode：`regular`
- series：`funcGraph`
- level：`L2`
- 提示：描 y=2x 上的点：停止绘制 → goto → 开始绘制；再与 y=x 参考线对比。
- demo：`plotLinear`
- 标签：
- 斜率
- 对比
- 教学目标：
- 比较 k=1 与 k=2 的图象
- 理解斜率越大越陡
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "cols": 10,
  "rows": 10,
  "cellCm": 10,
  "plots": [
    {
      "expr": "x",
      "xMin": 0,
      "xMax": 4,
      "step": 1,
      "color": "#38bdf8",
      "label": "y=x"
    },
    {
      "expr": "2*x",
      "xMin": 0,
      "xMax": 4,
      "step": 1,
      "color": "#f97316",
      "label": "y=2x"
    }
  ]
}
```

- **`starter`**：
```json
{
  "goto": [
    {
      "x": 0,
      "y": 0
    },
    {
      "x": 10,
      "y": 20
    },
    {
      "x": 20,
      "y": 40
    }
  ]
}
```

- **`plotValidate`**：
```json
{
  "expr": "2*x",
  "toleranceCm": 1.5,
  "mode": "vertices"
}
```

---

##### 3.3 过原点的直线

- 任务 ID：`fg_l2_3`
- 学段键：`funcGraph`
- 章节键：`l2`
- 章节名：L2 直线世界
- 单元：正比例
- 场景：`function`
- mode：`regular`
- series：`funcGraph`
- level：`L2`
- 提示：每个描点：停止绘制 → 移动到 (x,y) → 开始绘制。
- demo：`plotLinearSteep`
- 标签：
- y=kx
- 教学目标：
- 走 y=0.5x 与 y=3x 上的点
- 理解 k 改变倾斜程度
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "cols": 12,
  "rows": 10,
  "cellCm": 10,
  "plots": [
    {
      "expr": "0.5*x",
      "xMin": 0,
      "xMax": 4,
      "step": 1,
      "color": "#94a3b8",
      "label": "y=0.5x"
    },
    {
      "expr": "3*x",
      "xMin": 0,
      "xMax": 3,
      "step": 1,
      "color": "#f97316",
      "label": "y=3x"
    }
  ]
}
```

- **`starter`**：
```json
{
  "goto": [
    {
      "x": 0,
      "y": 0
    },
    {
      "x": 10,
      "y": 30
    },
    {
      "x": 20,
      "y": 60
    }
  ]
}
```

- **`plotValidate`**：
```json
{
  "expr": "3*x",
  "toleranceCm": 1.5,
  "mode": "vertices"
}
```

---

#### 第4章 L3 一次函数

##### 4.1 截距 b 的作用

- 任务 ID：`fg_l3_1`
- 学段键：`funcGraph`
- 章节键：`l3`
- 章节名：L3 一次函数
- 单元：一次函数
- 场景：`function`
- mode：`regular`
- series：`funcGraph`
- level：`L3`
- 提示：每个描点：停止绘制 → 移动到 (x,y) → 开始绘制。
- demo：`plotLinearIntercept`
- 标签：
- 截距
- y=2x+3
- 教学目标：
- 走 y=2x+3 上的点
- 观察直线不过原点
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "cols": 12,
  "rows": 10,
  "cellCm": 10,
  "plot": {
    "expr": "2*x+3",
    "xMin": 0,
    "xMax": 4,
    "step": 1,
    "color": "#38bdf8",
    "label": "y=2x+3"
  }
}
```

- **`starter`**：
```json
{
  "goto": [
    {
      "x": 0,
      "y": 30
    },
    {
      "x": 10,
      "y": 50
    },
    {
      "x": 20,
      "y": 70
    },
    {
      "x": 30,
      "y": 90
    }
  ]
}
```

- **`plotValidate`**：
```json
{
  "expr": "2*x+3",
  "toleranceCm": 1.5,
  "mode": "vertices"
}
```

---

##### 4.2 匀速 s-t 图

- 任务 ID：`fg_l3_2`
- 学段键：`funcGraph`
- 章节键：`l3`
- 章节名：L3 一次函数
- 单元：一次函数
- 场景：`time`
- mode：`regular`
- series：`funcGraph`
- level：`L3`
- 教学聚焦：函数图象专题：s=vt 是一次函数，s-t 图象为直线
- demo：`linear`
- 标签：
- s=vt
- s-t 图
- 教学目标：
- s=vt 函数模型
- 匀速运动图象
- 斜率=速度
- 数学公式：
- 一次函数: $$s = vt + s_0$$
- **`starter`**：
```json
{
  "speed": 5,
  "forward": 100
}
```

---

##### 4.3 追及与交点

- 任务 ID：`fg_l3_3`
- 学段键：`funcGraph`
- 章节键：`l3`
- 章节名：L3 一次函数
- 单元：一次函数
- 场景：`time`
- mode：`regular`
- series：`funcGraph`
- level：`L3`
- 教学聚焦：函数图象专题：追及问题对应两条 s-t 直线交点
- demo：`chase`
- 标签：
- 追及
- 交点
- 教学目标：
- 追及问题建模
- 速度差与时间
- 从图象读交点
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`starter`**：
```json
{
  "speed": 15,
  "forward": 60
}
```

---

#### 第5章 L4 二次函数

##### 5.1 抛物线描点

- 任务 ID：`fg_l4_1`
- 学段键：`funcGraph`
- 章节键：`l4`
- 章节名：L4 二次函数
- 单元：二次函数
- 场景：`function`
- mode：`regular`
- series：`funcGraph`
- level：`L4`
- 提示：每个描点：停止绘制 → 移动到 (x,y) → 开始绘制；勿用连续 goto 连线。
- demo：`plotParabola`
- 标签：
- 抛物线
- y=x²
- 教学目标：
- x=-2…2 描点 (x,x²)
- 认识抛物线形状
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "cols": 12,
  "rows": 12,
  "cellCm": 10,
  "plot": {
    "expr": "x*x",
    "xMin": -2,
    "xMax": 2,
    "step": 1,
    "color": "#a78bfa",
    "label": "y=x²"
  }
}
```

- **`starter`**：
```json
{
  "goto": [
    {
      "x": -20,
      "y": 40
    },
    {
      "x": -10,
      "y": 10
    },
    {
      "x": 0,
      "y": 0
    },
    {
      "x": 10,
      "y": 10
    },
    {
      "x": 20,
      "y": 40
    }
  ]
}
```

- **`plotValidate`**：
```json
{
  "expr": "x*x",
  "toleranceCm": 2,
  "mode": "vertices"
}
```

---

##### 5.2 参数 a 的影响

- 任务 ID：`fg_l4_2`
- 学段键：`funcGraph`
- 章节键：`l4`
- 章节名：L4 二次函数
- 单元：二次函数
- 场景：`function`
- mode：`regular`
- series：`funcGraph`
- level：`L4`
- 提示：每个描点：停止绘制 → 移动到 (x,y) → 开始绘制。
- demo：`plotParabola`
- 标签：
- 参数 a
- 教学目标：
- 对比 a=1、2、0.5 的开口
- 理解 |a| 越大越窄
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "cols": 12,
  "rows": 12,
  "cellCm": 10,
  "plots": [
    {
      "expr": "x*x",
      "xMin": -2,
      "xMax": 2,
      "step": 1,
      "color": "#38bdf8",
      "label": "y=x²"
    },
    {
      "expr": "2*x*x",
      "xMin": -2,
      "xMax": 2,
      "step": 1,
      "color": "#f97316",
      "label": "y=2x²"
    },
    {
      "expr": "0.5*x*x",
      "xMin": -2,
      "xMax": 2,
      "step": 1,
      "color": "#94a3b8",
      "label": "y=0.5x²"
    }
  ]
}
```

- **`starter`**：
```json
{
  "goto": [
    {
      "x": -20,
      "y": 40
    },
    {
      "x": 0,
      "y": 0
    },
    {
      "x": 20,
      "y": 40
    }
  ]
}
```

- **`plotValidate`**：
```json
{
  "expr": "x*x",
  "toleranceCm": 2,
  "mode": "vertices"
}
```

---

##### 5.3 顶点与对称轴

- 任务 ID：`fg_l4_3`
- 学段键：`funcGraph`
- 章节键：`l4`
- 章节名：L4 二次函数
- 单元：二次函数
- 场景：`function`
- mode：`regular`
- series：`funcGraph`
- level：`L4`
- 提示：每个描点：停止绘制 → 移动到 (x,y) → 开始绘制。
- demo：`plotParabolaShifted`
- 标签：
- 顶点
- 平移
- 教学目标：
- 走 y=(x-1)²+2 关键点
- 认识顶点与对称轴
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "cols": 12,
  "rows": 12,
  "cellCm": 10,
  "plot": {
    "expr": "(x-1)*(x-1)+2",
    "xMin": -1,
    "xMax": 3,
    "step": 1,
    "color": "#f472b6",
    "label": "y=(x-1)²+2"
  }
}
```

- **`starter`**：
```json
{
  "goto": [
    {
      "x": 0,
      "y": 30
    },
    {
      "x": 10,
      "y": 20
    },
    {
      "x": 20,
      "y": 30
    },
    {
      "x": 30,
      "y": 50
    }
  ]
}
```

- **`plotValidate`**：
```json
{
  "expr": "(x-1)*(x-1)+2",
  "toleranceCm": 2,
  "mode": "vertices"
}
```

---

#### 第6章 L5 拓展

##### 6.1 反比例 y=k/x

- 任务 ID：`fg_l5_1`
- 学段键：`funcGraph`
- 章节键：`l5`
- 章节名：L5 拓展
- 单元：反比例
- 场景：`function`
- mode：`regular`
- series：`funcGraph`
- level：`L5`
- 提示：x 取 2,4,5,8 等，算 y=20÷x；每点：停止绘制 → goto → 开始绘制。
- demo：`plotInverse`
- 标签：
- 反比例
- 双曲线
- 教学目标：
- 描点理解 y=20/x
- 观察两支曲线
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "cols": 12,
  "rows": 10,
  "cellCm": 10,
  "plot": {
    "expr": "20/x",
    "xMin": 2,
    "xMax": 8,
    "step": 1,
    "color": "#22d3ee",
    "label": "y=20/x"
  }
}
```

- **`starter`**：
```json
{
  "goto": [
    {
      "x": 20,
      "y": 10
    },
    {
      "x": 40,
      "y": 5
    },
    {
      "x": 50,
      "y": 4
    }
  ]
}
```

---

##### 6.2 分段函数

- 任务 ID：`fg_l5_2`
- 学段键：`funcGraph`
- 章节键：`l5`
- 章节名：L5 拓展
- 单元：分段函数
- 场景：`function`
- mode：`regular`
- series：`funcGraph`
- level：`L5`
- 提示：每个顶点：停止绘制 → goto → 开始绘制；段间自动断开，形成分段折线。
- demo：`plotPiecewise`
- 标签：
- 分段
- 折线
- 教学目标：
- 走折线路径
- 理解分段定义
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "cols": 12,
  "rows": 10,
  "cellCm": 10
}
```

- **`starter`**：
```json
{
  "goto": [
    {
      "x": 0,
      "y": 0
    },
    {
      "x": 20,
      "y": 20
    },
    {
      "x": 30,
      "y": 20
    },
    {
      "x": 50,
      "y": 0
    }
  ]
}
```

---

##### 6.3 延伸阅读：曲线巡逻与路径规划

- 任务 ID：`fg_l5_3`
- 学段键：`funcGraph`
- 章节键：`l5`
- 章节名：L5 拓展
- 单元：拓展
- 场景：`function`
- mode：`regular`
- series：`funcGraph`
- level：`L5`
- 教学聚焦：双车沿函数曲线拦截/伴随属于路径规划问题，已独立为专题课程
- 提示：课程抽屉 → 学段选「轮式机器人路径规划」→ 从 L1 开始；自由实验见 L4 实验室。
- demo：`plotLinear`
- 标签：
- 路径规划
- 双车
- 教学目标：
- 知道路径规划专题与函数图像专题的分工
- 在「轮式机器人路径规划」中可自定义 y=f(x) 并实验
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "cols": 12,
  "rows": 10,
  "cellCm": 10,
  "plot": {
    "expr": "2*x",
    "xMin": 0,
    "xMax": 4,
    "step": 1,
    "color": "#38bdf8",
    "label": "y=2x"
  }
}
```

- **`starter`**：
```json
{
  "goto": [
    {
      "x": 0,
      "y": 0
    },
    {
      "x": 20,
      "y": 40
    }
  ]
}
```

---

### 轮式机器人路径规划


## 双车并行说明

路径规划任务同样使用双槽入口：A 槽可放「曲线拦截演示」或沿曲线 goto；B 槽可放等待 + 直线 goto 至交汇点。
**相距同步**：「小车 B 等待直到与 A 相距小于 ε cm」——仅阻塞 B，A 可继续沿曲线运动。
拦截的关键是 **同时到达同一点**，勿将 A 的全部 goto 复制给 B。

#### 第1章 L1 曲线巡逻

##### 1.1 认识巡逻与拦截

- 任务 ID：`pp_l1_1`
- 学段键：`pathPlan`
- 章节键：`l1`
- 章节名：L1 曲线巡逻
- 单元：路径规划
- 场景：`function`
- mode：`curveTravel`
- travelSubtype：`meet`
- series：`pathPlan`
- level：`L1`
- 教学聚焦：路径规划 = 在已知曲线（y=f(x)）上安排两车运动，使相遇或伴随成立
- 提示：点「演示」：A 沿曲线到交汇点后继续循环；B 直线到交汇点。B 槽可用「等待直到与 A 相距小于 5 cm」替代固定秒数等待（不要复制 A 的全部 goto）。
- demo：`curveTravelMeet`
- 标签：
- 巡逻
- 拦截
- 路径规划
- 教学目标：
- 甲车沿 y=f(x) 循环巡逻（演示中先至交汇点，再继续绕圈）
- 乙车从起点直线驶向交汇点（不必与甲走同一条曲线）
- 理解拦截 = 同时到达同一点，而非两条相同轨迹
- 数学公式：
- 相遇: $$s_A(t)=s_{\text{曲}}(t),\quad |OB|=v_B t,\quad P_A(t)=P_B(t)$$
- **`sceneConfig`**：
```json
{
  "cols": 12,
  "rows": 10,
  "cellCm": 10,
  "userPlot": {
    "editable": true
  },
  "plot": {
    "expr": "2*x",
    "xMin": 0,
    "xMax": 4,
    "step": 1,
    "pathStep": 0.5,
    "color": "#38bdf8",
    "label": "y=2x"
  },
  "robots": [
    {
      "id": "A",
      "label": "巡逻车",
      "role": "patrol",
      "xCm": 0,
      "yCm": 0,
      "speed": 10,
      "color": "#22d3ee"
    },
    {
      "id": "B",
      "label": "拦截车",
      "role": "chaser",
      "xCm": 0,
      "yCm": 0,
      "speed": 12,
      "color": "#f97316"
    }
  ],
  "patrol": {
    "loop": true,
    "cycles": 2,
    "arcMeetFraction": 0.55
  },
  "curveMeetValidate": {
    "toleranceCm": 4
  },
  "stGraph": {
    "enabled": true,
    "tMaxSec": 18,
    "sMaxCm": 110,
    "showBoth": true
  }
}
```

- **`starter`**：
```json
{
  "curveTravelRun": true
}
```

---

#### 第2章 L2 一次与二次曲线

##### 2.1 一次函数曲线拦截

- 任务 ID：`pp_l2_1`
- 学段键：`pathPlan`
- 章节键：`l2`
- 章节名：L2 一次与二次曲线
- 单元：一次函数
- 场景：`function`
- mode：`curveTravel`
- travelSubtype：`meet`
- series：`pathPlan`
- level：`L2`
- demo：`curveTravelMeet`
- 标签：
- 一次函数
- 拦截
- y=kx+b
- 教学目标：
- 在直线型曲线上循环巡逻
- 从原点规划拦截
- 对比 s-t 图上两车路程
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "cols": 12,
  "rows": 10,
  "cellCm": 10,
  "userPlot": {
    "editable": true
  },
  "plot": {
    "expr": "2*x",
    "xMin": 0,
    "xMax": 4,
    "step": 1,
    "pathStep": 0.5,
    "color": "#38bdf8",
    "label": "y=2x"
  },
  "robots": [
    {
      "id": "A",
      "label": "巡逻车",
      "role": "patrol",
      "xCm": 0,
      "yCm": 0,
      "speed": 10,
      "color": "#22d3ee"
    },
    {
      "id": "B",
      "label": "拦截车",
      "role": "chaser",
      "xCm": 0,
      "yCm": 0,
      "speed": 12,
      "color": "#f97316"
    }
  ],
  "patrol": {
    "loop": true,
    "cycles": 1,
    "arcMeetFraction": 0.55
  },
  "curveMeetValidate": {
    "toleranceCm": 4
  },
  "stGraph": {
    "enabled": true,
    "tMaxSec": 18,
    "sMaxCm": 110,
    "showBoth": true
  }
}
```

- **`starter`**：
```json
{
  "curveTravelRun": true
}
```

---

##### 2.2 抛物线曲线拦截

- 任务 ID：`pp_l2_2`
- 学段键：`pathPlan`
- 章节键：`l2`
- 章节名：L2 一次与二次曲线
- 单元：二次函数
- 场景：`function`
- mode：`curveTravel`
- travelSubtype：`meet`
- series：`pathPlan`
- level：`L2`
- demo：`curveTravelMeet`
- 标签：
- 抛物线
- 拦截
- 教学目标：
- 曲率更大时弧长更长
- 体会拦截时间更难对齐
- 可改用自定义 y=ax²+bx+c
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "cols": 12,
  "rows": 12,
  "cellCm": 10,
  "userPlot": {
    "editable": true
  },
  "plot": {
    "expr": "x*x",
    "xMin": 0,
    "xMax": 2.5,
    "step": 0.5,
    "pathStep": 0.25,
    "color": "#a78bfa",
    "label": "y=x²"
  },
  "robots": [
    {
      "id": "A",
      "label": "巡逻车",
      "role": "patrol",
      "xCm": 0,
      "yCm": 0,
      "speed": 8,
      "color": "#22d3ee"
    },
    {
      "id": "B",
      "label": "拦截车",
      "role": "chaser",
      "xCm": 0,
      "yCm": 0,
      "speed": 11,
      "color": "#f97316"
    }
  ],
  "patrol": {
    "loop": true,
    "cycles": 1,
    "arcMeetFraction": 0.5
  },
  "curveMeetValidate": {
    "toleranceCm": 5
  },
  "stGraph": {
    "enabled": true,
    "tMaxSec": 20,
    "sMaxCm": 80,
    "showBoth": true
  }
}
```

- **`starter`**：
```json
{
  "curveTravelRun": true
}
```

---

#### 第3章 L3 伴随行走

##### 3.1 拦截后伴随

- 任务 ID：`pp_l3_1`
- 学段键：`pathPlan`
- 章节键：`l3`
- 章节名：L3 伴随行走
- 单元：伴随
- 场景：`function`
- mode：`curveTravel`
- travelSubtype：`companion`
- series：`pathPlan`
- level：`L3`
- demo：`curveTravelCompanion`
- 标签：
- 伴随
- 巡逻
- 教学目标：
- 先相遇再沿同曲线近距离跟随
- 观察轨迹重叠段
- 数学公式：
- 伴随: $$|P_A(t)-P_B(t)| \le \varepsilon$$
- **`sceneConfig`**：
```json
{
  "cols": 12,
  "rows": 10,
  "cellCm": 10,
  "userPlot": {
    "editable": true
  },
  "plot": {
    "expr": "2*x",
    "xMin": 0,
    "xMax": 3,
    "step": 1,
    "pathStep": 0.5,
    "color": "#38bdf8",
    "label": "y=2x"
  },
  "robots": [
    {
      "id": "A",
      "label": "巡逻车",
      "role": "patrol",
      "xCm": 0,
      "yCm": 0,
      "speed": 9,
      "color": "#22d3ee"
    },
    {
      "id": "B",
      "label": "伴随车",
      "role": "chaser",
      "xCm": 0,
      "yCm": 0,
      "speed": 9,
      "color": "#f97316"
    }
  ],
  "patrol": {
    "loop": true,
    "cycles": 1,
    "arcMeetFraction": 0.45
  },
  "companion": {
    "lagSec": 0.6
  },
  "companionValidate": {
    "toleranceCm": 3.5,
    "minOverlapSec": 2
  },
  "stGraph": {
    "enabled": true,
    "tMaxSec": 22,
    "sMaxCm": 100,
    "showBoth": true
  }
}
```

- **`starter`**：
```json
{
  "curveTravelRun": true,
  "curveTravelSubtype": "companion"
}
```

---

#### 第4章 L4 自定义实验室

##### 4.1 自定义曲线实验室

- 任务 ID：`pp_l4_1`
- 学段键：`pathPlan`
- 章节键：`l4`
- 章节名：L4 自定义实验室
- 单元：自由实验
- 场景：`function`
- mode：`curveTravel`
- travelSubtype：`meet`
- series：`pathPlan`
- level：`L4`
- 教学聚焦：教师/学生自行设定巡逻曲线，探索拦截能否成立
- 提示：可设 B 起点：例如曲线 y=2x+3 时把 B 放在 (0,0)、A 放在 (0,30)；或 B 从原点拦截曲线上的点。
- demo：`curveTravelMeet`
- 标签：
- 自定义
- 实验室
- y=f(x)
- 教学目标：
- 设定任意 y=f(x) 与定义域
- 调整两车速度后编程或演示
- 记录交汇条件是否满足
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "cols": 12,
  "rows": 12,
  "cellCm": 10,
  "userPlot": {
    "editable": true
  },
  "plot": {
    "expr": "2*x+3",
    "xMin": 0,
    "xMax": 3,
    "step": 1,
    "pathStep": 0.4,
    "color": "#22d3ee",
    "label": "y=2x+3"
  },
  "robots": [
    {
      "id": "A",
      "label": "巡逻车",
      "role": "patrol",
      "xCm": 0,
      "yCm": 30,
      "speed": 10,
      "color": "#22d3ee"
    },
    {
      "id": "B",
      "label": "拦截车",
      "role": "chaser",
      "xCm": 0,
      "yCm": 0,
      "speed": 12,
      "color": "#f97316"
    }
  ],
  "patrol": {
    "loop": true,
    "cycles": 1,
    "arcMeetFraction": 0.5
  },
  "curveMeetValidate": {
    "toleranceCm": 5
  },
  "stGraph": {
    "enabled": true,
    "tMaxSec": 25,
    "sMaxCm": 120,
    "showBoth": true
  }
}
```

- **`starter`**：
```json
{
  "curveTravelRun": true
}
```

---

### 轮式机器人探秘微积分

#### 第1章 L0 感受变化

##### 1.1 谁走得更快

- 任务 ID：`calc_l0_1`
- 学段键：`calculus`
- 章节键：`l0`
- 章节名：L0 感受变化
- 单元：感受变化
- 场景：`time`
- mode：`regular`
- series：`calculus`
- level：`L0`
- demo：`speedRace`
- 标签：
- 快慢
- 对比
- 教学目标：
- 同样时间比路程
- 建立「变化」直觉
- 挑战任务：
- 速度 10 走 5 秒 vs 速度 20 走 5 秒
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`starter`**：
```json
{
  "speed": 10,
  "forward": 50
}
```

---

##### 1.2 同样路程谁更久

- 任务 ID：`calc_l0_2`
- 学段键：`calculus`
- 章节键：`l0`
- 章节名：L0 感受变化
- 单元：感受变化
- 场景：`time`
- mode：`regular`
- series：`calculus`
- level：`L0`
- demo：`forward50`
- 标签：
- 时间
- 对比
- 教学目标：
- 固定 50 cm 比用时
- 理解速度与时间反比
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`starter`**：
```json
{
  "forward": 50
}
```

---

##### 1.3 先快后慢

- 任务 ID：`calc_l0_3`
- 学段键：`calculus`
- 章节键：`l0`
- 章节名：L0 感受变化
- 单元：感受变化
- 场景：`time`
- mode：`regular`
- series：`calculus`
- level：`L0`
- demo：`forward50`
- 标签：
- 分段速度
- 教学目标：
- 分段调速
- 感受运动状态变化
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`starter`**：
```json
{
  "speed": 20,
  "forward": 30,
  "speed2": 5,
  "forward2": 30
}
```

---

#### 第2章 L1 均匀变化

##### 2.1 每段多走一点

- 任务 ID：`calc_l1_1`
- 学段键：`calculus`
- 章节键：`l1`
- 章节名：L1 均匀变化
- 单元：均匀变化
- 场景：`distance`
- mode：`regular`
- series：`calculus`
- level：`L0`
- demo：`forward10`
- 标签：
- 递增
- 教学目标：
- 段长 10→15→20
- 观察变化规律
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`starter`**：
```json
{
  "forward": 10,
  "forward2": 15,
  "forward3": 20
}
```

---

##### 2.2 均匀加速初体验

- 任务 ID：`calc_l1_2`
- 学段键：`calculus`
- 章节键：`l1`
- 章节名：L1 均匀变化
- 单元：均匀变化
- 场景：`time`
- mode：`regular`
- series：`calculus`
- level：`L1`
- demo：`forward50`
- 标签：
- 加速
- 教学目标：
- 速度 5→10→15 各走一段
- 建立阶梯速度图直觉
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`starter`**：
```json
{
  "speed": 5,
  "forward": 20,
  "speed2": 10,
  "forward2": 20,
  "speed3": 15,
  "forward3": 20
}
```

---

##### 2.3 变化有没有规律

- 任务 ID：`calc_l1_3`
- 学段键：`calculus`
- 章节键：`l1`
- 章节名：L1 均匀变化
- 单元：均匀变化
- 场景：`data`
- mode：`regular`
- series：`calculus`
- level：`L1`
- demo：`forward10`
- 标签：
- 数据
- 教学目标：
- 多次运行记录距离
- 用数据发现规律
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`starter`**：
```json
{
  "repeat": 3,
  "forward": 20
}
```

---

#### 第3章 L2 斜率即速度

##### 3.1 s-t 图的斜率

- 任务 ID：`calc_l2_1`
- 学段键：`calculus`
- 章节键：`l2`
- 章节名：L2 斜率即速度
- 单元：斜率即速度
- 场景：`time`
- mode：`regular`
- series：`calculus`
- level：`L2`
- 教学聚焦：微积分专题：s-t 直线斜率 = 速度（包装匀速一次函数）
- demo：`linear`
- 标签：
- s-t
- 斜率
- s=vt
- 教学目标：
- s=vt 函数模型
- 匀速运动图象
- 斜率=速度
- 数学公式：
- 一次函数: $$s = vt$$
- **`sceneConfig`**：
```json
{
  "stGraph": {
    "enabled": true,
    "tMaxSec": 25,
    "sMaxCm": 120
  },
  "calcOverlay": {
    "type": "secant",
    "t0": 0,
    "t1": 5
  }
}
```

- **`starter`**：
```json
{
  "speed": 5,
  "forward": 100
}
```

- **`calcValidate`**：
```json
{
  "type": "slope",
  "t0": 0,
  "t1": 5,
  "expected": 5,
  "tolerance": 1
}
```

---

##### 3.2 不同斜率不同快

- 任务 ID：`calc_l2_2`
- 学段键：`calculus`
- 章节键：`l2`
- 章节名：L2 斜率即速度
- 单元：斜率即速度
- 场景：`time`
- mode：`regular`
- series：`calculus`
- level：`L2`
- 提示：先慢后快，观察 s-t 图两段斜率差异。
- demo：`calcTwoSpeed`
- 标签：
- 斜率
- 对比
- 教学目标：
- 速度 5 与 15 的 s-t 线对比
- 斜率越大走得越快
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "stGraph": {
    "enabled": true,
    "tMaxSec": 20,
    "sMaxCm": 90
  },
  "calcOverlay": {
    "type": "secant",
    "t0": 0,
    "t1": 4
  }
}
```

- **`starter`**：
```json
{
  "speed": 5,
  "forward": 40,
  "speed2": 15,
  "forward2": 40
}
```

---

##### 3.3 追及：速度差

- 任务 ID：`calc_l2_3`
- 学段键：`calculus`
- 章节键：`l2`
- 章节名：L2 斜率即速度
- 单元：斜率即速度
- 场景：`path`
- mode：`travel`
- travelSubtype：`chase`
- series：`calculus`
- level：`L2`
- 教学聚焦：微积分专题：追及对应 s-t 交点（包装追及问题）
- demo：`travelChase`
- 标签：
- 追及
- 交点
- 教学目标：
- 理解追及核心是速度差
- 从 s-t 图读交点与追及时刻
- 数学公式：
- 追及: $$t=\frac{\Delta s}{v_2-v_1}$$
- **`sceneConfig`**：
```json
{
  "robots": [
    {
      "id": "A",
      "label": "慢车",
      "xCm": 0,
      "yCm": 0,
      "speed": 8,
      "color": "#22d3ee"
    },
    {
      "id": "B",
      "label": "快车",
      "xCm": -40,
      "yCm": 0,
      "speed": 14,
      "color": "#f97316"
    }
  ],
  "trackLengthCm": 120,
  "trackAxisDeg": 0,
  "chaseValidate": {
    "toleranceCm": 6
  },
  "stGraph": {
    "enabled": true,
    "tMaxSec": 20,
    "sMaxCm": 140,
    "showBoth": true
  }
}
```

- **`starter`**：
```json
{
  "travelParallel": [],
  "autoMeet": true
}
```

---

#### 第4章 L3 非均匀变化

##### 4.1 变速运动

- 任务 ID：`calc_l3_1`
- 学段键：`calculus`
- 章节键：`l3`
- 章节名：L3 非均匀变化
- 单元：非均匀变化
- 场景：`calc`
- mode：`regular`
- series：`calculus`
- level：`L3`
- demo：`calcPiecewiseSpeed`
- 标签：
- 变速
- 分段
- 教学目标：
- 分段变速走完全程
- 观察 s-t 折线与 v-t 阶梯
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "stGraph": {
    "enabled": true,
    "tMaxSec": 30,
    "sMaxCm": 100
  },
  "vtGraph": {
    "enabled": true,
    "tMaxSec": 30,
    "vMax": 20
  }
}
```

- **`starter`**：
```json
{
  "speed": 5,
  "forward": 30,
  "speed2": 10,
  "forward2": 30,
  "speed3": 15,
  "forward3": 30
}
```

---

##### 4.2 分段走曲线

- 任务 ID：`calc_l3_2`
- 学段键：`calculus`
- 章节键：`l3`
- 章节名：L3 非均匀变化
- 单元：非均匀变化
- 场景：`calc`
- mode：`regular`
- series：`calculus`
- level：`L3`
- demo：`plotParabola`
- 标签：
- 折线逼近
- 教学目标：
- 用折线轨迹逼近抛物线
- 理解分段 vs 光滑
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "stGraph": {
    "enabled": true,
    "tMaxSec": 25,
    "sMaxCm": 80
  },
  "vtGraph": {
    "enabled": true,
    "tMaxSec": 25,
    "vMax": 25
  }
}
```

- **`starter`**：
```json
{
  "goto": [
    {
      "x": -20,
      "y": 40
    },
    {
      "x": -10,
      "y": 10
    },
    {
      "x": 0,
      "y": 0
    },
    {
      "x": 10,
      "y": 10
    },
    {
      "x": 20,
      "y": 40
    }
  ]
}
```

---

##### 4.3 分得越细越像

- 任务 ID：`calc_l3_3`
- 学段键：`calculus`
- 章节键：`l3`
- 章节名：L3 非均匀变化
- 单元：非均匀变化
- 场景：`calc`
- mode：`regular`
- series：`calculus`
- level：`L3`
- 提示：用多段相同小步长前进，观察 s-t 折线变密。
- demo：`calcFineSteps`
- 标签：
- 逼近
- 教学目标：
- 步长 10→5→2 分段前进
- 折线越来越像曲线
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "stGraph": {
    "enabled": true,
    "tMaxSec": 35,
    "sMaxCm": 60
  },
  "vtGraph": {
    "enabled": true,
    "tMaxSec": 35,
    "vMax": 20
  }
}
```

- **`starter`**：
```json
{
  "forward": 10,
  "forward2": 10,
  "forward3": 10,
  "forward4": 10,
  "forward5": 10,
  "forward6": 10
}
```

---

#### 第5章 L4 瞬时变化

##### 5.1 某一时刻多快

- 任务 ID：`calc_l4_1`
- 学段键：`calculus`
- 章节键：`l4`
- 章节名：L4 瞬时变化
- 单元：瞬时变化
- 场景：`calc`
- mode：`regular`
- series：`calculus`
- level：`L4`
- 标签：
- 平均速度
- 割线
- 教学目标：
- 取一小段算平均速度
- 理解割线斜率
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "stGraph": {
    "enabled": true,
    "tMaxSec": 20,
    "sMaxCm": 80
  },
  "vtGraph": {
    "enabled": true,
    "tMaxSec": 20,
    "vMax": 20
  },
  "calcOverlay": {
    "type": "secant",
    "t0": 2,
    "t1": 6
  }
}
```

- **`starter`**：
```json
{
  "speed": 10,
  "forward": 60
}
```

- **`calcValidate`**：
```json
{
  "type": "slope",
  "t0": 2,
  "t1": 6,
  "expected": 10,
  "tolerance": 1.5
}
```

---

##### 5.2 割线变切线

- 任务 ID：`calc_l4_2`
- 学段键：`calculus`
- 章节键：`l4`
- 章节名：L4 瞬时变化
- 单元：瞬时变化
- 场景：`calc`
- mode：`regular`
- series：`calculus`
- level：`L4`
- 提示：运行后对比 t0–t1 与更短区间的割线斜率。
- demo：`calcSecantNarrow`
- 标签：
- 割线
- 切线
- 教学目标：
- 缩小 Δt，观察割线斜率趋稳
- 感受瞬时变化率
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "stGraph": {
    "enabled": true,
    "tMaxSec": 15,
    "sMaxCm": 50
  },
  "calcOverlay": {
    "type": "secant",
    "t0": 4,
    "t1": 5
  }
}
```

- **`starter`**：
```json
{
  "speed": 8,
  "forward": 40
}
```

---

##### 5.3 导数直觉

- 任务 ID：`calc_l4_3`
- 学段键：`calculus`
- 章节键：`l4`
- 章节名：L4 瞬时变化
- 单元：瞬时变化
- 场景：`function`
- mode：`regular`
- series：`calculus`
- level：`L4`
- demo：`plotParabola`
- 标签：
- 抛物线
- 顶点
- 教学目标：
- 抛物线顶点处斜率为 0
- 割线→切线直觉
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "cols": 12,
  "rows": 12,
  "cellCm": 10,
  "plot": {
    "expr": "x*x",
    "xMin": -2,
    "xMax": 2,
    "step": 1,
    "color": "#a78bfa",
    "label": "y=x²"
  },
  "stGraph": {
    "enabled": true,
    "tMaxSec": 20,
    "sMaxCm": 50
  },
  "calcOverlay": {
    "type": "secant",
    "t0": -0.5,
    "t1": 0.5
  }
}
```

- **`starter`**：
```json
{
  "goto": [
    {
      "x": -10,
      "y": 10
    },
    {
      "x": 0,
      "y": 0
    },
    {
      "x": 10,
      "y": 10
    }
  ]
}
```

---

#### 第6章 L5 累积与面积

##### 6.1 v-t 与总路程

- 任务 ID：`calc_l5_1`
- 学段键：`calculus`
- 章节键：`l5`
- 章节名：L5 累积与面积
- 单元：累积与面积
- 场景：`calc`
- mode：`regular`
- series：`calculus`
- level：`L5`
- 标签：
- v-t
- 面积
- 教学目标：
- 矩形面积 = 路程
- 理解累积量
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "stGraph": {
    "enabled": true,
    "tMaxSec": 12,
    "sMaxCm": 120
  },
  "vtGraph": {
    "enabled": true,
    "tMaxSec": 12,
    "vMax": 15
  },
  "calcOverlay": {
    "type": "riemann",
    "t0": 0,
    "t1": 10,
    "n": 4
  }
}
```

- **`starter`**：
```json
{
  "speed": 10,
  "forward": 100
}
```

- **`calcValidate`**：
```json
{
  "type": "area",
  "t0": 0,
  "t1": 10,
  "n": 10,
  "expected": 100,
  "tolerance": 5
}
```

---

##### 6.2 变速：矩形逼近

- 任务 ID：`calc_l5_2`
- 学段键：`calculus`
- 章节键：`l5`
- 章节名：L5 累积与面积
- 单元：累积与面积
- 场景：`calc`
- mode：`regular`
- series：`calculus`
- level：`L5`
- 标签：
- 黎曼和
- 教学目标：
- 分段匀速，矩形求和
- 分得越细越准
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "stGraph": {
    "enabled": true,
    "tMaxSec": 25,
    "sMaxCm": 100
  },
  "vtGraph": {
    "enabled": true,
    "tMaxSec": 25,
    "vMax": 20
  },
  "calcOverlay": {
    "type": "riemann",
    "t0": 0,
    "t1": 10,
    "n": 5
  }
}
```

- **`starter`**：
```json
{
  "speed": 5,
  "forward": 20,
  "speed2": 10,
  "forward2": 20,
  "speed3": 15,
  "forward3": 20
}
```

- **`calcValidate`**：
```json
{
  "type": "area",
  "t0": 0,
  "t1": 8,
  "n": 8,
  "expected": 60,
  "tolerance": 20
}
```

---

##### 6.3 从 s 到 v 到面积

- 任务 ID：`calc_l5_3`
- 学段键：`calculus`
- 章节键：`l5`
- 章节名：L5 累积与面积
- 单元：累积与面积
- 场景：`calc`
- mode：`regular`
- series：`calculus`
- level：`L5`
- demo：`calcPiecewiseSpeed`
- 标签：
- 联动
- 综合
- 教学目标：
- s-t 斜率 ↔ v-t 面积
- 串联变化与累积
- 数学公式：
- 轮子周长: $$C = \pi \times d$$
- 行进距离: $$S = C \times n$$
- **`sceneConfig`**：
```json
{
  "stGraph": {
    "enabled": true,
    "tMaxSec": 20,
    "sMaxCm": 80
  },
  "vtGraph": {
    "enabled": true,
    "tMaxSec": 20,
    "vMax": 15
  },
  "calcOverlay": {
    "type": "riemann",
    "t0": 0,
    "t1": 8,
    "n": 4
  }
}
```

- **`starter`**：
```json
{
  "speed": 8,
  "forward": 64
}
```

---
