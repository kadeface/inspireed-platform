/**
 * PhET Simulation Catalog
 * Complete list of available PhET simulations organized by subject
 * Source: https://phet.colorado.edu
 */

export interface PhETSimulation {
  id: string
  name: string
  nameCn: string
  category: 'physics' | 'chemistry' | 'biology' | 'earth' | 'math'
  description: string
  descriptionCn: string
  url: string
  image?: string
  topics: string[]
}

export const PHET_SIMULATIONS: PhETSimulation[] = [
  // Physics - Mechanics
  {
    id: 'motion',
    name: 'Motion',
    nameCn: '运动',
    category: 'physics',
    description: 'Explore kinematics and motion graphs',
    descriptionCn: '探索运动学和运动图表',
    url: 'https://phet.colorado.edu/sims/html/moving-man/latest/moving-man_zh_CN.html',
    topics: ['kinematics', 'velocity', 'acceleration', 'graphs']
  },
  {
    id: 'forces-motion-basics',
    name: 'Forces and Motion: Basics',
    nameCn: '力与运动：基础',
    category: 'physics',
    description: 'Explore forces, acceleration, and friction',
    descriptionCn: '探索力、加速度和摩擦力',
    url: 'https://phet.colorado.edu/sims/html/forces-and-motion-basics/latest/forces-and-motion-basics_zh_CN.html',
    topics: ['forces', 'acceleration', 'friction', 'newton-laws']
  },
  {
    id: 'projectile-motion',
    name: 'Projectile Motion',
    nameCn: '抛体运动',
    category: 'physics',
    description: 'Explore projectile motion',
    descriptionCn: '探索抛体运动',
    url: 'https://phet.colorado.edu/sims/html/projectile-motion/latest/projectile-motion_zh_CN.html',
    topics: ['projectiles', 'trajectory', 'parabolic-motion']
  },
  {
    id: 'energy-skate-park',
    name: 'Energy Skate Park',
    nameCn: '能量滑板公园',
    category: 'physics',
    description: 'Explore conservation of energy',
    descriptionCn: '探索能量守恒',
    url: 'https://phet.colorado.edu/sims/html/energy-skate-park/latest/energy-skate-park_zh_CN.html',
    topics: ['energy', 'conservation', 'kinetic', 'potential']
  },
  {
    id: 'pendulum-lab',
    name: 'Pendulum Lab',
    nameCn: '单摆实验',
    category: 'physics',
    description: 'Explore pendulum motion and energy',
    descriptionCn: '探索单摆运动和能量',
    url: 'https://phet.colorado.edu/sims/html/pendulum-lab/latest/pendulum-lab_zh_CN.html',
    topics: ['oscillation', 'period', 'frequency', 'simple-harmonic-motion']
  },
  
  // Physics - Waves and Sound
  {
    id: 'wave-interference',
    name: 'Wave Interference',
    nameCn: '波的干涉',
    category: 'physics',
    description: 'Explore wave interference patterns',
    descriptionCn: '探索波的干涉图案',
    url: 'https://phet.colorado.edu/sims/html/wave-interference/latest/wave-interference_zh_CN.html',
    topics: ['waves', 'interference', 'superposition', 'standing-waves']
  },
  {
    id: 'sound',
    name: 'Sound',
    nameCn: '声音',
    category: 'physics',
    description: 'Explore sound waves and acoustics',
    descriptionCn: '探索声波和声学',
    url: 'https://phet.colorado.edu/sims/html/sound/latest/sound_zh_CN.html',
    topics: ['sound', 'waves', 'frequency', 'amplitude']
  },
  
  // Physics - Electricity and Magnetism
  {
    id: 'circuit-construction-kit',
    name: 'Circuit Construction Kit',
    nameCn: '电路搭建工具包',
    category: 'physics',
    description: 'Build and explore electric circuits',
    descriptionCn: '构建和探索电路',
    url: 'https://phet.colorado.edu/sims/html/circuit-construction-kit-dc/latest/circuit-construction-kit-dc_zh_CN.html',
    topics: ['circuits', 'electricity', 'voltage', 'current']
  },
  {
    id: 'electric-field-hockey',
    name: 'Electric Field Hockey',
    nameCn: '电场冰球',
    category: 'physics',
    description: 'Explore electric charges and fields',
    descriptionCn: '探索电荷和电场',
    url: 'https://phet.colorado.edu/sims/html/charges-and-fields/latest/charges-and-fields_zh_CN.html',
    topics: ['electric-field', 'charges', 'electrostatics']
  },
  {
    id: 'magnet-compass',
    name: 'Magnets and Compasses',
    nameCn: '磁铁和指南针',
    category: 'physics',
    description: 'Explore magnetic fields',
    descriptionCn: '探索磁场',
    url: 'https://phet.colorado.edu/sims/html/magnet-and-compass/latest/magnet-and-compass_zh_CN.html',
    topics: ['magnetism', 'magnetic-field', 'compass']
  },
  
  // Chemistry
  {
    id: 'atomic-structure',
    name: 'Build an Atom',
    nameCn: '构建原子',
    category: 'chemistry',
    description: 'Explore atomic structure',
    descriptionCn: '探索原子结构',
    url: 'https://phet.colorado.edu/sims/html/build-an-atom/latest/build-an-atom_zh_CN.html',
    topics: ['atoms', 'protons', 'neutrons', 'electrons', 'periodic-table']
  },
  {
    id: 'molecules-shapes',
    name: 'Molecule Shapes',
    nameCn: '分子形状',
    category: 'chemistry',
    description: 'Explore molecular geometry',
    descriptionCn: '探索分子几何',
    url: 'https://phet.colorado.edu/sims/html/molecule-shapes/latest/molecule-shapes_zh_CN.html',
    topics: ['molecules', 'geometry', 'bonding', 'lewis-structures']
  },
  {
    id: 'states-of-matter',
    name: 'States of Matter',
    nameCn: '物态',
    category: 'chemistry',
    description: 'Explore phase transitions',
    descriptionCn: '探索相变',
    url: 'https://phet.colorado.edu/sims/html/states-of-matter-basics/latest/states-of-matter-basics_zh_CN.html',
    topics: ['solid', 'liquid', 'gas', 'phase-transitions', 'temperature']
  },
  {
    id: 'ph-scale',
    name: 'pH Scale',
    nameCn: 'pH值',
    category: 'chemistry',
    description: 'Explore acidity and alkalinity',
    descriptionCn: '探索酸碱性',
    url: 'https://phet.colorado.edu/sims/html/ph-scale/latest/ph-scale_zh_CN.html',
    topics: ['ph', 'acids', 'bases', 'ph-scale']
  },
  {
    id: 'reactants-products-leftovers',
    name: 'Reactants, Products & Leftovers',
    nameCn: '反应物、产物与剩余',
    category: 'chemistry',
    description: 'Explore chemical reactions',
    descriptionCn: '探索化学反应',
    url: 'https://phet.colorado.edu/sims/html/reactants-products-and-leftovers/latest/reactants-products-and-leftovers_zh_CN.html',
    topics: ['chemical-reactions', 'stoichiometry', 'limiting-reagents']
  },
  
  // Biology
  {
    id: 'natural-selection',
    name: 'Natural Selection',
    nameCn: '自然选择',
    category: 'biology',
    description: 'Explore evolution and natural selection',
    descriptionCn: '探索进化和自然选择',
    url: 'https://phet.colorado.edu/sims/html/natural-selection/latest/natural-selection_zh_CN.html',
    topics: ['evolution', 'natural-selection', 'adaptation']
  },
  {
    id: 'gene-expression',
    name: 'Gene Expression',
    nameCn: '基因表达',
    category: 'biology',
    description: 'Explore DNA transcription and translation',
    descriptionCn: '探索DNA转录和翻译',
    url: 'https://phet.colorado.edu/sims/html/gene-expression-basics/latest/gene-expression-basics_zh_CN.html',
    topics: ['dna', 'transcription', 'translation', 'proteins']
  },
  
  // Earth & Space
  {
    id: 'gravity-and-orbits',
    name: 'Gravity and Orbits',
    nameCn: '引力和轨道',
    category: 'earth',
    description: 'Explore gravitational forces and orbits',
    descriptionCn: '探索引力和轨道',
    url: 'https://phet.colorado.edu/sims/html/gravity-and-orbits/latest/gravity-and-orbits_zh_CN.html',
    topics: ['gravity', 'orbits', 'planets', 'moons']
  },
  {
    id: 'solar-system',
    name: 'My Solar System',
    nameCn: '我的太阳系',
    category: 'earth',
    description: 'Build your own solar system',
    descriptionCn: '构建自己的太阳系',
    url: 'https://phet.colorado.edu/sims/html/my-solar-system/latest/my-solar-system_zh_CN.html',
    topics: ['solar-system', 'planets', 'gravity', 'orbits']
  },
  
  // Math & Statistics
  {
    id: 'fractions',
    name: 'Fractions: Intro',
    nameCn: '分数简介',
    category: 'math',
    description: 'Explore fractions visually',
    descriptionCn: '可视化探索分数',
    url: 'https://phet.colorado.edu/sims/html/fractions-intro/latest/fractions-intro_zh_CN.html',
    topics: ['fractions', 'numerator', 'denominator', 'equivalence']
  },
  {
    id: 'area-model',
    name: 'Area Model',
    nameCn: '面积模型',
    category: 'math',
    description: 'Explore multiplication and area',
    descriptionCn: '探索乘法和面积',
    url: 'https://phet.colorado.edu/sims/html/area-model-algebra/latest/area-model-algebra_zh_CN.html',
    topics: ['multiplication', 'area', 'algebra', 'polynomials']
  },
  {
    id: 'graphing-lines',
    name: 'Graphing Lines',
    nameCn: '直线图形',
    category: 'math',
    description: 'Explore linear equations and slopes',
    descriptionCn: '探索线性方程和斜率',
    url: 'https://phet.colorado.edu/sims/html/graphing-lines/latest/graphing-lines_zh_CN.html',
    topics: ['lines', 'slope', 'linear-equations', 'graphing']
  }
]

export const PHET_CATEGORIES = [
  { id: 'physics', name: '物理', nameEn: 'Physics' },
  { id: 'chemistry', name: '化学', nameEn: 'Chemistry' },
  { id: 'biology', name: '生物', nameEn: 'Biology' },
  { id: 'earth', name: '地球科学', nameEn: 'Earth & Space' },
  { id: 'math', name: '数学', nameEn: 'Math & Statistics' },
] as const

export function getPHETSimulationsByCategory(category?: string): PhETSimulation[] {
  if (!category) return PHET_SIMULATIONS
  return PHET_SIMULATIONS.filter(sim => sim.category === category)
}

export function getPHETSimulation(id: string): PhETSimulation | undefined {
  return PHET_SIMULATIONS.find(sim => sim.id === id)
}

