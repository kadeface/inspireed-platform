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
  }
  summary: {
    total_created: number
    total_skipped: number
    total_errors: number
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
    if (!file.name.endsWith('.json')) {
      return { valid: false, error: '文件必须是JSON格式' }
    }

    if (file.size === 0) {
      return { valid: false, error: '文件不能为空' }
    }

    if (file.size > 50 * 1024 * 1024) { // 50MB
      return { valid: false, error: '文件大小不能超过50MB' }
    }

    return { valid: true }
  }

  /**
   * 预览导入文件内容
   */
  async previewImportFile(file: File): Promise<any> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const content = JSON.parse(e.target?.result as string)
          resolve(content)
        } catch (error) {
          reject(new Error('JSON解析失败'))
        }
      }
      reader.onerror = () => reject(new Error('文件读取失败'))
      reader.readAsText(file, 'utf-8')
    })
  }
}

export const courseExportService = new CourseExportService()
export default courseExportService
