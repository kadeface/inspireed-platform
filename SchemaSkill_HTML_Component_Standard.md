# SchemaSkill → Interactive HTML Component Standard

## 1. 目标

定义一套标准接口，使 Claude Skill 输出的 Schema 能自动转化为：

- 可运行的 HTML5 交互组件
- 可嵌入教学平台的微型认知实验室
- 可组合成完整“概念探索环境”

实现：

Schema = 可执行结构  
Skill = 可运行认知模型

---

## 2. 总体架构

Claude Skill (Schema)
↓
Schema JSON
↓
Visualization Engine
↓
HTML Component
↓
Student Interaction
↓
Learning Analytics


---

## 3. 标准组件层级

### 3.1 Scene Layer（情境层）

```js
Scene {
  objects: [Car, Tank, Block, Person, Grid, Dice...],
  space: CoordinateSystem | AreaGrid | NumberLine,
  time: Timeline
}
HTML 实现：
Canvas / SVG
动态位置
物理约束（速度、填充、守恒）
3.2 Schema Overlay Layer（图式层）
统一支持五种核心图式可视化组件：
Schema	Component
Part–Whole	BarModel
Comparison	AlignedBars
Change	DynamicNumberLine
Rate	Distance-Time Strip
Proportion	AreaScalingGrid
Balance	EquationBalance
接口示例：
<SchemaOverlay type="BarModel" data={schemaData} />
3.3 Interaction Layer（操作层）
标准交互控件：
Control {
  type: Slider | Drag | Play | Step | Reset,
  bindTo: Variable
}
例如：
<Slider id="speedA" min="0" max="10" bind="carA.speed" />
3.4 Model Layer（数学结构层）
实时映射：
Model {
  variables: [x, y, t],
  relations: [x = vt, gap = x2 - x1],
  display: EquationPanel | Table | Graph
}
4. Skill 输出到组件的标准数据格式
4.1 Schema JSON
{
  "schema_type": "Rate_Convergence",
  "entities": ["CarA", "CarB"],
  "variables": {
    "vA": 60,
    "vB": 80,
    "gap": 40
  },
  "invariants": ["same_time"],
  "relations": ["gap(t) = gap0 - (vB - vA) * t"]
}
4.2 组件自动生成规则
Schema Type	自动加载组件
Part-Whole	BarModel + AreaGrid
Change	NumberLine + Timeline
Rate	MotionScene + DistanceBar
Proportion	ScalingGrid
Balance	ScaleBalance
5. HTML 组件模板（通用）
<SkillLab>
  <SceneCanvas />
  <SchemaOverlay />
  <ControlPanel />
  <ModelPanel />
  <InquiryGuide />
</SkillLab>
6. 学生操作与认知映射
每一次交互记录：
{
  "action": "drag",
  "object": "gap_bar",
  "cognitive_schema": "Difference",
  "understanding_level": "emerging"
}
用于：
图式掌握度评估
应用题理解诊断
AI 教学反馈
7. 与 Claude Skills 的对接协议
Claude Skill 输出必须遵循：
<SCHEMA>
<SCENE_MODEL>
<INTERACTION_RULES>
<INQUIRY_FLOW>
<HTML_COMPONENT_BINDINGS>
前端引擎读取后自动：
构建 Scene
渲染 Schema Overlay
绑定滑块与变量
同步方程变化
生成探究式提示