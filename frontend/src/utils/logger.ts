/**
 * 日志工具 - 支持日志级别控制，减少生产环境的日志噪音
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error'

// 从环境变量获取日志级别，默认在生产环境只显示 warn 和 error
const getLogLevel = (): LogLevel => {
  if (import.meta.env.DEV) {
    // 开发环境：可以通过 localStorage 控制日志级别
    const stored = localStorage.getItem('logLevel')
    if (stored && ['debug', 'info', 'warn', 'error'].includes(stored)) {
      return stored as LogLevel
    }
    return 'debug' // 开发环境默认显示所有日志
  }
  return 'warn' // 生产环境默认只显示警告和错误
}

const currentLogLevel = getLogLevel()

const logLevels: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
}

const shouldLog = (level: LogLevel): boolean => {
  return logLevels[level] >= logLevels[currentLogLevel]
}

// 日志去重：相同内容的日志在短时间内只输出一次
const logCache = new Map<string, number>()
const LOG_DEDUP_INTERVAL = 5000 // 5秒内相同日志只输出一次

const getLogKey = (level: LogLevel, message: string, ...args: any[]): string => {
  return `${level}:${message}:${JSON.stringify(args)}`
}

const checkDedup = (key: string): boolean => {
  const now = Date.now()
  const lastTime = logCache.get(key)
  
  if (lastTime && now - lastTime < LOG_DEDUP_INTERVAL) {
    return false // 跳过重复日志
  }
  
  logCache.set(key, now)
  
  // 定期清理缓存（避免内存泄漏）
  if (logCache.size > 1000) {
    const cutoff = now - LOG_DEDUP_INTERVAL * 2
    for (const [k, v] of logCache.entries()) {
      if (v < cutoff) {
        logCache.delete(k)
      }
    }
  }
  
  return true
}

export const logger = {
  debug: (message: string, ...args: any[]) => {
    if (!shouldLog('debug')) return
    const key = getLogKey('debug', message, ...args)
    if (!checkDedup(key)) return
    console.log(`🔍 [DEBUG] ${message}`, ...args)
  },
  
  info: (message: string, ...args: any[]) => {
    if (!shouldLog('info')) return
    const key = getLogKey('info', message, ...args)
    if (!checkDedup(key)) return
    console.log(`ℹ️ [INFO] ${message}`, ...args)
  },
  
  warn: (message: string, ...args: any[]) => {
    if (!shouldLog('warn')) return
    const key = getLogKey('warn', message, ...args)
    if (!checkDedup(key)) return
    console.warn(`⚠️ [WARN] ${message}`, ...args)
  },
  
  error: (message: string, ...args: any[]) => {
    if (!shouldLog('error')) return
    // 错误日志不去重，确保重要错误都能看到
    console.error(`❌ [ERROR] ${message}`, ...args)
  },
  
  // 轮询专用日志：只在开发环境且明确启用时输出
  poll: (message: string, ...args: any[]) => {
    // 轮询日志默认不输出，除非在开发环境且设置了 debugPolling
    if (import.meta.env.DEV && localStorage.getItem('debugPolling') === 'true') {
      const key = getLogKey('debug', `[POLL] ${message}`, ...args)
      if (!checkDedup(key)) return
      console.log(`🔄 [POLL] ${message}`, ...args)
    }
  },
  
  // 设置日志级别（用于运行时调整）
  setLevel: (level: LogLevel) => {
    localStorage.setItem('logLevel', level)
    // 重新加载页面以应用新设置（或手动刷新）
    console.log(`日志级别已设置为: ${level}`)
  },
  
  // 获取当前日志级别
  getLevel: (): LogLevel => {
    return currentLogLevel
  },
}

// 导出默认实例
export default logger

