/**
 * Tinkercad 3D 设计仿真目录
 * https://www.tinkercad.com
 */

export interface TinkercadSimulation {
  id: string
  name: string
  nameCn: string
  description: string
  descriptionCn: string
  url: string
  embedUrl?: string
  topics: string[]
}

export const TINKERCAD_DEFAULT_CONFIG = {
  width: 1000,
  height: 700,
  autoplay: false,
} as const

export const TINKERCAD_SIMULATIONS: TinkercadSimulation[] = [
  {
    id: 'tinkercad-3d-create',
    name: 'Tinkercad 3D Design',
    nameCn: 'Tinkercad 3D 建模',
    description: 'Autodesk Tinkercad - browser-based 3D design and modeling',
    descriptionCn: 'Autodesk Tinkercad 在线 3D 建模与设计，支持拖拽组合几何体、导出 3D 打印',
    url: 'https://www.tinkercad.com/things/create',
    embedUrl: 'https://www.tinkercad.com/things/create',
    topics: ['3D', 'CAD', '建模', '设计', '3D打印'],
  },
  {
    id: 'tinkercad-3d-gallery',
    name: 'Tinkercad 3D Gallery',
    nameCn: 'Tinkercad 3D 作品库',
    description: 'Browse and remix public 3D designs on Tinkercad',
    descriptionCn: '浏览 Tinkercad 公开 3D 作品，可 remix 学习他人设计',
    url: 'https://www.tinkercad.com/things',
    embedUrl: 'https://www.tinkercad.com/things',
    topics: ['3D', '作品', 'remix', '学习'],
  },
  {
    id: 'tinkercad-dashboard',
    name: 'Tinkercad Dashboard',
    nameCn: 'Tinkercad 工作台',
    description: 'Tinkercad dashboard - manage 3D designs, circuits, and codeblocks',
    descriptionCn: 'Tinkercad 工作台，管理 3D 设计、电路与代码块项目',
    url: 'https://www.tinkercad.com/dashboard',
    embedUrl: 'https://www.tinkercad.com/dashboard',
    topics: ['工作台', '项目管理', '3D', '电路'],
  },
]

export function getTinkercadSimulation(id: string): TinkercadSimulation | undefined {
  return TINKERCAD_SIMULATIONS.find((sim) => sim.id === id)
}

export function getTinkercadEmbedUrl(id: string): string | undefined {
  const sim = getTinkercadSimulation(id)
  return sim?.embedUrl || sim?.url
}
