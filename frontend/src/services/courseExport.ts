/**
 * 课程导出导入服务
 */
import api from './api'

export interface CourseExportOptions {
  include_lessons?: boolean
  include_resources?: boolean
}

export interface CourseImportOptions {
  overwrite_existing?: boolean
}

export interface ImportResult {
  message: string
  result: {
    subjects: { created: number; skipped: number }
    grades: { created: number; skipped: number }
    courses: { created: number; skipped: number }
    chapters: { created: number; skipped: number }
    lessons: { created: number; skipped: number }
    resources: { created: number; skipped: number }
    errors: string[]
    warnings?: string[]
  }
  summary: {
    total_created: number
    total_skipped: number
    total_errors: number
    total_warnings?: number
  }
}

class CourseExportService {
  /**
   * 下载课程导出模板
   */
  async downloadTemplate(): Promise<Blob> {
    const response = await api.downloadFile('/course-export/export-template')
    return response
  }

  /**
   * 导出单个课程
   */
  async exportCourse(
    courseId: number, 
    options: CourseExportOptions = {}
  ): Promise<Blob> {
    const params = new URLSearchParams()
    if (options.include_lessons !== undefined) {
      params.append('include_lessons', options.include_lessons.toString())
    }
    if (options.include_resources !== undefined) {
      params.append('include_resources', options.include_resources.toString())
    }

    const response = await api.downloadFile(`/course-export/courses/${courseId}/export?${params}`)
    return response
  }

  /**
   * 导出所有课程
   */
  async exportAllCourses(options: CourseExportOptions = {}): Promise<Blob> {
    const params = new URLSearchParams()
    if (options.include_lessons !== undefined) {
      params.append('include_lessons', options.include_lessons.toString())
    }
    if (options.include_resources !== undefined) {
      params.append('include_resources', options.include_resources.toString())
    }

    const response = await api.downloadFile(`/course-export/export-all?${params}`)
    return response
  }

  /**
   * 导出单个教案（教师、管理员或研究员）
   */
  async exportLesson(lessonId: number): Promise<Blob> {
    const response = await api.downloadFile(`/course-export/lessons/${lessonId}/export`)
    return response
  }

  /**
   * 导入课程数据
   */
  async importCourses(
    file: File, 
    options: CourseImportOptions = {}
  ): Promise<ImportResult> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('overwrite_existing', options.overwrite_existing?.toString() || 'false')

    // api.post 已经返回了 response.data，所以直接返回 response 即可
    const response = await api.post<ImportResult>('/course-export/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response
  }

  /**
   * 下载文件到本地
   */
  downloadFile(blob: Blob, filename: string): void {
    try {
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to download file:', error)
      // 备用方案：直接打开新窗口
      const url = window.URL.createObjectURL(blob)
      window.open(url, '_blank')
      setTimeout(() => window.URL.revokeObjectURL(url), 1000)
    }
  }

  /**
   * 验证导入文件格式
   */
  validateImportFile(file: File): { valid: boolean; error?: string } {
    const isJson = file.name.toLowerCase().endsWith('.json')
    const isZip = file.name.toLowerCase().endsWith('.zip')
    
    if (!isJson && !isZip) {
      return { valid: false, error: '文件必须是JSON或ZIP格式' }
    }

    if (file.size === 0) {
      return { valid: false, error: '文件不能为空' }
    }

    // ZIP文件可能更大，因为包含资源文件
    const maxSize = isZip ? 200 * 1024 * 1024 : 50 * 1024 * 1024 // ZIP: 200MB, JSON: 50MB
    if (file.size > maxSize) {
      return { valid: false, error: `文件大小不能超过${maxSize / 1024 / 1024}MB` }
    }

    return { valid: true }
  }

  /**
   * 预览导入文件内容
   * 支持JSON和ZIP格式
   * 尝试多种编码格式
   */
  async previewImportFile(file: File): Promise<any> {
    const isZip = file.name.toLowerCase().endsWith('.zip')
    
    // ZIP文件预览：提取并解析data.json
    if (isZip) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = async (e) => {
          try {
            const arrayBuffer = e.target?.result as ArrayBuffer
            if (!arrayBuffer) {
              reject(new Error('文件读取失败'))
              return
            }
            
            // 使用JSZip库解析ZIP文件
            // 注意：如果项目中没有JSZip，需要安装或使用其他方法
            // 这里提供一个简化的实现，实际项目中可能需要引入JSZip
            try {
              // 动态导入JSZip（如果可用）
              const JSZip = (window as any).JSZip
              if (!JSZip) {
                // 如果没有JSZip，返回提示信息
                resolve({
                  type: 'zip',
                  message: 'ZIP文件预览需要解压，请直接导入查看结果',
                  filename: file.name
                })
                return
              }
              
              const zip = await JSZip.loadAsync(arrayBuffer)
              const dataJson = zip.file('data.json')
              
              if (!dataJson) {
                reject(new Error('ZIP文件中未找到data.json文件'))
                return
              }
              
              const jsonText = await dataJson.async('string')
              const content = JSON.parse(jsonText)
              resolve(content)
            } catch (zipError: any) {
              // 如果JSZip不可用，返回基本信息
              resolve({
                type: 'zip',
                message: 'ZIP文件预览需要解压，请直接导入查看结果',
                filename: file.name,
                size: file.size
              })
            }
          } catch (error: any) {
            reject(new Error(`ZIP文件读取失败: ${error.message}`))
          }
        }
        reader.onerror = () => reject(new Error('文件读取失败'))
        reader.readAsArrayBuffer(file)
      })
    }
    
    // JSON文件预览：尝试多种编码格式
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      
      // 先读取为 ArrayBuffer，以便尝试多种编码
      reader.onload = async (e) => {
        try {
          const arrayBuffer = e.target?.result as ArrayBuffer
          if (!arrayBuffer) {
            reject(new Error('文件读取失败'))
            return
          }
          
          // 尝试多种编码
          const encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030']
          
          for (const encoding of encodings) {
            try {
              const decoder = new TextDecoder(encoding, { fatal: true })
              const text = decoder.decode(arrayBuffer)
              
              // 检查是否看起来像JSON
              const trimmed = text.trim()
              if (!trimmed.startsWith('{') && !trimmed.startsWith('[')) {
                continue
              }
              
              // 尝试解析JSON
              try {
                const content = JSON.parse(text)
                resolve(content)
                return
              } catch (jsonError) {
                // JSON解析失败，继续尝试下一个编码
                continue
              }
            } catch (decodeError) {
              // 解码失败，继续尝试下一个编码
              continue
            }
          }
          
          // 所有编码都失败，尝试使用 UTF-8（非严格模式）
          try {
            const decoder = new TextDecoder('utf-8', { fatal: false })
            const text = decoder.decode(arrayBuffer)
            const content = JSON.parse(text)
            resolve(content)
            return
          } catch (error) {
            reject(new Error('无法解析JSON文件，请确保文件使用UTF-8或GBK编码且格式正确'))
          }
        } catch (error: any) {
          reject(new Error(`文件读取失败: ${error.message}`))
        }
      }
      
      reader.onerror = () => reject(new Error('文件读取失败'))
      reader.readAsArrayBuffer(file)
    })
  }
}

export const courseExportService = new CourseExportService()
export default courseExportService
