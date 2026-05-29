# mathlab · 轮式机器人数学融合互动教学

基于《轮式机器人数学融合教案（完整版）》开发的浏览器互动教学平台：拖拽 Blockly 积木控制虚拟机器人，在模拟中完成测距、转角、走图形、坐标导航、函数图象与微积分直觉等任务。

## 目录位置

静态资源唯一源码目录：`frontend/public/mathlab/`（Vite build 时会复制到 `dist/mathlab/`，Docker 生产环境由 Nginx 提供）。

## 本地预览

**方式一（推荐，与平台一致）**

```bash
cd frontend
pnpm dev
# 访问 http://localhost:5173/mathlab/index.html
```

**方式二（仅 mathlab 静态页）**

```bash
cd frontend/public/mathlab
python3 -m http.server 8080
# 访问 http://localhost:8080/index.html
```

## 功能概览

| 模块 | 说明 |
|------|------|
| 教案导航 | 小学 26 课 + 初中 27 课 + 行程问题 + **函数图像专题** + **微积分专题**（共 **93** 课） |
| 函数图像专题 `funcGraph` | L0–L5：数轴→坐标→`SCENE.FUNCTION` 曲线叠加、`plotValidate` 描点验证（17 课） |
| 微积分专题 `calculus` | L0–L5：变化直觉→`SCENE.CALC` 的 s-t / v-t 双图、割线、黎曼和（18 课） |
| 图形化编程 | 前进/后退/转向/速度/等待/循环/条件/数学运算 |
| 运动模拟 | 轨迹、网格、数轴、坐标格、函数曲线层、行程图 |
| 教学面板 | 目标、公式（MathJax）、挑战任务、专题导语、示例程序 |
| 课堂竞赛 | `?mode=contest&contestId=…&task=fg_l2_1`；支持专题 `taskId` |

## 深链示例

| 用途 | URL 参数 |
|------|----------|
| 函数图像 L2 描点 | `?task=fg_l2_1` |
| 微积分 L3 变速 | `?task=calc_l3_1` |
| 竞赛模式 | `?mode=contest&contestId=1&task=calc_l2_3` |

## 纯函数单测（Node）

```bash
node --test frontend/public/mathlab/tests/function-plot.test.js
node --test frontend/public/mathlab/tests/calc-graph.test.js
```

## 文件结构

```
index.html              # 主入口
css/shell.css           # 样式（含 s-t / v-t 图表面板）
js/curriculum.js        # 教案与专题任务数据、SCENE 常量
js/function-plot.js     # y=f(x) 采样与轨迹验证（ESM）
js/calc-graph.js        # 斜率、黎曼和（ESM）
js/app.js               # Blockly + Canvas 模拟器
js/contest.js           # 课堂竞赛模式
tests/                  # node --test 纯函数用例
docs/                   # 教案文档与早期单文件版（归档）
```

## 使用说明

1. 选择学段 → 年级/章节 → 教学任务（含「探秘函数图像」「探秘微积分」）
2. 阅读教学目标与专题导语，点击「加载示例程序」或自行拖拽积木
3. 调整轮子直径、速度，点击「运行程序」或「演示」
4. 函数专题：观察曲线叠加与 `plotValidate` 状态；微积分专题：观察 s-t、v-t 图与割线/矩形和

## 部署更新

修改本目录后需重新构建前端 Docker 镜像（仅 `restart` 不会生效）：

```bash
cd docker
docker compose -f docker-compose.prod.yml build --no-cache frontend
docker compose -f docker-compose.prod.yml up -d frontend
```

## 许可

见 [LICENSE](LICENSE)
