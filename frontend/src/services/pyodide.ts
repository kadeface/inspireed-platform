/**
 * Pyodide 服务 - Python WebAssembly 执行引擎
 * 提供浏览器端 Python 代码执行能力
 */

// 使用CDN版本而不是本地安装的版本
declare const loadPyodide: any
declare type PyodideInterface = any

// 扩展window类型
declare global {
  interface Window {
    loadPyodide: any
  }
}

export interface ExecutionResult {
  output: string
  error: string | null
  result: any
  executionTime: number
}

export interface LoadingProgress {
  loaded: number
  total: number
  percentage: number
}

/**
 * Pyodide 服务类（单例）
 */
class PyodideService {
  private static instance: PyodideService | null = null
  private pyodide: PyodideInterface | null = null
  private isInitializing = false
  private initPromise: Promise<void> | null = null
  private loadingCallbacks: Array<(progress: LoadingProgress) => void> = []
  private installedPackages = new Set<string>()

  private constructor() {}

  /**
   * 获取单例实例
   */
  static getInstance(): PyodideService {
    if (!PyodideService.instance) {
      PyodideService.instance = new PyodideService()
    }
    return PyodideService.instance
  }

  /**
   * 初始化 Pyodide
   */
  async init(): Promise<void> {
    // 如果已经初始化，直接返回
    if (this.pyodide) {
      return
    }

    // 如果正在初始化，等待初始化完成
    if (this.isInitializing && this.initPromise) {
      return this.initPromise
    }

    this.isInitializing = true
    this.initPromise = this._init()

    try {
      await this.initPromise
    } finally {
      this.isInitializing = false
    }
  }

  private async _init(): Promise<void> {
    try {
      console.log('Loading Pyodide...')
      
      // 动态加载Pyodide CDN版本
      if (typeof window !== 'undefined') {
        // 加载Pyodide脚本
        if (!window.loadPyodide) {
          const script = document.createElement('script')
          script.src = 'https://cdn.jsdelivr.net/pyodide/v0.27.0/full/pyodide.js'
          script.async = true
          document.head.appendChild(script)
          
          await new Promise((resolve, reject) => {
            script.onload = resolve
            script.onerror = reject
          })
        }
        
        // 加载 Pyodide
        this.pyodide = await window.loadPyodide({
          indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.27.0/full/',
        })
      } else {
        throw new Error('Pyodide只能在浏览器环境中运行')
      }

      // 设置输出捕获
      await this.setupOutputCapture()

      console.log('Pyodide loaded successfully')
    } catch (error) {
      console.error('Failed to load Pyodide:', error)
      throw new Error('无法加载 Python 执行环境')
    }
  }

  /**
   * 设置输出捕获
   */
  private async setupOutputCapture(): Promise<void> {
    if (!this.pyodide) return

    // 创建输出捕获的 Python 代码
    await this.pyodide.runPythonAsync(`
import sys
from io import StringIO

class OutputCapture:
    def __init__(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
    
    def start(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr
    
    def stop(self):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
    
    def get_output(self):
        return self.stdout.getvalue()
    
    def get_error(self):
        return self.stderr.getvalue()
    
    def clear(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        sys.stdout = self.stdout
        sys.stderr = self.stderr

# 创建全局捕获器
_output_capture = OutputCapture()
`)
  }

  /**
   * 执行 Python 代码
   */
  async runPython(code: string): Promise<ExecutionResult> {
    // 确保 Pyodide 已初始化
    if (!this.pyodide) {
      await this.init()
    }

    if (!this.pyodide) {
      throw new Error('Pyodide 未初始化')
    }

    const startTime = performance.now()
    let output = ''
    let error: string | null = null
    let result: any = null

    try {
      // 清空并开始捕获输出
      await this.pyodide.runPythonAsync(`
_output_capture.clear()
_output_capture.start()
`)

      // 执行用户代码
      try {
        result = await this.pyodide.runPythonAsync(code)
      } catch (err: any) {
        error = this.formatError(err)
      }

      // 停止捕获并获取输出
      await this.pyodide.runPythonAsync(`_output_capture.stop()`)
      
      const capturedOutput = await this.pyodide.runPythonAsync(`_output_capture.get_output()`)
      const capturedError = await this.pyodide.runPythonAsync(`_output_capture.get_error()`)

      output = String(capturedOutput || '')
      
      // 如果有标准错误输出，也添加到错误信息中
      if (capturedError && String(capturedError).trim()) {
        if (error) {
          error = `${error}\n\n标准错误:\n${capturedError}`
        } else {
          error = String(capturedError)
        }
      }

      // 如果没有输出但有结果，显示结果
      if (!output && result !== undefined && result !== null) {
        output = String(result)
      }
    } catch (err: any) {
      error = this.formatError(err)
    }

    const executionTime = performance.now() - startTime

    return {
      output,
      error,
      result,
      executionTime,
    }
  }

  /**
   * 安装 Python 包
   */
  async installPackage(packageName: string): Promise<void> {
    if (!this.pyodide) {
      await this.init()
    }

    if (!this.pyodide) {
      throw new Error('Pyodide 未初始化')
    }

    // 检查是否已安装
    if (this.installedPackages.has(packageName)) {
      return
    }

    try {
      console.log(`Installing package: ${packageName}`)
      await this.pyodide.loadPackage(packageName)
      this.installedPackages.add(packageName)
      console.log(`Package installed: ${packageName}`)
    } catch (error) {
      console.error(`Failed to install package ${packageName}:`, error)
      throw new Error(`无法安装包: ${packageName}`)
    }
  }

  /**
   * 批量安装包
   */
  async installPackages(packageNames: string[]): Promise<void> {
    const toInstall = packageNames.filter((pkg) => !this.installedPackages.has(pkg))
    
    if (toInstall.length === 0) {
      return
    }

    if (!this.pyodide) {
      await this.init()
    }

    if (!this.pyodide) {
      throw new Error('Pyodide 未初始化')
    }

    try {
      console.log(`Installing packages: ${toInstall.join(', ')}`)
      await this.pyodide.loadPackage(toInstall)
      toInstall.forEach((pkg) => this.installedPackages.add(pkg))
      console.log('Packages installed successfully')
    } catch (error) {
      console.error('Failed to install packages:', error)
      throw new Error('无法安装包')
    }
  }

  /**
   * 检查是否已准备就绪
   */
  isReady(): boolean {
    return this.pyodide !== null
  }

  /**
   * 检查是否正在初始化
   */
  isLoading(): boolean {
    return this.isInitializing
  }

  /**
   * 格式化错误信息
   */
  private formatError(error: any): string {
    if (typeof error === 'string') {
      return error
    }

    if (error instanceof Error) {
      return error.message
    }

    if (error.message) {
      return String(error.message)
    }

    return String(error)
  }

  /**
   * 注册加载进度回调
   */
  onLoadingProgress(callback: (progress: LoadingProgress) => void): void {
    this.loadingCallbacks.push(callback)
  }

  /**
   * 清空环境（重置）
   */
  async reset(): Promise<void> {
    if (this.pyodide) {
      // 重新设置输出捕获
      await this.setupOutputCapture()
    }
  }

  /**
   * 获取已安装的包列表
   */
  getInstalledPackages(): string[] {
    return Array.from(this.installedPackages)
  }
}

// 导出单例实例
export const pyodideService = PyodideService.getInstance()

