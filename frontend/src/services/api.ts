import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig } from 'axios'

/**
 * 动态获取API基础URL
 * 根据当前访问的主机名自动适配后端地址
 */
function getApiBaseUrl(): string {
  // 如果环境变量中配置了API地址，优先使用
  if (import.meta.env.VITE_API_BASE_URL) {
    console.log('🔧 [API] 使用环境变量配置的 API 地址:', import.meta.env.VITE_API_BASE_URL)
    return import.meta.env.VITE_API_BASE_URL
  }
  
  // 动态获取当前主机名
  const hostname = window.location.hostname
  const protocol = window.location.protocol
  const port = window.location.port
  
  console.log('🔍 [API] 检测环境 - hostname:', hostname, 'protocol:', protocol, 'port:', port)
  
  // Cloud Studio 环境：如果 hostname 包含 cloudstudio.club 或 coding.net
  // 后端端口通常是 8000，但需要通过 Cloud Studio 分配的 URL 访问
  if (hostname.includes('cloudstudio.club') || hostname.includes('coding.net')) {
    // Cloud Studio 环境中，URL 格式为：{id}--{port}.{region}.cloudstudio.club
    // 前端 URL 示例：645cf02ac04c45c38ed3f5cceb49231b--5173.ap-shanghai2.cloudstudio.club
    // 后端 URL 应该：645cf02ac04c45c38ed3f5cceb49231b--8000.ap-shanghai2.cloudstudio.club
    // 需要将端口号从 5173 替换为 8000
    if (hostname.includes('--')) {
      // 将 --5173 替换为 --8000
      const backendHostname = hostname.replace(/--\d+/, '--8000')
      const apiUrl = `${protocol}//${backendHostname}/api/v1`
      console.log('✅ [API] Cloud Studio 环境，使用后端地址:', apiUrl)
      return apiUrl
    }
  }
  
  // 本地开发环境：前端端口5173 -> 后端端口8000
  const apiUrl = `${protocol}//${hostname}:8000/api/v1`
  console.log('📍 [API] 本地环境，使用后端地址:', apiUrl)
  return apiUrl
}

const API_BASE_URL = getApiBaseUrl()

class ApiService {
  private axiosInstance: AxiosInstance

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 120000, // 增加到120秒，适应文档转换等长时间操作
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // 请求拦截器
    this.axiosInstance.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        
        // 如果是FormData，删除Content-Type让浏览器自动设置
        if (config.data instanceof FormData) {
          delete config.headers['Content-Type']
        }
        
        // 调试日志已移除
        
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          const requestUrl = error.config?.url ?? ''
          const isAuthRequest = requestUrl.includes('/auth/login') || requestUrl.includes('/auth/register')

          if (!isAuthRequest) {
            localStorage.removeItem('access_token')
            window.location.href = '/login'
          }
        } else if (error.response?.status === 403) {
          // 403 权限错误，但不自动重定向，让调用方处理
          const errorMessage = error.response?.data?.detail || '需要相应权限'
          console.warn('权限不足:', errorMessage)
          // 可以在这里添加全局错误提示
        }
        return Promise.reject(error)
      }
    )
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    // 确保不使用缓存，特别是对于教案数据
    const noCacheConfig = {
      ...config,
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        ...config?.headers,
      },
    }
    const response = await this.axiosInstance.get<T>(url, noCacheConfig)
    return response.data
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.post<T>(url, data, config)
    return response.data
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.put<T>(url, data, config)
    return response.data
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.delete<T>(url, config)
    return response.data
  }

  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.patch<T>(url, data, config)
    return response.data
  }

  async downloadFile(url: string, config?: AxiosRequestConfig): Promise<Blob> {
    const response = await this.axiosInstance.get(url, {
      ...config,
      responseType: 'blob'
    })
    return response.data as Blob
  }
}

const api = new ApiService()

export { api }
export default api
