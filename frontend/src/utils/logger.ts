/**
 * 统一的调试日志工具
 * 在生产环境自动禁用所有调试日志
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
}

// 当前日志级别（从环境变量读取，默认为 INFO）
let currentLogLevel: LogLevel = LogLevel.INFO

// 从环境变量读取日志级别
if (import.meta.env.VITE_LOG_LEVEL === 'DEBUG') {
  currentLogLevel = LogLevel.DEBUG
} else if (import.meta.env.VITE_LOG_LEVEL === 'WARN') {
  currentLogLevel = LogLevel.WARN
} else if (import.meta.env.VITE_LOG_LEVEL === 'ERROR') {
  currentLogLevel = LogLevel.ERROR
}

// 是否启用调试日志
const isDebugEnabled = import.meta.env.VITE_ENABLE_DEBUG_LOGS === 'true' && import.meta.env.DEV

/**
 * 判断是否应该输出日志
 */
function shouldLog(level: LogLevel, moduleName?: string): boolean {
  // 如果禁用了调试日志，只输出 ERROR 级别
  if (!isDebugEnabled && level !== LogLevel.ERROR) {
    return false
  }

  // 检查日志级别
  if (level < currentLogLevel) {
    return false
  }

  // 检查模块是否在允许列表中
  if (import.meta.env.VITE_DEBUG_MODULES) {
    const modules = import.meta.env.VITE_DEBUG_MODULES.split(',').map(m => m.trim())
    // 如果指定了模块，并且当前模块不在列表中，不输出
    if (modules.length > 0 && !modules.includes('*') && moduleName && !modules.includes(moduleName)) {
      return false
    }
  }

  return true
}

/**
 * 获取日志前缀
 */
function getPrefix(moduleName?: string): string {
  return moduleName ? `[${moduleName}] ` : ''
}

/**
 * 调试日志（仅在开发环境）
 */
export function debug(message: any, ...args: any[]) {
  if (shouldLog(LogLevel.DEBUG)) {
    console.log(message, ...args)
  }
}

/**
 * 信息日志（带图标）
 */
export function log(message: any, ...args: any[]) {
  if (shouldLog(LogLevel.INFO)) {
    console.log(message, ...args)
  }
}

/**
 * 带图标的日志
 */
export function logWithEmoji(emoji: string, moduleName: string, message: any, ...args: any[]) {
  if (shouldLog(LogLevel.INFO, moduleName)) {
    console.log(`${emoji} ${getPrefix(moduleName)}`, message, ...args)
  }
}

/**
 * 警告日志
 */
export function warn(message: any, ...args: any[]) {
  if (shouldLog(LogLevel.WARN)) {
    console.warn(message, ...args)
  }
}

/**
 * 错误日志（始终输出）
 */
export function error(message: any, ...args: any[]) {
  // ERROR 级别始终输出
  console.error(message, ...args)
}

// 模块化日志导出
export const createLogger = (moduleName: string) => ({
  debug: (message: any, ...args: any[]) => {
    if (shouldLog(LogLevel.DEBUG, moduleName)) {
      console.log(getPrefix(moduleName), message, ...args)
    }
  },
  info: (message: any, ...args: any[]) => {
    if (shouldLog(LogLevel.INFO, moduleName)) {
      console.log(getPrefix(moduleName), message, ...args)
    }
  },
  warn: (message: any, ...args: any[]) => {
    if (shouldLog(LogLevel.WARN, moduleName)) {
      console.warn(getPrefix(moduleName), message, ...args)
    }
  },
  error: (message: any, ...args: any[]) => {
    console.error(getPrefix(moduleName), message, ...args)
  },
  // 带图标的日志方法
  logWithEmoji: (emoji: string, message: any, ...args: any[]) => {
    if (shouldLog(LogLevel.INFO, moduleName)) {
      console.log(`${emoji} ${getPrefix(moduleName)}`, message, ...args)
    }
  },
})

// 默认导出
export default {
  debug,
  log,
  logWithEmoji,
  warn,
  error,
  createLogger,
}
