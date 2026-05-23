# mathlab · 轮式机器人数学融合互动教学

基于《轮式机器人数学融合教案（完整版）》开发的浏览器互动教学平台：拖拽 Blockly 积木控制虚拟机器人，在模拟中完成测距、转角、走图形、坐标导航等任务。

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
| 教案导航 | 小学 2–6 年级 26 课 + 初中 6 册 27 课 |
| 图形化编程 | 前进/后退/转向/速度/等待/循环/条件/数学运算 |
| 运动模拟 | 轨迹、网格、数轴、坐标格、角度基准、钟面计时 |
| 教学面板 | 目标、公式（MathJax）、挑战任务、示例程序 |

## 文件结构

```
index.html          # 主入口
css/shell.css       # 样式
js/curriculum.js    # 教案任务数据与场景配置
js/app.js           # Blockly + Canvas 模拟器
js/contest.js       # 课堂竞赛模式
docs/               # 教案文档与早期单文件版（归档）
```

## 使用说明

1. 选择学段 → 年级/册别 → 教学任务
2. 阅读右侧教学目标与挑战，点击「加载示例程序」或自行拖拽积木
3. 调整轮子直径、速度，点击「运行程序」或「一键演示」
4. 观察轨迹、距离、圈数与用时等实时数据

## 部署更新

修改本目录后需重新构建前端 Docker 镜像（仅 `restart` 不会生效）：

```bash
cd docker
docker compose -f docker-compose.prod.yml build --no-cache frontend
docker compose -f docker-compose.prod.yml up -d frontend
```

## 许可

见 [LICENSE](LICENSE)
