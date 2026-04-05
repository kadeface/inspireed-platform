/**
 * 考场安排API服务
 */

import axios from 'axios'
import { productionSameOriginApiV1, sanitizeViteApiUrlForProduction } from '@/utils/runtimeApiBase'
import type {
  ExamRoom,
  ExamRoomStudent,
  ExamProctor,
  AutoAssignRoomsRequest,
  AutoAssignProctorsRequest,
  ProctorAssignmentResponse
} from '@/types/evaluation'

/**
 * 获取API基础URL
 * 自动检测本地网络访问或使用环境变量配置
 */
function getApiBaseUrl(): string {
  const hostname = window.location.hostname
  const protocol = window.location.protocol

  // 优先使用环境变量
  if (import.meta.env.VITE_API_BASE_URL) {
    const u = import.meta.env.VITE_API_BASE_URL
    const sanitized = sanitizeViteApiUrlForProduction(u)
    if (sanitized) return sanitized
    return u
  }

  // CloudStudio云开发环境
  if (hostname.includes('cloudstudio.club')) {
    // 子域名格式：workspace-id--port.cloudstudio.club
    if (hostname.includes('--')) {
      return `https://${hostname.replace(/--\d+/, '--8000')}/api/v1`
    }
    // 其他CloudStudio格式
    return `${protocol}//${hostname}:8000/api/v1`
  }

  if (!import.meta.env.DEV) {
    return productionSameOriginApiV1()
  }
  return `${protocol}//${hostname}:8000/api/v1`
}

const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

// 请求拦截器：添加认证token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, (error) => {
  return Promise.reject(error)
})

// 响应拦截器：处理错误
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const examRoomService = {
  /**
   * 自动分配考场
   */
  async autoAssignRooms(
    examId: number,
    data: AutoAssignRoomsRequest
  ): Promise<ExamRoom[]> {
    return await apiClient.post(`/exams/${examId}/rooms/auto-assign`, data)
  },

  /**
   * 自动分配监考教师
   */
  async autoAssignProctors(
    examId: number,
    data: AutoAssignProctorsRequest
  ): Promise<ProctorAssignmentResponse> {
    return await apiClient.post(`/exams/${examId}/rooms/proctors/auto-assign`, data)
  },

  /**
   * 获取考试的所有考场
   */
  async getExamRooms(examId: number): Promise<ExamRoom[]> {
    return await apiClient.get(`/exams/${examId}/rooms`)
  },

  /**
   * 获取考场详情
   */
  async getExamRoom(examId: number, roomId: number): Promise<ExamRoom> {
    return await apiClient.get(`/exams/${examId}/rooms/${roomId}`)
  },

  /**
   * 更新考场信息
   */
  async updateExamRoom(
    examId: number,
    roomId: number,
    data: Partial<ExamRoom>
  ): Promise<ExamRoom> {
    return await apiClient.put(`/exams/${examId}/rooms/${roomId}`, data)
  },

  /**
   * 删除考场
   */
  async deleteExamRoom(examId: number, roomId: number): Promise<void> {
    return await apiClient.delete(`/exams/${examId}/rooms/${roomId}`)
  },

  /**
   * 获取考场的所有学生
   */
  async getRoomStudents(examId: number, roomId: number): Promise<ExamRoomStudent[]> {
    return await apiClient.get(`/exams/${examId}/rooms/${roomId}/students`)
  },

  /**
   * 获取考场的所有监考教师
   */
  async getRoomProctors(examId: number, roomId: number): Promise<ExamProctor[]> {
    return await apiClient.get(`/exams/${examId}/rooms/${roomId}/proctors`)
  },

  /**
   * 导出座位表PDF
   */
  async exportSeatingChart(examId: number, roomId: number): Promise<void> {
    const response = await apiClient.get(
      `/exams/${examId}/rooms/${roomId}/export/seating-chart.pdf`,
      { responseType: 'blob' }
    )

    // 创建下载链接
    const blob = new Blob([response], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `座位表_${new Date().getTime()}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  },

  /**
   * 导出准考证PDF
   */
  async exportExamTickets(examId: number, roomId: number): Promise<void> {
    const response = await apiClient.get(
      `/exams/${examId}/rooms/${roomId}/export/exam-tickets.pdf`,
      { responseType: 'blob' }
    )

    // 创建下载链接
    const blob = new Blob([response], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `准考证_${new Date().getTime()}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  },

  /**
   * 导出监考手册PDF
   */
  async exportProctorHandbook(examId: number, roomId: number): Promise<void> {
    const response = await apiClient.get(
      `/exams/${examId}/rooms/${roomId}/export/proctor-handbook.pdf`,
      { responseType: 'blob' }
    )

    // 创建下载链接
    const blob = new Blob([response], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `监考手册_${new Date().getTime()}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  },

  /**
   * 清空考试的所有考场编排
   */
  async clearAllRooms(examId: number): Promise<void> {
    await apiClient.delete(`/exams/${examId}/rooms/clear-all`)
  },

  /**
   * 批量导出所有文档（座位表、准考证、监考手册）
   */
  async exportAllDocuments(examId: number): Promise<void> {
    const response = await apiClient.get(
      `/exams/${examId}/rooms/export/all-documents.zip`,
      { responseType: 'blob' }
    )

    // 创建下载链接
    const blob = new Blob([response], { type: 'application/zip' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `全部文档_${new Date().getTime()}.zip`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }
}
