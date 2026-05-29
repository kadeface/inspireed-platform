/* 轮式机器人数学融合教案 — 任务数据（抽象自 轮式机器人数学融合教案_合并版.md） */
'use strict';

/** 场景模式：决定画布叠加层与验证逻辑 */
const SCENE = {
  DISTANCE: 'distance',       // 测距：距离标记线
  ANGLE: 'angle',             // 转角：十字基准 + 角度弧
  TIME: 'time',               // 时间：计时器
  SHAPE: 'shape',             // 走图形：目标多边形轮廓
  PERIMETER: 'perimeter',     // 周长：矩形/正方形边框
  GRID: 'grid',               // 数对坐标网格
  NUMBERLINE: 'numberline',   // 数轴（有理数）
  CIRCLE: 'circle',           // 圆周/圆弧
  PATH: 'path',               // 通用路径（默认）
  DATA: 'data',               // 数据统计面板
  TRIG: 'trig',               // 直角三角形叠加（邻边/对边/斜边、仰角/坡度）
  FUNCTION: 'function',       // y=f(x) 曲线叠加、描点验证
  CALC: 'calc'                // s-t / v-t 联动、割线、矩形和
};

const DEFAULT_FORMULAS = [
  { title: '轮子周长', tex: '$$C = \\pi \\times d$$' },
  { title: '行进距离', tex: '$$S = C \\times n$$' }
];

function task(id, title, unit, scene, extra) {
  return Object.assign({
    id, title, unit, scene,
    mode: extra?.mode || 'regular',
    travelSubtype: extra?.travelSubtype || null,
    tags: extra?.tags || [],
    goals: extra?.goals || [],
    focus: extra?.focus || '',
    formulas: extra?.formulas || DEFAULT_FORMULAS,
    challenges: extra?.challenges || [],
    hint: extra?.hint || '',
    sceneConfig: extra?.sceneConfig || {},
    starter: extra?.starter || null,
    demo: extra?.demo || null
  }, extra || {});
}

const CURRICULUM = {
  primary: {
    name: '小学阶段',
    grades: {
      2: {
        name: '二年级',
        tasks: [
          task('p2t1', '任务1：机器人测距员——长度单位的认识', '长度单位', SCENE.DISTANCE, {
            tags: ['厘米', '米', '单位换算'],
            goals: ['建立 1cm、1m 的长度表象', '理解 1米=100厘米', '编程让机器人走指定距离并验证'],
            focus: '估算 → 测量 → 编程 → 验证',
            formulas: [
              { title: '单位换算', tex: '$$1\\text{ m} = 100\\text{ cm}$$' },
              { title: '轮子周长', tex: '$$C = \\pi d \\approx 9.42\\text{ cm}$$（d=3）' }
            ],
            challenges: ['让机器人走 100 cm（1米）', '让机器人走 50 cm', '让机器人走 120 cm'],
            sceneConfig: { markers: [30, 50, 100, 120], unit: 'cm' },
            hint: '使用「前进」积木，距离填厘米数。100cm=1米。',
            starter: { forward: 100 },
            demo: 'forward100'
          }),
          task('p2t2', '任务2：机器人转转转——角的初步认识', '角的初步认识', SCENE.ANGLE, {
            tags: ['直角', '锐角', '钝角'],
            goals: ['认识角的顶点与边', '辨认直角、锐角、钝角', '编程转出指定角度'],
            focus: '角的大小看张口，与边长短无关',
            formulas: [{ title: '角分类', tex: '锐角 $<90°$ · 直角 $=90°$ · 钝角 $>90°$' }],
            challenges: ['右转 90°（直角）', '右转 45°（锐角）', '右转 120°（钝角）'],
            sceneConfig: { showCross: true },
            hint: '用「右转/左转」积木输入角度，90° 为直角。',
            starter: { turns: [{ dir: 'right', deg: 90 }] },
            demo: 'turn90'
          }),
          task('p2t3', '任务3：机器人时钟——认识时间', '认识时间', SCENE.TIME, {
            tags: ['时', '分', '钟面'],
            goals: ['认识钟面与指针', '理解时、分的关系', '用等待积木模拟时间流逝'],
            focus: '1时=60分，分针走1格=5分',
            formulas: [{ title: '时间', tex: '$$1\\text{时} = 60\\text{分}$$' }],
            challenges: ['等待 3 秒（模拟分针走一小格）', '等待 5 秒', '前进+等待组合动作'],
            hint: '「等待」积木的单位是秒，可配合前进模拟指针运动。',
            starter: { wait: 3, forward: 30 },
            demo: 'waitDemo'
          }),
          task('p2t4', '任务4：机器人走图形——图形的运动（一）', '图形的运动', SCENE.SHAPE, {
            tags: ['平移', '旋转', '正方形'],
            goals: ['理解平移与旋转', '让机器人走正方形路线', '认识封闭图形'],
            focus: '走图形 = 平移 + 旋转的组合',
            challenges: ['走边长 40cm 的正方形', '走边长 30cm 的正方形'],
            sceneConfig: { shape: 'square', side: 40 },
            hint: '重复 4 次：前进 → 右转 90°。',
            starter: { repeat: 4, forward: 40, turn: 90 },
            demo: 'square40'
          }),
          task('p2t5', '任务5：机器人分糖果——有余数的除法', '有余数的除法', SCENE.DATA, {
            tags: ['除法', '余数', '分配'],
            goals: ['理解除法与余数含义', '17÷5=3…2 的分组模型', '每份 3 颗余 2 颗'],
            focus: '总数 = 每份×份数 + 余数',
            formulas: [
              { title: '有余数除法', tex: '$$a = b \\times q + r \\quad (0 \\le r < b)$$' },
              { title: '本课实例', tex: '$$17 = 5 \\times 3 + 2$$' }
            ],
            challenges: ['编程：重复 3 次每次前进 20cm（分3份）', '再走 20cm 表示余数部分'],
            hint: '用「重复 3 次前进」模拟每份，最后一次单独前进表示余数。',
            starter: { repeat: 3, forward: 20, extraForward: 20 },
            demo: 'division17'
          })
        ]
      },
      3: {
        name: '三年级',
        tasks: [
          task('p3t6', '任务6：机器人赛跑——时、分、秒', '时、分、秒', SCENE.TIME, {
            tags: ['秒', '时间换算', '速度'],
            goals: ['掌握时、分、秒换算', '比较不同速度到达同一距离的时间', '理解 S=vt 雏形'],
            formulas: [
              { title: '时间', tex: '$$1\\text{分}=60\\text{秒}$$' },
              { title: '路程', tex: '$$S = v \\times t$$' }
            ],
            challenges: ['速度 10 走 50cm', '速度 20 走 50cm（比较时间）'],
            hint: '先「设置速度」，再「前进」，观察用时差异。',
            starter: { speed: 10, forward: 50 },
            demo: 'speedRace'
          }),
          task('p3t7', '任务7：机器人精准测距——毫米、分米、千米', '测量', SCENE.DISTANCE, {
            tags: ['毫米', '分米', '千米'],
            goals: ['认识 mm、dm、km', '单位换算', '精准控制距离'],
            formulas: [
              { title: '换算', tex: '$$1\\text{dm}=10\\text{cm},\\;1\\text{m}=10\\text{dm}$$' },
              { title: '千米', tex: '$$1\\text{km}=1000\\text{m}$$' }
            ],
            challenges: ['走 10cm（1分米）', '走 100cm（1米）'],
            sceneConfig: { markers: [10, 100] },
            starter: { forward: 10 },
            demo: 'forward10'
          }),
          task('p3t8', '任务8：机器人走周长——长方形和正方形', '长方形和正方形', SCENE.PERIMETER, {
            tags: ['周长', '长方形', '正方形'],
            goals: ['理解周长含义', '验证正方形 C=4a、长方形 C=2(a+b)'],
            formulas: [
              { title: '正方形', tex: '$$C = 4a$$' },
              { title: '长方形', tex: '$$C = 2(a+b)$$' }
            ],
            challenges: ['走正方形周长 a=30cm（总 120cm）', '走长方形 40×20cm 周长'],
            sceneConfig: { rect: { w: 40, h: 20 }, square: { side: 30 } },
            starter: { repeat: 4, forward: 30, turn: 90 },
            demo: 'square30'
          }),
          task('p3t9', '任务9：机器人导航员——位置与方向（一）', '位置与方向', SCENE.PATH, {
            tags: ['东', '南', '西', '北'],
            goals: ['认识四个主方向', '按方向指令走路线', '描述行走路径'],
            challenges: ['向东走 50cm', '右转后向南走 30cm'],
            hint: '默认朝右（东），右转 90° 朝南。',
            starter: { forward: 50, turn: 90, forward2: 30 },
            demo: 'compass'
          }),
          task('p3t10', '任务10：机器人量面积——面积', '面积', SCENE.GRID, {
            tags: ['面积', '平方厘米', '数格子'],
            goals: ['理解面积是面的大小', '用单位正方形数面积', '长方形面积=长×宽'],
            formulas: [{ title: '长方形面积', tex: '$$S = a \\times b$$' }],
            sceneConfig: { cols: 8, rows: 5, cellCm: 10 },
            challenges: ['沿 3×2 格矩形走一圈', '走 4×3 区域边界'],
            starter: { repeat: 2, forward: 30, turn: 90, forward2: 20 },
            demo: 'areaRect'
          })
        ]
      },
      4: {
        name: '四年级',
        tasks: [
          task('p4t11', '任务11：机器人转角度——角的度量', '角的度量', SCENE.ANGLE, {
            tags: ['度', '量角', '旋转'],
            goals: ['认识 1°', '用量角器概念验证转角', '精确转出 30°、45°、120°'],
            formulas: [{ title: '周角', tex: '$$1\\text{周角}=360°$$' }],
            challenges: ['转 30°', '转 45°', '转 120°'],
            starter: { turns: [{ dir: 'right', deg: 45 }] },
            demo: 'turn45'
          }),
          task('p4t12', '任务12：机器人走平行——平行四边形和梯形', '平行四边形和梯形', SCENE.SHAPE, {
            tags: ['平行', '梯形', '四边形'],
            goals: ['认识平行四边形、梯形', '走平行四边形路径', '理解对边平行'],
            sceneConfig: { shape: 'parallelogram', top: 50, side: 30, slant: 20 },
            challenges: ['走平行四边形周长路径'],
            starter: { forward: 50, turn: 60, forward2: 30, turn2: 120 },
            demo: 'parallelogram'
          }),
          task('p4t13', '任务13：机器人最短路线——优化思想', '优化', SCENE.PATH, {
            tags: ['最短路径', '优化'],
            goals: ['比较不同路径长度', '理解两点间线段最短', '选择更优路线'],
            challenges: ['走直线 80cm', '对比折线路径（需更长）'],
            starter: { forward: 80 },
            demo: 'forward80'
          }),
          task('p4t14', '任务14：机器人画三角形——三角形', '三角形', SCENE.SHAPE, {
            tags: ['三角形', '内角', '稳定性'],
            goals: ['走三角形路线', '计算三边之和', '认识三角形稳定性'],
            sceneConfig: { shape: 'triangle', sides: [40, 40, 40] },
            formulas: [{ title: '等边三角形', tex: '$$C = 3a$$' }],
            challenges: ['走等边三角形 a=40cm'],
            starter: { repeat: 3, forward: 40, turn: 120 },
            demo: 'triangle'
          }),
          task('p4t15', '任务15：机器人走对称——图形的运动（二）', '图形的运动（二）', SCENE.PATH, {
            tags: ['轴对称', '镜像', '对称'],
            goals: ['理解轴对称', '走对称路径', '镜像运动'],
            challenges: ['走 L 形后沿对称轴返回'],
            starter: { forward: 50, turn: 90, forward2: 30 },
            demo: 'symmetry'
          }),
          task('p4t16', '任务16：机器人数据采集员——平均数与条形统计图', '平均数与统计图', SCENE.DATA, {
            tags: ['平均数', '统计', '数据'],
            goals: ['收集多次行进距离', '求平均数', '理解数据波动'],
            formulas: [{ title: '平均数', tex: '$$\\bar{x} = \\frac{x_1+x_2+\\cdots+x_n}{n}$$' }],
            challenges: ['走 3 次各 30cm 记录总距离', '计算平均每次距离'],
            starter: { repeat: 3, forward: 30 },
            demo: 'average'
          })
        ]
      },
      5: {
        name: '五年级',
        tasks: [
          task('p5t17', '任务17：机器人定位棋——位置（数对）', '位置', SCENE.GRID, {
            tags: ['数对', '列', '行', '平移'],
            goals: ['用数对 (列,行) 表示位置', '从 (1,1) 走到 (3,2)', '理解平移与数对变化'],
            formulas: [{ title: '平移', tex: '右移 $+\\Delta列$，上移 $+\\Delta行$' }],
            sceneConfig: { cols: 6, rows: 6, cellCm: 10, target: [3, 2] },
            challenges: ['从起点走到 (3,2)：右 2 格、上 1 格', '走到 (4,3)'],
            hint: '每格 10cm。先前进 20cm（2列），左转 90°，再前进 10cm（1行）。',
            starter: { forward: 20, turn: 90, forward2: 10 },
            demo: 'grid32'
          }),
          task('p5t18', '任务18：机器人走多边形——多边形的面积', '多边形的面积', SCENE.SHAPE, {
            tags: ['多边形', '面积', '分割'],
            goals: ['走多边形边界', '理解面积与周长区别', '分割求面积思想'],
            sceneConfig: { shape: 'hexagon', side: 25 },
            challenges: ['走正六边形，边长 25cm'],
            starter: { repeat: 6, forward: 25, turn: 60 },
            demo: 'hexagon'
          }),
          task('p5t19', '任务19：机器人种树——植树问题', '植树问题', SCENE.DISTANCE, {
            tags: ['植树', '间隔', '两端都种'],
            goals: ['理解间隔数与棵数关系', '两端都种：棵数=间隔+1', '编程等距停顿'],
            formulas: [{ title: '两端都种', tex: '$$棵数 = 间隔数 + 1$$' }],
            sceneConfig: { markers: [20, 40, 60, 80, 100], plant: true },
            challenges: ['100cm 每隔 20cm 停一次（共 6 棵）'],
            starter: { repeat: 5, forward: 20, wait: 0.5 },
            demo: 'planting'
          }),
          task('p5t20', '任务20：机器人编程解方程——简易方程', '简易方程', SCENE.PATH, {
            tags: ['方程', '未知数', '逆向'],
            goals: ['列简单方程', 'x+5=12 求 x', '逆向编程验证'],
            formulas: [{ title: '方程', tex: '$$x + 5 = 12 \\Rightarrow x = 7$$' }],
            challenges: ['走 70cm 验证 x=7（每单位 10cm）'],
            starter: { forward: 70 },
            demo: 'equation'
          })
        ]
      },
      6: {
        name: '六年级',
        tasks: [
          task('p6t23', '任务23：机器人画圆——圆', '圆', SCENE.CIRCLE, {
            tags: ['圆', '圆周率', '周长'],
            goals: ['理解圆的周长 C=2πr', '走圆周一段弧', '体会 π 的意义'],
            formulas: [
              { title: '周长', tex: '$$C = 2\\pi r = \\pi d$$' },
              { title: '面积', tex: '$$S = \\pi r^2$$' }
            ],
            sceneConfig: { radius: 40 },
            challenges: ['前进 π×d ≈ 一圈（d=3 时约 9.4cm）', '走 1/4 圆周'],
            starter: { forward: 9.42 },
            demo: 'oneLap'
          }),
          task('p6t24', '任务24：机器人导航2.0——位置与方向（二）', '位置与方向（二）', SCENE.PATH, {
            tags: ['北偏东', '角度方向', '导航'],
            goals: ['用角度描述方向', '北偏东 30° 行走', '综合导航'],
            challenges: ['转 30° 后走 60cm'],
            starter: { turn: 30, forward: 60 },
            demo: 'nav30'
          }),
          task('p6t25', '任务25：机器人齿轮比——比', '比', SCENE.DATA, {
            tags: ['比', '齿轮', '比例'],
            goals: ['理解比的意义', '齿轮 2:1 转速关系', '路程与圈数成比'],
            formulas: [{ title: '比', tex: '$$a:b = \\frac{a}{b}$$' }],
            challenges: ['大轮走 1 圈，小轮走 2 圈（2:1）'],
            starter: { forward: 18.84, forward2: 9.42 },
            demo: 'gearRatio'
          }),
          task('p6t26', '任务26：机器人比例尺地图——比例', '比例', SCENE.GRID, {
            tags: ['比例尺', '地图', '缩放'],
            goals: ['理解比例尺 1:100', '图上 1cm 代表实际 100cm', '按比例行走'],
            formulas: [{ title: '比例尺', tex: '$$1:100 = \\frac{1\\text{cm}}{100\\text{cm}}$$' }],
            sceneConfig: { cols: 10, rows: 6, cellCm: 10, scale: 100 },
            challenges: ['地图 3 格 = 实际 300cm，走 150cm'],
            starter: { forward: 150 },
            demo: 'scaleMap'
          })
        ]
      }
    }
  },
  junior: {
    name: '初中阶段',
    grades: {
      '7u': {
        name: '七年级上册',
        tasks: [
          task('j7u1', '任务1：数轴定位与有理数运算', '有理数', SCENE.NUMBERLINE, {
            tags: ['数轴', '有理数', '加减'],
            goals: ['数轴三要素', '用前进/后退表示正负', '验证 (+5)+(-3)=+2'],
            formulas: [{ title: '数轴', tex: '原点 · 正方向 · 单位长度' }],
            sceneConfig: { min: -10, max: 10, unitCm: 20 },
            challenges: ['前进 100cm（+5 个单位）', '再后退 60cm（-3 个单位），停在 +2'],
            hint: '数轴上 1 个单位 = 20cm。前进 100cm = +5，后退 60cm = -3，最终停在 +2。',
            starter: { forward: 100, backward: 60 },
            demo: 'numberline'
          }),
          task('j7u2', '任务2：行程方程解速度', '一元一次方程', SCENE.TIME, {
            tags: ['方程', '速度', 'S=vt'],
            goals: ['列行程方程', '已知 S、t 求 v', '编程验证'],
            formulas: [{ title: '行程', tex: '$$S = v \\times t$$' }],
            challenges: ['100cm 用 10 秒，求速度 10cm/s'],
            starter: { speed: 10, forward: 100 },
            demo: 'forward100'
          }),
          task('j7u3', '任务3：最短路径规划', '几何初步', SCENE.PATH, {
            tags: ['最短路径', '线段'],
            goals: ['两点间线段最短', '比较路径', '优化选择'],
            challenges: ['直线走 100cm'],
            starter: { forward: 100 },
            demo: 'forward100'
          }),
          task('j7u4', '任务4：机器人场地设计', '几何图形', SCENE.PERIMETER, {
            tags: ['设计', '周长', '面积'],
            goals: ['设计矩形场地', '计算周长与面积', '编程走边界'],
            sceneConfig: { rect: { w: 60, h: 40 } },
            starter: { repeat: 2, forward: 60, turn: 90, forward2: 40, turn2: 90 },
            demo: 'rect6040'
          })
        ]
      },
      '7d': {
        name: '七年级下册',
        tasks: [
          task('j7d5', '任务5：垂直转弯与平行巡线', '相交线与平行线', SCENE.ANGLE, {
            tags: ['垂直', '平行', '90°'],
            goals: ['垂直=90°', '平行线性质', '直角转弯'],
            challenges: ['连续 4 次 90° 转弯'],
            starter: { repeat: 4, forward: 40, turn: 90 },
            demo: 'square40'
          }),
          task('j7d6', '任务6：平移路径图案设计', '平移', SCENE.PATH, {
            tags: ['平移', '图案'],
            goals: ['平移性质', '设计重复图案', '坐标变化'],
            starter: { repeat: 3, forward: 30, turn: 90, forward2: 20 },
            demo: 'pattern'
          }),
          task('j7d7', '任务7：坐标系定位与导航', '平面直角坐标系', SCENE.GRID, {
            tags: ['坐标', '象限', '导航'],
            goals: ['建立坐标系', '用坐标定位', '编程走到 (4,3)'],
            sceneConfig: { cols: 8, rows: 8, cellCm: 10, target: [4, 3] },
            starter: { forward: 30, turn: 90, forward2: 20 },
            demo: 'grid43'
          }),
          task('j7d8', '任务8：坐标平移与编队运动', '坐标变换', SCENE.GRID, {
            tags: ['平移', '坐标', '编队'],
            goals: ['坐标平移规律', '(x,y)→(x+a,y+b)', '编队路径'],
            sceneConfig: { cols: 8, rows: 8, cellCm: 10 },
            starter: { forward: 40, turn: 90, forward2: 30 },
            demo: 'translate'
          }),
          task('j7d9', '任务9：速度与资源的方程求解', '二元一次方程组', SCENE.TIME, {
            tags: ['方程组', '速度'],
            goals: ['列方程组', '相遇问题', '编程模拟'],
            formulas: [{ title: '相遇', tex: '$$S_1 + S_2 = S_{总}$$' }],
            starter: { forward: 50, turn: 180, forward2: 30 },
            demo: 'meet'
          })
        ]
      },
      '8u': {
        name: '八年级上册',
        tasks: [
          task('j8u10', '任务10：三角形路径验证', '三角形', SCENE.SHAPE, {
            tags: ['三角形', '三边关系'],
            goals: ['走三角形验证三边', '两边之和大于第三边'],
            starter: { repeat: 3, forward: 50, turn: 120 },
            demo: 'triangle50'
          }),
          task('j8u11', '任务11：全等轨迹与距离测量', '全等三角形', SCENE.PATH, {
            tags: ['全等', '对应边'],
            goals: ['走全等路径', '对应边相等验证'],
            starter: { forward: 40, turn: 90, forward2: 30, turn2: 90, forward3: 40 },
            demo: 'congruent'
          }),
          task('j8u12', '任务12：对称路径运动', '轴对称', SCENE.PATH, {
            tags: ['轴对称', '对应点'],
            goals: ['轴对称性质', '走对称路径'],
            starter: { forward: 60, turn: 90, forward2: 40 },
            demo: 'symmetry'
          }),
          task('j8u13', '任务13：最短饮马路径', '最短路径', SCENE.PATH, {
            tags: ['反射', '最短'],
            goals: ['饮马问题模型', '对称转化最短路径'],
            starter: { forward: 50, turn: 45, forward2: 50 },
            demo: 'reflect'
          })
        ]
      },
      '8d': {
        name: '八年级下册',
        tasks: [
          task('j8d14', '任务14：距离测算与勾股定理', '勾股定理', SCENE.TRIG, {
            tags: ['勾股定理', 'a²+b²=c²', '3-4-5'],
            goals: [
              '对照叠加层认识直角边 a、b 与斜边 c',
              '沿 0°→90°→233° 走 30+40+50 cm 闭合路径',
              '验证 30²+40²=50²'
            ],
            focus: '叠加层为 3-4-5 直角三角形；机器人路径沿三边行走',
            formulas: [
              { title: '勾股定理', tex: '$$a^2 + b^2 = c^2$$' },
              { title: '本课', tex: '$$30^2 + 40^2 = 50^2$$' }
            ],
            challenges: ['沿 a→b→c 走完全程', '口算验证 900+1600=2500'],
            sceneConfig: {
              cols: 10, rows: 8, cellCm: 10,
              shape: 'triangle', sides: [30, 40, 50],
              trigTriangle: { adjacent: 30, opposite: 40, mode: 'pythagoras' }
            },
            hint: '沿叠加层：向 0° 走 30（a）→ 向 90° 走 40（b）→ 向 233° 走 50（c）闭合。',
            starter: {
              move2d: [
                { angle: 0, dist: 30 },
                { angle: 90, dist: 40 },
                { angle: 233.13, dist: 50 }
              ]
            },
            demo: 'pythagoras'
          }),
          task('j8d15', '任务15：圆柱面最短路径', '展开图', SCENE.PATH, {
            tags: ['展开', '最短路径'],
            goals: ['圆柱侧面展开', '最短路径转化'],
            starter: { forward: 80, turn: 90, forward2: 50 },
            demo: 'cylinder'
          }),
          task('j8d16', '任务16：匀速运动的函数建模', '一次函数', SCENE.TIME, {
            tags: ['一次函数', 's=vt'],
            goals: ['s=vt 函数模型', '匀速运动图象', '斜率=速度'],
            formulas: [{ title: '一次函数', tex: '$$s = vt + s_0$$' }],
            starter: { speed: 5, forward: 100 },
            demo: 'linear'
          }),
          task('j8d17', '任务17：追及问题的图象分析', '追及问题', SCENE.TIME, {
            tags: ['追及', '函数图象'],
            goals: ['追及问题建模', '速度差与时间'],
            starter: { speed: 15, forward: 60 },
            demo: 'chase'
          }),
          task('j8d18', '任务18：传感器数据统计分析', '数据分析', SCENE.DATA, {
            tags: ['统计', '分析'],
            goals: ['多次测量', '求平均与方差思想', '数据可视化'],
            starter: { repeat: 5, forward: 30 },
            demo: 'average'
          }),
          task('j8d_trig1', '任务19：30°方向移动与 sin、cos', '三角函数入门', SCENE.TRIG, {
            tags: ['sin', 'cos', '特殊角', '30°'],
            goals: [
              '理解 sin30°=1/2、cos30°=√3/2',
              '用「向角度移动」走 30° 方向',
              '用三角积木计算竖直分量 sin30°×20'
            ],
            focus: '平面角 0°=东、90°=北；位移 x=r·cosθ，y=r·sinθ',
            formulas: [
              { title: '30°', tex: '$$\\sin 30°=\\frac{1}{2},\\; \\cos 30°=\\frac{\\sqrt{3}}{2}$$' },
              { title: '位移分解', tex: '$$x=r\\cos\\theta,\\; y=r\\sin\\theta$$' }
            ],
            challenges: ['向 30° 移动 20 cm', '用 sin30°×20 验证竖直约 10 cm'],
            sceneConfig: {
              cols: 12, rows: 8, cellCm: 10,
              trigTriangle: { angle: 30, hypotenuse: 20, mode: 'coords' }
            },
            hint: '「向角度移动」填 30 与 20；或用 sin(30°)×20 算高度再编程。',
            starter: { move2d: { angle: 30, dist: 20 } },
            demo: 'trig30'
          }),
          task('j8d_trig2', '任务20：45°与 tan45°=1', '三角函数入门', SCENE.TRIG, {
            tags: ['tan', '45°', '等腰直角三角形'],
            goals: ['认识 tan45°=1', '45° 方向水平与竖直分量相等', '走等腰直角三角形路线'],
            formulas: [
              { title: '45°', tex: '$$\\tan 45° = 1,\\; \\sin 45°=\\cos 45°=\\frac{\\sqrt{2}}{2}$$' }
            ],
            challenges: ['向 45° 移动 28 cm', '水平、竖直分量各约 20 cm'],
            sceneConfig: {
              trigTriangle: { angle: 45, adjacent: 20, opposite: 20, mode: 'standard' }
            },
            hint: 'tan45°=对边/邻边=1，故水平路程≈竖直路程。',
            starter: { move2d: [{ angle: 45, dist: 28 }, { angle: 0, dist: 20 }, { angle: 90, dist: 20 }] },
            demo: 'trig45'
          })
        ]
      },
      '9u': {
        name: '九年级上册',
        tasks: [
          task('j9u19', '任务19：圆形巡检路径设计', '圆', SCENE.CIRCLE, {
            tags: ['圆', '巡检', '周长'],
            goals: ['圆形路径巡检', 'C=2πr 应用'],
            sceneConfig: { radius: 50 },
            starter: { forward: 31.4 },
            demo: 'arcQuarter'
          }),
          task('j9u20', '任务20：转弯圆弧半径计算', '圆', SCENE.CIRCLE, {
            tags: ['弧长', '半径'],
            goals: ['弧长公式 L=nπr/180', '转弯半径计算'],
            formulas: [{ title: '弧长', tex: '$$L = \\frac{n\\pi r}{180}$$' }],
            starter: { turn: 90, forward: 40 },
            demo: 'arc90'
          }),
          task('j9u21', '任务21：抛物线轨迹模拟', '二次函数', SCENE.PATH, {
            tags: ['抛物线', '二次函数'],
            goals: ['理解抛物线轨迹', '分段模拟 y=ax²'],
            formulas: [{ title: '二次函数', tex: '$$y = ax^2 + bx + c$$' }],
            starter: { forward: 20, turn: 30, forward2: 25, turn2: -30, forward3: 20 },
            demo: 'parabola'
          }),
          task('j9u22', '任务22：旋转后的坐标换算', '旋转', SCENE.GRID, {
            tags: ['旋转', '坐标变换'],
            goals: ['绕原点旋转', '坐标变换规律'],
            starter: { turn: 90, forward: 40 },
            demo: 'rotate90'
          }),
          task('j9u23', '任务23：随机运行的概率实验', '概率', SCENE.DATA, {
            tags: ['概率', '随机', '频率'],
            goals: ['随机转向实验', '频率估计概率'],
            starter: { repeat: 4, forward: 20, turn: 90 },
            demo: 'random'
          })
        ]
      },
      '9d': {
        name: '九年级下册',
        tasks: [
          task('j9d24', '任务24：定程巡检的速度规划', '函数应用', SCENE.TIME, {
            tags: ['规划', '速度'],
            goals: ['定路程变速度', '时间规划'],
            starter: { forward: 100, speed: 8 },
            demo: 'forward100'
          }),
          task('j9d25', '任务25：视觉测距与相似', '相似三角形', SCENE.PATH, {
            tags: ['相似', '测距'],
            goals: ['相似比测距', '比例计算'],
            formulas: [{ title: '相似比', tex: '对应边之比 $k$ 相等' }],
            starter: { forward: 60, turn: 90, forward2: 40 },
            demo: 'similar'
          }),
          task('j9d_trig1', '任务26：坐标与 sin、cos', '锐角三角函数', SCENE.TRIG, {
            tags: ['sin', 'cos', '坐标'],
            goals: [
              '已知 r=20、θ=30°，求终点坐标',
              '用 cosθ·r 与 sinθ·r 计算 x、y',
              '编程移动到 (17.3, 10) 附近'
            ],
            formulas: [
              { title: '坐标', tex: '$$x=r\\cos\\theta,\\; y=r\\sin\\theta$$' },
              { title: '本课', tex: '$$x=20\\cos30°\\approx17.3,\\; y=20\\sin30°=10$$' }
            ],
            challenges: ['移动到 x≈17.3, y≈10', '再向 90° 移动 10 cm'],
            sceneConfig: {
              cols: 12, rows: 8, cellCm: 10,
              trigTriangle: { angle: 30, hypotenuse: 20, mode: 'coords' }
            },
            hint: '用 cos(30°)×20、sin(30°)×20 积木算出坐标，再「移动到 x y」。',
            starter: { goto: { x: 17.3, y: 10 } },
            demo: 'trigGoto'
          }),
          task('j9d_trig2', '任务27：仰角测高度', '锐角三角函数', SCENE.TRIG, {
            tags: ['仰角', 'tan', '测高'],
            goals: ['仰角 α 时高度 h=l·tanα', '沿仰角方向前进模拟视线', '理解 tan 为对边/邻边'],
            formulas: [
              { title: '仰角', tex: '$$h = l \\cdot \\tan\\alpha$$' },
              { title: '30°示例', tex: '$$h = 40 \\times \\tan 30° \\approx 23.1\\text{ cm}$$' }
            ],
            challenges: ['沿 30° 移动 40 cm', '水平 40 cm 时高度 tan30°×40≈23 cm'],
            sceneConfig: {
              trigTriangle: { angle: 30, adjacent: 40, mode: 'elevation' }
            },
            hint: '用「向角度移动」模拟仰角；tan(30°)×水平距离 算高度。',
            starter: { move2d: { angle: 30, dist: 40 } },
            demo: 'elevation30'
          }),
          task('j9d26', '任务28：坡度与角度测量', '锐角三角函数', SCENE.TRIG, {
            tags: ['坡度', 'tan', '角度'],
            goals: ['坡度 i=tanα', '水平路程 l 与高度 h 的关系 h=l·tanα', '编程走斜坡路线'],
            formulas: [{ title: '坡度', tex: '$$i = \\tan\\alpha = \\frac{h}{l}$$' }],
            challenges: ['先转 15° 再走 80 cm', '用 tan15°×80 估算爬升高度'],
            sceneConfig: {
              trigTriangle: { angle: 15, adjacent: 80, mode: 'slope' }
            },
            hint: '右转 15° 后前进；爬升≈tan(15°)×80≈21 cm。',
            starter: { turn: 15, forward: 80 },
            demo: 'slope'
          }),
          task('j9d27', '任务29：综合感知与自主规划', '综合应用', SCENE.PATH, {
            tags: ['综合', '规划', '项目'],
            goals: ['综合数学与编程', '自主规划路径', '完成任务目标'],
            challenges: ['设计一条包含 2 次转弯的总长 150cm 路径'],
            starter: { forward: 50, turn: 90, forward2: 50, turn2: 90, forward3: 50 },
            demo: 'comprehensive'
          })
        ]
      }
    }
  },
  travel: {
    name: '行程问题',
    grades: {
      meet_basic: {
        name: 'L1 基础相遇',
        tasks: [
          task('tv_meet1', 'TV1：两地相向而行（相遇）', '行程问题', SCENE.PATH, {
            mode: 'travel',
            travelSubtype: 'meet',
            tags: ['行程', '相遇', 'S=vt'],
            goals: ['理解相向而行总路程守恒', '用双车并行仿真观察交点', '用 s-t 图读出相遇时刻'],
            formulas: [{ title: '相遇', tex: '$$t=\\frac{S}{v_1+v_2}$$' }],
            sceneConfig: {
              robots: [
                { id: 'A', label: '甲车', xCm: 0, yCm: 0, speed: 10, color: '#22d3ee' },
                { id: 'B', label: '乙车', xCm: 100, yCm: 0, speed: 15, color: '#f97316', face: 180 }
              ],
              trackLengthCm: 100,
              trackAxisDeg: 0,
              meetValidate: { toleranceCm: 5 },
              stGraph: { enabled: true, tMaxSec: 10, sMaxCm: 120, showBoth: true }
            },
            starter: { travelParallel: [], autoMeet: true },
            demo: 'travelMeet'
          })
        ]
      },
      meet_var: {
        name: 'L2 相遇变式',
        tasks: [
          task('tv_meet3', 'TV2：乙车延迟出发', '行程问题', SCENE.PATH, {
            mode: 'travel',
            travelSubtype: 'meet',
            tags: ['行程', '延迟出发'],
            goals: ['理解非同时起步的相遇', '能用程序表示“先后出发”'],
            formulas: [{ title: '分段', tex: '$$S=v_1t_1+v_2t_2$$' }],
            sceneConfig: {
              robots: [
                { id: 'A', label: '甲车', xCm: 0, yCm: 0, speed: 12, color: '#22d3ee' },
                { id: 'B', label: '乙车', xCm: 90, yCm: 0, speed: 18, color: '#f97316', face: 180 }
              ],
              trackLengthCm: 90,
              trackAxisDeg: 0,
              meetValidate: { toleranceCm: 6 },
              stGraph: { enabled: true, tMaxSec: 14, sMaxCm: 110, showBoth: true }
            },
            starter: { travelDelayStart: { waitSec: 2, autoMeet: true } },
            demo: 'travelMeetDelay'
          })
        ]
      },
      chase_basic: {
        name: 'L4 基础追及',
        tasks: [
          task('tv_chase1', 'TV3：同向追及', '行程问题', SCENE.PATH, {
            mode: 'travel',
            travelSubtype: 'chase',
            tags: ['追及', '速度差'],
            goals: ['理解追及核心是速度差', '从 s-t 图读交点与追及时刻'],
            formulas: [{ title: '追及', tex: '$$t=\\frac{\\Delta s}{v_2-v_1}$$' }],
            sceneConfig: {
              robots: [
                { id: 'A', label: '慢车', xCm: 0, yCm: 0, speed: 8, color: '#22d3ee' },
                { id: 'B', label: '快车', xCm: -40, yCm: 0, speed: 14, color: '#f97316' }
              ],
              trackLengthCm: 120,
              trackAxisDeg: 0,
              chaseValidate: { toleranceCm: 6 },
              stGraph: { enabled: true, tMaxSec: 20, sMaxCm: 140, showBoth: true }
            },
            starter: { travelParallel: [], autoMeet: true },
            demo: 'travelChase'
          })
        ]
      }
    }
  },
  funcGraph: {
    name: '轮式机器人探秘函数图像',
    grades: {
      l0: {
        name: 'L0 数轴与对应',
        tasks: [
          task('fg_l0_1', '数轴上的位置', '数轴与对应', SCENE.NUMBERLINE, {
            series: 'funcGraph', level: 'L0',
            tags: ['数轴', '位置'],
            goals: ['在数轴上走到指定位置', '理解数与距离的一一对应'],
            sceneConfig: { min: -5, max: 10, unitCm: 20 },
            challenges: ['走到 +3', '走到 +7', '走到 -2'],
            hint: '用「沿当前朝向前进/后退」配合数轴刻度。',
            starter: { forward: 60, backward: 40 },
            demo: 'numberline'
          }),
          task('fg_l0_2', '步长与数列', '数轴与对应', SCENE.DISTANCE, {
            series: 'funcGraph', level: 'L0',
            tags: ['数列', '重复'],
            goals: ['每次走相同步长', '观察 5,10,15,20 的规律'],
            challenges: ['每次走 5 cm，重复 4 次'],
            starter: { repeat: 4, forward: 5 },
            demo: 'forward10'
          }),
          task('fg_l0_3', '输入与输出', '数轴与对应', SCENE.DISTANCE, {
            series: 'funcGraph', level: 'L0',
            tags: ['对应关系'],
            goals: ['走 x 格记录终点', '建立输入→输出直觉'],
            challenges: ['走 10、20、30 cm，记录总距离'],
            starter: { forward: 10, forward2: 10, forward3: 10 },
            demo: 'forward30'
          })
        ]
      },
      l1: {
        name: 'L1 数对与比例',
        tasks: [
          task('fg_l1_1', '数对定位', '数对与比例', SCENE.GRID, {
            series: 'funcGraph', level: 'L1',
            tags: ['坐标', '数对'],
            goals: ['用 goto 走到 (2,3)、(4,6)', '理解横纵坐标'],
            sceneConfig: { cols: 10, rows: 8, cellCm: 10 },
            challenges: ['走到 (20,30) cm', '走到 (40,60) cm'],
            starter: { goto: [{ x: 20, y: 30 }, { x: 40, y: 60 }] },
            demo: 'grid32'
          }),
          task('fg_l1_2', '倍数关系', '数对与比例', SCENE.GRID, {
            series: 'funcGraph', level: 'L1',
            tags: ['正比例', '倍数'],
            goals: ['走 (1,2)(2,4)(3,6) 对应点', '发现 y=2x 关系'],
            sceneConfig: { cols: 10, rows: 10, cellCm: 10 },
            challenges: ['依次走到 (10,20)(20,40)(30,60)'],
            starter: {
              goto: [{ x: 10, y: 20 }, { x: 20, y: 40 }, { x: 30, y: 60 }]
            },
            demo: 'grid43'
          }),
          task('fg_l1_3', '正比例初探', '数对与比例', SCENE.GRID, {
            series: 'funcGraph', level: 'L1',
            tags: ['y=2x'],
            goals: ['验证轨迹是否满足 y=2x', '理解比例关系'],
            sceneConfig: {
              cols: 12, rows: 10, cellCm: 10,
              referenceLine: { k: 2, label: 'y=2x' }
            },
            hint: '轨迹点应落在 y=2x 参考线附近。',
            starter: {
              goto: [{ x: 10, y: 20 }, { x: 20, y: 40 }, { x: 30, y: 60 }, { x: 40, y: 80 }]
            },
            demo: 'grid43'
          })
        ]
      },
      l2: {
        name: 'L2 直线世界',
        tasks: [
          task('fg_l2_1', '描点成线', '正比例', SCENE.FUNCTION, {
            series: 'funcGraph', level: 'L2',
            tags: ['描点', '正比例'],
            goals: ['在 x=0,1,2,3 处描点', '观察点连成直线'],
            sceneConfig: {
              cols: 10, rows: 10, cellCm: 10,
              plot: { expr: '2*x', xMin: 0, xMax: 3, step: 1, color: '#38bdf8', label: 'y=2x' }
            },
            plotValidate: { expr: '2*x', toleranceCm: 1.5 },
            starter: { goto: [{ x: 0, y: 0 }, { x: 10, y: 20 }, { x: 20, y: 40 }, { x: 30, y: 60 }] },
            demo: 'plotLinear'
          }),
          task('fg_l2_2', '斜率 k 的意义', '正比例', SCENE.FUNCTION, {
            series: 'funcGraph', level: 'L2',
            tags: ['斜率', '对比'],
            goals: ['比较 k=1 与 k=2 的图象', '理解斜率越大越陡'],
            sceneConfig: {
              cols: 10, rows: 10, cellCm: 10,
              plots: [
                { expr: 'x', xMin: 0, xMax: 4, step: 1, color: '#38bdf8', label: 'y=x' },
                { expr: '2*x', xMin: 0, xMax: 4, step: 1, color: '#f97316', label: 'y=2x' }
              ]
            },
            plotValidate: { expr: '2*x', toleranceCm: 1.5 },
            starter: { goto: [{ x: 0, y: 0 }, { x: 10, y: 20 }, { x: 20, y: 40 }] },
            hint: '先走 y=2x 上的点，再与 y=x 参考线对比。',
            demo: 'plotLinear'
          }),
          task('fg_l2_3', '过原点的直线', '正比例', SCENE.FUNCTION, {
            series: 'funcGraph', level: 'L2',
            tags: ['y=kx'],
            goals: ['走 y=0.5x 与 y=3x 上的点', '理解 k 改变倾斜程度'],
            sceneConfig: {
              cols: 12, rows: 10, cellCm: 10,
              plots: [
                { expr: '0.5*x', xMin: 0, xMax: 4, step: 1, color: '#94a3b8', label: 'y=0.5x' },
                { expr: '3*x', xMin: 0, xMax: 3, step: 1, color: '#f97316', label: 'y=3x' }
              ]
            },
            plotValidate: { expr: '3*x', toleranceCm: 1.5 },
            starter: { goto: [{ x: 0, y: 0 }, { x: 10, y: 30 }, { x: 20, y: 60 }] },
            demo: 'plotLinearSteep'
          })
        ]
      },
      l3: {
        name: 'L3 一次函数',
        tasks: [
          task('fg_l3_1', '截距 b 的作用', '一次函数', SCENE.FUNCTION, {
            series: 'funcGraph', level: 'L3',
            tags: ['截距', 'y=2x+3'],
            goals: ['走 y=2x+3 上的点', '观察直线不过原点'],
            sceneConfig: {
              cols: 12, rows: 10, cellCm: 10,
              plot: { expr: '2*x+3', xMin: 0, xMax: 4, step: 1, color: '#38bdf8', label: 'y=2x+3' }
            },
            plotValidate: { expr: '2*x+3', toleranceCm: 1.5 },
            starter: { goto: [{ x: 0, y: 30 }, { x: 10, y: 50 }, { x: 20, y: 70 }, { x: 30, y: 90 }] },
            demo: 'plotLinearIntercept'
          }),
          task('fg_l3_2', '匀速 s-t 图', '一次函数', SCENE.TIME, {
            series: 'funcGraph', level: 'L3',
            focus: '函数图象专题：s=vt 是一次函数，s-t 图象为直线',
            tags: ['s=vt', 's-t 图'],
            goals: ['s=vt 函数模型', '匀速运动图象', '斜率=速度'],
            formulas: [{ title: '一次函数', tex: '$$s = vt + s_0$$' }],
            starter: { speed: 5, forward: 100 },
            demo: 'linear'
          }),
          task('fg_l3_3', '追及与交点', '一次函数', SCENE.TIME, {
            series: 'funcGraph', level: 'L3',
            focus: '函数图象专题：追及问题对应两条 s-t 直线交点',
            tags: ['追及', '交点'],
            goals: ['追及问题建模', '速度差与时间', '从图象读交点'],
            starter: { speed: 15, forward: 60 },
            demo: 'chase'
          })
        ]
      },
      l4: {
        name: 'L4 二次函数',
        tasks: [
          task('fg_l4_1', '抛物线描点', '二次函数', SCENE.FUNCTION, {
            series: 'funcGraph', level: 'L4',
            tags: ['抛物线', 'y=x²'],
            goals: ['x=-2…2 描点 (x,x²)', '认识抛物线形状'],
            sceneConfig: {
              cols: 12, rows: 12, cellCm: 10,
              plot: { expr: 'x*x', xMin: -2, xMax: 2, step: 1, color: '#a78bfa', label: 'y=x²' }
            },
            plotValidate: { expr: 'x*x', toleranceCm: 2 },
            starter: { goto: [{ x: -20, y: 40 }, { x: -10, y: 10 }, { x: 0, y: 0 }, { x: 10, y: 10 }, { x: 20, y: 40 }] },
            demo: 'plotParabola'
          }),
          task('fg_l4_2', '参数 a 的影响', '二次函数', SCENE.FUNCTION, {
            series: 'funcGraph', level: 'L4',
            tags: ['参数 a'],
            goals: ['对比 a=1、2、0.5 的开口', '理解 |a| 越大越窄'],
            sceneConfig: {
              cols: 12, rows: 12, cellCm: 10,
              plots: [
                { expr: 'x*x', xMin: -2, xMax: 2, step: 1, color: '#38bdf8', label: 'y=x²' },
                { expr: '2*x*x', xMin: -2, xMax: 2, step: 1, color: '#f97316', label: 'y=2x²' },
                { expr: '0.5*x*x', xMin: -2, xMax: 2, step: 1, color: '#94a3b8', label: 'y=0.5x²' }
              ]
            },
            plotValidate: { expr: 'x*x', toleranceCm: 2 },
            starter: { goto: [{ x: -20, y: 40 }, { x: 0, y: 0 }, { x: 20, y: 40 }] },
            demo: 'plotParabola'
          }),
          task('fg_l4_3', '顶点与对称轴', '二次函数', SCENE.FUNCTION, {
            series: 'funcGraph', level: 'L4',
            tags: ['顶点', '平移'],
            goals: ['走 y=(x-1)²+2 关键点', '认识顶点与对称轴'],
            sceneConfig: {
              cols: 12, rows: 12, cellCm: 10,
              plot: { expr: '(x-1)*(x-1)+2', xMin: -1, xMax: 3, step: 1, color: '#f472b6', label: 'y=(x-1)²+2' }
            },
            plotValidate: { expr: '(x-1)*(x-1)+2', toleranceCm: 2 },
            starter: { goto: [{ x: 0, y: 30 }, { x: 10, y: 20 }, { x: 20, y: 30 }, { x: 30, y: 50 }] },
            demo: 'plotParabolaShifted'
          })
        ]
      },
      l5: {
        name: 'L5 拓展',
        tasks: [
          task('fg_l5_1', '反比例 y=k/x', '反比例', SCENE.FUNCTION, {
            series: 'funcGraph', level: 'L5',
            tags: ['反比例', '双曲线'],
            goals: ['描点理解 y=20/x', '观察两支曲线'],
            sceneConfig: {
              cols: 12, rows: 10, cellCm: 10,
              plot: { expr: '20/x', xMin: 2, xMax: 8, step: 1, color: '#22d3ee', label: 'y=20/x' }
            },
            hint: 'x 取 2,4,5,8 等，分别计算 y=20÷x 再 goto。',
            starter: { goto: [{ x: 20, y: 10 }, { x: 40, y: 5 }, { x: 50, y: 4 }] },
            demo: 'plotInverse'
          }),
          task('fg_l5_2', '分段函数', '分段函数', SCENE.FUNCTION, {
            series: 'funcGraph', level: 'L5',
            tags: ['分段', '折线'],
            goals: ['走折线路径', '理解分段定义'],
            sceneConfig: { cols: 12, rows: 10, cellCm: 10 },
            starter: {
              goto: [{ x: 0, y: 0 }, { x: 20, y: 20 }, { x: 30, y: 20 }, { x: 50, y: 0 }]
            },
            hint: '每段用 goto 连接，整体是分段一次函数。',
            demo: 'plotPiecewise'
          })
        ]
      }
    }
  },
  calculus: {
    name: '轮式机器人探秘微积分',
    grades: {
      l0: {
        name: 'L0 感受变化',
        tasks: [
          task('calc_l0_1', '谁走得更快', '感受变化', SCENE.TIME, {
            series: 'calculus', level: 'L0',
            tags: ['快慢', '对比'],
            goals: ['同样时间比路程', '建立「变化」直觉'],
            challenges: ['速度 10 走 5 秒 vs 速度 20 走 5 秒'],
            starter: { speed: 10, forward: 50 },
            demo: 'speedRace'
          }),
          task('calc_l0_2', '同样路程谁更久', '感受变化', SCENE.TIME, {
            series: 'calculus', level: 'L0',
            tags: ['时间', '对比'],
            goals: ['固定 50 cm 比用时', '理解速度与时间反比'],
            starter: { forward: 50 },
            demo: 'forward50'
          }),
          task('calc_l0_3', '先快后慢', '感受变化', SCENE.TIME, {
            series: 'calculus', level: 'L0',
            tags: ['分段速度'],
            goals: ['分段调速', '感受运动状态变化'],
            starter: { speed: 20, forward: 30, speed2: 5, forward2: 30 },
            demo: 'forward50'
          })
        ]
      },
      l1: {
        name: 'L1 均匀变化',
        tasks: [
          task('calc_l1_1', '每段多走一点', '均匀变化', SCENE.DISTANCE, {
            series: 'calculus', level: 'L0',
            tags: ['递增'],
            goals: ['段长 10→15→20', '观察变化规律'],
            starter: { forward: 10, forward2: 15, forward3: 20 },
            demo: 'forward10'
          }),
          task('calc_l1_2', '均匀加速初体验', '均匀变化', SCENE.TIME, {
            series: 'calculus', level: 'L1',
            tags: ['加速'],
            goals: ['速度 5→10→15 各走一段', '建立阶梯速度图直觉'],
            starter: { speed: 5, forward: 20, speed2: 10, forward2: 20, speed3: 15, forward3: 20 },
            demo: 'forward50'
          }),
          task('calc_l1_3', '变化有没有规律', '均匀变化', SCENE.DATA, {
            series: 'calculus', level: 'L1',
            tags: ['数据'],
            goals: ['多次运行记录距离', '用数据发现规律'],
            starter: { repeat: 3, forward: 20 },
            demo: 'forward10'
          })
        ]
      },
      l2: {
        name: 'L2 斜率即速度',
        tasks: [
          task('calc_l2_1', 's-t 图的斜率', '斜率即速度', SCENE.TIME, {
            series: 'calculus', level: 'L2',
            focus: '微积分专题：s-t 直线斜率 = 速度（包装匀速一次函数）',
            tags: ['s-t', '斜率', 's=vt'],
            goals: ['s=vt 函数模型', '匀速运动图象', '斜率=速度'],
            formulas: [{ title: '一次函数', tex: '$$s = vt$$' }],
            sceneConfig: {
              stGraph: { enabled: true, tMaxSec: 25, sMaxCm: 120 },
              calcOverlay: { type: 'secant', t0: 0, t1: 5 }
            },
            starter: { speed: 5, forward: 100 },
            demo: 'linear',
            calcValidate: { type: 'slope', t0: 0, t1: 5, expected: 5, tolerance: 1 }
          }),
          task('calc_l2_2', '不同斜率不同快', '斜率即速度', SCENE.TIME, {
            series: 'calculus', level: 'L2',
            tags: ['斜率', '对比'],
            goals: ['速度 5 与 15 的 s-t 线对比', '斜率越大走得越快'],
            sceneConfig: {
              stGraph: { enabled: true, tMaxSec: 20, sMaxCm: 90 },
              calcOverlay: { type: 'secant', t0: 0, t1: 4 }
            },
            starter: { speed: 5, forward: 40, speed2: 15, forward2: 40 },
            hint: '先慢后快，观察 s-t 图两段斜率差异。',
            demo: 'calcTwoSpeed'
          }),
          task('calc_l2_3', '追及：速度差', '斜率即速度', SCENE.PATH, {
            series: 'calculus', level: 'L2',
            mode: 'travel',
            travelSubtype: 'chase',
            focus: '微积分专题：追及对应 s-t 交点（包装追及问题）',
            tags: ['追及', '交点'],
            goals: ['理解追及核心是速度差', '从 s-t 图读交点与追及时刻'],
            formulas: [{ title: '追及', tex: '$$t=\\frac{\\Delta s}{v_2-v_1}$$' }],
            sceneConfig: {
              robots: [
                { id: 'A', label: '慢车', xCm: 0, yCm: 0, speed: 8, color: '#22d3ee' },
                { id: 'B', label: '快车', xCm: -40, yCm: 0, speed: 14, color: '#f97316' }
              ],
              trackLengthCm: 120,
              trackAxisDeg: 0,
              chaseValidate: { toleranceCm: 6 },
              stGraph: { enabled: true, tMaxSec: 20, sMaxCm: 140, showBoth: true }
            },
            starter: { travelParallel: [], autoMeet: true },
            demo: 'travelChase'
          })
        ]
      },
      l3: {
        name: 'L3 非均匀变化',
        tasks: [
          task('calc_l3_1', '变速运动', '非均匀变化', SCENE.CALC, {
            series: 'calculus', level: 'L3',
            tags: ['变速', '分段'],
            goals: ['分段变速走完全程', '观察 s-t 折线与 v-t 阶梯'],
            sceneConfig: {
              stGraph: { enabled: true, tMaxSec: 30, sMaxCm: 100 },
              vtGraph: { enabled: true, tMaxSec: 30, vMax: 20 }
            },
            starter: { speed: 5, forward: 30, speed2: 10, forward2: 30, speed3: 15, forward3: 30 },
            demo: 'calcPiecewiseSpeed'
          }),
          task('calc_l3_2', '分段走曲线', '非均匀变化', SCENE.CALC, {
            series: 'calculus', level: 'L3',
            tags: ['折线逼近'],
            goals: ['用折线轨迹逼近抛物线', '理解分段 vs 光滑'],
            sceneConfig: {
              stGraph: { enabled: true, tMaxSec: 25, sMaxCm: 80 },
              vtGraph: { enabled: true, tMaxSec: 25, vMax: 25 }
            },
            starter: {
              goto: [{ x: -20, y: 40 }, { x: -10, y: 10 }, { x: 0, y: 0 }, { x: 10, y: 10 }, { x: 20, y: 40 }]
            },
            demo: 'plotParabola'
          }),
          task('calc_l3_3', '分得越细越像', '非均匀变化', SCENE.CALC, {
            series: 'calculus', level: 'L3',
            tags: ['逼近'],
            goals: ['步长 10→5→2 分段前进', '折线越来越像曲线'],
            sceneConfig: {
              stGraph: { enabled: true, tMaxSec: 35, sMaxCm: 60 },
              vtGraph: { enabled: true, tMaxSec: 35, vMax: 20 }
            },
            starter: {
              forward: 10, forward2: 10, forward3: 10, forward4: 10, forward5: 10, forward6: 10
            },
            hint: '用多段相同小步长前进，观察 s-t 折线变密。',
            demo: 'calcFineSteps'
          })
        ]
      },
      l4: {
        name: 'L4 瞬时变化',
        tasks: [
          task('calc_l4_1', '某一时刻多快', '瞬时变化', SCENE.CALC, {
            series: 'calculus', level: 'L4',
            tags: ['平均速度', '割线'],
            goals: ['取一小段算平均速度', '理解割线斜率'],
            sceneConfig: {
              stGraph: { enabled: true, tMaxSec: 20, sMaxCm: 80 },
              vtGraph: { enabled: true, tMaxSec: 20, vMax: 20 },
              calcOverlay: { type: 'secant', t0: 2, t1: 6 }
            },
            starter: { speed: 10, forward: 60 },
            calcValidate: { type: 'slope', t0: 2, t1: 6, expected: 10, tolerance: 1.5 }
          }),
          task('calc_l4_2', '割线变切线', '瞬时变化', SCENE.CALC, {
            series: 'calculus', level: 'L4',
            tags: ['割线', '切线'],
            goals: ['缩小 Δt，观察割线斜率趋稳', '感受瞬时变化率'],
            sceneConfig: {
              stGraph: { enabled: true, tMaxSec: 15, sMaxCm: 50 },
              calcOverlay: { type: 'secant', t0: 4, t1: 5 }
            },
            starter: { speed: 8, forward: 40 },
            hint: '运行后对比 t0–t1 与更短区间的割线斜率。',
            demo: 'calcSecantNarrow'
          }),
          task('calc_l4_3', '导数直觉', '瞬时变化', SCENE.FUNCTION, {
            series: 'calculus', level: 'L4',
            tags: ['抛物线', '顶点'],
            goals: ['抛物线顶点处斜率为 0', '割线→切线直觉'],
            sceneConfig: {
              cols: 12, rows: 12, cellCm: 10,
              plot: { expr: 'x*x', xMin: -2, xMax: 2, step: 1, color: '#a78bfa', label: 'y=x²' },
              stGraph: { enabled: true, tMaxSec: 20, sMaxCm: 50 },
              calcOverlay: { type: 'secant', t0: -0.5, t1: 0.5 }
            },
            starter: { goto: [{ x: -10, y: 10 }, { x: 0, y: 0 }, { x: 10, y: 10 }] },
            demo: 'plotParabola'
          })
        ]
      },
      l5: {
        name: 'L5 累积与面积',
        tasks: [
          task('calc_l5_1', 'v-t 与总路程', '累积与面积', SCENE.CALC, {
            series: 'calculus', level: 'L5',
            tags: ['v-t', '面积'],
            goals: ['矩形面积 = 路程', '理解累积量'],
            sceneConfig: {
              stGraph: { enabled: true, tMaxSec: 12, sMaxCm: 120 },
              vtGraph: { enabled: true, tMaxSec: 12, vMax: 15 },
              calcOverlay: { type: 'riemann', t0: 0, t1: 10, n: 4 }
            },
            starter: { speed: 10, forward: 100 },
            calcValidate: { type: 'area', t0: 0, t1: 10, n: 10, expected: 100, tolerance: 5 }
          }),
          task('calc_l5_2', '变速：矩形逼近', '累积与面积', SCENE.CALC, {
            series: 'calculus', level: 'L5',
            tags: ['黎曼和'],
            goals: ['分段匀速，矩形求和', '分得越细越准'],
            sceneConfig: {
              stGraph: { enabled: true, tMaxSec: 25, sMaxCm: 100 },
              vtGraph: { enabled: true, tMaxSec: 25, vMax: 20 },
              calcOverlay: { type: 'riemann', t0: 0, t1: 10, n: 5 }
            },
            starter: { speed: 5, forward: 20, speed2: 10, forward2: 20, speed3: 15, forward3: 20 },
            calcValidate: { type: 'area', t0: 0, t1: 8, n: 8, expected: 60, tolerance: 20 }
          }),
          task('calc_l5_3', '从 s 到 v 到面积', '累积与面积', SCENE.CALC, {
            series: 'calculus', level: 'L5',
            tags: ['联动', '综合'],
            goals: ['s-t 斜率 ↔ v-t 面积', '串联变化与累积'],
            sceneConfig: {
              stGraph: { enabled: true, tMaxSec: 20, sMaxCm: 80 },
              vtGraph: { enabled: true, tMaxSec: 20, vMax: 15 },
              calcOverlay: { type: 'riemann', t0: 0, t1: 8, n: 4 }
            },
            starter: { speed: 8, forward: 64 },
            demo: 'calcPiecewiseSpeed'
          })
        ]
      }
    }
  }
};

/** 相向相遇：按初始间距与速度算两车应前进的距离（cm） */
function travelMeetDistances(cfg) {
  const robots = cfg?.robots || [];
  const a = robots.find(r => r.id === 'A') || robots[0];
  const b = robots.find(r => r.id === 'B') || robots[1];
  if (!a || !b) return { da: 40, db: 60, tMeet: 4, meetS: 40 };
  const s0A = a.xCm ?? 0;
  const s0B = b.xCm ?? cfg.trackLengthCm ?? 100;
  const gap = Math.abs(s0B - s0A);
  const vA = a.speed ?? 10;
  const vB = b.speed ?? 10;
  const tMeet = gap / (vA + vB);
  const meetS = Math.min(s0A, s0B) + vA * tMeet;
  return {
    da: Math.round((meetS - s0A) * 100) / 100,
    db: Math.round((s0B - meetS) * 100) / 100,
    tMeet,
    meetS
  };
}

/** 同向追及：快车追上慢车所需前进距离 */
function travelChaseDistances(cfg) {
  const robots = cfg?.robots || [];
  const a = robots.find(r => r.id === 'A') || robots[0];
  const b = robots.find(r => r.id === 'B') || robots[1];
  if (!a || !b) return { da: 54, db: 94, tMeet: 6.67, meetS: 53.33 };
  const s0A = a.xCm ?? 0;
  const s0B = b.xCm ?? 0;
  const vA = a.speed ?? 8;
  const vB = b.speed ?? 14;
  const gap = s0A - s0B;
  if (gap <= 0 || vB <= vA) return { da: 0, db: 0, tMeet: 0, meetS: s0A };
  const tMeet = gap / (vB - vA);
  const meetS = s0A + vA * tMeet;
  return {
    da: Math.round((meetS - s0A) * 100) / 100,
    db: Math.round((meetS - s0B) * 100) / 100,
    tMeet,
    meetS
  };
}

/** 根据 starter 配置生成 Blockly XML（块自动串联） */
function buildStarterXml(s, sceneConfig) {
  if (!s) return null;

  function numShadow(v) {
    return `<shadow type="math_num"><field name="N">${v}</field></shadow>`;
  }

  function blockMove2d(angle, dist) {
    return `<block type="motion_move_2d"><value name="ANGLE">${numShadow(angle)}</value><value name="D">${numShadow(dist)}</value>`;
  }
  function blockGoto(x, y) {
    return `<block type="motion_goto_xy"><value name="X">${numShadow(x)}</value><value name="Y">${numShadow(y)}</value>`;
  }
  function blockForward(v) {
    return `<block type="motion_forward"><value name="D">${numShadow(v)}</value>`;
  }
  function blockBackward(v) {
    return `<block type="motion_backward"><value name="D">${numShadow(v)}</value>`;
  }
  function blockTurnRight(v) {
    return `<block type="motion_turn_right"><value name="A">${numShadow(v)}</value>`;
  }
  function blockTurnLeft(v) {
    return `<block type="motion_turn_left"><value name="A">${numShadow(v)}</value>`;
  }
  function blockSpeed(v) {
    return `<block type="motion_speed"><value name="S">${numShadow(v)}</value>`;
  }
  function blockWait(v) {
    return `<block type="motion_wait"><value name="T">${numShadow(v)}</value>`;
  }
  function blockForwardRobot(robot, v) {
    return `<block type="motion_forward_robot"><field name="ROBOT">${robot}</field><value name="D">${numShadow(v)}</value>`;
  }
  function blockSpeedRobot(robot, v) {
    return `<block type="motion_speed_robot"><field name="ROBOT">${robot}</field><value name="S">${numShadow(v)}</value>`;
  }
  function blockParallelMove(a, b) {
    return `<block type="control_parallel_move"><value name="DA">${numShadow(a)}</value><value name="DB">${numShadow(b)}</value>`;
  }
  function blockRepeat(n, inner) {
    return `<block type="control_repeat"><value name="N">${numShadow(n)}</value><statement name="DO">${inner}</statement>`;
  }

  const steps = [];
  if (s.travelParallel) {
    let a = s.travelParallel.find(j => (j.robot || 'A') === 'A')?.cm;
    let b = s.travelParallel.find(j => (j.robot || 'B') === 'B')?.cm;
    if (s.autoMeet !== false && sceneConfig) {
      if (sceneConfig.travelSubtype === 'chase') {
        const d = travelChaseDistances(sceneConfig);
        a = d.da; b = d.db;
      } else if (sceneConfig.travelSubtype === 'meet') {
        const d = travelMeetDistances(sceneConfig);
        a = d.da; b = d.db;
      }
    }
    steps.push(blockParallelMove(a ?? 0, b ?? 0));
  } else if (s.travelDelayStart) {
    const d = s.travelDelayStart;
    if (d.speedA != null) steps.push(blockSpeedRobot('A', d.speedA));
    if (d.speedB != null) steps.push(blockSpeedRobot('B', d.speedB));
    if (d.waitSec != null) steps.push(blockWait(d.waitSec));
    let da = d.da;
    let db = d.db;
    if (d.autoMeet !== false && sceneConfig?.travelSubtype === 'meet') {
      const m = travelMeetDistances(sceneConfig);
      da = m.da; db = m.db;
    }
    if (da != null || db != null) steps.push(blockParallelMove(da || 0, db || 0));
  } else if (s.repeat && s.forward != null && s.turn != null) {
    if (s.speed != null) steps.push(blockSpeed(s.speed));
    if (s.repeat === 4 && s.turn === 90) {
      [0, 90, 180, 270].forEach(deg => steps.push(blockMove2d(deg, s.forward)));
    } else {
      const inner = `<block type="motion_forward"><value name="D">${numShadow(s.forward)}</value><next><block type="motion_turn_right"><value name="A">${numShadow(s.turn)}</value></block></next></block>`;
      steps.push(`<block type="control_repeat"><value name="N">${numShadow(s.repeat)}</value><statement name="DO">${inner}</statement>`);
    }
  } else if (s.move2d) {
    if (s.speed != null) steps.push(blockSpeed(s.speed));
    (Array.isArray(s.move2d) ? s.move2d : [s.move2d]).forEach(m => {
      steps.push(blockMove2d(m.angle ?? m.a ?? 0, m.dist ?? m.d ?? m.forward ?? 0));
    });
  } else if (s.goto) {
    if (s.speed != null) steps.push(blockSpeed(s.speed));
    (Array.isArray(s.goto) ? s.goto : [s.goto]).forEach(p => {
      steps.push(blockGoto(p.x ?? p[0] ?? 0, p.y ?? p[1] ?? 0));
    });
  } else if (s.repeat != null && s.forward != null && s.turn == null) {
    if (s.speed != null) steps.push(blockSpeed(s.speed));
    const inner = `<block type="motion_forward"><value name="D">${numShadow(s.forward)}</value></block>`;
    steps.push(blockRepeat(s.repeat, inner));
  } else {
    if (s.speed != null) steps.push(blockSpeed(s.speed));
    if (s.forward != null) steps.push(blockMove2d(0, s.forward));
    if (s.backward != null) steps.push(blockBackward(s.backward));
    if (s.wait != null) steps.push(blockWait(s.wait));
    if (s.turn != null) steps.push(blockTurnRight(s.turn));
    if (s.speed2 != null) steps.push(blockSpeed(s.speed2));
    if (s.forward2 != null) steps.push(blockForward(s.forward2));
    if (s.turn2 != null) steps.push(blockTurnRight(s.turn2));
    if (s.speed3 != null) steps.push(blockSpeed(s.speed3));
    if (s.forward3 != null) steps.push(blockForward(s.forward3));
    if (s.extraForward != null) steps.push(blockForward(s.extraForward));
    if (s.turns) {
      steps.length = 0;
      s.turns.forEach(t => steps.push(t.dir === 'left' ? blockTurnLeft(t.deg) : blockTurnRight(t.deg)));
    }
  }

  if (!steps.length) return null;

  function chainBlocks(parts, idx) {
    const cur = parts[idx] + '</block>';
    if (idx >= parts.length - 1) return cur;
    return cur.replace('</block>', `<next>${chainBlocks(parts, idx + 1)}</next></block>`);
  }

  return `<xml><block type="event_start" x="40" y="40"><next>${chainBlocks(steps, 0)}</next></block></xml>`;
}

window.CURRICULUM = CURRICULUM;
window.SCENE = SCENE;
window.buildStarterXml = buildStarterXml;
window.travelMeetDistances = travelMeetDistances;
window.travelChaseDistances = travelChaseDistances;
window.DEFAULT_FORMULAS = DEFAULT_FORMULAS;
