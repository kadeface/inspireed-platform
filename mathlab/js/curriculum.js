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
  DATA: 'data'                // 数据统计面板
};

const DEFAULT_FORMULAS = [
  { title: '轮子周长', tex: '$$C = \\pi \\times d$$' },
  { title: '行进距离', tex: '$$S = C \\times n$$' }
];

function task(id, title, unit, scene, extra) {
  return Object.assign({
    id, title, unit, scene,
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
          task('j8d14', '任务14：距离测算与勾股定理', '勾股定理', SCENE.GRID, {
            tags: ['勾股定理', 'a²+b²=c²'],
            goals: ['走 3-4-5 直角三角形', '验证勾股定理'],
            formulas: [{ title: '勾股定理', tex: '$$a^2 + b^2 = c^2$$' }],
            sceneConfig: { shape: 'triangle', sides: [30, 40, 50] },
            starter: { forward: 30, turn: 90, forward2: 40, turn2: 135, forward3: 50 },
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
          task('j9d26', '任务26：坡度与角度测量', '锐角三角函数', SCENE.ANGLE, {
            tags: ['坡度', 'tan', '角度'],
            goals: ['坡度=tanα', '角度与高度关系'],
            formulas: [{ title: '坡度', tex: '$$i = \\tan\\alpha = \\frac{h}{l}$$' }],
            starter: { turn: 15, forward: 80 },
            demo: 'slope'
          }),
          task('j9d27', '任务27：综合感知与自主规划', '综合应用', SCENE.PATH, {
            tags: ['综合', '规划', '项目'],
            goals: ['综合数学与编程', '自主规划路径', '完成任务目标'],
            challenges: ['设计一条包含 2 次转弯的总长 150cm 路径'],
            starter: { forward: 50, turn: 90, forward2: 50, turn2: 90, forward3: 50 },
            demo: 'comprehensive'
          })
        ]
      }
    }
  }
};

/** 根据 starter 配置生成 Blockly XML（块自动串联） */
function buildStarterXml(s) {
  if (!s) return null;

  function numShadow(v) {
    return `<shadow type="math_num"><field name="N">${v}</field></shadow>`;
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
  function blockRepeat(n, inner) {
    return `<block type="control_repeat"><value name="N">${numShadow(n)}</value><statement name="DO">${inner}</statement>`;
  }

  const steps = [];
  if (s.repeat && s.forward != null && s.turn != null) {
    if (s.speed != null) steps.push(blockSpeed(s.speed));
    const inner = `<block type="motion_forward"><value name="D">${numShadow(s.forward)}</value><next><block type="motion_turn_right"><value name="A">${numShadow(s.turn)}</value></block></next></block>`;
    steps.push(`<block type="control_repeat"><value name="N">${numShadow(s.repeat)}</value><statement name="DO">${inner}</statement>`);
  } else {
    if (s.speed != null) steps.push(blockSpeed(s.speed));
    if (s.forward != null) steps.push(blockForward(s.forward));
    if (s.backward != null) steps.push(blockBackward(s.backward));
    if (s.wait != null) steps.push(blockWait(s.wait));
    if (s.turn != null) steps.push(blockTurnRight(s.turn));
    if (s.forward2 != null) steps.push(blockForward(s.forward2));
    if (s.turn2 != null) steps.push(blockTurnRight(s.turn2));
    if (s.forward3 != null) steps.push(blockForward(s.forward3));
    if (s.extraForward != null) steps.push(blockForward(s.extraForward));
    if (s.turns) {
      steps.length = 0;
      s.turns.forEach(t => steps.push(t.dir === 'left' ? blockTurnLeft(t.deg) : blockTurnRight(t.deg)));
    }
  }

  if (!steps.length) return null;

  let chain = steps.map(b => b + '</block>').join('<next>');
  chain = chain.replace(/<\/block><next>/g, '</block><next>');

  return `<xml><block type="event_start" x="40" y="40"><next>${chain}</next></block></xml>`;
}

window.CURRICULUM = CURRICULUM;
window.SCENE = SCENE;
window.buildStarterXml = buildStarterXml;
window.DEFAULT_FORMULAS = DEFAULT_FORMULAS;
