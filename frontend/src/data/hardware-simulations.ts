/**
 * 开源硬件仿真工具目录
 * 支持 Arduino、ESP32 等开源硬件的在线仿真
 */

export interface HardwareSimulation {
  id: string
  name: string
  nameCn: string
  platform: 'wokwi' | 'tinkercad' | 'circuitjs' | 'makecode' | 'mblock' | 'funcode' | 'custom'
  description: string
  descriptionCn: string
  url: string
  embedUrl?: string // iframe 嵌入 URL
  category: 'arduino' | 'esp32' | 'circuit' | 'microcontroller' | 'graphical' // 添加图形化编程分类
  programmingType: 'code' | 'graphical' | 'both' // 编程类型：代码、图形化、或两者都支持
  topics: string[]
  hardware?: string[] // 支持的硬件型号
  features?: string[] // 主要功能特性
}

export const HARDWARE_SIMULATIONS: HardwareSimulation[] = [
  // Wokwi - Arduino 仿真
  {
    id: 'wokwi-arduino-starter',
    name: 'Wokwi Arduino Starter',
    nameCn: 'Wokwi Arduino 入门',
    platform: 'wokwi',
    description: 'Online Arduino simulator with code editor and circuit builder',
    descriptionCn: '在线 Arduino 仿真器，支持代码编辑和电路搭建',
    url: 'https://wokwi.com/projects/new/arduino',
    embedUrl: 'https://wokwi.com/projects/new/arduino',
    category: 'arduino',
    programmingType: 'code',
    topics: ['arduino', 'microcontroller', 'embedded', 'programming'],
    hardware: ['Arduino Uno', 'Arduino Nano', 'Arduino Mega'],
    features: ['代码编辑', '电路仿真', '实时调试', '组件库']
  },
  {
    id: 'wokwi-esp32-starter',
    name: 'Wokwi ESP32 Starter',
    nameCn: 'Wokwi ESP32 入门',
    platform: 'wokwi',
    description: 'Online ESP32 simulator with WiFi and Bluetooth support',
    descriptionCn: '在线 ESP32 仿真器，支持 WiFi 和蓝牙',
    url: 'https://wokwi.com/projects/new/esp32',
    embedUrl: 'https://wokwi.com/projects/new/esp32',
    category: 'esp32',
    programmingType: 'code',
    topics: ['esp32', 'wifi', 'bluetooth', 'iot'],
    hardware: ['ESP32', 'ESP32-C3', 'ESP32-S2'],
    features: ['WiFi 仿真', '蓝牙仿真', 'IoT 开发', 'Web 服务器']
  },
  {
    id: 'wokwi-arduino-blink',
    name: 'Arduino Blink Example',
    nameCn: 'Arduino LED 闪烁示例',
    platform: 'wokwi',
    description: 'Classic Arduino blink example with LED',
    descriptionCn: '经典的 Arduino LED 闪烁示例',
    url: 'https://wokwi.com/arduino/projects/305569163575788097',
    embedUrl: 'https://wokwi.com/arduino/projects/305569163575788097',
    category: 'arduino',
    programmingType: 'code',
    topics: ['arduino', 'led', 'gpio', 'beginner'],
    hardware: ['Arduino Uno'],
    features: ['LED 控制', 'GPIO', '基础示例']
  },
  
  // Tinkercad Circuits (支持代码块/图形化编程)
  {
    id: 'tinkercad-circuits-starter',
    name: 'Tinkercad Circuits',
    nameCn: 'Tinkercad 电路仿真',
    platform: 'tinkercad',
    description: 'Autodesk Tinkercad Circuits - Arduino circuit simulator with blocks',
    descriptionCn: 'Autodesk Tinkercad 电路仿真器 - 支持代码块图形化编程',
    url: 'https://www.tinkercad.com/circuits',
    embedUrl: 'https://www.tinkercad.com/circuits',
    category: 'graphical',
    programmingType: 'both',
    topics: ['arduino', 'circuit', 'design', 'simulation', 'blocks'],
    hardware: ['Arduino Uno', 'Arduino Nano'],
    features: ['电路设计', '3D 可视化', '代码块编程', '组件库', '图形化编程']
  },
  {
    id: 'tinkercad-arduino-blink',
    name: 'Tinkercad Arduino Blink',
    nameCn: 'Tinkercad Arduino 闪烁',
    platform: 'tinkercad',
    description: 'Arduino blink example in Tinkercad with blocks',
    descriptionCn: 'Tinkercad 中的 Arduino 闪烁示例（代码块）',
    url: 'https://www.tinkercad.com/things/6MZ2LXKQCHL',
    embedUrl: 'https://www.tinkercad.com/things/6MZ2LXKQCHL',
    category: 'graphical',
    programmingType: 'both',
    topics: ['arduino', 'led', 'beginner', 'tutorial', 'blocks'],
    hardware: ['Arduino Uno'],
    features: ['LED 控制', '可视化仿真', '代码块', '图形化编程']
  },
  
  // CircuitJS (电路仿真)
  {
    id: 'circuitjs-starter',
    name: 'CircuitJS',
    nameCn: 'CircuitJS 电路仿真',
    platform: 'circuitjs',
    description: 'Browser-based circuit simulator',
    descriptionCn: '基于浏览器的电路仿真器',
    url: 'https://www.falstad.com/circuit/',
    embedUrl: 'https://www.falstad.com/circuit/',
    category: 'circuit',
    programmingType: 'code',
    topics: ['circuit', 'electronics', 'simulation', 'analysis'],
    hardware: [],
    features: ['电路分析', '波形显示', '参数调节', '多种元件']
  },
  
  // ========== 图形化编程工具 ==========
  
  // Microsoft MakeCode
  {
    id: 'makecode-microbit',
    name: 'MakeCode for micro:bit',
    nameCn: 'MakeCode micro:bit 图形化编程',
    platform: 'makecode',
    description: 'Microsoft MakeCode - Graphical programming for micro:bit',
    descriptionCn: 'Microsoft MakeCode - micro:bit 图形化编程平台',
    url: 'https://makecode.microbit.org/',
    embedUrl: 'https://makecode.microbit.org/',
    category: 'graphical',
    programmingType: 'graphical',
    topics: ['microbit', 'graphical', 'blocks', 'beginner', 'education'],
    hardware: ['micro:bit'],
    features: ['图形化编程', '代码块拖拽', '实时仿真', 'JavaScript 转换', 'Python 支持']
  },
  {
    id: 'makecode-arduino',
    name: 'MakeCode for Arduino',
    nameCn: 'MakeCode Arduino 图形化编程',
    platform: 'makecode',
    description: 'Microsoft MakeCode - Graphical programming for Arduino',
    descriptionCn: 'Microsoft MakeCode - Arduino 图形化编程平台',
    url: 'https://makecode.adafruit.com/',
    embedUrl: 'https://makecode.adafruit.com/',
    category: 'graphical',
    programmingType: 'graphical',
    topics: ['arduino', 'graphical', 'blocks', 'adafruit', 'circuit-playground'],
    hardware: ['Arduino', 'Circuit Playground Express', 'Adafruit'],
    features: ['图形化编程', '代码块拖拽', '电路仿真', '传感器支持']
  },
  {
    id: 'makecode-calliope',
    name: 'MakeCode for Calliope',
    nameCn: 'MakeCode Calliope 图形化编程',
    platform: 'makecode',
    description: 'Microsoft MakeCode - Graphical programming for Calliope mini',
    descriptionCn: 'Microsoft MakeCode - Calliope mini 图形化编程平台',
    url: 'https://makecode.calliope.cc/',
    embedUrl: 'https://makecode.calliope.cc/',
    category: 'graphical',
    programmingType: 'graphical',
    topics: ['calliope', 'graphical', 'blocks', 'education', 'germany'],
    hardware: ['Calliope mini'],
    features: ['图形化编程', '代码块拖拽', '传感器仿真', '音乐编程']
  },
  
  // mBlock (基于 Scratch)
  {
    id: 'mblock-starter',
    name: 'mBlock 5',
    nameCn: 'mBlock 5 图形化编程',
    platform: 'mblock',
    description: 'mBlock 5 - Scratch-based graphical programming for Arduino and robots',
    descriptionCn: 'mBlock 5 - 基于 Scratch 的图形化编程，支持 Arduino 和机器人',
    url: 'https://mblock.makeblock.com/',
    embedUrl: 'https://mblock.makeblock.com/',
    category: 'graphical',
    programmingType: 'graphical',
    topics: ['arduino', 'scratch', 'graphical', 'robotics', 'blocks'],
    hardware: ['Arduino Uno', 'Arduino Nano', 'mBot', 'Codey Rocky'],
    features: ['Scratch 图形化', 'Arduino 编程', '机器人控制', 'AI 功能', 'IoT 支持']
  },
  {
    id: 'mblock-microbit',
    name: 'mBlock for micro:bit',
    nameCn: 'mBlock micro:bit 图形化编程',
    platform: 'mblock',
    description: 'mBlock - Graphical programming for micro:bit',
    descriptionCn: 'mBlock - micro:bit 图形化编程',
    url: 'https://mblock.makeblock.com/',
    embedUrl: 'https://mblock.makeblock.com/',
    category: 'graphical',
    programmingType: 'graphical',
    topics: ['microbit', 'scratch', 'graphical', 'blocks', 'education'],
    hardware: ['micro:bit'],
    features: ['Scratch 图形化', '实时仿真', '传感器支持', '无线编程']
  },
  
  // Funcode AI 教室
  {
    id: 'funcode-starter',
    name: 'Funcode AI 教室',
    nameCn: 'Funcode AI 图形化编程教室',
    platform: 'funcode',
    description: 'Funcode AI Classroom - Graphical programming platform with AI features',
    descriptionCn: 'Funcode AI 教室 - 支持图形化编程和 AI 功能的在线平台',
    url: 'https://www.funcode.cc/',
    embedUrl: 'https://www.funcode.cc/',
    category: 'graphical',
    programmingType: 'graphical',
    topics: ['graphical', 'blocks', 'ai', 'education', 'circuit'],
    hardware: ['Arduino', 'ESP32', 'micro:bit'],
    features: ['图形化编程', 'AI 功能', '电路仿真', '代码转换', '在线烧录']
  },
  
  // Scratch for Arduino (S4A)
  {
    id: 'scratch-arduino',
    name: 'Scratch for Arduino',
    nameCn: 'Scratch Arduino 图形化编程',
    platform: 'custom',
    description: 'Scratch-based graphical programming for Arduino (S4A)',
    descriptionCn: '基于 Scratch 的 Arduino 图形化编程 (S4A)',
    url: 'http://s4a.cat/',
    embedUrl: 'http://s4a.cat/',
    category: 'graphical',
    programmingType: 'graphical',
    topics: ['arduino', 'scratch', 'graphical', 'blocks', 'education'],
    hardware: ['Arduino Uno', 'Arduino Nano'],
    features: ['Scratch 图形化', '实时交互', '传感器支持', '简单易用']
  }
]

export const HARDWARE_CATEGORIES = [
  { id: 'graphical', name: '图形化编程', nameEn: 'Graphical Programming' },
  { id: 'arduino', name: 'Arduino', nameEn: 'Arduino' },
  { id: 'esp32', name: 'ESP32', nameEn: 'ESP32' },
  { id: 'circuit', name: '电路仿真', nameEn: 'Circuit Simulation' },
  { id: 'microcontroller', name: '微控制器', nameEn: 'Microcontroller' },
] as const

export function getHardwareSimulationsByCategory(category?: string): HardwareSimulation[] {
  if (!category) return HARDWARE_SIMULATIONS
  return HARDWARE_SIMULATIONS.filter(sim => sim.category === category)
}

export function getHardwareSimulation(id: string): HardwareSimulation | undefined {
  return HARDWARE_SIMULATIONS.find(sim => sim.id === id)
}

export function getHardwareSimulationsByPlatform(platform: string): HardwareSimulation[] {
  return HARDWARE_SIMULATIONS.filter(sim => sim.platform === platform)
}

export function getHardwareSimulationsByProgrammingType(type: 'code' | 'graphical' | 'both'): HardwareSimulation[] {
  return HARDWARE_SIMULATIONS.filter(sim => 
    sim.programmingType === type || sim.programmingType === 'both'
  )
}

