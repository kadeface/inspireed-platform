/**
 * 统一的日志工具
 * 可以通过环境变量控制是否输出调试日志
 */

// 从环境变量读取配置，生产环境默认关闭调试日志
const isDevelopment = import.meta.env.MODE === 'development'
const ENABLE_DEBUG_LOGS = import.meta.env.VITE_ENABLE_DEBUG_LOGS === 'true' || isDevelopment

// 日志级别
export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR',
}

// 日志模块
export enum LogModule {
  API = 'API',
  LESSON = 'LESSON',
  ACTIVITY = 'ACTIVITY',
  WEBSOCKET = 'WEBSOCKET',
  SESSION = 'SESSION',
  ASSISTANT = 'ASSISTANT',
  CLASSROOM = 'CLASSROOM',
  GENERAL = 'GENERAL',
}

class Logger {
  private enabledModules: Set<string>
  private minLevel: LogLevel

  constructor() {
    // 可以通过环境变量配置启用的模块
    const enabledModulesStr = import.meta.env.VITE_DEBUG_MODULES || ''
    this.enabledModules = new Set(enabledModulesStr.split(',').filter(Boolean))
    
    // 如果没有指定模块，则启用所有模块
    if (this.enabledModules.size === 0 && ENABLE_DEBUG_LOGS) {
      Object.values(LogModule).forEach(module => this.enabledModules.add(module))
    }

    // 最小日志级别
    const minLevelStr = import.meta.env.VITE_LOG_LEVEL || 'INFO'
    this.minLevel = LogLevel[minLevelStr as keyof typeof LogLevel] || LogLevel.INFO
  }

  private shouldLog(level: LogLevel, module: LogModule): boolean {
    // 生产环境只输出 ERROR
    if (!ENABLE_DEBUG_LOGS && level !== LogLevel.ERROR) {
      return false
    }

    // 检查模块是否启用
    if (!this.enabledModules.has(module)) {
      return false
    }

    // 检查日志级别
    const levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR]
    const currentIndex = levels.indexOf(level)
    const minIndex = levels.indexOf(this.minLevel)
    
    return currentIndex >= minIndex
  }

  private formatMessage(level: LogLevel, module: LogModule, emoji: string, message: string): string {
    const timestamp = new Date().toLocaleTimeString()
    return `[${timestamp}] ${emoji} [${module}/${level}] ${message}`
  }

  debug(module: LogModule, message: string, data?: any, emoji: string = '🔍') {
    if (!this.shouldLog(LogLevel.DEBUG, module)) return
    
    const formattedMessage = this.formatMessage(LogLevel.DEBUG, module, emoji, message)
    if (data !== undefined) {
      console.log(formattedMessage, data)
    } else {
      console.log(formattedMessage)
    }
  }

  info(module: LogModule, message: string, data?: any, emoji: string = '✅') {
    if (!this.shouldLog(LogLevel.INFO, module)) return
    
    const formattedMessage = this.formatMessage(LogLevel.INFO, module, emoji, message)
    if (data !== undefined) {
      console.log(formattedMessage, data)
    } else {
      console.log(formattedMessage)
    }
  }

  warn(module: LogModule, message: string, data?: any, emoji: string = '⚠️') {
    if (!this.shouldLog(LogLevel.WARN, module)) return
    
    const formattedMessage = this.formatMessage(LogLevel.WARN, module, emoji, message)
    if (data !== undefined) {
      console.warn(formattedMessage, data)
    } else {
      console.warn(formattedMessage)
    }
  }

  error(module: LogModule, message: string, error?: any, emoji: string = '❌') {
    // ERROR 级别始终输出
    const formattedMessage = this.formatMessage(LogLevel.ERROR, module, emoji, message)
    if (error !== undefined) {
      console.error(formattedMessage, error)
    } else {
      console.error(formattedMessage)
    }
  }

  // 便捷方法
  lesson = {
    load: (message: string, data?: any) => this.debug(LogModule.LESSON, message, data, '📥'),
    save: (message: string, data?: any) => this.debug(LogModule.LESSON, message, data, '💾'),
    success: (message: string, data?: any) => this.info(LogModule.LESSON, message, data, '✅'),
  }

  activity = {
    mount: (message: string, data?: any) => this.debug(LogModule.ACTIVITY, message, data, '🔍'),
    create: (message: string, data?: any) => this.info(LogModule.ACTIVITY, message, data, '✅'),
    submit: (message: string, data?: any) => this.info(LogModule.ACTIVITY, message, data, '✅'),
  }

  api = {
    request: (message: string, data?: any) => this.debug(LogModule.API, message, data, '🔍'),
    success: (message: string, data?: any) => this.info(LogModule.API, message, data, '✅'),
    error: (message: string, error?: any) => this.error(LogModule.API, message, error, '❌'),
  }

  websocket = {
    connect: (message: string, data?: any) => this.info(LogModule.WEBSOCKET, message, data, '✅'),
    message: (message: string, data?: any) => this.debug(LogModule.WEBSOCKET, message, data, '📥'),
    disconnect: (message: string, data?: any) => this.info(LogModule.WEBSOCKET, message, data, '✅'),
  }

  session = {
    create: (message: string, data?: any) => this.info(LogModule.SESSION, message, data, '✅'),
    update: (message: string, data?: any) => this.debug(LogModule.SESSION, message, data, '🔍'),
  }
}

// 导出单例
export const logger = new Logger()

// 默认导出
export default logger
