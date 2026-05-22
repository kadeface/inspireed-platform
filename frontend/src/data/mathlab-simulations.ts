/**
 * 学科仿真 — mathlab 轮式机器人数学融合互动教学
 * 静态资源部署于 frontend/public/mathlab/（源目录：仓库根 mathlab/）
 */

export interface MathlabSimulation {
  id: string
  name: string
  nameCn: string
  description: string
  descriptionCn: string
  embedUrl: string
  topics: string[]
}

export const MATHLAB_DEFAULT_CONFIG = {
  width: 1320,
  height: 820,
  autoplay: false,
} as const

export const MATHLAB_SIMULATIONS: MathlabSimulation[] = [
  {
    id: 'robot-math-fusion',
    name: 'Wheeled Robot Math Lab',
    nameCn: '轮式机器人 · 数学融合互动教学',
    description: 'Blockly programming with a virtual wheeled robot for K–12 math tasks',
    descriptionCn:
      '拖拽积木控制虚拟轮式机器人，在模拟中完成测距、转角、走图形、坐标导航、三角函数（sin/cos/tan）等 50+ 数学教学任务',
    embedUrl: '/mathlab/index.html',
    topics: ['数学', '机器人', 'Blockly', '几何', '三角函数', '编程'],
  },
]

export function getMathlabSimulation(id: string): MathlabSimulation | undefined {
  return MATHLAB_SIMULATIONS.find((sim) => sim.id === id)
}

export interface MathlabEmbedOptions {
  taskId?: string
  mode?: 'contest'
  sessionId?: number
  contestId?: number
}

/** 构建 iframe 地址，可选 task / 竞赛参数 */
export function getMathlabEmbedUrl(
  id: string,
  taskIdOrOptions?: string | MathlabEmbedOptions
): string {
  const sim = getMathlabSimulation(id)
  const base = sim?.embedUrl ?? '/mathlab/index.html'
  const opts: MathlabEmbedOptions =
    typeof taskIdOrOptions === 'string'
      ? { taskId: taskIdOrOptions }
      : taskIdOrOptions || {}

  const params = new URLSearchParams()
  if (opts.taskId) params.set('task', opts.taskId)
  if (opts.mode === 'contest') params.set('mode', 'contest')
  if (opts.sessionId != null) params.set('sessionId', String(opts.sessionId))
  if (opts.contestId != null) params.set('contestId', String(opts.contestId))
  const qs = params.toString()
  if (!qs) return base
  const sep = base.includes('?') ? '&' : '?'
  return `${base}${sep}${qs}`
}
